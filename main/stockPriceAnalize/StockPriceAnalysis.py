from CommonConstant import (
                            CSVFILE_STORE_FOLDER_NAME,
                            TECHNICAL_INDEX_COLUMN_NAME_CLOSE,
                            TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST,
                            PREVIOUS_COLUMN_PREFIX,
                            DIFFERENCE_COLUMN_SUFFIX
                           )
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from CreateDataFrameForAnalysis import GetDataFrameForAnalysis
from ModelImprovement import GetOptimalClassifier
import glob
import os

PRICE_MOVEMENT_TYPE_UP = '上昇'
PRICE_MOVEMENT_TYPE_DOWN = '下落'


def __GetPredictDataFrameByBrand(sourceDataFrame, brandName, returnDataFrameColumnList):
    dataFrameForTraining = GetDataFrameForAnalysis(sourceDataFrame)

    answer_label = []
    for idx in range(len(dataFrameForTraining) - 1):
        if dataFrameForTraining[TECHNICAL_INDEX_COLUMN_NAME_CLOSE][idx + 1] > dataFrameForTraining[TECHNICAL_INDEX_COLUMN_NAME_CLOSE][idx]:
            answer_label.append(PRICE_MOVEMENT_TYPE_UP)
        else:
            answer_label.append(PRICE_MOVEMENT_TYPE_DOWN)

    trainTargetColumnsList = [columnName for columnName in TRAINING_TECHNICAL_INDEX_COLUMN_NAME_LIST]

    for idx in range(len(dataFrameForTraining.columns)):
        columnName = dataFrameForTraining.columns[idx]
        if PREVIOUS_COLUMN_PREFIX in columnName:
            trainTargetColumnsList.append(columnName)

        if DIFFERENCE_COLUMN_SUFFIX in columnName:
            trainTargetColumnsList.append(columnName)

    X_train, X_test, y_train, y_test = train_test_split(dataFrameForTraining[trainTargetColumnsList].iloc[:-1].values, answer_label, train_size=0.8, test_size=0.2)

    # randomForestClassifier = GetOptimalClassifier(X_train, y_train)
    randomForestClassifier = RandomForestClassifier()
    randomForestClassifier.fit(X_train, y_train)

    y_predict = randomForestClassifier.predict(X_test)

    return_predict = randomForestClassifier.predict(dataFrameForTraining[trainTargetColumnsList].iloc[-1].values.reshape(-1, len(trainTargetColumnsList)))
    accuracy = accuracy_score(y_test, y_predict)
    trainingDataCount = len(dataFrameForTraining)

    resultList = np.array([brandName, return_predict[0], accuracy, trainingDataCount])
    return pd.DataFrame(resultList.reshape(-1, len(returnDataFrameColumnList)), columns=returnDataFrameColumnList)


def GetPredictSummary():

    predictSummaryDataFrame = pd.DataFrame(columns=['銘柄', '予測値動き', '正確度', 'テストデータ数'])

    for csvFile in glob.glob(CSVFILE_STORE_FOLDER_NAME + '//*.csv'):
        dataFrameFromCSV = pd.read_csv(csvFile, encoding='UTF-8', engine='python')

        csvFileName = os.path.splitext(os.path.basename(csvFile))[0]
        resultDataFrameByBrand = __GetPredictDataFrameByBrand(dataFrameFromCSV, csvFileName, predictSummaryDataFrame.columns)
        predictSummaryDataFrame = predictSummaryDataFrame.append(resultDataFrameByBrand)

    predictSummaryDataFrame = predictSummaryDataFrame.sort_values('正確度', ascending=False)
    predictSummaryDataFrame.reset_index(drop=True, inplace=True)

    return predictSummaryDataFrame


a = GetPredictSummary()