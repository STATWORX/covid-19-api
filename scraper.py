import requests
import re
import pandas as pd
import numpy as np
from string import ascii_lowercase


class ECDCScaper:
    """ Scraper für ECDC data """
    def __init__(self):
        pass

    def to_numeric(self, df, columns):
        """ Casting columns to numeric """
        for col in columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    def parse_date(self, column):
        """ Data preparation """
        column = pd.to_datetime(column, format='%d/%m/%Y')
        return column.dt.date.astype(str)

    def prepare_data(self, df):
        """ Data prep for covid data """
        df = df.drop('countryterritoryCode', axis=1)
        df = df.rename(columns={'dateRep': 'date', 'countriesAndTerritories': 'country',
                                'geoId': 'code', 'popData2019': 'population', 'continentExp': 'continent'})
        df['date'] = self.parse_date(df['date'])
        df.loc[df.code == 'AI', 'population'] = 15094
        df.loc[df.code == 'ER', 'population'] = 4475000
        df.loc[df.code == 'FK', 'population'] = 2840
        df.loc[df.code == 'BQ', 'population'] = 25157
        df.loc[df.code == 'BLM', 'population'] = 9131
        df.loc[df.code == 'CZ', 'population'] = 10650000
        df.loc[df.code == 'SH', 'population'] = 5633
        df.loc[df.code == 'EH', 'population'] = 500000
        df.loc[df.code == 'JPG11668', 'population'] = 0
        df = self.to_numeric(df, ['day', 'month', 'year', 'cases', 'deaths', 'population'])
        df = df.sort_values(by=['country', 'date'])
        df['cases_cum'] = df.groupby(['country'])['cases'].cumsum()
        df['deaths_cum'] = df.groupby(['country'])['deaths'].cumsum()
        return df

    def load_data(self, url):
        """ Imports data from url """
        response = requests.get(url)
        records = response.json()['records']
        df = pd.DataFrame.from_dict(records)
        df = self.prepare_data(df)
        return df


class WikiScraper:
    """ Scraper for wikipedia data """
    def __init__(self):
        pass

    def remove_sortkey(self, text):
        """ Removes sortkey from date """
        return re.sub('^[^♠]*♠', '', text)

    def format_text(self, text):
        """ Text formatting """
        letters = ['(' + letter + ')' for letter in ascii_lowercase]
        replacements = ['\n', '–', '-', '—', '--', '.'] + letters
        for replacement in replacements:
            text = text.replace('\xa0', ' ')
            text = text.replace(replacement, '')
            text = self.remove_sortkey(text)
        return text

    def get_names(self, headers):
        """ Extracts state names """
        names = []
        for header in headers:
            if header.find('a') is not None:
                text = self.format_text(header.find('a').get('title'))
                names.append(text)
            else:
                text = self.format_text(header.text)
                names.append(text)
        names[0], names[1], names[-1], names[-2], names[-3] = 'week', 'date', 'remark', 'increment', 'total'
        return names

    def get_data(self, table, names):
        """ Extracts case data """
        df = []
        for row in table[1:-1]:
            cols = row.findAll('td')
            data = dict.fromkeys(names)
            if len(cols) == 21:
                week = cols[0]
            else:
                cols.insert(0, week)
            for i, col in enumerate(cols):
                data[names[i]] = self.format_text(col.text)
            df.append(data)
        return df

    def format_date(self, date):
        """ Formats date """
        months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Juni', 'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        date_components = date.replace('.', '').split(' ')
        for i, month in enumerate(months):
            date_components[0] = date_components[0].rjust(2, '0')
            date_components[1] = date_components[1].replace(month, str(i + 1).rjust(2, '0'))
        date = date_components[2] + '-' + date_components[1] + '-' + date_components[0]
        return date

    def split_date(self, date):
        """ Split date column """
        date_cols = date.str.split('-', expand=True).astype(np.int32)
        return date_cols[0], date_cols[1], date_cols[2]

    def extract_header(self, soup):
        """ Get header from table """
        table_header = soup.find_all('caption')[0].\
            find_parent().\
            find_parent().\
            find_next('tr').\
            findAll('th')
        return table_header

    def extract_cases(self, soup):
        """ Extract case table """
        table_cases = soup.find_all('table')[0].\
            find_all('tr', attrs={'class': None})
        return table_cases

    def extract_indicents(self, soup):
        """ Extract deaths table """
        table_incidents = soup.find_all('table')[1].\
            find_all('tr', attrs={'class': None})
        return table_incidents

    def extract_deaths(self, soup):
        """ Extract deaths table """
        table_deaths = soup.find_all('table')[2].\
            find_all('tr', attrs={'class': None})
        return table_deaths

    def remove_brackets(self, col):
        return col.replace('\([^)]*\)', '', regex=True)

    def prepare_data(self, data, variable):
        """ Generates data """
        df = pd.DataFrame.from_dict(data)
        df = df.drop(['total', 'increment', 'remark'], axis=1)
        df['date'] = df['date'].apply(self.format_date)
        df = df.apply(self.remove_brackets)
        df = pd.melt(df, id_vars=['week', 'date'], var_name='state', value_name=variable + '_cum')
        df[variable + '_cum'] = df[variable + '_cum'].replace(' ', '', regex=True)
        df[variable + '_cum'] = df[variable + '_cum'].replace('', '0', regex=True)
        df[variable + '_cum'] = df[variable + '_cum'].astype(np.int32)
        df[variable] = df.groupby('state')[variable + '_cum'].diff()
        df[variable] = df[variable].replace(np.nan, 0, regex=True).astype(np.int32)
        df['state'] = df['state'].str.replace('Freie Hansestadt Bremen', 'Bremen')
        df['state'] = df['state'].str.replace(' ', '')
        return df

    def join_data(self, df_cases, df_deaths):
        """ Merges case and death data """
        states = {
            'state': [
                'NordrheinWestfalen', 'Bayern', 'BadenWürttemberg', 'Niedersachsen',
                'Hessen', 'RheinlandPfalz', 'Sachsen', 'Berlin', 'SchleswigHolstein',
                'Brandenburg', 'SachsenAnhalt', 'Thüringen', 'Hamburg',
                'MecklenburgVorpommern', 'Saarland', 'Bremen'
            ],
            'population': [
                17933000, 13077000, 11070000, 7982000,
                6266000, 4085000, 4078000, 3645000,
                2897000, 2512000, 2208000, 2143000,
                1841000, 1610000, 991000, 683000
            ],
            'code': ['NW', 'BY', 'BW', 'NI',
                     'HE', 'RP', 'SN', 'BE',
                     'SH', 'BB', 'ST', 'TH',
                     'HH', 'MV', 'SL', 'HB']
        }
        df_states = pd.DataFrame.from_dict(states)
        df = pd.merge(left=df_cases, right=df_deaths, how='left', on=['date', 'state'])
        df = pd.merge(left=df, right=df_states, how='left', on=['state'])
        df = df.replace(np.nan, 0)
        df['population'] = df['population'].astype(np.int64)
        df['deaths'] = df['deaths'].astype(np.int32)
        df['deaths_cum'] = df['deaths_cum'].astype(np.int32)
        df['year'], df['month'], df['day'] = self.split_date(df['date'])
        df['country'] = 'Germany'
        df = df[['date', 'year', 'month', 'day', 'country', 'state', 'code', 'cases', 'cases_cum', 'deaths', 'deaths_cum', 'population']]
        return df
