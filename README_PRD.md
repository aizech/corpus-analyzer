# Corpus Analyzer - Product Requirements Document

## 1. Executive Summary

Corpus Analyzer is a Streamlit application for AI-assisted analysis of medical images, smartphone health photos, and photographed health documents. It serves patients, clinicians, and researchers with role-aware, evidence-oriented reports. The current release broadens the product from radiology-centric use to everyday health photos and documents while keeping the existing medical-imaging foundation intact.

## 2. Product Vision

### 2.1 Vision Statement

To help everyone understand what their body shows — from an MRI scan to a photo of a mole or a doctor's letter — through clear, privacy-first, AI-assisted orientation.

### 2.2 Target Users

- **Primary**: Medical professionals (doctors, specialists, nurses, radiologists)
- **Secondary**: Patients and everyday users seeking understandable explanations
- **Tertiary**: Medical researchers, healthcare administrators, educators

### 2.3 Key Value Propositions

- **Specialist skills for each content type:** routed agent selects the right instructions for radiology images, skin photos, nail photos, or photographed documents.
- **Role-aware reports:** separate output for clinicians, patients, and researchers.
- **Privacy before analysis:** explicit consent, local DICOM anonymization, EXIF/GPS stripping, optional face/tattoo masking.
- **Evidence-oriented:** optional online research and PubMed-backed references.
- **Your keys, your control:** bring-your-own-key (BYOK) OpenAI configuration.

## 3. Product Features

### 3.1 Core Features

#### 3.1.1 Multi-Agent Orchestration

- The solution is called **HALO** (HALO Agent Interface)
- Phase 1 runs with routed skills under `skills/core/`
- Future phases extend HALO to orchestrate multiple specialized agents

#### 3.1.2 Medical Knowledge Base

- Vector database integration for medical knowledge retrieval (planned)
- Knowledge search and retrieval capabilities
- Memory system for user preferences and conversation history (planned)

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

#### 3.1.4 Smartphone Photo Analysis

- Upload or capture skin, nail, wound, rash, or tick-bite photos with a phone.
- Structured educational orientation: what can be seen, possible explanations, when to see a doctor.
- No diagnosis or treatment recommendation.
- Explicit "I cannot assess this image" output when quality or content is insufficient.

#### 3.1.5 Document Explainer

- Photograph a doctor's letter, lab report, or medication package.
- Plain-language summary, explanation of medical terms, and suggested questions for the doctor.
- No treatment recommendation.

#### 3.1.6 Multi-Image Sessions

- Upload or capture more than one image in a single session.
- Mixed DICOM and standard images supported.
- Agent is instructed that images belong to the same case/session.

#### 3.1.7 Configuration Management

- Model selection (GPT-4o, GPT-4o-mini, GPT-5, etc.)
- API key management for OpenAI integration
- Optional feature flags (PDF export, web fetcher, progress tracking)

### 3.2 User Interface Components

#### 3.2.1 Main Analysis Interface

- Image-focused interaction for medical images and smartphone photos.
- Document-focused interaction for photographed health documents.
- Streaming responses with tool call visibility.
- Example prompts for common medical queries.
- Multi-image gallery with add/remove per session.

#### 3.2.2 Navigation

- Analyze (image and document analysis interface)
- Configuration (system settings and agent configuration)
- Feedback (ratings and feature requests)
- Security (privacy and data-handling information)
- About (platform information)

#### 3.2.3 Sidebar

- Model selection
- Response language (English / Deutsch)
- Role selection (Clinician / Patient / Researcher)
- Session management

## 4. Technical Requirements

### 4.1 Platform Architecture

#### 4.1.1 Framework

- Streamlit for web application frontend
- Agno framework for AI agent orchestration
- SQLite for session and memory management (planned)
- Directory-based knowledge document storage (`knowledge_docs/`)

#### 4.1.2 AI Models

- OpenAI GPT models (GPT-4o, GPT-4o-mini, GPT-5 family)
- OpenAI Vision models for image and document analysis
- OpenAI Embedding models for knowledge vectorization (text-embedding-3-small)

#### 4.1.3 Storage

- Session-only in-memory image handling by default
- SQLite for session storage (`halo_sessions.db`)
- SQLite for memory storage (`halo_memory.db`)
- Abstract storage interface for future progress tracking
- Optional on-premise / self-hosted deployment

### 4.2 Integration Requirements

#### 4.2.1 External APIs

- OpenAI API for language models and embeddings
- PubMed API for medical research and literature
- Web search capabilities for medical information retrieval

#### 4.2.2 Authentication

- Local API key management
- Session-based user identification

### 4.3 Performance Requirements

- Response time under 10 seconds for standard image queries
- Support for concurrent user sessions
- Efficient memory usage for long conversations
- Responsive UI across desktop and mobile devices

## 5. User Experience

### 5.1 User Flows

#### 5.1.1 New User Onboarding

1. User accesses the application
2. Enters user ID
3. Views introductory information
4. Begins interaction with default configuration

#### 5.1.2 Medical Image Query Flow

1. User navigates to the Analyze page
2. User uploads one or more medical images
3. System analyzes the images using the routed skill
4. User receives the structured report

#### 5.1.3 Smartphone Photo Flow

1. User navigates to the Analyze page
2. User uploads or captures one or more smartphone photos
3. System applies photo privacy (EXIF/GPS removal)
4. System routes to skin/nail/photo skill
5. User receives an orientation report

#### 5.1.4 Document Explainer Flow

1. User navigates to the Analyze page
2. User uploads or captures a health document
3. System routes to document-explainer skill
4. User receives a plain-language summary

### 5.2 UI/UX Design Principles

- **Clarity**: Clean, uncluttered design with clear information hierarchy
- **Accessibility**: High contrast, readable fonts, and intuitive navigation
- **Consistency**: Uniform design language across all application components
- **Feedback**: Clear system status indicators and progress feedback
- **Privacy-first**: Consent and anonymization before analysis

## 6. Development Roadmap

### 6.1 Phase 1: Core Platform (Current)

- Single routed agent with multiple skills
- Medical image analysis, skin/nail photo analysis, document explainer
- Multi-image upload and session gallery
- Photo privacy (EXIF/GPS removal, optional face/tattoo masking)
- Anamnesis fields
- Markdown and PDF export

### 6.2 Phase 2: Progress Tracking (Blocked by Legal Gate)

- Opt-in encrypted storage
- ABCDE progress comparison for skin lesions
- Body map for marking locations
- Conservative triage language (not a traffic-light medical device until legally cleared)
- Doctor handover export

### 6.3 Phase 3: Advanced Features

- Second-opinion escalation to human specialists
- Medical document processing improvements (OCR, structured extraction)
- Integration with electronic health records
- Advanced analytics dashboard
- Collaborative features for healthcare teams

## 7. Security and Compliance

### 7.1 Data Protection

- No permanent storage of sensitive patient information by default
- Session-based data handling
- Local API key management
- Secure file handling for uploaded images
- EXIF/GPS stripping for smartphone photos
- Optional face/tattoo masking (experimental, disabled by default)

### 7.2 Compliance Requirements

- Designed for de-identified, educational use
- GDPR Art. 9 special-category health data considerations
- HIPAA considerations for US contexts
- Clear data handling policies
- User authentication and access control (planned)

### 7.3 Purpose Statement

Corpus Analyzer is an educational and orientation tool that explains images and photographed documents in plain language for patients, clinicians, and researchers. It does not diagnose, triage, or recommend treatment.

## 8. Limitations and Constraints

### 8.1 Current Limitations

- Limited to available AI models and their capabilities
- Requires API keys for full functionality (OpenAI API key)
- No built-in user authentication system
- Smartphone photo quality check is guidance-only (no computer-vision QC yet)
- Progress tracking and persistent storage are not yet enabled
- Medical image analysis is for educational purposes only
- Not CE-marked or FDA-cleared for clinical decision-making
- Requires internet connection for API access

### 8.2 Future Considerations

- Additional model providers beyond OpenAI
- On-device or EU-hosted models
- Enhanced security features for enterprise deployment
- Native mobile application

## 9. Success Metrics

### 9.1 Key Performance Indicators

- User engagement (session duration, query count)
- Query success rate (completed vs. failed interactions)
- Agent utilization (distribution of tasks across skills)
- Report export usage
- System performance metrics (response time, error rate)

### 9.2 Feedback Mechanisms

- In-app feedback collection
- Usage analytics
- Error logging and monitoring

## 10. Appendix

### 10.1 Glossary

- **HALO**: HALO Agent Interface, the core orchestration system built on the Agno framework that coordinates multiple specialized agents
- **Agent**: Specialized AI assistant with specific capabilities (Medical Imaging Expert, Skin Photo Analyst, Document Explainer, etc.)
- **Tool**: Functional component that extends agent capabilities (PubMedTools, FileTools, web_fetch, etc.)
- **Session**: Persistent conversation context between user and system stored in SQLite
- **Skill**: Markdown file with task-specific instructions discovered by the skill router
- **Knowledge Base**: Vector database of medical information
- **Agno**: The underlying framework for building multi-agent AI systems with memory, knowledge, and reasoning capabilities
- **PubMed Tools**: Integration with PubMed medical research database for evidence-based information
- **Memory Manager**: System that stores and retrieves important user information and preferences

### 10.2 Project Structure

```
├── app.py                # Main Streamlit application entry point
├── views/                # Streamlit pages
│   ├── Medical_Image_Analysis.py  # Image and document analysis interface
│   ├── Configuration.py           # System settings
│   ├── Feedback.py                # User feedback
│   ├── Security.py                # Privacy and security information
│   └── About.py                   # Platform information
├── agents/               # Specialized agent implementations
│   └── medical_agent.py         # Routed medical imaging agent
├── agent_config/         # Agent and skill routing configuration
│   ├── agent_config.py
│   ├── skill_router.py
│   └── tool_registry.py
├── skills/               # Skill instructions and tools
│   └── core/
│       ├── medical-image-analysis/
│       ├── skin-photo-analysis/
│       ├── nail-photo-analysis/
│       ├── document-explainer/
│       └── web-fetcher/
├── storage/              # Abstract storage interface (Phase 2 prep)
├── assets/               # Static assets (images, icons)
├── config.py             # Application constants
├── dicom_utils.py        # DICOM anonymization
├── image_loader.py       # Multi-image loading helpers
├── photo_privacy.py      # EXIF/GPS removal
├── export.py             # Report generation
├── analysis_format.py    # Structured report parser
├── models.py             # Model configuration
├── ui.py                 # Shared UI components
├── utils.py              # Utility functions
├── tests/                # pytest test suite
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Project metadata
```

### 10.3 References

- Agno Framework Documentation
- OpenAI API Documentation
- Streamlit Documentation
- Medical AI Best Practices
- PubMed API Documentation
- GDPR Art. 9 Guidance
- HIPAA Privacy Rule

---

*Developed by Corpus Analytica - Your Trusted Partner in Healthcare. Making medical AI accessible, transparent, and empowering.*
