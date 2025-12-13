# Corpus Analyzer - Product Requirements Document

## 1. Executive Summary

Corpus Analyzer is a Streamlit application for AI-powered medical image analysis. Phase 1 focuses on a single Medical Imaging agent and serves as the foundation for the future multi-agent orchestration solution called **HALO**.

## 2. Product Vision

### 2.1 Vision Statement

To provide an accessible, specialized AI platform that enhances analysis and research workflows through intelligent agent orchestration. Corpus Analyzer aims to be a trusted assistant for exploration and analysis, providing evidence-based insights and comprehensive knowledge in an intuitive interface.

### 2.2 Target Users

- **Primary**: Medical professionals (doctors, specialists, nurses)
- **Secondary**: Healthcare administrators, medical researchers
- **Tertiary**: Medical students, healthcare educators

### 2.3 Key Value Propositions

- **Medical AI Orchestration**: Coordinate specialized AI agents for comprehensive healthcare assistance
- **Knowledge Integration**: Access and utilize medical knowledge through vector databases
- **Visual Analytics**: Planned for future phases
- **Secure Collaboration**: HIPAA-compliant session management for healthcare teams
- **Intuitive Interface**: User-friendly design optimized for healthcare workflows

## 3. Product Features

### 3.1 Core Features

#### 3.1.1 Multi-Agent Orchestration
- The solution is called **HALO** (HALO Agent Interface)
- Phase 1 runs with a single Medical Imaging agent
- Future phases extend HALO to orchestrate multiple specialized agents

#### 3.1.2 Medical Knowledge Base
- Vector database integration for medical knowledge retrieval
- Knowledge search and retrieval capabilities
- Memory system for user preferences and conversation history

#### 3.1.3 Medical Image Analysis
- Support for analyzing various medical imaging modalities (X-ray, MRI, CT, Ultrasound)
- Detailed professional analysis with anatomical review following a structured approach:
  - Image technical assessment (modality, quality, positioning)
  - Professional anatomical analysis with measurements
  - Clinical interpretation with diagnosis and confidence level
  - Patient-friendly explanations with jargon-free descriptions
  - Evidence-based context with PubMed literature references
- Medical disclaimer for educational use only
- Support for DICOM and standard image formats

#### 3.1.4 Image Analysis
- Support for uploading and analyzing medical images
- Image storage and management

#### 3.1.5 Configuration Management
- Model selection (GPT-4o, GPT-4o-mini, GPT-5)
- API key management for OpenAI integration

### 3.2 User Interface Components

#### 3.2.1 Main Chat Interface
- Image-focused interaction for the Medical Image Analysis workflow
- Streaming responses with tool call visibility
- Example prompts for common medical queries
- Memory system that retains important user information
- Knowledge base search integration for medical information retrieval

#### 3.2.2 Navigation
- Medical Image Analysis (specialized image analysis interface)
- Configuration (system settings and agent configuration)
- About (platform information)

#### 3.2.3 Sidebar
- Model selection
- Session management

## 4. Technical Requirements

### 4.1 Platform Architecture

#### 4.1.1 Framework
- Streamlit for web application frontend
- Agno framework for AI agent orchestration
- LanceDB for vector database storage
- SQLite for session and memory management

#### 4.1.2 AI Models
- OpenAI GPT models (GPT-4o, GPT-4o-mini, GPT-5)
- OpenAI Embedding models for knowledge vectorization (text-embedding-3-small)
- OpenAI Vision models for medical image analysis

#### 4.1.3 Storage
- SQLite for session storage (`halo_sessions.db`)
- SQLite for memory storage (`halo_memory.db`)
- File system for file and image storage (uploads)
- LanceDB for vector embeddings and knowledge retrieval
- Directory-based knowledge document storage (`knowledge_docs/`)

### 4.2 Integration Requirements

#### 4.2.1 External APIs
- OpenAI API for language models and embeddings
- PubMed API for medical research and literature
- Web search capabilities for medical information retrieval

#### 4.2.2 Authentication
- Local API key management
- Session-based user identification

### 4.3 Performance Requirements

- Response time under 5 seconds for standard queries
- Support for concurrent user sessions
- Efficient memory usage for long conversations
- Responsive UI across desktop devices

## 5. User Experience

### 5.1 User Flows

#### 5.1.1 New User Onboarding
1. User accesses the application
2. Enters user ID
3. Views introductory information
4. Begins interaction with default configuration

#### 5.1.2 Medical Query Flow
1. User navigates to the Medical Image Analysis page
2. User uploads a medical image
3. System analyzes the image using the Medical Imaging agent
4. User receives the structured report

#### 5.1.3 Image Analysis Flow
1. User navigates to the Medical Image Analysis page
2. User uploads medical image through the interface
3. System delegates to the Medical Imaging Expert agent
4. User receives structured analysis including:
   - Technical assessment of the image
   - Professional anatomical analysis
   - Clinical interpretation with diagnosis
   - Patient-friendly explanation
   - Evidence-based context from PubMed
5. Image can be stored locally for future reference

#### 5.1.4 Data Visualization Flow
This flow is planned for future HALO phases.

### 5.2 UI/UX Design Principles

- **Medical Focus**: Interface designed specifically for healthcare workflows
- **Clarity**: Clean, uncluttered design with clear information hierarchy
- **Accessibility**: High contrast, readable fonts, and intuitive navigation
- **Consistency**: Uniform design language across all application components
- **Feedback**: Clear system status indicators and progress feedback

## 6. Development Roadmap

### 6.1 Phase 1: Core Platform (Current)
- Single-agent medical imaging analysis (foundation)
- HALO naming and architecture baseline
- Configuration management (model + API key)

### 6.2 Phase 2: Enhanced Medical Capabilities
- Research agent with DuckDuckGo integration
- Medical knowledge base expansion
- Enhanced image analysis capabilities
- Additional specialized medical agents

### 6.3 Phase 3: Advanced Features
- Medical document processing
- Integration with electronic health records
- Advanced analytics dashboard
- Collaborative features for healthcare teams

## 7. Security and Compliance

### 7.1 Data Protection
- No permanent storage of sensitive patient information
- Session-based data handling
- Local API key management
- Secure file handling for uploaded images

### 7.2 Compliance Requirements
- Design aligned with HIPAA compliance principles
- Clear data handling policies
- User authentication and access control

## 8. Limitations and Constraints

### 8.1 Current Limitations
- Limited to available AI models and their capabilities
- Requires API keys for full functionality (OpenAI API key)
- No built-in user authentication system
- Limited to English language support
- Medical image analysis is for educational purposes only
- Not FDA approved for clinical decision-making
- Requires internet connection for API access

### 8.2 Future Considerations
- Multi-language support for international healthcare settings
- Integration with more specialized medical databases
- Mobile application development
- Enhanced security features for enterprise deployment

## 9. Success Metrics

### 9.1 Key Performance Indicators
- User engagement (session duration, query count)
- Query success rate (completed vs. failed interactions)
- Agent utilization (distribution of tasks across agents)
- Visualization generation metrics
- System performance metrics (response time, error rate)

### 9.2 Feedback Mechanisms
- In-app feedback collection
- Usage analytics
- Error logging and monitoring

## 10. Appendix

### 10.1 Glossary
- **HALO**: HALO Agent Interface, the core orchestration system built on Agno Team framework that coordinates multiple specialized agents
- **Agent**: Specialized AI assistant with specific capabilities (Medical Imaging Expert, PubMed Researcher, etc.)
- **Tool**: Functional component that extends agent capabilities (PubMedTools, FileTools, etc.)
- **Session**: Persistent conversation context between user and system stored in SQLite
- **Knowledge Base**: Vector database of medical information using LanceDB
- **Preset**: Saved configuration of agents and tools
- **LanceDB**: Vector database for storing and retrieving knowledge embeddings
- **Agno**: The underlying framework for building multi-agent AI systems with memory, knowledge, and reasoning capabilities
- **PubMed Tools**: Integration with PubMed medical research database for evidence-based information
- **Memory Manager**: System that stores and retrieves important user information and preferences

### 10.2 Project Structure

```
├── app.py                # Main Streamlit application entry point
├── pages/                # Additional Streamlit pages
│   ├── Medical_Image_Analysis.py  # Medical image analysis interface
│   ├── Configuration.py  # System settings
│   └── About.py          # Platform information
├── agents/               # Specialized agent implementations
│   ├── medical_agent.py  # Medical imaging expert
│   ├── pubmed_agent.py   # PubMed research agent
│   ├── data_analyst_agent.py  # Data analysis agent
│   └── visualizer_agent.py  # Visualization agent
├── tools/                # Custom tool implementations
├── assets/               # Static assets (images, icons)
├── halo.py              # HALO Agent Interface implementation
├── knowledge.py         # Knowledge base implementation
└── utils.py             # Utility functions
```

### 10.3 References
- Agno Framework Documentation
- OpenAI API Documentation
- Streamlit Documentation
- Medical AI Best Practices
- PubMed API Documentation

---

*Developed by Corpus Analytica - Your Trusted Partner in Healthcare. Making medical AI accessible, transparent, and empowering.*
