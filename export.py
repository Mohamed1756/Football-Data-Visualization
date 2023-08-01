import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def getReports():
    # Fetch the HTML content from the URL
    url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats'
    response = requests.get(url)
    html = response.content

    # Write the HTML content to a file
    with open("data1.html", "wb") as file:
        file.write(html)

    # Open the html file and replace the comment part with void
    with open("data1.html", 'r') as html1:
        bs2 = BeautifulSoup(html1, 'html.parser')
        usable_bs2 = bs2.prettify().replace("<!--", "").replace("-->", "")
        with open("data2.html", 'w') as commentless_content:
            commentless_content.write(usable_bs2)

    # Create a DataFrame to store player names and links
    player_data = {
        "Name": [],
        "Link": []
    }
    
    # Scrape player names and links from the HTML
    with open('data2.html', 'r') as main_page:
        bs3 = BeautifulSoup(main_page, 'html.parser')
        list_of_links = bs3.find_all('a', href=re.compile(r"^/en/players/[a-f0-9]{8}/[A-Za-z-]+$"))
        for link in list_of_links:
            player_data["Name"].append(link.text)
            player_data["Link"].append(link.attrs['href'])

    # Create a DataFrame from the player_data dictionary
    df = pd.DataFrame(player_data)

    # Save the DataFrame to a CSV file
    df.to_csv('player_profiles.csv', index=False)

# Call the function to get player data and save to CSV
getReports()

# Since some player names have non-English letters, this code replaces them with corresponding English letters
def name_updater():
    df = pd.read_csv('player_profiles.csv')
    df['Name'] = df['Link'].str.split('/').str[-1].str.replace('-', ' ')
    df.to_csv('player_profiles.csv', index=False)

# Call the function to update player names
name_updater()
