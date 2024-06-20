import os
import sqlite3
import tkinter as tk
import tkinter.ttk as ttk
import datetime as dt


class Database:
    conn = None   #will be called in with vjs selection
    c = None
    name=None
    tables =[]
    path=None

    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.load_tables()
        self.name = self.get_name()

    def remove_table(self,tname)-> None:
        self.c.execute(f"DROP TABLE {tname};")
        self.conn.commit()
        self.type_to_console(f"{tname} Deleted")

    def get_name(self):
        name =[]
        for c in self.path:
            if c=='.':
                break
            name.append(c)
        return "".join(name)

    def load_tables(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        list = self.c.fetchall()
        self.tables = [i[0] for i in list]
        self.tables = self.tables[1:]

class Table():
    db=None
    name = None
    cols = {}
    colarr=[]
    colinps=[]
    window = None
    del_ent=None
    search_ent=None
    listbox=None
    tree= None
    frame_bottom=None
    console=None
    #Initialise new window, this window will have the following buttons,
    #ADD_ENTRY : DONE
    #DEL_ENTRY: DOne
    #A dropbox of all the different sort methods AND Beside it, a dual switch that can be set to up/down (AScending/descending sort)
    #make the dropbox default (name)id, then under that..
    #for all cols that have dictionary second method, cols[i]= Number, Money,or Date make them a dropbox point
    #when you click sort button,, sort_table(col,up/down) read from the dropbox, up/down read from the switch
    def __init__(self, db, i: int):
        self.db = db
        self.name = db.tables[i]
        self.gather_cols()
        self.open_window()
    def type_to_console(self,message:str):
        self.console.config(state='normal')
        self.console.delete(0, tk.END)
        self.console.insert(0, message)
        self.console.config(state='disabled')

    def delete_entry(self,id) -> None:
        """
        Deletes from table only done by id (VJ SPECIFY THAT on the textbox where you take that name input)
        :param id:
        :return:
        """
        self.db.c.execute(f"SELECT * FROM {self.name} WHERE {self.name}id = ?", (id,))
        result = self.db.c.fetchone()
        if(result):

            self.db.c.execute(f"DELETE FROM {self.name} WHERE id=?;", (id,))
            self.type_to_console(f"Instance with ID: {id} Deleted")
        else:
            self.type_to_console(f"Instnace with ID: {id} Does Not Exist")

    def show_table(self):
        rose=self.get_rows()
        label=tk.Label(self.window,text=self.name,font=("Helvetica",24))
        label.pack(side=tk.TOP,padx=10,pady=5)
        self.tree = ttk.Treeview(self.window,show="headings")
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree["columns"]=self.colarr
        for col in self.colarr:
            self.tree.heading(col,text=col)
            self.tree.column(col,anchor=tk.W)
        for row in rose:
            self.tree.insert("",tk.END,values=row)

    def get_rows(self)->list:
        self.db.c.execute(f"SELECT * FROM {self.name};")
        rows = self.db.c.fetchall()
        return rows


    def gather_cols(self):
        """
        Gather all columns from a table -> (self.cols give vj the needed entry points to add any entry)
        """
        self.db.c.execute(f"PRAGMA TABLE_INFO({self.name});")
        info = self.db.c.fetchall()
        self.cols = {i[1]: i[2] for i in info}
        self.colarr=list(self.cols.keys())
        self.colinps=self.colarr[1:-1]

    def open_window(self):
        self.window = tk.Toplevel()
        self.window.geometry('500x500')
        self.show_table()

        label = tk.Label(self.window,text="Remove By ID")
        label.pack()
        self.del_ent=tk.Entry(self.window)
        self.del_ent.pack()
        remove_confirm=tk.Button(self.window,text="Confirm",command=self.read_del)
        remove_confirm.pack()
        button = tk.Button(self.window, text="Close", command=self.window.destroy)
        button.pack()
        subframe(self)
        self.frame_bottom = tk.Frame(self.window)
        self.frame_bottom.pack(pady=10)
        self.console = tk.Text(self.frame_bottom,height = 2, width=20, state= "disabled")
        self.console.pack()
        self.window.mainloop()



    def read_del(self):
        i=self.del_ent.get()#will be id number
        self.delete_entry(i)


class subframe():
    #needs also like an error text area to print the errors such as
    #columns not filled
    frame2 = None
    entries = []
    parent = None
    def __init__(self, parent:Table):
        self.parent= parent
        self.display_add_frame()


    def add_entry(self,entry) -> None:
        """
        Adds a new entry to the database with auto increment id for all
        :param database: database name
        :param entry: list of vals ["Chris", "Ortiz", "4372184373", "chrisalex.ortiz@yahoo.com"] taken from vj
        :return: None just updates the database
        """

        entry.append(dt.datetime.now().strftime("%Y-%m-%d"))
        placeholders = ','.join(['?'] * len(entry))
        self.parent.db.c.execute(f"INSERT INTO {self.parent.name} VALUES (NULL, {placeholders});", entry)
        #self.parent.db.c.execute(f"INSERT INTO {self.parent.name} VALUES ({placeholders});", entry)
        self.parent.db.conn.commit()
        self.parent.tree.insert('',tk.END,values=entry)



    def submit(self):
        vals =[]
        for i in self.entries:
            vals.append(i.get())
        if(self.isFull(vals)):
            self.add_entry(vals)
            self.parent.type_to_console("Entry Submitted!")
        else:
            self.parent.type_to_console("Fill all Entries")
            #ERROR
            #make a message saying inputs saved

    def isFull(self,vals)->bool:
        return all(vals)
    def display_add_frame(self):
        self.frame2=tk.Frame(self.parent.window)
        self.frame2.pack()
        #self.window2.title("Add Entry")
        #self.window2.geometry("300x300")

        for i,col in enumerate(self.parent.colinps):
            label = tk.Label(self.frame2, text=col+":")
            label.grid(row = 0, column = i, padx=5,pady=5)
            entry= tk.Entry(self.frame2)
            entry.grid(row = 1, column = i, padx=5,pady=5)
            self.entries.append(entry)
        button = tk.Button(self.frame2, text="Submit", command=self.submit)
        button.grid(row=2,columnspan=len(self.parent.colarr),pady=5)



#class MainWindow
# has buttons under each database,
# with list of all database, window frame listing all tables,
# gonna work with db.tables[i]

class MainWindow:
    home = None
    dbnames=[]
    dbclass=[]
    def __init__(self):
        self.home= tk.Tk()
        self.dbases=self.get_databases()
        self.load_all_dbs()
        self.home.mainloop()

    def get_databases(self):
        # List all items in the current directory
        items_in_directory = os.listdir('.')

        # Filter the items to include only those that end with .db
        db_files = [f for f in items_in_directory if f.endswith('.db')]

        for i in db_files:
            self.dbclass.append(Database(i))
        # Return the list of .db paths
        return db_files

    def load_all_dbs(self):
        for k in self.dbclass:
            DBWind(k)


class DBWind:
    parent=None
    winder=None
    tc_button=None

    tab_buttons=[]
    def __init__(self,parent:Database):
        self.winder=tk.Toplevel()
        self.parent=parent
        self.table_buttons()
        self.tc_buttons()
        self.winder.mainloop()

    def tc_buttons(self):
        self.tc_button= tk.Button(self.winder, text="Open Table Creator", command=self.open_tc)
        self.tc_button.pack(pady=10)

    def table_buttons(self):
        for i in range(len(self.parent.tables)):
            k = self.make_button(i)
            self.tab_buttons.append(k)

    def make_button(self,i):
        j = tk.Button(self.winder,text=self.parent.tables[i],command=lambda :self.init_table(i))
        j.pack()
        return j

    def init_table(self,i):
        Table(self.parent, i)

    def open_tc(self):
        TableCreator(self.parent)

class TableCreator():
    parent = None
    frame3=None
    console=None
    entries=[]
    comboboxes=[]
    frame_top = None
    frame_middle = None
    frame_bottom = None
    types ={
        "Name/Words": "varchar(250)",
        "Number": "int",
        "Money": "float",
        "Date": "date",
        "Description": "text"
    }
    def __init__(self, parent:Database):
        self.parent=parent
        self.set_table()


    def set_table(self):
        self.frame3=tk.Toplevel()
        self.frame3.title(f"{self.parent.name} Table Creator")
        self.frame3.geometry("600x400")

        # Frame for table name
        self.frame_top = tk.Frame(self.frame3)
        self.frame_top.pack(pady=10)

        tk.Label(self.frame_top, text="Table Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = tk.Entry(self.frame_top)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        # Frame for table columns
        self.frame_middle = tk.Frame(self.frame3)
        self.frame_middle.pack(pady=10)

        self.frame_bottom = tk.Frame(self.frame3)
        self.frame_bottom.pack(pady=10)
        self.console = tk.Text(self.frame_bottom,height = 2, width=20, state= "disabled")
        self.console.pack()


        for i in range(10):
            row_frame = tk.Frame(self.frame_middle)
            row_frame.pack(fill=tk.X, pady=2)

            entry = tk.Entry(row_frame)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.entries.append(entry)

            combobox = ttk.Combobox(row_frame, values=[
                "Name/Words",
                "Number/Money",
                "Date",
                "Description"
            ])
            combobox.pack(side=tk.LEFT, padx=5)
            self.comboboxes.append(combobox)

        # Submit button
        submit= tk.Button(self.frame3, text="Create Table", command=self.submit)
        submit.pack(pady=10)
        exit=tk.Button(self.frame3, text="Exit", command=self.frame3.destroy)
        exit.pack(pady=10)

    def submit(self):
        name = self.name_entry.get()
        colvals=[]
        typevals=[]
        for i in self.entries:
            colvals.append(i.get())
        for i in self.comboboxes:
            typevals.append(i)
        if self.isFull(colvals)&self.isFull(typevals):
            self.create_table(name,colvals,typevals)
            self.type_to_console("Submitted")
        else:
            self.type_to_console("Deleted")




    def isFull(self,vals)->bool:
        return all(vals)


    def create_table(self,tname,cols,types) -> None:
        """
        On click, new table is made, by reading the entries from vjs application (Table name, col names(LIST), and types[LIST])
        :return: NONE
        """
        coltypes ={
            "Name/Words": "varchar(250)",
            "Number": "int",
            "Money": "float",
            "Date": "date",
            "Description": "text"
        }

        columns = [f"{tname}Id INTEGER PRIMARY KEY AUTOINCREMENT"]#VJ THIS need to be kept here before u read all those colum names
        columns.append(cols)
        columns.append("Input Date DATE")
        i = 0
        while i < len(columns) and i < len(types):#iterates for as many columns
            if columns[i] and types[i]:
                columns.append(f"{columns[i]} {coltypes[types[i]]}")
            i += 1
        if tname and self.isFull(columns): #if both exist, proceed
            columns_str = ", ".join(columns)
            self.parent.tables.append(tname)
            self.parent.c.execute(f"CREATE TABLE {tname} ({columns_str});")
            self.type_to_console("Submitted!")
        else:
            self.type_to_console("Fill All Columns")



    def type_to_console(self,message: str):
        self.console.config(state='normal')
        self.console.delete(0, tk.END)
        self.console.insert(0, message)
        self.console.config(state='disabled')



if __name__ == '__main__':
    d=Database("your_database.db")
    d = DBWind(d)

