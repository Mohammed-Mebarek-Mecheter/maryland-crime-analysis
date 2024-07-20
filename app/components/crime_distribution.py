import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from app.data.data_loader import load_data

def calculate_capped_pct_change(series, cap=10):
    """Calculate percentage change with capping for extreme values."""
    pct_change = series.pct_change()
    return pct_change.clip(lower=-cap, upper=cap)

def prepare_data(df, selected_columns):
    """Prepare data for analysis and visualization."""
    crime_data = df[selected_columns + ['Year']].groupby('Year').sum()
    crime_data_pct_change = crime_data.apply(calculate_capped_pct_change).reset_index().melt('Year', var_name='Crime Type', value_name='Pct Change')
    return crime_data_pct_change.dropna()

def create_stacked_area_chart(data):
    """Create an Altair stacked area chart for crime distribution."""
    return alt.Chart(data).mark_area().encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Count:Q', stack='normalize', axis=alt.Axis(format='%'), title='Percentage of Total Crimes'),
        color=alt.Color('Crime Type:N', scale=alt.Scale(scheme='category10')),
        tooltip=[
            alt.Tooltip('Year:O', title='Year'),
            alt.Tooltip('Crime Type:N', title='Crime Type'),
            alt.Tooltip('Count:Q', title='Count', format=','),
            alt.Tooltip('Count:Q', title='Percentage', format='.2%')
        ]
    ).properties(
        width=700,
        height=400,
        title="Distribution of Crime Types in Maryland"
    ).interactive()

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
        return f'{value:.2f}%'

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
    st.header("Crime Distribution and Rate Changes Analysis in Maryland")
    st.write("Explore the distribution of crime types and analyze significant changes in crime rates in Maryland over the years.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define crime types
    crime_types_absolute = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']
    crime_types_per_100k = [f'{crime}Per100k' for crime in crime_types_absolute]

    # User interface for metric selection
    metric_choice = st.radio(
        "Choose the metric for analysis:",
        ("Absolute Numbers", "Rates per 100,000 Population")
    )

    selected_columns = crime_types_absolute if metric_choice == "Absolute Numbers" else crime_types_per_100k

    # User interface for crime type selection
    selected_crimes = st.multiselect(
        "Select crime types to display:",
        options=selected_columns,
        default=selected_columns[:3]
    )

    if not selected_crimes:
        st.warning("Please select at least one crime type.")
        return

    # Prepare data for stacked area chart
    crime_data = df[selected_crimes + ['Year']].groupby('Year').sum().reset_index()
    crime_data_melted = crime_data.melt('Year', var_name='Crime Type', value_name='Count')

    # Display stacked area chart
    stacked_area_chart = create_stacked_area_chart(crime_data_melted)
    st.altair_chart(stacked_area_chart, use_container_width=True)

    # Most common crime types
    st.subheader("Most Common Crime Types")
    total_by_crime = crime_data[selected_crimes].sum().sort_values(ascending=False)
    total_all_crimes = total_by_crime.sum()

    crime_summary = pd.DataFrame({
        'Crime Type': total_by_crime.index,
        'Total Count': total_by_crime.values,
        'Percentage': (total_by_crime.values / total_all_crimes) * 100
    })

    st.table(crime_summary.style.format({
        'Total Count': '{:,.0f}',
        'Percentage': '{:.2f}%'
    }))

    # Text summary of most common crime types
    st.write("### Summary of Most Common Crime Types")
    top_crimes = crime_summary.head(3)['Crime Type'].tolist()
    st.write(f"The three most common types of crimes in Maryland over the analyzed period are:")
    for i, crime in enumerate(top_crimes, 1):
        st.write(f"{i}. {crime} ({crime_summary.loc[crime_summary['Crime Type'] == crime, 'Percentage'].values[0]:.2f}% of all crimes)")

    # Calculate change in distribution from start to end
    start_year = crime_data['Year'].min()
    end_year = crime_data['Year'].max()
    start_distribution = crime_data[crime_data['Year'] == start_year][selected_crimes].iloc[0]
    end_distribution = crime_data[crime_data['Year'] == end_year][selected_crimes].iloc[0]

    distribution_change = pd.DataFrame({
        'Crime Type': selected_crimes,
        'Start Percentage': (start_distribution / start_distribution.sum()) * 100,
        'End Percentage': (end_distribution / end_distribution.sum()) * 100,
        'Change': ((end_distribution / end_distribution.sum()) - (start_distribution / start_distribution.sum())) * 100
    })

    st.write(f"### Change in Crime Distribution from {start_year} to {end_year}")
    st.table(distribution_change.style.format({
        'Start Percentage': '{:.2f}%',
        'End Percentage': '{:.2f}%',
        'Change': '{:+.2f}%'
    }))

    # Text summary of significant changes
    st.write("### Summary of Significant Changes in Crime Distribution")
    significant_changes = distribution_change[abs(distribution_change['Change']) > 1].sort_values('Change', ascending=False)

    if not significant_changes.empty:
        for _, row in significant_changes.iterrows():
            change_direction = "increased" if row['Change'] > 0 else "decreased"
            st.write(f"- The proportion of {row['Crime Type']} {change_direction} by {abs(row['Change']):.2f} percentage points.")
    else:
        st.write("No significant changes (>1 percentage point) in the distribution of crime types were observed.")

    # Prepare data for percentage change analysis
    crime_data_pct_change = prepare_data(df, selected_crimes)

    # Display line chart for percentage changes
    line_chart = create_line_chart(crime_data_pct_change)
    st.altair_chart(line_chart, use_container_width=True)

    # Show top changes
    show_top_changes(crime_data_pct_change)

    crime_summary = pd.DataFrame({
        'Crime Type': total_by_crime.index,
        'Total Count': total_by_crime.values,
        'Percentage': (total_by_crime.values / total_all_crimes) * 100
    })

    st.table(crime_summary.style.format({
        'Total Count': '{:,.0f}',
        'Percentage': '{:.2f}%'
    }))

    # Key insights
    st.subheader("Key Insights")
    st.write("1. The stacked area chart shows the distribution of crime types over time, allowing you to see how the proportion of each crime type has changed.")
    st.write("2. The line chart displays the percentage change in crime rates, helping identify significant increases or decreases over time.")
    st.write("3. The tables of top increases and decreases highlight the most dramatic changes in crime rates.")
    st.write("4. The summary table shows the most common types of crimes over the entire period.")
    st.write("5. You can switch between absolute numbers and rates per 100,000 population to get different perspectives on the data.")

    # Data download option
    csv = crime_data_melted.to_csv(index=False)
    st.download_button(
        label="Download crime distribution data as CSV",
        data=csv,
        file_name="maryland_crime_distribution.csv",
        mime="text/csv",
    )
