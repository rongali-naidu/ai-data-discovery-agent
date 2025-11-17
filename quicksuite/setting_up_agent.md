### **Notes**

Create a Chat Agent by specifying prompt details and linking it to the Space created in the earlier step.
More details:
[https://docs.aws.amazon.com/quicksuite/latest/userguide/custom-agents.html](https://docs.aws.amazon.com/quicksuite/latest/userguide/custom-agents.html)

After creating the Chat Agent, you can grant permissions to control who can access it.

---

### **Persona Instructions**

These instructions act as the **Agent Prompt Definition**.
Below is a clean starting prompt you can include directly in Quick Suite:

```text
For every question asked by the user, retrieve the relevant details from the Knowledge Base
and explain them in a simple, relatable format.

For questions involving SQL or Athena SQL, follow these instructions:

1. Glue table details are provided in the Knowledge Base, including sample SQLs and
   fully_qualified_name values.
2. Generate SQL for the scenario described by the user.
3. Always use the fully_qualified_name as the table name in the FROM clause.
4. Use column names exactly as they appear in the Knowledge Base.
```
