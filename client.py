from customtkinter import (
    CTk,
    CTkEntry,
    CTkFrame,
    CTkSwitch,
    CTkImage,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkLabel,
    CTkButton,
    set_appearance_mode,
    set_default_color_theme
)
from CTkMessagebox import CTkMessagebox
from PIL import Image
import sqlite3
import requests
import sys
import os
import time


class Client(CTk) :
    def __init__(self) :
        super().__init__()

        self.name = ""
        self.target = ""

        self.title("Messenger")
        self.geometry("450x650")
        self.resizable(False, False)
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM theme")
        theme = next(cur)
        self.appearance_mode = theme[0]
        if theme[0] in ["dark-blue", "blue", "green"] :
            set_default_color_theme(theme[0])
        else :
            set_default_color_theme(f"requirements/themes/{theme[0]}.json")
        set_appearance_mode(theme[1])
        conn.commit()
        conn.close()

        self.top_toolbar_frame = CTkFrame(self, width=450, height=60, corner_radius=0)
        self.top_toolbar_frame.place(x=0, y=0)

        CTkButton(self.top_toolbar_frame, text="", width=50, height=50, corner_radius=10,
                  image=CTkImage(Image.open("requirements/images/settings.png")),
                  command=self.settings_dialog).place(x=5, y=5)

        self.name_label = CTkLabel(self.top_toolbar_frame, text=self.name, font=("", 20))
        self.name_label.place(x=100, y=12)

        self.base_frame = CTkScrollableFrame(self, width=435, height=540, corner_radius=0)
        self.base_frame.place(x=0, y=60)

        message_frame = CTkFrame(self, corner_radius=0, width=450, height=50)
        message_frame.place(x=0, y=600)
        msg = CTkEntry(message_frame, width=360)
        msg.grid(row=0, column=0, pady=10, padx=10)
        msg.bind("<Return>", lambda event : self.send_message(msg.get()))
        self.btn = CTkButton(message_frame, text="Send ➜", width=0, command=lambda : self.send_message(msg.get()))
        self.btn.grid(row=0, column=1, pady=10, padx=10)

    def settings_dialog(self) :
        def exit_settings() :
            if name.get() and target.get :
                self.name = name.get()
                self.target = target.get()
                self.name_label.configure(text=f"{self.name}  ➜  {self.target}")
            settings_frame.place_forget()

        settings_frame = CTkFrame(self, width=450, height=650, corner_radius=0)
        back_btn = CTkButton(
            settings_frame, text="", width=50, height=50, corner_radius=10,
            image=CTkImage(Image.open("requirements/images/back_arrow.png")),
            command=exit_settings
        )
        back_btn.place(x=5, y=5)
        values = [i.replace(".json", "") for i in os.listdir("requirements/themes")]
        values.append("dark-blue")
        values.append("blue")
        values.append("green")
        ts = CTkOptionMenu(settings_frame, values=values, anchor="center",
                           corner_radius=10, command=self.change_theme)
        ts.set(self.appearance_mode)
        ts.place(x=160, y=50)
        sw = CTkSwitch(settings_frame, text="light/dark", command=self.change_theme)
        sw.place(x=180, y=100)
        name = CTkEntry(settings_frame, placeholder_text= \
            self.name if self.name else "Enter your name")
        name.place(x=160, y=170)
        target = CTkEntry(settings_frame, placeholder_text= \
            self.target if self.target else "Enter target name")
        target.place(x=160, y=200)
        settings_frame.place(x=0, y=0)

    def change_theme(self, theme=None) :
        if theme is not None :
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute(f"UPDATE theme SET 'color theme'='{theme}'")
            conn.commit()
            conn.close()
            msg = CTkMessagebox(
                title="Restart The Program ?",
                message="Do you want to restart the program\n"
                        "to apply the changes?",
                icon="question", option_1="Yes", option_2="No"
            )
            if msg.get() == "Yes" :
                python = sys.executable
                os.execl(python, python, *sys.argv)
        else :
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            match next(cur.execute(f"SELECT appearance from theme"))[0] :
                case "light" :
                    cur.execute(f"UPDATE theme SET appearance='dark'")
                    set_appearance_mode("dark")
                case "dark" :
                    cur.execute(f"UPDATE theme SET appearance='light'")
                    set_appearance_mode("light")
            conn.commit()
            conn.close()

    def send_message(self, message, receive: bool = False) :
        if message :
            hc = fc = (self.btn.cget("hover_color")[0], self.btn.cget("fg_color")[0],)
            plc = (200, 0)
            msg = ""
            for i in message.split() :
                msg += i + " "
                if len(msg.split("\n")[-1]) >= 30 :
                    msg += "\n"
            if receive :
                fc = tuple(reversed(fc))
                hc = tuple(reversed(hc))
                plc = tuple(reversed(plc))
            if not receive :
                requests.get(
                    "http://127.0.0.1:5000",
                    {
                        "receive" : "False",
                        "message" : msg,
                        "target" : self.target,
                        "name" : self.name
                    }
                )
            CTkButton(
                self.base_frame, text=msg,
                fg_color=fc,
                text_color=("#000", "#fff"),
                hover_color=hc
            ).pack(side="top", pady=5, padx=plc)

    def receive_message(self) :
        while True :
            self.bind("<Destroy>", ...)
            try :
                if message := requests.get("http://127.0.0.1:5000", {
                    "receive" : "True",
                    "target" : self.target,
                    "name" : self.name
                }).json()["message"] :
                    self.send_message(message, receive=True)
            except :
                pass
            for i in range(100) :
                time.sleep(0.01)
                self.update()

    def mainloop(self, *args, **kwargs) :
        self.after(1, self.receive_message)
        super().mainloop(*args, **kwargs)


if __name__ == "__main__" :
    t = Client()
    t.mainloop()
