import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
import sys
sys.path.append("..")
from Controller.controller import Controler
from data_types import Preference

class PeferencesPage(tk.Frame):
    def __init__(self, parent, registration_page):
        super().__init__(parent)
        self.parent = parent
        self.pref_city_var = tk.StringVar()
        self.pref_genre_var = tk.StringVar()
        self.pref_date_var = tk.StringVar()
        self.pref_day_parts_var = tk.StringVar()
        self.pref_price_var = tk.IntVar()

        parent.geometry("670x510")

        self.controller = Controler()
        self.events_list = list()

        # Create a frame for the left part
        self.left_frame = tk.Frame(self, width=200, height=500)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10)

        # Create button, preferences in the left frame
        # city preferences
        self.city_label = tk.Label(self.left_frame, text="➤ City:")
        self.city_label.grid(row=0, column=0, padx=5)
        self.city_list = ("София", "Варна", "Пловдив")
        self.city_pref = ttk.OptionMenu(
            self.left_frame, self.pref_city_var, self.city_list[0], *self.city_list
        )
        self.city_pref.grid(row=1, column=0, padx=5)

        # genre preferences
        self.genre_label = tk.Label(self.left_frame, text="➤ Genre:")
        self.genre_label.grid(row=2, column=0, padx=5)
        self.genre_list = (
            "concert",
            "family",
            "culture",
            "sport",
            "other",
        )
        self.genre_pref = ttk.OptionMenu(
            self.left_frame, self.pref_genre_var, self.genre_list[0], *self.genre_list
        )
        self.genre_pref.grid(row=3, column=0, padx=5)

        # date preferences
        self.date_label = tk.Label(self.left_frame, text="➤ Date:")
        self.date_label.grid(row=4, column=0, padx=5)
        self.date_list = (".", "^", "#", "%", "()")
        # self.date_pref = ttk.OptionMenu(
        #     self.left_frame, self.pref_date_var, self.date_list[0], *self.date_list
        # )
        # self.date_pref.grid(row=5, column=0, padx=5)
        self.calendar = Calendar(
            self.left_frame, selectmode="day", year=2023, month=7, day=6
        )
        self.calendar.grid(row=5, column=0, padx=5)

        # day parts preferences
        self.day_part_label = tk.Label(self.left_frame, text="➤ Day parts:")
        self.day_part_label.grid(row=6, column=0, padx=5)
        self.day_part_list = (
            "Morning (06-12)",
            "Afternoon (11-16)",
            "Evening (15-19)",
            "Night (18-24)",
        )
        self.day_part_pref = ttk.OptionMenu(
            self.left_frame,
            self.pref_day_parts_var,
            self.day_part_list[0],
            *self.day_part_list
        )
        self.day_part_pref.grid(row=7, column=0, padx=5)

        # price preferences
        self.price_label = tk.Label(self.left_frame, text="➤ Max price:")
        self.price_label.grid(row=8, column=0, padx=5)
        self.price_list = (30, 40, 50, 60, 80, 100, 120, 150, 200, 250)
        self.price_pref = ttk.OptionMenu(
            self.left_frame, self.pref_price_var, self.price_list[0], *self.price_list
        )
        self.price_pref.grid(row=9, column=0, padx=5)

        # search button
        self.search_button = tk.Button(self.left_frame, text="Search", command=self.search_events)
        self.search_button.grid(row=10, column=0, padx=5, pady=5)

        # Create a frame for the right part
        self.right_frame = tk.Frame(self, width=40, height=250)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.right_frame)
        self.text_widget = tk.Text(
            self.right_frame, width=42, height=25, relief="solid",
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.text_widget.yview)

        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a label in the right frame
        self.label_info = tk.Label(
            self.right_frame, text="Events...", width=48, height=28, relief="solid"
        )
        # self.label_info.pack()

        #Create button for picking an event
        self.pick_input_button = tk.Button(self, text="Pick event by id", command=self.pick_event)
        self.pick_input_button.grid(row=11, column=1, padx=5, pady=5)

        # Create input field for picking an event
        self.pick_input_field = tk.Entry(self)
        self.pick_input_field.grid(row=12, column=1, padx=5, pady=5)


    def set_label_text(self, text):
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text)

    def search_events(self):
        selected_city = self.pref_city_var.get()
        selected_genre = self.pref_genre_var.get()
        selected_date = format_date(self.calendar.get_date())
        selected_dayparts = self.pref_day_parts_var.get()
        selected_max_price = self.pref_price_var.get()
        self.set_label_text("Loading...")
        print("Loading...")
        new_preference = Preference(selected_genre, selected_city, selected_date, selected_dayparts, selected_max_price)
        self.controller.setPreference(new_preference)
        self.events_list = self.controller.getEvents()

        information = ""
        for event in self.events_list :
            information += str(self.events_list.index(event))
            information += " -> "
            information += event.name
            information += "\n"
            
        self.set_label_text(information)

    def pick_event(self):
        event_id = self.pick_input_field.get()
        if str(int(event_id)) == event_id :
            self.controller.pickEvent(self.events_list[int(event_id)].link)

def format_date(selected_date):
    date_object = datetime.strptime(selected_date, "%m/%d/%y")
    formatted_date = date_object.strftime("%d.%m.%Y")
    return formatted_date
