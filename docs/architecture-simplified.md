# Simplified Architecture Diagram

## High-Level System Architecture (Simplified)

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
    
    subgraph "Storage"
        S3[MinIO/S3<br/>Asset Storage]
        MONGO[MongoDB<br/>Campaign Metadata]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>DALL-E 3 + GPT-4o-mini]
    end
    
    UI -->|HTTP/REST| API
    API --> NATS
    API <--> MONGO
    
    NATS --> CE
    NATS --> CG
    NATS --> IG
    NATS --> BC
    NATS --> TO
    
    CE --> NATS
    CG --> NATS
    IG --> NATS
    BC --> NATS
    TO --> NATS
    
    CE --> OPENAI
    CG --> OPENAI
    IG --> OPENAI
    BC --> OPENAI
    
    IG --> S3
    BC --> S3
    TO --> S3
    
    CE <--> MONGO
    CG <--> MONGO
    IG <--> MONGO
    BC <--> MONGO
    TO <--> MONGO
    
    style UI fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    style API fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style NATS fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style CE fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style CG fill:#fff9c4,stroke:#f9a825,stroke-width:3px
    style IG fill:#ffebee,stroke:#d32f2f,stroke-width:3px
    style BC fill:#e0f2f1,stroke:#00897b,stroke-width:3px
    style TO fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    style OPENAI fill:#f1f8e9,stroke:#689f38,stroke-width:3px
    style S3 fill:#fff8e1,stroke:#ffa000,stroke-width:3px
    style MONGO fill:#fff8e1,stroke:#ffa000,stroke-width:3px
```

## Notes

**Simplifications from original diagram:**
- ✅ Removed Guardian DLQ and failure monitoring
- ✅ Removed message/event names from arrows
- ✅ Added distinct colors for each service (using fill colors and stroke borders)
- ✅ Kept core architecture and data flow

**Color Legend:**
- **Blue (UI):** User interface layer
- **Orange (API):** API gateway and orchestration
- **Purple (NATS):** Event bus infrastructure
- **Green (Context Enricher):** Context generation service
- **Yellow (Creative Generator):** Content generation service
- **Red (Image Generator):** Image generation service (DALL-E 3)
- **Teal (Brand Composer):** Logo placement and branding service
- **Pink (Text Overlay):** Text overlay and export service
- **Light Green (OpenAI):** External AI services
- **Amber (Storage):** Data persistence (MongoDB & S3)
