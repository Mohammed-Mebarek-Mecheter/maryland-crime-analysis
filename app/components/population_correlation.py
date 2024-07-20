import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from app.data.data_loader import load_data

def calculate_correlation(x, y):
    return stats.pearsonr(x, y)[0]

def show():
    st.header("Population and Crime Rate Correlation Analysis in Maryland")
    st.write("Explore the relationship between population size and various crime rates across different jurisdictions in Maryland.")

    # Load data
    df = load_data('app/data/cleaned_MD_Crime_Data.csv')

    # Define columns of interest
    crime_types = ['MurderPer100k', 'RapePer100k', 'RobberyPer100k', 'AggAssaultPer100k',
                   'BreakAndEnterPer100k', 'LarcenyTheftPer100k', 'MotorVehicleTheftPer100k']

    # Calculate average crime rates and population for each jurisdiction
    avg_data = df.groupby('Jurisdiction')[['Population'] + crime_types].mean().reset_index()

    # Calculate correlation coefficients
    correlations = [calculate_correlation(avg_data['Population'], avg_data[crime]) for crime in crime_types]
    correlation_df = pd.DataFrame({'Crime Type': crime_types, 'Correlation': correlations})
    correlation_df = correlation_df.sort_values('Correlation', ascending=False)

    # Create correlation bar chart
    fig_corr = px.bar(correlation_df, x='Crime Type', y='Correlation',
                      title='Correlation between Population and Crime Rates',
                      labels={'Correlation': 'Pearson Correlation Coefficient'},
                      color='Correlation',
                      color_continuous_scale='RdBu_r',
                      range_color=[-1, 1])
    fig_corr.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.write("This chart shows the correlation coefficients between population and various crime rates. "
             "A value close to 1 indicates a strong positive correlation, while a value close to -1 indicates "
             "a strong negative correlation. Values close to 0 suggest weak or no correlation.")

    # Scatter plots for each crime type
    st.subheader("Detailed Analysis: Population vs Crime Rates")
    fig = make_subplots(rows=3, cols=3, subplot_titles=crime_types)

    for i, crime_type in enumerate(crime_types, 1):
        row = (i - 1) // 3 + 1
        col = (i - 1) % 3 + 1

        fig.add_trace(
            go.Scatter(x=avg_data['Population'], y=avg_data[crime_type], mode='markers',
                       name=crime_type, text=avg_data['Jurisdiction'],
                       hovertemplate='<b>%{text}</b><br>Population: %{x}<br>' + crime_type + ': %{y:.2f}<extra></extra>'),
            row=row, col=col
        )

        # Add trendline
        z = np.polyfit(avg_data['Population'], avg_data[crime_type], 1)
        y_fit = np.poly1d(z)(avg_data['Population'])
        fig.add_trace(
            go.Scatter(x=avg_data['Population'], y=y_fit, mode='lines',
                       name=f'Trendline ({crime_type})', line=dict(color='red', dash='dash')),
            row=row, col=col
        )

        fig.update_xaxes(title_text="Population", row=row, col=col)
        fig.update_yaxes(title_text="Rate per 100k", row=row, col=col)

    fig.update_layout(height=1200, width=1000, title_text="Population vs Crime Rates Scatter Plots")
    st.plotly_chart(fig, use_container_width=True)

    # Linear regression analysis
    st.subheader("Linear Regression Analysis")
    selected_crime = st.selectbox("Select a crime type for detailed regression analysis:", crime_types)

    slope, intercept, r_value, p_value, std_err = stats.linregress(avg_data['Population'], avg_data[selected_crime])

    fig_regression = px.scatter(avg_data, x='Population', y=selected_crime,
                                trendline='ols', trendline_color_override='red',
                                hover_data=['Jurisdiction'],
                                labels={'Population': 'Population', selected_crime: f'{selected_crime} (per 100k)'},
                                title=f'Linear Regression: Population vs {selected_crime}')

    st.plotly_chart(fig_regression, use_container_width=True)

    st.write(f"R-squared value: {r_value**2:.4f}")
    st.write(f"p-value: {p_value:.4f}")

    if p_value < 0.05:
        st.write("The relationship between population and this crime rate is statistically significant.")
    else:
        st.write("There is no statistically significant relationship between population and this crime rate.")

    # Additional insights
    st.subheader("Key Insights")
    st.write("1. The correlation between population and crime rates varies across different types of crimes.")
    st.write("2. Some crime rates show a stronger correlation with population size than others.")
    st.write("3. A larger population doesn't necessarily mean higher crime rates for all types of crimes.")
    st.write("4. Other factors beyond population size, such as economic conditions, law enforcement strategies, "
             "and social factors, likely play significant roles in determining crime rates.")
    st.write("5. It's important to note that correlation does not imply causation. Further analysis would be needed "
             "to determine the underlying causes of variations in crime rates.")

    # Allow users to download the data
    csv = avg_data.to_csv(index=False)
    st.download_button(
        label="Download average crime rates by jurisdiction as CSV",
        data=csv,
        file_name="maryland_avg_crime_rates_by_jurisdiction.csv",
        mime="text/csv",
    )
