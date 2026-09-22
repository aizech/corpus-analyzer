# Corpus Analyzer

![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Demo](https://img.shields.io/badge/Demo-Live-orange.svg)

> 🏥 **Understand what your body shows — from an MRI scan to a photo of a mole.**
> Upload a medical image, a smartphone photo, or a photographed document and receive a structured, AI-generated report tailored to clinicians, patients, or researchers. Orientation and education — not a diagnosis.

**Live Demo:** [corpus-analyzer.streamlit.app](https://corpus-analyzer.streamlit.app/)

---

## 🎯 Mission

Help people understand what their medical images, body photos, and health documents show — clearly, transparently, and privately — and recognize when professional medical care is the next step.

---

## ✨ Key Features

| Feature | Status |
|---|---|
| Medical image analysis (X-ray, MRI, CT, ultrasound, DICOM) | ✅ |
| Upload of standard image formats, including smartphone photos | ✅ |
| Multiple images per session (different angles or mixed DICOM + photos) | ✅ |
| Analysis quality for non-radiology photos (skin, nails, …) | ✅ |
| Role-aware reports (Clinician / Patient / Researcher) | ✅ |
| Quick prompts (radiology style, red flags, patient-friendly, online research, patient context) | ✅ |
| Privacy-first consent before sending image data to an AI provider | ✅ |
| Local DICOM anonymization | ✅ |
| English / Deutsch response language | ✅ |
| Markdown and PDF export | ✅ |
| Guided photo capture with photo-quality tips | ✅ |
| Photo privacy: EXIF/GPS removal, face and tattoo masking | ✅ (masking requires optional opencv-python) |
| Follow-up questions (onset, change, itching, bleeding, pain) | ✅ |
| Dedicated skills for skin, nail, wound, rash, tick bite, eye/throat, document, and medication photos | ✅ |
| Photo-quality hints (blur, brightness, contrast) | ✅ |
| Progress tracking over time (opt-in) | � behind `ENABLE_PROGRESS_TRACKING` flag |
| Body map for marking locations | � behind `ENABLE_PROGRESS_TRACKING` flag |
| Doctor handover export (images, history, timeline) | � behind `ENABLE_PROGRESS_TRACKING` flag |
| Encrypted SQLite snapshot storage | 🚧 behind `ENABLE_PROGRESS_TRACKING` flag |

---

## 🎯 Why, How, What

### Why
We believe everyone has the right to understand what their body shows — and to know when it is time to let a doctor take a look. Too often, people are left alone with an image, a report, or a worry until the next appointment.

### How
- **Explained for the reader:** separate reports for **Patient**, **Clinician**, and **Researcher**.
- **Specialist skills instead of one generic model:** a routed agent picks the right skill and tools for each image or document type.
- **Privacy before analysis:** explicit consent before any image leaves the device; local removal of identifying DICOM metadata and photo EXIF/GPS data.
- **Transparent and evidence-oriented:** references, optional literature lookup, and a clear medical disclaimer.
- **Your keys, your control:** bring-your-own-key (BYOK) configuration.

### What
A web application for AI-assisted image and document analysis: upload → structured, understandable report.

- **Today:** X-ray, MRI, CT, ultrasound, DICOM, standard image formats — including photos taken with a smartphone, and photographed health documents.
- **Next:** guided phone capture for everyday health photos (skin, nails, wounds), multi-image sessions, progress tracking over time, and doctor-ready exports.

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
│   ├── Medical_Image_Analysis.py  # Image and document analysis interface
│   ├── Configuration.py          # Model and API key settings
│   ├── Feedback.py                 # User ratings and feedback
│   ├── Security.py                 # Security and privacy information
│   └── About.py                    # Platform information
├── agents/
│   └── medical_agent.py            # Routed medical imaging agent factory
├── agent_config/                   # Routed agent configuration
│   ├── agent_config.py             # Agent and RoutedAgent factories
│   ├── skill_router.py             # Skill discovery, ranking, and prompt composition
│   └── tool_registry.py            # Tool discovery from skill directories
├── skills/
│   └── core/
│       ├── medical-image-analysis/  # Medical imaging skill
│       ├── skin-photo-analysis/     # Skin and mole photo skill
│       ├── nail-photo-analysis/     # Nail photo skill
│       ├── document-explainer/      # Doctor's letter / document skill
│       └── web-fetcher/             # Web fetch tool for literature lookup
├── storage/                         # Abstract storage interface (Phase 2 prep)
├── assets/                          # Static assets and images
├── config.py                        # Application constants
├── dicom_utils.py                   # DICOM anonymization helpers
├── image_loader.py                  # Multi-image loading helpers
├── photo_privacy.py               # EXIF/GPS removal and optional face masking
├── export.py                        # PDF / Markdown report generation
├── analysis_format.py               # Structured report parser
├── models.py                          # Model configuration and selection
├── ui.py                              # Shared Streamlit UI components
├── utils.py                           # General utility functions
├── tests/                             # pytest test suite
├── requirements.txt                   # Python dependencies
└── pyproject.toml                     # Project metadata and ruff config
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

## 🩺 Medical Imaging & Photo Analysis

The routed agent produces structured educational reports.

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

### Multi-Image Sessions
You can upload or capture several images in one session — for example, different angles of a skin spot, or a DICOM scan alongside a smartphone photo. The agent is instructed that the images belong together, but it still cannot provide a diagnosis.

### Document Explainer
Photograph a doctor's letter, lab report, or medication package. The document explainer skill summarizes the content in plain language, explains medical terms, and suggests questions to ask your doctor.

---

## 🎯 Use Cases

### Patients and everyday users
- **Report understanding:** plain-language explanations of medical findings.
- **Everyday health photos:** moles and skin changes, nails, rashes, wounds, tick bites — photographed with a phone, explained in plain language, with guidance on when to see a doctor.
- **Document explainer:** understand a doctor's letter, lab value, or medication package without medical jargon.
- **Keeping track:** (planned) photograph the same spot over time and see what has changed.
- **Health literacy:** accessible medical information.

### Medical professionals
- **Second opinions:** validate initial interpretations.
- **Quality assurance:** review and verify imaging reports.
- **Education:** teaching tool for radiology residents.
- **Research:** extract structured data from imaging studies.

### Healthcare institutions
- **Workflow optimization**, **decision support**, and **structured documentation**.

---

## ✅ What Corpus Analyzer is — and isn't

**It is**
- An educational explanation of what an image or document shows, in language matched to the reader.
- A structured second look that helps you prepare questions for your doctor.
- (Planned) A way to track changes over time and a conservative pointer to when professional care is advisable.

**It is not**
- A diagnosis, a treatment recommendation, or a replacement for medical care.
- An emergency service. In an emergency, contact your local emergency number.
- A reason to wait: a skin change that grows, changes color, bleeds, or worries you should be looked at by a doctor — regardless of any AI output.

---

## 🔒 Security & Privacy

### Data Protection
- **No storage by default:** sessions are temporary; uploaded images are kept in memory for the current session only.
- **Consent first:** image data is sent to an AI provider only after explicit confirmation.
- **Anonymization:** local clearing of common identifying DICOM metadata and photo EXIF/GPS data before analysis. Face and tattoo masking is available as an experimental, opt-in feature.
- **Progress tracking (planned):** strictly opt-in, stored encrypted, deletable at any time. The no-storage default stays the default.
- **Data protection law:** health data is special-category data under **GDPR Art. 9**; the platform is designed for de-identified, educational use. HIPAA considerations apply for US contexts.
- **Legal gate:** Phase 2 features such as progress tracking require a documented legal and privacy review before they can be enabled. See [`docs/legal-gate.md`](docs/legal-gate.md).
- **Deployment:** optional on-premise / self-hosted deployment.

### Medical Disclaimer

> **⚠️ Important:** Corpus Analyzer is designed for educational and orientation purposes only. It does not provide a diagnosis. All analyses, suggestions, and information — for medical images as well as photos taken with a phone — must be reviewed by a qualified healthcare professional before any medical decision is made.
>
> The platform has not been CE-marked or FDA-cleared and must not replace professional medical advice, diagnosis, or treatment. If you are worried about a symptom or a change in your body, consult a healthcare provider.

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
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t corpus-analyzer .
docker run -p 8501:8501 corpus-analyzer
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
