# Corpus Analyzer - Architecture Decision Records

<img src="assets/godsinwhite_radiologist_light.png" alt="Corpus Analyzer" width="100" style="margin-bottom: 20px;"/>

## Table of Contents

1. [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
2. [System Architecture](#system-architecture)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Deployment Architecture](#deployment-architecture)
5. [Implementation Guidelines](#implementation-guidelines)

## Overview

Corpus Analyzer is an AI platform built on the Agno framework that orchestrates specialized AI agents for analysis and research workflows. The architecture uses a multi-agent approach with a HALO (HALO Agent Interface) coordinator.

This document outlines the key architectural decisions, system design, and implementation guidelines for the Corpus Analyzer platform.

---

## Architecture Decision Records (ADRs)

### ADR-001: Multi-Agent Architecture Pattern

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team

#### Context
Need to create a medical AI system that can handle diverse medical queries requiring different types of expertise (imaging, research, data analysis, etc.).

#### Decision
Implement a multi-agent architecture using the Agno framework with specialized medical agents coordinated by a central HALO (HALO Agent Interface) team.

#### Rationale
- **Specialization**: Each agent can focus on specific medical domains
- **Scalability**: Easy to add new medical specialties as separate agents
- **Maintainability**: Isolated agent logic reduces complexity
- **Flexibility**: Agents can be combined dynamically based on query requirements

#### Consequences
- **Positive**: Clear separation of concerns, specialized expertise, extensible architecture
- **Negative**: Increased system complexity, inter-agent communication overhead

---

### ADR-002: Streamlit as Frontend Framework

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team

#### Context
Need a rapid development framework for creating an interactive medical AI interface with real-time streaming capabilities.

#### Decision
Use Streamlit as the primary frontend framework for the web application.

#### Rationale
- **Rapid Development**: Python-native, minimal boilerplate code
- **Real-time Streaming**: Native support for streaming responses
- **Medical UI Components**: Easy integration of medical imaging displays
- **Deployment**: Simple cloud deployment options

#### Consequences
- **Positive**: Fast development cycle, Python ecosystem integration, built-in state management
- **Negative**: Limited customization compared to React/Vue, Python-only ecosystem

---

### ADR-003: SQLite + LanceDB Hybrid Storage

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team

#### Context
Need efficient storage for both structured session data and unstructured medical knowledge with vector search capabilities.

#### Decision
Implement hybrid storage using SQLite for session management and LanceDB for vector-based knowledge storage.

#### Rationale
- **SQLite**: Lightweight, serverless, ACID compliance for sessions
- **LanceDB**: Vector search capabilities for medical knowledge retrieval
- **Hybrid Approach**: Optimal performance for different data types
- **Local Deployment**: No external database dependencies

#### Consequences
- **Positive**: No external database setup, optimal query performance, vector search capabilities
- **Negative**: Limited to single-node deployment, manual backup procedures

---

### ADR-004: OpenAI GPT-4o as Primary Model

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team

#### Context
Need a high-performance multimodal AI model capable of medical image analysis and text generation.

#### Decision
Use OpenAI GPT-4o as the primary model with support for alternative models (Claude, Gemini).

#### Rationale
- **Multimodal**: Native support for image and text processing
- **Medical Performance**: Strong performance on medical reasoning tasks
- **API Stability**: Reliable API with good documentation
- **Flexibility**: Model abstraction allows easy switching

#### Consequences
- **Positive**: High-quality medical analysis, multimodal capabilities, reliable service
- **Negative**: API costs, dependency on external service, rate limiting

---

### ADR-005: Factory Pattern for Agent Creation

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team

#### Context
Need consistent, maintainable way to create and configure medical agents with proper dependency injection.

#### Decision
Implement factory pattern for agent creation with dynamic discovery and configuration.

#### Rationale
- **Consistency**: Standardized agent creation process
- **Dependency Injection**: Proper model, memory, and knowledge injection
- **Dynamic Discovery**: Automatic agent registration and discovery
- **Configuration**: Centralized agent configuration management

#### Consequences
- **Positive**: Consistent agent interfaces, easy testing, maintainable code
- **Negative**: Additional abstraction layer, learning curve for new developers

---

### ADR-006: Medical Disclaimer and Compliance

**Status:** Accepted  
**Date:** 2024-08-26  
**Decision Makers:** Development Team, Legal Team

#### Context
Medical AI system requires appropriate disclaimers and compliance measures to ensure responsible use.

#### Decision
Implement comprehensive medical disclaimers and educational-use-only positioning.

#### Rationale
- **Legal Protection**: Clear disclaimers about educational/demonstration use
- **Ethical AI**: Responsible AI deployment in medical domain
- **User Safety**: Clear guidance about professional medical consultation
- **Compliance**: Alignment with medical AI best practices

#### Consequences
- **Positive**: Legal protection, ethical deployment, user safety
- **Negative**: Limited commercial medical applications, user experience friction

---

### ADR-007: Agno Framework Compatibility

**Status:** Accepted  
**Date:** 2024-09-15  
**Decision Makers:** Development Team

#### Context
The application was initially built with an older version of the Agno framework (v2) but needed to be updated to work with the current version, which has significant API changes.

#### Decision
Refactor the codebase to align with the current Agno framework API, focusing on session management, response streaming, and database access patterns.

#### Rationale
- **API Evolution**: The Agno framework has evolved with breaking changes
- **Session Management**: New session handling mechanisms in current Agno version
- **Streaming Responses**: Changes in async generator patterns for streaming
- **Database Access**: Storage attribute renamed to db in newer versions
- **Future Compatibility**: Ensure ongoing compatibility with framework updates

#### Consequences
- **Positive**: Full compatibility with current Agno framework, improved performance, better error handling
- **Negative**: Required significant refactoring of session management code, temporary regression in some features

---

### ADR-008: Dark Theme UI Implementation

**Status:** Accepted  
**Date:** 2024-09-18  
**Decision Makers:** Development Team, UX Team

#### Context
The medical application needed a dark theme option to reduce eye strain during extended use and provide a modern, professional appearance aligned with medical software standards.

#### Decision
Implement a comprehensive dark theme using custom CSS with Streamlit, ensuring consistent styling across all UI elements.

#### Rationale
- **User Experience**: Reduce eye strain during extended medical analysis sessions
- **Professional Appearance**: Align with modern medical software design standards
- **Accessibility**: Improve contrast and readability for various lighting conditions
- **Consistency**: Ensure uniform appearance across all application components
- **Theme Switching**: Allow users to select their preferred theme

#### Consequences
- **Positive**: Improved user experience, professional appearance, better accessibility
- **Negative**: Additional CSS maintenance overhead, potential Streamlit version compatibility issues

---

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit Web UI]
        Pages[Multiple Pages]
        Components[Reusable Components]
    end
    
    subgraph "Application Layer"
        HALO[HALO Team Coordinator]
        AgentFactory[Agent Factory]
        SessionMgr[Session Manager]
        ConfigMgr[Configuration Manager]
    end
    
    subgraph "Agent Layer"
        MedAgent[Medical Imaging Agent]
        ResAgent[Research Agent]
        DataAgent[Data Analysis Agent]
        CalcAgent[Calculator Agent]
        PubAgent[PubMed Agent]
        VisAgent[Visualizer Agent]
    end
    
    subgraph "Service Layer"
        ToolKit[Tool Orchestration]
        KnowledgeBase[Knowledge Management]
        Memory[Memory System]
        Storage[Session Storage]
    end
    
    subgraph "Data Layer"
        SQLite[(SQLite DB)]
        LanceDB[(LanceDB Vector Store)]
        FileSystem[(File System)]
        TempStorage[(Temporary Storage)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        PubMed[PubMed API]
        WebSearch[Web Search APIs]
    end
    
    UI --> HALO
    Pages --> Components
    HALO --> AgentFactory
    HALO --> SessionMgr
    AgentFactory --> MedAgent
    AgentFactory --> ResAgent
    AgentFactory --> DataAgent
    AgentFactory --> CalcAgent
    AgentFactory --> PubAgent
    AgentFactory --> VisAgent
    
    MedAgent --> ToolKit
    ResAgent --> ToolKit
    DataAgent --> ToolKit
    
    ToolKit --> KnowledgeBase
    ToolKit --> Memory
    Memory --> SQLite
    KnowledgeBase --> LanceDB
    SessionMgr --> Storage
    Storage --> SQLite
    
    HALO --> OpenAI
    PubAgent --> PubMed
    ResAgent --> WebSearch
    
    FileSystem --> TempStorage
```

### Agent Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant HALO as HALO Coordinator
    participant Agent as Specialized Agent
    participant Tools as Tool System
    participant KB as Knowledge Base
    participant API as External APIs
    
    User->>UI: Submit medical query with image
    UI->>HALO: Process request
    HALO->>HALO: Analyze query requirements
    HALO->>Agent: Delegate to Medical Imaging Agent
    Agent->>Tools: Use image analysis tools
    Tools->>API: Call OpenAI Vision API
    API-->>Tools: Return analysis results
    Agent->>KB: Search medical knowledge
    KB-->>Agent: Return relevant medical literature
    Agent->>HALO: Return comprehensive analysis
    HALO->>UI: Stream response to user
    UI->>User: Display structured medical report
```

### Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Input Processing"
        UserInput[User Input]
        ImageUpload[Image Upload]
        DocumentUpload[Document Upload]
        TextInput[Text Query]
    end
    
    subgraph "Request Processing"
        RequestParser[Request Parser]
        ContentValidator[Content Validator]
        SecurityCheck[Security Validation]
    end
    
    subgraph "Agent Orchestration"
        HALO[HALO Coordinator]
        AgentSelector[Agent Selection Logic]
        TaskDistributor[Task Distribution]
    end
    
    subgraph "Specialized Processing"
        ImageAnalysis[Medical Image Analysis]
        TextAnalysis[Medical Text Analysis]
        ResearchQuery[Literature Research]
        DataProcessing[Data Analysis]
    end
    
    subgraph "Knowledge Integration"
        VectorSearch[Vector Knowledge Search]
        LiteratureSearch[PubMed Search]
        ContextAggregation[Context Aggregation]
    end
    
    subgraph "Response Generation"
        ResponseSynthesis[Response Synthesis]
        MedicalDisclaimer[Medical Disclaimer Addition]
        FormatOutput[Output Formatting]
    end
    
    subgraph "Output Delivery"
        StreamingResponse[Real-time Streaming]
        SessionStorage[Session Persistence]
        UserInterface[UI Display]
    end
    
    UserInput --> RequestParser
    ImageUpload --> RequestParser
    DocumentUpload --> RequestParser
    TextInput --> RequestParser
    
    RequestParser --> ContentValidator
    ContentValidator --> SecurityCheck
    SecurityCheck --> HALO
    
    HALO --> AgentSelector
    AgentSelector --> TaskDistributor
    TaskDistributor --> ImageAnalysis
    TaskDistributor --> TextAnalysis
    TaskDistributor --> ResearchQuery
    TaskDistributor --> DataProcessing
    
    ImageAnalysis --> VectorSearch
    TextAnalysis --> VectorSearch
    ResearchQuery --> LiteratureSearch
    DataProcessing --> ContextAggregation
    
    VectorSearch --> ResponseSynthesis
    LiteratureSearch --> ResponseSynthesis
    ContextAggregation --> ResponseSynthesis
    
    ResponseSynthesis --> MedicalDisclaimer
    MedicalDisclaimer --> FormatOutput
    FormatOutput --> StreamingResponse
    
    StreamingResponse --> SessionStorage
    StreamingResponse --> UserInterface
```

## Deployment Architecture

### Local Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        subgraph "Application"
            StreamlitApp[Streamlit Application]
            AgnoFramework[Agno Framework]
            Agents[Medical Agents]
        end
        
        subgraph "Local Storage"
            SQLiteLocal[(SQLite Sessions)]
            LanceDBLocal[(LanceDB Knowledge)]
            TempFiles[(Temporary Files)]
        end
        
        subgraph "Configuration"
            EnvFile[.env Configuration]
            ConfigPy[config.py Settings]
        end
    end
    
    subgraph "External Services"
        OpenAIAPI[OpenAI API]
        PubMedAPI[PubMed API]
    end
    
    StreamlitApp --> SQLiteLocal
    StreamlitApp --> LanceDBLocal
    AgnoFramework --> OpenAIAPI
    Agents --> PubMedAPI
    StreamlitApp --> EnvFile
    StreamlitApp --> ConfigPy
```

### Production Cloud Deployment

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Application Load Balancer]
    end
    
    subgraph "Application Tier"
        App1[Streamlit Instance 1]
        App2[Streamlit Instance 2]
        App3[Streamlit Instance N]
    end
    
    subgraph "Data Tier"
        SharedStorage[(Shared File Storage)]
        SQLiteCluster[(SQLite Cluster)]
        LanceDBCluster[(LanceDB Cluster)]
    end
    
    subgraph "External Services"
        OpenAIAPI[OpenAI API]
        PubMedAPI[PubMed API]
        MonitoringService[Application Monitoring]
    end
    
    subgraph "Security Layer"
        WAF[Web Application Firewall]
        SSL[SSL Termination]
        APIGateway[API Gateway]
    end
    
    Internet --> WAF
    WAF --> SSL
    SSL --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> SharedStorage
    App2 --> SharedStorage
    App3 --> SharedStorage
    
    App1 --> SQLiteCluster
    App2 --> SQLiteCluster
    App3 --> SQLiteCluster
    
    App1 --> LanceDBCluster
    App2 --> LanceDBCluster
    App3 --> LanceDBCluster
    
    App1 --> APIGateway
    App2 --> APIGateway
    App3 --> APIGateway
    
    APIGateway --> OpenAIAPI
    APIGateway --> PubMedAPI
    
    App1 --> MonitoringService
    App2 --> MonitoringService
    App3 --> MonitoringService
```

---

## Implementation Guidelines

### Development Workflow

1. **Agent Development**
   - Follow factory pattern for new agents
   - Implement proper error handling and logging
   - Include comprehensive medical disclaimers
   - Test with various medical image formats

2. **UI Development**
   - Use Streamlit components consistently
   - Implement proper session state management
   - Ensure mobile responsiveness
   - Follow accessibility guidelines

3. **Testing Strategy**
   - Unit tests for individual agents
   - Integration tests for agent coordination
   - UI tests for user workflows
   - Performance tests for image processing

4. **Security Considerations**
   - Validate all user inputs
   - Implement proper API key management
   - Ensure HIPAA compliance measures
   - Regular security audits

### Monitoring and Maintenance

1. **Performance Monitoring**
   - Response time tracking
   - Error rate monitoring
   - Resource utilization metrics
   - User session analytics

2. **Medical Content Updates**
   - Regular knowledge base updates
   - Medical literature integration
   - Agent performance evaluation
   - Compliance review cycles

---

## Architectural Summary

The Corpus Analyzer architecture represents a sophisticated approach to AI system design with several key characteristics:

1. **Multi-Agent Orchestration**: The HALO Agent Interface coordinates specialized medical agents, each with distinct capabilities and expertise areas.

2. **Layered Architecture**: Clear separation between frontend, application logic, agent implementation, services, and data storage provides maintainability and flexibility.

3. **Hybrid Storage**: Combination of SQLite for structured data and LanceDB for vector embeddings optimizes for different data access patterns.

4. **Streamlit Integration**: Leverages Streamlit's rapid development capabilities while extending it with custom components and styling.

5. **Agno Framework**: Built on the Agno multi-agent framework with careful attention to version compatibility and API evolution.

6. **Medical Compliance**: Architecture decisions reflect the specialized requirements of medical applications, including disclaimers and ethical considerations.

This architecture provides a solid foundation for continued development and extension of the Corpus Analyzer platform while maintaining focus on its core capabilities.

---

**Document Version:** 2.0  
**Last Updated:** September 19, 2025  
**Next Review:** October 19, 2025
