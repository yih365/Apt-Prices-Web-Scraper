from bs4 import BeautifulSoup
import requests

sites_dict = []

sites_dict['apartments_LA'] = "https://www.apartments.com/los-angeles-ca/"
sites_dict['zillow_LA'] = "https://www.zillow.com/los-angeles-ca/apartments/"
sites_dict['craigslist_LA'] = "https://losangeles.craigslist.org/search/apa#search=1~gallery~0~0"

for url in sites_dict.values():
    request = requests.get(url).text
    doc = BeautifulSoup(request, "html.parser")


