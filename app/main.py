import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
from app.components import navigation, introduction, trend_analysis, crime_distribution, geographical_analysis, population_correlation, crime_hotspots, crime_rate_changes
from app.config import APP_TITLE, SIDEBAR_TITLE

# Set the page configuration as the first Streamlit command
st.set_page_config(page_title=APP_TITLE, layout="wide")

# Function to include local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Include custom CSS
local_css("assets/styles.css")

# Main function to control the app
def main():
    st.sidebar.title(SIDEBAR_TITLE)
    choice = navigation.sidebar()

    if choice == "Introduction":
        introduction.show()
    elif choice == "Trend Analysis":
        trend_analysis.show()
    elif choice == "Crime Distribution":
        crime_distribution.show()
    elif choice == "Geographical Analysis":
        geographical_analysis.show()
    elif choice == "Population Correlation":
        population_correlation.show()
    elif choice == "Crime Hotspots":
        crime_hotspots.show()
    elif choice == "Crime Rate Changes":
        crime_rate_changes.show()

if __name__ == "__main__":
    main()
