from CommonConstant import DBConnectionINIFile
from configparser import ConfigParser
import sqlalchemy


def __login():

    configParser = ConfigParser()
    configParser.read(DBConnectionINIFile)

    instance = configParser['DBConnectionInformation']['serverName']
    port = configParser['DBConnectionInformation']['port']
    user = configParser['DBConnectionInformation']['user']
    password = configParser['DBConnectionInformation']['password']
    db = configParser['DBConnectionInformation']['DBName']

    connectionInformation = "mssql+pymssql://" + user + ":" + password + "@" + instance + ":" + port + "/" + db

    try:
        sqlEngine = sqlalchemy.create_engine(connectionInformation)
        connection = sqlEngine.connect()
        return connection

    except Exception as ex:
        print(ex)
        return None


def __update_execute(connection, df):

    transaction = None
    try:
        transaction = connection.begin()
        connection.execute('TRUNCATE TABLE PREDICT_RESULT_TEST ')
        df.to_sql('PREDICT_RESULT_TEST', connection, if_exists='append', index=None)
        transaction.commit()

    except Exception as ex:
        if transaction is not None and transaction.is_active:
            transaction.rollback()
        print(ex)

    finally:
        if connection is not None and not connection.closed:
            connection.close()

    return "FINISH"


def update_db(df):
    connection = __login()
    res = __update_execute(connection, df)

    return res
