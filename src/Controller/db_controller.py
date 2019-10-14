import sqlite3
import re

class DBController:
    
    path = ""

    ban_list = ['create', 'update', 'delete', 'fetch']    

    def __init__(self, path):
        print("init")
        self.path = path  
    def excute_sql(self, sql):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        if re.findall('|'.join(self.ban_list),sql):            
            raise Exception("Syntax ERROR")
        else:
            print("good")
        result = cursor.execute(sql).fetchall()
        names = list(map(lambda x: x[0], cursor.description))
        cursor.close()
        conn.close()
        return names, result
        
    
        
