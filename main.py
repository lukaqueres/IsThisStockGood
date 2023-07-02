"""
This is backend flask app for page

"""
import logging
import json
import asyncio

import flaskr.source as source

import flaskr.preview as preview

from datetime import date
from flask import Flask, request, render_template, send_file
import flask

logging.basicConfig(format='%(name)s - %(levelname)s : %(message)s')

logger = logging.getLogger("IsThisStockGood")

logger.level = logging.ERROR

app = Flask(__name__, static_folder='assets')


@app.route("/<ticker>/preview.jpg")
def symbol_preview(ticker: str = None):
	"""
	Generate jpg file with symbol preview for thumbnails.

	@param ticker: Ticker symbol
	@return: JPG image
	"""
	if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
		return flask.redirect(f"http://isthisstockgood.com/{ticker}/preview.jpg", code=302)
	
	ticker = ticker.upper()
	
	if source.check(ticker):
		data, code = source.ticker(ticker)
		if data["error"]:
			img = preview.error(ticker, code, data["error"])
		else:
			img = preview.ticker(ticker, data)
	else:
		img = preview.error(ticker, 400, "Invalid ticker",
		                    "Provided ticker is invalid. \nPlease check and correct, then try again.")
	return send_file(img, mimetype='image/jpeg')


@app.route("/<ticker>")
def company_page(ticker: str = None):
	"""
	Page with ticker loading

	@param ticker: Symbol
	@return: Page with loading data
	"""
	vals = {
		"ticker": ticker.upper(),
		"color_theme": flask.request.cookies.get('color-theme', None),
		"current_year": date.today().year,
	}
	return render_template('home.html', **vals)


@app.route("/")
def homepage():
	"""
	Main page without data

	@return: Main page
	"""
	if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
		return flask.redirect("http://isthisstockgood.com", code=302)
	
	vals = {
		"ticker": None,
		"color_theme": flask.request.cookies.get('color-theme', None),
		'current_year': date.today().year,
	}
	return render_template('home.html', **vals)


@app.route("/favourites")
def favourites():
	loop = asyncio.new_event_loop()
	favs: list = json.loads(flask.request.cookies.get('favourite-tickers', "[]"))
	result: dict[str, dict] = loop.run_until_complete(source.favourites(favs))
	
	loop.run_until_complete(asyncio.sleep(0))
	loop.close()
	return result


@app.route("/me/favourites")
def favourite():
	"""
	Page with favourite tickers and their details

	@return: Main page
	"""
	if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
		return flask.redirect("http://isthisstockgood.com/favourites", code=302)
	
	vals = {
		"color_theme": flask.request.cookies.get('color-theme', None),
		"favourite_tickers": json.loads(flask.request.cookies.get('favourite-tickers', "[]")),
		'current_year': date.today().year,
	}
	return render_template('favourites.html', **vals)


@app.route("/search/<ticker>")
def search(ticker: str):
	"""
	Return json with data acquired with ticker

	@param ticker: Symbol of company
	@return: Json data
	"""
	if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
		return flask.redirect(f"http://isthisstockgood.com/search/{ticker}", code=302)
	
	if not source.check(ticker):
		return {"error": "Invalid ticker"}, 400
	
	loop = asyncio.new_event_loop()
	ticker = ticker.upper()
	data, code = loop.run_until_complete(source.ticker(ticker))
	
	loop.run_until_complete(asyncio.sleep(0))
	loop.close()
	return data, code


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)
