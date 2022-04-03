from msilib.schema import Error
import pymysql 

class Database():
    def __init__(self,dbname,host = '127.0.0.1',user = 'root', pwd = ''):
        self.conn =  pymysql.connect(host =host, user = user, password = pwd)
        self.dbname = dbname

    def createdb(self):
        print("Creating Database: {}".format(self.dbname))
        self.conn.cursor().execute(f'create database {self.dbname}')
        print("DataBase Created Successfully")

    def createTable(self, querystring):
        print(f"RUNNING: {querystring}")
        self.conn.cursor().execute(querystring)
        print(f"Table Created  Successfully")
    def SelectQuery(self,querystring,param,mode = 'fetchone'):
        print(querystring)
        cur =  self.conn.cursor()
        cur.execute(querystring,param)
        if mode == 'fetchone':
            return cur.fetchone()
        elif mode == 'fetchall':
            return cur.fetchall()
        else:
            return "Error"

    
    def InsertQuery(self,querystring,param):
        self.conn.cursor().execute(querystring,param)
        self.conn.commit()
        print("Insert query executed")

    def UpdateQuery(self,querystring,param):
        self.conn.cursor().execute(querystring,param)
        self.conn.commit()
        print('Update query executed')

    def DeleteFromRow(self,querystring,param):
        self.conn.cursor().execute(querystring,param)
        self.conn.commit()
        print("Row Deleted  Successfully")
