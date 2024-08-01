import cherrypy
import requests
from sqlalchemy import create_engine, Column, String, Table, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

API_KEY = 'd305f696b732533afc6f35141356e19b'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/forecast'

# Set up the database
engine = create_engine('sqlite:///favorites.db')
metadata = MetaData()
favorites = Table('favorites', metadata,
                  Column('city', String, primary_key=True))
metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class WeatherApp:
    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def weather(self, city):
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {'error': 'City not found'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def forecast(self, city):
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(FORECAST_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            forecast_data = []
            current_date = datetime.now()
            for item in data['list']:
                item_date = datetime.fromtimestamp(item['dt'])
                if item_date.date() >= current_date.date() and item_date.date() <= (current_date + timedelta(days=7)).date():
                    forecast_data.append(item)
            return forecast_data
        else:
            return {'error': 'City not found'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def save_favorite(self, city):
        session.add(favorites.insert().values(city=city))
        session.commit()
        return {'message': 'City saved to favorites'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_favorites(self):
        result = session.query(favorites).all()
        favorites_list = [row.city for row in result]
        return favorites_list

if __name__ == '__main__':
    cherrypy.quickstart(WeatherApp(), '/')
