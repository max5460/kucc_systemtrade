import urllib.request as request
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from CommonConstant import CSVFILE_STORE_FOLDER_NAME, DROP_COLUMN_NAME_DATE, CSVFILE_EXTENSION
import os
from glob import glob

SOURCE_URL = 'https://kabuoji3.com/stock/'
CSV_NAME_UNUSABLE_WORDS = r'[\\/:*?"<>|]+'
BRAND_CODE_PARAMETER = 'stock/[0-9]+'
PAGE_PARAMETER = '\?page=[0-9]+'
BRAND_CODE_AND_YEAR_PARAMETER = 'stock/[0-9]+/[0-9]+'


def __GetExistBrandDictionary():
    existBrandDDict = {}
    for csvFile in glob(CSVFILE_STORE_FOLDER_NAME + '//*' + CSVFILE_EXTENSION):
        csvFileName = os.path.splitext(os.path.basename(csvFile))[0]

        if csvFileName in existBrandDDict:
            continue

        existBrandDDict[csvFileName] = pd.read_csv(csvFile, encoding='UTF-8')

    return existBrandDDict


def __GetBrandCodeFromCSVFile(csvFile):
    csvFileName = os.path.splitext(os.path.basename(csvFile))[0]
    companyNameFromCSVFile = re.search(' .*', csvFileName)[0]
    return csvFileName.replace(companyNameFromCSVFile, '')


def __stripInvalidCharacterFromFileName(fileName):
    return re.sub(CSV_NAME_UNUSABLE_WORDS, '', fileName)


def __DeleteDisappearedBrandCSV(existBrandDDict, brandOnWeb):
    for brand in existBrandDDict.keys():
        if brand not in brandOnWeb:
            os.remove(CSVFILE_STORE_FOLDER_NAME + '//' + brand + CSVFILE_EXTENSION)


def __GetExistBrandStockPriceDataFrame(urlTag, existBrandDDict, csvFileName):

    latestStockPriceDataFrame = pd.read_html(urlTag.attrs['href'])[0]
    time.sleep(1)
    mergedStockPriceDataFrame = pd.concat([latestStockPriceDataFrame, existBrandDDict[csvFileName]])
    mergedStockPriceDataFrame.drop_duplicates(inplace=True)

    return mergedStockPriceDataFrame


def __GetAllDayStockPriceDataFrame(urlTag):
    individualStockPriceDataFrame = pd.DataFrame(None)

    response_IndividualStockPricePerYear = request.urlopen(urlTag.attrs['href'])
    bs_GetIndividualStockPricePerYear = BeautifulSoup(response_IndividualStockPricePerYear, 'html.parser')
    time.sleep(1)

    for individualStockPricePerYearTag in bs_GetIndividualStockPricePerYear.find_all("a", href=re.compile(BRAND_CODE_AND_YEAR_PARAMETER)):
        individualStockPriceFromHtml = pd.read_html(individualStockPricePerYearTag.attrs['href'])

        if individualStockPriceFromHtml is None:
            continue

        individualStockPriceDataFrame = pd.concat([individualStockPriceDataFrame, individualStockPriceFromHtml[0]])
        time.sleep(1)

    return individualStockPriceDataFrame


def ExportIndividualStockPrice():

    existBrandDDict = __GetExistBrandDictionary()
    brandOnWeb = []

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

            for urlTag in bs_GetIndividualStockPrice.find_all("a", href=re.compile(BRAND_CODE_PARAMETER)):
                csvFileName = urlTag.text

                if csvFileName in existBrandDDict:
                    outIndividualStockPriceDataFrame = __GetExistBrandStockPriceDataFrame(urlTag, existBrandDDict, csvFileName)
                else:
                    outIndividualStockPriceDataFrame = __GetAllDayStockPriceDataFrame(urlTag)

                csvFilePath = CSVFILE_STORE_FOLDER_NAME + '\\' + __stripInvalidCharacterFromFileName(csvFileName) + CSVFILE_EXTENSION
                outIndividualStockPriceDataFrame.sort_values(DROP_COLUMN_NAME_DATE, inplace=True)
                outIndividualStockPriceDataFrame.to_csv(csvFilePath, index=False)

                brandOnWeb.append(csvFileName)

    except Exception as ex:
        return str(ex)

    __DeleteDisappearedBrandCSV(existBrandDDict, brandOnWeb)

    return None
