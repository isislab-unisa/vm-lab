import streamlit as st

from cryptography.fernet import Fernet

cipher_key = st.secrets["cipher_key"]
cipher = Fernet(cipher_key)