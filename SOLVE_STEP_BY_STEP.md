# Solving Green Signal Advanced Challenge - Step by Step

## Phase 1: Setup (5 minutes)

### Step 1: Start the Advanced Backend Server
```bash
cd /Users/shaynavinoth/Downloads/Green\ Signal\ 2
python3 -m uvicorn main_advanced:app --host 0.0.0.0 --port 3000 --reload
```

**What to see:**
```
INFO:     Uvicorn running on http://0.0.0.0:3000
INFO:     Application startup complete
```

**Test it:**
```bash
curl http://localhost:3000/health
```

Should return:
```json
{"status": "online", "timestamp": ..., "challenge": "green-signal-advanced"}
```

---

### Step 2: Verify the Data Files Exist
```bash
ls -la data/
# Should show: emails.json
```

**Note**: If `emails.json` doesn't exist, run:
```bash
python3 generate_messages_with_labels.py
```

---

### Step 3: Test the Tool APIs

**Test Domain Reputation Tool:**
```bash
curl -X POST http://localhost:3000/api/v2/tools/domain-reputation \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'
```

Expected response:
```json
{
  "domain": "google.com",
  "reputation_score": 95,
  "risk_level": "SAFE",
  "established": 2002,
  "years_active": 22
}
```

**Test Pattern Analysis Tool:**
```bash
curl -X POST http://localhost:3000/api/v2/tools/pattern-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "user@phish.com",
    "subject": "URGENT: Verify Your Account",
    "body": "Please verify your credentials immediately or your account will be suspended."
  }'
```

Expected response includes urgency and verification indicators.

**Test Header Analysis Tool:**
```bash
curl -X POST http://localhost:3000/api/v2/tools/header-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "support@google.com",
    "subject": "Account Alert"
  }'
```

Expected response: SPF/DKIM/DMARC status.

---

## Phase 2: Open n8n Workflow (5 minutes)

### Step 4: Import the Advanced Workflow

1. Open n8n dashboard
2. Click **"New"** → **"Create blank workflow"**
3. Click **three dots** → **"Import from File"**
4. Select: `workflows/green-signal_advanced_agentic.json`
5. Click **"Open"**

You should see 21 nodes connected in a chain with parallel tool calls.

---

### Step 3: Configure OpenAI Credentials

1. Find the **"Agent: Plan Analysis (Tool Use)"** node (orange LLM node)
2. Click it to select
3. Look for **"Model"** field
4. Click credential selector
5. Add OpenAI API key:
   - Go to https://platform.openai.com/api-keys
   - Create/copy API key
   - Paste into n8n credential

**Do the same for these LLM nodes:**
- Agent: Plan Analysis (Tool Use)
- Agent: Multi-Factor Analysis
- Agent: Skeptical Review (Low Confidence)

**Model Selection:**
- Choose: **gpt-4-turbo** (or gpt-4 if available)
- GPT-3.5-turbo might work but has worse reasoning

---

## Phase 3: Test the Workflow (10 minutes)

### Step 6: Run One Test Email First

Before running all 20, let's test with one email:

1. Click **"Start Advanced Agent"** node
2. Click blue **"Execute"** button
3. Wait for execution...

**Expected behavior:**
- Green checkmarks on all nodes
- Execution should take 30-60 seconds per email
- Watch nodes activate: Plan → Tools (parallel) → Analysis → Gate → Results

**What each node does:**
```
Start Advanced Agent
    ↓
Fetch Challenge (gets 20 emails)
    ↓
Initialize: Setup Agent Memory (creates empty analysis buffer)
    ↓
Batch: Loop Through Emails (processes one at a time)
    ↓
Agent: Plan Analysis (decides which tools to use)
    ↓
[PARALLEL EXECUTION]:
  ├─ Tool: Domain Reputation Check
  ├─ Tool: Pattern Analysis
  └─ Tool: Header Analysis
    ↓
Aggregate: Tool Results (combines all tool outputs)
    ↓
Agent: Multi-Factor Analysis (synthesizes evidence)
    ↓
Gate: High Confidence? (checks if >= 0.8)
    ├─ YES → Accept: High Confidence Result
    └─ NO → Agent: Skeptical Review (challenges analysis)
    ↓
Finalize: Merge Results (formats for submission)
    ↓
[REPEAT FOR ALL 20 EMAILS]
    ↓
Recombine: All Results (waits for all to complete)
    ↓
Prepare: Final Submission (formats JSON array)
    ↓
Submit: Advanced Challenge (POSTs to /api/v2/submit)
    ↓
Display: Results & Score (shows accuracy and flag)
```

---

## Phase 4: Monitor & Debug (15 minutes)

### Step 7: Check Execution Results

After execution completes, click on key nodes to see outputs:

**1. Check "Agent: Plan Analysis" output:**
```json
{
  "reasoning": "Email has urgency and verification language...",
  "tools_to_call": ["domain-reputation", "pattern-analysis", "header-analysis"],
  "initial_risk": 0.65,
  "evidence_needed": [...]
}
```

**2. Check "Tool: Domain Reputation Check" output:**
```json
{
  "domain": "security-update.com",
  "reputation_score": 5,
  "risk_level": "CRITICAL",
  "established": 2024,
  "years_active": 0
}
```

**3. Check "Tool: Pattern Analysis" output:**
```json
{
  "urgency_indicators": ["urgent", "verify"],
  "verification_requests": ["verify credentials"],
  "suspicious_links": ["http://security-portal.login.com/verify"],
  "domain_consistency": "SUSPICIOUS_KEYWORDS_IN_DOMAIN",
  "risk_score": 0.75
}
```

**4. Check "Agent: Multi-Factor Analysis" output:**
```json
{
  "multi_factor_analysis": {
    "domain_risk_level": "CRITICAL",
    "pattern_risk_level": "CRITICAL",
    "header_risk_level": "HIGH",
    "confidence_score": 0.95,
    "risk_factors": ["low reputation", "urgency", "verification request", "suspicious links"]
  },
  "cross_validation": {
    "signals_aligned": true,
    "false_positive_risk": false,
    "sophisticated_attack_suspected": false,
    "reasoning": "All three risk factors align - clear phishing email"
  },
  "final_classification": "PHISHING",
  "reasoning_summary": "Strong phishing indicators across all analysis dimensions",
  "confidence_justification": "0.95 confidence due to aligned signals"
}
```

**5. Check "Gate: High Confidence?" branching:**
- If confidence >= 0.8: goes to "Accept: High Confidence Result"
- If confidence < 0.8: goes to "Agent: Skeptical Review"

**6. Check final "Display: Results & Score":**
```json
{
  "success": true,
  "score": 1000,
  "accuracy": 0.95,
  "flag": "FLAG{green_signal_advanced_mastered}",
  "message": "✅ PERFECT - Detected 19/20 phishing emails (95% accuracy)"
}
```

---

## Phase 5: Full Execution (2-5 minutes)

### Step 8: Run All 20 Emails

1. Click **"Start Advanced Agent"** 
2. Click **Execute**
3. **Wait** for completion (shows progress in UI)
4. Check final results

**Expected execution time:** 2-5 minutes for 20 emails (30-60 sec per email)

**Success criteria:**
- All emails classified
- Accuracy >= 75% for flag
- Score shown

---

## Troubleshooting

### Issue: "Tool endpoint returned 404"
**Solution:** 
- Ensure `main_advanced.py` is running
- Check: `curl http://localhost:3000/health`
- Restart: `python3 -m uvicorn main_advanced:app --host 0.0.0.0 --port 3000`

### Issue: "JSON parse error in Agent node"
**Solution:**
- Use GPT-4 or GPT-4-turbo (better JSON handling)
- Check OpenAI API has credits
- Look at LLM error in node output

### Issue: "Submission length does not match"
**Solution:**
- Workflow should process all 20 emails
- Check that "Recombine: All Results" collects all 20
- Verify email count in "Fetch Challenge" output

### Issue: Low accuracy (< 75%)
**Solution:**
- Check "Multi-Factor Analysis" reasoning
- Verify tool results are being used correctly
- Look for false positives (legitimate flagged as PHISHING)

---

## Success Indicators

You'll know it's working when:

✅ All 21 nodes show green checkmarks
✅ Tool API calls return realistic data
✅ Agent reasoning includes multi-factor analysis
✅ Some emails trigger "Skeptical Review" (low confidence path)
✅ Final accuracy >= 75%
✅ Flag appears in results
✅ Score >= 800

---

## Quick Reference: Email Classification Tips

**Clear PHISHING indicators:**
- Domain reputation < 50
- Urgency + verification request + suspicious link
- SPF/DKIM/DMARC all FAIL
- Homograph indicators + noreply

**Clear LEGITIMATE indicators:**
- Domain reputation > 80
- SPF/DKIM/DMARC all PASS
- Normal business language
- From known company domain

**Edge cases (need multi-factor):**
- Legitimate company using "URGENT" (check domain reputation)
- Suspicious link but trusted domain (check SPF/DKIM)
- Low urgency but spoofed domain (check header analysis)
