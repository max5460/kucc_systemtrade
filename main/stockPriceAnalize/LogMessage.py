class WarningMessage:
    predictSummaryDataFrameError = '株価予測集計DataFrameが空です。処理を終了します。'
    dbUpdateError = 'データベースが正常に更新できませんでした。処理を終了します。'


class CreateDataFrameAnalysisMessage:
    sourceDataFrameError = '分析元DataFrameが空です。'
    decimalizeError = '分析元DataFrameにDecimal化できないカラムがあります。'
    technicalIndexDataFrameError = 'テクニカル分析DataFrameに欠損があります。'
    previousDayDataFrameError = '前日DataFrameの作成に失敗しました。'
    differenceDataFrameError = '当日数値と前日数値の差分DataFrameの作成に失敗しました。'
    DMIandADXDataFrameError = 'DMI、あるいはADXのDataFrameに欠損があります。'


class ExecuteDBMessage:
    connectDBError = 'SQLServerへの接続に失敗しました。'
    dbUpdateError = 'テーブルの更新に失敗。トランザクションをロールバックしました。'


class StockPriceAnalysisMessage:
    beginDataTraining = '%sの株価データ分析を開始します。'
    finishDataTraining = '%sの株価データ分析が完了しました。'


class StockPriceCSVMessage:
    scrapingError = '株価データのスクレイピングに失敗しました。'
    
    
class TechnicalIndexMessage:
    sourceDataFrameError_EMA = 'EMA計算元のDataFrameが空です。'
    calculateParameterError_EMA = '計算用パラメータがEMA計算元DataFrameの長さを超えています。'
    calculateSourceColumnError_EMA = 'EMA計算元DataFrame内に、計算用のカラムがありません。 指定されたカラム名:%s'

    baseLineAndRelativeLineParameterError_MACD = 'MACDの基準線パラメータが相対線パラメータを超えています。'
    sourceDataFrameError_MACD = 'MACD計算元のDataFrameが空です。'
    calculateParameterError_MACD = 'MACD計算元DataFrameの長さが計算用パラメータより短いです。'
    calculateSourceColumnError_MACD = 'MACD計算元DataFrame内に、計算用のカラムがありません。 指定されたカラム名:%s'
    baseLineDataFrameError_MACD = 'MACD計算用の基準線DataFrameが空です。'
    relativeLineDataFrameError_MACD = 'MACD計算用の相対線DataFrameが空です。'
    MACDcalculateError_MACD = 'MACDの計算に失敗しました。'

    sourceDataFrameError_DMIandADX = 'DMI、ADX計算元のDataFrameが空です。'
    calculateParameterError_DMIandADX = '計算用パラメータがDMI、ADX計算元DataFrameの長さを超えています。'
    calculateSourceColumnError_DMIandADX = 'DMI、ADX計算元DataFrame内に、計算用のカラムがありません。 指定されたカラム名:%s'
    calculateDMError_DMIandADX = 'DMの計算に失敗しました。'
    calculateTrueRangeError_DMIandADX = 'トゥルーレンジの計算に失敗しました。'
    calculateDIError_DMIandADX = 'DIの計算に失敗しました。'
    calculateDXError_DMIandADX = 'DXの計算に失敗しました。'





