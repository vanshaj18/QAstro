import streamlit as st

def themes():
    """
    Returns the theme of the application.
    """
    return {
        "primary": "#4CAF50",  # Green
        "secondary": "#FF9800",  # Orange
        # "accent": "#FF4081",  # Pink
        "background": "#F5F5F5",  # Light Gray
        "text_primary": "#212121",  # Dark Gray
        # "text_secondary": "#757575",  # Medium Gray
    }
def apply_theme():

    """
    Applies the theme to the Streamlit app.
    """
    t = themes()
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {t['background']};
                color: {t['text_primary']};
            }}
           
        </style>
        """,
        unsafe_allow_html=True,
    )