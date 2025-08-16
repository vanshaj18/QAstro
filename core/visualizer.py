from io import StringIO
import json
import pandas as pd
import streamlit as st

def display_data(data, database: str):
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
    if database != "NED" and database != "IRSA":
        # if the data is in json format, we need to convert it into a dictionary
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
        st.markdown(data, unsafe_allow_html=True)

    elif database == "GAIA ARCHIVE":
        headers = [x["description"] for x in extractedData['metadata']]
        data = extractedData['data']

    elif database == "IRSA":
        df = pd.read_csv(StringIO(extractedData), sep=",", header=None) 
        headers = df.iloc[0].tolist()
        data = df.iloc[1:].values.tolist()
        # return

    elif database == "NASA ADS":
        # NASA ADS returns JSON with 'response' containing 'docs' array
        if 'response' in extractedData and 'docs' in extractedData['response']:
            docs = extractedData['response']['docs']
            if not docs:
                raise ValueError("No publications found for the given search criteria")
            
            # Extract relevant fields from each document
            processed_data = []
            for doc in docs:
                row = {
                    'Bibcode': doc.get('bibcode', [''])[0] if isinstance(doc.get('bibcode'), list) else doc.get('bibcode', ''),
                    'Title': doc.get('title', [''])[0] if isinstance(doc.get('title'), list) else doc.get('title', ''),
                    'Authors': ', '.join(doc.get('author', [])) if doc.get('author') else '',
                    'Year': doc.get('year', ''),
                    'Publication': doc.get('pub', ''),
                    'DOI': ', '.join(doc.get('doi', [])) if doc.get('doi') else '',
                    'Citation Count': doc.get('citation_count', 0),
                    'Read Count': doc.get('read_count', 0),
                    'Keywords': ', '.join(doc.get('keyword', [])) if doc.get('keyword') else '',
                    'Abstract': doc.get('abstract', '')
                }
                processed_data.append(row)
            
            # Create DataFrame directly from processed data
            df = pd.DataFrame(processed_data)
            return df
        else:
            raise ValueError("Invalid NASA ADS response format") 

    #cleaning the data. todo: remove NAN, empty or NONE type data with columns
    try: 
        df = pd.DataFrame(columns=headers)
        # concating the rows
        df = pd.concat([df, pd.DataFrame(data, columns=headers)], ignore_index=True)
    except Exception as e:
        raise ValueError(f" Error in data fomatting: {e}")

    return df