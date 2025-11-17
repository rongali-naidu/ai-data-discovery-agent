# AI Data Discovery Agent


## Overview

This project delivers a complete, production-grade implementation of an **AI-powered Data Discovery & SQL Generation Agent** leveraging the following key components:

* **AWS Glue Data Catalog** – for table and metadata management
* **Amazon Athena** – for execution of generated SQL queries
* **Amazon S3** – as a knowledge-base store
* **Amazon Quick Suite** – for knowledge-base ingestion, chat agents, and RAG workflows
* **Large Language Models (LLMs)** – to interpret natural language, generate SQL, and reason over metadata

This solution automates:

* Extraction of fine-grained metadata (tables, columns, partitions, descriptions, view SQLs)
* Ingestion and indexing of that metadata + sample SQLs into Quick Suite knowledge bases
* Enabling an AI Agent that can:

  * Discover datasets and their structure
  * Understand business meaning of fields
  * Generate accurate SQL queries for analytics or validation

---

##  Why This Matters — A Rapid Evolution

In My AWS Blog publoshed in October 2024 [Enrichment of Metadata for Text-to-SQL](https://aws.amazon.com/blogs/big-data/enriching-metadata-for-accurate-text-to-sql-generation-for-amazon-athena), illustrated how rich, high-quality metadata is *critical* for accurate text-to-SQL generation.  Since then, the landscape has transformed dramatically. New services and frameworks introduced by AWS and others have made building Retrieval-Augmented Generation (RAG) systems, knowledge bases, and chat-agent workflows far simpler and more enterprise-ready.

In particular, Amazon Quick Suite heralds the next wave of “agentic AI” for business:

* It provides **Knowledge Bases** built on S3, document stores and metadata, enabling semantic retrieval. ([AWS Documentation][2])
* It enables **Chat Agents** that integrate with those knowledge bases and act as natural-language interfaces to your data. ([Amazon Web Services, Inc.][3])
* It supports integration with enterprise systems, Model Context Protocol (MCP) servers and workflows — bridging insight and action. ([Amazon Web Services, Inc.][4])

This repository builds on that momentum — leveraging the latest AWS capabilities to deliver a fully integrated Data Discovery + SQL Generation agent, ready for enterprise action.



### High-Level Overview

```
 ┌──────────────────────────────────────────────┐
 │                Users (Browser App)           │
 └──────────────────────────┬───────────────────┘
                            │
                            ▼
                  Quick Suite AI Agent
               (RAG + Prompt Template)
                            │
         ┌──────────────────┴──────────────────┐
         ▼                                     ▼
Quick Suite Knowledge Base              LLM (SQL & reasoning)
 (Glue & Athena JSON)                     
         ▲                                     │
         └──────────────────┬──────────────────┘
                            ▼
               AWS S3 Knowledge Base Bucket
                            ▲
           ┌────────────────┴────────────────┐
           ▼                                 ▼
   Lambda: Glue Metadata Builder     Lambda: Athena SQL Collector
           │                                 │
           ▼                                 ▼
    AWS Glue Catalog                  Athena Workgroups
```

---

## 🚀 Features

* **Automated Metadata Extraction**
  Extracts table descriptions, columns, partitions, view SQL, and other metadata from AWS Glue.
* **Sample SQL Collection**
  Collects saved queries from all Athena workgroups, and matches them to tables for context.
* **RAG-Ready Knowledge Base**
  Stores structured JSON documents in S3, which are ingested into Quick Suite as knowledge bases.
* **AI Agent Integration**
  Enables natural language chat for exploring data, discovering schema, generating SQL, and detecting data-quality issues.
* **SQL Generation & Validation**
  Generates safe and optimized SQL statements using LLMs, guided by metadata context and quality rules.

---

## Repository Structure

```
ai-data-discovery-agent/
│
├── README.md
├── architecture/
│   ├── ai_data_discovery_architecture.png
│   └── sequence_diagram.md
├── lambda/
│   ├── glue_kb_builder/
│   │   ├── handler.py
│   │   ├── requirements.txt
│   │   └── IAM_Policy.json
│   └── athena_sql_collector/
│       ├── handler.py
│       ├── requirements.txt
│       └── IAM_Policy.json
├── knowledge_base_samples/
│   ├── AwsDataCatalog/
│   └── athena_workgroups/
├── quicksuite/
│   ├── knowledge_base_config.md
│   ├── agent_prompt_template.md
│   ├── browser_app_setup.md
│   └── rag_config.yaml
├── docs/
│   ├── data_quality_tracker_template.xlsx
│   ├── data_quality_dimensions.md
│   └── MDM_considerations.md
└── LICENSE
```

---

## Setup & Deployment

1. Configure IAM roles with appropriate permissions (Glue, Athena, Lake Formation, S3, STS).
2. Deploy the Lambda functions in the `lambda/` folder (Glue metadata extractor & Athena query collector).
3. Schedule or trigger the extractor Lambda to populate S3.
4. Ingest the generated JSON files into Quick Suite as knowledge bases
5.  Crate Quick Suite Spaces linking the Knowledge Base
6. Create a Quick Suite Agent, assign the knowledge base(s), and use the prompt template in `quicksuite/agent_prompt_template.md`.
7. Hook the Agenet into your Browser App for end-user access.


---

## References

* “Enriching metadata for accurate text-to-SQL generation for Amazon Athena”, AWS Big Data Blog. ([Amazon Web Services, Inc.][1])
* “Announcing Amazon Quick Suite: your agentic teammate for answering questions and taking action.” ([Amazon Web Services, Inc.][5])
* “Connect Amazon Quick Suite to enterprise apps and agents with MCP.” ([Amazon Web Services, Inc.][4])
* “Establishing enterprise governance in Amazon Quick Suite using custom permissions.” ([Amazon Web Services, Inc.][6])





[1]: https://aws.amazon.com/blogs/big-data/enriching-metadata-for-accurate-text-to-sql-generation-for-amazon-athena/ "Enriching metadata for accurate text-to-SQL generation ..."
[2]: https://docs.aws.amazon.com/quicksuite/latest/userguide/knowledge-base-integrations.html "Knowledge bases - Amazon Quick Suite - AWS Documentation"
[3]: https://aws.amazon.com/quicksuite/ "Amazon Quick Suite – AWS - Agentic AI"
[4]: https://aws.amazon.com/blogs/machine-learning/connect-amazon-quick-suite-to-enterprise-apps-and-agents-with-mcp/ "Connect Amazon Quick Suite to enterprise apps and agents with MCP"
[5]: https://aws.amazon.com/blogs/aws/reimagine-the-way-you-work-with-ai-agents-in-amazon-quick-suite/ "Announcing Amazon Quick Suite: your agentic teammate for ..."
[6]: https://aws.amazon.com/blogs/business-intelligence/establishing-enterprise-governance-in-amazon-quick-suite-using-custom-permissions/ "Establishing enterprise governance in Amazon Quick Suite using ..."

