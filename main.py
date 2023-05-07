import logging
from datetime import date
from flask import Flask, request, render_template
from src.DataFetcher import fetchDataForTickerSymbol

logger = logging.getLogger("IsThisStockGood")

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)

h_format = logging.Formatter('%(name)s - %(levelname)s : %(message)s')
handler.setFormatter(h_format)

logger.addHandler(handler)

app = Flask(__name__)


@app.route('/')
def homepage():
  if request.environ['HTTP_HOST'].endswith('.appspot.com'):  #Redirect the appspot url to the custom url
    return '<meta http-equiv="refresh" content="0; url=https://isthisstockgood.com" />'

  template_values = {
    'page_title' : "Is This Stock Good?",
    'current_year' : date.today().year,
  }
  return render_template('home.html', **template_values)


@app.route('/search', methods=['POST'])
def search():
  if request.environ['HTTP_HOST'].endswith('.appspot.com'):  #Redirect the appspot url to the custom url
    return '<meta http-equiv="refresh" content="0; url=http://isthisstockgood.com" />'

  ticker = request.values.get('ticker')
  template_values = fetchDataForTickerSymbol(ticker)
  if not template_values:
    return render_template('json/error.json', **{'error' : 'Invalid ticker symbol'})
  return render_template('json/stock_data.json', **template_values)


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
