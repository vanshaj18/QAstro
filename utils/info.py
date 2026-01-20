import streamlit as st

def simbad_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }
        </style>
                
        <div class="container">
            <h2>SIMBAD Database</h2>
            <p>SIMBAD (Set of Identifications, Measurements, and Bibliography for Astronomical Data) is a database of astronomical objects. 
                It provides information such as coordinates, spectral types, and references for various celestial objects.</p>
            <p>For more information, visit the <a href="https://simbad.u-strasbg.fr/simbad/" target="_blank">SIMBAD website</a>.</p>
            <p>To query SIMBAD, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)    
    

def ned_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }   
        </style>
                
        <div class="container">
            <h2>NED Database</h2>
            <p>The NASA/IPAC Extragalactic Database (NED) is a database of extragalactic objects and their properties. 
                It provides information such as coordinates, redshifts, and references for various celestial objects.</p>
            <p>It is a valuable resource for astronomers and researchers in the field of astrophysics.</p>
            <p>For more information, visit the <a href="https://ned.ipac.caltech.edu/" target="_blank">NED website</a>.</p>
            <p>To query NED, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)
    

def sdss_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }   
        </style>
                
        <div class="container">
            <h2>SDSS Database</h2>
            <p>The Sloan Digital Sky Survey (SDSS) is a major multi-spectral imaging and spectroscopic survey of the 
                northern sky. It provides data on the positions, colors, and spectra of celestial objects.</p>
            <p>It is a valuable resource for astronomers and researchers in the field of astrophysics.</p>
            <p>For more information, visit the <a href="https://www.sdss.org/" target="_blank">SDSS website</a>.</p>
            <p>To query SDSS, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)
    

def gaia_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }   
        </style>
                
        <div class="container">
            <h2>GAIA Archive</h2>
            <p>The GAIA archive is a database of astrometric and photometric data from the GAIA mission. 
                It provides information on the positions, distances, and motions of celestial objects.</p>
            <p>It is a valuable resource for astronomers and researchers in the field of astrophysics.</p>
            <p>For more information, visit the <a href="https://gea.esac.esa.int/archive/" target="_blank">GAIA Archive website</a>.</p>
            <p>To query GAIA, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)
    
def iras_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }   
        </style>
                
        <div class="container">
            <h2>IRAS Database</h2>
            <p>The Infrared Astronomical Satellite (IRAS) was the first satellite to perform a survey of the entire sky in infrared wavelengths. 
                It provides data on the positions, fluxes, and colors of celestial objects.</p>
            <p>It is a valuable resource for astronomers and researchers in the field of astrophysics.</p>
            <p>For more information, visit the <a href="https://irsa.ipac.caltech.edu/" target="_blank">IRAS website</a>.</p>
            <p>To query IRAS, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)
    
def ads_info_md():
    st.markdown("""
        <style>
            .container {
                padding: 20px;
                width: 80%;
                text-align: left;    
                font-family: "Times New Roman";
                font-size: 18px;
            }   
        </style>
                
        <div class="container">
            <h2>NASA ADS Database</h2>
            <p>The NASA Astrophysics Data System (NASA ADS) is a database of astronomical publications. 
                It provides information such as titles, authors, and publication dates for various astronomical publications.</p>
            <p>It is a valuable resource for astronomers and researchers in the field of astrophysics.</p>
            <p>For more information, visit the <a href="https://ui.adsabs.harvard.edu/" target="_blank">NASA ADS website</a>.</p>
            <p>To query NASA ADS, you can use the following parameters:</p>
        </div>
        """, unsafe_allow_html=True)