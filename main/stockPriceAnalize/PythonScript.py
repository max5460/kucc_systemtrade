import StockPriceCSV
import StockPriceAnalysis
import ExecuteDb
import Logger
from logging import getLogger
import sys
from LogMessage import WarningMessage


if __name__ == "__main__":
    Logger.CreateLogger()
    logger = getLogger()

    logger.debug('Start CreateCSV')
    createCSVError = StockPriceCSV.ExportIndividualStockPrice()
    if createCSVError is not None:
        sys.exit(1)
    logger.debug('End CreateCSV')

    logger.debug('Start StockPriceAnalize')
    df = StockPriceAnalysis.GetPredictSummary()
    if df is None:
        logger.warning(WarningMessage.predictSummaryDataFrameError)
        sys.exit(1)
    logger.debug('End StockPriceAnalize')

    logger.debug('Start DataBaseUpdate')
    res = ExecuteDb.update_db(df)
    if res is not None:
        logger.warning(WarningMessage.dbUpdateError)
        sys.exit(1)
    logger.debug('End DataBaseUpdate')
