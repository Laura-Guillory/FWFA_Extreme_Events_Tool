import tkinter
from tkinter import ttk, messagebox, font
from source import query, display_results
import queue
from functools import partial


# Used to ensure that the user has entered a valid float number, or is in the process of entering a valid number.
# Because this is called after every key press, the following must also be valid:
# * an empty string (to allow the user to completely delete the contents of the entry box)
# * the minus sign (to allow the user to enter negative numbers)
# Returns True if the contents are valid, returns False otherwise
def validate_number(value):
    if value in ['', '-']:
        return True
    try:
        float(value)
    except ValueError:
        return False
    return True


# Create all the GUI elements of the application
class MainApplication:
    def __init__(self):
        self.processing_popup = None
        self.help_popup = None
        self.results_canvas = None
        self.tutorial_canvas = None
        self.active_canvas = None
        self.queue = None
        self.results_table = None
        self.scrollable_frame = None
        self.results = None
        self.first_query = True
        self.months_selected = [False] * 12

        # Set up main window
        self.window = tkinter.Tk()
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.title('Historical Extreme Event Analysis Tool (HEEAT)')
        self.window.geometry('650x450')
        self.window.minsize(650, 700)
        self.window.bind('<FocusIn>', self.focus_window)

        # Three columns
        self.column_left = tkinter.Frame(master=self.window)
        self.column_left.columnconfigure(0, weight=1)
        self.column_left.rowconfigure(0, weight=1)
        self.column_left.rowconfigure(1, weight=1)
        self.column_left.rowconfigure(3, weight=1)
        self.column_left.grid(row=0, column=0, sticky='new')
        self.column_middle = tkinter.Frame(master=self.window)
        self.column_middle.rowconfigure(0, weight=1)
        self.column_middle.grid(row=0, column=1, sticky='nsew')
        self.column_right = tkinter.Frame(master=self.window)
        self.column_right.grid(row=0, column=2, sticky='nsew')
        self.column_right.rowconfigure(3, weight=1)

        # Set up location section
        self.frame1 = tkinter.LabelFrame(master=self.column_left, text='1. Select Location', height=200, padx=5, pady=5)
        self.frame1.columnconfigure(1, weight=1)

        self.select_station_label = tkinter.Label(master=self.frame1, text='Choose a station:', width=13, anchor='w')

        self.station_list = query.get_all_stations()
        self.station_combobox = tkinter.ttk.Combobox(self.frame1, state='readonly', values=self.station_list)
        self.station_combobox.current(0)

        self.select_station_label.grid(row=0, column=0, padx=10, pady=10)
        self.station_combobox.grid(row=0, column=1, padx=5, pady=10, sticky='sew')
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky='new', columnspan=2)

        # Set up conditions section
        self.frame2 = tkinter.LabelFrame(master=self.column_left, text='2. Select Conditions', padx=5, pady=5)

        self.temperature_label = tkinter.Label(master=self.frame2, text='Temperature:', width=13, anchor='w')
        self.condition_list = ['Any', 'Lower Than', 'Higher Than']
        self.temperature_condition_combobox = tkinter.ttk.Combobox(
            self.frame2,
            state='readonly',
            values=self.condition_list
        )
        self.temperature_condition_combobox.current(0)
        self.temperature_condition_combobox.bind('<<ComboboxSelected>>', self.update_temperature_entry)
        self.v_number = self.window.register(validate_number)
        self.i_number = self.window.register(self.invalid_number)
        # Validates the entry box to make sure the user is entering a valid float.
        # Calls validate_number to check if the contents are valid. If they are not valid, then invalid_number is called
        self.temperature_entry = tkinter.Entry(
            master=self.frame2,
            state='disabled',
            validate='key',
            validatecommand=(self.v_number, '%P'),
            invalidcommand=(self.i_number, '%i', '%W', '%d')
        )
        self.temperature_entry.configure(width=5)
        self.temperature_entry.insert(0, '25')
        self.temperature_unit_label = tkinter.Label(master=self.frame2, text='°C')

        self.precipitation_label = tkinter.Label(master=self.frame2, text='Precipitation:', width=13, anchor='w')
        self.precipitation_condition_combobox = tkinter.ttk.Combobox(
            self.frame2,
            state='readonly',
            values=self.condition_list
        )
        self.precipitation_condition_combobox.current(0)
        self.precipitation_condition_combobox.bind('<<ComboboxSelected>>', self.update_precipitation_entry)
        self.precipitation_entry = tkinter.Entry(
            master=self.frame2,
            state='disabled',
            validate='key',
            validatecommand=(self.v_number, '%P'),
            invalidcommand=(self.i_number, '%i', '%W', '%d')
        )
        self.precipitation_entry.configure(width=5)
        self.precipitation_entry.insert(0, 10)
        self.precipitation_unit_label = tkinter.Label(master=self.frame2, text='mm')

        self.wind_label = tkinter.Label(master=self.frame2, text='Windspeed:', width=13, anchor='w')
        self.wind_condition_combobox = tkinter.ttk.Combobox(self.frame2, state='readonly', values=self.condition_list)
        self.wind_condition_combobox.current(0)
        self.wind_condition_combobox.bind('<<ComboboxSelected>>', self.update_wind_entry)
        # Validates the entry box to make sure the user is entering a valid float.
        # Calls validate_number to check if the contents are valid. If they are not valid, then invalid_number is called
        self.wind_entry = tkinter.Entry(
            master=self.frame2,
            state='disabled',
            validate='key',
            validatecommand=(self.v_number, '%P'),
            invalidcommand=(self.i_number, '%i', '%W', '%d')
        )
        self.wind_entry.configure(width=5)
        self.wind_entry.insert(0, 20)
        self.wind_unit_label = tkinter.Label(master=self.frame2, text='m/s')

        self.temperature_label.grid(row=0, column=0, padx=10, pady=10)
        self.temperature_condition_combobox.grid(row=0, column=1, padx=5, pady=10)
        self.temperature_entry.grid(row=0, column=2, padx=10, pady=10)
        self.temperature_unit_label.grid(row=0, column=3, pady=10)
        self.precipitation_label.grid(row=1, column=0, padx=10, pady=10)
        self.precipitation_condition_combobox.grid(row=1, column=1, padx=5, pady=10)
        self.precipitation_entry.grid(row=1, column=2, padx=10, pady=10)
        self.precipitation_unit_label.grid(row=1, column=3, pady=10)
        self.wind_label.grid(row=2, column=0, padx=10, pady=10)
        self.wind_condition_combobox.grid(row=2, column=1, padx=5, pady=10)
        self.wind_entry.grid(row=2, column=2, padx=10, pady=10)
        self.wind_unit_label.grid(row=2, column=3, pady=10)
        self.frame2.grid(row=1, column=0, padx=10, pady=10, sticky='new', columnspan=2)

        # Set up duration section
        self.frame3 = tkinter.LabelFrame(master=self.column_left, text='3. Select Duration', padx=5, pady=5)
        self.frame3.columnconfigure(2, weight=1)

        self.duration_label1 = tkinter.Label(master=self.frame3, text='Over')
        # Validates the entry box to make sure the user is entering a valid float.
        # Calls validate_number to check if the contents are valid. If they are not valid, then invalid_number is called
        self.duration_entry = tkinter.Entry(
            master=self.frame3,
            width=5,
            validate='key',
            validatecommand=(self.v_number, '%P'),
            invalidcommand=(self.i_number, '%i', '%W', '%d')
        )
        self.duration_entry.insert(0, '1')
        self.duration_label2 = tkinter.Label(master=self.frame3, text='consecutive days *')
        self.duration_message = tkinter.Message(
            master=self.frame3,
            width=350,
            text='* Precipitation is calculated as accumulated precipitation over the number of days specified.'
        )

        self.duration_label1.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.duration_entry.grid(row=0, column=1, pady=10, sticky='w')
        self.duration_label2.grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.duration_message.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
        self.frame3.grid(row=2, column=0, padx=10, pady=10, sticky='new', columnspan=2)

        # Set up Months section
        self.frame4 = tkinter.LabelFrame(master=self.column_left, text='4. Select Months', padx=5, pady=5)
        self.months_label = tkinter.Message(
            master=self.frame4, width=350,
            text='Select the months that you would like to filter for in your analysis. If you do not want to filter '
                 'for months, click \'Select All\'.'
        )
        self.month_select_all_button = tkinter.Button(master=self.frame4, text='Select All', width=16, bg='#dddddd',
                                                      command=self.select_all_months)
        self.month_buttons = []
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                       'November', 'December']
        for i in range(0, 12):
            self.month_buttons.append(tkinter.Button(master=self.frame4, text=month_names[i], width=16))
            self.month_buttons[i].config(command=partial(self.toggle_month, i))
            self.month_buttons[i].grid(row=int(i / 3) + 2, column=i % 3)
        self.months_label.grid(row=0, column=0, columnspan=3)
        self.month_select_all_button.grid(row=1, column=0, pady=10)
        self.frame4.grid(row=3, column=0, padx=10, pady=10, sticky='new', columnspan=2)

        # Query button
        self.query_button = tkinter.Button(
            master=self.column_left,
            text='Query',
            width=20,
            bg='#dddddd',
            command=self.query_button_press
        )

        # Help button
        self.help_button = tkinter.Button(
            master=self.column_left,
            text='Help',
            width=20,
            bg='#dddddd',
            command=self.help_button_press
        )

        self.query_button.grid(row=4, column=0, padx=10, pady=10, sticky='nw')
        self.help_button.grid(row=4, column=1, padx=10, pady=10, sticky='nw')

        # Separator
        self.separator = ttk.Separator(self.column_middle, orient='vertical')
        self.separator.grid(row=0, column=0, sticky='ns')

        # Set up results section
        self.results_label = tkinter.Label(
            master=self.column_right,
            text='Results',
            font='TkDefaultFont 11 bold',
            anchor='w'
        )
        self.results_summary = tkinter.Message(master=self.column_right, text='Placeholder', anchor='w', width=210)

        # Frame for show dates options
        self.show_dates_frame = tkinter.Frame(master=self.column_right)

        # Show dates button
        self.show_dates_button = tkinter.Button(
            master=self.show_dates_frame,
            text='Show Dates',
            width=10,
            bg='#dddddd',
            command=self.show_dates_button_press,
            state=tkinter.DISABLED
        )

        # Always show dates checkbox
        self.always_show_dates = tkinter.BooleanVar(value=True)
        self.always_show_dates_checkbutton = tkinter.Checkbutton(master=self.show_dates_frame, text='Always show dates',
                                                                 variable=self.always_show_dates, onvalue=True,
                                                                 offvalue=False,
                                                                 command=self.always_show_dates_checkbutton_press)

        results_container = tkinter.Frame(master=self.column_right, width=50, borderwidth=3, relief='sunken')
        results_container.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        results_container.rowconfigure(0, weight=1)
        self.results_canvas = tkinter.Canvas(results_container, width=200, borderwidth=0, highlightthickness=0)
        scrollbar = tkinter.Scrollbar(results_container, orient="vertical", command=self.results_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        self.scrollable_frame = tkinter.Frame(self.results_canvas, width=200)
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.bind("<Configure>", lambda e: self.results_canvas.configure(
            scrollregion=self.scrollable_frame.bbox("all"))
        )
        canvas_frame = self.results_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.results_canvas.bind('<Configure>', lambda e: self.results_canvas.itemconfig(canvas_frame,
                                                                                         width=e.width - 4))
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        self.window.bind_all('<MouseWheel>', self._on_mousewheel)
        self.results_canvas.grid(row=0, column=0, sticky='nsew')
        self.active_canvas = self.results_canvas

        # Add headers to results
        tkinter.Label(master=self.scrollable_frame, text='Start Date', borderwidth=1, relief='ridge', anchor='w',
                      padx=10).grid(row=0, column=0, sticky='nsew')
        tkinter.Label(master=self.scrollable_frame, text='End Date', borderwidth=1, relief='ridge', anchor='w',
                      padx=10).grid(row=0, column=1, sticky='nsew')

        self.results_label.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        self.results_summary.grid()
        self.results_summary.grid_forget()
        self.show_dates_frame.grid(row=2, column=0, pady=0)
        self.show_dates_button.grid(row=0, column=0, pady=0)
        self.always_show_dates_checkbutton.grid(row=0, column=1, padx=5, pady=0)
        results_container.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')

        # List of entries of results for re-use
        self.entries = []

        self.window.mainloop()

    # When 'Any' is selected, the entry box associated with temperature should be greyed out.
    # It should be re-enabled when an option other than 'Any' is selected.
    def update_temperature_entry(self, event: tkinter.Event):
        if self.temperature_condition_combobox.get() == 'Any':
            self.temperature_entry.configure(state='disabled')
        else:
            self.temperature_entry.configure(state='normal')

    # When 'Any' is selected, the entry box associated with precipitation should be greyed out.
    # It should be re-enabled when an option other than 'Any' is selected.
    def update_precipitation_entry(self, event: tkinter.Event):
        if self.precipitation_condition_combobox.get() == 'Any':
            self.precipitation_entry.configure(state='disabled')
        else:
            self.precipitation_entry.configure(state='normal')

    # When 'Any' is selected, the entry box associated with windspeed should be greyed out.
    # It should be re-enabled when an option other than 'Any' is selected.
    def update_wind_entry(self, event: tkinter.Event):
        if self.wind_condition_combobox.get() == 'Any':
            self.wind_entry.configure(state='disabled')
        else:
            self.wind_entry.configure(state='normal')

    # Called when an entry box is validated and the contents are found to be invalid
    # Removes the last character entered from the entry box
    def invalid_number(self, index, widget_name, action):
        widget = self.window.nametowidget(widget_name)
        if action == '0':
            widget.delete(0, tkinter.END)
        else:
            widget.delete(index, index)
        # After calling this method, validation must be re-enabled for some reason
        widget.after_idle(lambda: widget.configure(validate='key'))

    # Handles everything that should happen when the user presses the 'query' button, including validating user input,
    # assembling parameters, organising the progressbar popup and starting the thread that will perform the query and
    # display its results
    def query_button_press(self):
        if not self.validate_input():
            return
        query_parameters = {
            'station': self.station_combobox.current(),
            'consecutive_days': int(self.duration_entry.get()),
            'temperature': {
                'condition': self.temperature_condition_combobox.get(),
                'as_percentile': False,
                'value': float(self.temperature_entry.get()) if self.temperature_entry.get() != '' else None
            },
            'precipitation': {
                'condition': self.precipitation_condition_combobox.get(),
                'as_percentile': False,
                'value': float(self.precipitation_entry.get()) if self.precipitation_entry.get() != '' else None
            },
            'wind': {
                'condition': self.wind_condition_combobox.get(),
                'as_percentile': False,
                'value': float(self.wind_entry.get()) if self.wind_entry.get() != '' else None
            },
            'months': self.months_selected
        }
        self.open_popup()
        self.queue = queue.Queue()
        query.ThreadedQuery(self.queue, query_parameters).start()
        self.process_results()

    # Opens a popup that displays a progress bar while results are being fetched
    def open_popup(self):
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        self.processing_popup = tkinter.Toplevel(width=300, height=150)
        self.processing_popup.geometry('+%d+%d' % (x + (window_width / 2) - 100, y + (window_height / 2) - 50))
        self.processing_popup.grab_set()
        tkinter.Label(self.processing_popup, text='Processing...').grid(row=0, column=0, padx=10, pady=10)
        progress = ttk.Progressbar(self.processing_popup, orient=tkinter.HORIZONTAL, length=200, mode='indeterminate')
        progress.grid(row=1, column=0, padx=10, pady=10)
        progress.start(10)

    # Closes the popup
    def close_popup(self):
        self.processing_popup.grab_release()
        self.processing_popup.destroy()

    # Validates input before submitting a query. Returns True if the input is valid, and returns False otherwise.
    def validate_input(self):
        temperature_condition = self.temperature_condition_combobox.get()
        precipitation_condition = self.precipitation_condition_combobox.get()
        wind_condition = self.wind_condition_combobox.get()
        if temperature_condition == 'Any' and precipitation_condition == 'Any' and wind_condition == 'Any':
            messagebox.showwarning(
                title='Invalid input',
                message='No conditions have been selected.\n\nPlease select some requirements for Temperature, '
                        'Precipitation or Windspeed.'
            )
            return False
        if self.station_combobox.get() not in self.station_list:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid value for station: ' + self.station_combobox.get() + '\n\nPlease report this error.'
            )
            return False
        if temperature_condition not in self.condition_list:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid input for temperature condition: ' + temperature_condition +
                        '\n\nPlease report this error.'
            )
            return False
        if precipitation_condition not in self.condition_list:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid input for precipitation condition: ' + precipitation_condition +
                        '\n\nPlease report this error.'
            )
            return False
        if wind_condition not in self.condition_list:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid input for wind condition: ' + wind_condition + '\n\nPlease report this error.'
            )
            return False
        if temperature_condition != 'Any':
            if self.temperature_entry.get() == '':
                messagebox.showwarning(
                    title='Invalid input',
                    message='Please enter a temperature value.'
                )
                return False
            try:
                temperature_value = float(self.temperature_entry.get())
            except ValueError:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Temperature must be a number.'
                )
                return False
            if not -273 <= temperature_value <= 100:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Invalid temperature: ' + self.temperature_entry.get() +
                            '\n\nTemperature must be between -273 °C and 100 °C.'
                )
                return False
        if precipitation_condition != 'Any':
            if self.precipitation_entry.get() == '':
                messagebox.showwarning(
                    title='Invalid input',
                    message='Please enter a precipitation value.'
                )
                return False
            try:
                precipitation_value = float(self.precipitation_entry.get())
            except ValueError:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Precipitation must be a number.'
                )
                return False
            if not 0 <= precipitation_value <= 5000:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Invalid precipitation: ' + self.precipitation_entry.get() +
                            '\n\nPrecipitation must be between 0 mm and 5000 mm.'
                )
                return False
        if wind_condition != 'Any':
            if self.wind_entry.get() == '':
                messagebox.showwarning(
                    title='Invalid input',
                    message='Please enter a windspeed value.'
                )
                return False
            try:
                wind_value = float(self.wind_entry.get())
            except ValueError:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Windspeed must be a number.'
                )
                return False
            if not 0 <= wind_value <= 600:
                messagebox.showwarning(
                    title='Invalid input',
                    message='Invalid windspeed: ' + self.wind_entry.get() +
                            '\n\nWindspeed must be between 0 km/h and 600 km/h.'
                )
                return False
        if self.duration_entry.get() == '':
            messagebox.showwarning(
                title='Invalid input',
                message='Please enter a duration.'
            )
            return False
        try:
            duration_value = int(self.duration_entry.get())
        except ValueError:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid duration: ' + self.duration_entry.get() + '\n\nDuration must be a whole number.'
            )
            return False
        if not 1 <= duration_value <= 365:
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid duration: ' + self.duration_entry.get() +
                        '\n\nDuration must be between 1 and 365 days.'
            )
            return False
        if not any(self.months_selected):
            messagebox.showwarning(
                title='Invalid input',
                message='Invalid month filter. You must select at least one month. To skip filtering for months, click '
                '\'Select All\'.'
            )
            return False
        return True

    def process_results(self):
        try:
            errors, results = self.queue.get(block=False)
            if errors is MemoryError:
                messagebox.showwarning(
                    title='Not enough memory',
                    message='Insufficient memory to complete your request.'
                )
                self.close_popup()
                return
            elif errors:
                messagebox.showwarning(
                    title='Error',
                    message='There was a problem with your search. Please report this error.'
                )
                self.close_popup()
                return
            self.results = results
            if self.always_show_dates.get():
                self.display_summary(results)
                self.show_dates_button_press()
            else:
                self.display_summary(results)
        except queue.Empty:
            self.window.after(100, self.process_results)

    def show_dates_button_press(self):
        # Open loading popup
        self.open_popup()
        self.queue = queue.Queue()
        display_results.ThreadedDisplayResults(self.queue, self.results, self).start()

    def always_show_dates_checkbutton_press(self):
        if self.always_show_dates.get():
            self.show_dates_button.configure(state=tkinter.DISABLED)
        else:
            self.show_dates_button.configure(state=tkinter.NORMAL)

    def toggle_month(self, month_i):
        self.months_selected[month_i] = not self.months_selected[month_i]
        if self.months_selected[month_i]:
            self.month_buttons[month_i].config(relief='sunken', bg='#dddddd')
        else:
            self.month_buttons[month_i].config(relief='raised', bg='SystemButtonFace')

    def select_all_months(self):
        self.months_selected = [True] * 12
        for i in range(0, 12):
            self.month_buttons[i].config(relief='sunken', bg='#dddddd')

    # Called after results have been obtained, and displays them in the panel to the right
    def display_summary(self, results):
        # Update results in table
        # Fallback in case of error during processing - clear the table
        if results is None:
            self.results_summary['text'] = ''
            self.close_popup()
            return

        # Refresh summary
        new_text = 'The specified conditions have occurred {} times over 126 years (1889-2015)'.format(len(results))
        self.results_summary['text'] = new_text
        if self.first_query:
            self.results_summary.grid(row=1, column=0, padx=10, pady=(5, 10), sticky='ew')
            self.first_query = False
        else:
            for i in range(len(self.entries)):
                self.entries[i][0].grid_forget()
                self.entries[i][1].grid_forget()

        self.active_canvas = self.results_canvas
        self.close_popup()

    def focus_window(self, event):
        if event.widget == self.window:
            self.active_canvas = self.results_canvas
        elif event.widget == self.help_popup:
            self.active_canvas = self.tutorial_canvas

    def help_button_press(self):
        self.help_popup = tkinter.Toplevel()
        self.help_popup.bind('<FocusIn>', self.focus_window)
        self.tutorial_canvas = tkinter.Canvas(self.help_popup, width=550, height=500)
        self.tutorial_canvas.pack(side=tkinter.LEFT)
        self.active_canvas = self.tutorial_canvas
        scrollbar = tkinter.Scrollbar(self.help_popup, command=self.tutorial_canvas.yview)
        self.tutorial_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tutorial_canvas.bind(
            '<Configure>',
            lambda e: self.tutorial_canvas.configure(scrollregion=self.tutorial_canvas.bbox('all'))
        )
        self.help_popup.bind_all('<MouseWheel>', self._on_mousewheel)
        scrollable_frame = tkinter.Frame(self.tutorial_canvas)
        self.tutorial_canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        normal_font = font.Font(family='Helvetica', size=10)
        heading_font = font.Font(family='Helvetica', size=11, weight='bold')
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='Tutorial')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            width=500,
            text='The FWFA Extreme Events tool reviews historical records and report instances of extreme weather '
                 'events. It allows the user to set desired thresholds for temperature, precipitation, and windspeed, '
                 'and receive a report on the dates that these conditions have occurred in the past.\n\nThe options '
                 'available are explained below.'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='1. Select Location')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            justify=tkinter.LEFT,
            width=520,
            text='Here the user selects the location where they would like to examine historical records. The dropdown '
                 'menu offers a choice of 555 stations around Australia.'
        ).pack(fill=tkinter.X, expand=tkinter.YES)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='2. Select Conditions')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            width=500,
            text='Here the user selects the desired thresholds for each climate variable (temperature, precipitation, '
                 'and windspeed). The user can set thresholds for just one of the climate variables, two, or all '
                 'three.\n\nFor each climate variable, the user can choose between "Higher Than", "Lower Than", or '
                 '"Any".\n\n* Higher Than - the program will search for results where the climate variable was higher '
                 'than the value in the box to the right\n* Lower Than - the program will search for results where the '
                 'climate variable was lower than the value in the box to the right\n* Any - this climate variable '
                 'will be ignored and will not impact results\n\nSelecting "Any" for all three climate variables is '
                 'equivalent to not setting any threshold at all, and is not allowed. The user must select "Higher '
                 'Than" or "Lower Than" for at least one climate variable to do a valid search.\n\nBelow are some '
                 'examples of search parameters; it is encouraged to try them out.\n\nExample 1:\n\nTemperature:    '
                 'Higher Than     40 °C\nPrecipitation:  Any\nWindspeed:      Any\n\nIn this example, the program will '
                 'search for instances where the temperature over 40 °C. It will not matter whether it rained or what '
                 'the windspeed was that day.\n\nExample 2:\n\nTemperature:    Lower Than      5 °C\nPrecipitation:  '
                 'Higher Than     5 mm\nWindspeed:      Higher Than     5m/s\n\nIn this example, the program will '
                 'search for instances where the temperature was under 5 °C, it was rainy and windy. Searches like '
                 'this can be useful when examining windchill.'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='3. Select Duration')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            width=500,
            text='Here the user selects the minimum number of consecutive days necessary for the event to be included '
                 'in the results. The default is 1. In general extreme events that last longer are more severe; for '
                 'example, an extremely hot day can be manageable, but a heatwave lasting several weeks is a serious '
                 'event.\n\nIt should be noted that precipitation is calculated as accumulated precipitation over the '
                 'entire time window.'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='4. Getting results')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            width=500,
            text='To search using the thresholds that you have selected, click "Query". After a loading time, your '
                 'results should appear in the panel to the right.\n\nResults will consist of the first and last date '
                 'where the event occurred, with one entry per event.\n\nConsecutive days that fit the search criteria '
                 'will be considered to be one "event" spanning multiple days, even if the user specified a duration '
                 'of one day. This is intended to simplify results.\n\nIf there are no results, try widening your '
                 'search criteria or checking that the thresholds you have set are appropriate for the region that you '
                 'have specified.'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='Data sources')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            width=500,
            text='This program requires accurate data for daily windspeed, precipitation, minimum temperature and '
                 'maximum temperature, which is packaged with the application in netCDF format.\n\nPrecipitation and '
                 'temperature data is sourced from LongPaddock\'s SILO database (found at '
                 'https://www.longpaddock.qld.gov.au/silo/), which uses mathematical interpolation techniques to '
                 'infill gaps in time series.\n\nWind data is sourced from NOAA-CIRES-DOE Twentieth Century Reanalysis '
                 '(found at https://psl.noaa.gov/data/gridded/data.20thC_ReanV3.monolevel.html). Wind data was '
                 'obtained as eastward and northward components, which was used to calculate the overall windspeed '
                 'that is used in this program.\n\nThe date range for the data used in this program is 1 January 1889 '
                 'to 31 December 2015.'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)
        tkinter.Message(scrollable_frame, anchor='w', font=heading_font, width=500, text='Contacts')\
            .pack(fill=tkinter.X, expand=tkinter.YES, pady=10)
        tkinter.Message(
            scrollable_frame,
            font=normal_font,
            justify=tkinter.LEFT,
            width=500,
            text='Laura Guillory\nWeb Developer\nCentre for Applied Climate Science\nUniversity of Southern Queensland'
                 '\nlaura.guillory@usq.edu.au'
        ).pack(fill=tkinter.X, expand=tkinter.YES, padx=20)

    # Event when the user uses the scrollwheel, ensures that using the scrollwheel will scroll the results.
    def _on_mousewheel(self, event):
        self.active_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

