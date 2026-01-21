import sys
import pandas as pd
from core.api import data_fetcher
from core.visualizer import display_data
from utils.database_info import db_markdown
import streamlit as st
from utils.modal import _modal_creator
from core.logger.logger import view_logs

# define the function for the data page
def data_page():
    st.markdown("""
        <style> 
            .container {
                padding: 20px;
                width: 50%;    
            }     
        </style>""", unsafe_allow_html=True)


    # Query info text to show in modal
    query_info_text = """
        <div class="container">
            <h3>How to Query Astronomical Data</h3>
            <p>QAstro allows you to query multiple astronomical databases simultaneously.</p>
            <p>You can search for data using the following parameters:</p>
            <ul>
                <li> <b>Object Name</b>: Enter the name of the astronomical object (e.g., 'M 31', 'hd1').</li>
                <li> <b>RA (Right Ascension)</b>: Enter the RA in decimal degrees.</li>
                <li> <b>Dec (Declination)</b>: Enter the Dec in decimal degrees.</li>
                <li> <b>Bibcode</b>: Enter the bibcode of the object.</li>
                <li> <b>Database</b>: Select the database(s) you want to query.</li>
                <li> <b>Extra Options</b>: Depending on the selected database, you may have additional options (e.g., wavelength selection for VizieR).</li>
            </ul>
            <p>
                <b>For example</b>: Searching for the Andromeda Galaxy (M 31):<br>
                1. Enter "M31" in the Object Name field<br>
                2. Select the desired database.<br>
                3. Click the <b>Fetch Data</b> button to retrieve the data.<br>
                The retrieved data will be displayed in a table format, and you can download it as a CSV file.<br>
                If you want to start a new query, click the <b>New Query</b> button.<br>
            </p>
            <p>Happy querying!</p>
        </div>
    """

    col1, col2 = st.columns([0.95, 0.05])
    with col1:
        st.markdown('<h2 style="display:inline;">Querying Astronomical Data</h2>', unsafe_allow_html=True)
    with col2:
        if st.button("ℹ", key="show_query_info", help="How to query?"):
            st.session_state.query_info_modal_closed = False
            _modal_creator(input_text=query_info_text, checkbox_flag=False,
                modal_kwargs={'key': 'query_info_modal', 'title': 'How to Query Astronomical Data', 'padding': 10, 'max_width': 1000})

    # Sidebar - User Input
    st.sidebar.header("🔍 Query Parameters")
    object_name = st.sidebar.text_input("Enter Object Name")
    ra = st.sidebar.text_input("RA (deg)")
    dec = st.sidebar.text_input("Dec (deg)")
    bibcode = st.sidebar.text_input("bibcode")
    # "VizieR", "NED", "ADS",  "ALL"
    database = st.sidebar.selectbox("Select Database(s)", ["NONE", "SIMBAD", "IRSA", "SDSS", "GAIA ARCHIVE", "NASA ADS"])
    
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
        extra_options = st.sidebar.selectbox("Select common IRSA Catalogs", ["NONE", "ALL_WISE", "NEOWISE", "2MASS", "GLIMPSE_I", "COSMOS", "SPHEREX", "Euclid", "Spitzer"])
        
    if database == "NASA ADS":
        st.sidebar.subheader("NASA ADS Options")
        author = st.sidebar.text_input("Author (optional)")
        year_range = st.sidebar.text_input("Year Range (e.g., 2020-2023 or 2022)")
        extra_options = {
            'author': author if author else None,
            'year_range': year_range if year_range else None
        }

    # View Logs Toggle in Sidebar
    st.sidebar.markdown("---")
    view_logs_toggle = st.sidebar.toggle("📋 View Logs", key="view_logs_toggle", help="Toggle to show/hide application logs")
    
    # Display logs in sidebar if toggle is enabled
    if view_logs_toggle:
        st.sidebar.markdown("### 📋 Application Logs")
        try:
            logs_content = view_logs()
            st.sidebar.code(logs_content, language="log")
        except Exception as e:
            st.sidebar.error(f"Error loading logs: {e}")
            st.sidebar.code("Unable to load logs", language="log")

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
                if data["status_code"] != 200:
                    raise ValueError("No data returned. Please check your inputs.")
                
            except Exception as e:
                st.error(f"Error during data fetch: {e}")
                sys.exit(1)

            try: 
                df = display_data(data["data"], database)
                df.fillna('Not Available', inplace=True)
                df = df.loc[:, ~df.columns.duplicated()]
            
            except Exception as e:
                st.error(f"Error processing data: {e}")
                # Logs are already shown in sidebar if toggle is enabled
                sys.exit(1)

        st.success("✅ Data fetched successfully!")
        st.header(f"🔭 Retrieved Data: {database}")

        try:
            st.dataframe(df)
            # Logs are already shown in sidebar if toggle is enabled
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