import json
import requests
import pandas as pd

from flask import Flask, request

app = Flask(__name__)


def to_numeric(df, columns):
    """ Casting columns to numeric """
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def parse_date(column):
    """ Data preparation """
    column = pd.to_datetime(column, format='%d/%m/%Y')
    return column.dt.date.astype(str)


def prepare_data(df):
    """ Data prep for covid data """
    df = df.drop('countryterritoryCode', axis=1)
    df = df.rename(columns={'dateRep': 'date', 'countriesAndTerritories': 'country',
                            'geoId': 'code', 'popData2018': 'population'})
    df['date'] = parse_date(df['date'])
    df.loc[df.country == 'Anguilla', 'population'] = 15094
    df.loc[df.country == 'Eritrea', 'population'] = 4475000
    df = to_numeric(df, ['day', 'month', 'year', 'cases', 'deaths', 'population'])
    df = df.sort_values(by=['country', 'date'])
    df['cases_cum'] = df.groupby(['country'])['cases'].cumsum()
    df['deaths_cum'] = df.groupby(['country'])['deaths'].cumsum()
    return df


def load_data(url):
    """ Imports data from url """
    response = requests.get(url)
    records = json.loads(response.text)['records']
    df = pd.DataFrame.from_dict(records)
    df = prepare_data(df)
    return df


@app.route('/covid', methods=['POST'])
def handle_request():
    """ Request handler """
    request_json = request.get_json(force=True)
    url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/json/'
    data = load_data(url=url)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
