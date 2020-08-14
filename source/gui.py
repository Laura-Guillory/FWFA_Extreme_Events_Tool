import tkinter
from tkinter import ttk, messagebox
import query
import threading


def validate_number(value):
    if value in ['', '-']:
        return True
    try:
        float(value)
    except ValueError:
        return False
    return True


class MainApplication:
    def __init__(self):
        # Set up main window
        self.window = tkinter.Tk()
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.title('Forewarned is Forearmed - Historical Frequency of Extreme Events')

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
        self.column_right.rowconfigure(2, weight=1)

        # Set up location section
        self.frame1 = tkinter.LabelFrame(master=self.column_left, text='1. Select Location', height=200, padx=5, pady=5)
        self.frame1.columnconfigure(1, weight=1)

        self.select_station_label = tkinter.Label(master=self.frame1, text='Choose a station:', width=13, anchor='w')

        self.station_list = query.get_all_stations()
        self.station_combobox = tkinter.ttk.Combobox(self.frame1, state='readonly', values=self.station_list)
        self.station_combobox.current(0)

        self.select_station_label.grid(row=0, column=0, padx=10, pady=10)
        self.station_combobox.grid(row=0, column=1, padx=5, pady=10, sticky='sew')
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky='new')

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
        self.frame2.grid(row=1, column=0, padx=10, pady=10, sticky='new')

        # Set up duration section
        self.frame3 = tkinter.LabelFrame(master=self.column_left, text='3. Select Duration', padx=5, pady=5)

        self.duration_label1 = tkinter.Label(master=self.frame3, text='For')
        self.duration_entry = tkinter.Entry(
            master=self.frame3,
            width=5,
            validate='key',
            validatecommand=(self.v_number, '%P'),
            invalidcommand=(self.i_number, '%i', '%W', '%d')
        )
        self.duration_entry.insert(0, '1')
        self.duration_label2 = tkinter.Label(master=self.frame3, text='consecutive days')

        self.duration_label1.grid(row=0, column=0, padx=10, pady=10)
        self.duration_entry.grid(row=0, column=1, pady=10)
        self.duration_label2.grid(row=0, column=2, padx=10, pady=10)
        self.frame3.grid(row=2, column=0, padx=10, pady=10, sticky='new')

        # Query button
        self.button = tkinter.Button(
            master=self.column_left,
            text='Query',
            width=20,
            bg='#dddddd',
            command=self.query_button_press
        )

        self.button.grid(row=3, column=0, padx=10, pady=10, sticky='nw')

        # Separator
        self.separator = ttk.Separator(self.column_middle, orient='vertical')
        self.separator.grid(row=0, column=0, sticky='ns')

        # Set up results section
        self.results_label = tkinter.Label(master=self.column_right, text='RESULTS', anchor='w')
        self.results_summary = tkinter.Message(master=self.column_right, text='Placeholder', anchor='w', width=210)
        self.results_container = tkinter.Frame(
            master=self.column_right,
            width=230,
            borderwidth=3,
            relief='sunken'
        )

        self.results_label.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        self.results_summary.grid()
        self.results_summary.grid_forget()
        self.results_container.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        self.window.mainloop()

    def update_temperature_entry(self, event: tkinter.Event):
        if self.temperature_condition_combobox.get() == 'Any':
            self.temperature_entry.configure(state='disabled')
        else:
            self.temperature_entry.configure(state='normal')

    def update_precipitation_entry(self, event: tkinter.Event):
        if self.precipitation_condition_combobox.get() == 'Any':
            self.precipitation_entry.configure(state='disabled')
        else:
            self.precipitation_entry.configure(state='normal')

    def update_wind_entry(self, event: tkinter.Event):
        if self.wind_condition_combobox.get() == 'Any':
            self.wind_entry.configure(state='disabled')
        else:
            self.wind_entry.configure(state='normal')

    def invalid_number(self, index, widget_name, action):
        widget = self.window.nametowidget(widget_name)
        if action == '0':
            widget.delete(0, tkinter.END)
        else:
            widget.delete(index, index)
        widget.after_idle(lambda: widget.configure(validate='key'))

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
            }
        }
        threading.Thread(target=self.threaded_query, args=(query_parameters,)).start()

    def threaded_query(self, query_parameters):
        results = query.make_query(query_parameters)
        self.display_results(results)

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
        return True

    def display_results(self, results):
        # Refresh summary
        new_text = 'The specified conditions have occurred {} times over 126 years (1889-2015)'.format(len(results))
        self.results_summary['text'] = new_text
        self.results_summary.grid(row=1, column=0, padx=10, pady=(5, 10), sticky='ew')

        # Get rid of old results
        self.results_container.destroy()

        # Create canvas for table and scrollbar
        self.results_container = tkinter.Frame(master=self.column_right, width=50, borderwidth=3, relief='sunken')
        self.results_container.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.results_container.rowconfigure(0, weight=1)
        canvas = tkinter.Canvas(self.results_container, width=200)
        scrollbar = tkinter.Scrollbar(self.results_container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        scrollable_frame = tkinter.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=scrollable_frame.bbox("all")))
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_frame, width=e.width-4))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky='nsew')

        # Create results table
        table_head1 = tkinter.Label(master=scrollable_frame, text='Start Date', borderwidth=1, relief='ridge',
                                    anchor='w', padx=10)
        table_head2 = tkinter.Label(master=scrollable_frame, text='End Date', borderwidth=1, relief='ridge', anchor='w',
                                    padx=10)
        table_head1.grid(row=0, column=0, sticky='nsew')
        table_head2.grid(row=0, column=1, sticky='nsew')
        for i, result in enumerate(results):
            start_date = result[0].strftime('%Y-%m-%d')
            end_date = result[1].strftime('%Y-%m-%d')
            label1 = tkinter.Label(master=scrollable_frame, text=start_date, borderwidth=1, relief='ridge', bg='white',
                                   anchor='w', padx=10)
            label2 = tkinter.Label(master=scrollable_frame, text=end_date, borderwidth=1, relief='ridge', bg='white',
                                   anchor='w', padx=10)
            label1.grid(row=i+1, column=0, sticky='nsew')
            label2.grid(row=i+1, column=1, sticky='nsew')


if __name__ == '__main__':
    MainApplication()
