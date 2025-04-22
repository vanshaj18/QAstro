import sys
import streamlit as st
import pandas as pd
from core.api import data_fetcher
from core.visualizer import display_data
from utils.database_info import db_markdown

# define the function for the data page
def data_page():
    st.markdown("""
        <style> 
            .container {
                padding: 20px;
                width: 80%;    
            }     
        </style>""", unsafe_allow_html=True)
    
    #need to give examples for searching data 
    st.markdown("""
        <div class="container">
            <h2> Querying Astronomical Data </h2>
            <p> QAstro allows you to query multiple astronomical databases simultaneously.
            </p>
            <p> You can search for data using the following parameters:</p>
            <ul>
                <li> <b>Object Name</b>: Enter the name of the astronomical object (e.g., 'M 31', 'hd1').</li>
                <li> <b>RA (Right Ascension)</b>: Enter the RA in decimal degrees.</li>
                <li> <b>Dec (Declination)</b>: Enter the Dec in decimal degrees.</li>
                <li> <b>Bibcode</b>: Enter the bibcode of the object.</li>
                <li> <b>Database</b>: Select the database(s) you want to query.</li>
                <li> <b>Extra Options</b>: Depending on the selected database, you may have additional options (e.g., wavelength selection for VizieR).</li>
            </ul>
            <p> <b> For example</b>: Searching for the Andromeda Galaxy (M 31): 
                <br> 1. Enter "M31" in the Object Name field <br> 
                    2. Select the desired database. <br>
                    3. Click the <b> Fetch Data </b> button to retrieve the data. <br>
             The retrieved data will be displayed in a table format, and you can download it as a CSV file. <br>
             If you want to start a new query, click the <b>New Query</b> button. <br>
            <p> Happy querying!</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar - User Input
    # Sidebar form for user input
    st.sidebar.header("🔍 Query Parameters")
    object_name = st.sidebar.text_input("Enter Object Name")
    ra = st.sidebar.text_input("RA (deg)")
    dec = st.sidebar.text_input("Dec (deg)")
    bibcode = st.sidebar.text_input("bibcode")
    # "VizieR", "NED", "ADS",  "ALL"
    database = st.sidebar.selectbox("Select Database(s)", ["NONE", "SIMBAD", "IRSA", "SDSS", "GAIA ARCHIVE"])
    
    extra_options = None
    # if selected viser, add wavelength selection
    if database == "VizieR":
        extra_options = st.sidebar.selectbox("Select Wavelength", ["NONE", "Raido", "IR", "Optical", "UV", "EUV", "X-Ray", "Gamma"])

    #if SDSS is selected, subsquent options will be displayed
    if database == "SDSS":
        extra_options = st.sidebar.selectbox("Select SDSS Options", ["NONE", "Spectro", "IR Spectro"])

    if database == "GAIA ARCHIVE":
        extra_options = st.sidebar.selectbox("Select GAIA Database", ["NONE", "dr1", "dr2", "dr3"])  

    if database == "IRSA":
        extra_options = st.sidebar.selectbox("Select common IRSA Catalogs", ["NONE", "ALL_WISE", "2MASS", "GLIMPSE_I", "COSMOS", "IRAS"])

    submitted = st.sidebar.button("Fetch Data")
    if st.sidebar.button("New Query"):
        st.rerun()

    if submitted:
        # Handle form submission logic here
        st.sidebar.write("Querying with:")
        st.sidebar.write("Object Name:", object_name)
        st.sidebar.write("RA:", ra)
        st.sidebar.write("Dec:", dec)
        st.sidebar.write("Bibcode:", bibcode)
        st.sidebar.write("Database:", database)
        if extra_options:
            st.sidebar.write("catalogue:", extra_options)
            
        st.sidebar.success("Query submitted!")

        with st.spinner("🚀 Fetching data ... please wait ..."):
            try: 
                data = data_fetcher(
                    object_name=object_name,
                    ra=ra,
                    dec=dec,
                    bibcode=bibcode,
                    database=database,
                    extra_options=extra_options
                )
                # if data.status_code == 500:
                #     raise ValueError("Server error. Please try again later.")
                if data.status_code != 200:
                    raise ValueError("No data returned. Please check your inputs.")
                
            except Exception as e:
                st.error(f"Error during data fetch: {e}")
                sys.exit(1)

            try: 
                df = display_data(data.text, database)
                df.fillna('Not Available', inplace=True)
                df = df.loc[:, ~df.columns.duplicated()]
            
            except Exception as e:
                st.error(f"Error processing data: {e}")
                sys.exit(1)

        st.success("✅ Data fetched successfully!")
        st.header(f"🔭 Retrieved Data: {database}")

        try:
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error displaying dataframe: {e}")
            sys.exit(1)

        try:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Data", csv, "astro_data.csv", "text/csv")
        except Exception as e:
            st.error(f"Error generating download: {e}")
            sys.exit(1)

        # Display markdown/info for the database
        db_markdown(database)