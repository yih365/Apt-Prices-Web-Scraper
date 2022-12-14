from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import re


def main():
    sites_dict = {}

    sites_dict['apartments_LA'] = "https://www.apartments.com/los-angeles-ca/"
    sites_dict['zillow_LA'] = "https://www.zillow.com/los-angeles-ca/apartments/"
    sites_dict['craigslist_LA'] = "https://losangeles.craigslist.org/search/apa#search=1~gallery~0~0"

    driver = webdriver.Chrome('C:/chromedriver.exe')

    listings = {}

    craigslist(driver, sites_dict['craigslist_LA'], listings)
    # apartments(driver, sites_dict['apartments_LA'], listings)
    # zillow(driver, sites_dict['zillow_LA'], listings)

    # TODO: sort listings
    sorted_listings = listings.values()
    # Print listings
    for listing in sorted_listings:
        print(listing['price'])
        print(listing['address'])
        print(listing['details'])
        print(listing['link'])
        print()


def zillow(driver, url, listings):
    driver.get(url)
    html = driver.page_source

    doc = BeautifulSoup(html, "html.parser")

    divs = doc.find_all(class_ = "ListItem-c11n-8-73-8__sc-10e22w8-0 srp__hpnp3q-0 enEXBq with_constellation")
    for div in divs:
        # Save info for every listing
        price_res = div.find(attrs={"data-test" : "property-card-price"})
        address_res = div.find(attrs={"data-test" : "property-card-addr"})

        if address_res is None or price_res is None:
            continue

        # Look for link
        link_res = div.find(attrs={"data-test" : "property-card-link"})

        # Look for additional details about number of bedroom/bathroom
        details_res = div.find(attrs={"class" : "StyledPropertyCardHomeDetails-c11n-8-73-8__sc-1mlc4v9-0 jlVIIO"})
        details = ''
        if details_res is not None:
            details = details_res.text

        # replace '/b' in link with 'https://www.zillow.com/homedetails'
        link = link_res['href']
        if link[0:2] == '/b':
            link = 'https://www.zillow.com/homedetails' + link[2:]

        # Save text representation of the html results
        listings[div] = {'price': price_res.text, 'address': address_res.text, 'details': details, 'link': link}
        # TODO: have price as an int


def apartments(driver, url, listings):
    driver.get(url)
    html = driver.page_source

    doc = BeautifulSoup(html, "html.parser")
    print(doc)


def craigslist(driver, url, listings):
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    doc = BeautifulSoup(html, "html.parser")

    divs = doc.find_all(class_ = "cl-result-info gallery-layout")
    for div in divs:
        title_res = div.find(class_ = "titlestring")
        price_res = div.find(class_ = "priceinfo")
        print(title_res, price_res)
        if title_res is None or price_res is None:
            continue

        meta_res = div.find(class_ = "meta")
        location = ''
        if meta_res is not None:
            location = meta_res.text

        link = title_res['href']
        listings[div] = {'price': price_res.text, 'address': location, 'details': title_res.text, 'link': link}


if __name__ == '__main__':
    main()
