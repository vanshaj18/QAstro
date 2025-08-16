import streamlit as st
from streamlit_navigation_bar import st_navbar
import pages as pg
from utils.navbar import navbar
from utils.footer import footer
from utils.modal import modal

# # Set page title
st.set_page_config(page_title="QAstro", 
                   layout="centered", 
                   initial_sidebar_state="auto")

#navbar
pages = ["Home", "Data"]
styles = {
    "nav": {
        "background-color": "royalblue",
        # "background-image": "url(https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-19tEuUx_--lhSrN78Bfd29nChxdMZ9lZ-Q&s)",
        # "background-repeat": "no-repeat",
        # "background-position": "center",
        "justify-content": "center",
        "font-family": "Times New Roman",
        "font-size": "20px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "hover": {
        "color": "black"
    },
    "active": {
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "14px",
    }
}
options = {
    "show_menu": True,
    "show_sidebar": True,
}

page = st_navbar(
    pages,
    # logo_path=logo_path,
    # urls=urls,
    styles=styles,
    options=options,
)

# st.markdown(navbar, unsafe_allow_html=True)

# page routing
functions = {
    "Home": pg.home_page,
    "Data": pg.data_page,
}

go_to = functions.get(page)
if go_to:
    # initial prompt
    modal()
    # main code 
    go_to()
    # footer code
    st.markdown(footer, unsafe_allow_html=True)
