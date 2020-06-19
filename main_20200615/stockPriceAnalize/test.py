from CommonConstant import TECHNICAL_INDEX_COLUMN_NAME_OPEN, DROP_COLUMN_NAME_DATE, CSVFILE_STORE_FOLDER_NAME
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.layers import LSTM
from keras.layers import Dropout


window_len = 10


def data_maker(data):
    data_lstm_in = []

    if len(data) == window_len:
        temp = data[:window_len].copy()
        temp = temp / temp.iloc[0] - 1
        data_lstm_in.append(temp)

    for i in range(len(data) - window_len):
        temp = data[i:(i + window_len)].copy()
        temp = temp / temp.iloc[0] - 1
        data_lstm_in.append(temp)

    return data_lstm_in


def pd_to_np(data_lstm_in):
    data_lstm_in = [np.array(data_lstm_input) for data_lstm_input in data_lstm_in]  # array のリスト
    data_lstm_in = np.array(data_lstm_in)  # np.array

    return data_lstm_in


def build_model(inputs, output_size, neurons, active_func="linear", dropout=0.25, loss="mae", optimizer="adam"):
    model = Sequential()

    model.add(LSTM(neurons, input_shape=(inputs.shape[1], inputs.shape[2])))
    model.add(Dropout(dropout))
    model.add(Dense(units=output_size))
    model.add(Activation(active_func))

    model.compile(loss=loss, optimizer=optimizer)
    return model


df = pd.read_csv(CSVFILE_STORE_FOLDER_NAME + '//' + '1301 (株)極洋.csv')

split_date = '2013-06-05'
train = df[df[DROP_COLUMN_NAME_DATE] < split_date].copy()
test = df[df[DROP_COLUMN_NAME_DATE] >= split_date].copy()
latest = test[:window_len].copy()

train.drop(DROP_COLUMN_NAME_DATE, axis=1, inplace=True)
test.drop(DROP_COLUMN_NAME_DATE, axis=1, inplace=True)
latest.drop(DROP_COLUMN_NAME_DATE, axis=1, inplace=True)

length = len(test) - window_len

train_lstm_in = data_maker(train)
lstm_train_out = (train[TECHNICAL_INDEX_COLUMN_NAME_OPEN][window_len:].values / train[TECHNICAL_INDEX_COLUMN_NAME_OPEN][:-window_len].values) - 1
test_lstm_in = data_maker(test)
lstm_test_out = (test[TECHNICAL_INDEX_COLUMN_NAME_OPEN][window_len:].values / test[TECHNICAL_INDEX_COLUMN_NAME_OPEN][:-window_len].values) - 1
latest_lstm_in = data_maker(latest)

train_lstm_in = pd_to_np(train_lstm_in)
test_lstm_in = pd_to_np(test_lstm_in)
latest_lstm_in = pd_to_np(latest_lstm_in)

# ランダムシードの設定
np.random.seed(202)

# 初期モデルの構築
yen_model = build_model(train_lstm_in, output_size=1, neurons=20)

# データを流してフィッティングさせましょう
yen_history = yen_model.fit(train_lstm_in, lstm_train_out, epochs=10, batch_size=1, verbose=2, shuffle=True)

empty = []
future_array = np.array(empty)
for i in range(length):
    pred = (((np.transpose(yen_model.predict(latest_lstm_in)) + 1) * latest[TECHNICAL_INDEX_COLUMN_NAME_OPEN].values[0])[0])[0]
    future_array = np.append(future_array, pred)
    data = {TECHNICAL_INDEX_COLUMN_NAME_OPEN: [pred]}
    df1 = pd.DataFrame(data)
    latest = pd.concat([latest, df1], axis=0)
    latest.index = range(0, window_len + 1)
    latest = latest.drop(0, axis=0)
    latest_lstm_in = pd_to_np(latest_lstm_in)


plt.figure(figsize=(10, 8))
plt.plot(df[df[DROP_COLUMN_NAME_DATE] < split_date][DROP_COLUMN_NAME_DATE][window_len:], train[TECHNICAL_INDEX_COLUMN_NAME_OPEN][window_len:], label='Actual', color='blue')
plt.plot(df[df[DROP_COLUMN_NAME_DATE] < split_date][DROP_COLUMN_NAME_DATE][window_len:], ((np.transpose(yen_model.predict(train_lstm_in)) + 1) * train[TECHNICAL_INDEX_COLUMN_NAME_OPEN].values[:-window_len])[0],
         label='Predicted', color='red')
plt.show()

plt.figure(figsize=(10,8))
plt.plot(df[df[DROP_COLUMN_NAME_DATE] >= split_date][DROP_COLUMN_NAME_DATE][window_len:], test[TECHNICAL_INDEX_COLUMN_NAME_OPEN][window_len:], label='Actual', color='blue')
plt.plot(df[df[DROP_COLUMN_NAME_DATE] >= split_date][DROP_COLUMN_NAME_DATE][window_len:], future_array, label='future', color='green')
plt.show()
