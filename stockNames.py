from pymongo import MongoClient
import requests

# use own MongoDB base to make it work
client = MongoClient('mongodb://test:test@**********', 27017)
db = client.dbproject

response_data = requests.get("https://finnhub.io/api/v1/stock/symbol?exchange=US&token=bsijmhvrh5rd8hs1e35g")

stocks = response_data.json()
for stock in stocks:
    name = stock["description"]
    symbol = stock["symbol"]
    if name is not "":
        stock_name = {'name': name, 'symbol': symbol}
        db.stocks.insert_one(stock_name)
