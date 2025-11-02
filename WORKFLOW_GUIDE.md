# Green Signal - Agentic Workflow Solution Guide

## Workflow Logic Overview

This n8n workflow implements a phishing detection agent that processes emails through an LLM and aggregates results for submission.

### Architecture

```
Trigger → Fetch Emails → Extract Array → Loop Each Email → 
Format for LLM → Classify with LLM → Parse Response → 
Format Result → Collect Results → Aggregate → Submit → Display Result
```

---

## Node-by-Node Breakdown

### 1. **Manual Trigger**
- Entry point for the workflow
- Click "Execute" to start the agent
- No parameters needed

### 2. **Fetch Emails Data**
- HTTP GET request to `http://localhost:3000/api/challenges/green-signal`
- Returns: `{ challenge, title, description, emails: [...] }`
- Retrieves the 20 emails to classify

### 3. **Extract Emails Array**
- Set node that extracts just the emails array
- **Expression**: `={{ $json.emails }}`
- **Purpose**: Isolate the array for looping
- **Output**: Array of 20 email objects

### 4. **Loop Through Emails** ⭐ KEY NODE
- **Type**: Split in Batches (with batch size = 1)
- **Parameter**: `loopOver: $json`
- **Purpose**: Converts array into 20 separate item executions
- **How it works**:
  - First execution: processes `{ sender, subject, body }` of email #1
  - Second execution: processes email #2
  - ... repeats 20 times
- **Critical**: Without this, you can't process individual emails

### 5. **Format Email for LLM**
- Set node that wraps each email for LLM processing
- **Expression**: `={{ { email: $json, index: $nodeExecutionContext.itemIndex } }}`
- **Output**: 
  ```json
  {
    "email": { "sender": "...", "subject": "...", "body": "..." },
    "index": 0  // which email in the batch (0-19)
  }
  ```

### 6. **Classify Email with LLM** ⭐ INTELLIGENCE NODE
- **Type**: OpenAI LangChain node (or use Claude, Gemini, etc.)
- **Prompt**: Dynamic template that:
  - Feeds sender, subject, body to the LLM
  - Asks for classification: "PHISHING" or "LEGITIMATE"
  - Requests reasoning_summary
  - Forces JSON output format only
- **Input** (per email):
  ```
  You are a phishing detection expert. Analyze:
  Sender: user@example.com
  Subject: Urgent Account Verification
  Body: Please verify your credentials immediately...
  
  Return: {"classification": "PHISHING" or "LEGITIMATE", "reasoning_summary": "..."}
  ```
- **Output**: LLM's structured classification

### 7. **Parse LLM Response**
- Extracts classification and reasoning from LLM's JSON response
- **Expression**: 
  ```javascript
  {{ { 
    classification: $json.choices[0].message.content | json.parse().classification, 
    reasoning_summary: $json.choices[0].message.content | json.parse().reasoning_summary 
  } }}
  ```
- **Output**:
  ```json
  {
    "classification": "PHISHING",
    "reasoning_summary": "Contains urgency and verification request"
  }
  ```

### 8. **Format Result**
- Combines the original email with its classification
- **Expression**: 
  ```javascript
  {{ { 
    email: $json.email, 
    classification: $json.classification, 
    reasoning_summary: $json.reasoning_summary 
  } }}
  ```
- **Output** (matches API submission format):
  ```json
  {
    "email": { "sender": "...", "subject": "...", "body": "..." },
    "classification": "PHISHING",
    "reasoning_summary": "..."
  }
  ```

### 9. **Collect All Results** ⭐ AGGREGATION NODE
- **Type**: Split in Batches (recombines all items)
- **Purpose**: Waits for all 20 loop iterations to complete
- **Output**: Collected all 20 formatted results

### 10. **Aggregate Results**
- Combines all individual results into single submission array
- **Expression**:
  ```javascript
  {{ { results: $response.result.map(item => item.json) } }}
  ```
- **Output**:
  ```json
  {
    "results": [
      { "email": {...}, "classification": "PHISHING", "reasoning_summary": "..." },
      { "email": {...}, "classification": "LEGITIMATE", "reasoning_summary": "..." },
      ...  // 20 items total
    ]
  }
  ```

### 11. **Submit to Validation API**
- HTTP POST to `http://localhost:3000/api/challenges/green-signal/submit`
- **Body**: Send the aggregated results array directly
- **Key**: The API expects the raw array, not wrapped in an object
- **Response**: 
  ```json
  {
    "success": true,
    "message": "✅ Submission validated successfully.",
    "flag": "FLAG{green_signal_secured}"
  }
  ```

### 12. **Display Result**
- Final Set node that extracts the flag and status
- Shows success/failure message and the flag if successful

---

## Critical Implementation Details

### The Loop Pattern
```
Array of 20 emails
    ↓
Split in Batches (batch size 1)
    ↓
20 separate executions (one per email)
    ↓
Process each through LLM
    ↓
Split in Batches again (recombines)
    ↓
Single array of 20 results
```

### Why This Works
- **n8n execution model**: Each split iteration executes nodes sequentially
- **LLM loop**: LLM node runs 20 times (once per email), each with its own context
- **Aggregation**: Second split node collects all results before submission
- **Statelessness**: Each email is processed independently with full context

### Data Flow Example
```
Execution 1:
  Input:  { sender: "user@phishing.com", subject: "Verify Account", body: "..." }
  LLM:    "This is PHISHING because [reasons]"
  Output: { email: {...}, classification: "PHISHING", reasoning_summary: "..." }

Execution 2:
  Input:  { sender: "boss@company.com", subject: "Meeting Tomorrow", body: "..." }
  LLM:    "This is LEGITIMATE because [reasons]"
  Output: { email: {...}, classification: "LEGITIMATE", reasoning_summary: "..." }

... [20 times total]

Final: POST entire array to API
```

---

## Setup Instructions

### 1. Import the Workflow
1. Open n8n
2. Create new workflow
3. Click "Import from File"
4. Select `green-signal_workflow_solution.json`

### 2. Configure LLM Node
- **Credentials**: Connect your OpenAI (or other LLM) API key
- **Model**: Select appropriate model (gpt-4-turbo recommended)
- Or switch to Gemini, Claude, etc. by changing the node type

### 3. Start Backend Server
```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

### 4. Execute Workflow
- Click "Execute" on Manual Trigger
- Wait for all 20 emails to process
- Check final result for the flag

---

## Troubleshooting

### If submission fails: "length does not match"
- Check that all 20 emails were processed (look at execution log)
- Verify Aggregate Results node is collecting all items

### If LLM returns parse errors
- Ensure LLM model is configured and has API credits
- Check that the prompt format forces JSON-only output
- Try with a simpler model (gpt-3.5-turbo) first

### If API returns "Phishing classifications do not match"
- LLM might be misclassifying emails
- Consider refining the prompt with more specific instructions
- Try a more capable model (gpt-4)

### If batch collection hangs
- Verify HTTP request timeout settings
- Check that backend server is running on port 3000
- Look for network connectivity issues

---

## Extension Ideas

1. **Add Validation Logic**: If phishing count != expected, retry with different model
2. **Parallel Processing**: Use multiple LLM models and majority vote
3. **Confidence Scoring**: Have LLM provide confidence levels (0-1)
4. **Error Handling**: Add conditional branches for failed classifications
5. **Logging**: Add database node to log all classifications for analysis
