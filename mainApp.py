import os
import sqlite3
import datetime as dt
import tkinter
from tkinter import ttk

import customtkinter as ctk

class Database:
    conn = None
    c = None
    name = None
    tables = []
    path = None

    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.load_tables()
        self.name = self.get_name()

    def remove_table(self, tname) -> None:
        self.c.execute(f"DROP TABLE {tname};")
        self.conn.commit()
        self.type_to_console(f"{tname} Deleted")

    def get_name(self):
        name = []
        for c in self.path:
            if c == '.':
                break
            name.append(c)
        return "".join(name)

    def load_tables(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';")
        list = self.c.fetchall()
        self.tables = [i[0] for i in list]


class Table:
    app=None
    parent = None
    name = None
    cols = {}
    colarr = []
    colinps = []
    entries = []##
    window = None
    del_ent = None
    search_ent = None
    listbox = None
    tree = None
    input_frame=None
    frame_bottom = None
    console = None
    search_bar=None
    sort_box=None
    ascdesc=None
    bar_frame=None

    def __init__(self, db, i: int,app):
        self.parent = db
        self.app=app
        self.name = db.tables[i]
        self.gather_cols()
        self.open_window()

    def type_to_console(self, message: str):
        self.console.configure(state='normal')
        self.console.delete("1.0", ctk.END)
        self.console.insert("1.0", message)
        self.console.configure(state='disabled')

    def delete_entry(self, id) -> None:
        self.parent.c.execute(f"SELECT * FROM {self.name} WHERE {self.name}id = ?", (id,))
        result = self.parent.c.fetchone()
        if result:
            self.parent.c.execute(f"DELETE FROM {self.name} WHERE id=?;", (id,))
            self.type_to_console(f"Instance with ID: {id} Deleted")
        else:
            self.type_to_console(f"Instance with ID: {id} Does Not Exist")

    def show_table(self):

        label = ctk.CTkLabel(self.window, text=self.name, font=("Helvetica", 24))
        label.grid(row=0, column=0, padx=10,  sticky="nsew")


        self.bar_frame=ctk.CTkFrame(self.window,height=25)
        self.bar_frame.grid(row=1, columnspan=4, sticky ='nsew' )
        self.make_search_frame()


        self.tree = ttk.Treeview(self.window, show="headings")
        self.tree.grid(row=2, sticky="nsew")
        self.tree["columns"] = self.colarr

        for col in self.colarr:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=ctk.W)

        rows = self.get_rows()

        for row in rows:
            self.tree.insert("", ctk.END, values=row)

    def make_search_frame(self):
        # Configure the grid layout for the parent frame
        self.bar_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

        # Create the search bar entry
        self.search_bar = ctk.CTkEntry(self.bar_frame)
        self.search_bar.grid(row=0, column=0, columnspan=2, sticky='nsew')

        # Create the search button
        self.search_button = ctk.CTkButton(self.bar_frame, text="\U0001F50D Search", command=lambda: self.search_filter(self.search_bar.get()))
        self.search_button.grid(row=0, column=2, sticky='nsew')

        # Prepare the sort list
        sortlist = []
        for i in self.colinps:
            if self.cols[i] in ["INT", "FLOAT", "DATE"]:
                sortlist.append(i)

        # Create the ComboBox
        self.listbox = ctk.CTkComboBox(self.bar_frame, values=sortlist)
        self.listbox.set(self.colarr[0])  # Set the initial value
        self.listbox.grid(row=0, column=3, columnspan=2, sticky='nsew')

        # Create the switch
        switch_var = ctk.IntVar()
        self.ascdesc = ctk.CTkSwitch(self.bar_frame, text="\u2191/\u2193", variable=switch_var, offvalue=0, onvalue=1)
        self.ascdesc.grid(row=0, column=5, sticky='nsew')

        # Set the command for the switch
        self.ascdesc.configure(command=self.switch_callback)

    def switch_callback(self):
            self.sort_table(self.listbox.get(),self.ascdesc.get())





    def search_filter(self,text):
        """
        Searches for the text in any column of the specified table.
        :param table: table to search
        :param text: text to search for
        :return: NONE vj do display
        """
        columns = self.gather_cols()
        query = f"SELECT * FROM {self.name} WHERE "
        query += " OR ".join([f"{i} LIKE ?" for i in self.colarr])
        params = [f"%{text}%"] * len(self.cols)

        self.parent.c.execute(query, params)
        #show this table veej

    def sort_table(self, col, dir: int) -> None:
        """
        Takes in
        choice from all columns of type (number, money, date),
        either up or down (VJ IDEALLY MAKE THIS A SEXY LOOKING ON/OFF SWITCH)
        ->
        displays table accordingly
        """
        if dir==1:
            order="DESC"
        else:
            order="ASC"

        self.parent.c.execute(f"SELECT * FROM {self.name} ORDER BY {col} {order}")

    def get_rows(self) -> list:
        self.parent.c.execute(f"SELECT * FROM {self.name};")
        rows = self.parent.c.fetchall()
        return rows

    def gather_cols(self):
        self.parent.c.execute(f"PRAGMA TABLE_INFO({self.name});")
        info = self.parent.c.fetchall()
        self.cols = {i[1]: i[2] for i in info}
        self.colarr = list(self.cols.keys())
        self.colinps = self.colarr[1:-1]

    def open_window(self):
        self.window = ctk.CTk()
        self.window.geometry('500x500')
        self.window.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.window.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.show_table()
        label = ctk.CTkLabel(self.window, text="Remove By ID")
        label.grid(row=3, column=0, padx=5)
        self.del_ent = ctk.CTkEntry(self.window)
        self.del_ent.grid(row=5, column=0, padx=5)
        remove_confirm = ctk.CTkButton(self.window, text="Confirm", command=self.read_del)
        remove_confirm.grid(row=6, column=0, padx=5)
        button = ctk.CTkButton(self.window, text="Close", command=self.window.destroy)
        input_frame(self)
        button.grid(row=7, column=0, padx=5)
        self.frame_bottom = ctk.CTkFrame(self.window)
        self.frame_bottom.grid(row=8, column=0)
        self.console = ctk.CTkTextbox(self.frame_bottom, height=4, width=200, state="disabled")
        self.console.grid(row=0, column=0)
        self.window.mainloop()

    def read_del(self):
        i = self.del_ent.get()
        self.delete_entry(i)

    def add_entry(self, entry) -> None:
        entry.append(dt.datetime.now().strftime("%Y-%m-%d"))#Tag entry date
        placeholders = ','.join(['?'] * len(entry))
        self.parent.c.execute(f"INSERT INTO {self.name} VALUES (NULL, {placeholders});", entry)#Space for -ID Col
        self.parent.conn.commit()
        self.tree.insert('', ctk.END, values=entry)

    def submit_entry(self):
        vals = [i.get() for i in self.entries]
        if self.isFull(vals):
            self.add_entry(vals)
            self.type_to_console("Entry Submitted!")
        else:
            self.type_to_console("Fill all Entries")

    def isFull(self, vals) -> bool:
        return all(vals)

    def display_add_frame(self):
        self.input_frame = ctk.CTkFrame(self.parent.window)
        framelabel = ctk.CTkLabel(self.input_frame, text="Add a Table")
        framelabel.grid(row=0,columnspan=len(self.parent.colinps),pady=5)
        self.input_frame.grid(row=6, column=0, padx=5, pady=5)
        for i, col in enumerate(self.parent.colinps):
            label = ctk.CTkLabel(self.input_frame, text=f"{col}:")
            label.grid(row=1, column=i, padx=5, pady=5)
            entry = ctk.CTkEntry(self.input_frame)
            entry.grid(row=2, column=i, padx=5, pady=5)
            self.entries.append(entry)
        button = ctk.CTkButton(self.input_frame, text="Submit", command=self.submit_entry)
        button.grid(row=3, columnspan=len(self.parent.colarr), pady=5)


class App():
    window = None
    dbclass = []
    home = None
    dbnames=[]
    favourites = []
    tab_buttons=[]

    def __init__(self):
        self.window = ctk.CTk()
        self.get_databases()

        # configure window
        self.window.title("WHMC Database")
        self.window.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.load_grid()

        # create sidebar frame with widgets
        self.load_sideFrame()

        # create main entry and button
        self.load_bottom_textEntry()

        # create textbox
        self.load_textBox()

        # create tabview
        self.load_tabsBox()

        # create radiobutton frame
        # self.window.load_radioButton_frame()

        # create slider and progressbar frame
        # self.window.load_sliderProgbar_frame()

        # create scrollable frame
        # self.window.load_scrollFrame()

        # create checkbox and switch frame
        self.load_checkbox_frame()

        # set default values
        # self.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton")
        # self.checkbox_3.configure(state="disabled")
        # self.checkbox_1.select()
        # self.scrollable_frame_switches[0].select()
        # self.scrollable_frame_switches[4].select()
        # self.radio_button_3.configure(state="disabled")
        #self.optionmenu_1.set("CTkOptionmenu")
        #self.combobox_1.set("CTkComboBox")
        # self.slider_1.configure(command=self.window.progressbar_2.set)
        # self.slider_2.configure(command=self.window.progressbar_3.set)
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        # self.textbox.insert("0.0", "CTkTextbox\n\n" +
        #                    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor "
        #                    "invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        # self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        # self.seg_button_1.set("Value 2")
        self.window.mainloop()

    def get_databases(self):
        # List all items in the current directory
        items_in_directory = os.listdir('.')

        # Filter the items to include only those that end with .db
        db_files = [f for f in items_in_directory if f.endswith('.db')]

        for i in db_files:
            p = Database(i)
            self.dbclass.append(p)
            self.dbnames.append(p.name)
        # Return the list of .db paths
        return db_files

    def load_all_dbs(self):
        for k in self.dbclass:
            (k)

    def create_database(self):
        dialog = ctk.CTkInputDialog(text="Database Name", title="Create Database")
        self.add_db(dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")
        self.textbox.insert("0.0", "sidebar_button click\n\n")

    # load checkbox frame
    def load_checkbox_frame(self):
        self.checkbox_slider_frame = ctk.CTkFrame(self.window)
        self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.tableCreate_button = ctk.CTkButton(master=self.checkbox_slider_frame, text="Create New Table", command=self.open_tc)
        self.tableCreate_button.grid(row=1, column=0, pady=20, padx=20, sticky="n")

        self.tableDelete_button = ctk.CTkButton(master=self.checkbox_slider_frame, text="Delete Existing Table", command=self.sidebar_button_event)
        self.tableDelete_button.grid(row=2, column=0, pady=20, padx=20, sticky="n")

        self.favTable_button = ctk.CTkButton(master=self.checkbox_slider_frame, text="Add Table to Favourites", command=self.sidebar_button_event)
        self.favTable_button.grid(row=3, column=0, pady=20, padx=20, sticky="n")

        # self.checkbox_1 = ctk.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_2 = ctk.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_3 = ctk.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

    # load scrollable frame
    def load_scrollFrame(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window, label_text="CTkScrollableFrame")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []
        for i in range(100):
            switch = ctk.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches.append(switch)

    # loads sliders and progress bar frame
    def load_sliderProgbar_frame(self):
        self.slider_progressbar_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        self.seg_button_1 = ctk.CTkSegmentedButton(self.slider_progressbar_frame)
        self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = ctk.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_2 = ctk.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = ctk.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_2 = ctk.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        self.progressbar_3 = ctk.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

    # load radio button frame
    def load_radioButton_frame(self):
        self.radiobutton_frame = ctk.CTkFrame(self.window)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = ctk.CTkLabel(master=self.radiobutton_frame, text="CTkRadioButton Group:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1 = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                 variable=self.radio_var, value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2 = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                 variable=self.radio_var, value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3 = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                 variable=self.radio_var, value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

    # loads main tabs box and options
    def load_tabsBox(self):
        self.tabview = ctk.CTkTabview(self.window, width=600)
        self.tabview.grid(row=0, column=1, columnspan=3, padx=(20, 20), sticky="nsew")

        for i in self.dbclass:
            self.tabview.add(i.name)
            self.tabview.tab(i.name).grid_columnconfigure((0, 1, 2, 3), weight=1)
            self.tabview.tab(i.name).grid_rowconfigure((0, 1, 2, 3), weight=1)
            self.table_buttons(i)


        #self.tabview.tab("DB1").grid_columnconfigure((0, 1, 2, 3), weight=1)   # configure grid of individual tabs
        #self.tabview.tab("DB1").grid_rowconfigure((0, 1, 2, 3), weight=1)
        #self.tabview.tab("DB2").grid_columnconfigure(0, weight=1)

        #self.testbutton_tabview = ctk.CTkButton(self.tabview.tab("DB1"), text="table 4",
        #                                                  command=self.sidebar_button_event)
        #self.testbutton_tabview.grid(row=0, column=1, padx=20, pady=(10, 10))
        #
        #self.testbutton_tabview2 = ctk.CTkButton(self.tabview.tab("DB1"), text="table 5",
        #                                                   command=self.open_tc)
        #self.testbutton_tabview2.grid(row=0, column=2, padx=20, pady=(10, 10))
        #
        #self.testbutton_tabview3 = ctk.CTkButton(self.tabview.tab("DB1"), text="table 6",
        #                                                   command=self.sidebar_button_event)
        #self.testbutton_tabview3.grid(row=3, column=0, padx=20, pady=(10, 10))

        #self.testbutton_tabview4 = ctk.CTkButton(self.tabview.tab("DB1"), text="table 7",
        #                                                   command=self.sidebar_button_event)
        #self.testbutton_tabview4.grid(row=0, column=3, padx=20, pady=(10, 10))

        #self.optionmenu_1 = ctk.CTkOptionMenu(self.tabview.tab("DB1"), dynamic_resizing=False,
        #                                                values=["Value 1", "Value 2", "Value Long Long Long"])
        #self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        #self.combobox_1 = ctk.CTkComboBox(self.tabview.tab("DB1"),
        #                                            values=["Value 1", "Value 2", "Value Long....."])
        #self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))

        #self.label_tab_2 = ctk.CTkLabel(self.tabview.tab("DB2"), text="CTkLabel on Tab 2")
        #self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

    # loads main textbox
    def load_textBox(self):
        self.textbox = ctk.CTkTextbox(self.window, width=250)
        self.textbox.grid(row=1, column=1, columnspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew")

    # loads bottom text entry bar
    def load_bottom_textEntry(self):
        self.entry = ctk.CTkEntry(self.window, placeholder_text="SAMPLE")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.main_button_1 = ctk.CTkButton(master=self.window, fg_color="transparent", border_width=2,
                                           text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

    # configure 4x4 grid
    def load_grid(self):
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure((2, 3), weight=0)
        self.window.grid_rowconfigure((1, 2), weight=1)

    # load "ctk" Sideframe with 3 buttons and 2 drop menus
    def load_sideFrame(self):
        self.sidebar_frame = ctk.CTkFrame(self.window, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WHMC Database",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Create New DB",
                                              command=self.create_database)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Import/Export",
                                              command=self.sidebar_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Delete DB",
                                              command=self.sidebar_button_event)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = ctk.CTkButton(self.sidebar_frame, text="Re-Load DB's",
                                              font=ctk.CTkFont(size=20),
                                              command=self.load_tabsBox, width=220, height=50)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame,
                                                             values=["Light", "Dark", "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame,
                                                     values=["80%", "90%", "100%", "110%", "120%"],
                                                     command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")


    def add_db(self,val):

        val.replace(" ", "_")
        val+=".db"
        sqlite3.connect(val)
        self.dbclass.append(Database(val))
        self.dbnames.append(val)

    def open_tc(self):
        TableCreator(self)

    #def add_to_favs(self):

    def table_buttons(self,i):
        for j in range(len(i.tables)):
            k = self.make_tab_button(i,j)
            self.tab_buttons.append(k)

    def make_tab_button(self, i,j):
        p = ctk.CTkButton(self.tabview.tab(i.name), text=i.tables[j], command=lambda: self.init_table(i,j))
        p.grid(row=j, column=int(j/4), pady=5)
        p.bind("<Double-Button-1>", lambda: self.init_table(i,j))
        return j

    def init_table(self,i:Database,j):
        Table(i, j,self.window)


class TableCreator():
    parent = None
    frame3 = None
    console = None
    entries = []
    comboboxes = []
    frame_top = None
    frame_middle = None
    frame_bottom = None
    types = {
        "Name / Address / Email": "varchar(250)",
        "Counting Number": "int",
        "Money": "float",
        "Date": "date",
        "Description": "text"
    }

    def __init__(self, parent: App):
        self.parent = parent
        self.set_table()

    def set_table(self):
        self.frame3 = ctk.CTkToplevel(self.parent.window)
        self.frame3.transient(self.parent.window)
        self.frame3.title("Table Creator")
        self.frame3.geometry(f"{500}x{600}")

        # Ensure the popup window appears in front
        self.frame3.lift()
        self.frame3.focus_force()

        # Configure the main frame grid
        self.frame3.grid_rowconfigure(0, weight=1)
        self.frame3.grid_rowconfigure(1, weight=1)
        self.frame3.grid_rowconfigure(2, weight=1)
        self.frame3.grid_rowconfigure(3, weight=1)
        self.frame3.grid_rowconfigure(4, weight=1)
        self.frame3.grid_columnconfigure(0, weight=1)


        # Option menu for database names
        self.dbmenu = ctk.CTkOptionMenu(self.frame3, values=self.parent.dbnames)
        self.dbmenu.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="ew")

        # Frame for table name
        self.frame_top = ctk.CTkFrame(self.frame3)
        self.frame_top.grid(row=1, column=0, pady=10, sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)
        self.frame_top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_top, text="Table Name:").grid(row=0, padx=5, pady=2,column = 0, sticky ="ew")
        self.name_entry = ctk.CTkEntry(self.frame_top)
        self.name_entry.grid(row=0, column=1, padx=5,pady=2, sticky="ew")

        ctk.CTkLabel(self.frame_top, text="Column Name").grid(row=1, column=0, padx=5,pady=2, sticky="ew")
        ctk.CTkLabel(self.frame_top, text="Column Type").grid(row=1, column=1, padx=5,pady=2, sticky="ew")

        # Frame for table columns
        self.frame_middle = ctk.CTkFrame(self.frame3)
        self.frame_middle.grid(row=2, column=0, pady=10, sticky="ew")
        self.frame_middle.grid_columnconfigure(0, weight=1)

        self.entries = []
        self.comboboxes = []

        for i in range(10):
            row_frame = ctk.CTkFrame(self.frame_middle)
            row_frame.grid(row=i, column=0, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)

            entry = ctk.CTkEntry(row_frame)
            entry.grid(row=0, column=0, padx=5, sticky="ew")
            self.entries.append(entry)

            combobox = ctk.CTkComboBox(row_frame, values=[
                "Name / Address",
                "Counting Number",
                "Money",
                "Date",
                "Description"
            ])
            combobox.set('')
            combobox.grid(row=0, column=1, padx=5, sticky="ew")
            self.comboboxes.append(combobox)

        # Frame for console and buttons
        self.frame_bottom = ctk.CTkFrame(self.frame3)
        self.frame_bottom.grid(row=3, column=0, pady=10, sticky="ew")
        self.frame_bottom.grid_columnconfigure(0, weight=1)

        self.console = ctk.CTkTextbox(self.frame_bottom, height=2, width=120, state="disabled")
        self.console.grid(row=0, column=0, pady=5, sticky="ew")

        # Submit button
        submit = ctk.CTkButton(self.frame3, text="Create Table", command=self.submit)
        submit.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        # Exit button
        exit_button = ctk.CTkButton(self.frame3, text="Exit", command=self.frame3.destroy)
        exit_button.grid(row=5, column=0, pady=10, padx=20, sticky="ew")

    def submit(self):
        name = self.name_entry.get()
        name.replace(" ", "_")
        colvals = []
        typevals = []
        for i in self.entries:
            p = i.get()
            if p=='':
                continue
            p.replace(" ", "_")
            colvals.append(p)


        for i in self.comboboxes:
            p=i.get()
            if p!='':
                typevals.append(p)

        if self.isFull(colvals) & self.isFull(typevals):
            self.create_table(self.dbmenu.get(),name, colvals, typevals)
            self.type_to_console("Submitted")
        else:
            self.type_to_console("Fill Rows Properly")

    def isFull(self, vals) -> bool:
        return all(vals)

    def create_table(self,host,tname,cols,types) -> None:
        """
        On click, new table is made, by reading the entries from vjs application (Table name, col names(LIST), and types[LIST])
        :return: NONE
        """
        father= Database(host+".db")

        columns = [f"{tname}Id INTEGER PRIMARY KEY AUTOINCREMENT"]#VJ THIS need to be kept here before u read all those colum names


        i = 0
        while i < len(cols) and i < len(types):#iterates for as many columns
            if cols[i] and types[i]:
                columns.append(f"{cols[i]} {self.types[types[i]]}")
            i += 1
        columns.append("Input_Date DATE")
        if tname and self.isFull(columns): #if both exist, proceed
            columns_str = ", ".join(columns)
            self.parent.tables.append(tname)
            self.parent.c.execute(f"CREATE TABLE {tname} ({columns_str});")
            self.type_to_console("Submitted!")
        else:
            self.type_to_console("Fill All Columns")

    def type_to_console(self, message: str):
        self.console.configure(state='normal')
        self.console.delete("1.0", ctk.END)
        self.console.insert("1.0", message)
        self.console.configure(state='disabled')



if __name__ == "__main__":
    app = App()
