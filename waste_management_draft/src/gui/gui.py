# src/gui/gui.py
# Module: GUI Subsystem Main Application
# Fully integrates the original Live Monitoring system (with Bins, Facilities, Empty Buttons, 
# Fleet Treeview, and Event logs) with the new Analytics Dashboard as a tabbed environment.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import sys
import os

# Add parent path to resolve module imports cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.data_loader import load_all
from simulation.engine import SimulationEngine
from auth.user_manager import UserManager
from simulation.input_processor import InputProcessor
from auth import auth
from analytics.dashboard import AnalyticsDashboard
from utils import constants, logger

class WasteWiseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WasteWise - Integrated Urban Waste Collection & Analytics")
        self.geometry("1200x850")
        self.maximize_window()
        self.is_dark_mode = False
        
        # Reset all persistent logs on terminal execution
        logger.reset_all_logs()
        
        # Shared Managers
        self.user_manager = UserManager()
        self.input_processor = InputProcessor()
        
        # Load Simulation Core
        bins, vehicles, facilities, graph = load_all()
        self.engine = SimulationEngine(bins, vehicles, facilities, graph)
        self.engine.reset_all()

        # Connect Analytics Dashboard Engine
        self.dashboard = AnalyticsDashboard(self.engine, self)

        # Style Configuration
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        self.apply_theme()

        # Emergency Flashing Background Loop Initializer
        self.flash_toggle = False
        self.schedule_flash()

        # Transition to Login Screen
        self.show_login()

    def maximize_window(self):
        """Maximizes the application window to fill the entire screen dynamically."""
        try:
            self.attributes("-zoomed", True)
        except Exception:
            try:
                self.state("zoomed")
            except Exception:
                self.geometry("1600x950")

    def toggle_theme(self):
        """Switches between dark mode and light mode aesthetics."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Trigger dashboard refresh to update Matplotlib background styles instantly
        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            self.refresh_dashboard()

    def apply_theme(self):
        """Applies dynamic layout themes for all widgets in the platform."""
        bg_color = constants.DARK_MODE_BG if self.is_dark_mode else constants.LIGHT_MODE_BG
        fg_color = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG
        input_bg = constants.DARK_MODE_INPUT if self.is_dark_mode else constants.LIGHT_MODE_INPUT
        input_fg = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG

        self.configure(bg=bg_color)
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 12, "bold"))
        self.style.configure("Title.TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 18, "bold"))
        
        # Notebook (Tabs) styling
        self.style.configure("TNotebook", background=bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=input_bg, foreground=fg_color, padding=[12, 6], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", bg_color)], foreground=[("selected", fg_color)])
        
        # Treeview styling (Set rowheight=32 to prevent half-visible rows on Fedora Linux/DPI scales!)
        self.style.configure("Treeview", background=input_bg, foreground=input_fg, fieldbackground=input_bg, rowheight=32, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background=bg_color, foreground=fg_color, font=("Segoe UI", 10, "bold"))
        self.style.configure("TButton", foreground=fg_color, background=input_bg, font=("Segoe UI", 10, "bold"))
        
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.log_text.configure(bg=input_bg, fg=input_fg, insertbackground=input_fg)
            
        if hasattr(self, 'current_user') and self.current_user:
            if self.current_user.role.lower() == 'admin':
                if hasattr(self, 'notebook') and self.notebook.winfo_exists():
                    self.refresh_dashboard()
                if hasattr(self, 'admin_bin_widgets'):
                    self.refresh_admin_ui()
            else:
                if hasattr(self, 'res_bin_widgets'):
                    self.refresh_resident_ui()

    def clear_window(self):
        """Cleans all widgets in current window."""
        for widget in self.winfo_children():
            widget.destroy()
        if hasattr(self, 'admin_bin_widgets'):
            del self.admin_bin_widgets
        if hasattr(self, 'res_bin_widgets'):
            del self.res_bin_widgets
        if hasattr(self, 'admin_fac_widgets'):
            del self.admin_fac_widgets

    def schedule_flash(self):
        """Periodically flashes critical emergency labels in red foreground."""
        self.flash_toggle = not getattr(self, 'flash_toggle', False)
        
        # Admin emergency labels flashing logic
        if hasattr(self, 'admin_bin_widgets'):
            for b in self.engine.bins:
                if getattr(b, 'is_emergency', False):
                    w = self.admin_bin_widgets.get(b.bin_id)
                    if w:
                        color = "red" if self.flash_toggle else "#ff6666"
                        w["val"].config(foreground=color)
        
        # Resident emergency labels flashing logic
        if hasattr(self, 'res_bin_widgets'):
            for b_id, w in self.res_bin_widgets.items():
                b = w.get("obj")
                if b and getattr(b, 'is_emergency', False):
                    color = "red" if self.flash_toggle else "#ff6666"
                    w["val"].config(foreground=color)
                    
        self.after(500, self.schedule_flash)

    def show_login(self):
        """Renders standard credentials gate login window."""
        self.current_user = None
        self.clear_window()
        self.apply_theme()
        self.title("WasteWise - System Sign In")
        self.geometry("400x380")
        self.maximize_window()
        
        theme_btn = ttk.Button(self, text="Toggle Theme", command=self.toggle_theme)
        theme_btn.place(relx=0.95, rely=0.05, anchor=tk.NE)
        
        frame = ttk.Frame(self, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(frame, text="WasteWise Sign In", style="Title.TLabel").pack(pady=(0, 20))
        
        ttk.Label(frame, text="User ID:").pack(anchor=tk.W)
        ent_id = ttk.Entry(frame, width=30)
        ent_id.pack(pady=(5, 10))
        ent_id.focus_set()
        
        ttk.Label(frame, text="Password:").pack(anchor=tk.W)
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
        ttk.Button(frame, text="Log In", command=do_login).pack(fill=tk.X, pady=(10, 0))

    # -------------------------------------------------------------------------
    #  ADMIN ANALYTICS DASHBOARD VIEW WITH INTEGRATED LIVE MONITORING
    # -------------------------------------------------------------------------
    def show_admin(self, user):
        """Renders full tabbed operational analytics dashboard for admins."""
        self.clear_window()
        self.apply_theme()
        self.title(f"WasteWise Admin Control Panel - {user.name}")
        self.geometry("1200x850")
        self.maximize_window()
        self.current_user = user

        # 1. Top Header Frame
        head = ttk.Frame(self, padding=5)
        head.pack(fill=tk.X)
        ttk.Button(head, text="Logout", command=self.show_login).pack(side=tk.RIGHT, padx=10)
        ttk.Button(head, text="Theme Mode", command=self.toggle_theme).pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(head, text=f"Admin Panel: {user.name}", style="Header.TLabel").pack(side=tk.LEFT, padx=15)

        # Create Tabbed Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Live Monitoring (100% Original Fully-Integrated View)
        self.tab_monitor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_monitor, text="Live Monitoring")

        # Tabs 2-4: Dynamic Operations, Facilities, and Residents Dashboards (Omitted Routing and Emergencies tabs!)
        self.tab_ops = ttk.Frame(self.notebook)
        self.tab_fac = ttk.Frame(self.notebook)
        self.tab_res = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_ops, text="Operations Tab")
        self.notebook.add(self.tab_fac, text="Facilities Tab")
        self.notebook.add(self.tab_res, text="Residents Tab")

        # -------------------------------------------------------------------------
        #  BUILD LIVE MONITORING TAB LAYOUT (Matches original double-panel layout)
        # -------------------------------------------------------------------------
        left_panel = ttk.Frame(self.tab_monitor, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_panel = ttk.Frame(self.tab_monitor, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Side - Emergency Notification Alerts
        self.alerts_frame = ttk.LabelFrame(left_panel, text="Critical System Notifications", padding=10)
        self.alerts_frame.pack(fill=tk.X, pady=(0, 10))
        self.alerts_label = ttk.Label(self.alerts_frame, text="System Healthy. No active emergencies.", foreground="green", font=("Segoe UI", 10, "bold"))
        self.alerts_label.pack(fill=tk.X, padx=10, pady=2)

        # Left Side - City Bins Progress
        ttk.Label(left_panel, text="City Waste Bins", style="Header.TLabel").pack(anchor=tk.W)
        self.bins_frame = ttk.Frame(left_panel)
        self.bins_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.admin_bin_widgets = {}
        for b in self.engine.bins:
            row = ttk.Frame(self.bins_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{b.bin_id} ({b.waste_type})", width=25).pack(side=tk.LEFT)
            pb = ttk.Progressbar(row, orient=tk.HORIZONTAL, length=180, mode='determinate')
            pb.pack(side=tk.LEFT, padx=10)
            val = ttk.Label(row, text="0.0%", width=28)
            val.pack(side=tk.LEFT)
            self.admin_bin_widgets[b.bin_id] = {"pb": pb, "val": val}

        # Left Side - Processing Facilities Progress
        ttk.Label(left_panel, text="Processing Facilities", style="Header.TLabel").pack(anchor=tk.W)
        self.fac_frame = ttk.Frame(left_panel)
        self.fac_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.admin_fac_widgets = {}
        for f in self.engine.facilities:
            row = ttk.Frame(self.fac_frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{f.facility_id} ({f.facility_type})", width=25).pack(side=tk.LEFT)
            pb = ttk.Progressbar(row, orient=tk.HORIZONTAL, length=130, mode='determinate')
            pb.pack(side=tk.LEFT, padx=5)
            val = ttk.Label(row, text="0/0 kg", width=15)
            val.pack(side=tk.LEFT)
            time_lbl = ttk.Label(row, text="Next: 5", width=8)
            time_lbl.pack(side=tk.LEFT)
            
            # The essential Empty Facility button
            ttk.Button(row, text="Empty", width=8, command=lambda fid=f.facility_id: self.admin_empty_fac(fid)).pack(side=tk.LEFT, padx=5)
            self.admin_fac_widgets[f.facility_id] = {"pb": pb, "val": val, "time": time_lbl}

        # Right Side - Fleet Status List
        ttk.Label(right_panel, text="Fleet Logistics Status", style="Header.TLabel").pack(anchor=tk.W)
        cols = ('ID', 'Type', 'Load', 'Status', 'Last Action', 'Route', 'Distance', 'Bins Coll.')
        self.tree_veh = ttk.Treeview(right_panel, columns=cols, show='headings', height=7)
        for c in cols: 
            self.tree_veh.heading(c, text=c)
            if c == 'Route':
                self.tree_veh.column(c, width=130)
            elif c in ('Type', 'Last Action'):
                self.tree_veh.column(c, width=90)
            else:
                self.tree_veh.column(c, width=65)
        self.tree_veh.pack(fill=tk.X, pady=5)
        self.tree_veh.bind("<<TreeviewSelect>>", self.on_vehicle_click)

        # Right Side - Scrolling Live Events Log
        ttk.Label(right_panel, text="Live Events Stream Log", style="Header.TLabel").pack(anchor=tk.W, pady=(5, 0))
        card_bg = constants.DARK_MODE_INPUT if self.is_dark_mode else constants.LIGHT_MODE_INPUT
        fg_color = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG
        self.log_text = scrolledtext.ScrolledText(right_panel, height=14, font=("Consolas", 9), bg=card_bg, fg=fg_color, insertbackground=fg_color)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Right Side - Action Controls Frame
        ctrls = ttk.Frame(right_panel)
        ctrls.pack(fill=tk.X, pady=5)
        ttk.Button(ctrls, text="1. Advance Time", command=self.admin_simulate).pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
        ttk.Button(ctrls, text="2. Run Dispatch", command=self.admin_optimize).pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
        ttk.Button(ctrls, text="Reset System", command=self.admin_reset).pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)

        # Bind notebook tab switches to dynamically redraw analytics
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Startup Trigger
        self.admin_log("[SYSTEM] Live Monitoring Subsystem initialized. Connected to city grid.")
        self.refresh_admin_ui()

    def on_tab_changed(self, event=None):
        """Triggers dynamic render of the active tab on selection."""
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Redraws the active tab inside the dashboard notebook."""
        if not hasattr(self, 'notebook') or not self.notebook.winfo_exists():
            return
            
        # Get active tab index
        idx = self.notebook.index(self.notebook.select())
        
        # Render if it is an analytics tab
        if idx == 1:
            self.dashboard.render_operations_tab(self.tab_ops)
        elif idx == 2:
            self.dashboard.render_facilities_tab(self.tab_fac)
        elif idx == 3:
            self.dashboard.render_residents_tab(self.tab_res)

    def refresh_admin_ui(self):
        """Updates the Live Monitoring progress bars, labels, and vehicles tree in real time."""
        fg_col = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG

        # Update Emergency Alerts Panel
        emergencies = [b for b in self.engine.bins if getattr(b, 'is_emergency', False)]
        if hasattr(self, 'alerts_label'):
            if emergencies:
                alert_text = "\n".join([f"EMERGENCY: {eb.emergency_reason} at Bin {eb.bin_id}" for eb in emergencies])
                self.alerts_label.config(text=alert_text, foreground="red")
            else:
                self.alerts_label.config(text="System Healthy. No active emergencies.", foreground="green")

        # Update Waste Bins Progress
        if hasattr(self, 'admin_bin_widgets'):
            for b in self.engine.bins:
                w = self.admin_bin_widgets.get(b.bin_id)
                if w:
                    fill = b.get_fill_percentage()
                    w["pb"]["value"] = fill
                    
                    if getattr(b, 'is_emergency', False):
                        txt = f"{fill:.1f}% (C: {(b.contamination_level * 100):.1f}%) [EMERGENCY]"
                        color = "red"
                    else:
                        c_rate = getattr(b, 'contamination_level', 0.0) * 100
                        txt = f"{fill:.1f}% (C: {c_rate:.1f}%) [{b.assigned_vehicle}]" if b.assigned_vehicle else f"{fill:.1f}% (C: {c_rate:.1f}%)"
                        color = 'red' if fill >= 90 else 'orange' if fill >= 70 else fg_col
                        
                    w["val"].config(text=txt, foreground=color)

        # Update Processing Facilities Progress
        if hasattr(self, 'admin_fac_widgets'):
            for f in self.engine.facilities:
                w = self.admin_fac_widgets.get(f.facility_id)
                if w:
                    pct = (f.current_load / f.max_daily_capacity * 100) if f.max_daily_capacity > 0 else 0
                    w["pb"]["value"] = pct
                    
                    # Highlight if inactive due to emissions failover or manual shutdown
                    if not f.is_active:
                        if f.emissions >= f.emission_limit:
                            w["val"].config(text=f"{f.current_load:.1f}/{f.max_daily_capacity:.1f} kg (SUSPENDED)", foreground="red")
                            w["time"].config(text="FAILOVER", foreground="red")
                        else:
                            w["val"].config(text=f"{f.current_load:.1f}/{f.max_daily_capacity:.1f} kg (STOPPED)", foreground="orange")
                            w["time"].config(text="MANUAL", foreground="orange")
                    else:
                        w["val"].config(text=f"{f.current_load:.1f}/{f.max_daily_capacity:.1f} kg", foreground=fg_col)
                        if f.processing_time_left > 0:
                            w["time"].config(text=f"Next: {f.processing_time_left} ticks", foreground=fg_col)
                        else:
                            status = "READY" if (f.current_load / f.max_daily_capacity) >= f.efficiency_threshold else "WAITING"
                            w["time"].config(text=status, foreground='green' if status == "READY" else 'orange')

        # Update Vehicles Treeview
        if hasattr(self, 'tree_veh'):
            for i in self.tree_veh.get_children(): 
                self.tree_veh.delete(i)
            for v in self.engine.vehicles:
                route_str = " -> ".join(getattr(v, 'current_route', [])) if getattr(v, 'current_route', []) else "N/A"
                self.tree_veh.insert('', 'end', values=(
                    v.vehicle_id, 
                    v.vehicle_type, 
                    f"{v.current_load:.1f}kg", 
                    "Loaded" if v.current_load > 0 else "Idle",
                    getattr(v, 'last_task', 'None'),
                    route_str,
                    f"{getattr(v, 'total_distance_travelled', 0.0):.1f} km",
                    getattr(v, 'bins_collected_count', 0)
                ))

    def admin_log(self, msg):
        """Appends a new line of text to the scrolling Live event logger."""
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)

    def on_vehicle_click(self, event=None):
        """Listens for vehicle selection in the tree, resolving details in a popup."""
        selected = self.tree_veh.selection()
        if not selected:
            return
            
        item = self.tree_veh.item(selected[0])
        if not item or not item.get('values'):
            return
            
        veh_id = item['values'][0]
        vehicle = next((v for v in self.engine.vehicles if v.vehicle_id == veh_id), None)
        
        if vehicle:
            self.show_vehicle_details_popup(vehicle)

    def show_vehicle_details_popup(self, vehicle):
        """Renders premium popup card presenting total metrics of selected truck."""
        if hasattr(self, 'details_popup') and self.details_popup.winfo_exists():
            self.details_popup.destroy()
            
        popup = tk.Toplevel(self)
        popup.title(f"Vehicle Fleet Status - {vehicle.vehicle_id}")
        popup.geometry("520x680")
        popup.resizable(False, False)
        self.details_popup = popup
        
        bg_col = constants.DARK_MODE_BG if self.is_dark_mode else constants.LIGHT_MODE_BG
        fg_col = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG
        card_bg = constants.DARK_MODE_INPUT if self.is_dark_mode else constants.LIGHT_MODE_INPUT
        popup.configure(bg=bg_col)
        
        # Title
        title_frame = tk.Frame(popup, bg=bg_col, pady=12)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text=f"FLEET DETAIL: {vehicle.vehicle_id}", 
                 font=("Segoe UI", 14, "bold"), fg=fg_col, bg=bg_col).pack()
        
        # Core Info Box
        info_frame = tk.LabelFrame(popup, text="Core Specifications", font=("Segoe UI", 10, "bold"),
                                   bg=card_bg, fg=fg_col, bd=1, relief=tk.SOLID, padx=15, pady=8)
        info_frame.pack(fill=tk.X, padx=20, pady=8)
        
        def add_info_row(parent, label, val):
            row = tk.Frame(parent, bg=card_bg)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"), fg=fg_col, bg=card_bg, width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=val, font=("Segoe UI", 10), fg=fg_col, bg=card_bg, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        add_info_row(info_frame, "Vehicle Type:", vehicle.vehicle_type)
        add_info_row(info_frame, "Capacity Limit:", f"{vehicle.total_capacity:.1f} kg")
        pct = (vehicle.current_load / vehicle.total_capacity * 100) if vehicle.total_capacity > 0 else 0
        add_info_row(info_frame, "Current Load:", f"{vehicle.current_load:.1f} kg ({pct:.1f}%)")
        add_info_row(info_frame, "Status:", "Loaded & Routing" if vehicle.current_load > 0 else "Idle / Available")
        
        # Stats Box
        stats_frame = tk.LabelFrame(popup, text="Operational Statistics", font=("Segoe UI", 10, "bold"),
                                    bg=card_bg, fg=fg_col, bd=1, relief=tk.SOLID, padx=15, pady=8)
        stats_frame.pack(fill=tk.X, padx=20, pady=8)
        
        add_info_row(stats_frame, "Total Distance:", f"{getattr(vehicle, 'total_distance_travelled', 0.0):.2f} km")
        add_info_row(stats_frame, "Bins Collected (All):", f"{getattr(vehicle, 'bins_collected_count', 0)} bins")
        
        bins_this_trip = getattr(vehicle, 'last_target', 'N/A')
        if bins_this_trip == "N/A" or not bins_this_trip:
            bins_this_trip = "None"
        add_info_row(stats_frame, "Bins This Loop:", bins_this_trip)
        
        # Route Path Box
        route_path = getattr(vehicle, 'current_route', [])
        route_str = " -> ".join(route_path) if route_path else "N/A (No active loop)"
        
        route_frame = tk.LabelFrame(popup, text="Active Route Path", font=("Segoe UI", 10, "bold"),
                                    bg=card_bg, fg=fg_col, bd=1, relief=tk.SOLID, padx=15, pady=8)
        route_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        route_label = tk.Label(route_frame, text=route_str, font=("Consolas", 10, "bold"), 
                               fg="#ff9900" if self.is_dark_mode else "#d97706", bg=card_bg, wraplength=420, justify="left")
        route_label.pack(fill=tk.BOTH, expand=True)
        
        btn_close = ttk.Button(popup, text="Close Details", command=popup.destroy)
        btn_close.pack(pady=(5, 12))

    def admin_empty_fac(self, fid):
        """Manually empties facility load and restores processing ticks."""
        facility = next((f for f in self.engine.facilities if f.facility_id == fid), None)
        if facility:
            facility.empty_facility()
            self.admin_log(f"Facility {fid} manually emptied and cleared.")
            self.refresh_admin_ui()

    def admin_simulate(self):
        """Ticks simulation time, adding random trash into random city bins."""
        self.admin_log("\n--- TICK: Advancing Time / City Bins Filling ---")
        
        # Sample items for each canonical category to simulate realistic inputs
        items_map = {
            'biodegradable': ['food waste', 'vegetable peels', 'fruit scraps', 'leaves', 'leftovers', 'organic'],
            'recyclable': ['plastics', 'paper', 'glass bottle', 'cardboard', 'metal cans', 'plastic bottle'],
            'hazardous': ['syringes', 'bandages', 'expired medicine', 'chemicals', 'needles'],
            'e_waste': ['electronics', 'displays', 'batteries', 'motherboards', 'cables', 'monitors', 'phones']
        }
        
        for b in self.engine.bins:
            if random.random() > 0.3:
                amt = round(random.uniform(10.0, 40.0), 2)
                
                # Determine category of waste to dispose
                bin_cat = b.waste_type.lower()  # which is already resolved in lower-case
                
                # 80% chance of correct waste category, 20% chance of incorrect (contamination)
                if random.random() < 0.8:
                    disposed_cat = bin_cat
                else:
                    # Pick a different category
                    other_cats = [c for c in items_map.keys() if c != bin_cat]
                    disposed_cat = random.choice(other_cats) if other_cats else bin_cat
                
                # Pick a specific item from that category to simulate realistic resident input
                if disposed_cat in items_map:
                    disposed_item = random.choice(items_map[disposed_cat])
                else:
                    disposed_item = b.waste_type
                
                res = self.engine.add_waste(b.bin_id, disposed_item, amt, user_id="SimUser")
                if res and res.get('success'):
                    # Show contamination percentage
                    contam_pct = res.get('contamination_detected', 0.0) * 100
                    self.admin_log(
                        f"  -> Added {amt}kg of '{disposed_item}' (resolved: {disposed_cat}) to {b.bin_id}. "
                        f"Sensor: {contam_pct:.1f}% contamination."
                    )
                    
                    b_obj = self.engine.monitor.find_bin(b.bin_id)
                    if b_obj and getattr(b_obj, 'is_emergency', False):
                        self.admin_log(f"[EMERGENCY ACTIVE] Bin {b.bin_id} emergency triggered! Reason: {b_obj.emergency_reason}")

        self.engine.advance_facilities()
        self.refresh_admin_ui()

    def admin_optimize(self):
        """Invokes optimization and multi-bin routing cycle dispatches."""
        self.admin_log("\n--- DISPATCH ENGINE ACTIVATED ---")
        
        # Hook facility failover warning logging before running optimization
        for f in self.engine.facilities:
            if not f.is_active:
                self.admin_log(f"[ALERT] Facility {f.facility_id} inactive due to high emissions or manual stop! Failover active.")

        sumry = self.engine.run_optimization(alert_threshold=70.0)
        self.admin_log(f"SUCCESS: Collected {sumry['bins_collected']} Bins, Unloaded {sumry['vehicles_unloaded']} Vehicles.")
        
        # Log completed routes in live list
        for v in self.engine.vehicles:
            if getattr(v, 'current_route', []):
                self.admin_log(f"Route completed: {v.vehicle_id} collected Bins: {getattr(v, 'last_target', 'N/A')}")
                
        self.refresh_admin_ui()

    def admin_reset(self):
        """Clears simulation statuses back to zero."""
        self.engine.reset_all()
        self.admin_log("\n[SYSTEM RESET] Simulation entities restored to default.")
        self.refresh_admin_ui()

    # -------------------------------------------------------------------------
    #  INLINE USER MANAGEMENT DIALOGS (Consolidated into Residents Tab)
    # -------------------------------------------------------------------------
    def open_add_user_dialog(self, parent_win):
        """Displays dialog card adding a new user into CSV records."""
        dialog = tk.Toplevel(parent_win)
        dialog.title("Register New Account")
        dialog.geometry("380x640")
        dialog.configure(bg=constants.DARK_MODE_BG if self.is_dark_mode else constants.LIGHT_MODE_BG)
        dialog.grab_set()

        content = ttk.Frame(dialog, padding=15)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Full Name:").pack(anchor=tk.W)
        ent_name = ttk.Entry(content, width=30); ent_name.pack(pady=(0, 5))

        ttk.Label(content, text="Login ID:").pack(anchor=tk.W)
        ent_id = ttk.Entry(content, width=30); ent_id.pack(pady=(0, 5))

        ttk.Label(content, text="Password:").pack(anchor=tk.W)
        ent_pwd = ttk.Entry(content, width=30); ent_pwd.pack(pady=(0, 5))

        ttk.Label(content, text="Role:").pack(anchor=tk.W)
        combo_role = ttk.Combobox(content, values=["Admin", "Resident"], state="readonly")
        combo_role.pack(pady=(0, 5)); combo_role.current(1)

        ttk.Label(content, text="Assigned Zone:").pack(anchor=tk.W)
        zones = list(self.input_processor.mappings.get('zone_mappings', {}).keys())
        combo_zone = ttk.Combobox(content, values=zones, state="readonly")
        combo_zone.pack(pady=(0, 5)); combo_zone.current(0)
        
        ttk.Label(content, text="Initial Penalty Balance (₹):").pack(anchor=tk.W)
        ent_violation = ttk.Entry(content, width=30)
        ent_violation.insert(0, "0")
        ent_violation.pack(pady=(0, 5))

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
                dialog.destroy()
                parent_win.refresh_ptr()  # Refresh Treeview inside Residents tab!
            else:
                messagebox.showerror("Error", "User ID already exists.")

        ttk.Button(content, text="Create Account", command=save, padding=10).pack(pady=15, fill=tk.X)

    def open_edit_user_dialog(self, parent_win, selected_item):
        """Displays dialog card to edit an existing user account profile."""
        tree = selected_item["tree"]
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select a user to edit.")
            return
            
        values = tree.item(sel[0])['values']
        name_val = values[0]
        uid_val = values[1]
        role_val = values[2]
        zone_val = values[3]
        violation_val = values[4]
        
        # Fetch actual account password from manager database
        user_obj = self.user_manager.search_user(uid_val)
        pwd_val = user_obj.password if user_obj else ""

        dialog = tk.Toplevel(parent_win)
        dialog.title(f"Edit Account - {uid_val}")
        dialog.geometry("380x640")
        dialog.configure(bg=constants.DARK_MODE_BG if self.is_dark_mode else constants.LIGHT_MODE_BG)
        dialog.grab_set()

        content = ttk.Frame(dialog, padding=15)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text=f"Editing User ID: {uid_val}", font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))

        ttk.Label(content, text="Full Name:").pack(anchor=tk.W)
        ent_name = ttk.Entry(content, width=30)
        ent_name.insert(0, name_val)
        ent_name.pack(pady=(0, 5))

        ttk.Label(content, text="Password:").pack(anchor=tk.W)
        ent_pwd = ttk.Entry(content, width=30)
        ent_pwd.insert(0, pwd_val)
        ent_pwd.pack(pady=(0, 5))

        ttk.Label(content, text="Role:").pack(anchor=tk.W)
        combo_role = ttk.Combobox(content, values=["Admin", "Resident"], state="readonly")
        combo_role.pack(pady=(0, 5))
        combo_role.set(role_val)

        ttk.Label(content, text="Assigned Zone:").pack(anchor=tk.W)
        zones = list(self.input_processor.mappings.get('zone_mappings', {}).keys())
        combo_zone = ttk.Combobox(content, values=zones, state="readonly")
        combo_zone.pack(pady=(0, 5))
        combo_zone.set(zone_val)
        
        ttk.Label(content, text="Penalty Balance (₹):").pack(anchor=tk.W)
        ent_violation = ttk.Entry(content, width=30)
        ent_violation.insert(0, str(violation_val))
        ent_violation.pack(pady=(0, 5))

        def save():
            name = ent_name.get().strip()
            pwd = ent_pwd.get().strip()
            role = combo_role.get()
            zone = combo_zone.get()
            try:
                violation = int(ent_violation.get().strip())
                if violation < 0: raise ValueError
            except:
                messagebox.showerror("Error", "Violation Score must be a positive integer.")
                return

            if not name or not pwd:
                messagebox.showerror("Error", "Name and Password are required.")
                return

            if self.user_manager.update_user(uid_val, name, role, zone, password=pwd, violation_score=violation):
                dialog.destroy()
                parent_win.refresh_ptr()  # Refresh Treeview inside Residents tab!
            else:
                messagebox.showerror("Error", "Failed to update user.")

        ttk.Button(content, text="Apply Changes", command=save, padding=10).pack(pady=15, fill=tk.X)

    # -------------------------------------------------------------------------
    #  RESIDENT VIEW
    # -------------------------------------------------------------------------
    def show_resident(self, user):
        """Renders direct disposal interface for city residents."""
        self.clear_window()
        self.apply_theme()
        self.title(f"WasteWise Resident Disposal - {user.name}")
        self.geometry("600x600")
        self.maximize_window()
        self.current_user = user

        # Header
        head = ttk.Frame(self, padding=10)
        head.pack(fill=tk.X)
        ttk.Label(head, text=f"Logged in as: {user.name} (Resident)", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(head, text="Logout", command=self.show_login).pack(side=tk.RIGHT)
        ttk.Button(head, text="Mode", command=self.toggle_theme).pack(side=tk.RIGHT, padx=5)
        ttk.Label(head, text=f"Zone: {user.zone.capitalize()}", foreground="#aaa").pack(side=tk.RIGHT, padx=15)
        self.lbl_penalty = ttk.Label(head, text=f"Accumulated Penalty: ₹{float(user.violation_score):.2f}", foreground="red", font=("Segoe UI", 10, "bold"))
        self.lbl_penalty.pack(side=tk.RIGHT, padx=15)

        # Content Frame
        content = ttk.Frame(self, padding=20)
        content.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content, text="Your Assigned Zone Disposal Bins", font=("Segoe UI", 12)).pack(anchor=tk.W, pady=(0, 10))
        
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

        # Extract preset items for autocomplete/selection
        preset_items = []
        valid_items_dict = self.input_processor.mappings.get('valid_items', {})
        for cat, items in valid_items_dict.items():
            preset_items.extend(items)
        preset_items.extend(['biodegradable', 'recyclable', 'hazardous', 'e-waste'])
        preset_items = list(dict.fromkeys(preset_items))

        # Disposal Card
        dispose_frame = ttk.LabelFrame(content, text="Dispose Materials Safely", padding=15)
        dispose_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(dispose_frame, text="Select Bin:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        bids = list(self.res_bin_widgets.keys())
        combo = ttk.Combobox(dispose_frame, values=bids, state="readonly", width=15)
        combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(dispose_frame, text="Waste Type:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        combo_waste_type = ttk.Combobox(dispose_frame, values=preset_items, width=15)
        combo_waste_type.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        if preset_items:
            combo_waste_type.current(0)
        
        ttk.Label(dispose_frame, text="Quantity (kg):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        ent = ttk.Entry(dispose_frame, width=15)
        ent.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Capacity Status Label
        lbl_capacity = ttk.Label(dispose_frame, text="", font=("Segoe UI", 9, "italic"))
        lbl_capacity.grid(row=2, column=0, columnspan=5, padx=10, pady=(10, 0), sticky=tk.W)

        def update_capacity_info(*args):
            bid = combo.get()
            if not bid:
                lbl_capacity.config(text="")
                return
            b_obj = self.res_bin_widgets[bid]["obj"]
            available = b_obj.capacity - b_obj.fill_level
            lbl_capacity.config(
                text=(
                    f"Bin Status: {b_obj.fill_level:.1f}kg / {b_obj.capacity:.1f}kg filled ({available:.1f}kg capacity left)\n"
                    f"Correct Weight: {(b_obj.fill_level * (1 - getattr(b_obj, 'contamination_level', 0.0))):.1f} kg | "
                    f"Contaminated Weight: {(b_obj.fill_level * getattr(b_obj, 'contamination_level', 0.0)):.1f} kg | "
                    f"Contamination Rate: {(getattr(b_obj, 'contamination_level', 0.0) * 100):.1f}%"
                )
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
            w_type = combo_waste_type.get().strip()
            if not w_type:
                messagebox.showerror("Error", "Please enter/select a waste type.")
                return
            try:
                amt = float(ent.get())
                if amt <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Enter a valid positive number.")
                return
            
            b_obj = self.res_bin_widgets[bid]["obj"]
            res = self.engine.add_waste(bid, w_type, amt, user_id=self.current_user.user_id)
            
            if res and res.get("success"):
                ent.delete(0, tk.END)
                self.refresh_resident_ui()
                update_capacity_info()
                det = res.get('total_contamination', 0) * 100
                penalty = float(res.get('penalty', 0.0))
                
                if penalty > 0:
                    self.current_user.violation_score += penalty
                    self.user_manager.update_user(
                        self.current_user.user_id, self.current_user.name, 
                        self.current_user.role, self.current_user.zone, 
                        self.current_user.password, self.current_user.violation_score
                    )
                    if hasattr(self, 'lbl_penalty'):
                        self.lbl_penalty.config(text=f"Accumulated Penalty: ₹{float(self.current_user.violation_score):.2f}")
                        
                    messagebox.showwarning("Penalty Issued", f"Waste successfully disposed, but {det:.1f}% contamination was detected.\nYou have been penalized ₹{penalty:.2f}.")
                else:
                    messagebox.showinfo("Success", f"Waste successfully disposed! Automated smart sensor registered {det:.1f}% contamination.")
            else:
                reason = res.get("reason", "unknown") if res else "unknown"
                msg = res.get("message", "Cannot accept additional waste weight. Bin is currently full!") if res else "An unknown error occurred."
                if reason == "overflow":
                    messagebox.showerror("Bin Full", msg)
                else:
                    messagebox.showerror("Validation Error", msg)

        ent.bind("<Return>", commit)
        ttk.Button(dispose_frame, text="Dispose Weight", command=commit).grid(row=1, column=3, padx=20, pady=5)

        self.refresh_resident_ui()

    def refresh_resident_ui(self):
        """Redraws resident progress metrics in real-time."""
        fg_col = constants.DARK_MODE_FG if self.is_dark_mode else constants.LIGHT_MODE_FG
        for bid, w in self.res_bin_widgets.items():
            b = w["obj"]
            fill = b.get_fill_percentage()
            w["pb"]["value"] = fill
            
            if getattr(b, 'is_emergency', False):
                w["val"].config(text=f"{fill:.1f}% EMERGENCY", foreground="red")
            else:
                w["val"].config(text=f"{fill:.1f}%", foreground=fg_col)

def main():
    app = WasteWiseApp()
    app.mainloop()

if __name__ == "__main__":
    main()
