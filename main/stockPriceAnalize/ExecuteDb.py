from CommonConstant import DBConnectionINIFile
from configparser import ConfigParser
import sqlalchemy
from LogMessage import ExecuteDBMessage
from logging import getLogger
logger = getLogger()


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
        return connection, None

    except Exception as ex:
        return None, str(ex)


def __update_execute(connection, df):

    targetTableName = 'PREDICT_RESULT'
    transaction = None
    returnError = None

    try:
        transaction = connection.begin()
        connection.execute('TRUNCATE TABLE ' + targetTableName)
        df.to_sql(targetTableName, connection, if_exists='append', index=None)
        transaction.commit()

    except Exception as ex:
        if transaction is not None and transaction.is_active:
            transaction.rollback()
        returnError = str(ex)

    finally:
        if connection is not None and not connection.closed:
            connection.close()
        return returnError


def update_db(df):
    connection, connectionError = __login()
    if connectionError is not None:
        logger.info(ExecuteDBMessage.connectDBError + connectionError)
        return connectionError

    dbUpdateError = __update_execute(connection, df)
    if dbUpdateError is not None:
        logger.info(ExecuteDBMessage.dbUpdateError + dbUpdateError)
        return dbUpdateError

    return None
