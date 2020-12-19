#Web scrapping script for data mining of heavy equipment related data.
#Dec. 4 2020. Author: Gilson Frías

from bs4 import BeautifulSoup
import requests
from contextlib import closing

class scrapper:

    def __init__(self):
        self.urls = {"corotos":"https://www.corotos.com.do/k/",
                     "merclibre":"https://vehiculos.mercadolibre.com.do/"}
        self.corotos_descriptions = []
        self.corotos_currencies = []
        self.corotos_prices = []
        self.corotos_dates = []
        self.corotos_locations = []
        self.merclibre_descriptions = []
        self.merclibre_currencies = []
        self.merclibre_prices = []
        self.merclibre_locations = []
    
    def get_content(self, url):
        #Download HTML content from given url
        try:
            with closing(requests.get(url)) as page:
                if(page.status_code == 200):
                    return page
                else:
                    print("[INFO]::getContent page status code", page.status_code)
                    return None
        except:
            print("[Exception]::getContent page unreachable")
            return None

    def parse_corotos_listings(self, content):
        #Parse HTML content from one listing page at corotos.com.do. The listing page contains a grid of products.
        #TODO: Implement exception handling for 'find' method
        soup = BeautifulSoup(content, "html.parser")
        listing = soup.find("div", class_="listing")
        descriptions = []
        currencies = []
        prices = []
        dates = []
        locations = []
        urls = []
        if listing:
            #If there is a non empty listing, look for <span> and <h3> tags
            h3 = listing.find_all("h3")
            for header in h3:
                url = ""
                if header:
                    #Obtain href to product page
                    a = header.find("a")
                    if a:
                        url = ''.join([self.urls["corotos"][:-3], a["href"]])
                #Parse product page and obtain relevant data
                currency, price, description, date, location = self.parse_corotos_product(url)
                currencies.append(currency)
                prices.append(price)
                descriptions.append(description)
                dates.append(date)
                locations.append(location)
                urls.append(url)
        #Check if there is an additional listing page
        next_button = soup.find("div", class_="grid__cell grid__cell--medium-12of12")
        return ({"desc":descriptions, "pri":prices, "cur":currencies, "dat":dates, "loc":locations, "url":urls}, next_button)

    def parse_corotos_product(self, url):
        #Obtain the fetures for the product lsited in the given url
        content = self.get_content(url)
        price = ""
        currency = ""
        description = ""
        date = ""
        location = ""
        if content:
            soup = BeautifulSoup(content.content, "html.parser")
            price_header = soup.find("h2", class_="post__price")
            description_header = soup.find("h1", class_="post__title")
            date_p = soup.find("p", class_="post__date")
            location_ul = soup.find("ul", class_="post__category-and-location")
            if price_header:
                currency, price = price_header.text.split(" ")
            if description_header:
                description = description_header.text
            if date_p:
                date = date_p.text.split(": ")[1]
            if location_ul:
                location = location_ul.find("li").text.split(", ")[-1].replace("\n", "")
        return (currency, price, description, date, location)
        

    def scrap_corotos(self, inquiry, num_pages=10):
        #Parse all available pages for the given inquiry
        base_url = ''.join([self.urls["corotos"], inquiry])
        current_page = 1
        next_url = base_url
        while(True):
            content = self.get_content(next_url)
            if (content or current_page<num_pages):
                #If inquiry is successful, store scrapped data from all products featured
                print("[INFO] scrapping corotos.com.do listings page {}/{}".format(current_page, num_pages))
                features, next_ = self.parse_corotos_listings(content.content)
                self.corotos_descriptions.append(features["desc"])
                self.corotos_prices.append(features["pri"])
                self.corotos_currencies.append(features["cur"])
                self.corotos_dates.append(features["dat"])
                self.corotos_locations.append(features["loc"])
                print("[INFO] Number of products examined: {}\n".format(len(features["desc"])))
            else:
                break
            #Check for more listings if there was a positive response 
            if next_ and features["desc"]:
                current_page+=1
                next_url = ''.join([base_url, '?page={}'.format(current_page)])
            else:
                break

    def parse_merclib_listings(self, content):
        #Parse a single page of HTML content from mercadolibre.com.do
        #TODO: Implement exception handling for 'find' methods
        soup = BeautifulSoup(content, "html.parser")
        listings = soup.find_all("li", class_="ui-search-layout__item")
        descriptions = []
        prices = []
        currencies = []
        locations = []
        for item in listings:
            description = ""
            price = ""
            currency = ""
            location = ""
            description_header = item.find("h2")
            price_span = item.find("span", class_="price-tag-fraction")
            currency_span = item.find("span", class_="price-tag-symbol")
            location_span = item.find("span", class_="ui-search-item__group__element ui-search-item__location")
            #If tags exists, get the text they contain
            if description_header:
                description = description_header.text
            if price_span:
                price = price_span.text
            if currency_span:
                currency = currency_span.text
            if location_span:
                location = location_span.text
            descriptions.append(description)
            prices.append(price)
            currencies.append(currency)
            locations.append(location)
        return (descriptions, prices, currencies, locations)
    

    def scrap_merclib(self, inquiry, num_pages=10):
        #Parse all available pages for the given inquiry
        #TODO: enable parsing recursively by following link of next page
        base_url = ''.join([self.urls["merclibre"], inquiry])
        current_page = 1
        next_url = base_url
        content = self.get_content(next_url)
        print("[INFO] scrapping mercadolibre.com.do listings page {}/{}".format(current_page, num_pages))
        descriptions, prices, currencies, locations = self.parse_merclib_listings(content.content)
        print("[INFO] Number of products examined: {}\n".format(len(descriptions)))
        self.merclibre_descriptions = descriptions
        self.merclibre_prices = prices
        self.merclibre_currencies = currencies
        self.merclibre_locations = locations
     
    def get_models(self):
        #Retrieve all Caterpillar vehicle models from wikipedia.com
        content = self.get_content("https://en.wikipedia.org/wiki/List_of_Caterpillar_Inc._machines")
        models = []
        if content:
            soup = BeautifulSoup(content.content, "html.parser")
            models_table = soup.find("table", class_="multicol")
            models_li = models_table.find_all("li")
            for model in models_li:
                if "\n" not in model.text:
                    models.append(model.text)
        models = [model.split(" ")[1] for model in models]
        #Append additional models not found in the wikipedia list
        models = models + ["320DL", "216B", "320C", "420", "C11"]
        return models

    def get_exrate(self, currency="DOP"):
        #Consult the current exchange rate in reference to USD for the given currency
        response = self.get_content("https://api.exchangerate.host/latest?base=USD")
        if response:
            exrate = round(response.json()["rates"][currency], 2)
            date = response.json()["date"]
            return exrate, date


def main():
    scrap = scrapper()
    #Scrap webpages
    #scrap.scrap_corotos("caterpillar")
    #scrap.scrap_merclib("caterpillar")
    print(scrap.get_exrate())
    #scrap.get_models()
    #print(scrap.corotos_descriptions)
    #print(scrap.merclibre_descriptions)

if __name__ == "__main__":
    main()
