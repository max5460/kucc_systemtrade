import pandas as pd
import numpy as np
from statistics import mean
from math import fabs


def GetExponentialMovingAverage(calculateSourceDataFrame, calculate_parameter, calculateSourceColumnName, returnDataFrameColumnName):

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        return None

    if len(calculateSourceDataFrame) < calculate_parameter:
        return None

    if calculateSourceColumnName not in calculateSourceDataFrame:
        return None

    calculateSourceData = calculateSourceDataFrame[calculateSourceColumnName].values

    firstEMA = mean(calculateSourceData[0:calculate_parameter])
    exponentialMovingAverage = [firstEMA]

    smoothingExponential = 2 / (calculate_parameter + 1)

    for idx in range(calculate_parameter, len(calculateSourceData)):
        before_EMA = exponentialMovingAverage[-1]
        current_Amount = before_EMA + smoothingExponential * (calculateSourceData[idx] - before_EMA)
        exponentialMovingAverage.append(current_Amount)

    return pd.DataFrame(exponentialMovingAverage, columns=[returnDataFrameColumnName])


def GetMACD(calculateSourceDataFrame, calculateSourceColumnName, baseLine_parameter, relativeLine_parameter, signal_parameter, MACDDataFrameColumnName, signalDataFrameColumnName):

    if baseLine_parameter > relativeLine_parameter:
        return None, None

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        return None, None

    if calculateSourceColumnName not in calculateSourceDataFrame.columns:
        return None, None

    baseLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=baseLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='基準線')
    relativeLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=relativeLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='相対線')

    if baseLineDataFrame is None or len(baseLineDataFrame) == 0:
        return None, None

    if relativeLineDataFrame is None or len(relativeLineDataFrame) == 0:
        return None, None

    baseLineList = baseLineDataFrame.values
    relativeLineList = relativeLineDataFrame.values

    calculated_MACDlist = []
    for idx in range(len(relativeLineList)):
        calculated_MACDlist.append(baseLineList[idx + relativeLine_parameter - baseLine_parameter] - relativeLineList[idx])

    if len(calculated_MACDlist) == 0:
        return None, None

    MACD_DataFrame = pd.DataFrame(calculated_MACDlist, columns=[MACDDataFrameColumnName])
    signalDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=MACD_DataFrame, calculate_parameter=signal_parameter, calculateSourceColumnName=MACDDataFrameColumnName, returnDataFrameColumnName=signalDataFrameColumnName)

    return MACD_DataFrame, signalDataFrame


def __GetDM(todayHigh, todayLow, previousHigh, previousLow):

    if len(todayHigh) != len(todayLow) != len(previousHigh) != len(previousLow):
        return None, None

    calculateLength = len(todayHigh)

    plusDM = np.array([todayHigh[idx] - previousHigh[idx] for idx in range(calculateLength)])
    minusDM = np.array([previousLow[idx] - todayLow[idx] for idx in range(calculateLength)])

    for idx in range(calculateLength):
        if plusDM[idx] < 0 and minusDM[idx] < 0:
            plusDM[idx] = 0
            minusDM[idx] = 0
            continue

        if plusDM[idx] > minusDM[idx]:
            plusDM[idx] = todayHigh[idx] - previousHigh[idx]
            minusDM[idx] = 0
            continue

        if plusDM[idx] < minusDM[idx]:
            plusDM[idx] = 0
            minusDM[idx] = previousLow[idx] - todayLow[idx]
            continue

        if plusDM[idx] == minusDM[idx]:
            plusDM[idx] = 0
            minusDM[idx] = 0
            continue

    return plusDM, minusDM


def __GetTrueRange(todayHigh, todayLow, previousHigh, previousLow, previousClose):

    if len(todayHigh) != len(todayLow) != len(previousHigh) != len(previousLow) != len(previousClose):
        return None

    calculateLength = len(todayHigh)
    trueRangeList = []
    for idx in range(calculateLength):
        trueRangeCandidate_1 = fabs(todayHigh[idx] - todayLow[idx])
        trueRangeCandidate_2 = fabs(todayHigh[idx] - previousClose[idx])
        trueRangeCandidate_3 = fabs(previousClose[idx] - todayLow[idx])
        trueRangeList.append(max(trueRangeCandidate_1, trueRangeCandidate_2, trueRangeCandidate_3))

    return np.array(trueRangeList)


def __GetDI(plusDM, minusDM, trueRange, DI_Parameter):

    if len(plusDM) != len(minusDM) != len(trueRange):
        return None, None

    calculateLength = len(plusDM)

    if calculateLength < DI_Parameter:
        return None, None

    plusDIlist = []
    minusDIlist = []
    for idx in range(calculateLength - DI_Parameter + 1):
        plusDIlist.append(sum(plusDM[idx:DI_Parameter + idx]) / sum(trueRange[idx:DI_Parameter + idx]) * 100)
        minusDIlist.append(sum(minusDM[idx:DI_Parameter + idx]) / sum(trueRange[idx:DI_Parameter + idx]) * 100)

    return np.array(plusDIlist), np.array(minusDIlist)


def __GetDX(plusDI, minusDI, DXdataFrameColumnName):

    if len(plusDI) != len(minusDI):
        return None

    calculateLength = len(plusDI)

    DXlist = []
    for idx in range(calculateLength):
        DXlist.append(fabs(plusDI[idx] - minusDI[idx]) / (plusDI[idx] + minusDI[idx]) * 100)

    return pd.DataFrame(np.array(DXlist), columns=[DXdataFrameColumnName])


def GetDMIandADX(calculateSourceDataFrame, calculateSourceColumnName_TodayHigh, calculateSourceColumnName_TodayLow,
                 calculateSourceColumnName_PreviousHigh, calculateSourceColumnName_PreviousLow, calculateSourceColumnName_PreviousClose,
                 plusDIcolumnName, minusDIcolumnName, DI_Parameter, ADX_Parameter, ADXcolumnName):

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        return None, None, None

    if calculateSourceColumnName_TodayHigh not in calculateSourceDataFrame.columns:
        return None, None, None

    if calculateSourceColumnName_TodayLow not in calculateSourceDataFrame.columns:
        return None, None, None

    if calculateSourceColumnName_PreviousHigh not in calculateSourceDataFrame.columns:
        return None, None, None

    if calculateSourceColumnName_PreviousLow not in calculateSourceDataFrame.columns:
        return None, None, None

    if len(calculateSourceDataFrame) < DI_Parameter:
        return None, None, None

    todayHighList = calculateSourceDataFrame[calculateSourceColumnName_TodayHigh].values
    todayLowList = calculateSourceDataFrame[calculateSourceColumnName_TodayLow].values
    previousHighList = calculateSourceDataFrame[calculateSourceColumnName_PreviousHigh].values
    previousLowList = calculateSourceDataFrame[calculateSourceColumnName_PreviousLow].values
    previousCloseList = calculateSourceDataFrame[calculateSourceColumnName_PreviousClose].values

    plusDM, minusDM = __GetDM(todayHighList, todayLowList, previousHighList, previousLowList)
    if plusDM is None or minusDM is None:
        return None, None, None

    trueRange = __GetTrueRange(todayHighList, todayLowList, previousHighList, previousLowList, previousCloseList)
    if trueRange is None:
        return None, None, None

    plusDI, minusDI = __GetDI(plusDM, minusDM, trueRange, DI_Parameter)
    if plusDI is None or minusDI is None:
        return None, None, None

    DXdataFrameColumnName = 'DX'
    DXdataFrame = __GetDX(plusDI, minusDI, DXdataFrameColumnName)
    if DXdataFrame is None:
        return None, None, None

    plusDIdataFrame = pd.DataFrame(np.array(plusDI), columns=[plusDIcolumnName])
    minusDIdataFrame = pd.DataFrame(np.array(minusDI), columns=[minusDIcolumnName])
    ADXdataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=DXdataFrame, calculate_parameter=ADX_Parameter, calculateSourceColumnName=DXdataFrameColumnName, returnDataFrameColumnName=ADXcolumnName)

    return plusDIdataFrame, minusDIdataFrame, ADXdataFrame

