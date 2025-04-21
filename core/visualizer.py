import json
import pandas as pd
import streamlit as st

def display_data(data: str, database: str):
    """
    Given the data in a json format, the function will conver the data into a dataframe 
    for visualization.

    Args:
        - data (dict): The fetched data from the API call.
        
    Returns:
        df: Dataframe for easy visualization 
    """
    extractedData=data
    
    #extracting metadata
    if database != "NED":
        extractedData = json.loads(data)

    # extracting the headers depends on the reponse output
    # this can be handled with try and except block
    # also needs to handle the error output if returns empty
    if database == "SIMBAD":
        headers = [x["description"] for x in extractedData['metadata']]
        data = extractedData["data"]

    elif database == "SDSS":
        headers = []
        data = []
        for (k,v) in extractedData[0]["Rows"][0].items():
            headers.append(k)
            data.append(v)
    elif database == "NED":
        # render HTML page
        print(data)
        st.markdown(data, unsafe_allow_html=True)

    elif database == "GAIA ARCHIVE":
        headers = [x["description"] for x in extractedData['metadata']]
        data = extractedData['data']

    #cleaning the data. todo: remove NAN, empty or NONE type data with columns

    try: 
        df = pd.DataFrame(columns=headers)
        # concating the rows
        df = pd.concat([df, pd.DataFrame(data, columns=headers)], ignore_index=True)
    except Exception as e:
        raise ValueError(f" Error in data fomatting: {e}")

    return df