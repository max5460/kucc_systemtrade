import configparser
config = configparser.ConfigParser()
print(config.read('DBConnection.ini','UTF-8'))