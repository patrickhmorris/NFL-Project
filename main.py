import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from app import functions

# Define color scheme
BG_COLOR = "#FFFFFF"  # White background
PRIMARY_COLOR = "#D50A0A"  # Red primary color
SECONDARY_COLOR = "#000080"  # Blue secondary color
TEXT_COLOR = "#000000"  # Black text color

# GUI Setup
root = tk.Tk()
root.title("NFL Data App")
root.geometry("800x800")


# Create a Style object
style = ttk.Style()

style.theme_create("MyTheme", parent="alt", settings={
    "TFrame": {
        "configure": {"background": BG_COLOR}
    },
    "TLabel": {
        "configure": {"background": BG_COLOR, "foreground": TEXT_COLOR}
    },
    "TButton": {
        "configure": {"background": BG_COLOR, "foreground": TEXT_COLOR, "font": ('Georgia', 10)},
        "map": {
            "background": [("active", SECONDARY_COLOR)],
            "foreground": [("active", BG_COLOR)]
        }
    },
    "Treeview": {
        "configure": {
            "background": BG_COLOR,
            "field background": BG_COLOR,
            "foreground": TEXT_COLOR,
            "row height": 25
        },
        "map": {
            "background": [("selected", SECONDARY_COLOR)],
            "foreground": [("selected", BG_COLOR)]
        }
    },
    "Treeview.Heading": {
        "configure": {"background": BG_COLOR, "foreground": TEXT_COLOR, "font": ('Helvetica', 10)}
    },
    "TEntry": {
        "configure": {"field background": BG_COLOR, "foreground": TEXT_COLOR, "border width": 2}
    },
    "Vertical.TScrollbar": {
        "configure": {"background": PRIMARY_COLOR}
    },
    "Horizontal.TScrollbar": {
        "configure": {"background": PRIMARY_COLOR}
    },
    "TLabelframe": {
        "configure": {"background": BG_COLOR, "foreground": TEXT_COLOR, "relief": "solid"}
    },
    "TLabelframe.Label": {
        "configure": {"background": BG_COLOR, "foreground": SECONDARY_COLOR}
    },
})


# Turning theme on
style.theme_use("MyTheme")


# Load team logos
logos_folder = 'app/NFL Team Logos/'
team_logos_filenames = {
    "ARI": "arizona-cardinals.png",
    "ATL": "atlanta-falcons.png",
    "BAL": "baltimore-ravens.png",
    "BUF": "buffalo-bills.png",
    "CAR": "carolina-panthers.png",
    "CHI": "chicago-bears.png",
    "CIN": "cincinnati-bengals.png",
    "CLE": "cleveland-browns.png",
    "DAL": "dallas-cowboys.png",
    "DEN": "denver-broncos.png",
    "DET": "detroit-lions.png",
    "GB": "green-bay-packers.png",
    "HOU": "houston-texans.png",
    "IND": "indianapolis-colts.png",
    "JAX": "jacksonville-jaguars.png",
    "KC": "kansas-city-chiefs.png",
    "LV": "las-vegas-raiders.png",
    "LAC": "los-angeles-chargers.png",
    "LAR": "los-angeles-rams.png",
    "MIA": "miami-dolphins.png",
    "MIN": "minnesota-vikings.png",
    "NE": "new-england-patriots.png",
    "NO": "new-orleans-saints.png",
    "NYG": "new-york-giants.png",
    "NYJ": "new-york-jets.png",
    "PHI": "philadelphia-eagles.png",
    "PIT": "pittsburgh-steelers.png",
    "SF": "san-francisco-49ers.png",
    "SEA": "seattle-seahawks.png",
    "TB": "tampa-bay-buccaneers.png",
    "TEN": "tennessee-titans.png",
    "WAS": "washington-commanders.png"
}

# Load images and store in a dictionary
loaded_team_logos = {}
for abbr, filename in team_logos_filenames.items():
    path = logos_folder + filename
    with Image.open(path) as img:

        # Resize image here
        desired_size = (200, 200)  # Adjust this as needed
        img = img.resize(desired_size, Image.Resampling.LANCZOS)
        loaded_team_logos[abbr] = ImageTk.PhotoImage(img)


# Keep a reference to the images
root.image_references = list(loaded_team_logos.values())

# Load draft data
draft_data = functions.load_draft_data('app/updated_draft_data_pm.csv')

# Setup Treeview
tree = functions.setup_treeview(root)
tree.bind('<<TreeviewSelect>>', lambda e: functions.on_tree_select(tree, team_logo_label, loaded_team_logos))


# Top Frame for Filtering Section
top_frame = ttk.Frame(root)
top_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
season_label = ttk.Label(top_frame, text="Enter Season:")
season_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
season_entry = ttk.Entry(top_frame)
season_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
player_label = ttk.Label(top_frame, text="Enter Player Name:")
player_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')
player_entry = ttk.Entry(top_frame)
player_entry.grid(row=0, column=3, padx=5, pady=5, sticky='ew')


# Button Frame
button_frame = ttk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

# search button
search_button = (ttk.Button
                 (top_frame, text="Search",
                  command=lambda: functions.on_search_click(tree, draft_data, season_entry, player_entry)))

# search button grid
search_button.grid(row=0, column=4, padx=5, pady=5)


# Detailed View Frame
detailed_frame = ttk.Frame(root)
detailed_frame.grid(row=3, column=0, columnspan=3, padx=1, pady=1, sticky='nsew')

# Centered the detailed_frame within a single column
detailed_frame.grid(row=3, column=1, columnspan=1, padx=1, pady=1, sticky='nsew')

# Create a widget (e.g., label or frame) inside detailed_frame and center it
widget_inside_detailed_frame = ttk.Label(detailed_frame, text="Centered Widget")
widget_inside_detailed_frame.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

# Configure the widget to be centered horizontally and vertically
detailed_frame.columnconfigure(0, weight=1)  # Center horizontally
detailed_frame.rowconfigure(0, weight=1)     # Center vertically

# Label for Team Logo
team_logo_label = ttk.Label(detailed_frame)
team_logo_label.grid(row=0, column=0, columnspan=1, sticky='nsew')

team_logo_label = ttk.Label(detailed_frame)
team_logo_label.grid(row=0, column=0, padx=5, pady=5)

# Label for Detailed Information
info_label = ttk.Label(detailed_frame, text="", wraplength=400)
info_label.grid(row=0, column=1, padx=5, pady=5)

# Creating buttons
button_texts_commands = {
    "Most Passing Yards": lambda: functions.show_filtered_data('pass_yards', tree, draft_data),
    "Most Pass TDs": lambda: functions.show_filtered_data('pass_tds', tree, draft_data),
    "Most Rush TDs": lambda: functions.show_filtered_data('rush_tds', tree, draft_data),
    "Most Rec TDs": lambda: functions.show_filtered_data('rec_tds', tree, draft_data),
    "Most Rush Yards": lambda: functions.show_filtered_data('rush_yards', tree, draft_data),
    "Most Rec Yards": lambda: functions.show_filtered_data('rec_yards', tree, draft_data)
}

for text, command in button_texts_commands.items():
    functions.create_button(button_frame, text, command, 0, list(button_texts_commands.keys()).index(text))

# Main loop
if __name__ == "__main__":
    root.mainloop()
