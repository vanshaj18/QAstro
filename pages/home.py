import streamlit as st

def home_page():
    # Inject CSS
    st.markdown("""
        <style>
            .bg-container {
                padding: 10px;
                border-radius: 10px;
                position: relative;
                z-index: 1;
            }
            .bg-overlay {
                padding: 3rem;
                border-radius: 12px;
                text-align: center;
                font-size: 1.5em;
            }
            .title {
                text-align: center;
                font-size: 3em;
                font-weight: bold;
                font-family: "Times New Roman", serif;
                margin-top: 0.5rem;
            }
            .content {
                font-size: 1.2em;
                font-family: "Times New Roman", serif;
                line-height: 1.6;
            }
            .content h3 h4{
                font-family: "Times New Roman", serif;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
            <div class="bg-container">
                <div class="title"> QAstro </div>
                <div style="color:red;"> <p> We are working on fixing SDSS integraiton. Please check back late for SDSSr. </p> </div>
                <div class = "content">  
                    <h3> Overview </h3>
                        <p> QAstro is a web-based application designed to facilitate the gathering and visualization of astronomical data. 
                        With a user-friendly interface, it allows users to query multiple astronomical databases simultaneously. 
                        The application is built using Streamlit and is hosted on Streamlit Cloud, ensuring easy access.</p>
                    <h3> The Idea </h3>
                        <p>The idea behind the application revolves around the need for a unified platform where astronomical data for a given object can be fetched easily.
                            Having faced the issue of gathering data from multiple databases myself, I understand the time spent by researchers in astronomy and astrophysics just to gather data.
                            With a vast number of databases in the astronomy community, it's difficult to keep track of all available data on an object.
                            QAstro provides a simple and elegant platform to fetch data simultaneously from databases like SIMBAD, IRAS, 2MASS, GAIA Archive, SDSS, and more.</p>
                    <h4> Features </h4>
                        <p>
                        <ul type="square"> 
                            <li> <b>User-friendly Interface</b>: Designed for the general public. QAstro handles the data collection.</li>
                            <li> <b>Multiple Database Queries</b>: Query various astronomical databases from one place.</li>
                            <li> <b>Time Efficiency</b>: Reduce time spent on data gathering.</li>
                        <ul>
                        </p>
                    <h4> Supported Databases </h4>
                        <p> 
                            <ol> 
                                <li> SIMBAD  </li>
                                <li> SDSS  </li>
                                <li> GAIA Archive </li>
                                <li> IRAS </li>
                                <li> NASA ADS </li>
                                <li> NED </li>
                                <li> Vizier </li>
                            </ol>
                        </p>
                    <h4> Future Implementations </h4>
                        <p> 
                            <ul type="square"> 
                                <li> Data-Visualization on Aitoff Projection </li>
                                <li> Filter selection </li>
                                <li> Natural Language based queries </li>
                            </ul>
                        </p>
                </div>
            </div>""", 
        unsafe_allow_html=True)