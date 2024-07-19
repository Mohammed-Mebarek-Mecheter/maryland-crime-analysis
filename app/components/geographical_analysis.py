import streamlit as st
import plotly.express as px
from app.data.data_loader import load_data

def show():
    st.header("Geographical Analysis of Crime Rates in Maryland")
    st.write("Explore crime rates across different jurisdictions in Maryland.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define crime types
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']

    # Calculate total crime and crime rate
    df['TotalCrime'] = df[crime_types].sum(axis=1)
    df['CrimeRate'] = df['TotalCrime'] / df['Population'] * 100000  # per 100,000 population

    # Calculate average crime rates by jurisdiction
    avg_crime_rates = df.groupby('Jurisdiction').agg({
        'CrimeRate': 'mean',
        'Population': 'mean',
        'TotalCrime': 'mean'
    }).reset_index()

    # Sort jurisdictions by crime rate
    avg_crime_rates = avg_crime_rates.sort_values('CrimeRate', ascending=False)

    # Create bar chart
    fig = px.bar(avg_crime_rates,
                 x='Jurisdiction',
                 y='CrimeRate',
                 title="Average Crime Rates by Jurisdiction (per 100,000 population)",
                 labels={'CrimeRate': 'Crime Rate (per 100,000)', 'Jurisdiction': 'Jurisdiction'},
                 color='CrimeRate',
                 color_continuous_scale='Reds',
                 hover_data=['Population', 'TotalCrime'])

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Add a slider to select number of top/bottom jurisdictions
    num_jurisdictions = st.slider("Select number of top/bottom jurisdictions to display", 5, 20, 10)

    # Display top and bottom jurisdictions
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Top {num_jurisdictions} Jurisdictions by Crime Rate")
        st.table(avg_crime_rates.head(num_jurisdictions).style.format({
            'CrimeRate': '{:.2f}',
            'Population': '{:,.0f}',
            'TotalCrime': '{:.0f}'
        }))

    with col2:
        st.subheader(f"Bottom {num_jurisdictions} Jurisdictions by Crime Rate")
        st.table(avg_crime_rates.tail(num_jurisdictions).style.format({
            'CrimeRate': '{:.2f}',
            'Population': '{:,.0f}',
            'TotalCrime': '{:.0f}'
        }))

    # Add crime type breakdown
    st.subheader("Crime Type Breakdown")
    selected_jurisdiction = st.selectbox("Select a jurisdiction:", avg_crime_rates['Jurisdiction'])

    jurisdiction_data = df[df['Jurisdiction'] == selected_jurisdiction]
    crime_breakdown = jurisdiction_data[crime_types].mean()

    fig_pie = px.pie(values=crime_breakdown.values, names=crime_breakdown.index,
                     title=f"Crime Type Breakdown for {selected_jurisdiction}")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Time series analysis
    st.subheader("Crime Rate Over Time")
    jurisdiction_time_series = df[df['Jurisdiction'] == selected_jurisdiction].groupby('Year')['CrimeRate'].mean().reset_index()

    fig_time = px.line(jurisdiction_time_series, x='Year', y='CrimeRate',
                       title=f"Crime Rate Over Time in {selected_jurisdiction}")
    st.plotly_chart(fig_time, use_container_width=True)

    # Additional insights
    st.subheader("Key Insights")
    st.write(f"1. The jurisdiction with the highest average crime rate is {avg_crime_rates.iloc[0]['Jurisdiction']} "
             f"with a rate of {avg_crime_rates.iloc[0]['CrimeRate']:.2f} crimes per 100,000 population.")
    st.write(f"2. The jurisdiction with the lowest average crime rate is {avg_crime_rates.iloc[-1]['Jurisdiction']} "
             f"with a rate of {avg_crime_rates.iloc[-1]['CrimeRate']:.2f} crimes per 100,000 population.")
    st.write("3. Urban areas tend to have higher crime rates compared to rural areas, which could be due to factors "
             "such as population density, economic conditions, and social factors.")
    st.write("4. The crime type breakdown varies across jurisdictions, reflecting local patterns and challenges.")
    st.write("5. Crime rates have generally shown a decreasing trend over time in many jurisdictions, but there are exceptions.")

    # Allow users to download the data
    csv = avg_crime_rates.to_csv(index=False)
    st.download_button(
        label="Download crime rate data as CSV",
        data=csv,
        file_name="maryland_crime_rates_by_jurisdiction.csv",
        mime="text/csv",
    )