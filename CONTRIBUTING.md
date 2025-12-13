# Contributing to Corpus Analytica Projects

Thank you for your interest in contributing to the Corpus Analytica projects! We have two main projects that work together to provide comprehensive medical AI solutions:

- **Corpus Analyzer** - Open-source AI platform built on the Agno framework
- **[Corpus Analytica Core SaaS](https://github.com/aizech/corpus-core-saas)** - Commercial medical AI platform with premium features

## 🏥 Medical AI Development Guidelines

**Important Medical Disclaimer:** These platforms are designed for educational and demonstration purposes. All medical analyses and information should be reviewed by qualified healthcare professionals before making medical decisions. Contributors must understand that medical AI applications carry significant ethical and legal responsibilities.

### Responsible AI Development

1. **Patient Safety First**: Always prioritize patient safety and well-being in your contributions
2. **Evidence-Based Approach**: Ensure all medical information and recommendations are supported by current medical literature
3. **Clear Limitations**: Clearly communicate the limitations and appropriate use cases of AI assistance
4. **Bias Awareness**: Be mindful of potential biases in training data and algorithms
5. **Privacy Protection**: Handle medical data with the utmost care and respect for patient privacy

## 🚀 Quick Start for Contributors

### Prerequisites

- **Python 3.8+** - Both projects require Python 3.8 or higher
- **Git** - For version control and collaboration
- **OpenAI API Key** - Required for AI functionality (get from [OpenAI Platform](https://platform.openai.com/))
- **Medical Knowledge** - Basic understanding of medical concepts and terminology (recommended)

### Development Environment Setup

1. **Fork the Repository**
   ```bash
   # For Corpus Analyzer (open-source)
   git clone <your-repo-url>.git
   cd corpus_analyzer

   # For Corpus Core SaaS (commercial)
   git clone https://github.com/aizech/corpus-core-saas.git
   cd corpus-core-saas
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # For Corpus Analyzer (open-source)
   # Create a .env file in the project root if you need to provide API keys

   # For Corpus Core SaaS (commercial)
   cp .streamlit/secrets-example.toml .streamlit/secrets.toml
   cp .streamlit/config-example.toml .streamlit/config.toml
   # Configure authentication and payment settings
   ```

## 📝 Contribution Process

### 1. Choose Your Project

**Corpus Analyzer**
- Focus: Core agent development, knowledge integration, and analysis features
- Technologies: Agno framework, LanceDB, SQLite, Streamlit

**Corpus Core SaaS**
- Focus: Production-ready features, user experience, HIPAA compliance
- Technologies: Streamlit, OAuth, Stripe payments, premium features
- Best for: Full-stack developers, UX specialists, healthcare IT professionals

### 2. Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Use descriptive branch names: feature/medical-image-analysis
   ```

2. **Make Your Changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   python -m pytest tests/

   # Test the application
   streamlit run app.py
   ```

4. **Commit with Conventional Commits**
   ```bash
   git add .
   git commit -m "feat: add new medical image analysis feature

   - Added support for CT scan analysis
   - Integrated with PubMed for evidence-based reporting
   - Added patient-friendly explanations"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub

## 💻 Coding Standards

### Python Code Style

- **Formatting**: Use `black` for code formatting
  ```bash
  pip install black
  black your_file.py
  ```

- **Linting**: Use `flake8` for code quality
  ```bash
  pip install flake8
  flake8 your_file.py
  ```

- **Type Hints**: Use type hints for better code documentation
  ```python
  from typing import List, Dict, Optional

  def analyze_medical_image(image_path: str) -> Dict[str, str]:
      # Function implementation
      pass
  ```

### Medical AI Specific Guidelines

1. **Agent Development** (Agno Framework)
   ```python
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat

   # Create specialized medical agents
   agent = Agent(
       name="Medical_Imaging_Expert",
       role="Analyze medical images and provide clinical insights",
       model=OpenAIChat(id="gpt-4o"),
       instructions=[
           "Always provide evidence-based analysis",
           "Include confidence levels for assessments",
           "Suggest when human expert consultation is needed"
       ]
   )
   ```

2. **Medical Data Handling**
   ```python
   # Always anonymize patient data
   def anonymize_medical_data(data: Dict) -> Dict:
       # Remove or hash PHI (Protected Health Information)
       pass

   # Implement proper error handling for medical scenarios
   def safe_medical_analysis(image_path: str) -> Optional[Dict]:
       try:
           return analyze_medical_image(image_path)
       except Exception as e:
           # Log error but don't expose sensitive information
           return None
   ```

3. **Documentation Requirements**
   ```python
   def analyze_chest_xray(image_path: str) -> Dict[str, Any]:
       """
       Analyze chest X-ray for potential abnormalities.

       Args:
           image_path: Path to chest X-ray image file

       Returns:
           Dictionary containing:
           - technical_assessment: Technical quality analysis
           - clinical_findings: Identified abnormalities
           - confidence_score: AI confidence (0-100)
           - recommendations: Suggested next steps
           - disclaimer: Standard medical disclaimer

       Note:
           This AI analysis is for educational purposes only.
           Always consult with qualified healthcare providers.
       """
   ```

## 🧪 Testing Requirements

### Testing Medical AI Features

1. **Unit Tests** for individual functions
2. **Integration Tests** for agent interactions
3. **Medical Accuracy Tests** (where possible)
4. **Privacy and Security Tests** for data handling

```python
# Example test structure
import pytest
from medical_agent import MedicalImagingAgent

def test_medical_image_analysis():
    """Test medical image analysis functionality."""
    agent = MedicalImagingAgent()
    result = agent.analyze("test_xray.jpg")

    assert "technical_assessment" in result
    assert "clinical_findings" in result
    assert "disclaimer" in result
    assert result["confidence_score"] >= 0
    assert result["confidence_score"] <= 100

def test_medical_disclaimer_inclusion():
    """Ensure all medical responses include disclaimers."""
    agent = MedicalImagingAgent()
    result = agent.analyze("test_image.jpg")

    assert "educational purposes only" in result["disclaimer"].lower()
    assert "consult healthcare provider" in result["disclaimer"].lower()
```

## 📋 Project-Specific Guidelines

### Corpus Analyzer Contributions

**Priority Areas:**
- New medical agent capabilities
- Knowledge base improvements
- Medical literature integration
- Algorithm accuracy enhancements

**Technical Focus:**
- Agno framework optimizations
- LanceDB query performance
- Medical image processing
- Multi-agent coordination

### Corpus Analytica Platform Contributions

**Priority Areas:**
- User experience improvements
- HIPAA compliance features
- Payment integration enhancements
- Authentication security
- Mobile responsiveness

**Technical Focus:**
- Streamlit performance optimization
- OAuth integration improvements
- Subscription management
- Medical data privacy controls

## 🔒 Security and Compliance

### HIPAA Compliance (Medical AI Platform)

1. **Data Protection**: Ensure all medical data is encrypted in transit and at rest
2. **Access Controls**: Implement proper authentication and authorization
3. **Audit Logging**: Track all access to medical data
4. **Data Anonymization**: Remove or hash PHI when not required for functionality

### General Security Practices

1. **API Key Management**: Never commit API keys to version control
2. **Dependency Security**: Regularly update and audit dependencies
3. **Input Validation**: Validate all user inputs, especially medical data
4. **Error Handling**: Don't expose sensitive information in error messages

## 🌍 Internationalization

Both projects support multiple languages. When adding new features:

1. **Add translations** in `locales/` directory
2. **Use translation keys** instead of hardcoded text
3. **Consider medical terminology** variations across languages
4. **Test with medical professionals** from different regions

## 📚 Documentation

### Documentation Requirements

1. **Code Documentation**: Use docstrings for all functions and classes
2. **Medical Context**: Explain medical concepts and terminology
3. **Usage Examples**: Provide clear examples of how to use new features
4. **Architecture Documentation**: Update ADRs for significant changes

### Documentation Structure

```
docs/
├── api/                    # API documentation
├── medical-guidelines/     # Medical AI development guidelines
├── architecture/          # System architecture docs
└── user-guide/            # User-facing documentation
```

## 🚢 Deployment and DevOps

### Local Development

```bash
# Run in development mode
streamlit run app.py --server.headless true

# Run tests
pytest tests/ -v

# Check code quality
flake8 . --max-line-length=88
black --check .
```

### Production Deployment

1. **Environment Setup**: Configure production environment variables
2. **Security**: Set up SSL certificates and security headers
3. **Monitoring**: Implement logging and health checks
4. **Backup**: Set up regular backups of medical data

## 🤝 Community Guidelines

### Code of Conduct

We expect all contributors to:
- Be respectful and inclusive
- Focus on constructive feedback
- Maintain patient privacy and confidentiality
- Follow ethical AI development practices
- Respect medical professionalism standards

### Getting Help

1. **Check Documentation**: Review existing docs and README files
2. **Search Issues**: Look for similar issues or discussions
3. **Ask Questions**: Open an issue for questions or clarification
4. **Join Discussions**: Participate in community discussions

## 🎯 Contribution Ideas

### For Corpus Analytica (Open-Source)

- [ ] New medical imaging modalities (Ultrasound, Pathology slides)
- [ ] Enhanced PubMed research integration
- [ ] Medical calculator implementations
- [ ] Multi-language medical knowledge bases
- [ ] Advanced visualization tools for medical data

### For Corpus Analytica (Commercial)

- [ ] Improved mobile responsiveness
- [ ] Advanced subscription management features
- [ ] Enhanced medical image annotation tools
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard

## 📄 License and Legal

### Corpus Analytica (Open-Source)
- **License**: MIT License
- **Medical Disclaimer**: Educational and research purposes only
- **Liability**: No warranty for medical applications

### Corpus Analytica (Commercial)
- **License**: Proprietary software
- **HIPAA Compliance**: Designed for healthcare environments
- **Professional Use**: Intended for healthcare professionals

## 🙏 Acknowledgments

Thank you for contributing to medical AI advancement! Your work helps make healthcare more accessible and informed. Remember: with great AI power comes great responsibility for patient care and ethical development.

---

*Made with ❤️ by Corpus Analytica - Advancing healthcare through responsible AI*
