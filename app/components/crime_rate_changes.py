import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from app.data.data_loader import load_data

def calculate_capped_pct_change(series, cap=1000):
    """Calculate percentage change with capping for extreme values."""
    pct_change = series.pct_change()
    return pct_change.clip(lower=-cap, upper=cap)

def prepare_data(df, crime_types):
    """Prepare data for analysis and visualization."""
    crime_data = df[crime_types + ['Year']].set_index('Year')
    crime_data_pct_change = crime_data.apply(calculate_capped_pct_change).reset_index().melt('Year', var_name='Crime Type', value_name='Pct Change')
    return crime_data_pct_change.dropna()

def create_line_chart(data):
    """Create an Altair line chart for crime rate changes."""
    return alt.Chart(data).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Pct Change:Q', title='Percentage Change', axis=alt.Axis(format='%')),
        color=alt.Color('Crime Type:N', title='Crime Type'),
        tooltip=[
            alt.Tooltip('Year:O', title='Year'),
            alt.Tooltip('Crime Type:N', title='Crime Type'),
            alt.Tooltip('Pct Change:Q', title='Percentage Change', format='.2%')
        ]
    ).properties(
        width=700,
        height=400,
        title="Percentage Change in Crime Rates Over Time"
    ).interactive()

def format_pct_change(value):
    """Format percentage change, handling extreme values."""
    if pd.isna(value):
        return 'N/A'
    elif value == 10:  # Our cap value
        return '>1000%'
    elif value == -10:  # Our negative cap value
        return '<-1000%'
    else:
        return f'{value:.2%}'

def show_top_changes(data, top_n=5):
    """Display top increases and decreases in crime rates."""
    data['Absolute Change'] = data['Pct Change'].abs()
    top_increases = data.nlargest(top_n, 'Pct Change')
    top_decreases = data.nsmallest(top_n, 'Pct Change')

    st.write(f"### Top {top_n} Increases in Crime Rates")
    st.table(top_increases[['Year', 'Crime Type', 'Pct Change']].style.format({'Pct Change': format_pct_change}))

    st.write(f"### Top {top_n} Decreases in Crime Rates")
    st.table(top_decreases[['Year', 'Crime Type', 'Pct Change']].style.format({'Pct Change': format_pct_change}))

def show():
    st.header("Crime Rate Changes Analysis in Maryland")
    st.write("Analyze the most significant increases or decreases in crime rates for different types of crimes in Maryland over the years.")

    # Load and prepare data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']
    crime_data_pct_change = prepare_data(df, crime_types)

    # User interface for crime type selection
    selected_crimes = st.multiselect(
        "Select crime types to display:",
        options=crime_types,
        default=crime_types
    )

    if not selected_crimes:
        st.warning("Please select at least one crime type.")
        return

    # Filter data based on selection
    filtered_data = crime_data_pct_change[crime_data_pct_change['Crime Type'].isin(selected_crimes)]

    # Display line chart
    line_chart = create_line_chart(filtered_data)
    st.altair_chart(line_chart, use_container_width=True)

    # Show top changes
    show_top_changes(filtered_data)

    # Data download option
    csv = crime_data_pct_change.to_csv(index=False)
    st.download_button(
        label="Download crime rate changes data as CSV",
        data=csv,
        file_name="maryland_crime_rate_changes.csv",
        mime="text/csv",
    )
