import sqlite3
import os

class Database:

    serialNumber = 1
    tableName = "data" + str(serialNumber)

    def connectToDB(self):
        self.conn = sqlite3.connect("chatData.db")
        self.cursor = self.conn.cursor()

    def tableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.tableName,))
        return bool(self.cursor.fetchone())


    def insertData(self, msg_dis):
        self.cursor.execute("""
            INSERT INTO {} VALUES(
                ?, ?, ?
            )
        """.format(self.tableName), (msg_dis['type'], msg_dis['name'], msg_dis['msg']))

    def createTable(self):
        if not self.tableExists():
            self.cursor.execute(f"CREATE TABLE {self.tableName}(type, name, msg)")
            self.conn.commit()
        else:
            self.serialNumber = self.serialNumber + 1
            self.tableName = "data" + str(self.serialNumber)
            self.cursor.execute(f"CREATE TABLE {self.tableName}(type, name, msg)")
            self.conn.commit()
            
        

    def deleteData(self):
        # don't need  but still created
        pass

    def displayData(self):
        self.cursor.execute(f"SELECT * FROM {self.tableName}")
        self.conn.commit()

    

        
