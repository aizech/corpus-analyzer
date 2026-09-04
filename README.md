# Corpus Analyzer

![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Demo](https://img.shields.io/badge/Demo-Live-orange.svg)

> 🏥 **Medical Image Analysis for Education & Second Opinions**
> Upload an X-ray, MRI, CT, ultrasound, or DICOM image and receive a structured, AI-generated report tailored to clinicians, patients, or researchers.

**Live Demo:** [corpus-analyzer.streamlit.app](https://corpus-analyzer.streamlit.app/)

---

## 🎯 Mission

Make medical imaging analysis more accessible and understandable through AI-powered, educational reports while keeping patient privacy and transparency front and center.

---

## ✨ Key Features

### 🩻 Medical Image Analysis
- **Multi-modality Support**: X-ray, MRI, CT, ultrasound, and DICOM images
- **Structured Reporting**: Technical assessment, findings, clinical interpretation, patient-friendly explanation, and references
- **Role-Aware Reports**: Separate analyses for **Clinician**, **Patient**, and **Researcher** audiences
- **Evidence-Based Context**: Optional online research quick prompt for literature-backed insights

### 🧠 AI Intelligence
- **Routed Medical Imaging Agent**: A local skill-based agent that selects the right prompt and tools for the request
- **Web-Fetcher Tool**: Live page retrieval for up-to-date references (enabled by default, configurable)
- **DICOM Anonymization**: Local clearing of common identifying metadata tags before analysis

### 🎨 User Experience
- **Quick Prompts**: Select one or more additive prompts (radiology style, red flags, patient-friendly, online research, patient context)
- **Language Switch**: English / Deutsch response language
- **Material Icons**: Clean, professional iconography throughout the interface
- **Markdown & PDF Export**: Download reports for documentation or sharing
- **Privacy-First Consent**: Explicit confirmation before sending image data to an AI provider

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** - Modern Python features and compatibility
- **Git** - For repository cloning and version control
- **Internet Connection** - For API access and model inference

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aizech/corpus-analyzer.git
cd corpus-analyzer

# 2. Create virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the application
streamlit run app.py
```

**Application available at:** `http://localhost:8501`

---

## ⚙️ Configuration

### API Keys

Configure your OpenAI API key in the Configuration page or via environment:

```bash
# Option 1: Configuration UI (Recommended)
# Visit http://localhost:8501 and navigate to Configuration page
# Enter your API key in the provided field

# Option 2: Environment file
# Copy the example file and add your real values
cp .env.example .env
```

### Optional PDF Export

PDF export is disabled by default in `requirements.txt`. To enable it, install the optional dependency:

```bash
pip install -e ".[pdf]"
```

Or uncomment the `fpdf2` line in `requirements.txt` and run `pip install -r requirements.txt`.

Set `ENABLE_PDF_EXPORT` in your `.env` to control the feature:

```bash
# Enable PDF export (requires fpdf2)
ENABLE_PDF_EXPORT="true"

# Disable PDF export to avoid loading fpdf2 entirely
ENABLE_PDF_EXPORT="false"
```

When PDF export is disabled, the app still offers Markdown export and no `fpdf2` warning is shown.

### Optional Email Configuration

For feedback email delivery:

```bash
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=support@corpusanalytica.com
SMTP_TO=support@corpusanalytica.com
```

### GitHub Integration

```bash
GITHUB_REPO_URL=https://github.com/aizech/corpus-analyzer
```

---

## 📁 Architecture

### Core Components

```
corpus-analyzer/
├── app.py                    # Main Streamlit application with page navigation
├── views/
│   ├── Medical_Image_Analysis.py  # Medical imaging interface
│   ├── Configuration.py          # Model and API key settings
│   ├── Feedback.py               # User ratings and feedback
│   ├── Security.py               # Security and privacy information
│   └── About.py                  # Platform information
├── agents/
│   └── medical_agent.py        # Routed medical imaging agent factory
├── agent_config/                 # Routed agent configuration
│   ├── agent_config.py         # Agent and RoutedAgent factories
│   ├── skill_router.py         # Skill discovery, ranking, and prompt composition
│   └── tool_registry.py        # Tool discovery from skill directories
├── skills/
│   └── core/
│       ├── medical-image-analysis/SKILL.md  # Medical imaging skill
│       └── web-fetcher/                     # Web fetch tool for literature lookup
├── assets/                       # Static assets and images
├── config.py                     # Application constants
├── dicom_utils.py                # DICOM anonymization helpers
├── export.py                     # PDF / Markdown report generation
├── analysis_format.py            # Structured report parser
├── models.py                     # Model configuration and selection
├── ui.py                         # Shared Streamlit UI components
├── utils.py                      # General utility functions
├── tests/                        # pytest test suite
├── requirements.txt              # Python dependencies
└── pyproject.toml                # Project metadata and ruff config
```

### Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agent Framework** | [Agno](https://github.com/agno-agi/agno) | AI agent orchestration |
| **Agent Routing** | Local skill router + tool registry | Skill discovery, prompt composition, and tool injection |
| **Frontend** | [Streamlit](https://streamlit.io/) | Web interface |
| **AI Models** | OpenAI GPT (GPT-4o, GPT-4o-mini, etc.) | Medical inference |
| **Image Processing** | Pillow, pydicom | DICOM and image handling |
| **Web Research** | Local web-fetcher tool + httpx/trafilatura | Live page retrieval for references |
| **Export** | markdown (required), fpdf2 (optional) | Markdown and optional PDF reports |
| **Testing** | pytest, ruff | Code quality and regression tests |

---

## 🩺 Medical Imaging Analysis

The medical imaging agent produces structured educational reports.

### Output Structure
1. **Image Technical Assessment**: Modality, anatomical region, image quality
2. **Professional Analysis**: Systematic anatomical review and findings
3. **Clinical Interpretation**: Diagnosis, differential, confidence, follow-up
4. **Patient Education**: Jargon-free explanation of what the findings mean
5. **Evidence-Based Context**: References and guidelines (enhanced by the online research prompt)
6. **Medical Disclaimer**: Reminder that this is for educational purposes only

### Role-Aware Reports
- **Clinician**: Concise, structured radiology terminology with differentials and follow-up
- **Patient**: Plain-language explanation focused on meaning and next steps
- **Researcher**: Technical depth, confidence discussion, and evidence-based references

After analyzing in one role, switching roles offers a **Re-analyze** button to generate a fresh report for the new audience.

---

## 🎯 Use Cases

### Medical Professionals
- **Second Opinions**: Validate initial radiological interpretations
- **Quality Assurance**: Review and verify imaging reports
- **Education**: Teaching tool for radiology residents
- **Research**: Extract structured data from imaging studies

### Patients
- **Report Understanding**: Clear explanations of medical findings
- **Treatment Planning**: Insights into next steps and options
- **Health Literacy**: Accessible medical information

### Healthcare Institutions
- **Workflow Optimization**: Streamline imaging analysis processes
- **Decision Support**: AI-assisted diagnostic recommendations
- **Documentation**: Structured reporting templates

---

## 🔒 Security & Privacy

### Data Protection
- **No Patient Data Storage**: Sessions are temporary and local
- **HIPAA Considerations**: Designed for de-identified educational use
- **Secure API Communication**: Encrypted data transmission
- **Local Processing**: Optional on-premise deployment available

### Medical Disclaimer

> **⚠️ Important:** This platform is designed for educational and demonstration purposes only. All medical analyses, suggestions, or information should be reviewed by qualified healthcare professionals before making medical decisions.
>
> The platform is not FDA-approved for clinical decision-making and should not replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

---

---

## 📊 Performance

### Behavior
- **Response Time**: Depends on the selected OpenAI model and image size; typically a few seconds
- **Caching**: Report export functions are cached per image/analysis pair
- **Session Handling**: Uploaded images are kept in memory only for the current session
- **No Persistent Storage**: The app does not persist uploaded images or reports by default

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Connect GitHub repository to Streamlit Cloud
2. Configure environment variables
3. Deploy with automatic CI/CD

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Self-Hosting
```bash
# Production deployment
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

## 🔗 Corpus Analytica Ecosystem

Corpus Analyzer is part of a comprehensive medical AI platform:

### Core Platforms
- **[HALO Core](https://github.com/aizech/halo_core)** - Multi-agent orchestration platform
- **[Clinical Skills](https://github.com/aizech/clinical-skills)** - AI agent skills for radiology
- **[Corpus Core SaaS](https://github.com/aizech/corpus-core-saas)** - Streamlit SaaS template

### WordPress Integration
- **[PainTracker](https://github.com/aizech/corpus-analytica-paintracker)** - 3D pain mapping plugin
- **[Second Opinion](https://github.com/aizech/corpus-analytica-2ndop)** - Complete medical workflow

### Web Presence
- **[Marketing Site](https://www.corpusanalytica.com)** - Corporate website and documentation

---

## 🤝 Contributing

We welcome contributions from the medical and AI communities!

### How to Contribute

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

### Contribution Areas
- **Medical Knowledge**: Expand knowledge base and clinical guidelines
- **AI Models**: Improve analysis accuracy and capabilities
- **User Experience**: Enhance interface and workflows
- **Documentation**: Improve guides and examples
- **Testing**: Add comprehensive test coverage

### Guidelines
- Follow medical ethics and patient privacy standards
- Ensure clinical accuracy and evidence-based recommendations
- Maintain code quality and documentation standards
- Test thoroughly with medical imaging data

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Community

### Get Help
- **Issues**: [GitHub Issues](https://github.com/aizech/corpus-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aizech/corpus-analyzer/discussions)
- **Email**: support@corpusanalytica.com

### Resources
- **Documentation**: [Platform Docs](https://docs.corpusanalytica.com)
- **Live Demo**: [corpus-analyzer.streamlit.app](https://corpus-analyzer.streamlit.app/)
- **Company**: [Corpus Analytica](https://www.corpusanalytica.com)

### Community
- **Contributors**: [GitHub Contributors](https://github.com/aizech/corpus-analyzer/graphs/contributors)
- **Medical Advisory Board**: Clinical experts and radiologists
- **Developer Community**: AI engineers and healthcare technologists

---

<div align="center">

**🏥 Built by [Corpus Analytica](https://corpusanalytica.com)**
*Advancing medical AI through intelligent, ethical, and accessible solutions*

[![Live Demo](https://img.shields.io/badge/Demo-Try_Now-FF4B4B.svg)](https://corpus-analyzer.streamlit.app/)
[![Documentation](https://img.shields.io/badge/Docs-Read_More-blue.svg)](https://docs.corpusanalytica.com)
[![Community](https://img.shields.io/badge/Community-Join_Discussions-green.svg)](https://github.com/aizech/corpus-analyzer/discussions)

</div>
