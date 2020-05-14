import StockPriceCSV
import StockPriceAnalysis
import ExecuteDb

if __name__ == "__main__":
   #log = StockPriceCSV.ExportIndividualStockPrice()
   #print('CreateCSV LOG')
   #print(log)
   df = StockPriceAnalysis.GetPredictSummary()
   print('AnalyzeCSV LOG')
   res = ExecuteDb.update_db(df)
   print(res)
   print("END")

