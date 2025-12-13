<img src="assets/godsinwhite_radiologist_light.png" alt="Corpus Analyzer" width="100" style="margin-bottom: 20px;"/>

# Corpus Analyzer

Corpus Analyzer is a multi-agent medical AI platform that delivers intelligent diagnostics, image analysis, and research insights through a secure, intuitive interface.

## Overview

This Phase 1 release runs with a single Medical Imaging agent. The broader solution is called **HALO** and will evolve into a multi-agent orchestration layer on top of this foundation.

The platform features a modern, intuitive Streamlit interface with both light and dark themes, real-time streaming responses, and comprehensive medical knowledge integration through vector databases.

# Corpus Analytica - Your Trusted Partner in Healthcare

At [Corpus Analytica](https://www.corpusanalytica.com), we redefine how medical professionals and patients connect—through a platform built for simplicity, security, and global reach.

#### What We Offer:
- Seamless Connections: We unite doctors, specialists, and patients through our cutting-edge digital platform.

- Expert Second Opinions: Gain easy access to a network of certified physicians and specialists for reliable second opinions.

- Effortless Booking: Our intuitive interface makes requesting and scheduling consultations fast and frustration-free.

- Global Access: Wherever you are, our online consultations bring expert medical advice right to your screen.

- Data You Can Trust: We uphold the highest standards in data protection and patient privacy—because your health deserves nothing less.

#### Experience Healthcare in a New Dimension
Your health is invaluable. With Corpus Analytica, discover a smarter, safer, and more connected way to care.

> *"Healthcare should be accessible, transparent, and empowering. At Corpus Analytica, we're building more than just a platform—we're building trust, one consultation at a time."* — Bernhard Z., Founder of [Corpus Analytica](https://www.corpusanalytica.com)


## Live Demo

Take a look at the live demo: [https://corpus-analyzer.streamlit.app/](https://corpus-analyzer.streamlit.app/)


## Features

- 🏥 **Medical AI Focus**: Medical imaging analysis workflow
- 🩻 **Medical Image Analysis**: Structured analysis of uploaded medical images (incl. DICOM)
-  **Session Management**: Local session and memory storage
- 🎨 **Intuitive Medical UI**: Clean, responsive interface with light/dark theme support
- ⭐ **Feedback Page**: Collects user rating and feedback, with optional email delivery via SMTP
- 🧾 **GitHub Issue Templates**: Bug reports and feature requests route through templates and can be added to the Corpus Analyzer project board

## System Requirements

- Python 3.9 or higher
- Git (for cloning the repository)
- Internet connection for API access

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/aizech/corpus-analyzer
cd corpus_analyzer
```

2. **Set Up Virtual Environment**

Using venv (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

**Important:** In the configuration page you can bring your own API keys.

Alternatively, you can create a `.env` file in the project root and configure your API keys:

```env
OPENAI_API_KEY=your_openai_key

# Feedback email (optional)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=support@corpusanalytica.com
SMTP_TO=support@corpusanalytica.com
```

The Feedback page will also use the following optional variable for GitHub issue links:

```env
GITHUB_REPO_URL=https://github.com/aizech/corpus-analyzer
```

5. **Launch the Application**

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

## Project Structure

```
├── app.py              # Main Streamlit application entry point
├── pages/              # Additional Streamlit pages
│   ├── Medical_Image_Analysis.py  # Medical image analysis interface
│   ├── Configuration.py  # System settings
│   ├── Feedback.py       # User ratings + feedback (email + GitHub links)
│   └── About.py          # Platform information
├── agents/              # Specialized agent implementations
│   ├── medical_agent.py  # Medical imaging expert
│   └── ...
├── tools/              # Custom tool implementations
├── assets/             # Static assets (images, icons)
├── halo.py             # HALO Agent Interface implementation
├── knowledge.py        # Knowledge base implementation
├── config.py           # Application configuration
├── utils.py            # Utility functions
├── knowledge_docs/     # Knowledge base documents
└── requirements.txt    # Project dependencies
```

GitHub issue templates live in:

```
.github/ISSUE_TEMPLATE/
```

## Configuration

The application can be configured through:

- `.env` file for API keys and sensitive data
- `config.py` for application settings

## Agent

Phase 1 includes a single Medical Imaging agent:

### Medical Imaging Expert
- Analyzes various medical imaging modalities (X-ray, MRI, CT, Ultrasound)
- Provides structured analysis with technical assessment, professional analysis, and clinical interpretation
- Delivers patient-friendly explanations of medical findings
- Includes evidence-based context from medical literature

## Example Use Cases

1. **Medical Image Analysis**
   - "Analyze this chest X-ray and identify any abnormalities"
   - "Review this MRI scan and describe the findings"
   - "Compare these two CT scans and highlight any changes"

## Support

For support and questions:
- Open an issue in the GitHub repository: https://github.com/aizech/corpus-analyzer/issues
- Bug reports and feature requests are encouraged via the templates linked from the in-app Feedback page

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Medical Disclaimer

**Important:** This project is designed for educational and demonstration purposes only. Any medical analyses, suggestions, or information should be reviewed by qualified healthcare professionals before making medical decisions.

The platform is not FDA-approved for clinical decision-making and should not replace professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Architecture Documentation

For detailed information about the system architecture and design decisions:

- **README_ADR.md**: Contains Architecture Decision Records (ADRs) and system architecture diagrams
- **README_PRD.md**: Contains the Product Requirements Document with detailed feature specifications

## Technical Stack

- **Framework**: [Agno](https://github.com/agno-ai/agno)
- **Frontend**: [Streamlit](https://streamlit.io/) for the web interface
- **AI Models**: OpenAI GPT models (GPT-4o, GPT-4o-mini, GPT-5)
- **Vector Database**: LanceDB for knowledge storage and retrieval
- **Session Storage**: SQLite (`halo_sessions.db` and `halo_memory.db`)

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Based on the Agno framework
- Powered by OpenAI models and APIs

Open [localhost:8501](http://localhost:8501) to view your Corpus Analyzer interface.