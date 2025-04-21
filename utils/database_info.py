import streamlit as st
from utils.info import gaia_info_md, iras_info_md, ned_info_md, sdss_info_md, simbad_info_md

def db_markdown(database):
    """
    Create a markdown based on the database selected.
    """
    if database == "SIMBAD":
        simbad_info_md()

    if database == "NED":
        ned_info_md()

    if database == "SDSS":
        sdss_info_md()

    if database == "GAIA ARCHIVE":
        gaia_info_md()

    if database == "IRAS":
        iras_info_md()