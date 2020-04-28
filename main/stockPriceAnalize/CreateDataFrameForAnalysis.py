from CommonConstant import (
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            TECHNICAL_INDEX_COLUMN_NAME_SHORT_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_MIDDLE_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_LONG_EMA,
                            TECHNICAL_INDEX_COLUMN_NAME_MACD,
                            TECHNICAL_INDEX_COLUMN_NAME_SIGNAL,
                            TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST,
                            PREVIOUS_COLUMN_PREFIX,
                            DIFFERENCE_COLUMN_SUFFIX
                           )
import pandas as pd
from TechnicalIndex import GetExponentialMovingAverage, GetMACD


def __AddDifferenceColumn(technicalIndexDataFrame):

    previousDayColumns = [columnName for columnName in technicalIndexDataFrame.columns if PREVIOUS_COLUMN_PREFIX in columnName]
    if len(previousDayColumns) == 0:
        return

    for columnName in TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST:
        technicalIndexDataFrame[columnName + DIFFERENCE_COLUMN_SUFFIX] = technicalIndexDataFrame[columnName] - technicalIndexDataFrame[PREVIOUS_COLUMN_PREFIX + columnName]


def __GetAlignedDataFrameLength(technicalIndexDataFrameList):

    errorDataFrameList = [technicalIndexDataFrame for technicalIndexDataFrame in technicalIndexDataFrameList if technicalIndexDataFrame is None or len(technicalIndexDataFrame) == 0]
    if len(errorDataFrameList) != 0:
        return None

    minimumRowsCount = min([len(technicalIndexDataFrame) for technicalIndexDataFrame in technicalIndexDataFrameList])

    for technicalIndexDataFrame in technicalIndexDataFrameList:
        if len(technicalIndexDataFrame) > minimumRowsCount:
            technicalIndexDataFrame.drop(labels=technicalIndexDataFrame.index[0:len(technicalIndexDataFrame) - minimumRowsCount], inplace=True)
            technicalIndexDataFrame.reset_index(drop=True, inplace=True)

    return technicalIndexDataFrameList


def __GetPreviousDayTechnicalIndex(technicalIndexDataFrame):

    previousDayTechnicalIndexDataFrame = technicalIndexDataFrame[TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST].copy()
    previousTrainingTechnicalIndexColumnList = [PREVIOUS_COLUMN_PREFIX + columnName for columnName in TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST]
    previousDayTechnicalIndexDataFrame.columns = previousTrainingTechnicalIndexColumnList

    return previousDayTechnicalIndexDataFrame


def GetDataFrameForAnalysis(sourceDataFrame):

    shortEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=sourceDataFrame, calculate_parameter=5, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SHORT_EMA)
    middleEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=sourceDataFrame, calculate_parameter=20, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MIDDLE_EMA)
    longEMADataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=sourceDataFrame, calculate_parameter=60, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, returnDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_LONG_EMA)
    MACD_DataFrame, signalDataFrame = GetMACD(calculateSourceDataFrame=sourceDataFrame, calculateSourceColumnName=TECHNICAL_INDEX_COLUMN_NAME_CLOSE, baseLine_parameter=12, relativeLine_parameter=26, signal_parameter=9, MACDDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_MACD, signalDataFrameColumnName=TECHNICAL_INDEX_COLUMN_NAME_SIGNAL)
    technicalIndexDataFrameList = [sourceDataFrame, shortEMADataFrame, middleEMADataFrame, longEMADataFrame, MACD_DataFrame, signalDataFrame]

    alignedDataFrameList = __GetAlignedDataFrameLength(technicalIndexDataFrameList)
    technicalIndexDataFrame = pd.concat(alignedDataFrameList, axis=1)
    lastDayTechnicalIndexDataFrame = __GetPreviousDayTechnicalIndex(technicalIndexDataFrame)

    technicalIndexDataFrame.drop(0, inplace=True)
    technicalIndexDataFrame.reset_index(drop=True, inplace=True)
    todayAndPreviousDayTechnicalIndexDataFrame = pd.concat([technicalIndexDataFrame[TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST], lastDayTechnicalIndexDataFrame.iloc[:-1]], axis=1)
    __AddDifferenceColumn(todayAndPreviousDayTechnicalIndexDataFrame)


    nonPriceMovementIndex = todayAndPreviousDayTechnicalIndexDataFrame.index[todayAndPreviousDayTechnicalIndexDataFrame[TECHNICAL_INDEX_COLUMN_NAME_CLOSE] == todayAndPreviousDayTechnicalIndexDataFrame[PREVIOUS_COLUMN_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_CLOSE]]
    if len(nonPriceMovementIndex) > 0:
        todayAndPreviousDayTechnicalIndexDataFrame.drop(nonPriceMovementIndex, inplace=True)
        todayAndPreviousDayTechnicalIndexDataFrame.reset_index(drop=True, inplace=True)

    returnDataFrame = todayAndPreviousDayTechnicalIndexDataFrame

    return returnDataFrame

