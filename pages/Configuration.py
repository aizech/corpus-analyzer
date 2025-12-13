import streamlit as st
import json
import os
import sys
import dotenv
import datetime
from pathlib import Path

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Configuration",
    page_icon=config.APP_ICON,
    layout="wide",
    #initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)

# Page title
one_cola = st.columns([1])[0]
with one_cola:
    col1a, col2a = st.columns([1, 5])

    with col1a:
        #team_image = config.LOGO_TEAM_PATH
        st.image(config.LOGO_TEAM_PATH, width=100)
        #st.image(team_image, width=400)
    with col2a:
        st.markdown("""
        # Corpus Analyzer 
        ## Configuration
        """, unsafe_allow_html=True)


# Function to save model configuration
def save_model_config(model_config):
    model_config_file = os.path.join(os.path.dirname(__file__), "..", "model_config.json")
    with open(model_config_file, 'w') as f:
        json.dump(model_config, f, indent=2)

# Function to load model configuration
def load_model_config():
    model_config_file = os.path.join(os.path.dirname(__file__), "..", "model_config.json")
    default_config = {
        "default_model": "gpt-4o"
    }
    
    if os.path.exists(model_config_file):
        with open(model_config_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_config
    return default_config

# Main function
def main():
    # Load model configuration
    model_config = load_model_config()

    tab1, tab2 = st.tabs(["Models", "API Keys"])

    with tab1:
        #st.header("AI Model")
        
        # Define available models
        model_options = {
            "gpt-4o": "openai:gpt-4o",
            "gpt-4o-mini": "openai:gpt-4o-mini",
            "gpt-5": "openai:gpt-5"
        }
        
        # Get current default model
        current_default = model_config.get("default_model", "gpt-4o")
        
        # Model selection
        st.subheader("Default AI Model")
        st.write("Select the default model to use across the application. This model will be used for all sessions.")    
        
        selected_model_key = st.selectbox(
            "Select a model",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(current_default) if current_default in model_options else 0,
            key="model_selector_config"
        )
        
        # Save model configuration
        if st.button("Save Model Configuration", type="primary"):
            model_config["default_model"] = selected_model_key
            save_model_config(model_config)
            st.success(f"Default model set to {selected_model_key}")

    with tab2:
        #st.header("API Keys")
        
        # Check if running on Streamlit Cloud or locally
        is_cloud = os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud'
        
        # Initialize session state for API keys if not already done
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {}
        
        #st.subheader("OpenAI API Key")
        
        #st.write("How you get an [OpenAI API Key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).")
                   
        if is_cloud:
            # Running on Streamlit Cloud - user needs to provide their own API key
            st.warning("You're running this app online. Please enter your own API key below. "\
                   "This key will be stored in your session and won't be saved permanently.")
            
            # Get API key from session state or empty string as default
            default_key = st.session_state.api_keys.get('OPENAI_API_KEY', '')
            
            # OpenAI API Key input
            openai_api_key = st.text_input(
                "Enter your OpenAI API Key",
                value=default_key,
                type="password",
                help="Your OpenAI API key for accessing GPT models"
            )
            
            # Save API key to session state when entered
            if openai_api_key:
                st.session_state.api_keys['OPENAI_API_KEY'] = openai_api_key
                # Update environment variable for current session
                os.environ["OPENAI_API_KEY"] = openai_api_key
                if st.button("Apply API Key"):
                    st.success("API Key applied for this session!")
            else:
                st.warning("Please enter your OpenAI API key to use this application.")
                
        else:
            st.info("This app is in BETA. We sponsor this project. So no API Key is needed yet.")
            
            # Running locally - read from .env file
            # st.error("You're running this app locally. API keys will be saved to the .env file.")
            #
            # # Load existing environment variables
            # env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            # if os.path.exists(env_path):
            #     dotenv.load_dotenv(env_path)
            #
            # # OpenAI API Key
            # openai_api_key = st.text_input(
            #     "Enter your OpenAI API Key",
            #     value=os.environ.get("OPENAI_API_KEY", ""),
            #     type="password",
            #     help="Your OpenAI API key for accessing GPT models"
            # )
            #
            # # Save API Keys button
            # if st.button("Save API Keys"):
            #     # Create or update .env file
            #     env_vars = {}
            #     if os.path.exists(env_path):
            #         # Load existing variables
            #         with open(env_path, 'r') as f:
            #             for line in f:
            #                 if '=' in line and not line.startswith('#'):
            #                     key, value = line.strip().split('=', 1)
            #                     env_vars[key] = value
            #
            #     # Update with new values
            #     env_vars["OPENAI_API_KEY"] = openai_api_key
            #
            #     # Write back to .env file
            #     with open(env_path, 'w') as f:
            #         for key, value in env_vars.items():
            #             f.write(f"{key}={value}\n")
            #
            #     # Update current environment
            #     os.environ["OPENAI_API_KEY"] = openai_api_key
            #
            #     st.success("API Keys saved successfully to .env file!")

if __name__ == "__main__":
    main()
