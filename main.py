import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from tabulate import tabulate

def scrape_player_data(player_url):
    # Use BeautifulSoup to parse the page source
    page_source = BeautifulSoup(requests.get(player_url).content, "html.parser")

   # Find the table with the id "scout_summary_FW" for forwards
    table_fw = page_source.find("table", {"id": "scout_summary_FW"})

    # Find the table with the id "scout_summary_AM" for attacking midfielders
    table_am = page_source.find("table", {"id": "scout_summary_AM"})
    
    # Find the table with the id "scout_summary_MF" for midfielders
    table_mf = page_source.find("table", {"id": "scout_summary_MF"})

    # Find the table for defenders
    table_dc = page_source.find("table", {"id": "scout_summary_CB"})

    table_fb = page_source.find("table",{"id": "scout_summary_FB"})

   

    if table_fw:
        position = "Forward"
        player_data_df = pd.read_html(str(table_fw))[0]
    elif table_am:
        position = "Attacking Midfielder"
        player_data_df = pd.read_html(str(table_am))[0]
    elif table_mf:
        position = "Midfielder"
        player_data_df = pd.read_html(str(table_mf))[0]
    elif table_dc:
        position = "Center Back"
        player_data_df = pd.read_html(str(table_dc))[0]
    elif table_fb:
        position = "Forward"
        player_data_df = pd.read_html(str(table_fb))[0]
    else:
        print("Tables with id not found for player:", player_url)
        return None, None

    return player_data_df, position

def get_selected_stats_for_position(position):
    if position == "Forward":
        return [
            "Non-Penalty Goals",
            "Non-Penalty xG",
            "Shots Total",
            "Assists",
            "xAG",
            "npxG + xAG",
            "Shot-Creating Actions",
        ]
    elif position == "Attacking Midfielder":
        return [
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
        ]
    elif position == "Midfielder":
        return [
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
        ]
    elif position == "Center Back":
        return [
            "Passes Attempted",
            "Progressive Passes",
            "Progressive Carries",
            "Tackles",
            "Interceptions",
            "Blocks",
            "Clearances",
            "Aerials won",
        ]
    else:
        return [] 

def highlight_strengths_weaknesses(percentile):
    if percentile >= 50:
        return 'green'  # Use green for strengths (percentile >= 50)
    else:
        return 'red'  # Use red for weaknesses (percentile < 50)
    
if __name__ == "__main__":
    # Create a Streamlit app
    st.title("Player Profiles")
    st.write("Data source: https://fbref.com")

    # Read the player_profiles.csv file
    player_profiles_df = pd.read_csv('player_profiles.csv')

    # Get the unique player names from the DataFrame
    player_names = player_profiles_df['Name'].unique()

    # Add dropdown menu to select the player from the player_profiles.csv
    selected_player = st.selectbox("Select Player", player_names)

    # Find the corresponding player URL from the DataFrame
    player_url = player_profiles_df.loc[player_profiles_df['Name'] == selected_player, 'Link'].iloc[0]

    # Add 'https://fbref.com' at the start of the URL if it is missing
    if not player_url.startswith('https://fbref.com'):
        player_url = 'https://fbref.com' + player_url

    # Debugging print statement to check the player_url
    print("Selected Player URL:", player_url)

    # Scrape player data and display radar charts
    if player_url:
        player_data, position = scrape_player_data(player_url)
        if player_data is not None:
            
            # Get the selected stats for the player's position
            selected_stats = get_selected_stats_for_position(position)
            
            print("player_data:", player_data)
            print(player_data.columns)

            # Filter the DataFrame to include only the selected stats
            selected_columns = player_data[player_data['Statistic'].isin(selected_stats)]
            selected_columns = selected_columns.loc[:, ['Statistic', 'Percentile']]

            # Sort the DataFrame by the 'Percentile' column in descending order
            selected_columns_sorted = selected_columns.sort_values(by='Percentile', ascending=False)

            # Prepare data for the radar chart
            data_for_radar = selected_columns_sorted.set_index('Statistic')
            data_for_radar.columns = ['Percentile']

            # Limit the number of stats to 10 
            num_stats_to_display = min(10, len(data_for_radar))
            data_for_radar = data_for_radar.head(num_stats_to_display)

            # Generate the radar chart
            fig = px.line_polar(data_for_radar, r='Percentile', theta=data_for_radar.index, line_close=True)

            # Set radar chart layout
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 104],
                        showticklabels=True,
                        tickfont=dict(color='black', size=10),
                    ),
                ),
                showlegend=False,
                title=f"{selected_player} Standard Stats Percentiles",
                width=800,
                height=600,
            )

            # Add labels to the data points on the radar chart
            for i in range(num_stats_to_display):
                fig.add_trace(
                    go.Scatterpolar(
                        r=[data_for_radar.iloc[i]['Percentile']],
                        theta=[data_for_radar.index[i]],
                        mode='markers+text',
                        fill='toself',  # Fill the area inside the chart up to the marker points
                        fillcolor=highlight_strengths_weaknesses(data_for_radar.iloc[i]['Percentile']),  # Use the color based on the percentile
                        text=[f"{data_for_radar.iloc[i]['Percentile']}%"],
                        textposition="middle center",
                        textfont=dict(size=10, color='darkblue'),
                        marker=dict(size=10, color=highlight_strengths_weaknesses(data_for_radar.iloc[i]['Percentile'])),
                    )
                )

            # Display the radar chart
            st.subheader(f"Radar Chart for {selected_player}:")
            st.plotly_chart(fig)