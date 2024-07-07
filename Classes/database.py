import sqlite3
class Database:
    conn = None
    c = None
    name = None
    tables = []
    path = None


    def __init__(self, path):
        self.path = path
        self.loadTables()
        self.name = self.getName()

    def connect(self):
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
    def close(self):
        self.conn.close()

    def removeTable(self, j: int) -> None:
        self.connect()
        self.c.execute(f"DROP TABLE if exists {self.tables[j]};")
        self.conn.commit()
        self.close()

    def getName(self):
        name = []
        for c in self.path:
            if c == '.':
                break
            if c != '_':
                name.append(c)
            else:
                name.append(" ")
        return "".join(name)

    def loadTables(self):
        self.connect()
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';")
        tables = self.c.fetchall()
        self.tables = [i[0] for i in tables]
        self.close()