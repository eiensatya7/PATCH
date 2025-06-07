1. Add lob_application and error_event fields discussed
   1. Need lob_application field to store AppDynamics URL
   2. Jira url
   3. Info url path
   4. Fix path params to get Environment from error event url
   5. Save user like, dislike and user comments
2. Create Throttle/dedup logic without vector
3. Create placeholders in error_event_task python code
   1. Stacktrace vector processing
       * Convert stacktrace to vector
       * Compare with existing vectors and find similarity above threshold
       * Store vector in db
   2. Create Context memory as a dict that is thread safe
   3. Fetch bitbucket Code and save in cache folder
   4. Checkout latest branch
   5. Find Jira ticket ids from commits (from line of exception or top n jira from the commit history)
   6. Get Java DAG from bitbucket code
   7. Fetch Splunk logs by correlation id
   8. Filter splunk logs for PII (optional)
   9. Aggregate splunk logs and Java DAG
   10. Create final LLM prompt (with List of Jira tickets, Splunk logs, Java DAG, stacktrace)
   11. Call LLM with the final prompt and list of tools/mcp servers
   12. Save results to DB
   13. Send email with the response and pull request
4. Create Models
   1. Splunk request response model
   2. Java DAG request response model
   3. Aggregate model for Splunk + Java DAG
5. Create Pydantic AI agent with tools
   1. Splunk tool
   2. Java DAG tool
   3. Jira tool
   4. Bitbucket tool
6. LLM call using AWS Bedrock
   1. Create a function to call LLM with the final prompt and tools
   2. Handle response and save to DB