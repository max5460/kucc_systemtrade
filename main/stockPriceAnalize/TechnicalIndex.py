import pandas as pd
import numpy as np
from statistics import mean
from math import fabs
from decimal import Decimal
from LogMessage import TechnicalIndexMessage
from logging import getLogger
logger = getLogger()


def GetExponentialMovingAverage(calculateSourceDataFrame, calculate_parameter, calculateSourceColumnName, returnDataFrameColumnName):

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        logger.info(TechnicalIndexMessage.sourceDataFrameError_EMA)
        return None

    if len(calculateSourceDataFrame) < calculate_parameter:
        logger.info(TechnicalIndexMessage.calculateParameterError_EMA)
        return None

    if calculateSourceColumnName not in calculateSourceDataFrame:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_EMA % calculateSourceColumnName)
        return None

    calculateSourceData = calculateSourceDataFrame[calculateSourceColumnName].values
    EMA_Ndarray = np.empty((len(calculateSourceDataFrame)), dtype=Decimal)

    firstEMA = mean(calculateSourceData[0:calculate_parameter])
    EMA_Ndarray[calculate_parameter - 1] = firstEMA

    smoothingExponential = 2 / (calculate_parameter + 1)
    smoothingExponential = Decimal(str(smoothingExponential))

    for idx in range(calculate_parameter, len(calculateSourceData)):
        before_EMA = EMA_Ndarray[idx - 1]
        current_Amount = before_EMA + smoothingExponential * (calculateSourceData[idx] - before_EMA)
        EMA_Ndarray[idx] = current_Amount

    return pd.DataFrame(EMA_Ndarray, columns=[returnDataFrameColumnName], index=calculateSourceDataFrame.index)


def GetMACD(calculateSourceDataFrame, calculateSourceColumnName, baseLine_parameter, relativeLine_parameter, signal_parameter, MACDDataFrameColumnName, signalDataFrameColumnName):

    if baseLine_parameter > relativeLine_parameter:
        logger.info(TechnicalIndexMessage.baseLineAndRelativeLineParameterError_MACD)
        return None, None

    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        logger.info(TechnicalIndexMessage.sourceDataFrameError_MACD)
        return None, None

    if calculateSourceColumnName not in calculateSourceDataFrame.columns:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_MACD % calculateSourceColumnName)
        return None, None

    baseLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=baseLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='基準線')
    relativeLineDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=calculateSourceDataFrame, calculate_parameter=relativeLine_parameter, calculateSourceColumnName=calculateSourceColumnName, returnDataFrameColumnName='相対線')

    if baseLineDataFrame is None or len(baseLineDataFrame) == 0:
        logger.info(TechnicalIndexMessage.baseLineDataFrameError_MACD)
        return None, None

    if relativeLineDataFrame is None or len(relativeLineDataFrame) == 0:
        logger.info(TechnicalIndexMessage.relativeLineDataFrameError_MACD)
        return None, None

    baseLineNdarray = baseLineDataFrame.values.reshape(len(baseLineDataFrame))
    relativeLineNdarray = relativeLineDataFrame.values.reshape(len(relativeLineDataFrame))

    MACD_NdArray = np.empty(len(baseLineDataFrame), dtype=Decimal)

    for idx in range(relativeLine_parameter - 1, len(relativeLineNdarray)):
        MACD_NdArray[idx] = baseLineNdarray[idx] - relativeLineNdarray[idx]

    MACD_DataFrame = pd.DataFrame(MACD_NdArray, columns=[MACDDataFrameColumnName], index=calculateSourceDataFrame.index)
    signalDataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=MACD_DataFrame.dropna(), calculate_parameter=signal_parameter, calculateSourceColumnName=MACDDataFrameColumnName, returnDataFrameColumnName=signalDataFrameColumnName)

    return MACD_DataFrame, signalDataFrame


def GetDMIandADX(calculateSourceDataFrame, calculateSourceColumnName_TodayHigh, calculateSourceColumnName_TodayLow,
                 calculateSourceColumnName_PreviousHigh, calculateSourceColumnName_PreviousLow, calculateSourceColumnName_PreviousClose,
                 plusDIcolumnName, minusDIcolumnName, DI_Parameter, ADX_Parameter, ADXcolumnName):

    def __GetDM(todayHigh, todayLow, previousHigh, previousLow):

        if len(todayHigh) != len(todayLow) != len(previousHigh) != len(previousLow):
            return None, None

        calculateLength = len(todayHigh)

        temporaryPlusDM = np.array([todayHigh[idx] - previousHigh[idx] for idx in range(calculateLength)])
        temporaryMinusDM = np.array([previousLow[idx] - todayLow[idx] for idx in range(calculateLength)])

        for idx in range(calculateLength):
            if temporaryPlusDM[idx] < 0 and temporaryMinusDM[idx] < 0:
                temporaryPlusDM[idx] = 0
                temporaryMinusDM[idx] = 0
                continue

            if temporaryPlusDM[idx] > temporaryMinusDM[idx]:
                temporaryPlusDM[idx] = todayHigh[idx] - previousHigh[idx]
                temporaryMinusDM[idx] = 0
                continue

            if temporaryPlusDM[idx] < temporaryMinusDM[idx]:
                temporaryPlusDM[idx] = 0
                temporaryMinusDM[idx] = previousLow[idx] - todayLow[idx]
                continue

            if temporaryPlusDM[idx] == temporaryMinusDM[idx]:
                temporaryPlusDM[idx] = 0
                temporaryMinusDM[idx] = 0
                continue

        return temporaryPlusDM, temporaryMinusDM


    def __GetTrueRange(todayHigh, todayLow, previousHigh, previousLow, previousClose):

        if len(todayHigh) != len(todayLow) != len(previousHigh) != len(previousLow) != len(previousClose):
            return None

        calculateLength = len(todayHigh)
        trueRangeList = []
        for idx in range(calculateLength):
            trueRangeCandidate_1 = fabs(todayHigh[idx] - todayLow[idx])
            trueRangeCandidate_2 = fabs(todayHigh[idx] - previousClose[idx])
            trueRangeCandidate_3 = fabs(previousClose[idx] - todayLow[idx])
            trueRangeList.append(Decimal(str(max(trueRangeCandidate_1, trueRangeCandidate_2, trueRangeCandidate_3))))

        return np.array(trueRangeList)


    def __GetDI(_plusDM, _minusDM, _trueRange, _DI_Parameter):

        if len(_plusDM) != len(_minusDM) != len(_trueRange):
            return None, None

        calculateLength = len(_plusDM)

        if calculateLength < _DI_Parameter:
            return None, None

        plusDI_Ndarray = np.empty(len(_plusDM), dtype=Decimal)
        minusDI_Ndarray = np.empty(len(_minusDM), dtype=Decimal)
        for idx in range(calculateLength - _DI_Parameter + 1):
            denominator = sum(_trueRange[idx:_DI_Parameter + idx])
            if denominator != Decimal('0'):
                plusDI_Ndarray[_DI_Parameter - 1 + idx] = sum(_plusDM[idx:_DI_Parameter + idx]) / denominator * 100
                minusDI_Ndarray[_DI_Parameter - 1 + idx] = sum(_minusDM[idx:_DI_Parameter + idx]) / denominator * 100
            else:
                plusDI_Ndarray[_DI_Parameter - 1 + idx] = Decimal('0')
                minusDI_Ndarray[_DI_Parameter - 1 + idx] = Decimal('0')

        return plusDI_Ndarray, minusDI_Ndarray


    def __GetDX(_plusDI, _minusDI, _DXdataFrameColumnName, _DI_Parameter, returnDataFrameIndex):

        if len(_plusDI) != len(_minusDI):
            return None

        calculateLength = len(_plusDI)

        DX_Ndarray = np.empty(calculateLength, dtype=Decimal)

        for idx in range(_DI_Parameter - 1, calculateLength):
            denominator = (_plusDI[idx] + _minusDI[idx])
            if denominator != Decimal('0'):
                DX_Ndarray[idx] = Decimal(str(fabs(_plusDI[idx] - _minusDI[idx]))) / denominator * 100
            else:
                DX_Ndarray[idx] = Decimal('0')

        return pd.DataFrame(DX_Ndarray, columns=[_DXdataFrameColumnName], index=returnDataFrameIndex)


    if calculateSourceDataFrame is None or len(calculateSourceDataFrame) == 0:
        logger.info(TechnicalIndexMessage.sourceDataFrameError_DMIandADX)
        return None, None, None

    if calculateSourceColumnName_TodayHigh not in calculateSourceDataFrame.columns:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_DMIandADX % calculateSourceColumnName_TodayHigh)
        return None, None, None

    if calculateSourceColumnName_TodayLow not in calculateSourceDataFrame.columns:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_DMIandADX % calculateSourceColumnName_TodayLow)
        return None, None, None

    if calculateSourceColumnName_PreviousHigh not in calculateSourceDataFrame.columns:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_DMIandADX % calculateSourceColumnName_PreviousHigh)
        return None, None, None

    if calculateSourceColumnName_PreviousLow not in calculateSourceDataFrame.columns:
        logger.info(TechnicalIndexMessage.calculateSourceColumnError_DMIandADX % calculateSourceColumnName_PreviousLow)
        return None, None, None

    if len(calculateSourceDataFrame) < DI_Parameter:
        logger.info(TechnicalIndexMessage.calculateParameterError_DMIandADX)
        return None, None, None

    todayHighList = calculateSourceDataFrame[calculateSourceColumnName_TodayHigh].values
    todayLowList = calculateSourceDataFrame[calculateSourceColumnName_TodayLow].values
    previousHighList = calculateSourceDataFrame[calculateSourceColumnName_PreviousHigh].values
    previousLowList = calculateSourceDataFrame[calculateSourceColumnName_PreviousLow].values
    previousCloseList = calculateSourceDataFrame[calculateSourceColumnName_PreviousClose].values

    plusDM, minusDM = __GetDM(todayHighList, todayLowList, previousHighList, previousLowList)
    if plusDM is None or minusDM is None:
        logger.info(TechnicalIndexMessage.calculateDMError_DMIandADX)
        return None, None, None

    trueRange = __GetTrueRange(todayHighList, todayLowList, previousHighList, previousLowList, previousCloseList)
    if trueRange is None:
        logger.info(TechnicalIndexMessage.calculateTrueRangeError_DMIandADX)
        return None, None, None

    plusDI, minusDI = __GetDI(plusDM, minusDM, trueRange, DI_Parameter)
    if plusDI is None or minusDI is None:
        logger.info(TechnicalIndexMessage.calculateDIError_DMIandADX)
        return None, None, None

    DXdataFrameColumnName = 'DX'
    calculateSourceDataFrameIndex = calculateSourceDataFrame.index
    DXdataFrame = __GetDX(plusDI, minusDI, DXdataFrameColumnName, DI_Parameter, calculateSourceDataFrameIndex)
    if DXdataFrame is None:
        logger.info(TechnicalIndexMessage.calculateDXError_DMIandADX)
        return None, None, None

    plusDIdataFrame = pd.DataFrame(np.array(plusDI), columns=[plusDIcolumnName], index=calculateSourceDataFrameIndex)
    minusDIdataFrame = pd.DataFrame(np.array(minusDI), columns=[minusDIcolumnName], index=calculateSourceDataFrameIndex)
    ADXdataFrame = GetExponentialMovingAverage(calculateSourceDataFrame=DXdataFrame.dropna(), calculate_parameter=ADX_Parameter, calculateSourceColumnName=DXdataFrameColumnName, returnDataFrameColumnName=ADXcolumnName)

    return plusDIdataFrame, minusDIdataFrame, ADXdataFrame

