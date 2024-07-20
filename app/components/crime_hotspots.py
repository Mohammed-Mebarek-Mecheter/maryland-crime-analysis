import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app.data.data_loader import load_data
import pandas as pd
import numpy as np

def show():
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')
    st.header("Crime Hotspots in Maryland")
    st.write("Identify and analyze crime hotspots across different jurisdictions in Maryland to prioritize resource allocation.")

    # Define the crime types to be analyzed
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']

    # Calculate the total crime rate per jurisdiction over the entire period
    df['TotalCrime'] = df[crime_types].sum(axis=1)
    total_crime_per_jurisdiction = df.groupby('Jurisdiction').agg({
        'TotalCrime': 'sum',
        'Population': 'mean'
    }).reset_index()

    # Calculate crime rate per 100,000 inhabitants
    total_crime_per_jurisdiction['CrimeRate'] = (total_crime_per_jurisdiction['TotalCrime'] / total_crime_per_jurisdiction['Population']) * 100000

    # Calculate the average crime rate
    avg_crime_rate = total_crime_per_jurisdiction['CrimeRate'].mean()

    # Identify hotspots (jurisdictions with crime rates above average)
    total_crime_per_jurisdiction['Hotspot'] = total_crime_per_jurisdiction['CrimeRate'] > avg_crime_rate

    # Sort the jurisdictions by crime rate in descending order
    total_crime_per_jurisdiction = total_crime_per_jurisdiction.sort_values(by='CrimeRate', ascending=False)

    # Create a bar chart to visualize the crime rate per jurisdiction
    fig = px.bar(total_crime_per_jurisdiction,
                 x='Jurisdiction',
                 y='CrimeRate',
                 title="Crime Rate by Jurisdiction (per 100,000 inhabitants)",
                 labels={'CrimeRate': 'Crime Rate per 100,000', 'Jurisdiction': 'Jurisdiction'},
                 color='Hotspot',
                 color_discrete_map={True: 'red', False: 'blue'},
                 hover_data=['TotalCrime', 'Population'])

    # Update color legend
    fig.update_traces(showlegend=True)
    fig.data[0].name = 'Hotspot'
    fig.data[1].name = 'Not Hotspot'

    fig.add_hline(y=avg_crime_rate, line_dash="dash", line_color="green", annotation_text="Average Crime Rate")
    fig.update_layout(xaxis_tickangle=-45, legend_title_text='Hotspot Classification')

    st.plotly_chart(fig, use_container_width=True)

    # Explain hotspot classification
    st.write("**Hotspot Classification:**")
    st.write("- Hotspot (Red): Jurisdictions with crime rates above the average")
    st.write("- Not Hotspot (Blue): Jurisdictions with crime rates at or below the average")
    st.write(f"- Average Crime Rate: {avg_crime_rate:.2f} per 100,000 inhabitants")

    # Highlight the top hotspots
    num_hotspots = st.slider("Select number of top hotspots to display", 5, 20, 10)
    st.subheader(f"Top {num_hotspots} Crime Hotspots:")
    top_hotspots = total_crime_per_jurisdiction.head(num_hotspots)

    # Format the data for display
    top_hotspots_display = top_hotspots.copy()
    top_hotspots_display['CrimeRate'] = top_hotspots_display['CrimeRate'].round(2)
    top_hotspots_display['TotalCrime'] = top_hotspots_display['TotalCrime'].astype(int)
    top_hotspots_display['Population'] = top_hotspots_display['Population'].astype(int)

    st.table(top_hotspots_display[['Jurisdiction', 'CrimeRate', 'TotalCrime', 'Population']])

    # Crime type breakdown for top hotspots
    st.subheader("Crime Type Breakdown for Top Hotspots")
    top_jurisdictions = top_hotspots['Jurisdiction'].tolist()
    crime_breakdown = df[df['Jurisdiction'].isin(top_jurisdictions)].groupby('Jurisdiction')[crime_types].sum()

    # Normalize the crime counts to percentages
    crime_breakdown_pct = crime_breakdown.div(crime_breakdown.sum(axis=1), axis=0) * 100

    # Create a heatmap for crime type breakdown
    fig_heatmap = px.imshow(crime_breakdown_pct.T,
                            labels=dict(x="Jurisdiction", y="Crime Type", color="Percentage"),
                            x=crime_breakdown_pct.index,
                            y=crime_types,
                            color_continuous_scale="Reds",
                            title="Crime Type Distribution in Top Hotspots")

    fig_heatmap.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Trend analysis for top hotspots
    st.subheader("Crime Rate Trend for Top Hotspots")
    top_5_hotspots = top_hotspots['Jurisdiction'].head().tolist()
    trend_data = df[df['Jurisdiction'].isin(top_5_hotspots)]

    fig_trend = px.line(trend_data, x='Year', y='TotalCrime', color='Jurisdiction',
                        title="Total Crime Trend for Top 5 Hotspots",
                        labels={'TotalCrime': 'Total Crimes', 'Year': 'Year'})
    st.plotly_chart(fig_trend, use_container_width=True)

    # Resource allocation recommendation
    st.subheader("Resource Allocation Recommendations:")
    st.write("Based on the analysis, we recommend prioritizing the following areas for increased policing and resource allocation:")

    for i, (_, hotspot) in enumerate(top_hotspots.head().iterrows(), 1):
        dominant_crime = crime_breakdown_pct.loc[hotspot['Jurisdiction']].idxmax()
        st.write(f"{i}. {hotspot['Jurisdiction']}:")
        st.write(f"   - Crime Rate: {hotspot['CrimeRate']:.2f} per 100,000 inhabitants")
        st.write(f"   - Focus Area: {dominant_crime} (Highest percentage among crime types)")

    # Key insights
    st.subheader("Key Insights:")
    st.write(f"1. The jurisdiction with the highest crime rate is {top_hotspots.iloc[0]['Jurisdiction']} "
             f"with a rate of {top_hotspots.iloc[0]['CrimeRate']:.2f} crimes per 100,000 inhabitants.")
    st.write(f"2. {len(total_crime_per_jurisdiction[total_crime_per_jurisdiction['Hotspot']])} out of {len(total_crime_per_jurisdiction)} "
             f"jurisdictions are identified as hotspots (crime rate above average).")
    st.write("3. The heatmap shows that different hotspots may require different strategies based on their dominant crime types.")
    st.write("4. The trend analysis for top hotspots can help in understanding whether the situation is improving or worsening over time.")

    # Allow users to download the data
    csv = total_crime_per_jurisdiction.to_csv(index=False)
    st.download_button(
        label="Download crime hotspots data as CSV",
        data=csv,
        file_name="crime_hotspots_maryland.csv",
        mime="text/csv",
    )
