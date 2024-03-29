import os
import streamlit as st
import requests

from dashboard import run

API_BASE_URL = os.environ['API_BASE_URL']
st.set_page_config(layout="wide")

def authenticate_user(username: str, password: str):
    """Authenticate user by making a request to the FastAPI backend."""
    response = requests.post(f"{API_BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def show_login_page():
    """Display the login form and handle user authentication."""
    col1, col2, col3 = st.columns([1,3,1])

    col2.title("Login to Access Job Market Dashboard")
    username = col2.text_input("Username")
    password = col2.text_input("Password", type="password")

    if col2.button("Login"):
        token_response = authenticate_user(username, password)
        if token_response:
            st.session_state['access_token'] = token_response['access_token']
            col2.success("Logged in successfully.")
            st.rerun()
        else:
            st.session_state['access_token'] = None
            col2.error("Failed to login. Check your username and password.")


if 'access_token' not in st.session_state or st.session_state['access_token'] is None:
    show_login_page()
else:
    run()