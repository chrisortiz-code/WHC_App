import customtkinter as ctk
import matplotlib.pyplot as plt
class PhoneEntryFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.entry1 = ctk.CTkEntry(self, width=40, justify='center')
        self.entry2 = ctk.CTkEntry(self, width=40, justify='center')
        self.entry3 = ctk.CTkEntry(self, width=50, justify='center')

        self.entry1.grid(row=0, column=0, padx=(0, 2))
        ctk.CTkLabel(self, text="-").grid(row=0, column=1)
        self.entry2.grid(row=0, column=2, padx=(2, 2))
        ctk.CTkLabel(self, text="-").grid(row=0, column=3)
        self.entry3.grid(row=0, column=4, padx=(2, 0))

        self.entry2.focus_set()
        print("focused")
        self.entry1.bind("<KeyRelease>", self.auto_focus)
        self.entry2.bind("<KeyRelease>", self.auto_focus)

    def auto_focus(self, event):
        print("self.entry1.get()")
        widget = event.widget
        if len(widget.get()) == 3 and widget == self.entry1:
            self.entry2.focus()
        elif len(widget.get()) == 3 and widget == self.entry2:
            self.entry3.focus()

app = ctk.CTk()
app.geometry("300x100")

phone_frame = PhoneEntryFrame(app)
phone_frame.pack(pady=20, padx=20)
app.mainloop()
