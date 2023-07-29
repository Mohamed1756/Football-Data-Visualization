import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from tabulate import tabulate

def scrape_player_data():
    url = "https://fbref.com/en/players/42fd9c7f/scout/365_m1/Kylian-Mbappe-Scouting-Report"

    # Use BeautifulSoup to parse the page source
    page_source = BeautifulSoup(requests.get(url).content, "html.parser")

    # Find the table with the id "scout_summary_FW"
    table = page_source.find("table", {"id": "scout_summary_FW"})

    if not table:
        print("Table with id 'scout_summary_FW' not found.")
        return None

    # Use pandas to read the HTML table into a DataFrame
    player_data_df = pd.read_html(str(table))[0]

    return player_data_df

def highlight_strengths_weaknesses(percentile):
    if percentile >= 50:
        return 'green'  # Use green for strengths (percentile >= 50)
    else:
        return 'red'  # Use red for weaknesses (percentile < 50)


if __name__ == "__main__":
    player_data = scrape_player_data()
    if player_data is not None:
        # Select the desired stats for the radar chart
        selected_stats = [
            "Non-Penalty Goals",
            "Non-Penalty xG",
            "Shots Total",
            "Assists",
            "xAG",
            "npxG + xAG",
            "Shot-Creating Actions",
            "Passes Attempted",
            "Pass Completion %",
            "Progressive Passes",
            "Progressive Carries",
            "Successful Take-Ons",
            "Touches (Att Pen)",
            "Progressive Passes Rec",
            "Tackles",
            "Interceptions",
            "Blocks",
            "Clearances",
            "Aerials won"
        ]

        # Filter the DataFrame to include only the selected stats
        selected_columns = player_data[player_data[("Standard Stats", "Statistic")].isin(selected_stats)]
        selected_columns = selected_columns.loc[:, [('Standard Stats', 'Statistic'), ('Standard Stats', 'Percentile')]]

        # Sort the DataFrame by the 'Percentile' column in descending order
        selected_columns_sorted = selected_columns.sort_values(by=('Standard Stats', 'Percentile'), ascending=False)

        # Create a Streamlit app
        st.title("Radar Chart for Kylian Mbappe's Standard Stats Percentiles")
        st.write("Data source: https://fbref.com")

        # Display the DataFrame
        st.subheader("Data:")
        st.write(selected_columns_sorted)

        # Prepare data for the radar chart
        data_for_radar = selected_columns_sorted.set_index(('Standard Stats', 'Statistic'))
        data_for_radar.columns = ['Percentile']

        # Limit the number of stats to 6-8 for a well-balanced radar chart
        num_stats_to_display = min(8, len(data_for_radar))
        data_for_radar = data_for_radar.head(num_stats_to_display)

        # Generate the radar chart
        fig = px.line_polar(data_for_radar, r='Percentile', theta=data_for_radar.index, line_close=True)

        # Set radar chart layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                ),
            ),
            showlegend=False,
            title="Kylian Mbappe's Standard Stats Percentiles",
        )

        # Add labels to the data points on the radar chart
        for i in range(num_stats_to_display):
            fig.add_trace(
                go.Scatterpolar(
                    r=[data_for_radar.iloc[i]['Percentile']],
                    theta=[data_for_radar.index[i]],
                    mode='markers+text',
                    text=[f"{data_for_radar.iloc[i]['Percentile']}%"],
                    textposition="top center",
                    marker=dict(size=10, color=highlight_strengths_weaknesses(data_for_radar.iloc[i]['Percentile'])),
                )
            )

        # Display the radar chart
        st.subheader("Radar Chart:")
        st.plotly_chart(fig)
