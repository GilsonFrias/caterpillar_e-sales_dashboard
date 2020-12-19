#Dashboard webapp entry point script.
#Dec. 8 2020, Gilson Frías
from flask import Flask
import os
import sys
from .dash.dashboard import init_dashboard

#path = os.path.dirname(os.path.abspath(__file__))
#sys.path.insert(0, os.path.join(path, '../web_scrap'))

#from caterpillar import CatDataHandler

def init_app():
    #Instantiate and configure flask app
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    
    with app.app_context():
        #Instantiate web-scrapping and data cleaning object
        #cat_data = CatDataHandler()
        
        #Import app components
        from . import routes

        #Import dashboard into current app
        app = init_dashboard(app)

        return app
