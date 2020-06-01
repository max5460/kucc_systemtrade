from CommonConstant import (
                            DROP_COLUMN_NAME_LIST,
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
                            DIFFERENCE_COLUMN_SUFFIX
                           )
import pandas as pd
from TechnicalIndex import GetExponentialMovingAverage, GetMACD, GetDMIandADX
from decimal import Decimal, InvalidOperation
from LogMessage import CreateDataFrameAnalysisMessage
from logging import getLogger
logger = getLogger()


def __DecimalizeDataFrame(sourceDataFrame):

    if sourceDataFrame is None or len(sourceDataFrame) == 0:
        return None

    sourceColumns = sourceDataFrame.columns
    sourceNdarray = sourceDataFrame.values
    Y_length, X_length = sourceNdarray.shape

    try:
        for X_idx in range(X_length):
            for Y_idx in range(Y_length):
                sourceNdarray[Y_idx, X_idx] = Decimal(str(sourceNdarray[Y_idx, X_idx]))
    except InvalidOperation:
        return None

    return pd.DataFrame(sourceNdarray, columns=sourceColumns)


def __GetDifferenceColumnBetweenTodayAndPreviousDay(sourceDataFrame):

    returnDataFrame = pd.DataFrame(None)

    todayColumns = [columnName for columnName in sourceDataFrame.columns if PREVIOUS_COLUMN_PREFIX not in columnName]

    for columnName in todayColumns:
        if PREVIOUS_COLUMN_PREFIX + columnName in sourceDataFrame.columns:
            returnDataFrame[columnName + DIFFERENCE_COLUMN_SUFFIX] = sourceDataFrame[columnName] - sourceDataFrame[PREVIOUS_COLUMN_PREFIX + columnName]

    return returnDataFrame


def __GetAlignedDataFrameLength(sourceDataFrameList):

    errorDataFrameList = [technicalIndexDataFrame for technicalIndexDataFrame in sourceDataFrameList if technicalIndexDataFrame is None or len(technicalIndexDataFrame) == 0]
    if len(errorDataFrameList) != 0:
        return []

    minimumRowsCount = min([len(technicalIndexDataFrame) for technicalIndexDataFrame in sourceDataFrameList])

    for technicalIndexDataFrame in sourceDataFrameList:
        if len(technicalIndexDataFrame) > minimumRowsCount:
            technicalIndexDataFrame.drop(labels=technicalIndexDataFrame.index[0:len(technicalIndexDataFrame) - minimumRowsCount], inplace=True)
            technicalIndexDataFrame.reset_index(drop=True, inplace=True)

    return sourceDataFrameList


def __GetPreviousDayTechnicalIndex(sourceDataFrame):

    previousDayTechnicalIndexDataFrame = sourceDataFrame.copy()
    previousTrainingTechnicalIndexColumnList = [PREVIOUS_COLUMN_PREFIX + columnName for columnName in sourceDataFrame.columns]
    previousDayTechnicalIndexDataFrame.columns = previousTrainingTechnicalIndexColumnList

    return previousDayTechnicalIndexDataFrame


def __GetDMIandADXDataFrame(sourceDataFrame):

    plusDIdataFrame, minusDIdataFrame, ADXdataFrame = GetDMIandADX(calculateSourceDataFrame=sourceDataFrame,
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

    if plusDIdataFrame is None or minusDIdataFrame is None or ADXdataFrame is None:
        return None

    DMIandADXDataFrameList = [plusDIdataFrame, minusDIdataFrame, ADXdataFrame]
    alignedDataFrameList = __GetAlignedDataFrameLength(DMIandADXDataFrameList)
    if len(alignedDataFrameList) == 0:
        return None

    DMIandADXDataFrame = pd.concat(alignedDataFrameList, axis=1)

    previousDayDMIandADXDataFrame = __GetPreviousDayTechnicalIndex(DMIandADXDataFrame)
    if previousDayDMIandADXDataFrame is None:
        return None

    DMIandADXDataFrame.drop(0, inplace=True)
    DMIandADXDataFrame.reset_index(drop=True, inplace=True)
    DMIandADXDataFrame = pd.concat([DMIandADXDataFrame, previousDayDMIandADXDataFrame.iloc[:-1]], axis=1)
    differenceDataFrameBetweenTodayAndPreviousDay = __GetDifferenceColumnBetweenTodayAndPreviousDay(DMIandADXDataFrame)
    if differenceDataFrameBetweenTodayAndPreviousDay is None:
        return None

    DMIandADXDataFrame = pd.concat([DMIandADXDataFrame, differenceDataFrameBetweenTodayAndPreviousDay], axis=1)

    return DMIandADXDataFrame


def GetDataFrameForAnalysis(sourceDataFrame):

    if sourceDataFrame is None or len(sourceDataFrame) == 0:
        logger.info(CreateDataFrameAnalysisMessage.sourceDataFrameError)
        return None

    technicalIndexDataFrame = sourceDataFrame.copy()

    for dropColumnName in DROP_COLUMN_NAME_LIST:
        if dropColumnName in technicalIndexDataFrame.columns:
            technicalIndexDataFrame.drop(dropColumnName, axis=1, inplace=True)

    technicalIndexDataFrame = __DecimalizeDataFrame(technicalIndexDataFrame)
    if technicalIndexDataFrame is None:
        logger.info(CreateDataFrameAnalysisMessage.decimalizeError)
        return None

    shortEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=technicalIndexDataFrame, calculate_parameter=5, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SHORT_EMA)
    middleEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=technicalIndexDataFrame, calculate_parameter=20, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MIDDLE_EMA)
    longEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=technicalIndexDataFrame, calculate_parameter=60, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_LONG_EMA)
    MACD_DataFrame, signalDataFrame = GetMACD(calculateSourceDataFrame=technicalIndexDataFrame, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, baseLine_parameter=12, relativeLine_parameter=26, signal_parameter=9, MACDDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MACD, signalDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SIGNAL)

    technicalIndexDataFrameList = [technicalIndexDataFrame, shortEMADataFrame, middleEMADataFrame, longEMADataFrame, MACD_DataFrame, signalDataFrame]
    alignedDataFrameList = __GetAlignedDataFrameLength(technicalIndexDataFrameList)
    if len(alignedDataFrameList) == 0:
        logger.info(CreateDataFrameAnalysisMessage.technicalIndexDataFrameError)
        return None

    technicalIndexDataFrame = pd.concat(alignedDataFrameList, axis=1)

    previousDayTechnicalIndexDataFrame = __GetPreviousDayTechnicalIndex(technicalIndexDataFrame)
    if previousDayTechnicalIndexDataFrame is None:
        logger.info(CreateDataFrameAnalysisMessage.previousDayDataFrameError)
        return None

    technicalIndexDataFrame.drop(0, inplace=True)
    technicalIndexDataFrame.reset_index(drop=True, inplace=True)
    technicalIndexDataFrame = pd.concat([technicalIndexDataFrame, previousDayTechnicalIndexDataFrame.iloc[:-1]], axis=1)
    differenceDataFrameBetweenTodayAndPreviousDay = __GetDifferenceColumnBetweenTodayAndPreviousDay(technicalIndexDataFrame)
    if differenceDataFrameBetweenTodayAndPreviousDay is None:
        logger.info(CreateDataFrameAnalysisMessage.differenceDataFrameError)
        return None

    technicalIndexDataFrame = pd.concat([technicalIndexDataFrame, differenceDataFrameBetweenTodayAndPreviousDay], axis=1)

    DMIandADXDataFrame = __GetDMIandADXDataFrame(technicalIndexDataFrame)
    if DMIandADXDataFrame is None:
        logger.info(CreateDataFrameAnalysisMessage.DMIandADXDataFrameError)
        return None

    alignedDataFrameList = __GetAlignedDataFrameLength([technicalIndexDataFrame, DMIandADXDataFrame])
    if len(alignedDataFrameList) == 0:
        logger.info(CreateDataFrameAnalysisMessage.DMIandADXDataFrameError)
        return None

    technicalIndexDataFrame = pd.concat(alignedDataFrameList, axis=1)

    nonPriceMovementIndex = technicalIndexDataFrame.index[technicalIndexDataFrame[TECHNICAL_INDEX_COLUMN_NAME_CLOSE + DIFFERENCE_COLUMN_SUFFIX] == 0]
    if len(nonPriceMovementIndex) > 0:
        technicalIndexDataFrame.drop(nonPriceMovementIndex, inplace=True)
        technicalIndexDataFrame.reset_index(drop=True, inplace=True)

    return technicalIndexDataFrame

