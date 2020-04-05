# A free API for COVID-19 data

For all those, who are struggling with gathering and preparing COVID-19 data, we've created a **free** API that makes it easy to integrate the latest worldwide and Germany COVID-19 data into your application. The API uses official data from the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide) (world data) as well as Robert-Koch Institute ([Germany data, through this Wikipedia article](https://de.wikipedia.org/wiki/COVID-19-Pandemie_in_Deutschland)) and delivers a clear and concise data structure for further processing, analysis etc.

If you have any questions, do not hesitate to open an issue or to contact us. If you use our API in your website or product, it would be great, if you could add a link to our website: https://www.statworx.com. Thank you and stay healthy!

## Making a request

### World data API

The world API delivers data for 196 countries, queryable by their 2-character [country alpha codes](https://www.iban.com/country-codes). If you want to query all countries, use `{'code': 'ALL'}` in the payload. You can invoke the API using any programming language, e.g. Python:

```python
import requests
import json
import pandas as pd

# POST to API
payload = {'code': 'DE'}
URL = 'https://api.statworx.com/covid'
response = requests.post(url=URL, data=json.dumps(payload))

# Convert to data frame
df = pd.DataFrame.from_dict(json.loads(response.text))
```

or R:

```R
library(httr)
library(jsonlite)

# Post to API
payload <- list(code = "DE")
response <- httr::POST(url = "https://api.statworx.com/covid",
                       body = toJSON(payload, auto_unbox = TRUE), encode = "json")

# Convert to data frame
content <- rawToChar(response$content)
df <- data.frame(fromJSON(content))
```

This is what the result looks like:

| date       | day  | month | year | cases | deaths | country | code | population | cases_cum | deaths_cum |
| ---------- | ---- | ----- | ---- | ----- | ------ | ------- | ---- | ---------- | --------- | ---------- |
| 2019-12-31 | 31   | 12    | 2019 | 0     | 0      | Germany | DE   | 82927922   | 0         | 0          |
| 2020-01-01 | 1    | 1     | 2020 | 0     | 0      | Germany | DE   | 82927922   | 0         | 0          |
| 2020-01-02 | 2    | 1     | 2020 | 0     | 0      | Germany | DE   | 82927922   | 0         | 0          |
| ...        | ...  | ...   | ...  | ...   | ...    | ...     | ...  | ...        | ...       | ...        |

### Germany data API

The Germany data API is very similar to the world data API, except that (at the moment) it does not require any payload. This means that you can als use simple GET-requests for querying the data. For Python, you would query the data like this:

```python
import requests
import json
import pandas as pd

# POST to API
URL = 'https://api.statworx.com/covid/de'
response = requests.get(url=URL)

# Convert to data frame
df = pd.DataFrame.from_dict(json.loads(response.text))
```

Again, in R we use:

```R
library(httr)
library(jsonlite)

# Post to API
response <- httr::GET(url = "https://api.statworx.com/covid", encode = "json")

# Convert to data frame
content <- rawToChar(response$content)
df <- data.frame(fromJSON(content))
```

The resulting data frame looks something like this:

| date       | day  | month | year | cases | deaths | country | state  | code | population | cases_cum | deaths_cum |
| ---------- | ---- | ----- | ---- | ----- | ------ | ------- | ------ | ---- | ---------- | --------- | ---------- |
| 2020-02-24 | 24   | 2     | 2020 | 0     | 0      | Germany | Bayern | BY   | 13077000   | 0         | 0          |
| 2020-02-25 | 25   | 2     | 2020 | 1     | 0      | Germany | Bayern | BY   | 13077000   | 1         | 0          |
| 2020-02-26 | 26   | 2     | 2020 | 2     | 0      | Germany | Bayern | BY   | 13077000   | 3         | 0          |
| ...        | ...  | ...   | ...  | ...   | ...    | ...     | ...    | ...  | ...        | ...       | ...        |


## What fields does the data contain?

The API JSON response contains the following data points:

| Name       | Description                   | Type   | Example      |
| ---------- | ---------------------------   | ------ | ------------ |
| date       | Date                          | string | '2020-01-01' |
| day        | Day of week                   | int    | 2            |
| month      | Month                         | int    | 5            |
| year       | Year                          | int    | 2020         |
| cases      | Number of cases reported      | int    | 100          |
| deaths     | Number of deaths reported     | int    | 10           |
| country    | Country name                  | string | 'Germany'    |
| state      | State name (only Germany API) | string | 'Germany'    |
| code       | ISO code country or state     | string | 'DE' or 'BY' |
| population | Population as of 2018         | int    | 82927922     |
| cases_cum  | Cumulative number of cases    | int    | 29212        |
| deaths_cum | Cumulative number of deaths   | int    | 262          |

##  Why not use the original data?

There are several COVID-19 data sources out there. However, most of the sources are kind of quirky (e.g. wide format, bad column names etc.). Furthermore, many data sources so not contain the cumulative sum of cases or population information for relative KPIs. Our API data is arranged and named using best practices (e.g. long format, snake case variable names) and augmented with cumulative case and death numbers as well as population info on country (world API) and state (Germany API) level.

## How did you do that?

The API is built using Python 3 and deployed using [Google Cloud Run](https://cloud.google.com/run?hl=en), a container-based serverless function framework in the cloud.

## Credits

If you have any questions or remarks, do not hesitate to open an issue or to contact us. Also, if you use our API in your website or product, it would be great, if you could add a link to our website: https://www.statworx.com. Thank you and stay healthy!