#!/usr/bin/env python
# coding: utf-8
# A web-scrapping and container class for data related to the sale of Caterpillar products
#TODO:
    #1.Implement DB logic to store relevant scrapped data
    #2.Migrate images_urls to a external file
    #3.Embed the generated offers map directly into the web app, avoid writting map.html

import numpy as np
import plotly.graph_objects as go
from scrapper import scrapper
import geopandas as gpd
import pandas as pd
import altair as alt
from altair import datum
from altair_saver import save

class CatDataHandler:
    
    def __init__(self):
        self.scrap = None
        self.exc_rate = 0.0
        self.todays_date = ''
        self.min_price = 10000
        self.max_price = 10000000
        self.map = None

        #Caterpillar models sprites
        self.images_urls = {
                '12G':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.EQF8pXV8yirn22-4sCo4zgHaEK%26pid%3DApi&f=1',
                '216B':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.b3oIzfBUzGag9JgtAZTt8wHaEK%26o%3D6%26pid%3DApi&f=1',
                '320C':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.kAzYXm-G5qVSlxn2p7gVpgHaEK%26pid%3DApi&f=1',
                '320DL':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%3Fid%3DOIP.GGYXPpcBW8ES0uzhfARsCgHaEK%26pid%3DApi&f=1',
                '416C':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.ytimg.com%2Fvi%2FwJX8FNPKABU%2Fmaxresdefault.jpg&f=1&nofb=1',
                '416E':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP._1Iwf4r8hazq78XP5ssXZwHaEK%26pid%3DApi&f=1',
                '420':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.FWnSD9JVIAZ6f2Q5NdPZqwHaEK%26o%3D6%26pid%3DApi&f=1',
                '420D':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.GDEipJ01DG0jVxu-JINPDAHaEK%26pid%3DApi&f=1',
                '420E':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.jkhLR0im4wnSFv41BYm0QgHaEK%26pid%3DApi&f=1',
                '420F':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.8tXl0ae8xsuO4089I_gHjQHaFj%26pid%3DApi&f=1',
                '950':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.KetPThLffiL9FIm4xLshfQHaEK%26pid%3DApi&f=1',
                '950B':'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse2.mm.bing.net%2Fth%3Fid%3DOIP.bOb-Z7zlK1aZygn6hQQwowEsDh%26pid%3DApi&f=1'
        }
        

        #Listing fields
        self.models = np.zeros((30,), dtype=np.dtype('<U8'))
        self.descriptions = np.zeros((30,), dtype=np.dtype('<U100'))
        self.prices = np.zeros((30,), dtype=np.dtype('float64'))
        self.currencies = np.zeros((30,), dtype=np.dtype('<U3'))
        self.locations = np.zeros((30,), dtype=np.dtype('<U35'))
        
        #Per model metrics
        self.unique_models = np.zeros((30,), dtype=np.dtype('<U8'))
        self.unique_models_counts = np.zeros((30,), dtype=np.dtype('int64'))
        self.avg_model_prices = np.zeros((30,), dtype=np.dtype('float64'))
        self.top_models = np.zeros((3, 2), dtype=np.dtype('<U8'))

        #Per province metrics
        self.unique_provs = np.zeros((30,), dtype=np.dtype('<U35'))
        self.unique_provs_counts = np.zeros((30,), dtype=np.dtype('int16'))
        
        #Overall metrics
        self.total_sale_price = 0
        self.total_listings = 0
        self.number_of_models = 0
        self.avg_price = 0
        self.unique_currencies = np.zeros((2,), dtype=np.dtype('<U3'))
        self.currencies_counts = np.zeros((2,), dtype=np.dtype('int64'))
        
        #Plotly font settings
        self.font_settings = font=dict(
            family="Courier New, monospace",
            size=14,
            #color="RebeccaPurple"
        )
            
        
                
    def flatten_list(self, unflatten):
        #Reduce a multi-dimensional list into a one dim. (flatten) list
        flatten = []
        for element in unflatten:
            if type(element) is list:
                for item in element:
                    flatten.append(item)
            else:
                flatten.append(element)
        return flatten

    def clean_names(self, str_):
        #Eliminate accents form str_
        if 'á' in str_:
            str_ = str_.replace('á', 'a')
        if 'é' in str_:
            str_ = str_.replace('é', 'e')
        if 'í' in str_:
            str_ = str_.replace('í', 'i')
        if 'ó' in str_:
            str_ = str_.replace('ó', 'o')
        if 'ú' in str_:
            str_ = str_.replace('ú', 'u')
        if 'ñ' in str_:
            str_ = str_.replace('ñ', 'n')
        if str_ == 'Montecristi':
            str_ = 'Monte Cristi'
        return str_
    
    def scrap_pages(self, inquiry='caterpillar'):
        #Scrap sale listings 
        self.scrap = scrapper()
        self.scrap.scrap_corotos(inquiry)
        self.scrap.scrap_merclib(inquiry)
        
    def prepare_data(self):
        #Scrap for sale listings
        if self.scrap == None:
            self.scrap_pages()
        #If parsing the listings was successfull, proceed to clean data and calculate metrics
        if self.scrap.corotos_descriptions and self.scrap.merclibre_descriptions:
            #Flatten and concatenate feature lists
            descriptions = self.flatten_list(self.scrap.corotos_descriptions) +                        self.flatten_list(self.scrap.merclibre_descriptions)
            prices = self.flatten_list(self.scrap.corotos_prices) +                        self.flatten_list(self.scrap.merclibre_prices)
            currencies = self.flatten_list(self.scrap.corotos_currencies) +                        self.flatten_list(self.scrap.merclibre_currencies)
            locations = self.flatten_list(self.scrap.corotos_locations) +                        self.flatten_list(self.scrap.merclibre_locations)
            #Get rid of accents
            locations = [self.clean_names(str_) for str_ in locations]
            dates = self.flatten_list(self.scrap.corotos_dates)
            
            #Get today's DOP->USD exchange rate
            exc_rate, today_date = self.scrap.get_exrate()
            self.exc_rate = float(exc_rate)
            self.today_date = today_date

            #Convert prices from USD to DOP
            prices = [int(price.replace(",", "")) for price in prices] #xx,xxx,xxx -> xxxxxxxx
            
            prices_dop = []
            for currency, price in zip(currencies, prices):
                if "U" in currency:
                    prices_dop.append(price*exc_rate)
                else:
                    prices_dop.append(price)
                    
            #Clean up listings post date strings
            dates = [date.split(" de ") for date in dates]
            
            #Convert to numpy arrays
            descriptions = np.array(descriptions)
            prices = np.array(prices_dop)
            currencies = np.array(currencies)
            locations = np.array(locations)
            dates = np.array(dates)
            
            #Filter out listings that are not related to the inquiry term
            descriptions_low = [str_.lower() for str_ in descriptions]
            #queries = inquiry.split(' ')
            queries = ["caterpillar", "caterpilar", "cat", "cater"]
            mask = []
            for entry in descriptions_low:
                words = entry.split(" ")
                flag = False
                for word in words:
                    if word in queries:
                        flag = True
                        break
                mask.append(flag)
            mask = np.array(mask)
            
            #Filter out equipments with a price below the minimum threshold
            indx = np.logical_and(prices>self.min_price, prices<self.max_price)
            mask = np.logical_and(mask, indx)

            descriptions = descriptions[mask]
            prices = prices[mask]
            currencies = currencies[mask]
            locations = locations[mask]
            #TODO: obtain and filter the mercadolibre.com.do dates
            dates = dates[mask[:dates.shape[0]]]
            
            #Look for models
            
            #Get list of Caterpillar models from wikipedia
            models_list = self.scrap.get_models()
            #Look for the vehicle model in each sale post description
            models = np.array([self.find_model(des, models_list) for des in descriptions])
            
            #Filter out entries without defined model
            mask = models != ""
            self.models = models[mask]
            self.descriptions = descriptions[mask]
            self.prices = prices[mask]
            self.currencies = currencies[mask]
            self.locations = locations[mask]

            #Compute number of sales per province
            self.unique_provs, self.unique_provs_counts = np.unique(self.locations, return_counts=True)
            
            #Identify how many unique models are listed
            unique_models, counts = np.unique(self.models, return_counts=True)
            
            #Compute mean price for each model
            avg_prices = np.zeros(counts.shape)
            for model, n in zip(unique_models, range(unique_models.size)):
                mask = self.models == model
                avg_prices[n] = self.prices[mask].mean()
                
            self.unique_models = unique_models
            self.unique_models_counts = counts
            self.avg_model_prices = avg_prices
                
            #Compute top 3 most offered models
            max_counts = self.get_n_max(counts)
            top_models = []
            for count in max_counts:
                mask = counts == count
                model = unique_models[mask][0]
                price = int(avg_prices[mask][0])
                top_models.append((model, price))
                
            self.top_models = np.array(top_models)

            #Compute sale metrics
            self.total_sale_price = int(self.prices.sum())
            self.total_listings = self.prices.size
            self.numger_of_models = unique_models.size
            self.avg_price = int(self.prices.mean())
            
            #Compute distribution of currencies
            c = []
            for currency in currencies:
                if "U" in currency:
                    c.append("USD")
                else:
                    c.append("DOP")

            self.unique_currencies, self.currencies_counts = np.unique(c, return_counts=True)
            
    
            
    def is_in_database(self, model, models_list):
        #Check if a given model string matches a string within the modesl list
        is_in_catalog = False
        for ref_model in models_list:
            if (model in ref_model) or (model[:-1] == ref_model):
                is_in_catalog = True
        return is_in_catalog
    
    def get_n_max(self, lst, n=3):
        #Compute the n greater numbers in a list
        max_counts = [lst.max()]
        lst_cp = lst.copy()
        for _ in range(n-1):
            lst_cp = lst_cp[lst_cp != lst_cp.max()]
            if lst_cp.size:
                max_counts.append(lst_cp.max())
            else:
                break
        return max_counts

    def find_model(self, str_, models_list):
        #Find a potential Caterpillar model within a given string considering the models_list from wikipedia 
        digits = list(range(10))
        digits = [str(digit) for digit in digits]
        years = list(range(1990, 2021))
        years = [str(year) for year in years]
        min_digits = 2
        #get rid of new line chars
        str_ = str_.replace("\n", " ")
        #Convert to uppercase
        str_ = str_.upper()
        str_ = str_.split(" ")
        for word in str_:
            #Discard price tags
            if "$" in word:
                continue
            #Get rid off forbidden characters
            for ch in [".", ",", "#", "?", "!", "/"]:
                word = word.replace(ch, "")
            #Check for CB-XXX and CS-XXX models
            if "-" in word:
                words = word.split("-")
                if words[0] not in ["CB", "CS"]:
                    word = words[0]
            #Count how many digits are in word
            digits_count = 0
            for ch in word:
                if ch in digits:
                    digits_count+=1
            #Return first candidate word that suffices the model criteria
            if (digits_count>=min_digits) & (word not in years):
                if self.is_in_database(word, models_list):
                    return word
        return ""
    
    def shortenNames(self, string):
        #Get rid of the term 'Provincia' in a string defining a location 
        if 'Provincia' in string.split():
            return " ".join(string.split()[1:])
        else:
            return string
    
    def draw_map(self, shapefile_path="web_scrap/geo_data/dom_admbnda_adm2_2020.shp"):
        #Load geographich coordinates and draw altair choropleth
        
        #DR geographic shapefile source: https://data.humdata.org/dataset/dominican-republic-administrative-boundaries-levels-0-6 
        gdf = gpd.read_file(shapefile_path)
        #Shroten the name of provinces in gdf
        gdf['Province']=gdf['ADM2_REF'].map(self.shortenNames)
        
        #Change Coodinate Reference System to EPSG: 4326, otherwise altair would not plot it 
        #correctly https://altair-viz.github.io/user_guide/data.html#projections
        gdf = gdf.loc[:, ['geometry', 'Province']].to_crs("EPSG:4326")
        #df = pd.DataFrame({'Price':self.prices, 'Province':self.locations})
        
        #Compute data per province
        prices_prov = []
        listings_prov = []
        for province in gdf["Province"].tolist():
            mask = self.locations == province 
            listings_prov.append(int(mask.sum()))
            prices_prov.append(int(self.prices[mask].sum()))
            
        df = pd.DataFrame({'Listings':listings_prov, 'Price':prices_prov, 
                           'Province':gdf['Province'].tolist()})
        
        
        #Plot volumen ofertado por provincia
        map_color =  alt.Color('Price:Q', scale=alt.Scale(scheme='viridis', domain=[1, round(df['Price'].max()+1000)]),
                      legend=alt.Legend(title='Escala volumenes de venta (DOP)', labelFont='Courier New, monospace', 
                                        labelFontSize=14, titleOrient='right', tickCount=5))

        tt = [alt.Tooltip(field='Province', type='nominal'),
              alt.Tooltip(field='Price', type='quantitative', format='.2f')]

        map_ = alt.Chart(gdf).mark_geoshape(
            stroke='#666666',#'#b15928',
            strokeWidth=0.5
        ).encode(
            color=alt.condition(datum['Price'] > 0, map_color, alt.value('lightgray')),
            tooltip=tt#['Province:N', 'total USD/m2:Q']
        ).transform_lookup(
            lookup='Province',
            from_=alt.LookupData(df, 'Province', ['Price'])
        ).properties(
            projection={'type':'mercator'},
            width=450,
            height=300,
            title='Distribución volumenes de venta en el territorio nacional'
        )

        map_.configure_title(
                fontSize=34,
                #fontStyle='italic'
        )
        
        self.map = map_
        
        #Save map to HTML file
        save(map_, 'map.html')
