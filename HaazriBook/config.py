import streamlit as st

def get_secret(section, key, default=None):
    try:
        return st.secrets[section][key]
    except:
        return default

# Database configuration
ADMIN_USERNAME = get_secret("database", "admin_username", "admin")
ADMIN_PASSWORD = get_secret("database", "admin_password", "admin")

# Twilio configuration
TWILIO_ACCOUNT_SID = get_secret("twilio", "account_sid", "")
TWILIO_AUTH_TOKEN = get_secret("twilio", "auth_token", "")
TWILIO_PHONE_NUMBER = get_secret("twilio", "phone_number", "") 