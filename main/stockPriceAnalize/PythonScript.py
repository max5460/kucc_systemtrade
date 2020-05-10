import StockPriceCSV
import StockPriceAnalysis

if __name__ == "__main__":
   #create_r = StockPriceCSV.ExportIndividualStockPrice()
   #print('CreateCSV LOG')
   #print(create_r)
   analysis_r = StockPriceAnalysis.GetPredictSummary()
   print('AnalyzeCSV LOG')
   print(analysis_r)
   print("END")

