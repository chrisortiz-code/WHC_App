import sqlite3
from Classes import Database

import customtkinter as ctk
from tkinter import ttk,messagebox

class Table:
    host=None
    parent = None
    window = None
    name = None
    colNames = []
    colInps = []
    listbox = None
    tableTree = None
    console = None
    searchBar = None
    ascSwitch = None
    buttonFrame = None
    consoleFrame = None
    barFrame = None
    addWindow=None

    def __init__(self, host,i, j: int):
        self.host=host
        self.parent=self.host.Databases[i]
        self.name = self.parent.tables[j]
        self.gatherColumns()
        self.openWindow()

    def gatherColumns(self):
        self.parent.connect()
        self.parent.c.execute(f"PRAGMA TABLE_INFO({self.name});")
        info = self.parent.c.fetchall()
        self.parent.close()
        self.colNames = [i[1] for i in info]
        self.colTypes = [i[2] for i in info]
        self.colTypes = self.colTypes[1:-1]
        self.colInps = self.colNames[1:-1]

    def openWindow(self):
        self.window = ctk.CTk()
        self.window.geometry(f"{1300}x{800}")
        self.window.resizable(True,True)
        # Configure grid layout of the main window
        for i in range(11):
            self.window.grid_rowconfigure(i, weight=(1 if i == 2 else 0))  # Row 2 for treeview
        self.window.grid_columnconfigure((0, 1), weight=1)


        # Title bar
        title = ctk.CTkLabel(self.window, text=self.name.replace("_", " "), font=self.host.titleFont)
        title.grid(row=0, column=0, columnspan=2, padx=10, sticky="nsew")

        # Show table and other frames
        self.makeSearchFrame()
        self.showTable()
        self.showConsoleFrame()
        self.loadButtonFrame()

        self.window.mainloop()

    def makeSearchFrame(self):
        self.barFrame = ctk.CTkFrame(self.window)
        self.barFrame.grid(row=1, column=0, columnspan=2, sticky='nsew')
        # Configure the grid layout for the parent favouritesPopup
        self.barFrame.grid_columnconfigure(list(range(41)), weight=1)

        # Create the search bar entry
        contextLabel = ctk.CTkLabel(self.barFrame, text="Find Matches:")
        contextLabel.grid(row=0, column=0, sticky='nsew')
        self.searchBar = ctk.CTkEntry(self.barFrame)
        self.searchBar.grid(row=0, column=1, columnspan=5, sticky='nsew')

        # Create the search button
        self.searchButton = ctk.CTkButton(self.barFrame, text="\U0001F50D", command=self.orderTable)
        self.searchButton.grid(row=0, column=6, sticky='nsew')

        # Prepare the sort list
        sortlist = []
        for i in self.colTypes:
            if i in ["INT", "FLOAT", "DATE"]:
                sortlist.append(self.colNames[i].replace("_"," "))
        # Create the ComboBox
        contextLabel = ctk.CTkLabel(self.barFrame, text="Sort by:")
        contextLabel.grid(column=34, row=0, sticky='nsew')
        self.listbox = ctk.CTkComboBox(self.barFrame, values=sortlist)
        self.listbox.set(self.colNames[0].replace("_", " "))  # Set the initial value
        self.listbox.grid(row=0, column=35, columnspan=5, sticky='nsew')

        # Create the switch
        switchVar = ctk.IntVar()
        self.ascSwitch = ctk.CTkSwitch(self.barFrame, text="\u2191/\u2193", variable=switchVar, offvalue=0, onvalue=1)
        self.ascSwitch.grid(row=0, column=40, sticky='nsew')

        # Set the command for the switch
        self.ascSwitch.configure(command=self.orderTable)

    def showTable(self):
        style=ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        fieldbackground="grey",
                        foreground="white")
        self.tableTree = ttk.Treeview(self.window, show="headings", style="Treeview")
        self.tableTree.grid(row=2, column=0, columnspan=2, rowspan=8, sticky="nsew")
        self.tableTree["columns"] = self.colNames


        for col in self.colNames:
            self.tableTree.heading(col, text=col.replace("_", " "))
            self.tableTree.column(col, anchor=ctk.W)

        self.orderTable()  #ASCENDING ID,, DEFAULT

    def loadButtonFrame(self):
        self.buttonFrame = ctk.CTkFrame(self.window)
        self.buttonFrame.grid(row=10, column=0, sticky="nsew")
        self.buttonFrame.grid_columnconfigure((0, 1, 2), weight=1)
        self.buttonFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        button = ctk.CTkButton(self.buttonFrame, text="Add Entry", command=self.openAddWindow)
        button.grid(row=0, column=0,rowspan=4,sticky="nsew",padx=10,pady=10)
        updateButton= ctk.CTkButton(self.buttonFrame, text="Update Entry", command=self.openUpdateCallback)
        updateButton.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        removeConfirm = ctk.CTkButton(self.buttonFrame, text="Delete Entry", command=lambda: self.confirm_deletion(self.delEntry))
        removeConfirm.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=10, pady=10)

    def showConsoleFrame(self):
        self.consoleFrame = ctk.CTkFrame(self.window)
        self.consoleFrame.grid(row=10, column=1, sticky="nsew")

        self.consoleFrame.grid_columnconfigure(1, weight=1)
        self.consoleFrame.grid_columnconfigure((0, 2), weight=0)
        self.console = ctk.CTkTextbox(self.consoleFrame, state="disabled", height=150, width=450)
        self.console.grid(column=1,padx=5,pady=5,sticky="nsew")

    def openAddWindow(self):
        if self.addWindow!=None:
            self.addWindow.destroy()

        self.addEntries = []
        self.addWindow=ctk.CTkToplevel(self.window)
        self.addWindow.lift()
        self.addWindow.focus_force()
        self.addWindow.geometry(f"{150 * len(self.colInps)}x110")
        self.addWindow.resizable(False,False)
        self.addWindow.grid_rowconfigure((0,1),weight=1)
        self.addWindow.grid_columnconfigure(list(range(len(self.colInps))),weight=1)
        self.addWindow.title("Add Entry")
        maxrow=0
        column=0
        for k,i in enumerate(self.colInps):
            label = ctk.CTkLabel(self.addWindow, text=f"{i.replace('_', ' ')}:")
            entry = ctk.CTkEntry(self.addWindow)
            if self.colTypes[k]!="TEXT":
                label.grid(row=0, column=column,sticky="nsew",padx=5,pady=2)
                entry.grid(row=1, column=column,sticky="nsew",padx=5,pady=5)
                column+=1
                maxrow=max(1,maxrow)
            else:
                entry.configure(height=80)
                self.addWindow.geometry(f"{150 * (len(self.colInps)-1)}x{220}")
                label.grid(row=2, columnspan=len(self.colInps)-1,sticky="nsew",pady=2)
                entry.grid(row=3, columnspan=len(self.colInps)-1,sticky="nsew",pady=5)
                self.addWindow.grid_rowconfigure((0,1,2,3,4),weight=1)
                maxrow=max(3,maxrow)
            self.addEntries.append(entry)
        button = ctk.CTkButton(self.addWindow, text="Submit", command=self.addEntry)
        self.addWindow.grid_columnconfigure(list(range(column)), weight=1)
        self.addWindow.grid_rowconfigure(1, weight=1)
        button.grid(row=maxrow+1, columnspan=len(self.colInps))

    def openUpdateCallback(self):
        selectedItem=self.tableTree.selection()
        if selectedItem:
            vals = self.tableTree.item(selectedItem, 'values')
            vals=vals[1:-1]
            self.openUpdateWindow(vals)

    def openUpdateWindow(self, vals:list):
        self.updateEntries = []
        self.updateWindow=ctk.CTkToplevel(self.window)
        self.updateWindow.lift()
        self.updateWindow.focus_force()
        self.updateWindow.geometry("600x110")
        self.updateWindow.title(f"Update Entry #{vals[0]}")
        for k,i in enumerate(self.colInps):
            label = ctk.CTkLabel(self.updateWindow, text=f"{i.replace('_', ' ')}:")
            label.grid(row=0, column=k)
            entry = ctk.CTkEntry(self.updateWindow, placeholder_text=vals[k])
            entry.grid(row=1, column=k)
            self.updateEntries.append(entry)
        button = ctk.CTkButton(self.updateWindow, text="Submit", command=lambda: self.updateEntry(vals[0]))

        self.updateWindow.grid_rowconfigure(1, weight=1)
        button.grid(row=2, columnspan=len(self.colInps))

    def orderTable(self):
        """
        Orders the table using
        state of the selected sorting column
        state of the search bar
        :param asc: direction (1 for DESC, 2 for ASC)
        :return: None
        """
        order = "DESC" if self.ascSwitch.get() == 1 else "ASC"
        self.parent.connect()
        sqlstring=f"SELECT * FROM {self.name}"
        search=self.searchBar.get()
        if search!="":
            sqlstring+= f" WHERE "
            sqlstring += " OR ".join([f"{i} LIKE ?" for i in self.colNames])
            params = [f"%{search}%"] * len(self.colNames)
        sqlstring+=f" ORDER BY {self.listbox.get().replace(" ","_")} {order}"

        if search!="": self.parent.c.execute(sqlstring,params)
        else: self.parent.c.execute(sqlstring)

        self.tableTree.delete(*self.tableTree.get_children())
        rows = self.parent.c.fetchall()
        self.parent.close()

        if len(rows) > 10:
            scrollbar = ttk.Scrollbar(self.window, orient='vertical', command=self.tableTree.yview)
            scrollbar.grid(row=2, column=11)
            self.tableTree.configure(yscrollcommand=scrollbar.set)

        for j, newrow in enumerate(rows):
            tag = 'oddrow' if j % 2 == 0 else 'evenrow'
            self.tableTree.insert("", ctk.END, values=newrow, tags=tag)


    def confirm_deletion(self,action):
        self.selectedRow=self.tableTree.selection()
        if self.selectedRow!= '':
            response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to proceed with this action?")
            if response:
                action()

    def TTC(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.configure(state="disabled")

    def delEntry(self):
        vals = self.tableTree.item(self.selectedRow, 'values')
        self.parent.connect()
        self.parent.c.execute(f"DELETE FROM {self.name} WHERE id=?;", (vals[0],))
        self.TTC(f"Instance with ID: {vals[0]} Deleted")
        self.parent.close()

    def addEntry(self):
        vals= [i.get() for i in self.addEntries]
        if all(vals):
            vals.append(dt.datetime.now().strftime("%Y-%m-%d"))#Tag entry date
            placeholders = ','.join(['?'] * len(self.addEntries))
            self.parent.connect()
            self.parent.c.execute(f"INSERT INTO {self.name} VALUES (NULL, {placeholders});", vals)#Space for ID Col
            self.parent.conn.commit()
            self.parent.close()
            rowVals=[int(self.tableTree.item(self.tableTree.get_children()[-1],f"{self.name} ID"))+1] + vals #Gets the last ID <- not input from user
            self.tableTree.insert('', ctk.END, values=rowVals)
            self.TTC("Entry Submitted!")
        else:
            self.TTC("Fill all Entries")

    #update an entry
    def updateEntry(self, id):

        filledIn = [i.get() for i in self.updateEntries]
        sqlstring= ""
        for j,i in enumerate(filledIn):
            if i != "":
                sqlstring+=f"{self.colInps[j]}={filledIn[j]}, "
        sqlstring = sqlstring[:-2]
        self.parent.connect()
        self.parent.c.execute(f"UPDATE {self.name} SET {sqlstring} WHERE {self.name}_ID = {id};")
        self.parent.conn.commit()
        self.parent.close()
        self.orderTable()
