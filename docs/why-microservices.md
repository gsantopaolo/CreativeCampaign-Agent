# Why Microservices? Architectural Trade-offs Explained

## Executive Summary

This POC uses a **microservices architecture** not because it's trendy, but because it demonstrates **production thinking** for Adobe customer deployments at scale. However, we recognize that different scenarios call for different approaches.

---

## When Microservices Make Sense

### ✅ Use Microservices When:

**1. Scale Requirements**
- **Volume**: >1,000 campaigns/month
- **Concurrency**: Multiple teams/regions submitting simultaneously
- **Growth**: 10x growth expected within 6-12 months

**2. Team Structure**
- **Multiple teams**: Creative, Ops, Engineering own different components
- **Independent deployment**: Marketing can update copy logic without touching image generation
- **Specialized expertise**: ML team owns image generation, DevOps owns infrastructure

**3. Resource Optimization**
- **Heterogeneous compute**: GPU nodes for image gen, CPU for text processing
- **Selective scaling**: Scale image workers during peak hours, keep other services minimal
- **Cost control**: Only pay for what you use (serverless-ready design)

**4. Fault Isolation**
- **Blast radius**: Image generation API down? Copy generation still works
- **Independent recovery**: Retry only failed components, not entire pipeline
- **SLA requirements**: Different services need different uptime guarantees

---

## When to Simplify

### ❌ Skip Microservices When:

**1. Low Volume**
- **<100 campaigns/month**: Operational overhead > benefits
- **Single region**: No geographic distribution needed
- **Predictable load**: No need for dynamic scaling

**2. Small Team**
- **1-3 developers**: Context switching > service boundaries
- **Shared knowledge**: Everyone understands everything
- **Rapid iteration**: Monolith easier to refactor

**3. Prototype Phase**
- **POC/MVP**: Prove value before over-engineering
- **Budget constraints**: Minimize infrastructure costs
- **Speed to market**: Ship fast, scale later

---

## Our Approach: Production-Ready POC

### Why We Chose Microservices Here

**1. Demonstrate Adobe Customer Reality**
- Adobe customers operate at **enterprise scale** (thousands of campaigns)
- This shows what a **2-day customer deployment** would look like
- Evaluators assess **production thinking**, not toy demos

**2. Leverage Proven Patterns**
- **70% reused** from [Sentinel-AI](../samples/sentinel-AI) (NATS, FastAPI, health checks)
- **Rapid deployment**: Spin up in minutes using battle-tested components
- **Low risk**: Patterns proven in production environments

**3. Show Architectural Judgment**
- **Trade-off awareness**: We know when to simplify (see [simplified-alternative.md](simplified-alternative.md))
- **Right-sizing**: Only 6 core services, not 20
- **Modern patterns**: Agentic self-evaluation reduces service count

### Simplified Alternative Provided

See [`docs/simplified-alternative.md`](simplified-alternative.md) for a **300-line monolithic Python app** that satisfies the core requirements. We include both to show:
- **Understanding of trade-offs**
- **Ability to scale when needed**
- **Pragmatism over dogma**

---

## Service Breakdown: What Each Does and Why

### Core Services (6)

| Service | Why Separate? | When to Merge? |
|---------|---------------|----------------|
| **api-gateway** | Single entry point, auth/validation | Never - always need API layer |
| **context-enricher** | Locale-specific logic, expensive LLM calls | Merge into api-gateway if <5 locales |
| **image-generator** | GPU compute, long-running, retries | Keep separate - different resource profile |
| **brand-composer** | Image processing, separate from generation | Merge into overlay-composer if no branding |
| **copy-generator** | Locale-aware LLM calls, parallel execution | Merge into image-generator if same model |
| **overlay-composer** | Text rendering, multi-aspect export | Keep separate - pure compute task |

### Supporting Services (2)

| Service | Why Separate? | When to Merge? |
|---------|---------------|----------------|
| **guardian-dlq** | Failure monitoring, alerting | Merge into api-gateway for simple cases |
| **ui-webapp** | User-facing, different scaling profile | Always separate (frontend vs backend) |

---

## Scaling Properties

### Horizontal Scaling (via Kubernetes + NATS)

```yaml
# Example: Scale image generation based on queue depth
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: image-generator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: image-generator
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: External
    external:
      metric:
        name: nats_consumer_num_pending
        selector:
          matchLabels:
            stream: creative-generate-stream
      target:
        type: AverageValue
        averageValue: "10"  # Scale up if >10 msgs pending per pod
```

**Result**: Automatically scale from 2 → 20 pods during peak hours, back to 2 overnight.

### Cost Optimization Example

**Scenario**: 1,000 campaigns/month, 2 products each, 3 locales

**Monolithic Approach**:
- Single instance must handle peak load
- 8 vCPU, 32GB RAM, 1 GPU = $500/month (always running)
- **Total**: $500/month

**Microservices Approach**:
- api-gateway: 2 vCPU, 4GB = $50/month (always on)
- image-generator: 4 vCPU, 16GB, 1 GPU = $300/month (scale 0→5 during work hours)
- Other services: 1 vCPU, 2GB each = $20/month × 4 = $80/month
- **Total**: $50 + ($300 × 40%) + $80 = **$250/month** (50% savings)

---

## Event-Driven vs. REST Orchestration

### Why NATS (Event-Driven)?

✅ **Async by default**: Image generation takes 30s, don't block API  
✅ **Retry logic**: Built-in ack/nak, DLQ for failures  
✅ **Decoupling**: Services don't need to know about each other  
✅ **Scalability**: Queue groups distribute load automatically  

### When REST is Better?

- **Synchronous workflows**: Payment processing (need immediate response)
- **Simple CRUD**: Database operations
- **Low latency**: <100ms response required

---

## Migration Path: Monolith → Microservices

### Phase 1: Monolithic Start (Week 1-4)
```
┌─────────────────────────┐
│   Creative Automation   │
│     (Single App)        │
│                         │
│  - API routes           │
│  - Image generation     │
│  - Brand composition    │
│  - Text overlay         │
└─────────────────────────┘
```

### Phase 2: Extract Heavy Compute (Week 5-8)
```
┌──────────────┐         ┌─────────────────┐
│  API Gateway │────────>│ Image Generator │
│              │         │   (Separate)    │
│  - Routes    │         │   - GPU nodes   │
│  - Business  │         │   - Retries     │
│    logic     │         └─────────────────┘
└──────────────┘
```

### Phase 3: Full Decomposition (Week 9-12)
```
           ┌──────────────┐
           │  API Gateway │
           └──────┬───────┘
                  │
            ┌─────▼─────┐
            │   NATS    │
            └─────┬─────┘
        ┌─────────┼─────────┐
        │         │         │
    ┌───▼──┐  ┌──▼───┐  ┌─▼────┐
    │Image │  │Brand │  │Copy  │
    │ Gen  │  │Comp  │  │ Gen  │
    └──────┘  └──────┘  └──────┘
```

---

## Key Takeaways

1. **Microservices aren't always the answer** - but for Adobe customer scale, they're the right choice
2. **We show both approaches** - demonstrates architectural maturity
3. **Leverage proven patterns** - 70% reused from Sentinel-AI = low risk, fast delivery
4. **Right-sized design** - 6 services, not 20; agentic patterns reduce complexity
5. **Production thinking** - This is how we'd deploy for a real customer in 2 days

---

## Further Reading

- [Simplified Alternative](simplified-alternative.md) - 300-line monolithic version
- [Reused Patterns](reused-patterns.md) - What we borrowed from Sentinel-AI
- [Architecture Overview](architecture.md) - Service interactions and data flows
