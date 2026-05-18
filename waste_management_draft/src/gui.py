import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import threading
import sys
import os

# Add src path ensuring we can import backend logic
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from data_loader import load_all
from engine import SimulationEngine

# User Management & Auth Imports
from user_management.user_manager import UserManager
from user_management.input_handler import InputProcessor
from auth import auth

class WasteWiseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WasteWise - Integrated Urban System")
        self.geometry("1100x800")
        self.is_dark_mode = False
        
        # Shared Managers
        self.user_manager = UserManager()
        self.input_processor = InputProcessor()
        
        # Simulation Logic (Shared across views)
        bins, vehicles, facilities, graph = load_all()
        self.engine = SimulationEngine(bins, vehicles, facilities, graph)
        self.engine.reset_all()

        # Styles
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        self.apply_theme()

        # Transition to Login
        self.show_login()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        bg_color = "#2b2b2b" if self.is_dark_mode else "#f4f4f9"
        fg_color = "#ffffff" if self.is_dark_mode else "#000000"
        input_bg = "#3c3f41" if self.is_dark_mode else "#ffffff"
        input_fg = "#ffffff" if self.is_dark_mode else "#000000"

        self.configure(bg=bg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 14, "bold"))
        self.style.configure("Title.TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 18, "bold"))
        
        # Treeview formatting
        self.style.configure("Treeview", background=input_bg, foreground=input_fg, fieldbackground=input_bg)
        self.style.configure("Treeview.Heading", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", foreground=fg_color) 
        
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.log_text.configure(bg=input_bg, fg=input_fg, insertbackground=input_fg)
            
        if hasattr(self, 'current_user') and self.current_user:
            if self.current_user.role.lower() == 'admin':
                if hasattr(self, 'admin_bin_widgets'):
                    self.refresh_admin_ui()
            else:
                if hasattr(self, 'res_bin_widgets'):
                    self.refresh_resident_ui()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
        if hasattr(self, 'admin_bin_widgets'):
            del self.admin_bin_widgets
        if hasattr(self, 'res_bin_widgets'):
            del self.res_bin_widgets

    def show_login(self):
        self.current_user = None
        self.clear_window()
        self.apply_theme()
        self.title("WasteWise Login")
        self.geometry("400x380")
        
        theme_btn = ttk.Button(self, text="Toggle Theme", command=self.toggle_theme)
        theme_btn.place(relx=0.95, rely=0.05, anchor=tk.NE)
        
        frame = ttk.Frame(self, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(frame, text="WasteWise Login", style="Title.TLabel").pack(pady=(0, 20))
        
        ttk.Label(frame, text="Enter User ID:").pack(anchor=tk.W)
        ent_id = ttk.Entry(frame, width=30)
        ent_id.pack(pady=(5, 10))
        ent_id.focus_set()
        
        ttk.Label(frame, text="Enter Password:").pack(anchor=tk.W)
        ent_pwd = ttk.Entry(frame, width=30, show="*")
        ent_pwd.pack(pady=(5, 20))
        
        def do_login(event=None):
            uid = ent_id.get().strip()
            pwd = ent_pwd.get().strip()
            
            user = auth.login(uid, pwd)
            if user:
                self.current_user = user
                if user.role.lower() == 'admin':
                    self.show_admin(user)
                else:
                    self.show_resident(user)
            else:
                messagebox.showerror("Login Failed", "Invalid User ID or Password")
                ent_id.delete(0, tk.END)
                ent_pwd.delete(0, tk.END)
                ent_id.focus_set()

        ent_id.bind("<Return>", do_login)
        ent_pwd.bind("<Return>", do_login)
        ttk.Button(frame, text="Login", command=do_login).pack(fill=tk.X, pady=(10, 0))

    # -------------------------------------------------------------------------
    #  ADMIN DASHBOARD VIEW
    # -------------------------------------------------------------------------
    def show_admin(self, user):
        self.clear_window()
        self.apply_theme()
        self.title(f"WasteWise Admin - {user.name}")
        self.geometry("1100x750")
        self.current_user = user

        # Header
        head = ttk.Frame(self, padding=5)
        head.pack(fill=tk.X)
        ttk.Button(head, text="Logout", command=self.show_login).pack(side=tk.RIGHT, padx=10)
        ttk.Button(head, text="Toggle Theme", command=self.toggle_theme).pack(side=tk.RIGHT, padx=10)
        ttk.Button(head, text="Manage Users", command=self.show_user_management).pack(side=tk.RIGHT, padx=10)
        ttk.Label(head, text=f"Logged in as: {user.name} (Admin)", font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT, padx=10)

        # Main Layout
        self.left_panel = ttk.Frame(self, padding=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_panel = ttk.Frame(self, padding=10)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bins Area
        ttk.Label(self.left_panel, text="City Waste Bins", style="Header.TLabel").pack(anchor=tk.W)
        self.bins_frame = ttk.Frame(self.left_panel)
        self.bins_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.admin_bin_widgets = {}
        for b in self.engine.bins:
            row = ttk.Frame(self.bins_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{b.bin_id} ({b.waste_type})", width=25).pack(side=tk.LEFT)
            pb = ttk.Progressbar(row, orient=tk.HORIZONTAL, length=200, mode='determinate')
            pb.pack(side=tk.LEFT, padx=10)
            val = ttk.Label(row, text="0.0%", width=15)
            val.pack(side=tk.LEFT)
            self.admin_bin_widgets[b.bin_id] = {"pb": pb, "val": val}

        # Facilities
        ttk.Label(self.left_panel, text="Processing Facilities", style="Header.TLabel").pack(anchor=tk.W)
        self.fac_frame = ttk.Frame(self.left_panel)
        self.fac_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.admin_fac_widgets = {}
        for f in self.engine.facilities:
            row = ttk.Frame(self.fac_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{f.facility_id} ({f.facility_type})", width=25).pack(side=tk.LEFT)
            pb = ttk.Progressbar(row, orient=tk.HORIZONTAL, length=150, mode='determinate')
            pb.pack(side=tk.LEFT, padx=5)
            val = ttk.Label(row, text="0/0 kg", width=15)
            val.pack(side=tk.LEFT)
            time_lbl = ttk.Label(row, text="Next: 5", width=8)
            time_lbl.pack(side=tk.LEFT)
            ttk.Button(row, text="Empty", width=8, command=lambda fid=f.facility_id: self.admin_empty_fac(fid)).pack(side=tk.LEFT, padx=5)
            self.admin_fac_widgets[f.facility_id] = {"pb": pb, "val": val, "time": time_lbl}

        # Fleet / Logs
        ttk.Label(self.right_panel, text="Fleet Status", style="Header.TLabel").pack(anchor=tk.W)
        cols = ('ID', 'Type', 'Load', 'Status', 'Last Action', 'Target')
        self.tree_veh = ttk.Treeview(self.right_panel, columns=cols, show='headings', height=7)
        for c in cols: 
            self.tree_veh.heading(c, text=c)
            self.tree_veh.column(c, width=100)
        self.tree_veh.pack(fill=tk.X, pady=10)

        ttk.Label(self.right_panel, text="Live Events Log", style="Header.TLabel").pack(anchor=tk.W)
        input_bg = "#3c3f41" if self.is_dark_mode else "#ffffff"
        input_fg = "#ffffff" if self.is_dark_mode else "#000000"
        self.log_text = scrolledtext.ScrolledText(self.right_panel, height=15, width=50, font=("Consolas", 9), bg=input_bg, fg=input_fg, insertbackground=input_fg)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)

        ctrls = ttk.Frame(self.right_panel)
        ctrls.pack(fill=tk.X)
        ttk.Button(ctrls, text="1. Advance Time", command=self.admin_simulate).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(ctrls, text="2. Run Dispatch", command=self.admin_optimize).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(ctrls, text="Reset System", command=self.admin_reset).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.refresh_admin_ui()

    def refresh_admin_ui(self):
        fg_col = "#ffffff" if self.is_dark_mode else "#000000"

        for b in self.engine.bins:
            fill = b.get_fill_percentage()
            w = self.admin_bin_widgets[b.bin_id]
            w["pb"]["value"] = fill
            txt = f"{fill:.1f}% [{b.assigned_vehicle}]" if b.assigned_vehicle else f"{fill:.1f}%"
            w["val"].config(text=txt, foreground='red' if fill >= 90 else 'orange' if fill >= 70 else fg_col)

        for f in self.engine.facilities:
            w = self.admin_fac_widgets[f.facility_id]
            pct = (f.current_load / f.max_daily_capacity * 100) if f.max_daily_capacity > 0 else 0
            w["pb"]["value"] = pct
            w["val"].config(text=f"{f.current_load:.1f}/{f.max_daily_capacity:.1f} kg", foreground=fg_col)
            if f.processing_time_left > 0:
                w["time"].config(text=f"Next: {f.processing_time_left} ticks", foreground=fg_col)
            else:
                status = "READY" if (f.current_load / f.max_daily_capacity) >= f.efficiency_threshold else "WAITING"
                w["time"].config(text=status, foreground='green' if status == "READY" else 'orange')

        for i in self.tree_veh.get_children(): self.tree_veh.delete(i)
        for v in self.engine.vehicles:
            self.tree_veh.insert('', 'end', values=(v.vehicle_id, v.vehicle_type, f"{v.current_load:.1f}kg", 
                                                    "Loaded" if v.current_load > 0 else "Idle",
                                                    getattr(v, 'last_task', 'None'),
                                                    getattr(v, 'last_target', 'N/A')))

    def admin_log(self, msg):
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)

    def admin_simulate(self):
        self.admin_log("\n--- TICK: Adding Waste ---")
        for b in self.engine.bins:
            if random.random() > 0.3:
                amt = round(random.uniform(10.0, 40.0), 2)
                res = self.engine.add_waste(b.bin_id, b.waste_type, amt, user_id="SimUser")
                if res and res.get('success'):
                    self.admin_log(f"  -> Added {amt}kg to {b.bin_id} ({res.get('contamination_detected', 0)*100:.1f}% detection)")
        self.engine.advance_facilities()
        self.refresh_admin_ui()

    def admin_optimize(self):
        sumry = self.engine.run_optimization(alert_threshold=70.0)
        self.admin_log(f"\nEngine: Collected {sumry['bins_collected']}, Unloaded {sumry['vehicles_unloaded']}")
        self.refresh_admin_ui()

    def admin_empty_fac(self, fid):
        f = next((fac for fac in self.engine.facilities if fac.facility_id == fid), None)
        if f: f.empty_facility(); self.admin_log(f"\n[MANUAL] {fid} cleared."); self.refresh_admin_ui()

    def admin_reset(self):
        self.engine.reset_all(); self.admin_log("\n[RESET] Reverted to start."); self.refresh_admin_ui()

    # --- USER MANAGEMENT SECTION ---
    def show_user_management(self):
        win = tk.Toplevel(self)
        win.title("User Management")
        win.geometry("600x450")
        win.configure(bg="#2b2b2b" if self.is_dark_mode else "#f4f4f9")
        win.grab_set()

        head = ttk.Frame(win, padding=10)
        head.pack(fill=tk.X)
        ttk.Label(head, text="System Users", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(head, text="Add New User", command=lambda: self.open_add_user_dialog(win)).pack(side=tk.RIGHT)

        cols = ("Name", "ID", "Role", "Zone", "Violation Score")
        tree = ttk.Treeview(win, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            for i in tree.get_children(): tree.delete(i)
            # Accessing user_manager's internal list
            for u in self.user_manager.users:
                tree.insert('', 'end', values=(u.name, u.user_id, u.role, u.zone, u.violation_score))

        def delete_selected():
            sel = tree.selection()
            if not sel: return
            uid = tree.item(sel[0])['values'][1]
            if str(uid) == self.current_user.user_id:
                messagebox.showerror("Error", "You cannot delete yourself!")
                return
            if messagebox.askyesno("Confirm", f"Delete user {uid}?"):
                if self.user_manager.delete_user(uid):
                    refresh_list()
                    messagebox.showinfo("Success", "User deleted.")

        btn_bar = ttk.Frame(win, padding=10)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Delete Selected", command=delete_selected).pack(side=tk.RIGHT)
        
        win.refresh_ptr = refresh_list # Attach for child dialog
        refresh_list()

    def open_add_user_dialog(self, parent_win):
        dialog = tk.Toplevel(parent_win)
        dialog.title("Add New User")
        dialog.geometry("350x480")
        dialog.configure(bg="#2b2b2b" if self.is_dark_mode else "#f4f4f9")
        dialog.grab_set()

        content = ttk.Frame(dialog, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Full Name:").pack(anchor=tk.W)
        ent_name = ttk.Entry(content, width=30); ent_name.pack(pady=(0, 10))

        ttk.Label(content, text="Login ID:").pack(anchor=tk.W)
        ent_id = ttk.Entry(content, width=30); ent_id.pack(pady=(0, 10))

        ttk.Label(content, text="Password:").pack(anchor=tk.W)
        ent_pwd = ttk.Entry(content, width=30); ent_pwd.pack(pady=(0, 10))

        ttk.Label(content, text="Role:").pack(anchor=tk.W)
        combo_role = ttk.Combobox(content, values=["Admin", "Resident"], state="readonly")
        combo_role.pack(pady=(0, 10)); combo_role.current(1)

        ttk.Label(content, text="Assigned Zone:").pack(anchor=tk.W)
        zones = list(self.input_processor.mappings.get('zone_mappings', {}).keys())
        combo_zone = ttk.Combobox(content, values=zones, state="readonly")
        combo_zone.pack(pady=(0, 10)); combo_zone.current(0)
        
        ttk.Label(content, text="Initial Violation Score:").pack(anchor=tk.W)
        ent_violation = ttk.Entry(content, width=30)
        ent_violation.insert(0, "0")
        ent_violation.pack(pady=(0, 10))

        def save():
            name = ent_name.get().strip()
            uid = ent_id.get().strip()
            pwd = ent_pwd.get().strip()
            role = combo_role.get()
            zone = combo_zone.get()
            try:
                violation = int(ent_violation.get().strip())
                if violation < 0: raise ValueError
            except:
                messagebox.showerror("Error", "Violation Score must be a positive integer.")
                return

            if not name or not uid or not pwd:
                messagebox.showerror("Error", "All fields are required.")
                return

            if self.user_manager.add_user(uid, name, role, zone, password=pwd, violation_score=violation):
                messagebox.showinfo("Success", f"User {uid} created!")
                dialog.destroy()
                parent_win.refresh_ptr()
            else:
                messagebox.showerror("Error", "User ID already exists.")

        ttk.Button(content, text="Create User", command=save, padding=10).pack(pady=10, fill=tk.X)
    #  RESIDENT VIEW
    # -------------------------------------------------------------------------
    def show_resident(self, user):
        self.clear_window()
        self.apply_theme()
        self.title(f"WasteWise Resident - {user.name}")
        self.geometry("600x600")
        self.current_user = user

        # Header
        head = ttk.Frame(self, padding=10)
        head.pack(fill=tk.X)
        ttk.Label(head, text=f"Logged in as: {user.name} (Resident)", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(head, text="Logout", command=self.show_login).pack(side=tk.RIGHT)
        ttk.Button(head, text="Toggle Theme", command=self.toggle_theme).pack(side=tk.RIGHT, padx=5)
        ttk.Label(head, text=f"Zone: {user.zone.capitalize()}", foreground="#666" if not self.is_dark_mode else "#aaa").pack(side=tk.RIGHT, padx=15)

        # Content
        content = ttk.Frame(self, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Your Local Bins", font=("Segoe UI", 12)).pack(anchor=tk.W, pady=(0, 10))
        
        self.res_bin_widgets = {}
        allowed = self.input_processor.get_allowed_bins(user.zone)
        
        for b in self.engine.bins:
            if b.waste_type.lower() in allowed:
                row = ttk.Frame(content)
                row.pack(fill=tk.X, pady=10)
                ttk.Label(row, text=f"{b.waste_type.capitalize()} Bin ({b.bin_id})", width=25).pack(side=tk.LEFT)
                pb = ttk.Progressbar(row, orient=tk.HORIZONTAL, length=200, mode='determinate')
                pb.pack(side=tk.LEFT, padx=10)
                val = ttk.Label(row, text="0.0%", width=8)
                val.pack(side=tk.LEFT)
                self.res_bin_widgets[b.bin_id] = {"pb": pb, "val": val, "obj": b}

        # Dispose Waste Section (Inline)
        dispose_frame = ttk.LabelFrame(content, text="Dispose Waste", padding=15)
        dispose_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(dispose_frame, text="Select Bin:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        bids = list(self.res_bin_widgets.keys())
        combo = ttk.Combobox(dispose_frame, values=bids, state="readonly", width=15)
        combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(dispose_frame, text="Amount (kg):").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        ent = ttk.Entry(dispose_frame, width=15)
        ent.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # Capacity Status Label
        lbl_capacity = ttk.Label(dispose_frame, text="", font=("Segoe UI", 9, "italic"))
        lbl_capacity.grid(row=1, column=0, columnspan=5, padx=10, pady=(10, 0), sticky=tk.W)

        def update_capacity_info(*args):
            bid = combo.get()
            if not bid:
                lbl_capacity.config(text="")
                return
            b_obj = self.res_bin_widgets[bid]["obj"]
            available = b_obj.capacity - b_obj.fill_level
            lbl_capacity.config(
                text=f"Bin Status: {b_obj.fill_level:.1f}kg / {b_obj.capacity:.1f}kg filled ({available:.1f}kg capacity left)"
            )

        combo.bind("<<ComboboxSelected>>", update_capacity_info)

        if bids:
            combo.current(0)
            update_capacity_info()
        
        def commit(event=None):
            bid = combo.get()
            if not bid:
                messagebox.showerror("Error", "No bins available.")
                return
            try:
                amt = float(ent.get())
                if amt <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Enter a valid positive number.")
                return
            
            b_obj = self.res_bin_widgets[bid]["obj"]
            res = self.engine.add_waste(bid, b_obj.waste_type, amt, user_id=self.current_user.user_id)
            
            if res and res.get("success"):
                ent.delete(0, tk.END)
                self.refresh_resident_ui()
                update_capacity_info()
                det = res.get('contamination_detected', 0) * 100
                messagebox.showinfo("Success", f"Waste added! Smart sensor detected {det:.1f}% contamination.")
            else:
                messagebox.showerror("Full", "Cannot add waste. Bin might be full.")

        ent.bind("<Return>", commit)
        ttk.Button(dispose_frame, text="Submit", command=commit).grid(row=0, column=4, padx=20, pady=5)

        self.refresh_resident_ui()

    def refresh_resident_ui(self):
        for bid, w in self.res_bin_widgets.items():
            b = w["obj"]
            fill = b.get_fill_percentage()
            w["pb"]["value"] = fill
            w["val"].config(text=f"{fill:.1f}%")

if __name__ == "__main__":
    app = WasteWiseApp()
    app.mainloop()
