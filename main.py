import json
import requests

from scraper import ECDCScaper, WikiScraper
from bs4 import BeautifulSoup
from flask import Flask, request

# Flask
app = Flask(__name__)

# Scraper
ecdc = ECDCScaper()
wiki = WikiScraper()


@app.route('/covid', methods=['GET', 'POST'])
def handle_request():
    """ Request handler """
    url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/json/'
    request_json = request.get_json(force=True)
    data = ecdc.load_data(url=url)
    if 'type' in request_json:
        type = request_json['type']
    else:
        type = 'list'
    if 'country' in request_json:
        country = request_json['country']
        if country == 'All':
            payload = data.to_dict(type)
        else:
            payload = data[data.country == country].to_dict(type)
        code = 200
    elif 'code' in request_json:
        code = request_json['code']
        if code == 'ALL':
            payload = data.to_dict(type)
        else:
            payload = data[data.code == code].to_dict(type)
        code = 200
    else:
        payload = {'Error: please provide "country" or "code" in your payload.'}
        code = 400
    return json.dumps(payload), code


@app.route('/covid/de', methods=['GET', 'POST'])
def handle_request_de():
    """ Request handler """
    url = "https://de.wikipedia.org/wiki/COVID-19-Pandemie_in_Deutschland"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # Extract data from website
    table_header = wiki.extract_header(soup)
    table_cases = wiki.extract_cases(soup)
    table_deaths = wiki.extract_deaths(soup)

    # Get data
    names = wiki.get_names(table_header)
    cases = wiki.get_data(table_cases, names)
    deaths = wiki.get_data(table_deaths, names)

    # Data prep
    df_cases = wiki.prepare_data(cases, variable='cases')
    df_deaths = wiki.prepare_data(deaths, variable='deaths')
    df_payload = wiki.join_data(df_cases, df_deaths)

    # Payload
    payload = df_payload.to_dict('list')
    return json.dumps(payload), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
