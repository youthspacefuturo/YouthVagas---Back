import pymysql

conn = pymysql.connect(
    host="srv1526.hstgr.io",
    user="u155031960_adminYouth",
    password="YouthV4g4s!!yV",
    database="u155031960_YouthVagas",
    port=3306
)
print("Conexão OK")
conn.close()