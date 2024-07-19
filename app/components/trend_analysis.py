import streamlit as st
import altair as alt
import pandas as pd
from app.data.data_loader import load_data

def show():
    st.header("Crime Rate Trend Analysis in Maryland (1975-2020)")
    st.write("Explore how overall and specific crime rates have changed over the years in Maryland.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Ensure 'Year' is datetime
    df['Year'] = pd.to_datetime(df['Year'], format='%Y')

    # Calculate overall crime rate
    crime_rates = df.groupby('Year')['OverallCrimeRatePer100k'].mean().reset_index()

    # Create overall trend chart
    overall_chart = alt.Chart(crime_rates).mark_line(point=True).encode(
        x=alt.X('Year:T', title='Year'),
        y=alt.Y('OverallCrimeRatePer100k:Q', title='Overall Crime Rate (per 100k)'),
        tooltip=['Year:T', alt.Tooltip('OverallCrimeRatePer100k:Q', format='.2f')]
    ).properties(
        title='Overall Crime Rate Trend in Maryland (1975-2020)'
    ).interactive()

    st.altair_chart(overall_chart, use_container_width=True)

    # Calculate percent change
    crime_rates['PercentChange'] = crime_rates['OverallCrimeRatePer100k'].pct_change() * 100

    # Display key statistics
    st.subheader("Key Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("1975 Crime Rate", f"{crime_rates['OverallCrimeRatePer100k'].iloc[0]:.2f}")
    col2.metric("2020 Crime Rate", f"{crime_rates['OverallCrimeRatePer100k'].iloc[-1]:.2f}")
    col3.metric("Overall Change", f"{(crime_rates['OverallCrimeRatePer100k'].iloc[-1] - crime_rates['OverallCrimeRatePer100k'].iloc[0]) / crime_rates['OverallCrimeRatePer100k'].iloc[0] * 100:.2f}%")

    # Specific crime types analysis
    st.subheader("Specific Crime Types Analysis")
    crime_types = ['MurderPer100k', 'RapePer100k', 'RobberyPer100k', 'AggAssaultPer100k',
                   'BreakAndEnterPer100k', 'LarcenyTheftPer100k', 'MotorVehicleTheftPer100k']

    selected_crimes = st.multiselect("Select crime types to analyze:", crime_types, default=['MurderPer100k', 'RobberyPer100k'])

    if selected_crimes:
        specific_crime_rates = df.groupby('Year')[selected_crimes].mean().reset_index()
        specific_crime_rates = pd.melt(specific_crime_rates, id_vars=['Year'], value_vars=selected_crimes,
                                       var_name='Crime Type', value_name='Rate')

        specific_chart = alt.Chart(specific_crime_rates).mark_line(point=True).encode(
            x=alt.X('Year:T', title='Year'),
            y=alt.Y('Rate:Q', title='Crime Rate (per 100k)'),
            color='Crime Type:N',
            tooltip=['Year:T', 'Crime Type:N', alt.Tooltip('Rate:Q', format='.2f')]
        ).properties(
            title='Specific Crime Rate Trends in Maryland (1975-2020)'
        ).interactive()

        st.altair_chart(specific_chart, use_container_width=True)

    # Year-over-year change
    st.subheader("Year-over-Year Change in Overall Crime Rate")
    yoy_chart = alt.Chart(crime_rates).mark_bar().encode(
        x=alt.X('Year:T', title='Year'),
        y=alt.Y('PercentChange:Q', title='Percent Change'),
        color=alt.condition(
            alt.datum.PercentChange > 0,
            alt.value("red"),  # The positive color
            alt.value("green")  # The negative color
        ),
        tooltip=['Year:T', alt.Tooltip('PercentChange:Q', format='.2f')]
    ).properties(
        title='Year-over-Year Change in Overall Crime Rate'
    ).interactive()

    st.altair_chart(yoy_chart, use_container_width=True)

    # Additional insights
    st.subheader("Key Insights")
    st.write("1. The overall crime rate in Maryland has shown a general declining trend from 1975 to 2020.")
    st.write("2. There have been fluctuations in the crime rate, with some years showing increases.")
    st.write("3. Different types of crimes may show different trends over time.")
    st.write("4. The year-over-year change helps identify specific periods of significant increase or decrease in crime rates.")
    st.write("5. Factors such as economic conditions, law enforcement strategies, and social changes may contribute to these trends.")

    # Allow users to download the data
    csv = crime_rates.to_csv(index=False)
    st.download_button(
        label="Download trend data as CSV",
        data=csv,
        file_name="maryland_crime_rate_trend.csv",
        mime="text/csv",
    )