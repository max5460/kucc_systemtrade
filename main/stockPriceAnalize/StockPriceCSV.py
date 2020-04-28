import urllib.request as request
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from CommonConstant import CSVFILE_STORE_FOLDER_NAME

SOURCE_URL = 'https://kabuoji3.com/stock/'
CSV_NAME_UNUSABLE_WORDS = r'[\\/:*?"<>|]+'
STOCK_NUMBER_PARAMETER = 'stock/[0-9]+'
PAGE_PARAMETER = '\?page=[0-9]+'
STOCK_NUMBER_AND_YEAR_PARAMETER = 'stock/[0-9]+/[0-9]+'


def __stripInvalidCharacterFromFileName(fileName):
    return re.sub(CSV_NAME_UNUSABLE_WORDS, '', fileName)


def __GetStockPriceDataFrame(urlTag):
    individualStockPriceDataFrame = pd.DataFrame(None)

    response_IndividualStockPricePerYear = request.urlopen(urlTag.attrs['href'])
    bs_GetIndividualStockPricePerYear = BeautifulSoup(response_IndividualStockPricePerYear, 'html.parser')
    time.sleep(1)

    for individualStockPricePerYearTag in bs_GetIndividualStockPricePerYear.find_all("a", href=re.compile(STOCK_NUMBER_AND_YEAR_PARAMETER)):
        individualStockPriceFromHtml = pd.read_html(individualStockPricePerYearTag.attrs['href'])

        if individualStockPriceFromHtml is None:
            continue

        individualStockPriceDataFrame = pd.concat([individualStockPriceDataFrame, individualStockPriceFromHtml[0]])

    individualStockPriceDataFrame = individualStockPriceDataFrame.sort_values('日付')
    return individualStockPriceDataFrame


def ExportIndividualStockPrice():
    try:
        response_StockPriceTop = request.urlopen(SOURCE_URL)
        bs_GetStockPriceTop = BeautifulSoup(response_StockPriceTop, 'html.parser')
        time.sleep(1)

        stockPriceTopPageParameters = bs_GetStockPriceTop.find_all("a", href=re.compile(PAGE_PARAMETER))
        list_allStockPricePageURL = [SOURCE_URL + stockPriceTopPageParameters[i].attrs['href'] for i in range(len(stockPriceTopPageParameters))]

        for idx in range(len(list_allStockPricePageURL)):
            response_IndividualStockPrice = request.urlopen(list_allStockPricePageURL[idx])
            bs_GetIndividualStockPrice = BeautifulSoup(response_IndividualStockPrice, 'html.parser')
            time.sleep(1)

            for urlTag in bs_GetIndividualStockPrice.find_all("a", href=re.compile(STOCK_NUMBER_PARAMETER)):
                outIndividualStockPriceDataFrame = __GetStockPriceDataFrame(urlTag)
                csvFilePath = CSVFILE_STORE_FOLDER_NAME + '\\' + __stripInvalidCharacterFromFileName(urlTag.text) + '.csv'
                outIndividualStockPriceDataFrame.to_csv(csvFilePath, index=False)

    except Exception as ex:
        return str(ex)

    return None
