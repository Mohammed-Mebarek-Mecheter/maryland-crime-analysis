import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.data.data_loader import load_data

def show():
    st.header("Geographical Analysis of Crime Rates in Maryland")
    st.write("Explore crime rates across different jurisdictions in Maryland and compare them to the state average.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define crime types
    crime_types = ['MurderPer100k', 'RapePer100k', 'RobberyPer100k', 'AggAssaultPer100k',
                   'BreakAndEnterPer100k', 'LarcenyTheftPer100k', 'MotorVehicleTheftPer100k']

    # Calculate total crime rate
    df['TotalCrimeRate'] = df[crime_types].sum(axis=1)

    # Calculate average crime rates by jurisdiction
    avg_crime_rates = df.groupby('Jurisdiction').agg({
        'TotalCrimeRate': 'mean',
        'Population': 'mean'
    }).reset_index()

    # Calculate state average crime rate
    state_avg_crime_rate = avg_crime_rates['TotalCrimeRate'].mean()

    # Calculate difference from state average
    avg_crime_rates['DiffFromStateAvg'] = avg_crime_rates['TotalCrimeRate'] - state_avg_crime_rate
    avg_crime_rates['PercentDiffFromStateAvg'] = (avg_crime_rates['DiffFromStateAvg'] / state_avg_crime_rate) * 100

    # Sort jurisdictions by crime rate
    avg_crime_rates = avg_crime_rates.sort_values('TotalCrimeRate', ascending=False)

    # Create bar chart
    fig = px.bar(avg_crime_rates,
                 x='Jurisdiction',
                 y='TotalCrimeRate',
                 title="Average Crime Rates by Jurisdiction (per 100,000 population)",
                 labels={'TotalCrimeRate': 'Crime Rate (per 100,000)', 'Jurisdiction': 'Jurisdiction'},
                 color='DiffFromStateAvg',
                 color_continuous_scale='RdYlGn_r',
                 hover_data=['Population', 'PercentDiffFromStateAvg'])

    fig.add_hline(y=state_avg_crime_rate, line_dash="dash", line_color="red",
                  annotation_text="State Average", annotation_position="bottom right")

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Display top and bottom jurisdictions
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Jurisdictions by Crime Rate")
        st.table(avg_crime_rates.head().style.format({
            'TotalCrimeRate': '{:.2f}',
            'Population': '{:,.0f}',
            'DiffFromStateAvg': '{:.2f}',
            'PercentDiffFromStateAvg': '{:.2f}%'
        }))

    with col2:
        st.subheader("Bottom 5 Jurisdictions by Crime Rate")
        st.table(avg_crime_rates.tail().style.format({
            'TotalCrimeRate': '{:.2f}',
            'Population': '{:,.0f}',
            'DiffFromStateAvg': '{:.2f}',
            'PercentDiffFromStateAvg': '{:.2f}%'
        }))

    # Create scatter plot
    fig_scatter = px.scatter(avg_crime_rates, x='Population', y='TotalCrimeRate',
                             hover_name='Jurisdiction', size='Population', color='DiffFromStateAvg',
                             color_continuous_scale='RdYlGn_r',
                             title='Crime Rate vs Population by Jurisdiction')

    fig_scatter.add_hline(y=state_avg_crime_rate, line_dash="dash", line_color="red",
                          annotation_text="State Average", annotation_position="bottom right")

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Additional insights
    st.subheader("Key Insights")
    highest_rate = avg_crime_rates.iloc[0]
    lowest_rate = avg_crime_rates.iloc[-1]

    st.write(f"1. The jurisdiction with the highest average crime rate is {highest_rate['Jurisdiction']} "
             f"with a rate of {highest_rate['TotalCrimeRate']:.2f} crimes per 100,000 population, "
             f"{highest_rate['PercentDiffFromStateAvg']:.2f}% above the state average.")

    st.write(f"2. The jurisdiction with the lowest average crime rate is {lowest_rate['Jurisdiction']} "
             f"with a rate of {lowest_rate['TotalCrimeRate']:.2f} crimes per 100,000 population, "
             f"{abs(lowest_rate['PercentDiffFromStateAvg']):.2f}% below the state average.")

    st.write(f"3. The state average crime rate is {state_avg_crime_rate:.2f} crimes per 100,000 population.")

    above_avg = avg_crime_rates[avg_crime_rates['DiffFromStateAvg'] > 0]
    below_avg = avg_crime_rates[avg_crime_rates['DiffFromStateAvg'] < 0]
    st.write(f"4. {len(above_avg)} jurisdictions have crime rates above the state average, "
             f"while {len(below_avg)} are below average.")

    st.write("5. There appears to be a correlation between population size and crime rate, "
             "with more populous jurisdictions generally having higher crime rates.")

    # Allow users to download the data
    csv = avg_crime_rates.to_csv(index=False)
    st.download_button(
        label="Download crime rate data as CSV",
        data=csv,
        file_name="maryland_crime_rates_by_jurisdiction.csv",
        mime="text/csv",
    )
