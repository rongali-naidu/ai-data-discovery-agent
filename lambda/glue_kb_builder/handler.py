import boto3
import json
import os
import re

# Environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME')
ASSUME_ROLE_ARN = os.environ.get('ASSUME_ROLE_ARN')  # Role to assume
CATALOG_NAME = "AwsDataCatalog"  # default catalog

def get_clients(assume_role_arn):
    """
    Assume the target role and create Glue and S3 clients with temporary credentials
    """
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName='LambdaGlueMetadataSession'
    )
    
    creds = response['Credentials']
    
    glue_client = boto3.client(
        'glue',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
    )
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
    )
    
    athena_client = boto3.client(
        'athena',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
    )
    return glue_client, s3_client, athena_client

def fetch_athena_queries(athena_client,s3_client):
    """
    Fetch saved Athena queries across all workgroups
    """
    sample_sqls = []
    
    # List workgroups
    workgroups = athena_client.list_work_groups()['WorkGroups']
    workgroup_names = [wg['Name'] for wg in workgroups]
    
    for wg in workgroup_names:
        # List queries in this workgroup
        wg_sqls = []
        paginator = athena_client.get_paginator('list_named_queries')
        pages = paginator.paginate(WorkGroup=wg)
        query_ids = []
        for page in pages:
            query_ids.extend(page.get('NamedQueryIds', []))
        
        for qid in query_ids:
            q = athena_client.get_named_query(NamedQueryId=qid)['NamedQuery']
            sample_sqls.append({
                "query_name": q['Name'],
                "workgroup": wg,
                "database": q['Database'],
                "query_sql": q['QueryString']
            })
            wg_sqls.append({
                "query_name": q['Name'],
                "workgroup": wg,
                "database": q['Database'],
                "query_sql": q['QueryString']
            })
        # Save per-workgroup JSON
        s3_key = f"athena_saved_queries/{wg}.json"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(wg_sqls, indent=2)
        )
        print(f"Saved {len(wg_sqls)} queries for workgroup '{wg}' → s3://{BUCKET_NAME}/{s3_key}")
                
    return sample_sqls


def lambda_handler(event, context):
    if not BUCKET_NAME:
        return {"status": "error", "message": "BUCKET_NAME environment variable not set"}
    if not ASSUME_ROLE_ARN:
        return {"status": "error", "message": "ASSUME_ROLE_ARN environment variable not set"}
    
    glue, s3, athena = get_clients(ASSUME_ROLE_ARN)
    
    try:
        # Fetch Athena queries
        all_queries = fetch_athena_queries(athena,s3)
        print(f"Fetched {len(all_queries)} Athena saved queries across all workgroups")

        # Get databases
        databases = glue.get_databases()['DatabaseList']
        
        for db in databases:
            db_name = db['Name']
            print(f"Processing database: {db_name}")
            
            # Pagination for all tables
            paginator = glue.get_paginator('get_tables')
            pages = paginator.paginate(DatabaseName=db_name)
            
            tables = []
            for page in pages:
                tables.extend(page.get('TableList', []))
            
            print(f"Total tables found in {db_name}: {len(tables)}")
            db_metadata = []
            
            for table in tables:
                table_name = table['Name']
                table_type = table.get('TableType', 'TABLE')
                view_sql = table.get('ViewOriginalText', '') if table_type == 'VIRTUAL_VIEW' else ''
                
                storage_desc = table.get('StorageDescriptor', {})
                
                columns = [
                    {"name": col['Name'], "type": col['Type'], "comment": col.get('Comment', '')}
                    for col in storage_desc.get('Columns', [])
                ]
                
                partitions = [
                    {"name": p['Name'], "type": p['Type'], "comment": p.get('Comment', '')}
                    for p in table.get('PartitionKeys', [])
                ]
                
                table_metadata = {
                    "table_comment": table.get('Description', ''),
                    "location": storage_desc.get('Location', ''),
                    "classification": table.get('TableType', ''),
                    "owner": table.get('Owner', ''),
                    "create_time": str(table.get('CreateTime', '')),
                    "update_time": str(table.get('UpdateTime', '')),
                    "parameters": table.get('Parameters', {}),
                    "table_type": table_type,
                    "view_sql": view_sql
                }
                
                fqn = f'{CATALOG_NAME}.{db_name}."{table_name}"'
                     # Find relevant Athena queries for this table (case-insensitive search)

                relevant_queries = []
                pattern = re.compile(r'\b{}\b'.format(re.escape(table_name)), re.IGNORECASE)
                for q in all_queries:
                    if pattern.search(q['query_sql']):
                        relevant_queries.append({
                            "query_name": q['query_name'],
                            "workgroup": q['workgroup'],
                            "query_sql": q['query_sql']
                        })    

                db_metadata.append({
                    "table_name": table_name,
                    "fully_qualified_name": fqn,
                    "table_metadata": table_metadata,
                    "columns": columns,
                    "partitions": partitions,
                    "sample_sqls": relevant_queries
                })
            
            # Save to S3
            s3_key = f"{CATALOG_NAME}/{db_name}.json"
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=json.dumps(db_metadata, indent=2)
            )
            print(f"Saved metadata for DB '{db_name}' → s3://{BUCKET_NAME}/{s3_key}")
        
        return {"status": "success", "message": "Glue metadata uploaded successfully"}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}
