import streamlit as st
import altair as alt
from app.data.data_loader import load_data

def show():
    st.header("Crime Distribution Analysis in Maryland")
    st.write("Explore the distribution and trends of different crime types in Maryland over the years.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define crime types
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggAssault', 'BreakAndEnter', 'LarcenyTheft', 'MotorVehicleTheft']

    # Prepare data
    crime_data = df[crime_types + ['Year']].groupby('Year').sum().reset_index()
    crime_data_melted = crime_data.melt('Year', var_name='Crime Type', value_name='Count')

    # Add crime type filter
    selected_crimes = st.multiselect(
        "Select crime types to display:",
        options=crime_types,
        default=crime_types[:3]  # Default to showing first 3 crime types
    )

    if not selected_crimes:
        st.warning("Please select at least one crime type.")
        return

    # Filter data based on selection
    filtered_data = crime_data_melted[crime_data_melted['Crime Type'].isin(selected_crimes)]

    # Create heatmap
    heatmap = alt.Chart(filtered_data).mark_rect().encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Crime Type:N', title='Crime Type'),
        color=alt.Color('Count:Q', title='Count', scale=alt.Scale(scheme='reds')),
        tooltip=[
            alt.Tooltip('Year:O', title='Year'),
            alt.Tooltip('Crime Type:N', title='Crime Type'),
            alt.Tooltip('Count:Q', title='Count', format=',')
        ]
    ).properties(
        width=700,
        height=400,
        title="Crime Type Distribution Over Years"
    )

    # Display heatmap
    st.altair_chart(heatmap, use_container_width=True)

    # Display total crime count as a line chart
    total_crime_data = crime_data.melt('Year', var_name='Crime Type', value_name='Count')
    total_crime_data = total_crime_data.groupby('Year')['Count'].sum().reset_index()

    total_crime_chart = alt.Chart(total_crime_data).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Count:Q', title='Total Number of Crimes'),
        tooltip=['Year:O', alt.Tooltip('Count:Q', format=',')]
    ).properties(
        title='Total Crime Count Over Time',
        width=700,
        height=300
    ).interactive()

    st.altair_chart(total_crime_chart, use_container_width=True)

    # Add year selector
    selected_year = st.slider('Select a year for detailed analysis:', min_value=int(df['Year'].min()), max_value=int(df['Year'].max()))

    # Pie chart for selected year
    year_data = crime_data_melted[crime_data_melted['Year'] == selected_year]
    pie_chart = alt.Chart(year_data).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Crime Type", type="nominal", scale=alt.Scale(scheme='category10')),
        tooltip=['Crime Type', alt.Tooltip('Count:Q', format=',')]
    ).properties(
        title=f'Crime Distribution in {selected_year}',
        width=400,
        height=400
    )

    st.altair_chart(pie_chart, use_container_width=True)

    # Calculate and display statistics
    total_crimes = year_data['Count'].sum()
    st.subheader(f"Crime Statistics for {selected_year}")
    st.write(f"Total number of reported crimes: {total_crimes:,}")

    # Display percentage for each crime type
    for crime_type in crime_types:
        crime_count = year_data[year_data['Crime Type'] == crime_type]['Count'].values[0]
        percentage = (crime_count / total_crimes) * 100
        st.write(f"{crime_type}: {crime_count:,} ({percentage:.2f}%)")

    # Trend analysis for each crime type
    st.subheader("Trend Analysis for Each Crime Type")
    selected_crime = st.selectbox("Select a crime type for trend analysis:", crime_types)

    trend_data = crime_data_melted[crime_data_melted['Crime Type'] == selected_crime]
    trend_chart = alt.Chart(trend_data).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Count:Q', title='Number of Crimes'),
        tooltip=['Year:O', alt.Tooltip('Count:Q', format=',')]
    ).properties(
        title=f'Trend of {selected_crime} in Maryland (1975-2020)',
        width=700,
        height=400
    ).interactive()

    st.altair_chart(trend_chart, use_container_width=True)

    # Additional insights
    st.subheader("Key Insights")
    st.write("1. The distribution of crime types has changed over the years, with some crimes becoming more or less prevalent.")
    st.write("2. Property crimes (such as Larceny Theft and Breaking and Entering) generally make up a larger portion of total crimes compared to violent crimes.")
    st.write("3. The trends for different crime types can vary significantly, reflecting changes in society, law enforcement strategies, and reporting practices.")
    st.write("4. While some crime types show a general decreasing trend over the years, others may have increased or remained relatively stable.")
    st.write("5. It's important to consider both the absolute numbers and the percentages when analyzing crime distribution, as the total number of crimes may have changed over time.")

    # Allow users to download the data
    csv = crime_data_melted.to_csv(index=False)
    st.download_button(
        label="Download crime distribution data as CSV",
        data=csv,
        file_name="maryland_crime_distribution.csv",
        mime="text/csv",
    )
