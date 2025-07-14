import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="medical_store",
        cursorclass=pymysql.cursors.DictCursor
    )
