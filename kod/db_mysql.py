import mysql.connector

def connect():
    conn = mysql.connector.connect(
    unix_socket="/tmp/mysql.sock",
    user="root",
    password="123",
    database="ai_db"
    )
    return conn, conn.cursor()