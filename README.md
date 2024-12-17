WHC Database Management Application
Overview
The WHC Database Management Application is a graphical user interface (GUI) built using CustomTkinter for managing SQLite databases. The app provides tools for creating, managing, exporting, and importing tables within multiple databases. It's designed to simplify database operations and offer an intuitive way to manage relational data.

Features
Database Operations:

Create new databases.
Delete existing databases.
View and manage tables within databases.
Table Management:

Create new tables with customizable columns.
Delete tables.
Import tables from CSV files.
Export tables to CSV or PDF formats.
Data Manipulation:

Add, update, and delete table entries.
Search and sort data within tables.
Generate summary reports for numeric columns.
Favorites:

Mark tables as favorites for quick access.
Toggle favorite status with a button.
Logging:

View detailed activity logs of database operations.
Log entries include timestamps and operation details.
Prerequisites
Python (version 3.8 or higher)
Dependencies:
customtkinter
Pillow
reportlab
sqlite3
tkinter
csv
datetime
os
To install dependencies, run:

bash
Copy code
pip install customtkinter Pillow reportlab
Directory Structure
graphql
Copy code
WHC_Database_App/
│-- main.py            # Main application file
│-- Databases/         # Directory where SQLite databases are stored
│-- auxiliaries/
│   ├── whc_database.png  # Logo for the app
│   ├── logo-whc.png      # Additional logo image
│   └── helperdb          # SQLite helper database for managing metadata
└-- log.txt            # Activity log file
How to Run the Application
Clone the repository:

bash
Copy code
git clone https://github.com/your-repository/WHC_Database_App.git
cd WHC_Database_App
Run the main script:

bash
Copy code
python main.py
The main window should open, and you can start managing your databases.

Application Guide
Main Window
The main window is divided into several sections:

Sidebar:

Displays the application logo and title.
Contains buttons to access key functions.
Tabs:

Displays tabs for each database.
Each tab shows the tables within that database.
Console:

Displays status messages and feedback.
Buttons:

Create Table: Opens the Table Creator window.
Delete Table: Deletes the selected table (requires confirmation).
View Log: Opens the log file to display recorded activities.
Create New DB: Opens a dialog to create a new database.
Export Table: Export table data to CSV or PDF.
Import Table: Import data from a CSV file.
Toggle Favorite: Mark or unmark a table as a favorite.
Table Operations
Add Entry: Add a new row to the selected table.
Update Entry: Modify an existing row.
Delete Entry: Remove a row from the table.
Search: Search for specific entries within a table.
Sort: Sort table data by specified columns.
Favorites
Access frequently used tables quickly from the Favourites tab.
Toggle favorite status using the Toggle Favourite button.
Exporting and Importing Tables
Export:

Save table data as a CSV or PDF.
Choose the file type and location using a file dialog.
Import:

Import data from a CSV file.
Choose whether the CSV file contains headers.
Map CSV columns to appropriate data types.
Logging
All major actions are logged to log.txt with timestamps.
View logs using the View Log button in the main window.
Shortcuts and Tips
ESC Key: Cancel current actions like deletion confirmations.
Right-Click: Provides context-specific options (if implemented).
Known Issues
Ambiguous Table Names: Ensure table names are unique across databases.
Database Path: Ensure the Databases/ and auxiliaries/ directories exist before running the app.
CSV Imports: Ensure CSV files are formatted correctly for successful imports.
Future Improvements
Add support for more data types.
Enhance the UI with themes and additional styling.
Implement undo/redo functionality for data manipulation.
