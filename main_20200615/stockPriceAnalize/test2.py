import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense,  LSTM
from keras import metrics
from sklearn.preprocessing import MinMaxScaler
from CommonConstant import TECHNICAL_INDEX_COLUMN_NAME_CLOSE, TECHNICAL_INDEX_COLUMN_NAME_OPEN, TECHNICAL_INDEX_COLUMN_NAME_LOW, TECHNICAL_INDEX_COLUMN_NAME_HIGH, CSVFILE_EXTENSION, CSVFILE_STORE_FOLDER_NAME


df = pd.read_csv(CSVFILE_STORE_FOLDER_NAME + '//1301 (株)極洋' + CSVFILE_EXTENSION, encoding='utf-8')
df = df[df['日付'] >= '2016-09-28']
L = len(df)
Hi = np.array([df[TECHNICAL_INDEX_COLUMN_NAME_HIGH]])
Low = np.array([df[TECHNICAL_INDEX_COLUMN_NAME_LOW]])
Close = np.array([df[TECHNICAL_INDEX_COLUMN_NAME_CLOSE]])
# 入力データ、出力データ作成
Hi = Hi.reshape(-1, 1)  # 行列に変換する。（配列の要素数行×1列）
Low = Low.reshape(-1, 1)  # 行列に変換する。（配列の要素数行×1列）
Close = Close.reshape(-1, 1)  # 行列に変換する。（配列の要素数行×1列）
Hi1 = Hi[0:L-3, :]  # 予測対象日の3日前のデータ
Low1 = Low[0:L-3, :]  # 予測対象日の3日前のデータ
Close1 = Close[0:L-3, :]  # 予測対象日の3日前のデータ
Hi2 = Hi[1:L-2, :]  # 予測対象日の2日前のデータ
Low2 = Low[1:L-2, :]  # 予測対象日の2日前のデータ
Close2 = Close[1:L-2, :]  # 予測対象日の2日前のデータ
Hi3 = Hi[2:L-1, :]  # 予測対象日の前日データ
Low3 = Low[2:L-1, :]  # 予測対象日の前日のデータ
Close3 = Close[2:L-1, :]  # 予測対象日の前日のデータ
X = np.concatenate([Low1, Hi1, Close1, Low2, Hi2, Close2, Low3, Hi3, Close3], axis=1)
Y = Close[3:L, :]  # 予測対象日のデータ
scaler = MinMaxScaler()
scaler.fit(X)
X = scaler.transform(X)
scaler1 = MinMaxScaler()
scaler1.fit(Y)
Y = scaler1.transform(Y)
X = np.reshape(X, (X.shape[0], 1, X.shape[1]))
print(X.shape)
# X_train = X[:190, :, :]
# X_test = X[190:, :, :]
# Y_train = Y[:190, :]
# Y_test = Y[190:, :]
X_train = X[:-1, :, :]
X_test = X[-1, :, :]
Y_train = Y[:-1, :]
Y_test = Y[-1, :]

X_test = X_test.reshape(1, 1, 9)
model = Sequential()
model.add(LSTM(100, activation='tanh', input_shape=(X_train.shape[1], X_train.shape[2]), recurrent_activation='hard_sigmoid'))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=[metrics.mae])
model.fit(X_train, Y_train, epochs=100, batch_size=1, verbose=2)

Predict = model.predict(X_test, verbose=1)
# オリジナルのスケールに戻す、タイムインデックスを付ける。
Y_train = scaler1.inverse_transform(Y_train)
Y_train = pd.DataFrame(Y_train)
# Y_train.index = pd.to_datetime(df.iloc[3:193, 0])
Y_test = scaler1.inverse_transform(Y_test.reshape(1, 1))
Y_test = pd.DataFrame(Y_test)
# Y_test.index = pd.to_datetime(df.iloc[193:, 0])
Predict = scaler1.inverse_transform(Predict)
Predict = pd.DataFrame(Predict)
# Predict.index = pd.to_datetime(df.iloc[193:, 0])

plt.figure(figsize=(15, 10))
plt.plot(Y_test, label='Test')
plt.plot(Predict, label='Prediction')
plt.legend(loc='best')
plt.show()
