import sys 
sys.path.append('scrapy/')

from flask import Flask
from flask import render_template
from pymongo import MongoClient
from movie import get_movie
from cinema import get_cinema
from ticket import get_ticket
import datetime

db = MongoClient('localhost', 27017).test_database
app = Flask(__name__)

@app.route('/')
def index(names=None):
	names = list(db.table_movie.find())
	return render_template('index.html',names=names)

@app.route("/cinemas/movieID=<taobaoID>")
def cinema(taobaoID):
	movie = db.table_movie.find_one({'taobaoID':taobaoID})
	cinemas =list(db.table_cinema.find())
	return render_template('cinemas.html',cinemas = list(cinemas),movie = movie)

@app.route("/prices/movieID=<movieID>&cinemaID=<cinemaID>")
def price(movieID,cinemaID):
	tickets = get_ticket(db,movieID,cinemaID)
	tickets.sort(key=lambda x:x['Date'])
	movie = db.table_movie.find_one({'taobaoID':movieID})['name']
	cinema = db.table_cinema.find_one({'taobaoID':cinemaID})['name']
	for ticket in tickets:
		ticket['Date'] = ticket['Date'].strftime('%m-%d %H:%M')
	return render_template('prices.html',tickets =tickets ,movie = movie,cinema = cinema)

if __name__ == '__main__':
	movies = get_movie(db)
	cinemas= get_cinema(db)
	app.run()