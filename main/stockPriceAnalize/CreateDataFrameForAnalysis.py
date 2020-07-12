from CommonConstant import (
                            INDEX_COLUMN_NAME_DATE,
                            TECHNICAL_INDEX_COLUMN_NAME_OPEN,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            TECHNICAL_INDEX_COLUMN_NAME_LOW,
                            TECHNICAL_INDEX_COLUMN_NAME_HIGH,
                            TECHNICAL_INDEX_COLUMN_NAME_SHORT_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_MIDDLE_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_LONG_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_MACD,
                            TECHNICAL_INDEX_COLUMN_NAME_SIGNAL,
                            TECHNICAL_INDEX_COLUMN_NAME_PLUS_DI,
                            TECHNICAL_INDEX_COLUMN_NAME_MINUS_DI,
                            TECHNICAL_INDEX_COLUMN_NAME_ADX,
                            PREVIOUS_COLUMN_PREFIX,
                            PREVIOUS_DAYS_CONSTANT,
                            TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST,
                            TOMORROW_PRICE_PREFIX,
                            LSTM_INPUT_WINDOW_LENGTH
                           )
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from TechnicalIndex import GetExponentialMovingAverage, GetMACD, GetDMIandADX
from decimal import Decimal, InvalidOperation
from LogMessage import CreateDataFrameAnalysisMessage
from logging import getLogger
logger = getLogger()


def __DecimalizeDataFrame(sourceDataFrame):

    if sourceDataFrame is None or len(sourceDataFrame) == 0:
        return None

    sourceNdarray = sourceDataFrame.values
    decimalizedNdarray = np.empty(sourceNdarray.shape, dtype=Decimal)

    Y_length, X_length = sourceNdarray.shape
    try:
        for y_idx in range(Y_length):
            for x_idx in range(X_length):
                decimalizedNdarray[y_idx, x_idx] = Decimal(str(sourceNdarray[y_idx, x_idx]))
    except InvalidOperation:
        return None

    return pd.DataFrame(decimalizedNdarray, columns=sourceDataFrame.columns, index=sourceDataFrame.index)


def __GetTechnicalIndexDataFrameList(sourceDataFrame):
    def __GetPreviousDayTechnicalIndex(_sourceOHLCdataFrame):

        previousDayTechnicalIndexDataFrame = _sourceOHLCdataFrame.copy().shift()
        previousTrainingTechnicalIndexColumnList = [PREVIOUS_COLUMN_PREFIX + columnName for columnName in sourceDataFrame.columns]
        previousDayTechnicalIndexDataFrame.columns = previousTrainingTechnicalIndexColumnList

        return previousDayTechnicalIndexDataFrame.dropna()

    calculateSourceOHLC = sourceDataFrame.copy()

    shortEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceOHLC, calculate_parameter=5, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SHORT_EMA)
    middleEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceOHLC, calculate_parameter=20, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MIDDLE_EMA)
    longEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceOHLC, calculate_parameter=60, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_LONG_EMA)
    MACD_DataFrame, signalDataFrame = GetMACD(calculateSourceDataFrame=calculateSourceOHLC, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, baseLine_parameter=12, relativeLine_parameter=26, signal_parameter=9, MACDDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MACD, signalDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SIGNAL)

    previousDayOHLCdataFrame = __GetPreviousDayTechnicalIndex(calculateSourceOHLC)
    if previousDayOHLCdataFrame is None:
        logger.info(CreateDataFrameAnalysisMessage.previousDayDataFrameError)
        return None

    todayAndPreviousOHLCdataFrame = pd.concat([calculateSourceOHLC, previousDayOHLCdataFrame], axis=1).dropna()
    plusDIdataFrame, minusDIdataFrame, ADXdataFrame = GetDMIandADX(calculateSourceDataFrame=todayAndPreviousOHLCdataFrame,
                                                                   calculateSourceColumnName_TodayHigh=TECHNICAL_INDEX_COLUMN_NAME_HIGH,
                                                                   calculateSourceColumnName_TodayLow=TECHNICAL_INDEX_COLUMN_NAME_LOW,
                                                                   calculateSourceColumnName_PreviousHigh=PREVIOUS_COLUMN_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_HIGH,
                                                                   calculateSourceColumnName_PreviousLow=PREVIOUS_COLUMN_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_LOW,
                                                                   calculateSourceColumnName_PreviousClose=PREVIOUS_COLUMN_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                                                                   plusDIcolumnName=TECHNICAL_INDEX_COLUMN_NAME_PLUS_DI,
                                                                   minusDIcolumnName=TECHNICAL_INDEX_COLUMN_NAME_MINUS_DI,
                                                                   DI_Parameter=14,
                                                                   ADX_Parameter=26,
                                                                   ADXcolumnName=TECHNICAL_INDEX_COLUMN_NAME_ADX)

    return [shortEMADataFrame, middleEMADataFrame, longEMADataFrame, MACD_DataFrame, signalDataFrame, plusDIdataFrame, minusDIdataFrame, ADXdataFrame]


def __GetSeveralDaysTechnicalIndexDataFrame(sourceDataFrame, fundamentalColumnName):

    if sourceDataFrame is None or len(sourceDataFrame) == 0:
        logger.info(CreateDataFrameAnalysisMessage.sourceDataFrameError)
        return None

    if len(sourceDataFrame) < LSTM_INPUT_WINDOW_LENGTH:
        return None

    if fundamentalColumnName not in sourceDataFrame.columns:
        return None

    severalDaysDataFrame = sourceDataFrame[[fundamentalColumnName]].copy()

    severalDaysDataFrame.sort_index(ascending=False, inplace=True)

    returnDataFrameColumn = [fundamentalColumnName]
    for idx in range(1, LSTM_INPUT_WINDOW_LENGTH):
        previousCloseSeries = severalDaysDataFrame[fundamentalColumnName].shift(-1 * idx)
        addedColumnName = str(idx) + PREVIOUS_DAYS_CONSTANT + fundamentalColumnName
        severalDaysDataFrame[addedColumnName] = previousCloseSeries
        returnDataFrameColumn.insert(0, addedColumnName)

    severalDaysDataFrame.sort_index(ascending=True, inplace=True)

    return severalDaysDataFrame[returnDataFrameColumn]


def __GetScaledDataFrame(sourceDataFrame):
    copiedDataFrame = sourceDataFrame.copy()

    copiedDataFrame.dropna(inplace=True)
    returnDataFrameLength = len(copiedDataFrame)
    returnDataFrameColumnsCount = len(copiedDataFrame.columns)

    returnNdArray = np.empty([returnDataFrameLength, returnDataFrameColumnsCount])

    for idx in range(returnDataFrameColumnsCount):
        standardScaler = StandardScaler()
        floatNdArray = np.array(copiedDataFrame[copiedDataFrame.columns[idx]].astype('float64')).reshape(returnDataFrameLength, 1)
        returnNdArray[0:returnDataFrameLength, idx:idx + 1] = standardScaler.fit_transform(floatNdArray)

    returnDataFrameIndex = copiedDataFrame.index
    return pd.DataFrame(returnNdArray, columns=sourceDataFrame.columns, index=returnDataFrameIndex)


def GetDataFrameForAnalysis(sourceDataFrame):

    if sourceDataFrame is None or len(sourceDataFrame) == 0:
        logger.info(CreateDataFrameAnalysisMessage.sourceDataFrameError)
        return None

    columnNameList_OHLC = [INDEX_COLUMN_NAME_DATE, TECHNICAL_INDEX_COLUMN_NAME_OPEN, TECHNICAL_INDEX_COLUMN_NAME_HIGH, TECHNICAL_INDEX_COLUMN_NAME_LOW, TECHNICAL_INDEX_COLUMN_NAME_CLOSE]
    sourceOHLCdataFrame = sourceDataFrame[columnNameList_OHLC].copy()
    sourceOHLCdataFrame.set_index(INDEX_COLUMN_NAME_DATE, inplace=True)

    decimalizedOHLCdataFrame = __DecimalizeDataFrame(sourceOHLCdataFrame)

    if decimalizedOHLCdataFrame is None:
        logger.info(CreateDataFrameAnalysisMessage.decimalizeError)
        return None

    technicalIndexDataFrameList = __GetTechnicalIndexDataFrameList(decimalizedOHLCdataFrame)

    for checkedTechnicalIndexDataFrame in technicalIndexDataFrameList:
        if checkedTechnicalIndexDataFrame is None or len(checkedTechnicalIndexDataFrame) == 0:
            logger.info(CreateDataFrameAnalysisMessage.technicalIndexDataFrameError)
            return None

    technicalIndexDataFrame = pd.concat(technicalIndexDataFrameList, axis=1)
    technicalIndexAndOHLCdataFrame = pd.concat([decimalizedOHLCdataFrame, technicalIndexDataFrame], axis=1)
    scaledDataFrame = __GetScaledDataFrame(technicalIndexAndOHLCdataFrame[TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST].dropna())

    severalDaysTechnicalIndexDataFrame = pd.DataFrame(None)
    for severalDaysColumnTechnicalIndexColumnName in TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST:
        severalDaysDataFrame = __GetSeveralDaysTechnicalIndexDataFrame(scaledDataFrame, severalDaysColumnTechnicalIndexColumnName)
        severalDaysTechnicalIndexDataFrame = pd.concat([severalDaysTechnicalIndexDataFrame, severalDaysDataFrame], axis=1)

    tomorrowClosePriceDataFrame = decimalizedOHLCdataFrame[[TECHNICAL_INDEX_COLUMN_NAME_CLOSE]].shift(-1).astype('float64')

    # dropnaメソッドで消えないように便宜上0にしておく
    tomorrowClosePriceDataFrame.iloc[-1] = 0
    tomorrowClosePriceDataFrame.columns = [TOMORROW_PRICE_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_CLOSE]

    returnDataFrame = pd.concat([severalDaysTechnicalIndexDataFrame, tomorrowClosePriceDataFrame], axis=1)
    returnDataFrame.dropna(inplace=True)

    return returnDataFrame


