import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.data.data_loader import load_data
import pandas as pd

def show():
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')
    st.header("Crime Hotspots in Maryland")
    st.write("Identify and analyze crime hotspots across different jurisdictions in Maryland.")

    # Define the crime types to be analyzed
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']

    # Calculate the total crime rate per jurisdiction over the entire period
    df['TotalCrime'] = df[crime_types].sum(axis=1)
    total_crime_per_jurisdiction = df.groupby('Jurisdiction').agg({
        'TotalCrime': 'sum',
        'Population': 'mean'  # Assuming you have a Population column
    }).reset_index()

    # Calculate crime rate per 100,000 inhabitants
    total_crime_per_jurisdiction['CrimeRate'] = (total_crime_per_jurisdiction['TotalCrime'] / total_crime_per_jurisdiction['Population']) * 100000

    # Sort the jurisdictions by crime rate in descending order to identify hotspots
    total_crime_per_jurisdiction = total_crime_per_jurisdiction.sort_values(by='CrimeRate', ascending=False)

    # Create a bar chart to visualize the crime rate per jurisdiction
    fig = px.bar(total_crime_per_jurisdiction,
                 x='Jurisdiction',
                 y='CrimeRate',
                 title="Crime Rate by Jurisdiction (per 100,000 inhabitants)",
                 labels={'CrimeRate': 'Crime Rate per 100,000', 'Jurisdiction': 'Jurisdiction'},
                 color='CrimeRate',
                 color_continuous_scale='Reds',
                 hover_data=['TotalCrime', 'Population'])

    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    # Add a slider to select number of top hotspots
    num_hotspots = st.slider("Select number of top hotspots to display", 5, 20, 10)

    # Highlight the top hotspots
    st.subheader(f"Top {num_hotspots} Crime Hotspots:")
    top_hotspots = total_crime_per_jurisdiction.head(num_hotspots)

    # Format the data for display
    top_hotspots_display = top_hotspots.copy()
    top_hotspots_display['CrimeRate'] = top_hotspots_display['CrimeRate'].round(2)
    top_hotspots_display['TotalCrime'] = top_hotspots_display['TotalCrime'].astype(int)
    top_hotspots_display['Population'] = top_hotspots_display['Population'].astype(int)

    st.table(top_hotspots_display)

    # Add a multi-select for crime types
    selected_crimes = st.multiselect("Select crime types to analyze:", crime_types, default=crime_types)

    if selected_crimes:
        st.subheader("Crime Type Breakdown for Top Hotspots")

        # Calculate the breakdown of crime types for the top hotspots
        top_jurisdictions = top_hotspots['Jurisdiction'].tolist()
        crime_breakdown = df[df['Jurisdiction'].isin(top_jurisdictions)].groupby('Jurisdiction')[selected_crimes].sum()

        # Create a stacked bar chart for crime type breakdown
        fig_breakdown = go.Figure()
        for crime in selected_crimes:
            fig_breakdown.add_trace(go.Bar(x=crime_breakdown.index, y=crime_breakdown[crime], name=crime))

        fig_breakdown.update_layout(barmode='stack', title="Crime Type Breakdown for Top Hotspots",
                                    xaxis_title="Jurisdiction", yaxis_title="Number of Crimes")

        st.plotly_chart(fig_breakdown, use_container_width=True)

    # Add some analysis and insights
    st.subheader("Key Insights:")
    st.write(f"1. The jurisdiction with the highest crime rate is {top_hotspots.iloc[0]['Jurisdiction']} "
             f"with a rate of {top_hotspots.iloc[0]['CrimeRate']:.2f} crimes per 100,000 inhabitants.")
    st.write(f"2. The total number of crimes recorded across all jurisdictions is {total_crime_per_jurisdiction['TotalCrime'].sum():,}.")
    st.write("3. Urban areas tend to have higher crime rates compared to rural areas, which could be due to factors such as population density and socioeconomic conditions.")

    # Allow users to download the data
    csv = total_crime_per_jurisdiction.to_csv(index=False)
    st.download_button(
        label="Download crime hotspots data as CSV",
        data=csv,
        file_name="crime_hotspots_maryland.csv",
        mime="text/csv",
    )