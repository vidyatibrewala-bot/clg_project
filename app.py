"""
Smart Campus Resource & Room Booking System
Desktop GUI Application (Python Tkinter)

Features:
- Resource Catalog: Browse Auditoriums, Labs, Study Pods, Seminar Halls & Hardware Kits
- Real-Time Conflict Detection: Automatically blocks overlapping / duplicate time slots
- Multi-Role Support: Student, Professor, Lab Assistant, Campus Manager
- Admin Approval Workflow: One-click Approve / Reject controls for administrators
- Digital Access Pass: Displays booking code, PIN, and room access verification
- College Viva / Demo helpers: Built-in conflict simulation and database reset
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import database

# Color Scheme: Professional White & Emerald Green
COLOR_BG_DARK = "#f8fafc"
COLOR_BG_CARD = "#ffffff"
COLOR_BG_INPUT = "#ffffff"
COLOR_BORDER = "#e2e8f0"
COLOR_BRAND = "#059669"
COLOR_BRAND_HOVER = "#047857"
COLOR_TEXT_MAIN = "#0f172a"
COLOR_TEXT_MUTED = "#64748b"
COLOR_APPROVED = "#047857"
COLOR_PENDING = "#b45309"
COLOR_REJECTED = "#b91c1c"


class SmartCampusApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart Campus Resource & Room Booking System")
        self.geometry("1120x740")
        self.minsize(980, 640)
        self.configure(bg=COLOR_BG_DARK)

        # Active Persona / Role
        self.current_user = {
            "name": "Alex Rivera",
            "role": "Student"
        }

        self.setup_styles()
        self.create_header()
        self.create_tabs()
        self.update_status_bar()

        # Center on screen
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configure colors and fonts
        style.configure(".", background=COLOR_BG_DARK, foreground=COLOR_TEXT_MAIN, font=("Segoe UI", 10))
        
        # Tabs / Notebook styling
        style.configure("TNotebook", background=COLOR_BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_BG_CARD, foreground=COLOR_TEXT_MUTED,
                        padding=[16, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", COLOR_BRAND)],
                  foreground=[("selected", "#ffffff")])

        # Treeview (Tables)
        style.configure("Treeview",
                        background=COLOR_BG_CARD,
                        foreground=COLOR_TEXT_MAIN,
                        fieldbackground=COLOR_BG_CARD,
                        rowheight=28,
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background="#f1f5f9",
                        foreground=COLOR_TEXT_MAIN,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", "#d1fae5")], foreground=[("selected", "#047857")])

        # Buttons
        style.configure("Brand.TButton",
                        background=COLOR_BRAND,
                        foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"),
                        padding=[12, 6],
                        borderwidth=0)
        style.map("Brand.TButton",
                  background=[("active", COLOR_BRAND_HOVER)])

        style.configure("Secondary.TButton",
                        background="#f1f5f9",
                        foreground=COLOR_TEXT_MAIN,
                        font=("Segoe UI", 9),
                        padding=[10, 5],
                        borderwidth=0)
        style.map("Secondary.TButton",
                  background=[("active", "#e2e8f0")])

        style.configure("Approve.TButton",
                        background="#15803d",
                        foreground="#ffffff",
                        font=("Segoe UI", 9, "bold"),
                        padding=[10, 5])
        style.map("Approve.TButton", background=[("active", "#16a34a")])

        style.configure("Reject.TButton",
                        background="#b91c1c",
                        foreground="#ffffff",
                        font=("Segoe UI", 9, "bold"),
                        padding=[10, 5])
        style.map("Reject.TButton", background=[("active", "#dc2626")])

    # --------------------------------------------------------------------------
    # Top Header & Persona Switcher
    # --------------------------------------------------------------------------
    def create_header(self):
        header_frame = tk.Frame(self, bg=COLOR_BG_CARD, padx=18, pady=12)
        header_frame.pack(fill="x", side="top")

        # Left: Brand Logo & Title
        title_box = tk.Frame(header_frame, bg=COLOR_BG_CARD)
        title_box.pack(side="left")

        lbl_title = tk.Label(
            title_box,
            text="🏛️ Smart Campus Resource & Room Booking System",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MAIN
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = tk.Label(
            title_box,
            text="Digital space management • Automated conflict prevention • Admin approvals",
            font=("Segoe UI", 8),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MUTED
        )
        lbl_subtitle.pack(anchor="w")

        # Right: Persona Switcher and Demo Simulation Buttons
        right_box = tk.Frame(header_frame, bg=COLOR_BG_CARD)
        right_box.pack(side="right")

        tk.Label(right_box, text="Current User:", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))

        self.role_combobox = ttk.Combobox(
            right_box,
            values=[
                "Alex Rivera (Student)",
                "Dr. Elena Vance (Professor)",
                "Marcus Chen (Lab Assistant)",
                "Sarah Jenkins (Campus Manager)"
            ],
            state="readonly",
            width=26
        )
        self.role_combobox.current(0)
        self.role_combobox.pack(side="left", padx=4)
        self.role_combobox.bind("<<ComboboxSelected>>", self.on_persona_change)

        # "Simulate Conflict Test" demo helper button
        btn_conflict_demo = ttk.Button(
            right_box,
            text="⚡ Test Conflict Blocker",
            style="Brand.TButton",
            command=self.simulate_conflict_test
        )
        btn_conflict_demo.pack(side="left", padx=8)

        # Reset Demo Data button
        btn_reset = ttk.Button(
            right_box,
            text="🔄 Reset DB",
            style="Secondary.TButton",
            command=self.reset_system_data
        )
        btn_reset.pack(side="left", padx=2)

    def on_persona_change(self, event=None):
        val = self.role_combobox.get()
        if "Student" in val:
            self.current_user = {"name": "Alex Rivera", "role": "Student"}
        elif "Professor" in val:
            self.current_user = {"name": "Dr. Elena Vance", "role": "Professor"}
        elif "Lab Assistant" in val:
            self.current_user = {"name": "Marcus Chen", "role": "Lab Assistant"}
        elif "Campus Manager" in val:
            self.current_user = {"name": "Sarah Jenkins", "role": "Campus Manager"}

        self.update_status_bar()
        self.refresh_bookings_table()
        self.refresh_admin_table()

    # --------------------------------------------------------------------------
    # Main Tabs Container
    # --------------------------------------------------------------------------
    def create_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=8)

        # Tab 1: Resource Catalog
        self.tab_catalog = tk.Frame(self.notebook, bg=COLOR_BG_DARK, padx=12, pady=12)
        self.notebook.add(self.tab_catalog, text="  🏛️ Resource Catalog  ")
        self.build_catalog_tab()

        # Tab 2: New Reservation & Conflict Blocker
        self.tab_booking = tk.Frame(self.notebook, bg=COLOR_BG_DARK, padx=12, pady=12)
        self.notebook.add(self.tab_booking, text="  📅 Book a Slot  ")
        self.build_booking_tab()

        # Tab 3: All Bookings & Passes
        self.tab_bookings_list = tk.Frame(self.notebook, bg=COLOR_BG_DARK, padx=12, pady=12)
        self.notebook.add(self.tab_bookings_list, text="  📋 Reservation Log & Pass  ")
        self.build_bookings_list_tab()

        # Tab 4: Admin Approvals Center
        self.tab_admin = tk.Frame(self.notebook, bg=COLOR_BG_DARK, padx=12, pady=12)
        self.notebook.add(self.tab_admin, text="  🛡️ Admin Approvals  ")
        self.build_admin_tab()

        # Tab 5: Campus Analytics & Utility
        self.tab_analytics = tk.Frame(self.notebook, bg=COLOR_BG_DARK, padx=12, pady=12)
        self.notebook.add(self.tab_analytics, text="  📊 Analytics & Stats  ")
        self.build_analytics_tab()

        # Status Bar at bottom
        self.status_bar = tk.Label(
            self,
            text="Ready",
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            padx=12,
            pady=4
        )
        self.status_bar.pack(side="bottom", fill="x")

    def update_status_bar(self, custom_msg=None):
        if custom_msg:
            self.status_bar.config(text=custom_msg)
        else:
            stats = database.get_system_statistics()
            self.status_bar.config(
                text=f"Active User: {self.current_user['name']} ({self.current_user['role']})  |  "
                     f"Total Resources: {stats['total_resources']}  |  "
                     f"Total Bookings: {stats['total_bookings']}  |  "
                     f"Pending Approvals: {stats['pending_count']}  |  "
                     f"Active Today: {stats['today_active']}"
            )

    # --------------------------------------------------------------------------
    # Tab 1: Resource Catalog
    # --------------------------------------------------------------------------
    def build_catalog_tab(self):
        # Top filters bar
        filter_bar = tk.Frame(self.tab_catalog, bg=COLOR_BG_CARD, padx=10, pady=8)
        filter_bar.pack(fill="x", pady=(0, 10))

        tk.Label(filter_bar, text="Category Filter:", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        categories = database.get_all_categories()
        self.catalog_cat_cb = ttk.Combobox(filter_bar, values=categories, state="readonly", width=18)
        self.catalog_cat_cb.current(0)
        self.catalog_cat_cb.pack(side="left", padx=6)
        self.catalog_cat_cb.bind("<<ComboboxSelected>>", lambda e: self.load_catalog_resources())

        btn_refresh = ttk.Button(filter_bar, text="Refresh", style="Secondary.TButton", command=self.load_catalog_resources)
        btn_refresh.pack(side="left", padx=6)

        btn_book_sel = ttk.Button(filter_bar, text="⚡ Book Selected Resource", style="Brand.TButton", command=self.prefill_and_switch_to_booking)
        btn_book_sel.pack(side="right", padx=6)

        btn_view_day = ttk.Button(filter_bar, text="📅 View Today's Schedule", style="Secondary.TButton", command=self.view_selected_schedule)
        btn_view_day.pack(side="right", padx=6)

        # Catalog Table
        columns = ("id", "name", "category", "location", "capacity", "approval", "amenities")
        self.catalog_tree = ttk.Treeview(self.tab_catalog, columns=columns, show="headings", selectmode="browse")

        self.catalog_tree.heading("id", text="ID")
        self.catalog_tree.heading("name", text="Resource / Room Name")
        self.catalog_tree.heading("category", text="Category")
        self.catalog_tree.heading("location", text="Campus Location")
        self.catalog_tree.heading("capacity", text="Capacity")
        self.catalog_tree.heading("approval", text="Approval Required?")
        self.catalog_tree.heading("amenities", text="Key Amenities / Features")

        self.catalog_tree.column("id", width=40, anchor="center")
        self.catalog_tree.column("name", width=260)
        self.catalog_tree.column("category", width=110)
        self.catalog_tree.column("location", width=170)
        self.catalog_tree.column("capacity", width=75, anchor="center")
        self.catalog_tree.column("approval", width=120, anchor="center")
        self.catalog_tree.column("amenities", width=340)

        # Scrollbar
        scroll_y = ttk.Scrollbar(self.tab_catalog, orient="vertical", command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scroll_y.set)

        self.catalog_tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.load_catalog_resources()

    def load_catalog_resources(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        cat = self.catalog_cat_cb.get()
        resources = database.get_all_resources(cat)
        for r in resources:
            approval_str = "Yes (Admin Review)" if r["requires_approval"] == 1 else "No (Instant)"
            cap_str = f"{r['capacity']} people" if r['capacity'] > 1 else "1 kit"
            self.catalog_tree.insert("", "end", values=(
                r["id"],
                r["name"],
                r["category"],
                r["location"],
                cap_str,
                approval_str,
                r["amenities"] or ""
            ))

    def prefill_and_switch_to_booking(self):
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showinfo("Select Resource", "Please click on a resource in the table first.")
            return

        item = self.catalog_tree.item(selected[0])
        res_id = item["values"][0]
        res_name = item["values"][1]

        # Populate Booking Tab dropdown and switch to Tab 2
        for idx, text in enumerate(self.booking_res_cb["values"]):
            if f"[{res_id}]" in text:
                self.booking_res_cb.current(idx)
                break

        self.notebook.select(self.tab_booking)

    def view_selected_schedule(self):
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showinfo("Select Resource", "Please click on a resource to inspect its schedule.")
            return

        item = self.catalog_tree.item(selected[0])
        res_id = item["values"][0]
        res_name = item["values"][1]
        today = datetime.date.today().strftime("%Y-%m-%d")

        bookings = database.get_day_schedule_for_resource(res_id, today)

        info = f"Schedule for: {res_name}\nDate: {today}\n"
        info += "=" * 50 + "\n\n"

        if not bookings:
            info += "✅ No bookings scheduled today. The room is 100% available!"
        else:
            info += f"Occupied Slots ({len(bookings)}):\n"
            for b in bookings:
                info += f"• {b['start_time']} - {b['end_time']} : {b['purpose']} (by {b['user_name']}, {b['status']})\n"

        messagebox.showinfo("Room Schedule", info)

    # --------------------------------------------------------------------------
    # Tab 2: New Reservation & Conflict Blocker
    # --------------------------------------------------------------------------
    def build_booking_tab(self):
        container = tk.Frame(self.tab_booking, bg=COLOR_BG_DARK)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # Card Frame
        card = tk.Frame(container, bg=COLOR_BG_CARD, padx=24, pady=20, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        lbl_header = tk.Label(
            card,
            text="📅 Campus Space & Equipment Reservation",
            font=("Segoe UI", 13, "bold"),
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MAIN
        )
        lbl_header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # 1. Resource Selector
        tk.Label(card, text="Select Resource / Space *", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        resources = database.get_all_resources()
        res_options = [f"[{r['id']}] {r['name']} ({r['category']})" for r in resources]

        self.booking_res_cb = ttk.Combobox(card, values=res_options, state="readonly", width=46)
        if res_options:
            self.booking_res_cb.current(0)
        self.booking_res_cb.grid(row=1, column=1, sticky="w", pady=6)

        # 2. Date Picker
        tk.Label(card, text="Date (YYYY-MM-DD) *", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.entry_date = tk.Entry(card, bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, highlightbackground=COLOR_BORDER, highlightthickness=1, width=22, font=("Segoe UI", 10))
        self.entry_date.insert(0, today_str)
        self.entry_date.grid(row=2, column=1, sticky="w", pady=6)

        # 3. Start & End Time
        tk.Label(card, text="Start Time (HH:MM) *", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=6)
        time_frame = tk.Frame(card, bg=COLOR_BG_CARD)
        time_frame.grid(row=3, column=1, sticky="w", pady=6)

        self.entry_start_time = tk.Entry(time_frame, bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, highlightbackground=COLOR_BORDER, highlightthickness=1, width=8, font=("Segoe UI", 10))
        self.entry_start_time.insert(0, "14:00")
        self.entry_start_time.pack(side="left")

        tk.Label(time_frame, text="   End Time: ", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.entry_end_time = tk.Entry(time_frame, bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, highlightbackground=COLOR_BORDER, highlightthickness=1, width=8, font=("Segoe UI", 10))
        self.entry_end_time.insert(0, "15:30")
        self.entry_end_time.pack(side="left")

        # 4. Attendees
        tk.Label(card, text="Expected Attendees", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=6)
        self.entry_attendees = tk.Entry(card, bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, highlightbackground=COLOR_BORDER, highlightthickness=1, width=10, font=("Segoe UI", 10))
        self.entry_attendees.insert(0, "4")
        self.entry_attendees.grid(row=4, column=1, sticky="w", pady=6)

        # 5. Purpose
        tk.Label(card, text="Meeting Purpose / Title *", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w", pady=6)
        self.entry_purpose = tk.Entry(card, bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, highlightbackground=COLOR_BORDER, highlightthickness=1, width=46, font=("Segoe UI", 10))
        self.entry_purpose.insert(0, "Senior Project Architecture & Code Review")
        self.entry_purpose.grid(row=5, column=1, sticky="w", pady=6)

        # Conflict Check Banner / Preview Box
        self.conflict_status_label = tk.Label(
            card,
            text="⚡ Double-Booking Blocker: Active & Ready",
            bg="#ecfdf5",
            fg="#047857",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
            anchor="w"
        )
        self.conflict_status_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(15, 12))

        # Buttons Frame
        btn_box = tk.Frame(card, bg=COLOR_BG_CARD)
        btn_box.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))

        btn_check = ttk.Button(btn_box, text="🔍 Check Live Conflict", style="Secondary.TButton", command=self.check_conflict_only)
        btn_check.pack(side="left", padx=(0, 10))

        btn_submit = ttk.Button(btn_box, text="✅ Confirm Reservation", style="Brand.TButton", command=self.submit_booking)
        btn_submit.pack(side="left")

    def get_selected_resource_id(self):
        val = self.booking_res_cb.get()
        if not val or "[" not in val:
            return None
        res_id_str = val.split("[")[1].split("]")[0]
        return int(res_id_str)

    def check_conflict_only(self):
        res_id = self.get_selected_resource_id()
        if not res_id:
            messagebox.showwarning("Incomplete Form", "Please select a resource first.")
            return

        date_val = self.entry_date.get().strip()
        start_val = self.entry_start_time.get().strip()
        end_val = self.entry_end_time.get().strip()

        has_conflict, conflict, msg = database.check_booking_conflict(res_id, date_val, start_val, end_val)

        if has_conflict:
            self.conflict_status_label.config(
                text=f"🚨 CONFLICT DETECTED! Overlaps with an existing reservation.",
                bg="#fef2f2",
                fg="#b91c1c"
            )
            messagebox.showerror("Automated Conflict Prevention", msg)
        else:
            self.conflict_status_label.config(
                text="✅ Slot is 100% available with zero scheduling clashes!",
                bg="#ecfdf5",
                fg="#047857"
            )
            messagebox.showinfo("Slot Available", "Great news! The requested time window is completely free.")

    def submit_booking(self):
        res_id = self.get_selected_resource_id()
        if not res_id:
            messagebox.showwarning("Incomplete Form", "Please select a resource.")
            return

        date_val = self.entry_date.get().strip()
        start_val = self.entry_start_time.get().strip()
        end_val = self.entry_end_time.get().strip()
        purpose_val = self.entry_purpose.get().strip()

        try:
            attendees_val = int(self.entry_attendees.get().strip())
        except ValueError:
            attendees_val = 1

        if not purpose_val:
            messagebox.showwarning("Incomplete Form", "Please provide a purpose or meeting agenda.")
            return

        # Attempt to create booking (enforces conflict blocker)
        success, msg, code = database.create_booking(
            resource_id=res_id,
            user_name=self.current_user["name"],
            user_role=self.current_user["role"],
            booking_date=date_val,
            start_time=start_val,
            end_time=end_val,
            purpose=purpose_val,
            attendees=attendees_val
        )

        if not success:
            # Overlap prevented!
            self.conflict_status_label.config(
                text="🚨 DOUBLE-BOOKING PREVENTED! The system blocked this duplicate slot.",
                bg="#fef2f2",
                fg="#b91c1c"
            )
            messagebox.showerror("Conflict Engine Block", msg)
            return

        # Success!
        self.conflict_status_label.config(
            text=f"✅ Booking Confirmed! Code: {code}",
            bg="#ecfdf5",
            fg="#047857"
        )
        messagebox.showinfo("Reservation Success", f"{msg}\n\nYour digital access code is: {code}")

        self.update_status_bar()
        self.refresh_bookings_table()
        self.refresh_admin_table()
        self.refresh_analytics()
        self.notebook.select(self.tab_bookings_list)

    # --------------------------------------------------------------------------
    # Tab 3: Reservation Log & Digital Access Pass
    # --------------------------------------------------------------------------
    def build_bookings_list_tab(self):
        filter_bar = tk.Frame(self.tab_bookings_list, bg=COLOR_BG_CARD, padx=10, pady=8)
        filter_bar.pack(fill="x", pady=(0, 10))

        tk.Label(filter_bar, text="Status Filter:", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        self.bookings_status_cb = ttk.Combobox(filter_bar, values=["All", "Pending", "Approved", "Rejected"], state="readonly", width=14)
        self.bookings_status_cb.current(0)
        self.bookings_status_cb.pack(side="left", padx=6)
        self.bookings_status_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_bookings_table())

        btn_refresh = ttk.Button(filter_bar, text="Refresh", style="Secondary.TButton", command=self.refresh_bookings_table)
        btn_refresh.pack(side="left", padx=6)

        btn_pass = ttk.Button(filter_bar, text="🎟️ View Digital Room Pass", style="Brand.TButton", command=self.view_selected_pass)
        btn_pass.pack(side="right", padx=6)

        btn_cancel = ttk.Button(filter_bar, text="Cancel Slot", style="Secondary.TButton", command=self.cancel_selected_booking)
        btn_cancel.pack(side="right", padx=4)

        # Table
        cols = ("id", "code", "resource", "user", "role", "date", "time", "attendees", "status", "purpose")
        self.bookings_tree = ttk.Treeview(self.tab_bookings_list, columns=cols, show="headings", selectmode="browse")

        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("code", text="Pass Code")
        self.bookings_tree.heading("resource", text="Resource Name")
        self.bookings_tree.heading("user", text="Reserved By")
        self.bookings_tree.heading("role", text="Role")
        self.bookings_tree.heading("date", text="Date")
        self.bookings_tree.heading("time", text="Time Slot")
        self.bookings_tree.heading("attendees", text="Att.")
        self.bookings_tree.heading("status", text="Status")
        self.bookings_tree.heading("purpose", text="Purpose")

        self.bookings_tree.column("id", width=35, anchor="center")
        self.bookings_tree.column("code", width=85, anchor="center")
        self.bookings_tree.column("resource", width=220)
        self.bookings_tree.column("user", width=130)
        self.bookings_tree.column("role", width=100)
        self.bookings_tree.column("date", width=95, anchor="center")
        self.bookings_tree.column("time", width=110, anchor="center")
        self.bookings_tree.column("attendees", width=45, anchor="center")
        self.bookings_tree.column("status", width=90, anchor="center")
        self.bookings_tree.column("purpose", width=230)

        scroll_y = ttk.Scrollbar(self.tab_bookings_list, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scroll_y.set)

        self.bookings_tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.refresh_bookings_table()

    def refresh_bookings_table(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        status_filter = self.bookings_status_cb.get()
        bookings = database.get_all_bookings(status_filter=status_filter)

        for b in bookings:
            self.bookings_tree.insert("", "end", values=(
                b["id"],
                b["booking_code"],
                b["resource_name"],
                b["user_name"],
                b["user_role"],
                b["booking_date"],
                f"{b['start_time']} - {b['end_time']}",
                b["attendees"],
                b["status"],
                b["purpose"]
            ))

    def view_selected_pass(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showinfo("Select Booking", "Please select a booking from the table first.")
            return

        item = self.bookings_tree.item(selected[0])
        val = item["values"]
        b_code = val[1]
        res_name = val[2]
        user_name = val[3]
        user_role = val[4]
        date_str = val[5]
        slot_str = val[6]
        status_str = val[8]
        purpose_str = val[9]

        pin_code = str((int(b_code.replace("BKG-", "")) * 37 + 1019) % 9000 + 1000)

        pass_text = f"""
=====================================================
🏛️ UNIVERSITY SMART CAMPUS SECURE ACCESS PASS
=====================================================
Booking Reference : {b_code}
Resource / Room   : {res_name}
Authorized Holder : {user_name} ({user_role})
Date of Access    : {date_str}
Allocated Window  : {slot_str}
Status            : {status_str}
Agenda / Purpose  : {purpose_str}

-----------------------------------------------------
DOOR READER KEYPAD PIN : {pin_code}
DIGITAL PASS QR TOKEN  : CAMPUS-{b_code}-SECURE
-----------------------------------------------------
Instructions:
1. Enter the 4-digit PIN on the digital door lock.
2. If room is unoccupied for 15 mins, IoT sensors
   will auto-release the reservation.
=====================================================
"""
        messagebox.showinfo("Digital Campus Room Pass", pass_text)

    def cancel_selected_booking(self):
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showinfo("Select Booking", "Please select a reservation to cancel.")
            return

        item = self.bookings_tree.item(selected[0])
        b_id = item["values"][0]
        b_code = item["values"][1]

        if messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel reservation {b_code}?"):
            database.update_booking_status(b_id, "Cancelled")
            messagebox.showinfo("Cancelled", f"Reservation {b_code} has been cancelled. The time slot is now free!")
            self.refresh_bookings_table()
            self.refresh_admin_table()
            self.update_status_bar()

    # --------------------------------------------------------------------------
    # Tab 4: Admin Approvals Center
    # --------------------------------------------------------------------------
    def build_admin_tab(self):
        # KPI Row
        kpi_frame = tk.Frame(self.tab_admin, bg=COLOR_BG_DARK)
        kpi_frame.pack(fill="x", pady=(0, 10))

        self.lbl_kpi_pending = tk.Label(
            kpi_frame,
            text="⏳ Pending: 0",
            bg=COLOR_BG_CARD,
            fg=COLOR_PENDING,
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.lbl_kpi_pending.pack(side="left", padx=(0, 10))

        self.lbl_kpi_approved = tk.Label(
            kpi_frame,
            text="✅ Approved: 0",
            bg=COLOR_BG_CARD,
            fg=COLOR_APPROVED,
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.lbl_kpi_approved.pack(side="left", padx=(0, 10))

        self.lbl_kpi_today = tk.Label(
            kpi_frame,
            text="⚡ Active Today: 0",
            bg=COLOR_BG_CARD,
            fg=COLOR_BRAND_HOVER,
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.lbl_kpi_today.pack(side="left")

        # Admin Actions Toolbar
        admin_toolbar = tk.Frame(self.tab_admin, bg=COLOR_BG_CARD, padx=10, pady=8)
        admin_toolbar.pack(fill="x", pady=(0, 10))

        tk.Label(admin_toolbar, text="Admin Approval Queue:", bg=COLOR_BG_CARD, fg=COLOR_TEXT_MAIN, font=("Segoe UI", 10, "bold")).pack(side="left", padx=4)

        btn_approve = ttk.Button(admin_toolbar, text="✅ Approve Selected", style="Approve.TButton", command=self.admin_approve_selected)
        btn_approve.pack(side="right", padx=6)

        btn_reject = ttk.Button(admin_toolbar, text="❌ Reject Selected", style="Reject.TButton", command=self.admin_reject_selected)
        btn_reject.pack(side="right", padx=6)

        btn_refresh = ttk.Button(admin_toolbar, text="Refresh Queue", style="Secondary.TButton", command=self.refresh_admin_table)
        btn_refresh.pack(side="right", padx=6)

        # Admin Queue Table
        cols = ("id", "code", "resource", "user", "role", "date", "time", "purpose", "status")
        self.admin_tree = ttk.Treeview(self.tab_admin, columns=cols, show="headings", selectmode="browse")

        self.admin_tree.heading("id", text="ID")
        self.admin_tree.heading("code", text="Pass Code")
        self.admin_tree.heading("resource", text="Resource Name")
        self.admin_tree.heading("user", text="Requested By")
        self.admin_tree.heading("role", text="Role")
        self.admin_tree.heading("date", text="Date")
        self.admin_tree.heading("time", text="Time Slot")
        self.admin_tree.heading("purpose", text="Purpose")
        self.admin_tree.heading("status", text="Current Status")

        self.admin_tree.column("id", width=35, anchor="center")
        self.admin_tree.column("code", width=85, anchor="center")
        self.admin_tree.column("resource", width=230)
        self.admin_tree.column("user", width=140)
        self.admin_tree.column("role", width=105)
        self.admin_tree.column("date", width=95, anchor="center")
        self.admin_tree.column("time", width=110, anchor="center")
        self.admin_tree.column("purpose", width=250)
        self.admin_tree.column("status", width=95, anchor="center")

        scroll_y = ttk.Scrollbar(self.tab_admin, orient="vertical", command=self.admin_tree.yview)
        self.admin_tree.configure(yscrollcommand=scroll_y.set)

        self.admin_tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.refresh_admin_table()

    def refresh_admin_table(self):
        for item in self.admin_tree.get_children():
            self.admin_tree.delete(item)

        stats = database.get_system_statistics()
        self.lbl_kpi_pending.config(text=f"⏳ Pending: {stats['pending_count']}")
        self.lbl_kpi_approved.config(text=f"✅ Approved: {stats['approved_count']}")
        self.lbl_kpi_today.config(text=f"⚡ Active Today: {stats['today_active']}")

        bookings = database.get_all_bookings()
        for b in bookings:
            self.admin_tree.insert("", "end", values=(
                b["id"],
                b["booking_code"],
                b["resource_name"],
                b["user_name"],
                b["user_role"],
                b["booking_date"],
                f"{b['start_time']} - {b['end_time']}",
                b["purpose"],
                b["status"]
            ))

    def admin_approve_selected(self):
        selected = self.admin_tree.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select a booking to approve.")
            return

        item = self.admin_tree.item(selected[0])
        b_id = item["values"][0]
        b_code = item["values"][1]

        database.update_booking_status(b_id, "Approved")
        messagebox.showinfo("Approved", f"Reservation {b_code} has been APPROVED! Access pass is now valid.")
        self.refresh_admin_table()
        self.refresh_bookings_table()
        self.update_status_bar()

    def admin_reject_selected(self):
        selected = self.admin_tree.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select a booking to reject.")
            return

        item = self.admin_tree.item(selected[0])
        b_id = item["values"][0]
        b_code = item["values"][1]

        database.update_booking_status(b_id, "Rejected")
        messagebox.showwarning("Rejected", f"Reservation {b_code} has been REJECTED.")
        self.refresh_admin_table()
        self.refresh_bookings_table()
        self.update_status_bar()

    # --------------------------------------------------------------------------
    # Tab 5: Analytics & Stats
    # --------------------------------------------------------------------------
    def build_analytics_tab(self):
        container = tk.Frame(self.tab_analytics, bg=COLOR_BG_DARK, padx=16, pady=16)
        container.pack(fill="both", expand=True)

        self.lbl_analytics_summary = tk.Label(
            container,
            text="",
            bg=COLOR_BG_CARD,
            fg=COLOR_TEXT_MAIN,
            font=("Segoe UI", 10),
            justify="left",
            padx=20,
            pady=16,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.lbl_analytics_summary.pack(fill="both", expand=True)

        self.refresh_analytics()

    def refresh_analytics(self):
        stats = database.get_system_statistics()
        bookings = database.get_all_bookings()
        today = datetime.date.today().strftime("%Y-%m-%d")

        text = f"""
====================================================================================
📊 SMART CAMPUS RESOURCE MANAGEMENT & SCHEDULING METRICS
====================================================================================

Key Performance Indicators (KPIs):
  • Total Registered Resources (Rooms + Hardware):  {stats['total_resources']}
  • Total System Reservations Logged:             {stats['total_bookings']}
  • Active Reservations Today ({today}):          {stats['today_active']}
  • Pending Administrator Sign-Offs:              {stats['pending_count']}
  • Approved Active Reservations:                 {stats['approved_count']}

Core Engine Guarantees (From Project Presentation):
  1. Automated Conflict Blocker:
     Prevents double-booking overlapping slots across all rooms using exact interval testing:
     [Start_A, End_A] clashes if (Start_A < End_B) AND (End_A > Start_B).

  2. Role-Based Governance:
     • Students: Instant booking for study pods and project labs.
     • Professors: Priority reservations for auditoriums and seminar halls.
     • Lab Assistants: Hardware kit tracking and component testing stations.
     • Campus Managers: Centralized one-click approval/rejection console.

  3. Future Scope / IoT Integration (Slide 11):
     • Presence sensor simulation: Auto-releases slots if 15 minutes pass with no occupants.
     • Energy optimization: Standby mode activated when rooms are free.
====================================================================================
"""
        self.lbl_analytics_summary.config(text=text)

    # --------------------------------------------------------------------------
    # Presentation / Viva Helpers
    # --------------------------------------------------------------------------
    def simulate_conflict_test(self):
        """Simulates an immediate double-booking attempt to show evaluators."""
        today = datetime.date.today().strftime("%Y-%m-%d")

        # Select Tab 2
        self.notebook.select(self.tab_booking)

        # Pre-fill with slot 10:30 to 11:30 for Grand Innovation Auditorium
        # (which deliberately collides with Dr. Vance's keynote 10:00 to 12:00)
        self.booking_res_cb.current(0)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, today)
        self.entry_start_time.delete(0, tk.END)
        self.entry_start_time.insert(0, "10:30")
        self.entry_end_time.delete(0, tk.END)
        self.entry_end_time.insert(0, "11:30")
        self.entry_purpose.delete(0, tk.END)
        self.entry_purpose.insert(0, "Duplicate Student Session Test (Demonstrating Conflict Blocker)")

        self.check_conflict_only()

    def reset_system_data(self):
        if messagebox.askyesno("Reset Database", "Reset all campus bookings and resources back to the default demo state?"):
            database.reset_database()
            self.load_catalog_resources()
            self.refresh_bookings_table()
            self.refresh_admin_table()
            self.refresh_analytics()
            self.update_status_bar()
            messagebox.showinfo("Reset Complete", "Database successfully restored to clean initial demo state.")


if __name__ == "__main__":
    app = SmartCampusApp()
    app.mainloop()
