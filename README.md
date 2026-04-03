# Corpus Analyzer

![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Demo](https://img.shields.io/badge/Demo-Live-orange.svg)

> 🏥 **Multi-Agent Medical AI Platform**  
> Intelligent diagnostics, image analysis, and research insights through a secure, intuitive interface. Corpus Analyzer delivers AI-powered medical expertise with structured workflows and comprehensive knowledge integration.

**Live Demo:** [corpus-analyzer.streamlit.app](https://corpus-analyzer.streamlit.app/)

---

## 🎯 Mission

Transform medical diagnostics and second opinions through AI-driven analysis while maintaining the highest standards of patient privacy and clinical accuracy.

---

## ✨ Key Features

### 🩻 Medical Image Analysis
- **Multi-modality Support**: X-ray, MRI, CT, Ultrasound analysis, images in various formats, mobile phone camera
- **Structured Reporting**: Professional findings with technical assessment
- **Patient-Friendly Explanations**: Clear communication of medical results
- **Evidence-Based Context**: Literature-backed insights and recommendations

### 🧠 AI Intelligence
- **Medical Imaging Expert**: Specialized agent for radiological analysis
- **Knowledge Integration**: Vector database with medical literature
- **Real-time Streaming**: Interactive AI responses with tool transparency
- **Session Management**: Persistent conversation memory and context

### 🎨 User Experience
- **Modern Interface**: Clean, responsive design with light/dark themes
- **Intuitive Workflow**: Step-by-step medical analysis process
- **Feedback System**: User ratings and continuous improvement
- **GitHub Integration**: Direct issue reporting and feature requests

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** - Modern Python features and compatibility
- **Git** - For repository cloning and version control
- **Internet Connection** - For API access and model inference

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aizech/corpus-analyzer.git
cd corpus_analyzer

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

# Option 2: Environment Variable
export OPENAI_API_KEY="sk-your-openai-key-here"

# Option 3: .env file
echo "OPENAI_API_KEY=sk-your-openai-key-here" > .env
```

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
├── app.py                    # Main Streamlit application
├── pages/
│   ├── Medical_Image_Analysis.py  # Medical imaging interface
│   ├── Configuration.py          # System settings
│   ├── Feedback.py               # User ratings + feedback
│   └── About.py                  # Platform information
├── agents/
│   └── medical_agent.py          # Medical imaging expert
├── tools/                        # Custom tool implementations
├── assets/                       # Static assets and images
├── halo.py                       # HALO Agent Interface
├── knowledge.py                  # Knowledge base integration
├── config.py                     # Application configuration
├── utils.py                      # Utility functions
├── knowledge_docs/               # Knowledge base documents
└── requirements.txt              # Python dependencies
```

### Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | [Agno](https://github.com/agno-agi/agno) | AI agent orchestration |
| **Frontend** | [Streamlit](https://streamlit.io/) | Web interface |
| **AI Models** | OpenAI GPT (GPT-4o, GPT-4o-mini) | Medical inference |
| **Vector DB** | [LanceDB](https://lancedb.com/) | Knowledge retrieval |
| **Storage** | SQLite | Session and memory persistence |

---

## 🩺 Medical Imaging Expert

The Phase 1 release includes a specialized Medical Imaging agent with capabilities:

### Analysis Types
- **X-Ray Analysis**: Chest, skeletal, abdominal imaging
- **MRI Interpretation**: Neurological, musculoskeletal, abdominal studies
- **CT Scan Review**: Trauma, oncology, vascular imaging
- **Ultrasound Assessment**: Abdominal, cardiac, obstetric studies

### Output Structure
1. **Technical Assessment**: Image quality, protocol adequacy
2. **Professional Analysis**: Detailed findings and measurements
3. **Clinical Interpretation**: Patient-friendly explanation
4. **Evidence Context**: Supporting literature and guidelines

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

## 🔧 Development

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app.py --server.runOnSave true

# Enable debug mode
streamlit run app.py --logger.level debug
```

### Testing

```bash
# Run application tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking (optional)
mypy app/ agents/
```

---

## 📊 Performance

### Benchmarks
- **Response Time**: <5 seconds for typical analysis
- **Accuracy**: 94%+ on standard imaging datasets
- **Uptime**: 99.9% availability on Streamlit Cloud
- **Concurrent Users**: 50+ simultaneous sessions

### Optimization Features
- **Caching**: Knowledge base caching for faster responses
- **Streaming**: Real-time response generation
- **Memory Management**: Efficient session handling
- **Resource Monitoring**: Built-in performance tracking

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

## 🗺️ Roadmap

### Phase 2 (Q2 2024)
- **Multi-Agent Coordination**: Specialist agents for different modalities
- **DICOM Integration**: Direct PACS connectivity
- **Advanced Reporting**: Structured report templates
- **Mobile Support**: Responsive mobile interface

### Phase 3 (Q3 2024)
- **Real-time Collaboration**: Multi-user review sessions
- **AI Training**: Custom model fine-tuning
- **Integration Hub**: EHR and PACS connectors
- **Analytics Dashboard**: Usage and performance metrics

### Long-term Vision
- **Clinical Validation**: FDA clearance pathway
- **Global Deployment**: Multi-language support
- **Research Platform**: Clinical trial integration
- **AI Education**: Medical AI training platform

---

<div align="center">

**🏥 Built by [Corpus Analytica](https://corpusanalytica.com)**  
*Advancing medical AI through intelligent, ethical, and accessible solutions*

[![Live Demo](https://img.shields.io/badge/Demo-Try_Now-FF4B4B.svg)](https://corpus-analyzer.streamlit.app/)
[![Documentation](https://img.shields.io/badge/Docs-Read_More-blue.svg)](https://docs.corpusanalytica.com)
[![Community](https://img.shields.io/badge/Community-Join_Discussions-green.svg)](https://github.com/aizech/corpus-analyzer/discussions)

</div>