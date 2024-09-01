import csv
import os
import sqlite3
import datetime as dt
from tkinter import ttk, filedialog
import customtkinter as ctk
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab import platypus


class App:
    """
    Class for the main window
    Holds Data:
        Array of initialized Databases
        2D array of tables in each DB
    8 buttons
        Open Table - self.openTable
        Edit Favourites - self.openFavourites
        Create Table - self.openTc
        Delete Table - self.delTable
        View Log - self.viewLog
        Create DB - self.addDBDialog
        Export Table - self.exportTable
        Import Table - self.importTable

    """
    selection = []
    currentTab = ""
    mainScreen = None
    Databases = []
    favourites = []
    favsCheckbox = []
    favouritesPopup = None
    importWindow = None
    height= 20

    def __init__(self):
        self.mainScreen = ctk.CTk()
        self.regFont = ctk.CTkFont(family="open sans")
        self.titleFont = ctk.CTkFont(size=24, weight="bold", family="open sans")

        self.getDatabases()

        # configure window
        self.mainScreen.title("WHC Database")
        self.mainScreen.geometry(f"{1100}x{580}")
        self.mainScreen.grid_columnconfigure(1, weight=1)
        self.mainScreen.grid_rowconfigure(0, weight=1)

        # create sidebar favouritesPopup with widgets
        self.loadSideFrame()

        # create console
        self.loadConsole()

        # create tabview
        self.loadTabsBox()

        # create widget favouritesPopup
        self.loadWidgetFrame()

        self.mainScreen.mainloop()

    def getDatabases(self):
        """
        gathers from /Databases, initialises as Database()
        fills self.tables
        sets up self.tabButtons
        :return:
        """
        directory = os.listdir("Databases")

        for i in directory:
            self.Databases.append(Database(i[:-3]))
        self.tables=[i.tables for i in self.Databases]
        self.tabButtons = [[] for _ in range(len(self.Databases))]

    def reLoadApp(self):
        """
        reloads mainScreen
        with updated SQL Data
        keeps selected tabview
        :return:
        """
        # Clear the existing Databases
        self.selection = []
        self.Databases.clear()

        # Reload the databases
        self.getDatabases()

        # Reload the tab view
        self.loadTabsBox()
        if self.currentTab != '':
            self.tabview.set(self.currentTab)

    def addDBDialog(self):
        """
        opens dialog to create a new database
        prompts user for name
        :return:
        """
        dialog = ctk.CTkInputDialog(text="Database Name", title="Create Database")

        def newDb(val):
            """
            connects to a new database
            :param val: name passed
            prevents duplicate names
            """
            if val:
                val.replace(" ", "_")
                if val not in [i.name for i in self.Databases]:
                    sqlite3.connect(val)
                    self.Databases.append(Database(val))
                    self.reLoadApp()
                    self.showToolTip("Database created!")
                    self.writeToLog(f"Database created: {val}")
                else:
                    self.showToolTip("Database name in use exists")

        newDb(dialog.get_input())

    def loadWidgetFrame(self):
        """
        loads the main frame
        Create Table - self.openTc
        Delete Table - self.delTable
        View Log - self.viewLog
        Create DB - self.addDBDialog
        Export Table - self.exportTable
        Import Table - self.importTable
        :return:
        """
        self.widgetFrame = ctk.CTkFrame(self.mainScreen)
        self.widgetFrame.grid(row=1, column=1, columnspan=2, padx=(20, 20), pady=(10, 10), sticky="nsew")
        self.widgetFrame.grid_columnconfigure((0, 1), weight=1)
        self.widgetFrame.grid_rowconfigure((0, 1, 2), weight=1)

        self.tableCreateButton = ctk.CTkButton(master=self.widgetFrame, text="Create New Table", command=self.openTc,
                                               font=self.regFont)
        self.tableCreateButton.grid(row=0, column=0, pady=20, padx=20, sticky="n")
        self.tableCreateButton.configure(width=210)

        self.tableDeleteButton = ctk.CTkButton(master=self.widgetFrame, text="Delete Table",
                                               command=lambda: self.confirmDeletion(self.delTable), font=self.regFont)
        self.tableDeleteButton.grid(row=1, column=0, pady=20, padx=20, sticky="n")
        self.tableDeleteButton.configure(width=210)

        self.viewLogButton = ctk.CTkButton(master=self.widgetFrame, text="View Log", command=self.viewLog,
                                           font=self.regFont)
        self.viewLogButton.grid(row=2, column=0, pady=20, padx=20, sticky="n")
        self.viewLogButton.configure(width=210)
        self.newDbButton = ctk.CTkButton(self.widgetFrame, text="Create New DB", command=self.addDBDialog,
                                         font=self.regFont)
        self.newDbButton.grid(row=0, column=1, padx=20, pady=10)
        self.newDbButton.configure(width=210)
        self.exportButton = ctk.CTkButton(self.widgetFrame, text="Export Table", command=self.exportTable,
                                          font=self.regFont)
        self.exportButton.grid(row=1, column=1, padx=20, pady=10)
        self.exportButton.configure(width=210)
        self.importButton = ctk.CTkButton(self.widgetFrame, text="Import Table", command=self.openImport,
                                          font=self.regFont)
        self.importButton.grid(row=2, column=1, padx=20, pady=10)
        self.importButton.configure(width=210)

    def confirmDeletion(self, action):
        """
        acts as a confirmation layer for sensitive deletion actions
        :param action: function of button to map to confirm button
        :return:
        """
        if self.selection:
            button = self.tableDeleteButton
            buttonGridInfo = button.grid_info()

            # Remove the original button from the grid
            button.grid_remove()

            # Create a frame to hold the Yes/No buttons
            confirmFrame = ctk.CTkFrame(self.widgetFrame)
            confirmFrame.grid(row=buttonGridInfo['row'], column=buttonGridInfo['column'], columnspan=1)

            def onConfirm(response):
                # Destroy the frame
                confirmFrame.destroy()
                # Regrid the original button
                button.grid(row=buttonGridInfo['row'], column=buttonGridInfo['column'])
                if response:
                    action()

            # Create Yes/No buttons
            yesButton = ctk.CTkButton(confirmFrame, text="Delete?", command=lambda: onConfirm("Yes"), width=105,
                                      height=28)
            yesButton.grid(row=0, column=0)
            noButton = ctk.CTkButton(confirmFrame, text="Cancel", command=lambda: onConfirm("No"), width=105, height=28)
            noButton.grid(row=0, column=1)

    def loadTabsBox(self):
        """
        loads tabView for all Databases
        calls loadFavs
        calls tableButtons
        :return:
        """
        self.tabview = ctk.CTkTabview(self.mainScreen, width=600)
        self.tabview._grid_forget_all_tabs()
        self.tabview.grid(row=0, column=1, columnspan=3, padx=(20, 20), sticky="nsew")

        self.loadFavs()
        for i in self.Databases:
            colCount = max(len(i.tables) // 5, 4)
            self.tabview.add(i.name)
            self.tabview.tab(i.name).grid_columnconfigure(list(range(colCount)), weight=1)
            self.tabview.tab(i.name).grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
            self.tableButtons(self.Databases.index(i))
    def loadFavs(self):
        """
        reads i,j from aux/favourites
        calls makeFavButton( self.tables[i][j] )
        :return:
        """
        self.tabview.add("Favourites")

        self.tabview.tab("Favourites").grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        def makeFButton(i: int, j: int,k:int):
            """
            favourites tab buttons
            do not support first click methods
                -delete table
                -export
            calls openTable(i,j)
            :param i: database index
            :param j: table index
            :return:
            """
            buttonText = self.tables[i][j].replace("_", " ")
            button = ctk.CTkButton(self.tabview.tab("Favourites"), text=buttonText,
                                   command=lambda: self.openTable(i, j),
                                   font=self.regFont)
            button.grid(row=k % 4, column=k // colCount, pady=5)


        with open('auxiliaries/favourites.txt') as file:
            s = (file.read()).split('\n')
            colCount = max(len(s) // 4, 4)
            self.tabview.tab("Favourites").grid_columnconfigure(list(range(colCount)), weight=1)
            ind = 0
            for i in (s):
                if i:
                    d = int(i[0])
                    # i.1 is letter, get 2: else 1:
                    try:
                        int(i[1])
                        t = int(i[1])
                    except  ValueError:
                        t = int(i[2:])

                    makeFButton(d, t,ind)
                    self.favourites.append((d, t))
                    ind += 1

        #Opens update favourites menu
        updateFavs = ctk.CTkButton(self.tabview.tab("Favourites"), text="Update Favourites",
                                   command=self.favouritesMenu)
        updateFavs.grid(row=4, column=colCount - 1)


    # loads main console
    def tableButtons(self, i: int):
        """
        calls makeButton(i,j) for j in i.tables
        :param i: database index
        :return:
        """
        for j in range(len(self.Databases[i].tables)):
            k = self.makeButton(i, j)
            self.tabButtons[i].append(k)

    def loadConsole(self):
        """
        generates uneditable textbox as feedback console
        :return:
        """
        self.console = ctk.CTkTextbox(self.mainScreen, width=250, state="disabled", border_width=2)
        self.console.grid(row=1, column=3, padx=(20, 20), pady=(10, 10), sticky="nsew")

    def loadSideFrame(self):
        """
        takes logo and title png from aux
        loads into side frame
        :return:
        """
        self.sideFrame = ctk.CTkFrame(self.mainScreen, width=140, corner_radius=0, border_width=2)
        self.sideFrame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sideFrame.grid_rowconfigure((0, 1, 2), weight=1)
        image = ctk.CTkImage(light_image=Image.open("auxiliaries/whc_database.png"), dark_image=Image.open(
            "auxiliaries/whc_database.png"), size=(210, 120))
        self.titleLogo = ctk.CTkLabel(self.sideFrame, text="", image=image)
        self.titleLogo.grid(row=0, column=0, padx=20, pady=(20, 10))

        image = ctk.CTkImage(light_image=Image.open("auxiliaries/logo-whc.png"), dark_image=Image.open(
            "auxiliaries/logo-whc.png"), size=(210, 180))

        self.logo = ctk.CTkLabel(self.sideFrame, image=image, text="")
        self.logo.grid(row=1, column=0, padx=20, pady=(20, 10), rowspan=2)

    def showToolTip(self, message: str):
        """
        configures console to editable momentarily
        :param message: string to be printed
        :return:
        """
        self.console.configure(state="normal")
        self.console.delete("1.0", ctk.END)
        self.console.insert("end", message)
        self.console.configure(state="disabled")

    def delTable(self):
        """
        deletes the current selected table
        adjusts
            according db tables array
            2d tables array
            tabButtons
            clears selection
        calls reloadApp
        :return:
        """
        d = self.selection[0]
        t = self.selection[1]
        db = self.Databases[d]
        
        db.removeTable(t)

        name=db.tables[t]

        del db.tables[t]
        del self.tabButtons[d][t]

        if t // 10 > 10:
            t_string = f"C{t}"
        elif t // 10 > 0:
            t_string = f"M{t}"
        else:
            t_string = f"{t}"
        with open('auxiliaries/favourites.txt', 'r') as file:
            s = (file.read()).split('\n')
        for i in s:
            if i == f"{d}{t_string}":
                s.remove(i)
        with open('auxiliaries/favourites.txt', 'w') as file:
            file.writelines(s)

        self.showToolTip(f"Table {name} has been deleted.")

        self.writeToLog(f"{name} removed from {db.name}")
        self.selection = []
        self.reLoadApp()


    def openTc(self):
        """
        opens the TableCreator if there isn't one currently open
        :return:
        """
        if self.Databases:
            children= [i.title() for i in self.mainScreen.children.values() if isinstance(i, ctk.CTkToplevel)]
            if "Table Creator" not in children:
                TableCreator(self)
        else:
            self.showToolTip("Make a Database first")

    def openTable(self, i: int, j):
        """
        opens the table based on the indices passed through (self.selection)
        resets the selected button
        :param i: database index
        :param j: table index
        :return:
        """
        Table(self,i,j)
        self.resetButton(i, j)

    def makeButton(self, i, j):
        """
        creates button with self.firstClick (wrapper function)
        grids appropriately based on index in tables
        :param i: database index
        :param j: table index
        :return: button
        """
        colcount = max(len(self.Databases[i].tables) // 5, 4)
        buttonText = self.tables[i][j].replace("_", " ")
        button = ctk.CTkButton(self.tabview.tab(self.Databases[i].name), text=buttonText,
                               command=lambda: self.firstClick(
                                   i, j), font=self.regFont)
        button.grid(row=j % 4, column=j // colcount, pady=5)
        return button

    def updateFav(self):
        """
        reads from checkbox of tables
        1 -> favourited else no
        updates favs.txt accordingly
        :return:
        """
        results = []

        for k, p in enumerate(self.favsCheckbox):
            for i, check in enumerate(p):
                if check.get() == 1:
                    if i//10>10: i_string=f"C{i}"
                    elif i//10>0: i_string=f"M{i}"
                    else: i_string=f"{i}"

                    results.append(f"{k}{i_string}\n")

        with open('auxiliaries/favourites.txt', 'w') as file:
            file.writelines(results)

        self.reLoadApp()

    def resetButton(self, i:int , j:int ):
        """
        configures button located at tabButtons[i,j]
        resets function, colour, border
        clears selection
        :param i: database index
        :param j: table index
        :return:
        """
        self.tabButtons[i][j].configure(
            text=self.tables[i][j].replace("_", " "),
            command=lambda: self.firstClick(i, j),
            fg_color="#1f6aa5",
            hover_color="#144870",
            border_width=0,
            text_color="white",
            font=self.regFont)
        self.selection = []

    def favouritesMenu(self):
        """
        opens window of checkboxes for each table in each DB
        sets value to the current favourited state reading self.favourites
        :return:
        """
        if self.favouritesPopup != None:
            self.favouritesPopup.destroy()

        self.favouritesPopup = ctk.CTkToplevel(self.mainScreen)
        self.favouritesPopup.title('Favourites')
        self.favouritesPopup.geometry = f"{100 * len(self.Databases)}x{40 * 10}"
        self.favouritesPopup.resizable(False, False)
        self.favouritesPopup.lift()
        self.favouritesPopup.focus_force()

        maxrow = 0
        for k, db in enumerate(self.Databases):
            label = ctk.CTkLabel(self.favouritesPopup, text=db.name)
            label.grid(column=k, row=0)

            self.favsCheckbox.append([])
            for j, table in enumerate(db.tables):
                var = ctk.IntVar(value=1 if (k, j) in self.favourites else 0)
                checkbox = ctk.CTkCheckBox(self.favouritesPopup, text=table.replace("_", " "), variable=var)
                checkbox.grid(column=k, row=j + 1, padx=5, pady=5)
                self.favsCheckbox[k].append(var)
                maxrow = max(maxrow, j + 1)
        saveButton = ctk.CTkButton(self.favouritesPopup, text="Save", command=self.updateFav)
        saveButton.grid(columnspan=len(self.Databases), row=maxrow + 1)

    def firstClick(self, i: int, j: int):
        """
        gives the button the function to openTable(i,j)
        configures button colour, borderd
        :param i: database index
        :param j: table index
        :return:
        """
        if self.selection != []:
            self.resetButton(self.selection[0], self.selection[1])
        self.currentTab = self.tabview.get()
        self.tabButtons[i][j].configure(
            command=lambda: self.openTable(i, j),
            fg_color="#eb9751",
            text=self.tables[i][j].replace("_", " "),
            text_color="white",
            hover_color="#a56a39",
            border_color="white",
            border_width=2,
            font=self.regFont
        )

        self.selection = [i,j]

    def exportTable(self):
        """
        export the selected table data to a CSV or PDF file.
        prompts the user to select a file path
        generates based on selected path
        csv -> CSV
        reportlab -> PDF
        calls resetButton
        """
        if self.selection != []:
            fileTypes = [("CSV files", "*.csv"), ("PDF files", "*.pdf")]
            filePath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=fileTypes)
            d = self.selection[0]
            t = self.selection[1]
            db = self.Databases[d]
            table = self.tables[d][t]

            info = db.executeSQL(f"PRAGMA TABLE_INFO({table});")
            headers = [i[1].replace("_", " ") for i in info]
            rows = db.executeSQL(f"Select * from {table};")
            rows = [[i.replace("\n"," ") if isinstance(i,str) else i for i in row] for row in rows]
            if (filePath.endswith(".csv")):
                with open(filePath, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(rows)
            elif (filePath.endswith(".pdf")):

                doc = platypus.SimpleDocTemplate(filePath, pagesize=letter)

                # Combine headers and data into a single table data structure
                tableData = [headers] + rows

                # Create a Table with the data
                title = headers[0][:-3]
                dbName = self.Databases[self.selection[0]].name.replace("_", " ")
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
                    style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey)) if i % 2 == 0 else style.append(
                        ('BACKGROUND', (0, i), (-1, i), colors.white))

                style.append(('BACKGROUND', (0, 0), (-1, 0), colors.grey))  # Headers background

                tStyle = platypus.TableStyle(style)
                table.setStyle(tStyle)
                spacer2 = spacer
                log = platypus.Paragraph(
                    f"Table Exported on {dt.datetime.now().strftime("%Y-%m-%d")} at {dt.datetime.now().strftime("%I:%m %p")}")
                # Build the PDF
                elements = [title, spacer, table, spacer2, log]
                doc.build(elements)
            self.showToolTip(f"Data exported to {filePath} successfully.")
            self.resetButton(d, t)

    def openImport(self):
        """
        opens ImportWindow if one is not currently open
        :return:
        """
        children= [i.title() for i in self.mainScreen.children.values() if isinstance(i, ctk.CTkToplevel)]
        if self.Databases and "Import Table" not in children:
            ImportTableWindow(self)

    def viewLog(self):
        """
        opens log.txt to CTkToplevel
        :return:
        """
        children = [i.title() for i in self.mainScreen.children.values() if isinstance(i, ctk.CTkToplevel)]
        if "Activity Log" not in children:
            self.logWindow=ctk.CTkToplevel(self.mainScreen)
            self.logWindow.title('Activity Log')
            self.logWindow.grid_rowconfigure(0,weight=1)
            self.logWindow.grid_columnconfigure(0,weight=1)
            self.logWindow.resizable(False,False)
            self.logWindow.geometry("600x650")
            textBox=ctk.CTkTextbox(self.logWindow)
            with open('auxiliaries/log.txt', 'r') as file:
                content = file.read()
            textBox.configure(state="normal")
            textBox.insert("end", content)
            textBox.configure(state="disabled")
            textBox.grid(padx=5,pady=5,sticky="nsew")

    def writeToLog(self,message):
        """
        writes message to log and tags the date and time
        :param message: string to be printed
        :return:
        """
        with open('auxiliaries/log.txt', 'r') as file:
            log = file.readlines()
        msg= f"-{message} - {dt.datetime.now().strftime("%Y-%m-%d")} {dt.datetime.now().strftime("%I:%M %p")}\n\n"
        log.append(msg)
        with open('auxiliaries/log.txt',"w") as file:
            file.writelines(log)


class Table:
    """
    Class Table
    Reads
        host : App
        connects to host.Databases[i] for sql queries
    """
    host = None
    parent = None
    window = None
    name = None
    colNames = []
    inputCols = []
    listbox = None
    tableTree = None
    console = None
    searchBar = None
    ascSwitch = None
    buttonFrame = None
    consoleFrame = None
    barFrame = None
    addWindow = None
    checkboxWindow = None
    descriptionEntry = None
    visibleColumns = []
    telephoneColumn=None

    def __init__(self, host, i, j: int):
        self.host = host
        self.parent = self.host.Databases[i]
        self.name = self.parent.tables[j]
        self.gatherColumns()
        self.openWindow()

    def gatherColumns(self):
        """
        query the database for table columns by self name
        loads dataTypes, colNames
        :return:
        """
        info = self.parent.executeSQL(f"PRAGMA TABLE_INFO({self.name});")
        self.colNames = [i[1] for i in info]
        self.dataTypes = [i[2] for i in info][1:]
        self.inputCols = self.colNames[1:]

    def openWindow(self):
        """
        initializes the TopLevel
        :return:
        """
        self.window = ctk.CTkToplevel(self.host.mainScreen)
        self.window.title(self.name)
        width = self.window.winfo_screenwidth()-20
        height = self.window.winfo_screenheight()-20
        self.window.geometry(f"{width}x{height}+0+0")

        self.window.resizable(True, True)
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

        self.columnFilter = ctk.CTkButton(self.barFrame, text="Filter Columns", command=self.openVisibilityWindow)
        self.columnFilter.grid(column=20, row=0, sticky='nsew')
        # Create the search button
        self.searchButton = ctk.CTkButton(self.barFrame, text="\U0001F50D", command=self.orderTable,width=6)
        self.searchButton.grid(row=0, column=6, sticky='nsew')

        if self.dataTypes.__contains__("INT") | self.dataTypes.__contains__("float"):
            self.reportBox = ctk.CTkComboBox(self.barFrame, values=[i for i in self.inputCols if
                                                                    self.dataTypes[self.inputCols.index(i)] in (
                                                                        "INT", "float")])
            self.reportBox.grid(row=0, column=11, sticky="nsew")
            ctk.CTkButton(self.barFrame, text="Print Report", command=self.columnReport,width=6).grid(row=0, column=12,
                                                                                              sticky='nsew')

        # Prepare the sort list
        sortlist = [self.colNames[0].replace("_", " ")]
        for k, i in enumerate(self.dataTypes):
            if i in ["INT", "float", "DATE"]:
                sortlist.append(self.colNames[k + 1].replace("_", " "))
        # Create the ComboBox
        if len(sortlist)>1:
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
        rows= self.parent.executeSQL(f"SELECT * FROM {self.name}")
        if(self.dataTypes.__contains__("TEXT")):
            stringIndex = self.dataTypes.index("TEXT")
            for i in rows:
                j = i[stringIndex + 1]
                charCount = len(j)
                lineCount= len(j.splitlines())
                self.host.height = max((charCount//30) * 20, self.host.height,lineCount*20)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure('Treeview',
                        fieldbackground="white",
                        rowheight=self.host.height,font=self.host.regFont,
                        borderwidth=2)
        style.map('Treeview', background=[('selected', '#1f6aa5')])

        self.tableTree = ttk.Treeview(self.window, show="headings", style="Treeview")
        self.tableTree.tag_configure("oddrow", background="#dddee0")
        self.tableTree.grid(row=2, column=0, columnspan=2, rowspan=8, sticky="nsew")
        self.tableTree["columns"] = self.colNames
        self.visibleColumns = self.colNames
        for col in self.colNames:
            self.tableTree.heading(col, text=col.replace("_", " "))
            self.tableTree.column(col, anchor=ctk.W)

        self.orderTable()  # ASCENDING ID,, DEFAULT

    def loadButtonFrame(self):
        self.buttonFrame = ctk.CTkFrame(self.window)
        self.buttonFrame.grid(row=10, column=0, sticky="nsew")
        self.buttonFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.buttonFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        button = ctk.CTkButton(self.buttonFrame, text="Add Entry", command=self.openAddWindow)
        button.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=10, columnspan=2)
        updateButton = ctk.CTkButton(self.buttonFrame, text="Update Entry", command=self.openUpdateCallback)
        updateButton.grid(row=0, column=2, rowspan=4, sticky="nsew", padx=10, pady=10, columnspan=2)
        self.removeButton = ctk.CTkButton(self.buttonFrame, text="Delete Entry", command=lambda: self.confirmDeletion(
            self.delEntry))
        self.removeButton.grid(row=0, column=4, rowspan=4, sticky="nsew", padx=10, pady=10, columnspan=2)

    def showConsoleFrame(self):
        self.consoleFrame = ctk.CTkFrame(self.window)
        self.consoleFrame.grid(row=10, column=1, sticky="nsew")

        self.consoleFrame.grid_columnconfigure(1, weight=1)
        self.consoleFrame.grid_columnconfigure((0, 2), weight=0)
        self.console = ctk.CTkTextbox(self.consoleFrame, state="disabled", height=150, width=450, border_width=2)
        self.console.grid(column=1, padx=5, pady=5, sticky="nsew")

    def openAddWindow(self):
        children = [i.title() for i in self.window.children.values() if isinstance(i, ctk.CTkToplevel)]
        if "Add Entry" not in children:
            self.addEntries = []
            self.addWindow = ctk.CTkToplevel(self.window)
            self.addWindow.lift()
            self.addWindow.focus_force()
            self.addWindow.geometry(f"{160 * len(self.inputCols)}x110")
            self.addWindow.resizable(False, False)
            self.addWindow.grid_rowconfigure((0, 1), weight=1)
            self.addWindow.grid_columnconfigure(list(range(len(self.inputCols))), weight=1)
            self.addWindow.title("Add Entry")
            maxrow = 0
            column = 0
            for k, i in enumerate(self.inputCols):
                label = ctk.CTkLabel(self.addWindow, text=f"{i.replace('_', ' ')}:")
                if self.dataTypes[k] == "TEXT":
                    self.descriptionColumn = i.replace('_', ' ')
                    self.descriptionEntry = ctk.CTkTextbox(self.addWindow, border_width=2, height=80)
                    self.addWindow.geometry(f"{max(150 * (len(self.inputCols) - 1), 200)}x{220}")
                    label.grid(row=2, columnspan=len(self.inputCols) - 1, sticky="nsew", pady=2)
                    self.descriptionEntry.grid(row=3, columnspan=len(self.inputCols) - 1, sticky="nsew", pady=5, padx=10)
                    self.addWindow.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
                    maxrow = max(3, maxrow)
                elif self.dataTypes[k] == "varchar(30)":
                    self.addWindow.geometry(f"{max(150 * (len(self.inputCols) - 1), 350)}x{110}")
                    self.telephoneColumn= i.replace('_', ' ')
                    label.grid(row=0, column=column, sticky="nsew", pady=2, padx=10)
                    self.telephoneEntry(column,self.addWindow)
                    column += 1
                    maxrow = max(1, maxrow)
                else:
                    entry = ctk.CTkEntry(self.addWindow)
                    label.grid(row=0, column=column, sticky="nsew", padx=10, pady=2)
                    entry.grid(row=1, column=column, sticky="nsew", padx=10, pady=5)
                    column += 1
                    maxrow = max(1, maxrow)
                    self.addEntries.append(entry)

            button = ctk.CTkButton(self.addWindow, text="Submit", command=self.addEntryCallback)
            self.addWindow.grid_columnconfigure([list(range(column)) if column>0 else 0], weight=1)
            self.addWindow.grid_rowconfigure(1, weight=1)
            button.grid(row=maxrow + 1, columnspan=len(self.inputCols))

    def openUpdateCallback(self):
        selectedItem = self.tableTree.selection()
        if selectedItem:
            vals = self.tableTree.item(selectedItem, 'values')

            self.openUpdateWindow(vals)

    def columnReport(self):
        colName = self.reportBox.get()
        result = self.parent.executeSQL(f"SELECT MAX({colName}), MIN({colName}), SUM({colName}), AVG({colName}) FROM {self.name}")[0]
        # Print the summary to the textbox
        summaryMessage = f"Summary for {colName}:\n"
        summaryMessage += f"Max: {result[0]}\n"
        summaryMessage += f"Min: {result[1]}\n"
        summaryMessage += f"Total: {result[2]}\n"
        summaryMessage += f"Average: {result[3]}\n"
        self.showToolTip(summaryMessage)

    def openUpdateWindow(self, vals: list):
        children = [i.title() for i in self.window.children.values() if isinstance(i, ctk.CTkToplevel)]
        if "Update Entry" not in children:
            self.updateEntries = []
            self.updateWindow = ctk.CTkToplevel(self.window)
            self.updateWindow.lift()
            self.updateWindow.focus_force()
            self.updateWindow.geometry(f"{150 * len(self.inputCols)}x110")
            id = vals[0]
            vals = vals[1:]
            maxrow = 0
            column = 0

            self.updateWindow.title(f"Update Entry")
            self.updateWindow.grid_rowconfigure(1, weight=1)

            for k, i in enumerate(self.inputCols):
                label = ctk.CTkLabel(self.updateWindow, text=f"{i.replace('_', ' ')}:")
                if self.dataTypes[k] == "TEXT":#Description size
                    self.descriptionColumn = i.replace('_', ' ')
                    self.descriptionEntry = ctk.CTkTextbox(self.updateWindow, border_width=2, height=80)
                    self.descriptionEntry.configure(height=80)
                    self.descriptionEntry.insert(1.0, vals[k])
                    label.grid(row=2, columnspan=len(self.inputCols) - 1, sticky="nsew", pady=2, padx=5)
                    self.descriptionEntry.grid(row=3, columnspan=len(self.inputCols) - 1, sticky="nsew", pady=5, padx=5)
                    self.updateWindow.geometry(f"{200 * (len(self.inputCols) - 1)}x{300}")
                    self.updateWindow.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
                    maxrow = max(3, maxrow)
                elif self.dataTypes[k] == "varchar(30)":#Telephone Size
                    self.telephoneColumn= i.replace('_', ' ')
                    label.grid(row=0, column=column, sticky="nsew", padx=5, pady=2)
                    self.telephoneEntry(column,self.updateWindow)
                    self.updateWindow.geometry(f"{max(150 * (len(self.inputCols) - 1), 350)}x{110}")

                    self.block1.insert(0,vals[k][:3])
                    self.block2.insert(0,vals[k][4:7])
                    self.block3.insert(0,vals[k][8:12])
                    if len(vals[k]) > 12:
                        self.ext.insert(0,vals[k][14:-1])
                    column += 1
                    maxrow = max(1, maxrow)
                else:
                    entry = ctk.CTkEntry(self.updateWindow, placeholder_text=vals[k])
                    label.grid(row=0, column=column, sticky="nsew", padx=5, pady=2)
                    entry.grid(row=1, column=column, sticky="nsew", padx=5, pady=5)

                    self.updateEntries.append(entry)
            self.updateWindow.grid_columnconfigure(list(range(column)), weight=1)
            button = ctk.CTkButton(self.updateWindow, text="Submit", command=lambda: self.updateEntry(id))

            button.grid(row=maxrow + 1, columnspan=len(self.inputCols))

    def openVisibilityWindow(self):
        children = [i.title() for i in self.window.children.values() if isinstance(i, ctk.CTkToplevel)]
        if "Filter View" not in children:
            colCount = len(self.colNames) // 3 + 1
            self.checkboxWindow = ctk.CTkToplevel(self.window)
            self.checkboxWindow.title("Filter View")
            ctk.CTkLabel(self.checkboxWindow, text="Select Columns").grid(row=0, sticky='nsew', columnspan=colCount)
            self.checkboxWindow.grid_columnconfigure(list(range(colCount - 1)), weight=1)
            self.checkboxWindow.grid_rowconfigure(list(range(5)), weight=1)
            self.checkboxWindow.geometry(f"{300}x{150}")
            self.checkboxWindow.resizable(False, False)

            self.checkVars = []
            for i, col in enumerate(self.colNames):
                j = ctk.BooleanVar(value=col in self.visibleColumns)
                self.checkVars.append(j)
                chk = ctk.CTkCheckBox(self.checkboxWindow, text=col.replace("_", " "), variable=j)
                chk.grid(row=i % 3 + 1, column=i // 3, pady=3, padx=3)

            confirmButton = ctk.CTkButton(self.checkboxWindow, text="Confirm", command=self.updateVisibleColumns)
            confirmButton.grid(row=4, sticky='nsew', columnspan=colCount)

    def updateVisibleColumns(self):
        self.visibleColumns = [self.colNames[k] for k, var in enumerate(self.checkVars) if var.get()]
        self.tableTree.config(displaycolumns=self.visibleColumns)
        self.checkboxWindow.destroy()
        self.adjustColumnWidths()  # Adjust the column widths after updating visible columns

    def adjustColumnWidths(self):
        total_width = self.tableTree.winfo_width()
        num_columns = len(self.visibleColumns)
        if num_columns > 0:
            column_width = total_width // num_columns
            for col in self.visibleColumns:
                self.tableTree.column(col, width=column_width)

    def orderTable(self):
        """
        Orders the table using
        state of the selected sorting column
        state of the search bar
        """
        order = "DESC" if self.ascSwitch.get() == 1 else "ASC"

        sqlstring = f"SELECT * FROM {self.name}"
        search = self.searchBar.get()
        params=None
        if search != "":
            sqlstring += f" WHERE "
            sqlstring += " OR ".join([f"{i} LIKE ?" for i in self.colNames])
            params = [f"%{search}%"] * len(self.colNames)
        if self.listbox:
            sqlstring += f" ORDER BY {self.listbox.get().replace(" ", "_")} {order}"
        else:
            sqlstring += f" ORDER BY {self.name}_ID {order}"
        if params:
            rows =self.parent.executeSQL(sqlstring,params)
        else:
            rows = self.parent.executeSQL(sqlstring)
        self.tableTree.delete(*self.tableTree.get_children())

        if len(rows) > 12:
            scrollbar = ttk.Scrollbar(self.window, orient='vertical', command=self.tableTree.yview)
            scrollbar.grid(row=2, column=3,rowspan=8,sticky='ns')
            self.tableTree.configure(yscrollcommand=scrollbar.set)

        for j, newrow in enumerate(rows):
            tag = 'oddrow' if j % 2 == 0 else 'evenrow'
            self.tableTree.insert("", ctk.END, values=newrow, tags=tag)

    def confirmDeletion(self, action):
        self.selectedRow = self.tableTree.selection()
        if self.selectedRow:
            button = self.removeButton

            # Remove the original button from the grid
            button.grid_remove()

            # Create a frame to hold the Yes/No buttons

            def onConfirm(response):

                # Destroy the frame
                yesButton.destroy()
                noButton.destroy()
                # Regrid the original button
                button.grid(row=0, column=4, rowspan=4, sticky="nsew", padx=10, pady=10, columnspan=2)

                if response:
                    action()

            # Create Yes/No buttons
            yesButton = ctk.CTkButton(self.buttonFrame, text="Delete?", command=lambda: onConfirm("Yes"), width=120)
            yesButton.grid(row=0, column=4, sticky="nsew", rowspan=4, padx=(10, 2), pady=10)
            noButton = ctk.CTkButton(self.buttonFrame, text="Cancel", command=lambda: onConfirm("No"), width=120)
            noButton.grid(row=0, column=5, sticky="nsew", rowspan=4, padx=(2, 10), pady=10)

    def delEntry(self):
        vals = self.tableTree.item(self.selectedRow, 'values')
        self.parent.executeSQL(f"DELETE FROM {self.name} WHERE {self.name}_ID=?;", vals[0])
        self.showToolTip(f"Instance with ID: {vals[0]} Deleted")
        self.host.writeToLog(f"ID: {vals[0]} Deleted from {self.name} ({self.parent.name})")
        self.orderTable()

    def limitEntry(self,entry, limit):
        def callback(event):
            if len(entry.get()) >= limit:
                entry.delete(limit, ctk.END)

        entry.bind('<KeyRelease>', callback)

    def telephoneEntry(self, i: int,window: ctk.CTkToplevel):
        frame = ctk.CTkFrame(window,height=25)
        frame.grid(row=1, column=i, sticky='nsew',padx=5, pady=2)
        frame.grid_columnconfigure((0, 2, 4, 6), weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # First part (3 digits)
        self.block1 = ctk.CTkEntry(frame, width=50)
        self.block1.grid(row=0, column=0, sticky='ew')
        self.limitEntry(self.block1, 3)

        # Dash separator
        ctk.CTkLabel(frame, text="-").grid(row=0, column=1, sticky='ew')

        # Second part (3 digits)
        self.block2 = ctk.CTkEntry(frame, width=50)
        self.block2.grid(row=0, column=2,sticky='ew')
        self.limitEntry(self.block2, 3)

        # Dash separator
        ctk.CTkLabel(frame, text="-").grid(row=0, column=3,sticky='ew')

        # Third part (4 digits)
        self.block3 = ctk.CTkEntry(frame, width=65)
        self.block3.grid(row=0, column=4,sticky='ew')
        self.limitEntry(self.block3, 4)

        # Extension label
        ctk.CTkLabel(frame, text=" ex: ").grid(row=0, column=5,sticky='ew')

        # Extension part (5 digits)
        self.ext = ctk.CTkEntry(frame, width=70)
        self.ext.grid(row=0, column=6,sticky='ew')
        self.limitEntry(self.ext, 5)
    
    def submitPhoneEntry(self)-> str:
        first= self.block1.get()
        second= self.block2.get()
        third= self.block3.get()
        ext= self.ext.get()
        
        if ext!="":
            return f"{first}-{second}-{third} ({ext})"
        else:
            return f"{first}-{second}-{third}"
            

    def addEntryCallback(self):
        
        vals = [i.get() for i in self.addEntries]
        if self.descriptionEntry:
            vals.insert(self.inputCols.index(self.descriptionColumn), self.descriptionEntry.get(1.0, ctk.END))
        if self.telephoneColumn:
            vals.insert(self.inputCols.index(self.telephoneColumn), self.submitPhoneEntry())
        try:
            self.parent.addEntry(vals, self.parent.tables.index(self.name))
            self.orderTable()
            self.showToolTip("Entry Submitted!")
            self.host.writeToLog(f"Entry added to {self.name} ({self.parent.name})")
            self.addWindow.destroy()
        except sqlite3.Error as e:
            self.showToolTip(f"Format Error: {e}")
        except ValueError:
            self.showToolTip("Fill Rows Properly")

    # update an entry
    def updateEntry(self, id):
        params = []
        filledIn = [i.get() for i in self.updateEntries]
        if self.descriptionEntry:
            if self.descriptionEntry.get(1.0, ctk.END) != "":
                filledIn.insert(self.inputCols.index(self.descriptionColumn), self.descriptionEntry.get(1.0, ctk.END))
        if self.telephoneColumn:
            filledIn.insert(self.inputCols.index(self.telephoneColumn), self.submitPhoneEntry())
        sqlstring = ""
        for j, i in enumerate(filledIn):
            if i != "":
                sqlstring += f"{self.inputCols[j]}=?, "
                params.append(filledIn[j])
        sqlstring = sqlstring[:-2]
        try:
            self.parent.executeSQL(f"UPDATE {self.name} SET {sqlstring} WHERE {self.name}_ID = {id};", params)
            self.updateWindow.destroy()
            self.orderTable()
        except sqlite3.Error as e:
            self.showToolTip(f"Format Error: {e}")

    def showToolTip(self, text):
        self.console.configure(state="normal")
        self.console.delete("1.0", ctk.END)
        self.console.insert("end", text)
        self.console.configure(state="disabled")

    def close(self):
        self.window.destroy()


class Database:
    conn = None
    c = None
    name = None
    tables = []
    path = None

    def __init__(self, path):
        self.path = path + ".db"
        self.loadTables()
        self.name = self.getName()

    def connect(self):
        dbPath = os.path.join('Databases', self.path)
        self.conn = sqlite3.connect(dbPath)
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

    def removeTable(self, j: int) -> None:
        self.executeSQL(f"DROP TABLE if exists {self.tables[j]};")
    def executeSQL(self,query, params=None):
        self.connect()
        if params:
            self.c.execute(query, params)
        else:
            self.c.execute(query)
        self.conn.commit()
        info = self.c.fetchall()
        self.close()
        return info

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
        tables = self.executeSQL("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';")

        self.tables = [i[0] for i in tables]


    def addEntry(self, vals, index: int):
        if all(vals):
            placeholders = ','.join(['?'] * len(vals))
            self.executeSQL(f"INSERT INTO {self.tables[index]} VALUES (NULL, {placeholders});", vals)
        else:
            raise ValueError


class TableCreator:
    def __init__(self, parent: App):
        self.parent = parent
        self.popup = None
        self.console = None
        self.entries = []
        self.comboboxes = []
        self.frameTop = None
        self.frameMiddle = None
        self.frameBottom = None
        self.types = {
            "Name / Address": "varchar(50)",
            "Whole Number": "int",
            "Money (Decimal)": "float",
            "Date": "date",
            "Phone Number": "varchar(30)",
            "Description": "text"
        }
        self.setTable()

    def close(self):
        self.popup.destroy()

    def setTable(self):
        self.popup = ctk.CTkToplevel(self.parent.mainScreen)
        self.popup.transient(self.parent.mainScreen)
        self.popup.title("Table Creator")
        self.popup.geometry(f"{500}x{660}")

        self.popup.lift()
        self.popup.focus_force()

        self.popup.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.popup.grid_columnconfigure(0, weight=1)

        databaseNames = [db.name.replace("_", " ") for db in self.parent.Databases]
        self.highestFrame = ctk.CTkFrame(self.popup)
        self.highestFrame.grid(row=0)

        self.dbMenu = ctk.CTkOptionMenu(self.highestFrame, values=databaseNames)
        if self.parent.tabview.get() != "Favourites":
            self.dbMenu.set(self.parent.tabview.get())
        self.dbMenu.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.frameTop = ctk.CTkFrame(self.popup)
        self.frameTop.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frameTop.grid_columnconfigure(0, weight=1)
        self.frameTop.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frameTop, text="Table Name:").grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.tableNameEntry = ctk.CTkEntry(self.frameTop)
        self.tableNameEntry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.frameMiddle = ctk.CTkFrame(self.popup)
        self.frameMiddle.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frameMiddle.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.frameMiddle, text="Column Name").grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(self.frameMiddle, text="Column Type").grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.entries = []
        self.comboboxes = []

        for i in range(1, 11):
            rowFrame = ctk.CTkFrame(self.frameMiddle)
            rowFrame.grid(row=i, column=0, pady=2, sticky="ew", columnspan=2)
            rowFrame.grid_columnconfigure(0, weight=1)
            rowFrame.grid_columnconfigure(1, weight=1)

            entry = ctk.CTkEntry(rowFrame)
            entry.grid(row=0, column=0, padx=5, sticky="ew")
            self.entries.append(entry)

            combobox = ctk.CTkComboBox(rowFrame, values=list(self.types.keys()))
            combobox.set('')
            combobox.grid(row=0, column=1, padx=5, sticky="ew")
            self.comboboxes.append(combobox)

        self.frameBottom = ctk.CTkFrame(self.popup)
        self.frameBottom.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.frameBottom.grid_columnconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(self.frameBottom, height=2, width=120, state="disabled", font=self.parent.regFont,
                                      border_width=2)
        self.console.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        self.confirmButton = ctk.CTkButton(self.popup, text="Create Table", command=self.submitTable)
        self.confirmButton.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        exitButton = ctk.CTkButton(self.popup, text="Exit", command=self.close)
        exitButton.grid(row=5, column=0, pady=10, padx=20, sticky="ew")

    def submitTable(self):
        tableName = self.tableNameEntry.get().replace(" ", "_")
        if any(tableName in i for i in self.parent.tables):
            self.showTooltip("Table name in use")
        else:
            columnNames = [entry.get().replace(" ", "_") for entry in self.entries if entry.get()]
            columnTypes = [combobox.get() for combobox in self.comboboxes if combobox.get()]
            descriptionCount = columnTypes.count("Description")

            if all(columnNames) and all(columnTypes) and descriptionCount < 2 and tableName:
                dbName = self.dbMenu.get().replace(" ", "_")
                self.createTable(dbName, tableName, columnNames, columnTypes)
                self.close()
                self.parent.showToolTip(f"{tableName.replace("_"," ")} generated in {dbName}")

                self.parent.writeToLog(f"Table {tableName} added to {dbName}")
                self.parent.reLoadApp()
            elif descriptionCount >= 2:
                self.showTooltip("Only use 1 description column")
            elif not tableName:
                self.showTooltip("Name the table")
            else:
                self.showTooltip("Fill Rows Properly")

    def createTable(self, host: str, tableName: str, columnNames: list, columnTypes: list) -> None:
        db = Database(host)
        columns = [f"{tableName}_ID INTEGER PRIMARY KEY AUTOINCREMENT"]
        for colName, colType in zip(columnNames, columnTypes):
            columns.append(f"{colName} {self.types[colType]}")


        columnstr = ", ".join(columns)

        try:
            db.tables.append(tableName)
            x=f"CREATE TABLE {tableName} ({columnstr});"
            db.executeSQL(x)
        except sqlite3.Error as e:
            self.showTooltip(f"Format Error: {e}")



    def showTooltip(self, message: str):
        self.console.configure(state='normal')
        self.console.delete("1.0", ctk.END)
        self.console.insert("1.0", message)
        self.console.configure(state='disabled')


class ImportTableWindow(TableCreator):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.popup.geometry(f"{500}x{300}")
        self.popup.title("Import Table")
        self.headerVar = ctk.IntVar(value=1)
        self.frameMiddle.grid_forget()

        ctk.CTkButton(self.highestFrame, text="Import", command=self.openFileDialog).grid(row=0, column=1, padx=20,
                                                                                          pady=(20, 10), sticky="ew")

    def openFileDialog(self):
        self.filePath = filedialog.askopenfilename(title="Select a File",
                                                   filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if self.filePath:
            self.popup.geometry(f"{500}x{620}")
            with open(self.filePath, 'r') as csvFile:
                firstLine = csvFile.readline()
                self.numColumns = firstLine.count(',') + 1

            self.headerCheckBox = ctk.CTkCheckBox(self.frameTop, text="Column Headers in File?",
                                                  variable=self.headerVar,
                                                  command=self.displayColumnInputs)
            self.headerCheckBox.grid(columnspan=2, row=2)

            self.frameMiddle = ctk.CTkFrame(self.popup)
            self.frameMiddle.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
            self.frameMiddle.grid_columnconfigure(0, weight=1)
            self.frameMiddle.grid_rowconfigure(0, weight=1)
            self.frameLeft = ctk.CTkFrame(self.frameMiddle)
            self.frameLeft.grid(column=0, row=0)

            self.frameRight = ctk.CTkFrame(self.frameMiddle)
            ctk.CTkLabel(self.frameRight, text="Column Name").grid(row=0, column=0, padx=5, pady=2, sticky="ew")
            ctk.CTkLabel(self.frameLeft, text="Column Type").grid(row=0, column=0, padx=5, pady=2, sticky="ew")

            self.columnEntries = []
            self.columnTypeComboboxes = []

            for i in range(1, self.numColumns + 1):
                entryFrame = ctk.CTkFrame(self.frameRight)
                entryFrame.grid(row=i, column=0, pady=2, sticky="ew")
                entryFrame.grid_columnconfigure(0, weight=1)
                entryFrame.grid_columnconfigure(1, weight=1)

                columnEntry = ctk.CTkEntry(entryFrame)
                columnEntry.grid(row=0, column=0, padx=5, sticky="ew")
                self.columnEntries.append(columnEntry)

                comboboxFrame = ctk.CTkFrame(self.frameLeft)
                columnTypeCombobox = ctk.CTkComboBox(comboboxFrame, values=list(self.types.keys()))
                columnTypeCombobox.set('')
                columnTypeCombobox.grid(row=0, column=0, padx=5, sticky="ew")
                comboboxFrame.grid(row=i, column=0, pady=2, sticky="ew")
                comboboxFrame.grid_columnconfigure(0, weight=1)
                comboboxFrame.grid_columnconfigure(1, weight=1)
                self.columnTypeComboboxes.append(columnTypeCombobox)

            self.confirmButton.configure(command=self.readCSVFile)

    def displayColumnInputs(self):
        if self.headerCheckBox.get() == 0:
            self.frameMiddle.grid_columnconfigure((0, 1), weight=1)
            self.frameRight.grid(column=1, row=0)
        else:
            self.frameMiddle.grid_columnconfigure(1, weight=0)
            self.frameRight.grid_forget()

    def readCSVFile(self):
        with open(self.filePath, 'r') as csvFile:
            self.csvReader = list(csv.reader(csvFile, delimiter='\t'))

        self.selectedDatabase = self.dbMenu.get()

        if (self.headerVar.get() == 1):
            headers = [i.replace(" ", "_") for i in self.csvReader[0][0].split(",")]
            columnTypes = [combobox.get() for combobox in self.columnTypeComboboxes]
            name = self.tableNameEntry.get()
            if all(columnTypes) and all([name not in i for i in self.parent.tables]):
                chars_to_remove = '"\''
                headers = [''.join([c for c in i if c not in chars_to_remove])for i in headers]
                self.createTable(self.selectedDatabase.replace(" ", "_"), name, headers,
                                 columnTypes)
            elif not all(columnTypes):
                self.showTooltip("Fill types properly")
            elif not name:
                self.showTooltip("Name the table")
            elif (name in i for i in self.parent.tables):
                self.showTooltip("Table name in use")
        else:
            self.submitTable()
        self.populateTable()

    def populateTable(self):
        db = Database(self.selectedDatabase.replace(" ", "_"))
        db.tables.append(self.tableNameEntry.get())
        startIndex = self.headerVar.get()

        while startIndex < len(self.csvReader):
            vals = [i for i in self.csvReader[startIndex][0].split(",")]
            db.addEntry(vals, len(db.tables)-1)
            startIndex += 1
        self.close()
        self.parent.reLoadApp()
