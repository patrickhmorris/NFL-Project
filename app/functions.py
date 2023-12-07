import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


# load draft data
def load_draft_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except pd.errors.ParserError:
        print("Error: File could not be parsed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


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


# setup treeview
def setup_treeview(main_root):
    tree_frame = ttk.Frame(main_root)
    tree_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
    tree_scroll_y.pack(side='right', fill='y')
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side='bottom', fill='x')

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
    tree_frame.config(width=800, height=300)

    return view_tree
