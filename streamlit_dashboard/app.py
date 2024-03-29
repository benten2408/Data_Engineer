import os
import streamlit as st
import requests

from dashboard import run

API_BASE_URL = os.environ['API_BASE_URL']

def authenticate_user(username: str, password: str):
    """Authenticate user by making a request to the FastAPI backend."""
    st.write("dans streamlit/app.py authenticate_user juste avant requests.post")
    response = requests.post(f"{API_BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def show_login_page():
    """Display the login form and handle user authentication."""
    st.title("Login to Access Job Market Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        token_response = authenticate_user(username, password)
        if token_response:
            st.session_state['access_token'] = token_response['access_token']
            st.success("Logged in successfully.")
            st.rerun()
        else:
            st.session_state['access_token'] = None
            st.error("Failed to login. Check your username and password.")


if 'access_token' not in st.session_state or st.session_state['access_token'] is None:
    show_login_page()
else:
    run()