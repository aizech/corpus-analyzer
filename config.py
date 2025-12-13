from pathlib import Path

class Config:
    COMPANY = "Corpus Analytica"
    COMPANY_URL = "https://www.corpusanalytica.com/"

    SUPPORT_URL = "https://www.corpusanalytica.com/support"

    # --- Constants & Directories ---
    APP_NAME      = "Corpus Analyzer"
    APP_ICON      = ":material/smart_toy:"
    APP_URL       = "https://www.corpusanalytica.com/"
    CONTACT_EMAIL = "support@corpusanalytica.com"

    GITHUB_REPO_URL = "https://github.com/aizech/corpus-analyzer"

    THIS_DIR      = Path(__file__).parent
    #STYLES_DIR    = THIS_DIR / "styles"
    #CSS_FILE      = THIS_DIR / "styles" / "custom.css"
    ASSETS_DIR    = THIS_DIR / "assets"
    
    APP_DESCRIPTION = "Corpus Analyzer is an AI interface for analyzing and exploring images with AI agent workflows."

    MENU_ITEMS = {
        'Get Help': f"{APP_URL}/help",
        'Report a bug': f"{APP_URL}/about",
        'About': "## This is the " + APP_NAME + " App!  Made with " + ":heart: by " + COMPANY
    }

    MASTER_AGENT_ICON = ASSETS_DIR / "godsinwhite_radiologist_light.png"

    LOGO_TEXT_PATH = ASSETS_DIR / "corpus_analyzer_logo_text_light.png"
    LOGO_ICON_PATH = ASSETS_DIR / "godsinwhite_radiologist_light.png"
    LOGO_TEAM_PATH = ASSETS_DIR / "godsinwhite_radiologist_light.png"

    LEAD_AGENT_NAME = "Chief Doctor"
    TEAM_AGENT_NAME = "Specialists"

# Create a single instance to be imported by other modules
config = Config()
