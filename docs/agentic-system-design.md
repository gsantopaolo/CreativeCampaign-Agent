# Agentic System Design

## Overview

This document describes the design of an AI-driven agent system that monitors, orchestrates, and optimizes the creative campaign pipeline. The system leverages the existing event-driven architecture (NATS JetStream) to provide intelligent automation, quality control, and proactive alerting.

---

## Agent Architecture

### Core Agent: Campaign Intelligence Agent

A single, intelligent agent that monitors the entire pipeline and makes decisions based on campaign state, asset inventory, and quality metrics.

```
┌─────────────────────────────────────────────────┐
│         Campaign Intelligence Agent             │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Monitor    │  │   Analyze    │           │
│  │  NATS Events │→ │  Campaign    │           │
│  │              │  │    State     │           │
│  └──────────────┘  └──────┬───────┘           │
│                            │                    │
│  ┌──────────────┐  ┌──────▼───────┐           │
│  │   Generate   │←─│   Decision   │           │
│  │    Alerts    │  │    Engine    │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
    [Alerts]            [Triggers]
```

---

## Agent Responsibilities

### 1. Campaign Brief Monitoring

**Trigger:** `briefs.ingested` event from NATS

**Actions:**
- Validate campaign brief completeness
- Check for required fields (campaign_id, products, locales)
- Verify asset availability (logo, brand colors)
- Assess campaign complexity (# products × # locales × # aspect ratios)

**Decision Logic:**
```python
if missing_required_fields:
    alert("Campaign brief incomplete", severity="error")
    halt_pipeline()
elif missing_optional_assets:
    alert("Optional assets missing", severity="warning")
    continue_with_defaults()
else:
    trigger_context_enrichment()
```

### 2. Automated Task Triggering

**Trigger:** Pipeline stage completion events

**Orchestration Flow:**
```
briefs.ingested
    ↓
[Agent Decision: Start context enrichment]
    ↓
context.enrich.ready
    ↓
[Agent Decision: Parallel image generation for all locale/product combinations]
    ↓
creative.generate.done (multiple)
    ↓
[Agent Decision: Brand composition when all images ready]
    ↓
creative.brand.compose.done (multiple)
    ↓
[Agent Decision: Text generation]
    ↓
creative.copy.generate.done (multiple)
    ↓
[Agent Decision: Multi-format overlay]
    ↓
creative.overlay.done (multiple)
    ↓
[Agent Decision: Mark campaign ready for review]
```

**Intelligence:**
- Waits for all parallel tasks to complete before triggering next stage
- Detects failures and routes to DLQ
- Adjusts parallelism based on system load
- Prioritizes campaigns based on deadlines

### 3. Variant Count & Diversity Tracking

**Trigger:** `creative.generate.done` events

**Metrics Tracked:**
```python
variant_metrics = {
    "campaign_id": "fall_2025_promo",
    "locale": "en",
    "product_id": "p01",
    "total_variants": 4,  # One per aspect ratio
    "aspect_ratios": ["1x1", "4x5", "9x16", "16x9"],
    "diversity_score": 0.85,  # Visual similarity analysis
    "generation_time_avg": 45.2,  # seconds
    "compliance_pass_rate": 1.0
}
```

**Diversity Analysis:**
- Compare image embeddings to measure visual diversity
- Flag if variants are too similar (diversity_score < 0.5)
- Recommend regeneration with different seeds

**Decision Logic:**
```python
if variant_count < 3:
    alert(f"Insufficient variants: {variant_count}/3 minimum", 
          severity="warning",
          action="Consider regenerating with different prompts")
elif diversity_score < 0.5:
    alert(f"Low diversity score: {diversity_score}",
          severity="info",
          action="Variants may be too similar")
```

### 4. Missing/Insufficient Asset Flagging

**Trigger:** Campaign creation, pipeline start

**Checks:**
```python
asset_checks = {
    "logo": {
        "required": True,
        "present": bool(campaign.brand.logo_s3_uri),
        "fallback": "Use default logo"
    },
    "brand_colors": {
        "required": False,
        "present": bool(campaign.brand.primary_color),
        "fallback": "Use system default (#000000)"
    },
    "products": {
        "required": True,
        "minimum": 2,
        "present": len(campaign.products),
        "fallback": None
    },
    "locales": {
        "required": True,
        "minimum": 1,
        "present": len(campaign.target_locales),
        "fallback": None
    },
    "variants_per_product": {
        "required": False,
        "minimum": 3,
        "present": count_variants(),
        "fallback": "Generate more variants"
    }
}
```

**Alert Examples:**
```
⚠️ Missing Logo
Campaign: fall_2025_promo
Issue: No logo uploaded
Impact: Using default logo
Action: Upload brand logo for better results

⚠️ Insufficient Variants
Campaign: fall_2025_promo
Product: p01, Locale: en
Issue: Only 2 variants generated (minimum 3 recommended)
Impact: Limited A/B testing options
Action: Regenerate with additional prompts
```

### 5. Alert & Logging Mechanism

**Alert Channels:**
```python
alert_config = {
    "ui": {
        "enabled": True,
        "method": "nats_publish",
        "topic": "alerts.ui",
        "real_time": True
    },
    "email": {
        "enabled": True,
        "method": "smtp",
        "recipients": ["creative-lead@company.com"],
        "severity_threshold": "warning"
    },
    "slack": {
        "enabled": False,
        "webhook": "https://hooks.slack.com/...",
        "severity_threshold": "error"
    },
    "logging": {
        "enabled": True,
        "level": "info",
        "structured": True,
        "correlation_id": True
    }
}
```

**Alert Structure:**
```json
{
  "alert_id": "alert_abc123",
  "timestamp": "2025-10-12T23:15:00Z",
  "campaign_id": "fall_2025_promo",
  "severity": "warning",
  "category": "asset_validation",
  "title": "Insufficient Variants Generated",
  "message": "Only 2 variants generated for product p01 in locale en. Minimum 3 recommended for effective A/B testing.",
  "context": {
    "product_id": "p01",
    "locale": "en",
    "variant_count": 2,
    "minimum_recommended": 3
  },
  "suggested_actions": [
    "Regenerate with additional prompt variations",
    "Adjust generation parameters",
    "Review product description for clarity"
  ],
  "correlation_id": "corr_xyz789"
}
```

---

## Model Context Protocol

### What Information the LLM Sees

When the agent needs to draft human-readable alerts or make decisions, it receives:

```python
llm_context = {
    # Campaign Metadata
    "campaign": {
        "id": "fall_2025_promo",
        "created_at": "2025-10-12T20:00:00Z",
        "deadline": "2025-10-15T00:00:00Z",
        "priority": "high",
        "products": [
            {"id": "p01", "name": "Vitamin C Serum"},
            {"id": "p02", "name": "Hydration Cream"}
        ],
        "locales": ["en", "de", "fr", "it"],
        "aspect_ratios": ["1x1", "4x5", "9x16", "16x9"]
    },
    
    # Current Pipeline State
    "pipeline": {
        "stage": "image_generation",
        "progress": 0.75,  # 75% complete
        "completed_tasks": 12,
        "total_tasks": 16,
        "failed_tasks": 0,
        "estimated_completion": "2025-10-12T23:30:00Z"
    },
    
    # Asset Inventory
    "assets": {
        "logo_present": True,
        "brand_colors_defined": True,
        "variants_generated": {
            "en": {"p01": 4, "p02": 4},
            "de": {"p01": 2, "p02": 0},  # Issue here
            "fr": {"p01": 0, "p02": 0},
            "it": {"p01": 0, "p02": 0}
        }
    },
    
    # Quality Metrics
    "quality": {
        "compliance_pass_rate": 1.0,
        "average_diversity_score": 0.82,
        "average_generation_time": 45.2,
        "error_rate": 0.0
    },
    
    # Historical Data
    "history": {
        "similar_campaigns": 5,
        "average_success_rate": 0.95,
        "common_issues": ["API rate limits", "Low diversity scores"]
    },
    
    # Stakeholder Preferences
    "stakeholders": {
        "creative_lead": {
            "alert_preference": "email",
            "notification_threshold": "warning"
        },
        "ad_operations": {
            "alert_preference": "ui",
            "notification_threshold": "info"
        }
    }
}
```

### LLM Prompt Template

```
You are an AI agent monitoring a creative campaign pipeline.

Campaign: {campaign.id}
Stage: {pipeline.stage}
Progress: {pipeline.progress}%

Issue Detected:
{issue_description}

Context:
{llm_context}

Task: Draft a clear, actionable alert for {stakeholder_role}.

Requirements:
1. Explain what happened in simple terms
2. Describe the impact on the campaign
3. Provide 2-3 specific actions to resolve
4. Include relevant metrics and deadlines
5. Maintain professional but friendly tone

Alert:
```

### Example LLM-Generated Alert

**Input:**
- Issue: Insufficient variants for DE locale
- Stakeholder: Creative Lead
- Context: 2/4 products have 0 variants

**Output:**
```
Subject: Action Required: Fall 2025 Campaign - German Locale Variants

Hi [Creative Lead],

I noticed an issue with the Fall 2025 campaign that needs your attention.

What Happened:
The image generation for the German (DE) locale is incomplete. We have:
- Product p01 (Vitamin C Serum): 2 variants ✓
- Product p02 (Hydration Cream): 0 variants ✗

Impact:
- Campaign cannot proceed to brand composition stage
- German market launch may be delayed
- Current deadline: Oct 15 (3 days away)

Recommended Actions:
1. Check if product p02 description is clear and detailed
2. Regenerate images for p02 with adjusted prompts
3. Consider using English variants as fallback if time-critical

Current Status:
- Overall progress: 75% complete
- Other locales: On track
- Estimated time to fix: 15-20 minutes

Let me know if you need help adjusting the generation parameters!

Best,
Campaign Intelligence Agent
```

---

## Implementation Notes

### Technology Stack

- **Event Monitoring:** NATS JetStream subscriptions
- **State Management:** MongoDB for campaign state
- **Decision Engine:** Python with async/await
- **LLM Integration:** OpenAI GPT-4o-mini for alert generation
- **Alerting:** NATS publish (UI), SMTP (email), Webhooks (Slack)

### Scalability

- **Stateless Agent:** Can run multiple instances
- **Event-Driven:** Reacts to NATS events, no polling
- **Parallel Processing:** Handles multiple campaigns simultaneously
- **Graceful Degradation:** Falls back to basic alerts if LLM unavailable

### Monitoring

```python
agent_metrics = {
    "campaigns_monitored": 150,
    "alerts_generated": 23,
    "decisions_made": 1200,
    "average_decision_time_ms": 45,
    "llm_calls": 23,
    "llm_success_rate": 1.0
}
```

---

## Benefits

1. **Proactive Issue Detection:** Catches problems before they impact deadlines
2. **Intelligent Orchestration:** Optimizes pipeline execution automatically
3. **Human-Readable Alerts:** LLM-generated messages are clear and actionable
4. **Reduced Manual Monitoring:** Stakeholders only alerted when action needed
5. **Data-Driven Decisions:** Uses historical data to improve recommendations
6. **Scalable:** Handles hundreds of campaigns without manual intervention

---

## Future Enhancements

1. **Predictive Analytics:** Predict campaign completion time based on historical data
2. **Auto-Remediation:** Automatically retry failed tasks with adjusted parameters
3. **A/B Test Suggestions:** Recommend which variants to test based on past performance
4. **Budget Optimization:** Alert when GenAI API costs exceed budget thresholds
5. **Quality Scoring:** ML model to predict campaign success before launch
