# Architecture Diagram

## High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface"
        UI[Streamlit Web UI<br/>Campaign Creation & Monitoring]
    end
    
    subgraph "API Layer"
        API[API Gateway<br/>FastAPI + REST]
    end
    
    subgraph "Event Bus"
        NATS[NATS JetStream<br/>Event-Driven Communication]
    end
    
    subgraph "Core Services"
        CE[Context Enricher<br/>Locale-specific context]
        CG[Creative Generator<br/>GPT-4o-mini]
        IG[Image Generator<br/>DALL-E 3]
        BC[Brand Composer<br/>AI Logo Placement]
        TO[Text Overlay<br/>Multi-format Export]
    end
    
    subgraph "Supporting Services"
        GDQ[Guardian DLQ<br/>Failure Monitoring]
    end
    
    subgraph "Storage"
        S3[MinIO/S3<br/>Asset Storage]
        MONGO[MongoDB<br/>Campaign Metadata]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>DALL-E 3 + GPT-4o-mini]
    end
    
    UI -->|HTTP/REST| API
    API -->|Publish Events| NATS
    API <-->|Read/Write| MONGO
    
    NATS -->|context.enrich.request| CE
    NATS -->|creative.generate.request| CG
    NATS -->|creative.generate.done| IG
    NATS -->|image.generated| BC
    NATS -->|brand.composed| TO
    
    CE -->|context.enrich.ready| NATS
    CG -->|creative.generate.done| NATS
    IG -->|image.generated| NATS
    BC -->|brand.composed| NATS
    TO -->|text.overlay.done| NATS
    
    CE -->|Generate Context| OPENAI
    CG -->|Generate Content| OPENAI
    IG -->|Generate Images| OPENAI
    BC -->|AI Logo Analysis| OPENAI
    
    IG -->|Upload Images| S3
    BC -->|Upload Branded| S3
    TO -->|Upload Final Assets| S3
    
    CE <-->|Store Context| MONGO
    CG <-->|Store Creatives| MONGO
    IG <-->|Store Images| MONGO
    BC <-->|Update Metadata| MONGO
    TO <-->|Update Status| MONGO
    
    NATS -.->|Failed Messages| GDQ
    GDQ -->|Alert| UI
    
    style UI fill:#e1f5ff
    style API fill:#fff3e0
    style NATS fill:#f3e5f5
    style OPENAI fill:#e8f5e9
    style S3 fill:#fff9c4
    style MONGO fill:#fff9c4
```

## Data Flow: Campaign Creation to Final Assets

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant API as API Gateway
    participant NATS as NATS JetStream
    participant CE as Context Enricher
    participant CG as Creative Generator
    participant IG as Image Generator
    participant BC as Brand Composer
    participant TO as Text Overlay
    participant OpenAI as OpenAI API
    participant S3 as MinIO/S3
    participant DB as MongoDB

    User->>UI: Create Campaign
    UI->>API: POST /campaigns
    API->>DB: Save Campaign
    API->>NATS: Publish briefs.ingested
    API-->>UI: 202 Accepted
    
    NATS->>CE: context.enrich.request
    CE->>OpenAI: Generate Context (GPT-4o-mini)
    CE->>DB: Store Context Pack
    CE->>NATS: Publish context.enrich.ready
    
    NATS->>CG: creative.generate.request
    CG->>OpenAI: Generate Content (GPT-4o-mini)
    CG->>DB: Store Creative
    CG->>NATS: Publish creative.generate.done
    
    NATS->>IG: creative.generate.done
    IG->>OpenAI: Generate Images (DALL-E 3 × 4 aspect ratios)
    OpenAI-->>IG: Image Data
    IG->>S3: Upload Images
    IG->>DB: Store Image Metadata
    IG->>NATS: Publish image.generated
    
    NATS->>BC: image.generated
    BC->>S3: Download Image
    BC->>OpenAI: Analyze for Logo Placement (GPT-4o-mini Vision)
    OpenAI-->>BC: Optimal Position + Reasoning
    BC->>BC: Apply Logo + Brand Colors
    BC->>S3: Upload Branded Image
    BC->>DB: Update with Placement Info
    BC->>NATS: Publish brand.composed
    
    NATS->>TO: brand.composed
    TO->>S3: Download Branded Image
    TO->>TO: Overlay Text (4 aspect ratios)
    TO->>S3: Upload Final Assets (1x1, 4x5, 9x16, 16x9)
    TO->>DB: Update Campaign Status
    TO->>NATS: Publish text.overlay.done
    
    NATS->>API: creative.ready_for_review
    API->>UI: Real-time Update
    UI-->>User: Campaign Ready!
```

## Stakeholder Views

### Creative Lead View

```mermaid
graph LR
    subgraph "Creative Lead Workflow"
        A[Create Campaign<br/>Brief] --> B[AI Generates<br/>Variants]
        B --> C[Review Images<br/>& Copy]
        C --> D{Approve?}
        D -->|Yes| E[Assets Ready<br/>for Export]
        D -->|No| F[Request<br/>Revision]
        F --> B
    end
    
    style A fill:#e1f5ff
    style C fill:#fff3e0
    style E fill:#e8f5e9
```

**Key Features:**
- Real-time campaign status dashboard
- Visual preview of all variants
- One-click approval/revision
- AI-powered logo placement (no manual config)

### Ad Operations View

```mermaid
graph TB
    subgraph "Asset Management"
        A[Campaign<br/>Approved] --> B[S3 Storage<br/>Organized by Locale/Format]
        B --> C[4 Aspect Ratios<br/>1x1, 4x5, 9x16, 16x9]
        C --> D[Presigned URLs<br/>for Download]
        D --> E[Deploy to<br/>Ad Platforms]
    end
    
    style B fill:#fff9c4
    style C fill:#e8f5e9
```

**Key Features:**
- Automatic multi-format generation
- S3 storage organized by locale/aspect ratio
- Bulk download capabilities
- Presigned URLs for easy sharing

### IT/Engineering View

```mermaid
graph TB
    subgraph "System Reliability"
        A[Health Checks] --> B[Service<br/>Monitoring]
        B --> C{Healthy?}
        C -->|Yes| D[Continue<br/>Processing]
        C -->|No| E[DLQ<br/>Guardian]
        E --> F[Alert<br/>Operations]
        E --> G[Retry<br/>Logic]
    end
    
    style B fill:#e1f5ff
    style E fill:#ffebee
    style F fill:#ffebee
```

**Key Features:**
- Event-driven architecture (NATS)
- Dead Letter Queue for failed messages
- Structured logging with correlation IDs
- Health checks and metrics endpoints
- Docker Compose for easy deployment

### Legal/Compliance View

```mermaid
graph LR
    subgraph "Compliance Pipeline"
        A[Campaign<br/>Input] --> B[Brand Guidelines<br/>Check]
        B --> C[Banned Words<br/>Detection]
        C --> D[Legal Guidelines<br/>Validation]
        D --> E{Compliant?}
        E -->|Yes| F[Approve]
        E -->|No| G[Flag &<br/>Alert]
    end
    
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style G fill:#ffebee
```

**Key Features:**
- Configurable banned words per locale
- Legal guidelines field
- Compliance validation stage
- All decisions logged with timestamps
- Audit trail available

## Technology Stack

```mermaid
graph TB
    subgraph "Frontend"
        UI[Streamlit<br/>Python Web Framework]
    end
    
    subgraph "Backend"
        API[FastAPI<br/>REST API]
        WORKERS[Microservices<br/>Python Workers]
    end
    
    subgraph "Message Bus"
        NATS[NATS JetStream<br/>Event Streaming]
    end
    
    subgraph "Data Layer"
        MONGO[MongoDB<br/>Document Store]
        S3[MinIO/S3<br/>Object Storage]
    end
    
    subgraph "AI/ML"
        OPENAI[OpenAI API<br/>DALL-E 3 + GPT-4o-mini]
    end
    
    subgraph "Infrastructure"
        DOCKER[Docker Compose<br/>Container Orchestration]
    end
    
    UI --> API
    API --> NATS
    WORKERS --> NATS
    WORKERS --> MONGO
    WORKERS --> S3
    WORKERS --> OPENAI
    DOCKER --> UI
    DOCKER --> API
    DOCKER --> WORKERS
    DOCKER --> NATS
    DOCKER --> MONGO
    DOCKER --> S3
```

## Scaling Strategy

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        A[Low Load<br/>2 pods each] --> B{Queue<br/>Depth?}
        B -->|< 10 msgs| A
        B -->|> 10 msgs| C[Scale Up<br/>5-20 pods]
        C --> D[Process<br/>Faster]
        D --> E{Queue<br/>Empty?}
        E -->|No| C
        E -->|Yes| F[Scale Down<br/>2 pods]
        F --> A
    end
    
    style A fill:#e8f5e9
    style C fill:#fff3e0
    style F fill:#e8f5e9
```

**Scaling Properties:**
- **Image Generator**: GPU-intensive, scales 2→20 pods based on queue depth
- **Context Enricher**: CPU-bound, scales 2→10 pods
- **Brand Composer**: Memory-intensive (image processing), scales 2→10 pods
- **Text Generator**: LLM API calls, scales 2→15 pods
- **Overlay Composer**: CPU-bound, scales 2→10 pods

## Event Flow

```mermaid
graph LR
    A[briefs.ingested] --> B[context.enrich.request]
    B --> C[context.enrich.ready]
    C --> D[creative.generate.request]
    D --> E[creative.generate.done]
    E --> F[creative.brand.compose.request]
    F --> G[creative.brand.compose.done]
    G --> H[creative.copy.generate.request]
    H --> I[creative.copy.generate.done]
    I --> J[creative.overlay.request]
    J --> K[creative.overlay.done]
    K --> L[creative.ready_for_review]
    
    style A fill:#e1f5ff
    style L fill:#e8f5e9
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development (Docker Compose)"
        DC[docker-compose.yml<br/>All services on localhost]
    end
    
    subgraph "Production (Kubernetes)"
        K8S[Kubernetes Cluster]
        ING[Ingress<br/>Load Balancer]
        SVC[Services<br/>6 core + 2 supporting]
        HPA[Horizontal Pod<br/>Autoscaler]
        PV[Persistent Volumes<br/>MongoDB + MinIO]
    end
    
    DC -->|Deploy| K8S
    ING --> SVC
    SVC --> HPA
    SVC --> PV
    
    style DC fill:#e1f5ff
    style K8S fill:#e8f5e9
```

---

## Diagram Usage

### For Presentations
1. Copy the Mermaid code blocks
2. Paste into [Mermaid Live Editor](https://mermaid.live)
3. Export as PNG/SVG for slides

### For Documentation
- GitHub, GitLab, and many markdown viewers support Mermaid natively
- Diagrams will render automatically

### For Lucidchart/Draw.io
Use these diagrams as reference to create more polished versions with:
- Custom icons
- Brand colors
- Additional annotations
