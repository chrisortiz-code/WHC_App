import csv
import os
import sqlite3
import datetime as dt
from tkinter import ttk, filedialog,messagebox
import customtkinter as ctk
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab import platypus


class App:
    buttonColour = "#1f6aa5"
    selection=""
    selectedButton=None
    currentTab=""
    window = None
    Databases = []
    loaded=[]
    currentTc=None
    favourites=[]
    favsCheckbox=[]
    favouritesPopup=None

    def __init__(self):
        self.window = ctk.CTk()
        self.regFont=ctk.CTkFont(family="open sans")
        self.titleFont=ctk.CTkFont(size=24, weight="bold", family="open sans")

        self.getDatabases()

        # configure window
        self.window.title("WHC Database")
        self.window.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.loadGrid()

        # create sidebar favouritesPopup with widgets
        self.loadSideFrame()

        # create console
        self.loadConsole()

        # create tabview
        self.loadTabsBox()

        # create widget favouritesPopup
        self.loadWidgetFrame()

        self.window.mainloop()

    def loadGrid(self):
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure((2, 3), weight=0)
        self.window.grid_rowconfigure(0, weight=1)

    def getDatabases(self):
        self.loaded = ['Favourites']

        # List all items in the current directory
        directory = os.listdir("Databases")

        for i in directory:
            p = Database(i)
            self.Databases.append(p)

        self.tabButtons = [[] for _ in range(len(self.Databases))]

    def reLoadApp(self):
        # Clear the existing Databases and
        self.selection=""
        self.Databases.clear()
        self.loaded.clear()


        # Reload the databases
        self.getDatabases()

        # Reload the tab view
        self.loadTabsBox()
        if self.currentTab!='':
            self.tabview.set(self.currentTab)

    def openNewDb(self):
        dialog = ctk.CTkInputDialog(text="Database Name", title="Create Database")
        self.newDb(dialog.get_input())

    def newDb(self,val):

        val.replace(" ", "_")
        val+=".db"
        if val not in self.Databases:
            sqlite3.connect(val)
            self.Databases.append(Database(val))
            self.reLoadApp()
        else:
            self.TTC("Database already exists")#change to console


    def loadWidgetFrame(self):
        self.widgetFrame = ctk.CTkFrame(self.window)
        self.widgetFrame.grid(row=1, column=1, columnspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.tableCreateButton = ctk.CTkButton(master=self.widgetFrame, text="Create New Table", command=self.openTc, font=self.regFont)
        self.tableCreateButton.grid(row=0, column=0, pady=20, padx=20, sticky="n")
        self.tableCreateButton.configure(width=210)

        self.tableDeleteButton = ctk.CTkButton(master=self.widgetFrame, text="Delete Table", command=lambda: self.confirm_deletion(self.delTable), font=self.regFont)
        self.tableDeleteButton.grid(row=1, column=0, pady=20, padx=20, sticky="n")
        self.tableDeleteButton.configure(width=210)

        self.favTableButton = ctk.CTkButton(master=self.widgetFrame, text="Placeholder", command=self.openTc, font=self.regFont)
        self.favTableButton.grid(row=2, column=0, pady=20, padx=20, sticky="n")
        self.favTableButton.configure(width=210)
        self.newDbButton = ctk.CTkButton(self.widgetFrame, text="Create New DB", command=self.openNewDb, font=self.regFont)
        self.newDbButton.grid(row=0, column=1, padx=20, pady=10)
        self.newDbButton.configure(width=210)
        self.summaryButton = ctk.CTkButton(self.widgetFrame, text="Export Table", command=self.exportTable, font=self.regFont)
        self.summaryButton.grid(row=1, column=1, padx=20, pady=10)
        self.summaryButton.configure(width=210)
        self.importExport = ctk.CTkButton(self.widgetFrame, text="Import Table", command=self.openTc, font=self.regFont)
        self.importExport.grid(row=2, column=1, padx=20, pady=10)
        self.importExport.configure(width=210)

    def confirm_deletion(self,action):
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to proceed with this action?")
        if response:
            action()

    def loadTabsBox(self):
        self.tabview = ctk.CTkTabview(self.window, width=600)
        self.tabview._grid_forget_all_tabs()
        self.tabview.grid(row=0, column=1, columnspan=3, padx=(20, 20), sticky="nsew")

        self.loadFavs()
        for i in self.Databases:
            if i not in self.loaded:
                self.loaded.append(i)
                self.tabview.add(i.name)
                self.tabview.tab(i.name).grid_columnconfigure((0, 1, 2, 3), weight=1)
                self.tabview.tab(i.name).grid_rowconfigure((0, 1, 2, 3), weight=1)
                self.tableButtons(self.Databases.index(i))
    # loads main console
    def loadConsole(self):
        self.console = ctk.CTkTextbox(self.window, width=250,state="disabled")
        self.console.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

    def loadSideFrame(self):
        self.sideFrame = ctk.CTkFrame(self.window, width=140, corner_radius=0)
        self.sideFrame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sideFrame.grid_rowconfigure(1, weight=1)
        self.logoLabel = ctk.CTkLabel(self.sideFrame, text="WHC Database",
                                      font=self.titleFont)
        self.logoLabel.grid(row=0, column=0, padx=20, pady=(20, 10))
        image=ctk.CTkImage(light_image=Image.open("auxiliaries/logo-whc.png"), dark_image=Image.open(
            "auxiliaries/logo-whc.png"), size=(210, 180))

        self.logo = ctk.CTkLabel(self.sideFrame, image=image, text="")
        self.logo.grid(row=1, column=0, padx=20, pady=(20, 10))


    def TTC(self, message: str):

        self.console.configure(state="normal")
        self.console.delete("1.0",ctk.END)
        self.console.insert("end", message)
        self.console.configure(state="disabled")

    def delTable(self):

        db = self.Databases[int(self.selection[0])]
        db.removeTable(int(self.selection[1]))

        del db.tables[int(self.selection[1])]
        del self.tabButtons[int(self.selection[0])][int(self.selection[1])]
        with open('auxiliaries/favourites.txt', 'r') as file:
            s=(file.read()).split('\n')
        for i in s:
            if i==f"{self.selection[0]} {self.selection[1]}":
                s.remove(i)
        with open('auxiliaries/favourites.txt', 'w') as file:
            file.writelines(s)

        self.TTC("Table has been deleted.")
        self.selection=""
        self.reLoadApp()

    def openTc(self):
        if self.currentTc!=None:
            self.currentTc.close()
        p = TableCreator(self)
        self.currentTc=p

    def openTable(self,i:int,j):
        self.resetButton(i, j)
        Table(self,i, j)

    def tableButtons(self,i:int):
        for j in range(len(self.Databases[i].tables)):
            k = self.makeButton(i, j)
            self.tabButtons[i].append(k)

    def makeButton(self, i, j):
        buttonText = self.Databases[i].tables[j].replace("_", " ")
        button = ctk.CTkButton(self.tabview.tab(self.Databases[i].name), text=buttonText, command=lambda: self.firstClick(
            i, j), font=self.regFont)
        button.grid(row=j%3, column=j//3, pady=5)
        return button

    def makeFButton(self, i:int , j: int):
        buttonText = self.Databases[i].tables[j].replace("_", " ")
        button = ctk.CTkButton(self.tabview.tab("Favourites"), text=buttonText, command=lambda: self.openTable(i, j), font=self.regFont)
        button.grid(row=j%3, column=j//3, pady=5)
        return button

    def updateFav(self):
        results = []

        for k,p in enumerate(self.favsCheckbox):
            for i,j in enumerate(p):
                if j.get()==1:
                    results.append(f"{k} {i}\n")

        with open('auxiliaries/favourites.txt', 'w') as file:
            file.writelines(results)

        self.reLoadApp()


    def resetButton(self,i,j):
        self.tabButtons[i][j].configure(
            text=self.Databases[i].tables[j].replace("_", " "),
            command=lambda: self.firstClick(i, j),
            fg_color=self.buttonColour,
            hover_color="#144870",
            border_width=0,
            text_color="white",
            font=self.regFont)
        self.selection = ""

    def favouritesMenu(self):
        if self.favouritesPopup!=None:
            self.favouritesPopup.destroy()

        self.favouritesPopup = ctk.CTkToplevel(self.window)
        self.favouritesPopup.geometry=f"{100*len(self.Databases)}x{40*10}"
        self.favouritesPopup.resizable(False,False)
        self.favouritesPopup.lift()
        self.favouritesPopup.focus_force()

        maxrow=0
        for k,db in enumerate(self.Databases):
            label = ctk.CTkLabel(self.favouritesPopup, text=db.name)
            label.grid(column=k,row=0)

            self.favsCheckbox.append([])
            for j,table in enumerate(db.tables):
                var = ctk.IntVar(value=1 if (k,j) in self.favourites else 0)
                checkbox = ctk.CTkCheckBox(self.favouritesPopup, text=table.replace("_"," "), variable=var)
                checkbox.grid(column=k,row=j+1,padx=5,pady=5)
                self.favsCheckbox[k].append(var)
                maxrow=max(maxrow,j+1)
        saveButton = ctk.CTkButton(self.favouritesPopup, text="Save", command=self.updateFav)
        saveButton.grid(columnspan=len(self.Databases),row=maxrow+1)



    def firstClick(self, i: int, j: int):
        if self.selection!="":
            self.resetButton(int(self.selection[0]), int(self.selection[1]))
        self.currentTab=self.tabview.get()
        self.tabButtons[i][j].configure(
            command=lambda: self.openTable(i, j),
            fg_color="#eb9751",
            text=self.Databases[i].tables[j].replace("_", " "),
            text_color="white",
            hover_color="#a56a39",
            border_color="white",
            border_width=2,
            font=self.regFont
        )

        self.selection = f"{i}{j}"

    def loadFavs(self):
        self.tabview.add("Favourites")
        self.tabview.tab("Favourites").grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.tabview.tab("Favourites").grid_rowconfigure((0, 1, 2, 3), weight=1)
        updateFavs=ctk.CTkButton(self.tabview.tab("Favourites"),text= "Update Favourites",command=self.favouritesMenu)
        updateFavs.grid(row=3,column=3)

        with open('auxiliaries/favourites.txt') as file:
            s=(file.read()).split('\n')
            for i in (s):
                if i:
                    self.makeFButton(int(i[0]), int(i[2]))
                    self.favourites.append((int(i[0]),int(i[2])))
        self.loaded.append('Favourites')

    def createExport(self,fileName:str):
        """
        Creates an export of the table
        Reads file type and uses csv, or reportlib
        :param fileName:
        :return:
        """
        d=int(self.selection[0])
        t=int(self.selection[1])
        dbName=self.Databases[d]
        table=dbName.tables[t]
        dbName.connect()
        dbName.c.execute(f"PRAGMA TABLE_INFO({table});")
        info =dbName.c.fetchall()
        headers = [i[1].replace("_"," ") for i in info]
        dbName.c.execute(f"Select * from {table};")
        rows = dbName.c.fetchall()
        dbName.close()
        if(fileName.endswith(".csv")):
            with open(fileName, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            self.TTC(f"Data exported to {fileName} successfully.")
        elif(fileName.endswith(".pdf")):

            doc = platypus.SimpleDocTemplate(fileName, pagesize=letter)

            # Combine headers and data into a single table data structure
            tableData = [headers] + rows

            # Create a Table with the data
            title= headers[0][:-3]
            dbName= self.Databases[int(self.selection[0])].name.replace("_", " ")
            styles = getSampleStyleSheet()
            title_style = styles['Title']

            # Create a title paragraph
            title = platypus.Paragraph(dbName + " - " + title, title_style)

            # Create a spacer
            spacer = platypus.Spacer(1, 0.2 * inch)
            table = platypus.Table(tableData)

            # Add some basic styling
            style = [
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]

            for i, row in enumerate(tableData):
                style.append(('BACKGROUND',(0,i),(-1,i),colors.lightgrey)) if i % 2 == 0 else style.append(('BACKGROUND',(0,i),(-1,i),colors.white))

            style.append(('BACKGROUND', (0, 0), (-1, 0), colors.grey)) #Headers background

            tStyle= platypus.TableStyle(style)
            table.setStyle(tStyle)
            spacer2=spacer
            log= platypus.Paragraph(f"Table Exported on {dt.datetime.now().strftime("%Y-%m-%d")} at {dt.datetime.now().strftime("%I:%m %p")}")
            # Build the PDF
            elements = [title,spacer,table,spacer2,log]
            doc.build(elements)
            self.TTC(f"Data exported to {fileName} successfully.")

    def exportTable(self):
        """
        Export the selected table data to a CSV or PDF file.
        This function prompts the user to select a file path
        saves the selected table data as a CSV file or PDF file.
        calls the `createExport` method to generate the export file.
        resets the button at the selected table position and clears the `selection` attribute.

        """
        if self.selection!="":
            fileTypes = [("CSV files", "*.csv"), ("PDF files", "*.pdf")]
            filePath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=fileTypes)
            self.createExport(filePath)
            self.resetButton(self.selection[0],self.selection[1])
            self.selection=""

    #need import table, open dialoog, columns in file or nah
    #yes pick db and read
    #no table creator, then insert

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
        # Configure the grid layout for the parent
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
        for k,i in enumerate(self.colTypes):
            if i in ["INT", "FLOAT", "DATE"]:
                sortlist.append(self.colNames[k].replace("_"," "))
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

            vals=vals[:-1]
            self.openUpdateWindow(vals)

    def openUpdateWindow(self, vals:list):
        self.updateEntries = []
        self.updateWindow=ctk.CTkToplevel(self.window)
        self.updateWindow.lift()
        self.updateWindow.focus_force()
        self.updateWindow.geometry("600x110")
        id=vals[0]
        self.updateWindow.title(f"Update Entry #{id}")
        for k,i in enumerate(self.colInps):
            label = ctk.CTkLabel(self.updateWindow, text=f"{i.replace('_', ' ')}:")
            label.grid(row=0, column=k)
            entry = ctk.CTkEntry(self.updateWindow, placeholder_text=vals[k+1])
            entry.grid(row=1, column=k)
            self.updateEntries.append(entry)
        print(vals)
        button = ctk.CTkButton(self.updateWindow, text="Submit", command=lambda: self.updateEntry(id))

        self.updateWindow.grid_rowconfigure(1, weight=1)
        button.grid(row=2, columnspan=len(self.colInps))

    def orderTable(self):
        """
        Orders the table using
        state of the selected sorting column
        state of the search bar
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
            placeholders = ','.join(['?'] * (len(self.addEntries)+1))
            self.parent.connect()
            self.parent.c.execute(f"INSERT INTO {self.name} VALUES (NULL, {placeholders});", vals)#Space for ID Col
            self.parent.conn.commit()
            self.parent.close()
            prevId=self.tableTree.get_children()[-1]
            if prevId:
                rowVals=[int(self.tableTree.item(prevId,f"{self.name.replace("_"," ")} ID"))+1] + vals
            else:
                rowVals=[1]+vals
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
        print(sqlstring,self.name)
        self.parent.connect()
        self.parent.c.execute(f"UPDATE {self.name} SET {sqlstring} WHERE {self.name}_ID = {id};")
        self.parent.conn.commit()
        self.parent.close()
        self.orderTable()

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
        dbPath = os.path.join('Databases', self.path)
        self.conn = sqlite3.connect(dbPath)
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

        # Configure the main grid
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

        # Frame for table name
        self.frameTop = ctk.CTkFrame(self.popup)
        self.frameTop.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frameTop.grid_columnconfigure(0, weight=1)
        self.frameTop.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frameTop, text="Table Name:").grid(row=0, padx=5, pady=2, column = 0, sticky ="ew")
        self.nameEntry = ctk.CTkEntry(self.frameTop)
        self.nameEntry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(self.frameTop, text="Column Name").grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(self.frameTop, text="Column Type").grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Frame for table columns
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
        Creates new table by reading the entries from entry points DB Host,Table Name, Col names and Col types (Lists)
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