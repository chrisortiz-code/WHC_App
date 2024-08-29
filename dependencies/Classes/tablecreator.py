import customtkinter as ctk
from dependencies.Classes import App
from dependencies.Classes import Database
class TableCreator:
    parent = None
    popup = None
    console = None
    entries = []
    comboboxes = []
    frameTop = None
    frameMiddle = None
    frameBottom = None
    types = {
        "Name / Number / Address": "varchar(20)",
        "Whole Number": "int",
        "Money (Decimal)": "float",
        "Date": "date",
        "Description": "text"
    }

    def __init__(self, parent: App):
        self.parent = parent
        self.setTable()

    def close(self):
        self.popup.destroy()

    def setTable(self):
        self.popup = ctk.CTkToplevel(self.parent.window)
        self.popup.transient(self.parent.window)
        self.popup.title("Table Creator")
        self.popup.geometry(f"{500}x{660}")

        # Ensure the popup window appears in front
        self.popup.lift()
        self.popup.focus_force()

        # Configure the main favouritesPopup grid
        self.popup.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.popup.grid_columnconfigure(0, weight=1)
        nameVals=[]
        for i in self.parent.Databases:
            nameVals.append(i.name.replace("_"," "))

        # Option menu for database names
        self.dbmenu = ctk.CTkOptionMenu(self.popup, values=nameVals)
        if self.parent.tabview.get()!="Favourites":
            self.dbmenu.set(self.parent.tabview.get())
        self.dbmenu.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Frame for currentTable name
        self.frameTop = ctk.CTkFrame(self.popup)
        self.frameTop.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frameTop.grid_columnconfigure(0, weight=1)
        self.frameTop.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frameTop, text="Table Name:").grid(row=0, padx=5, pady=2, column = 0, sticky ="ew")
        self.nameEntry = ctk.CTkEntry(self.frameTop)
        self.nameEntry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self.frameTop, text="Column Name").grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(self.frameTop, text="Column Type").grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Frame for currentTable columns
        self.frameMiddle = ctk.CTkFrame(self.popup)
        self.frameMiddle.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frameMiddle.grid_columnconfigure(0, weight=1)

        self.entries = []
        self.comboboxes = []

        for i in range(10):
            rowFrame = ctk.CTkFrame(self.frameMiddle)
            rowFrame.grid(row=i, column=0, pady=2, sticky="ew")
            rowFrame.grid_columnconfigure(0, weight=1)
            rowFrame.grid_columnconfigure(1, weight=1)

            entry = ctk.CTkEntry(rowFrame)
            entry.grid(row=0, column=0, padx=5, sticky="ew")
            self.entries.append(entry)

            combobox = ctk.CTkComboBox(rowFrame, values=[i for i in self.types.keys()])
            combobox.set('')
            combobox.grid(row=0, column=1, padx=5, sticky="ew")
            self.comboboxes.append(combobox)

        # Frame for console and buttons
        self.frameBottom = ctk.CTkFrame(self.popup)
        self.frameBottom.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.frameBottom.grid_columnconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(self.frameBottom, height=2, width=120, state="disabled", font=self.parent.regFont)
        self.console.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        # Submit button
        submit = ctk.CTkButton(self.popup, text="Create Table", command=self.submit)
        submit.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        # Exit button
        exitButton = ctk.CTkButton(self.popup, text="Exit", command=self.popup.destroy)
        exitButton.grid(row=5, column=0, pady=10, padx=20, sticky="ew")

    def submit(self):
        name = self.nameEntry.get()
        name.replace(" ", "_")
        colvals = []
        typevals = []
        for i in self.entries:
            p = i.get()
            if p!='':
                colName=""
                for c in p:
                    if c==" ":
                        colName+="_"
                    else:
                        colName+=c
                colvals.append(colName)

        dcount=0
        for i in self.comboboxes:
            p=i.get()
            if p!='':
                if p =="Description":
                    dcount+=1
                typevals.append(p)
        if all(colvals) & all(typevals)&(dcount<2):
            self.createTable(self.dbmenu.get(), name, colvals, typevals)
            self.popup.destroy()
            self.parent.TTC("Table Created")
            self.parent.reLoadApp()
        elif dcount>=2:
            self.TTC("Only use 1 description column")
        else:
            self.TTC("Fill Rows Properly")

    def createTable(self,host,tname,cols,types) -> None:
        """
        Creates new currentTable by reading the entries from entry points DB Host,Table Name, Col names and Col types (Lists)
        :return: NONE
        """
        father= Database(host+".db")

        columns = [f"{tname.replace(" ","_")}_ID INTEGER PRIMARY KEY AUTOINCREMENT"]


        i = 0
        while i < len(cols) and i < len(types):#iterates for as many columns
            if cols[i] and types[i]:
                columns.append(f"{cols[i]} {self.types[types[i]]}")
            i += 1
        columns.append("Input_Date DATE")
        if tname and all(cols): #if both exist, proceed
            columns_str = ", ".join(columns)
            father.tables.append(tname)
            father.connect()
            father.c.execute(f"CREATE TABLE {tname.replace(" ","_")} ({columns_str});")
            father.close()
            self.TTC("Submitted!")
        else:
            self.TTC("Fill All Columns")

    def TTC(self, message: str):
        self.console.configure(state='normal')
        self.console.delete("1.0", ctk.END)
        self.console.insert("1.0", message)
        self.console.configure(state='disabled')

