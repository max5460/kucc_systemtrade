from CommonConstant import (
                            CSVFILE_STORE_FOLDER_NAME,
                            CSVFILE_EXTENSION,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            PREVIOUS_DAYS_CONSTANT,
                            TOMORROW_PRICE_PREFIX,
                            TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST,
                            LSTM_INPUT_WINDOW_LENGTH,
                            PREDICT_MODEL_STORE_FOLDER_NAME
                           )
from CreateDataFrameForAnalysis import GetDataFrameForAnalysis
from LogMessage import StockPriceAnalysisMessage
import pandas as pd
from keras import metrics
from keras.models import Sequential, load_model
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
        for idx in range(LSTM_INPUT_WINDOW_LENGTH - 1, 0 - 1, -1):
            if idx == 0:
                returnColumnList.append(technicalIndexColumnName)
            else:
                returnColumnList.append(str(idx) + PREVIOUS_DAYS_CONSTANT + technicalIndexColumnName)

    return returnColumnList


def __GetReshapedNdArrayForX(ndArrayForX):

    shapeForLSTM = (-1, LSTM_INPUT_WINDOW_LENGTH, len(TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST))

    return ndArrayForX.reshape(shapeForLSTM)


def __GetReshapedNdArrayForY(ndArrayForY, columnListForY):

    shapeForLSTM = (-1, len(columnListForY))

    return ndArrayForY.reshape(shapeForLSTM)


def __CreateScalerAndTransform(transformedNdArray):

    standardScaler = StandardScaler()
    standardScaler.fit(transformedNdArray)

    return standardScaler, standardScaler.transform(transformedNdArray)


def __GetBrandCodeAndName(csvFile):
    csvFileName = os.path.splitext(os.path.basename(csvFile))[0]
    brandCodeAndName = csvFileName.split(maxsplit=1)

    if len(brandCodeAndName) == 2:
        return brandCodeAndName[0], brandCodeAndName[1]
    else:
        return brandCodeAndName, ''


def __CreatePredictModelAndFitting(brandCode, X, Y):

    modelFileName = PREDICT_MODEL_STORE_FOLDER_NAME + '//' + brandCode + '.h5'
    if os.path.isfile(modelFileName):
        predictModel = load_model(modelFileName)
        predictModel.fit(X[X.shape[0] - 1:X.shape[0]], Y[Y.shape[0] - 1:Y.shape[0]], epochs=30, batch_size=1, verbose=2)
    else:
        predictModel = Sequential()
        predictModel.add(LSTM(100, activation='tanh', input_shape=(X.shape[1], X.shape[2]), recurrent_activation='hard_sigmoid'))
        predictModel.add(Dense(1))
        predictModel.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=[metrics.mae])
        predictModel.fit(X, Y, epochs=30, batch_size=1, verbose=2)

    predictModel.save(modelFileName)
    return predictModel


def GetPredictSummary():

    resultSummaryList = []

    columnListForX = __GetColumnsListForX()
    columnListForY = [TOMORROW_PRICE_PREFIX + TECHNICAL_INDEX_COLUMN_NAME_CLOSE]

    for csvFile in glob.glob(CSVFILE_STORE_FOLDER_NAME + '//*' + CSVFILE_EXTENSION):
        dataFrameFromCSV = pd.read_csv(csvFile, encoding='UTF-8', engine='python')

        dataFrameForTraining = GetDataFrameForAnalysis(dataFrameFromCSV)
        if dataFrameForTraining is None:
            continue

        brandCode, brandName = __GetBrandCodeAndName(csvFile)
        logger.debug(StockPriceAnalysisMessage.beginDataTraining % brandCode + brandName)

        X = __GetReshapedNdArrayForX(dataFrameForTraining[columnListForX].iloc[:-1].values)
        standardScalerForY, scaledY = __CreateScalerAndTransform(dataFrameForTraining[columnListForY].iloc[:-1].values)
        Y = __GetReshapedNdArrayForY(scaledY, columnListForY)
        ndArrayForPredict = __GetReshapedNdArrayForX(dataFrameForTraining[columnListForX].iloc[-1].values)

        predictModel = __CreatePredictModelAndFitting(brandCode, X, Y)
        predictResult = predictModel.predict(ndArrayForPredict[0:1])
        predictResult = standardScalerForY.inverse_transform(predictResult)[0][0]

        resultSummaryList.append([brandCode, brandName, predictResult, X.shape[0], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        logger.debug(StockPriceAnalysisMessage.finishDataTraining % brandCode + brandName)

    resultSummaryColumnList = ['BRAND_CODE', 'BRAND_DESC', 'PREDICTION', 'TRAINING_DATA_COUNT', 'PREDICT_DATE']
    return pd.DataFrame(resultSummaryList, columns=resultSummaryColumnList)
