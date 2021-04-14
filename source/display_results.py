import threading
import tkinter


class ThreadedDisplayResults(threading.Thread):
    def __init__(self, queue, results, window):
        threading.Thread.__init__(self)
        self.queue = queue
        self.results = results
        self.window = window

    def run(self):
        # Fallback in case of error during processing - clear the table
        if self.results is None:
            self.window.close_popup()
            return

        # Repurpose Labels if existing. If more Labels than required, hide them temporarily.
        for i, result in enumerate(self.results):
            start_date = '%02d-%02d-%d' % (result[0].year, result[0].month, result[0].day)
            end_date = '%02d-%02d-%d' % (result[1].year, result[1].month, result[1].day)
            if len(self.window.entries) <= i:
                self.window.entries.append([])
                self.window.entries[i].append(tkinter.Label(master=self.window.scrollable_frame, text=start_date,
                                                            borderwidth=1, relief='ridge', anchor='w', padx=10,
                                                            bg='white'))
                self.window.entries[i].append(tkinter.Label(master=self.window.scrollable_frame, text=end_date,
                                                            borderwidth=1, relief='ridge', anchor='w', padx=10,
                                                            bg='white'))
            else:
                self.window.entries[i][0]['text'] = start_date
                self.window.entries[i][1]['text'] = end_date
            self.window.entries[i][0].grid(row=i + 1, column=0, sticky='nsew')
            self.window.entries[i][1].grid(row=i + 1, column=1, sticky='nsew')
        if len(self.window.entries) > len(self.results):
            for i in range(len(self.results), len(self.window.entries)):
                self.window.entries[i][0].grid_forget()
                self.window.entries[i][1].grid_forget()
        self.window.results_canvas.yview_moveto(0)
        self.window.active_canvas = self.window.results_canvas
        self.window.close_popup()
