import requests, json
from bs4 import BeautifulSoup
from advanced_expiry_caching import Cache
import csv

# Constants
START_URL = "https://www.nps.gov/index.htm"
FILENAME = "sample_secondprog_cache.json"

# Uses one instance of the Cache, even though data will be obtained from multiple places
PROGRAM_CACHE = Cache(FILENAME)

# Tool to build functionality
def access_page_data(url):
    data = PROGRAM_CACHE.get(url)
    if not data:
        data = requests.get(url).text
        # Default here with the Cache.set tool is that it will expire in 7 days, which is probably fine but something to explore
        PROGRAM_CACHE.set(url, data)
    return data

# Accessing main page
main_page = access_page_data(START_URL)

# Find <ul> with class 'SearchBar-keywordSearch' and obtain links at each list item
main_soup = BeautifulSoup(main_page, features="html.parser")
list_of_states = main_soup.find('ul', {'class': 'SearchBar-keywordSearch'})
# print(list_of_states)

# For each item in unordered list, capture and CACHE
all_links = list_of_states.find_all('a')
# print(all_links)

# Obtain all the data in the BeautifulSoup objects to work with...
states_pages = []
full_link = ''
for link in all_links:
    full_link = 'https://www.nps.gov' + link['href']
    page_data = access_page_data(full_link)
    soup_of_page = BeautifulSoup(page_data, features="html.parser")
    states_pages.append(soup_of_page)

# Get the information from each page
all_parks = []
parks_data = []
for page in states_pages:
    # Get state name
    state = page.find('h1', {'class': 'page-title'}).text

    # Get list of parks
    list_of_parks = page.find_all('ul', {'id': 'list_parks'})
    for park in list_of_parks:
        name = park.find('h3').text
        s_type = park.find('h2').text
        descr = park.find('p').text.strip('\n')
        loc = park.find('h4').text

        parks_data.append( [name, s_type, descr, loc, state] )

print(parks_data)

# Write parks data to csv file
f = open('parks_data.csv', 'w')

with f:
    writer = csv.writer(f)
    writer.writerows(parks_data)
