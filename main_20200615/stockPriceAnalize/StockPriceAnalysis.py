from CommonConstant import (
                            CSVFILE_STORE_FOLDER_NAME,
                            CSVFILE_EXTENSION,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE_ADJUSTMENT,
                            CLOSE_PRICE_COUNT_IN_A_ROW
                           )
import numpy as np
import pandas as pd
from keras import metrics
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from CreateDataFrameForAnalysis import GetSeveralDaysClosePriceDataFrame, GetDataFrameForAnalysis, GetSeveralDaysClosePriceDataFrame2
import glob
import os
from datetime import datetime
from logging import getLogger
logger = getLogger()


def __GetPredictModel(inputBatchSize, inputVectorDimension):
    predictModel = Sequential()
    predictModel.add(LSTM(100, activation='tanh', input_shape=(inputBatchSize, inputVectorDimension), recurrent_activation='hard_sigmoid'))
    predictModel.add(Dense(1))
    predictModel.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=[metrics.mae])

    return predictModel


def GetPredictSummary():

    trainTargetColumnsList = [TECHNICAL_INDEX_COLUMN_NAME_CLOSE]
    for idx in range(1, CLOSE_PRICE_COUNT_IN_A_ROW + 1):
        trainTargetColumnsList.append(str(idx) + '日前' + TECHNICAL_INDEX_COLUMN_NAME_CLOSE)

    csvFileNameList = []
    trainingDataCountList = []
    dataFrameForX = pd.DataFrame(None, columns=trainTargetColumnsList)
    dataFrameForY = pd.DataFrame(None, columns=[TECHNICAL_INDEX_COLUMN_NAME_CLOSE])
    dataFrameForPredict = pd.DataFrame(None)
    # predictModel = __GetPredictModel(1, CLOSE_PRICE_COUNT_IN_A_ROW + 1)
    predictModel = load_model('test.h5')
    standardScalerForY = MinMaxScaler()

    for csvFile in glob.glob(CSVFILE_STORE_FOLDER_NAME + '//*' + CSVFILE_EXTENSION):
        dataFrameFromCSV = pd.read_csv(csvFile, encoding='UTF-8', engine='python')

        test = GetDataFrameForAnalysis(dataFrameFromCSV)
        test = GetSeveralDaysClosePriceDataFrame2(test)

        severalDaysClosePriceDataFrame = GetSeveralDaysClosePriceDataFrame(dataFrameFromCSV)
        if severalDaysClosePriceDataFrame is None:
            continue

        dataFrameForX = dataFrameForX.append(severalDaysClosePriceDataFrame[trainTargetColumnsList].iloc[:-1])
        temporarySeriesForY = dataFrameFromCSV[[TECHNICAL_INDEX_COLUMN_NAME_CLOSE]].iloc[CLOSE_PRICE_COUNT_IN_A_ROW:-1]
        dataFrameForY = dataFrameForY.append(temporarySeriesForY)
        temporarySeriesForPredict = severalDaysClosePriceDataFrame[trainTargetColumnsList].iloc[-1]
        dataFrameForPredict = dataFrameForPredict.append(pd.DataFrame([temporarySeriesForPredict]))

        csvFileName = os.path.splitext(os.path.basename(csvFile))[0]
        csvFileNameList.append(csvFileName)
        logger.debug(csvFileName + 'の分析・フィッティングを開始')

        trainingDataCountList.append(len(severalDaysClosePriceDataFrame) - 1)

    dataFrameForX.reset_index(drop=True, inplace=True)
    dataFrameForY.reset_index(drop=True, inplace=True)
    dataFrameForPredict.reset_index(drop=True, inplace=True)

    X = dataFrameForX.values
    standardScalerForX = MinMaxScaler()
    standardizedX = standardScalerForX.fit_transform(X)
    X_train = standardizedX.reshape(X.shape[0], 1, X.shape[1])

    Y = dataFrameForY.values
    reshapedY = Y.reshape(Y.shape[0], 1)
    Y_train = standardScalerForY.fit_transform(reshapedY)

    # predictModel.fit(X_train, Y_train, epochs=100, batch_size=1, verbose=2)

    standardizedDataForPredict = standardScalerForX.fit_transform(dataFrameForPredict.values)
    arrayForPredict = standardizedDataForPredict.reshape(standardizedDataForPredict.shape[0], X_train.shape[1], X_train.shape[2])

    predictSummaryDataFrame = pd.DataFrame(columns=['BRAND_CODE', 'BRAND_DESC', 'PREDICTION', 'TRAINING_DATA_COUNT', 'PREDICT_DATE'])
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for idx in range(len(csvFileNameList)):
        BrandCodeAndName = csvFileNameList[idx].split(maxsplit=1)
        brandCode = ''
        brandName = ''

        if len(BrandCodeAndName) == 2:
            brandCode = BrandCodeAndName[0]
            brandName = BrandCodeAndName[1]

        predictResult = predictModel.predict(arrayForPredict[idx].reshape(1, 1, arrayForPredict.shape[2]))
        predictResult = standardScalerForY.inverse_transform(predictResult)

        predictSummaryDataFrame = predictSummaryDataFrame.append(pd.DataFrame([[brandCode, brandName, predictResult[0][0], trainingDataCountList[idx], current_time]], columns=predictSummaryDataFrame.columns))


    return predictSummaryDataFrame
