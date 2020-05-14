import pyodbc
from datetime import datetime

def __login():

    instance = "systemtrade.cztijmkhdo19.us-east-2.rds.amazonaws.com,1433"
    user = "admin"
    pasword = "v7JYRrWx"
    db = "systemTrade"
    connection = "DRIVER={SQL Server};SERVER=" + instance + ";uid=" + user + ";pwd=" + pasword + ";DATABASE=" + db

    return pyodbc.connect(connection)


def __update_execute(con,df):

    cursor = con.cursor()
    for index,item in df.iterrows():
       try:
          select = """SELECT 1 
                      FROM   PREDICT_RESULT 
                      WHERE  BRAND_CODE = '""" + str(df.at[index,'BRAND_CODE']) + """'"""
          cursor.execute(select)
          rows = cursor.fetchval()
          #print(rows)

          if rows != 1:
             values = "(N'" + str(df.at[index,'BRAND_CODE']) + "'),(N'" + str(df.at[index,'BRAND_DESC']) + "'),(N'" + str(df.at[index,'PREDICTION']) + "')," + \
                      str(df.at[index,'ACCURACY']) + "," + str(df.at[index,'TRAINING_DATA_COUNT']) + ",'" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

             sql = """INSERT
                      INTO PREDICT_RESULT(
                                          BRAND_CODE,
                                          BRAND_DESC,
                                          PREDICTION,
                                          ACCURACY,
                                          TRAINING_DATA_COUNT,
                                          PREDICT_DATE
                                         )
                      VALUES (""" + values + """)"""
             cursor.execute(sql)
             con.commit()

          else:
             values = "PREDICTION = (N'" + str(df.at[index,'PREDICTION']) + "'),ACCURACY = " + str(df.at[index,'ACCURACY']) + \
                      ",TRAINING_DATA_COUNT = " + str(df.at[index,'TRAINING_DATA_COUNT']) + ",PREDICT_DATE = '" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

             sql = """UPDATE PREDICT_RESULT 
                      SET """ + values + """ 
                      WHERE BRAND_CODE = '""" + str(df.at[index,'BRAND_CODE']) + """'"""
             cursor.execute(sql)
             con.commit()

       except Exception as ex:
           cursor.close()
           print(ex)

    cursor.close()
    return "FINISH"

def update_db(dataFrame):
    con = __login()
    res = __update_execute(con,dataFrame)
    
    return res
