import streamlit as st

def show():
    st.title("Maryland Crime Data Analysis (1975-2020)")
    st.write("""
    This app provides an analysis of historical crime data in Maryland to identify trends, patterns, and potential areas for intervention.
    The goal is to inform strategic planning for reducing crime rates by 10% in the next five years.
    """)

import streamlit as st

def show():
    st.title("Maryland Crime Data Analysis (1975-2020)")
    st.write("""
    This interactive app empowers Maryland's Department of Public Safety to analyze historical crime data from 1975 to 2020. 

    The analysis aims to identify trends, patterns, and potential crime hotspots to inform strategic planning initiatives. The ultimate goal is to achieve a 10% reduction in overall crime rates within the next five years.

    By exploring the various sections of this app, you can gain insights into:

    * **Trend Analysis:** Overall crime rate trends across Maryland over the past decades.
    * **Crime Distribution:** The most prevalent crime types and how their distribution has changed over time.
    * **Geographical Analysis:** Jurisdictions with the highest and lowest crime rates compared to the state average.
    * **Population Correlation:** The relationship between population size and crime rates in different areas.
    * **Crime Rate Changes:** The most significant increases or decreases in crime rates for different types of crimes.
    * **Crime Hotspots:** Identification of areas with high crime concentration for targeted interventions.

    This data-driven approach can guide effective resource allocation and crime prevention strategies to enhance public safety in Maryland.

    **Acknowledgement:** We acknowledge Data in Motion (https://datainmotion.co/) for providing this challenging crime analysis project and the opportunity to showcase data visualization techniques.

    Explore the app and gain valuable insights to support strategic decision-making for crime reduction in Maryland.
    """)

    # Footer section
    st.markdown(
    """
    Made with ❤️ by [Mebarek](https://www.linkedin.com/in/mohammed-mecheter/). 
    [GitHub](https://github.com/Mohammed-Mebarek-Mecheter/) | 
    [LinkedIn](https://www.linkedin.com/in/mohammed-mecheter/) | 
    [Portfolio](https://mebarek.pages.dev/)
    """
    )
