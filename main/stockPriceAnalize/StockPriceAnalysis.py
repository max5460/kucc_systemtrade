from CommonConstant import (
                            CSVFILE_STORE_FOLDER_NAME,
                            CSVFILE_EXTENSION,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            PREVIOUS_DAYS_CONSTANT,
                            TOMORROW_PRICE_PREFIX,
                            TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST,
                            LSTM_INPUT_WINDOW_LENGTH
                           )
from CreateDataFrameForAnalysis import GetDataFrameForAnalysis
from LogMessage import StockPriceAnalysisMessage
import pandas as pd
from keras import metrics
from keras.models import Sequential
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from sklearn.preprocessing import StandardScaler
import glob
import os
from datetime import datetime
from logging import getLogger
logger = getLogger()


def __GetColumnsListForX():

    returnColumnList = []
    for technicalIndexColumnName in TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST:
        for idx in range(LSTM_INPUT_WINDOW_LENGTH, 0 - 1, -1):
            if idx == 0:
                returnColumnList.append(technicalIndexColumnName)
            else:
                returnColumnList.append(str(idx) + PREVIOUS_DAYS_CONSTANT + technicalIndexColumnName)

    return returnColumnList


def __GetReshapedNdArrayForX(ndArrayForX):

    shapeForLSTM = (ndArrayForX.shape[0], len(TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST), LSTM_INPUT_WINDOW_LENGTH + 1)

    return ndArrayForX.reshape(shapeForLSTM)


def __GetReshapedNdArrayForY(ndArrayForY, columnListForY):

    shapeForLSTM = (ndArrayForY.shape[0], len(columnListForY))

    return ndArrayForY.reshape(shapeForLSTM)


def __CreateScalerAndTransform(transformedNdArray):

    standardScaler = StandardScaler()
    standardScaler.fit(transformedNdArray)

    return standardScaler, standardScaler.transform(transformedNdArray)


def __GetTrainAndTestData(X, Y, divideRate):

    divideIndex = int(len(X) * divideRate)
    X_train = X[:divideIndex, :, :]
    X_test = X[divideIndex:, :, :]
    Y_train = Y[:divideIndex, :]
    Y_test = Y[divideIndex:, :]

    return X_train, X_test, Y_train, Y_test


def __CreateInformationForSummary():

    columnListForX = __GetColumnsListForX()
    columnListForY = [TOMORROW_PRICE_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_CLOSE]

    brandCodeList = []
    brandNameList = []
    trainingDataCountList = []
    dataFrameForX = pd.DataFrame(None, columns=columnListForX)
    dataFrameForY = pd.DataFrame(None, columns=columnListForY)
    dataFrameForPredict = pd.DataFrame(None, columns=columnListForX)

    for csvFile in glob.glob(CSVFILE_STORE_FOLDER_NAME + '//*' + CSVFILE_EXTENSION):
        dataFrameFromCSV = pd.read_csv(csvFile, encoding='UTF-8', engine='python')

        dataFrameForTraining = GetDataFrameForAnalysis(dataFrameFromCSV)
        if dataFrameForTraining is None:
            continue

        dataFrameForX = dataFrameForX.append(dataFrameForTraining[columnListForX].iloc[:-1])
        dataFrameForY = dataFrameForY.append(dataFrameForTraining[columnListForY].iloc[:-1])
        dataFrameForPredict = dataFrameForPredict.append(dataFrameForTraining[columnListForX].iloc[-1])

        csvFileName = os.path.splitext(os.path.basename(csvFile))[0]
        brandCodeAndName = csvFileName.split(maxsplit=1)

        if len(brandCodeAndName) == 2:
            brandCodeList.append(brandCodeAndName[0])
            brandNameList.append(brandCodeAndName[1])
        else:
            brandCodeList.append('')
            brandNameList.append('')

        logger.debug(StockPriceAnalysisMessage.addTrainingDataInformation % csvFileName)

        trainingDataCountList.append(len(dataFrameForX))

    X = __GetReshapedNdArrayForX(dataFrameForX.values)
    standardScalerForY, scaledY = __CreateScalerAndTransform(dataFrameForY.values)
    Y = __GetReshapedNdArrayForY(scaledY, columnListForY)
    ndArrayForPredict = __GetReshapedNdArrayForX(dataFrameForPredict.values)

    return X, Y, ndArrayForPredict, standardScalerForY, brandCodeList, brandNameList, trainingDataCountList


def __GetPredictModel(inputBatchSize, inputVectorDimension):
    predictModel = Sequential()
    predictModel.add(LSTM(100, activation='tanh', input_shape=(inputBatchSize, inputVectorDimension), recurrent_activation='hard_sigmoid'))
    predictModel.add(Dense(1))
    predictModel.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=[metrics.mae])

    return predictModel


def __CreatePredictModelAndFitting(X, Y):
    X_train, X_test, Y_train, Y_test = __GetTrainAndTestData(X, Y, divideRate=0.8)

    predictModel = __GetPredictModel(X.shape[0], X.shape[1])
    predictModel.fit(X_train, Y_train, epochs=100, batch_size=1, verbose=2)

    return predictModel


def GetPredictSummary():

    X, Y, ndArrayForPredict, standardScalerForY, brandCodeList, brandNameList, trainingDataCountList = __CreateInformationForSummary()
    predictModel = __CreatePredictModelAndFitting(X, Y)

    resultSummaryList = []

    for idx in range(ndArrayForPredict.shape[0]):
        predictResult = predictModel.predict(ndArrayForPredict[idx:idx + 1])
        predictResult = standardScalerForY.inverse_transform(predictResult)

        resultSummaryList.append([brandCodeList[idx], brandNameList[idx], predictResult[0][0], trainingDataCountList[idx], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    resultSummaryColumnList = ['BRAND_CODE', 'BRAND_DESC', 'PREDICTION', 'TRAINING_DATA_COUNT', 'PREDICT_DATE']

    return pd.DataFrame(resultSummaryList, columns=resultSummaryColumnList)
