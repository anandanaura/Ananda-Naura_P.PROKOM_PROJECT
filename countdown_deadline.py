import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class DeadlineApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Aplikasi Deadline Modern")
        self.master.geometry("720x550")

        # Database
        self.conn = sqlite3.connect("tasks.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, deadline TEXT)"
        )

        # INPUT FRAME
        input_frame = ctk.CTkFrame(master, corner_radius=15)
        input_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(input_frame, text="Tambah Tugas Baru", font=("Segoe UI", 18, "bold")).pack(pady=10)

        self.task_entry = ctk.CTkEntry(input_frame, placeholder_text="Nama Tugas", width=450)
        self.task_entry.pack(pady=5)

        self.deadline_entry = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Deadline (YYYY-MM-DD HH:MM:SS)", 
            width=450
        )
        self.deadline_entry.pack(pady=5)

        ctk.CTkButton(input_frame, text="Tambah Tugas", command=self.add_task).pack(pady=10)

        # TOMBOL TUGAS HARI INI
        button_frame = ctk.CTkFrame(master, corner_radius=15)
        button_frame.pack(padx=20, pady=10, fill="x")

        self.today_button = ctk.CTkButton(
            button_frame,
            text="Pilih Tugas Hari Ini",
            height=40,
            command=self.pick_today_task
        )
        self.today_button.pack(pady=10)

        # TABEL / TEXTBOX
        table_frame = ctk.CTkFrame(master, corner_radius=15)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.task_box = ctk.CTkTextbox(table_frame, width=650, height=300)
        self.task_box.pack(pady=10)

        # Jalankan update setiap 1 detik
        self.update_tasks()

    # Tambah Tugas
    def add_task(self):
        name = self.task_entry.get()
        deadline = self.deadline_entry.get()

        if not name or not deadline:
            messagebox.showwarning("Warning", "Isi semua field dulu!")
            return

        try:
            datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except:
            messagebox.showerror("Format Salah", "Gunakan format:\nYYYY-MM-DD HH:MM:SS")
            return

        self.cursor.execute(
            "INSERT INTO tasks (name, deadline) VALUES (?, ?)",
            (name, deadline)
        )
        self.conn.commit()

        self.task_entry.delete(0, "end")
        self.deadline_entry.delete(0, "end")

        self.update_tasks()
        messagebox.showinfo("Sukses", "Tugas ditambahkan!")

    
    # Update Daftar + Countdown
    def update_tasks(self):
        self.task_box.delete("0.0", "end")

        self.cursor.execute("SELECT * FROM tasks ORDER BY deadline")
        tasks = self.cursor.fetchall()

        text = "DAFTAR TUGAS (Countdown)\n-------------------------------------\n\n"

        for t in tasks:
            name = t[1]
            deadline_str = t[2]

            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                diff = deadline - now

                if diff.total_seconds() <= 0:
                    countdown = "⛔ LEWAT DEADLINE!"
                else:
                    days = diff.days
                    hours, r = divmod(diff.seconds, 3600)
                    minutes, seconds = divmod(r, 60)
                    countdown = f"{days}h {hours}j {minutes}m {seconds}d"
            except:
                countdown = "ERROR DEADLINE"

            text += f"Tugas   : {name}\nDeadline: {deadline_str}\nSisa    : {countdown}\n\n"

        self.task_box.insert("0.0", text)

        # panggil update lagi setelah 1000ms
        self.master.after(1000, self.update_tasks)

   
    # TUGAS HARI INI (1 hari 1 tugas)
    def pick_today_task(self):
        self.cursor.execute("SELECT * FROM tasks ORDER BY deadline")
        tasks = self.cursor.fetchall()

        if not tasks:
            messagebox.showinfo("Info", "Tidak ada tugas.")
            return

        # Ambil tugas terdekat
        t = tasks[0]
        task_id, name, deadline = t

        messagebox.showinfo(
            "Tugas Hari Ini",
            f"Tugas: {name}\nDeadline: {deadline}\n\nKerjakan ini hari ini!"
        )

        # Hapus dari DB
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

        self.update_tasks()


root = ctk.CTk()
DeadlineApp(root)
root.mainloop()

