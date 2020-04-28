import pandas as pd
import numpy as np
from decimal import Decimal
from statistics import mean


def __Decimalize(number):
    return Decimal(str(number))


def GetExponentialMovingAverage(calculateSourceDataFrame, calculate_parameter, calculateSourceColumnName, returnDataFrameColumnName):

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        return None

    if len(calculateSourceDataFrame) < calculate_parameter:
        return None

    if calculateSourceColumnName not in calculateSourceDataFrame:
        return None

    firstEMA = __Decimalize(mean(calculateSourceDataFrame[calculateSourceColumnName][0:calculate_parameter]))
    exponentialMovingAverageNdarray = np.array([firstEMA])

    smoothingExponential = __Decimalize(2 / (calculate_parameter + 1))

    for idx in range(calculate_parameter, len(calculateSourceDataFrame)):
        before_EMA = exponentialMovingAverageNdarray[-1]
        current_Amount = before_EMA + smoothingExponential * __Decimalize((calculateSourceDataFrame[calculateSourceColumnName].loc[idx] - before_EMA))
        exponentialMovingAverageNdarray = np.append(exponentialMovingAverageNdarray, current_Amount)

    returnDataFrame = pd.DataFrame(exponentialMovingAverageNdarray)
    returnDataFrame.columns = [returnDataFrameColumnName]

    return returnDataFrame


def GetMACD(calculateSourceDataFrame, calculateSourceColumnName, baseLine_parameter, relativeLine_parameter, signal_parameter, MACDDataFrameColumnName, signalDataFrameColumnName):

    if baseLine_parameter > relativeLine_parameter:
        return None

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        return None

    if calculateSourceColumnName not in calculateSourceDataFrame.columns:
        return None

    baseLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=baseLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='基準線')
    relativeLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=relativeLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='相対線')

    if baseLineDataFrame is None or len(baseLineDataFrame) == 0:
        return None

    if relativeLineDataFrame is None or len(relativeLineDataFrame) == 0:
        return None

    baseLineList = baseLineDataFrame.values
    relativeLineList = relativeLineDataFrame.values

    calculated_MACDlist = []
    for idx in range(len(relativeLineList)):
        calculated_MACDlist.append(baseLineList[idx + relativeLine_parameter - baseLine_parameter] - relativeLineList[idx])

    if len(calculated_MACDlist) == 0:
        return None

    MACD_DataFrame = pd.DataFrame(calculated_MACDlist, columns=[MACDDataFrameColumnName])
    signalDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=MACD_DataFrame, calculate_parameter=signal_parameter, calculateSourceColumnName=MACDDataFrameColumnName, returnDataFrameColumnName=signalDataFrameColumnName)

    return MACD_DataFrame, signalDataFrame
