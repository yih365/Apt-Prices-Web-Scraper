from bs4 import BeautifulSoup
from selenium import webdriver
import matplotlib.pyplot as plt
import csv
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
    # TODO: apartments(driver, sites_dict['apartments_LA'], listings)
    zillow(driver, sites_dict['zillow_LA'], listings)

    # sort listings
    sorted_listings = sorted(listings.items(), key=lambda x: x[1]['price_number'])

    print_prompt = input("Would you like to print the results? (y/n) ")
    if print_prompt == 'y':
        # Print listings
        for listing in sorted_listings:
            listing = listing[1]
            print(listing['price'])
            print(listing['address'])
            print(listing['details'])
            print(listing['link'])
            print()

    path = input("Full path of csv file: ")
    csv_write(path, sorted_listings)
    csv_display(path)


def csv_write(path, listings):
    with open(path, 'w') as f:
        fieldnames = ['price_number', 'price', 'address', 'details', 'link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for listing in listings:
            try:
                writer.writerow(listing[1])
            except:
                # Users may have used unencodable characters as descriptions (such as some emojis)
                listing[1]['details'] = ''
                writer.writerow(listing[1])


def csv_display(path):
    with open(path, 'r') as file:
        reader = csv.DictReader(file, delimiter=',')

        sites = []
        prices = []
        reader = list(reader)
        for row in reader:
            if row['link'].find('zillow') != -1:
                sites.append('Zillow')               
            elif row['link'].find('craigslist') != -1:
                sites.append('Craigslist')
            else:
                raise Exception('Appears non-valid link.')
            prices.append(int(row['price_number']))

        plt.scatter(sites, prices, color='r', s=100)
        plt.xlabel('Site')
        plt.ylabel('Price')
        plt.show()


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
        listings[div] = {'price_number': price_to_int(price_res.text), 'price': price_res.text, 'address': address_res.text, 'details': details, 'link': link}


def apartments(driver, url, listings):
    # TODO:
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
        if title_res is None or price_res is None:
            continue

        meta_res = div.find(class_ = "meta")
        location = ''
        if meta_res is not None:
            location = meta_res.text

        link = title_res['href']
        listings[div] = {'price_number': price_to_int(price_res.text), 'price': price_res.text, 'address': location, 'details': title_res.text, 'link': link}


PRICE_REGEX = re.compile(r"\$\d+(,\d+)?")
def price_to_int(price_text):
    # Price to int using regex
    price = PRICE_REGEX.search(price_text).group(0).split(',')

    if len(price) == 1:
        # There was no comma
        return int(price[0][1:])

    price = price[0][1:] + price[1]
    return int(price)


if __name__ == '__main__':
    main()
