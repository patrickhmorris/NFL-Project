import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

import sqlite3


# Create playerstats table in Sqlite
def create_playerstats_table():
    db_path = 'app/draft_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PlayerStats (
            id INTEGER PRIMARY KEY,
            season INTEGER,
            pick INTEGER,
            round INTEGER,
            team TEXT,
            name TEXT,
            hof BOOLEAN,
            position TEXT,
            college TEXT,
            allpro INTEGER,
            probowls INTEGER,
            seasons_started INTEGER,
            games INTEGER,
            pass_completions INTEGER,
            pass_attempts INTEGER,
            pass_yards INTEGER,
            pass_tds INTEGER,
            pass_ints INTEGER,
            rush_atts INTEGER,
            rush_yards INTEGER,
            rush_tds INTEGER,
            receptions INTEGER,
            rec_yards INTEGER,
            rec_tds INTEGER,
            def_solo_tackles INTEGER,
            def_ints INTEGER,
            def_sacks INTEGER
        )
    """)
    conn.commit()
    conn.close()


# load csv to db for functionality
def load_csv_to_db(csv_file_path):
    db_path = 'app/draft_data.db'
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_file_path)

    # Convert boolean to integer for SQLite
    df['hof'] = df['hof'].astype(int)

    # Replace NaN with None for SQLite compatibility
    df.where(pd.notnull(df), None)

    df.to_sql('PlayerStats', conn, if_exists='replace', index=False)
    conn.close()


# load draft data
def load_draft_data():
    try:
        db_path = 'app/draft_data.db'
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM PlayerStats"
        data = pd.read_sql_query(query, conn)
        conn.close()

        data = preprocess_data(data)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


# preprocess data
def preprocess_data(data):
    data['hof'] = data['hof'].apply(lambda x: "YES" if x == 1 else "NO")
    return data


# insert new data into db
def insert_new_data(new_data):
    db_path = 'app/draft_data.db'  # Path to your database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql = """
    INSERT INTO PlayerStats (
        season, pick, round, team, name, hof, position, college, allpro, probowls,
        seasons_started, games, pass_completions, pass_attempts, pass_yards, pass_tds, pass_ints,
        rush_atts, rush_yards, rush_tds, receptions, rec_yards, rec_tds, def_solo_tackles,
        def_ints, def_sacks
    ) """

    cursor.execute(sql, (
        new_data['season'], new_data['pick'], new_data['round'], new_data['team'], new_data['name'],
        new_data['hof'], new_data['position'], new_data['college'], new_data['allpro'], new_data['probowls'],
        new_data['seasons_started'], new_data['games'], new_data['pass_completions'], new_data['pass_attempts'],
        new_data['pass_yards'], new_data['pass_tds'], new_data['pass_ints'], new_data['rush_atts'],
        new_data['rush_yards'], new_data['rush_tds'], new_data['receptions'], new_data['rec_yards'],
        new_data['rec_tds'], new_data['def_solo_tackles'], new_data['def_ints'], new_data['def_sacks']
    ))

    conn.commit()
    conn.close()


# Collect data from entries to put into database
def submit_data(entries, window, tree):
    new_data = {field: entry.get() for field, entry in entries.items()}
    try:
        insert_new_data(new_data)
        messagebox.showinfo("Success", "Data successfully added.")
        window.destroy()  # Close the entry window upon successful submission
        # Refresh the treeview
        draft_data = load_draft_data()
        for item in tree.get_children():
            tree.delete(item)
        for index, row in draft_data.iterrows():
            values = [row[col] for col in draft_data.columns]
            tree.insert('', 'end', iid=str(index), values=values)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# open data entry window for new stats
def open_data_entry_window(root, tree):
    entry_window = tk.Toplevel(root)
    entry_window.title("Add New Player Stats")

    # Define the fields based on your database schema
    fields = ['season', 'pick', 'round', 'team', 'name', 'hof', 'position', 'college',
              'allpro', 'probowls', 'seasons_started', 'games', 'pass_completions',
              'pass_attempts', 'pass_yards', 'pass_tds', 'pass_ints', 'rush_atts',
              'rush_yards', 'rush_tds', 'receptions', 'rec_yards', 'rec_tds',
              'def_solo_tackles', 'def_ints', 'def_sacks']

    entries = {}
    for i, field in enumerate(fields):
        tk.Label(entry_window, text=f"{field.replace('_', ' ').title()}:").grid(row=i, column=0, sticky='nsew')
        entry = tk.Entry(entry_window)
        entry.grid(row=i, column=1, sticky='nsew')
        entries[field] = entry

    submit_button = tk.Button(entry_window, text="Submit",
                              command=lambda: submit_data(entries, entry_window, tree))
    submit_button.grid(row=len(fields), column=0, columnspan=2, pady=10)


# filter data by attribute
def filter_data_by_attribute(data, column, top_n=10, filter_type=None, filter_value=None):
    if data[column].dtype == 'object':
        if filter_type == 'contains':
            return data[data[column].str.contains(filter_value, case=False, na=False)]
        elif filter_type == 'exact':
            return data[data[column].astype(str).str.lower() == filter_value.lower()]
        else:
            return data
    else:
        return data.nlargest(top_n, column)


# format data for display
def format_data_for_display(data):
    # Drop columns with all NaN values or all zeros
    formatted_data = data.dropna(axis=1, how='all').replace({0: None}).dropna(axis=1, how='all')
    return formatted_data


# show filtered data
def show_filtered_data(column, view_tree, draft_data):
    # Ensure that the column name is correct and exists in draft_data
    if column in draft_data.columns:
        filtered_data = filter_data_by_attribute(draft_data, column)
        formatted_data = format_data_for_display(filtered_data)

        for item in view_tree.get_children():
            view_tree.delete(item)

        for index, row in formatted_data.iterrows():
            values = [row[col] for col in formatted_data.columns]
            view_tree.insert('', 'end', iid=str(index), values=values)
    else:
        print(f"Column '{column}' not found in data.")


# create button
def create_button(frame, btn_text, btn_command, row, column):
    button = ttk.Button(frame, text=btn_text, command=btn_command)
    button.grid(row=row, column=column, padx=10, pady=5, sticky='ew')


# search button
def on_search_click(tree, draft_data, season_entry, player_entry):
    season = season_entry.get().strip()
    player = player_entry.get().strip()

    # Validate season input (assuming it should be a year)
    if season and not season.isdigit():
        messagebox.showerror("Invalid Input", "Invalid season input. Please enter a valid year.")
        return

    # Validate player input (example: check for non-alphanumeric characters)
    if player and not player.replace(" ", "").isalnum():
        messagebox.showerror("Invalid Input", "Invalid player name input. Please enter a valid name.")
        return

    filtered_data = filter_treeview_data(draft_data, season, player)
    show_filtered_data('season', tree, filtered_data)


# filter data
def filter_treeview_data(data, season, player_name):
    filtered_data = data
    if season:
        filtered_data = filtered_data[filtered_data['season'].astype(str).str.lower() == season.lower()]
    if player_name:
        filtered_data = filtered_data[
            filtered_data['name'].str.lower().str.contains(player_name.lower(), case=False, na=False)]

    return format_data_for_display(filtered_data)


# search data
def search_data(tree, draft_data, season_entry, player_entry):
    season = season_entry.get()
    player = player_entry.get()
    filtered_data = filter_treeview_data(draft_data, season, player)

    # Use a correct column name for display
    show_filtered_data('season', tree, filtered_data)  # Adjust 'season' as needed


# on tree select show team logo
def on_tree_select(tree, team_logo_label, loaded_team_logos):
    selected_item = tree.focus()
    if selected_item:
        item_data = tree.item(selected_item)
        team_abbr = item_data['values'][3]

        # Update the logo label with the team logo
        team_logo = loaded_team_logos.get(team_abbr, None)
        if team_logo:
            team_logo_label.config(image=team_logo)
            team_logo_label.image = team_logo
        else:
            team_logo_label.config(image='')


# refresh treeview
def refresh_treeview(tree):
    draft_data = load_draft_data()
    for item in tree.get_children():
        tree.delete(item)
    for index, row in draft_data.iterrows():
        values = [row[col] for col in draft_data.columns]
        tree.insert('', 'end', iid=str(index), values=values)


# setup treeview
def setup_treeview(main_root):
    tree_frame = ttk.Frame(main_root)
    tree_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
    tree_scroll_y.pack(side='right', fill='y')
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side='bottom', fill='x')

    # Column Renames for display
    view_tree = ttk.Treeview(tree_frame)
    view_tree['columns'] = ['Season', 'Pick', 'Round', 'Team', 'Name', 'HOF', 'Position', 'College', 'All-Pro',
                            'Probowls', 'Seasons Started', 'Games', 'Completions', 'Attempts', 'Pass Yards', 'Pass TDs',
                            'Pass Interceptions', 'Rush Attempts', 'Rush Yards', 'Rush TDs', 'Receptions',
                            'Receiving Yards', 'Receiving TDs', 'Tackles', 'Defensive Interceptions', 'Sacks']

    # Set column widths and headings
    column_width = 110
    for col in view_tree['columns']:
        view_tree.column(col, width=column_width, minwidth=75, anchor='c', stretch=tk.NO)
        view_tree.heading(col, text=col, anchor='c')

    # Configure scrollbars
    tree_scroll_y.config(command=view_tree.yview)
    tree_scroll_x.config(command=view_tree.xview)

    # Hide default index column
    view_tree.column("#0", width=0, stretch=tk.NO)
    view_tree.heading("#0", text="")

    view_tree.pack(expand=True, fill='both')
    tree_frame.pack_propagate(False)
    tree_frame.config(width=800, height=350)

    return view_tree
