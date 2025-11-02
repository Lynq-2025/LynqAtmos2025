# Green Signal - Advanced Agentic Workflow Architecture

## 🧠 What Makes This Truly "Agentic"

This workflow implements **ReAct (Reasoning + Acting)** pattern with:
- **Multi-agent reasoning chains** (not just single LLM calls)
- **Adaptive decision-making** based on confidence scores
- **Hierarchical agent delegation** (primary → expert → meta-validator)
- **Cross-validation at scale** (batch-level pattern analysis)
- **Self-reflection and adjustment** mechanisms

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTIC LOOP PATTERN                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. OBSERVE (Fetch & Analyze Patterns)                      │
│       ↓                                                       │
│  2. REASON (Primary Agent - Multi-factor analysis)          │
│       ↓                                                       │
│  3. ACT (Make Decision with Confidence)                     │
│       ↓                                                       │
│  4. CHECK (Validate Confidence Threshold)                   │
│       ├─→ HIGH: Accept ✓                                   │
│       └─→ LOW: Escalate to Expert Agent                    │
│       ↓                                                       │
│  5. EXPERT_REVIEW (Challenge & Refine)                     │
│       ↓                                                       │
│  6. META_VALIDATE (Batch-level Cross-check)                │
│       ↓                                                       │
│  7. ADAPT (Adjust based on patterns)                        │
│       ↓                                                       │
│  8. SUBMIT (Final action)                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Node Architecture

### **Phase 1: Observation & Initialization**

#### 1. **Start Agent**
- Manual trigger to begin agentic workflow
- Represents agent awakening

#### 2. **Fetch Emails**
- Agent's first tool: HTTP request to retrieve challenge data
- **Tool invocation**: Gathering information for reasoning

#### 3. **Initialize Agent State**
- **Agentic feature**: Sets up internal state/memory
- Initializes hypotheses: 35% phishing, 65% legitimate
- Creates tracking structures for adaptive learning
- **Output**:
  ```json
  {
    "emails": [...],
    "totalCount": 20,
    "phishingHypothesis": 0.35,
    "legitimateHypothesis": 0.65,
    "agentState": "INITIALIZED"
  }
  ```

#### 4. **Agent: Analyze Email Patterns**
- **Agentic reasoning**: Pre-analysis pattern recognition
- Sets up batch processing strategy
- Tracks classification rounds for adaptive behavior
- Establishes confidence threshold (0.7)
- **Output**:
  ```json
  {
    "processed": [],
    "pendingAnalysis": [...20 emails...],
    "classificationRound": 1,
    "confidence_threshold": 0.7,
    "agentState": "ANALYZING_PATTERNS"
  }
  ```

---

### **Phase 2: Primary Reasoning Agent**

#### 5. **Batch Process Emails**
- Splits array into individual items (one per execution)
- Each email gets full reasoning context

#### 6. **Agent: Reasoning & Classification** ⭐ PRIMARY AGENT
- **Agentic reasoning chain** (not just prediction):
  ```
  OBSERVE → REASON → ASSESS → DECIDE
  ```
- **Inputs provided to agent**:
  - Current classification round
  - Confidence threshold
  - Previously processed emails (context window)
  - Current email being analyzed

- **Prompt forces structured reasoning**:
  ```
  1. OBSERVE: Identify key indicators
     - Urgency language patterns
     - Verification request type
     - Suspicious link patterns
     - Domain spoofing attempts
  
  2. REASON: Cross-reference patterns
     - Compare against earlier emails
     - Identify similar attack vectors
     - Look for consistency
  
  3. ASSESS: Multi-factor confidence
     - Risk factors: urgency, verification, links, spoofing
     - Calculate composite confidence (0.0-1.0)
  
  4. DECIDE: Provide classification + reasoning
  ```

- **Agent output includes**:
  ```json
  {
    "reasoning_chain": {
      "observed_indicators": ["urgency", "verification_request"],
      "pattern_matches": "Similar to email #3 - fake security alert",
      "risk_factors": {
        "urgency": true,
        "verification_request": true,
        "suspicious_link": true,
        "domain_spoofing": false
      },
      "confidence_score": 0.92,
      "decision_rationale": "Strong phishing indicators..."
    },
    "classification": "PHISHING",
    "reasoning_summary": "Contains urgent language and verification request",
    "adaptive_notes": "Watch for this pattern in remaining emails"
  }
  ```

#### 7. **Parse Reasoning Output**
- Extracts structured reasoning from LLM response
- Prepares data for confidence validation

---

### **Phase 3: Adaptive Decision Making**

#### 8. **Check: High Confidence?** ⭐ DECISION NODE
- **Agentic branching**: Adaptive routing based on confidence
- **Threshold**: 0.7 (70% confidence)
- **Decision logic**:
  ```
  IF confidence >= 0.7:
    → Path A: Accept primary result (fast track)
  ELSE:
    → Path B: Escalate to expert agent (careful review)
  ```

This is **true agentic behavior**: Agent doesn't blindly accept every classification. Low-confidence decisions get expert review.

#### 9. **Accept: Primary Agent Result**
- **Path A (high confidence)**
- Agent trusts its own reasoning
- Formats result with confidence metadata

#### 10. **Agent: Expert Review (Low Confidence)** ⭐ SECONDARY AGENT
- **Path B (low confidence < 0.7)**
- **Hierarchical delegation**: Primary agent hands off uncertain cases
- **Expert agent task**:
  ```
  1. CHALLENGE: Question primary agent's reasoning
  2. SEARCH: Look for subtle indicators missed
  3. ANALYZE: Industry-specific context
  4. OVERRIDE: Can disagree with primary agent
  ```
- **Expert prompt forces adversarial review**:
  - "Challenge the primary agent's reasoning"
  - "Look for indicators the primary agent may have missed"
  - "Consider context and industry-specific patterns"
  - "Provide FINAL classification with high confidence"

- **Expert output**:
  ```json
  {
    "expert_analysis": "Detailed deep-dive analysis",
    "primary_agent_assessment": "Primary agent was correct/incorrect",
    "overrides": true/false,
    "final_classification": "PHISHING",
    "final_confidence": 0.95,
    "reasoning_summary": "Expert summary"
  }
  ```

#### 11. **Parse Expert Output**
- Extracts expert's final decision
- Flags if expert overrode primary agent

#### 12. **Merge: Combine Agent Results**
- Consolidates both paths (high confidence + expert review)
- Tracks which agent made final decision
- Includes metadata for auditing

---

### **Phase 4: Aggregation & Meta-Analysis**

#### 13. **Finalize Batch Results**
- Recombines all 20 email results
- Waits for all iterations to complete

#### 14. **Agent: Aggregate Statistics** 📊 ANALYSIS NODE
- **Meta-level reasoning**:
  - Total processed: 20
  - PHISHING count: X
  - LEGITIMATE count: Y
  - Phishing percentage: Z%
- Prepares data for batch-level validation

#### 15. **Agent: Meta-Validator (Batch Analysis)** ⭐ META-AGENT
- **Highest-level agentic reasoning**:
  - Analyzes entire batch for consistency
  - Cross-validates individual classifications against batch patterns
  - Detects anomalies and inconsistencies
  - Can recommend adjustments

- **Meta-agent reasoning**:
  ```
  1. PATTERN_CHECK: Is phishing percentage reasonable?
     - Expected: 30-40% in real data
     - Actual: Z%
     - Deviation acceptable?
  
  2. CLUSTER_ANALYSIS: Are there suspicious clusters?
     - All "urgent security alerts" classified same way?
     - Internal emails all legitimate?
     - Marketing emails show pattern?
  
  3. ANOMALY_DETECTION: Which emails seem misclassified?
     - Email that contradicts cluster pattern?
     - High-confidence email that breaks trend?
  
  4. RECOMMENDATION: Should adjustments be made?
  ```

- **Meta-validator output**:
  ```json
  {
    "batch_analysis": "Analysis of overall patterns",
    "anomalies_detected": ["Email #7 seems misclassified", "Unusual cluster of urgent alerts"],
    "recommendations": ["Consider re-evaluating email #7"],
    "validation_passed": true,
    "adjusted_results": [ ... modified results ... ]
  }
  ```

#### 16. **Apply Meta-Agent Adjustments**
- Applies refinements recommended by meta-validator
- Final quality assurance step

---

## Key Agentic Features

### **1. Reasoning Chains (Not Just Predictions)**
- Each agent provides explicit reasoning
- Multi-factor analysis (urgency + links + spoofing + etc.)
- Confidence scores based on reasoning depth

### **2. Adaptive Routing**
- Primary agent confidence determines next action
- Low confidence → escalate to expert
- Not all emails processed identically

### **3. Hierarchical Delegation**
```
Primary Agent (fast, general-purpose)
    ↓ (if low confidence)
Expert Agent (careful, specialized)
    ↓ (combines all results)
Meta-Validator (batch-level oversight)
```

### **4. Self-Reflection**
- Agents acknowledge uncertainty
- Agents track patterns from earlier decisions
- Meta-agent reviews entire batch for consistency

### **5. Tool Use**
- HTTP requests (fetch emails)
- LLM calls as "tools" for reasoning
- Conditional branching based on tool outputs

### **6. Adaptive Learning**
- Later emails processed with context from earlier ones
- Agent state tracks classification patterns
- Meta-validator adjusts classifications for consistency

---

## Data Flow Example

```
Email #1: "Urgent: Verify your account"
├─ Primary Agent Reasoning:
│  ├─ Observe: urgency, verification request, suspicious link
│  ├─ Risk score: 0.85
│  ├─ Confidence: 0.92 (HIGH)
│  └─ Classify: PHISHING ✓
└─ Result: Accept primary classification

Email #8: "Please review your recent transactions"
├─ Primary Agent Reasoning:
│  ├─ Observe: verification request, no urgency, corporate sender
│  ├─ Risk score: 0.45
│  ├─ Confidence: 0.58 (LOW) ⚠️
│  └─ Classify: UNCERTAIN
├─ Expert Agent Review:
│  ├─ Challenge: Is this actually suspicious?
│  ├─ Analyze: Similar to legitimate corporate emails
│  ├─ Override: Primary agent was too cautious
│  └─ Final: LEGITIMATE (confidence: 0.85)
└─ Result: Expert overrides primary agent

Meta-Validator Review (all 20 emails):
├─ Phishing count: 7
├─ Pattern: All phishing emails have urgency + verification
├─ Pattern: All legitimate are normal business comms
├─ Anomalies: Email #15 claims PHISHING but lacks typical indicators
├─ Recommendation: Reconsider email #15
└─ Final adjustment: Apply recommendations
```

---

## Why This Is "True Agentic AI"

| Feature | Simple Gen AI | This Agentic Workflow |
|---------|---------------|----------------------|
| Decision Making | Single LLM call | Multi-step reasoning chain |
| Confidence | N/A | Explicit confidence scores |
| Uncertainty Handling | Always commits | Low confidence → escalate |
| Self-Review | None | Expert review of uncertain cases |
| Batch Analysis | Process individually | Meta-level cross-validation |
| Adaptation | Static | Learns from earlier decisions |
| Fallback Strategy | None | Hierarchical delegation |
| Reasoning Transparency | Black box | Explicit reasoning chains |

---

## Implementation Checklist

- [ ] Configure OpenAI API credentials for LLM nodes
- [ ] Set model to GPT-4 or GPT-4-turbo (for better reasoning)
- [ ] Start backend server: `uvicorn main:app --host 0.0.0.0 --port 3000`
- [ ] Import `green-signal_agentic_workflow.json` into n8n
- [ ] Click "Execute" on Start Agent
- [ ] Monitor execution for agent reasoning chains
- [ ] Check final meta-validator output for consistency analysis
- [ ] Verify flag capture if all classifications correct

---

## Monitoring Agent Behavior

Check these nodes in execution logs:

1. **Agent: Reasoning & Classification**
   - Look for reasoning_chain in output
   - Check confidence scores (should be varied)

2. **Check: High Confidence?**
   - Count how many emails go to expert review
   - Expected: ~30-40% should be escalated (uncertain)

3. **Agent: Expert Review**
   - How often does expert override?
   - Expert confidence usually higher

4. **Agent: Meta-Validator**
   - Look for detected anomalies
   - Check recommendations for adjustments

---

## Extension Ideas

1. **Add Memory**: Store email patterns in database for future sessions
2. **Add Voting**: Use 3 independent agents + majority vote
3. **Add Feedback Loop**: If submission fails, adapt and retry
4. **Add Explainability**: Generate human-readable report of reasoning
5. **Add Uncertainty Sampling**: Use confidence to determine which emails need human review
6. **Add Few-Shot Learning**: Prime agents with known examples before classification
