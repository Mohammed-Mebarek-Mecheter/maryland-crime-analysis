import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from app.data.data_loader import load_data

def show():
    st.header("Population and Crime Rate Correlation Analysis")
    st.write("Explore the relationship between population size and various crime rates across different jurisdictions in Maryland.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define columns of interest
    columns_of_interest = ['Population', 'MurderPer100k', 'RapePer100k', 'RobberyPer100k',
                           'AggAssaultPer100k', 'BreakAndEnterPer100k', 'LarcenyTheftPer100k', 'MotorVehicleTheftPer100k']

    # Create correlation matrix
    crime_population_data = df[columns_of_interest]
    correlation_matrix = crime_population_data.corr()

    # Heatmap
    st.subheader("Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, ax=ax)
    # Set background color to black
    ax.set_facecolor('blue')
    plt.title("Correlation between Population and Crime Rates")
    st.pyplot(fig)

    # Interpretation of the heatmap
    st.write("This heatmap shows the correlation coefficients between population and various crime rates. "
             "A value close to 1 indicates a strong positive correlation, while a value close to -1 indicates "
             "a strong negative correlation. Values close to 0 suggest weak or no correlation.")

    # Select a crime type for detailed analysis
    st.subheader("Detailed Analysis")
    crime_type = st.selectbox("Select a crime type for detailed analysis:",
                              columns_of_interest[1:])

    # Scatter plot
    fig = px.scatter(df, x='Population', y=crime_type,
                     hover_data=['Jurisdiction', 'Year'],
                     title=f"Population vs {crime_type}",
                     labels={'Population': 'Population', crime_type: f'{crime_type} (per 100k)'},
                     trendline="ols")
    st.plotly_chart(fig)

    # Correlation coefficient
    correlation = df['Population'].corr(df[crime_type])
    st.write(f"The correlation coefficient between Population and {crime_type} is {correlation:.2f}")

    # Interpretation
    if abs(correlation) < 0.3:
        st.write("This suggests a weak correlation between population size and this crime rate.")
    elif abs(correlation) < 0.7:
        st.write("This suggests a moderate correlation between population size and this crime rate.")
    else:
        st.write("This suggests a strong correlation between population size and this crime rate.")

    # Top 5 jurisdictions
    st.subheader("Top 5 Jurisdictions")
    top_5 = df.groupby('Jurisdiction')[crime_type].mean().sort_values(ascending=False).head()
    st.table(top_5)

    # Additional insights
    st.subheader("Additional Insights")
    st.write("1. The correlation between population and crime rates varies across different types of crimes.")
    st.write("2. Some crime rates may be more strongly correlated with population size than others.")
    st.write("3. Other factors beyond population size, such as economic conditions, law enforcement strategies, "
             "and social factors, likely play significant roles in determining crime rates.")
    st.write("4. It's important to note that correlation does not imply causation. A larger population doesn't "
             "necessarily cause higher crime rates; there may be other underlying factors at play.")

    # Allow users to download the correlation matrix
    csv = correlation_matrix.to_csv(index=True)
    st.download_button(
        label="Download correlation matrix as CSV",
        data=csv,
        file_name="population_crime_correlation.csv",
        mime="text/csv",
    )