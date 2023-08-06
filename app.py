from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display

app = Flask(__name__)
# MongoClient no longer accessible
# unfortunately this means that the code will not run correctly from scratch
# replace with own client for this base code to work
client = MongoClient('mongodb://test:test@**********', 27017)
db = client.dbproject


@app.route('/')
def main_page():
    return render_template('Main_Page.html')


@app.route('/info', methods=['GET'])
def info_page():
    return render_template('info.html')


@app.route('/contact', methods=['GET'])
def contact_page():
    return render_template('contact.html')


@app.route('/stockNames', methods=['GET'])
def get_names():
    symbol_receive = request.args.get('symbol')
    result = db.stocks.find_one({"symbol": symbol_receive}, {'_id': 0, 'symbol': 0})

    return jsonify({'result': 'success', 'stocks': result})


@app.route('/financials', methods=['GET'])
def get_financials():
    symbol_receive = request.args.get('symbol')

    if db.financialInfo.find_one({"symbol": symbol_receive}) is None:
        name_result = db.stocks.find_one({"symbol": symbol_receive}, {'_id': 0, 'symbol': 0})
        name_upper = name_result['name']
        name_lower = name_upper.lower()

        options = Options()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        display = Display(visible=0,size=(1024,768))
        display.start()
        driver = webdriver.Chrome('/home/ubuntu/myproject/cdrive/chromedriver', options=options)
        driver.implicitly_wait(3)
        driver.get(
            'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/income-statement?freq=A')

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        revenue_list = []
        date_list = []
        gross_profit_list = []
        opr_income_list = []
        net_income_list = []
        research_list = []
        eps_list = []

        revenues = soup.select('#row0jqxgrid > div')
        dates = soup.select('#columntablejqxgrid > div')
        gross_profits = soup.select('#row2jqxgrid > div')
        operating_incomes = soup.select('#row7jqxgrid > div')
        net_incomes = soup.select('#row15jqxgrid > div')
        research_expenses = soup.select('#row3jqxgrid > div')
        earnings_per_share = soup.select('#row21jqxgrid > div')

        for revenue in revenues[2:7]:
            value = revenue.select_one('div').text
            revenue_list.append(value)
        for date in dates[2:7]:
            day = date.select_one('div > div > span').text
            year = day[0:4]
            date_list.append(year)
        for profit in gross_profits[2:7]:
            value = profit.select_one('div').text
            gross_profit_list.append(value)
        for income in operating_incomes[2:7]:
            value = income.select_one('div').text
            opr_income_list.append(value)
        for income in net_incomes[2:7]:
            value = income.select_one('div').text
            net_income_list.append(value)
        for expense in research_expenses[2:7]:
            value = expense.select_one('div').text
            research_list.append(value)
        for earnings in earnings_per_share[2:7]:
            value = earnings.select_one('div').text
            eps_list.append(value)

        driver.get(
            'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/financial-ratios?freq=A')

        soup1 = BeautifulSoup(driver.page_source, 'html.parser')

        roe_list = []
        roa_list = []
        roi_list = []

        roes = soup1.select('#row13jqxgrid > div')
        roas = soup1.select('#row15jqxgrid > div')
        rois = soup1.select('#row16jqxgrid > div')

        for roe in roes[2:7]:
            value = roe.select_one('div').text
            roe_list.append(value)
        for roa in roas[2:7]:
            value = roa.select_one('div').text
            roa_list.append(value)
        for roi in rois[2:7]:
            value = roi.select_one('div').text
            roi_list.append(value)

        entry = {'symbol': symbol_receive,
                 'date': date_list,
                 'revenue': revenue_list,
                 'R&D': research_list,
                 'grossProfit': gross_profit_list,
                 'operatingIncome': opr_income_list,
                 'netIncome': net_income_list,
                 'EPS': eps_list,
                 'ROE': roe_list,
                 'ROA': roa_list,
                 'ROI': roi_list}

        db.financialInfo.insert_one(entry)
        result1 = db.financialInfo.find_one({"symbol": symbol_receive}, {'_id': 0})
        return jsonify({'result': 'success', 'financialInfo': result1})

    else:
        result = db.financialInfo.find_one({"symbol": symbol_receive}, {'_id': 0})
        return jsonify({'result': 'success', 'financialInfo': result})


@app.route('/valuation', methods=['GET'])
def get_valuation():
    symbol_receive = request.args.get('symbol')
    name_result = db.stocks.find_one({"symbol": symbol_receive}, {'_id': 0, 'symbol': 0})
    name_upper = name_result['name']
    name_lower = name_upper.lower()

    options = Options()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Chrome('/home/ubuntu/myproject/cdrive/chromedriver', options=options)
    driver.implicitly_wait(3)
    driver.get(
        'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/pe-ratio')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pe_ratio = soup.select_one('#style-1 > table > tbody > tr:nth-child(1) > td:nth-child(4)').text

    driver.get(
        'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/price-sales')
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
    ps_ratio = soup1.select_one('#style-1 > table > tbody > tr:nth-child(1) > td:nth-child(4)').text

    driver.get(
        'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/price-book')
    soup2 = BeautifulSoup(driver.page_source, 'html.parser')
    pb_ratio = soup2.select_one('#style-1 > table > tbody > tr:nth-child(1) > td:nth-child(4)').text

    driver.get(
        'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/price-fcf')
    soup3 = BeautifulSoup(driver.page_source, 'html.parser')
    pfcf_ratio = soup3.select_one('#style-1 > table > tbody > tr:nth-child(1) > td:nth-child(4)').text

    result = {'pe_ratio': pe_ratio,
              'ps_ratio': ps_ratio,
              'pb_ratio': pb_ratio,
              'pfcf_ratio': pfcf_ratio}

    return jsonify({'result': 'success', 'valuationInfo': result})


@app.route('/balance', methods=['GET'])
def get_balance():
    symbol_receive = request.args.get('symbol')
    name_result = db.stocks.find_one({"symbol": symbol_receive}, {'_id': 0, 'symbol': 0})
    name_upper = name_result['name']
    name_lower = name_upper.lower()

    options = Options()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Chrome('/home/ubuntu/myproject/cdrive/chromedriver',options=options)
    driver.implicitly_wait(3)
    driver.get(
        'https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/financial-ratios?freq=Q')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_ratio = soup.select_one('#row0jqxgrid > div:nth-child(3) > div').text
    debt_equity_ratio = soup.select_one('#row2jqxgrid > div:nth-child(3) > div').text

    driver.get('https://www.macrotrends.net/stocks/charts/' + symbol_receive + '/' + name_lower + '/balance-sheet?freq=Q')
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
    tot_assets = soup1.select_one('#row11jqxgrid > div:nth-child(3) > div').text
    tot_debt = soup1.select_one('#row16jqxgrid > div:nth-child(3) > div').text

    result= {'currentRatio': current_ratio,
             'debtEquityRatio': debt_equity_ratio,
             'assets': tot_assets,
             'debt': tot_debt}

    return jsonify({'result': 'success', 'balanceInfo': result})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
