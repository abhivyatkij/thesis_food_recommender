# app.py

import streamlit as st
from my_module import greet

st.set_page_config(page_title="Streamlit Demo", layout="centered")

st.title("Simple Streamlit Demo")

# text input widget
name = st.text_input("Enter your name:", "World")

# when button clicked, call greet() and show result
if st.button("Say Hello"):
    message = greet(name)
    st.write(message)
