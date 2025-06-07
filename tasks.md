* Add lob_application and error_event fields discussed
  * Need lob_application field to store AppDynamics URL
  * Jira url
  * Info url path
  * Fix path params to get Environment from error event url
  * Save user like, dislike and comments
* Create Throttle/dedup logic without vector
* Create placeholders in error_event_task python code
  * Stacktrace vector processing
    * Convert stacktrace to vector
    * Compare with existing vectors and find similarity above threshold
    * Store vector in db
  * Create Context memory as a dict that is thread safe
  * Fetch bitbucket Code and save in cache folder
  * Checkout latest branch
  * Find Jira ticket ids from commits (from line of exception or top n jira from the commit history)
  * Get Java DAG from bitbucket code
  * Fetch Splunk logs by correlation id
  * Filter splunk logs for PII (optional)
  * Aggregate splunk logs and Java DAG
  * Create final LLM prompt (with List of Jira tickets, Splunk logs, Java DAG, stacktrace)
  * Call LLM with the final prompt and list of tools/mcp servers 
  * Save results to DB
  * Send email with the response and pull request
* Create Models
  * Splunk request response model
  * Java DAG request response model
  * Aggregate model for Splunk + Java DAG
* Create Pydantic AI agent with tools
  * Splunk tool
  * Java DAG tool
  * Jira tool
  * Bitbucket tool
* LLM call using AWS Bedrock
  * Create a function to call LLM with the final prompt and tools
  * Handle response and save to DB