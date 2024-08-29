import csv
import os
import sqlite3
import datetime as dt
from tkinter import ttk, filedialog,messagebox
import customtkinter as ctk
import reportlab
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, TableStyle, Paragraph, Spacer


class App:
    buttonColour = "#1f6aa5"
    selection=""
    selectedButton=None
    currentTab=""
    window = None
    Databases = []
    loaded=[]
    currentTc=None



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

        self.favTableButton = ctk.CTkButton(master=self.widgetFrame, text="Toggle Favourite", command=self.toggleFav, font=self.regFont)
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
        self.tabview.add("Favourites")
        self.tabview.tab("Favourites").grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.tabview.tab("Favourites").grid_rowconfigure((0, 1, 2, 3), weight=1)
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
            i, j, button), font=self.regFont)
        button.grid(row=j%3, column=int(j/3), pady=5)
        return button

    def makeFButton(self, i:int , j: int):
        buttonText = self.Databases[i].tables[j].replace("_", " ")
        button = ctk.CTkButton(self.tabview.tab("Favourites"), text=buttonText, command=lambda: self.openTable(i, j), font=self.regFont)
        button.grid(row=j, column=int(j/4), pady=5)
        return button

    def toggleFav(self):
        pair = f"{self.selection[0]} {self.selection[1]}\n"

        with open('auxiliaries/favourites.txt', 'r') as file:
            lines = file.readlines()

        if pair in lines:
            lines.remove(pair)
            self.TTC("Removed From Favourites")
        else:
            lines.append(pair)
            self.TTC("Added to Favourites")
        with open('auxiliaries/favourites.txt', 'w') as file:
            file.writelines(lines)

        self.resetButton(int(self.selection[0]), int(self.selection[1]))
        self.reLoadApp()

    def resetButton(self,i,j):
        self.tabButtons[i][j].configure(
            text=self.Databases[i].tables[j].replace("_", " "),
            command=lambda: self.firstClick(i, j, self.tabButtons[i][j]),
            fg_color=self.buttonColour,
            hover_color="#144870",
            border_width=0,
            text_color="white",
            font=self.regFont)
        self.selection = ""


    def firstClick(self, i: int, j: int,b: ctk.CTkButton):
        if self.selection!="":
            self.resetButton(int(self.selection[0]), int(self.selection[1]))
        self.currentTab=self.tabview.get()
        b.configure(
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
        self.loaded.append('Favourites')
        with open('auxiliaries/favourites.txt') as file:
            s=(file.read()).split('\n')
            for i in (s):
                if i:
                    self.makeFButton(int(i[0]), int(i[2]))

    def createExport(self,fileName:str):
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

            doc = SimpleDocTemplate(fileName, pagesize=letter)

            # Combine headers and data into a single currentTable data structure
            tableData = [headers] + rows

            # Create a Table with the data
            title= headers[0][:-3]
            dbName= self.Databases[int(self.selection[0])].name.replace("_", " ")
            styles = getSampleStyleSheet()
            title_style = styles['Title']

            # Create a title paragraph
            title = Paragraph(dbName + " - " + title, title_style)

            # Create a spacer
            spacer = Spacer(1, 0.2 * inch)
            table = reportlab.platypus.Table(tableData)

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

            tStyle= TableStyle(style)
            table.setStyle(tStyle)
            spacer2=spacer
            log= Paragraph(f"Table Exported on {dt.datetime.now().strftime("%Y-%m-%d")} at {dt.datetime.now().strftime("%I:%m %p")}")
            # Build the PDF
            elements = [title,spacer,table,spacer2,log]
            doc.build(elements)
            self.TTC(f"Data exported to {fileName} successfully.")

    def exportTable(self):
        if self.selection!="":
            fileTypes = [("CSV files", "*.csv"), ("PDF files", "*.pdf")]
            filePath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=fileTypes)
            self.createExport(filePath)
            self.resetButton(self.selection[0],self.selection[1])
            self.selection=""