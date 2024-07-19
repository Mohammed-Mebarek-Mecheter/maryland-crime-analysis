import streamlit as st

def sidebar():
    st.sidebar.title("")
    options = [
        "Introduction",
        "Trend Analysis",
        "Crime Distribution",
        "Geographical Analysis",
        "Population Correlation",
        "Crime Hotspots",
        "Crime Rate Changes"
    ]
    return st.sidebar.radio("Go to", options)
