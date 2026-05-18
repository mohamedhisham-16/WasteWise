# src/analytics/dashboard.py
# Module: Analytics Dashboard
# Computes metrics and renders the Tkinter/Matplotlib operational dashboards.

import os
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from utils import csv_utils, logger, constants
from auth import user_manager

class AnalyticsDashboard:
    """Computes all historical and live analytics, and manages visual rendering inside tkinter."""
    
    def __init__(self, engine, app_instance):
        self.engine = engine
        self.app = app_instance  # Reference to main gui app for styling and theme settings

    def get_operations_metrics(self):
        """Calculates central operations stats."""
        # Read from route logs
        routes = csv_utils.read_csv(logger.ROUTE_LOG, as_dict=True)
        total_waste = 0.0
        bins_serviced = 0
        
        for r in routes:
            try:
                total_waste += float(r.get("waste_collected_kg", 0.0))
                bins_str = r.get("bins_collected", "")
                if bins_str and bins_str != "N/A":
                    bins_serviced += len([b.strip() for b in bins_str.split(",") if b.strip()])
            except (ValueError, TypeError):
                pass
                
        active_vehicles = sum(1 for v in self.engine.vehicles if v.total_distance_travelled > 0 or not v.is_available)
        active_facilities = sum(1 for f in self.engine.facilities if f.is_active)
        current_emergencies = sum(1 for b in self.engine.bins if getattr(b, 'is_emergency', False))
        
        return {
            "total_waste_collected_kg": round(total_waste, 1),
            "total_bins_serviced": bins_serviced,
            "active_vehicles": active_vehicles,
            "total_facilities_active": active_facilities,
            "current_emergencies": current_emergencies
        }

    def get_facility_metrics(self):
        """Calculates facility and failover specific metrics."""
        facilities = self.engine.facilities
        inactive_facilities = sum(1 for f in facilities if not f.is_active)
        total_redirects = sum(getattr(f, 'redirected_count', 0) for f in facilities)
        
        # Most polluting facility
        most_polluting = None
        max_emissions = -1.0
        for f in facilities:
            if f.emissions > max_emissions:
                max_emissions = f.emissions
                most_polluting = f
                
        # Most efficient facility
        most_efficient = None
        max_efficiency = -1.0
        for f in facilities:
            if f.is_active:
                eff = f.current_load / f.emissions if f.emissions > 0 else (99999.0 if f.current_load > 0 else 0.0)
                if eff > max_efficiency:
                    max_efficiency = eff
                    most_efficient = f
                    
        if not most_efficient and facilities:
            most_efficient = facilities[0]
        if not most_polluting and facilities:
            most_polluting = facilities[0]
            
        return {
            "inactive_count": inactive_facilities,
            "total_redirects": total_redirects,
            "most_polluting_id": most_polluting.facility_id if most_polluting else "N/A",
            "most_polluting_emissions": round(most_polluting.emissions, 1) if most_polluting else 0.0,
            "most_efficient_id": most_efficient.facility_id if most_efficient else "N/A",
            "most_efficient_type": most_efficient.facility_type if most_efficient else "N/A"
        }

    def get_resident_metrics(self):
        """Calculates resident compliance metrics."""
        disposals = csv_utils.read_csv(logger.DISPOSAL_LOG, as_dict=True)
        
        total_penalties = 0.0
        total_contamination = 0.0
        total_quantity = 0.0
        warning_counts = 0
        
        for d in disposals:
            try:
                qty = float(d.get("quantity", 0.0))
                contam = float(d.get("contamination", 0.0))
                pen = float(d.get("penalty", 0.0))
                total_penalties += pen
                total_contamination += contam
                total_quantity += qty
                
                if qty > 0 and (contam / qty) > constants.CONTAMINATION_WARNING_THRESHOLD:
                    warning_counts += 1
            except (ValueError, TypeError):
                pass
                
        avg_contamination_pct = (total_contamination / total_quantity * 100) if total_quantity > 0 else 0.0
        
        return {
            "total_penalties_issued": round(total_penalties, 1),
            "average_contamination_pct": round(avg_contamination_pct, 1),
            "warning_counts": warning_counts
        }

    # -------------------------------------------------------------------------
    #  TAB RENDERING ENGINE
    # -------------------------------------------------------------------------
    def render_operations_tab(self, frame):
        """Populates the Operations tab."""
        self.clear_frame(frame)
        bg = constants.DARK_MODE_BG if self.app.is_dark_mode else constants.LIGHT_MODE_BG
        fg = constants.DARK_MODE_FG if self.app.is_dark_mode else constants.LIGHT_MODE_FG
        card_bg = constants.DARK_MODE_INPUT if self.app.is_dark_mode else constants.LIGHT_MODE_INPUT
        
        metrics = self.get_operations_metrics()
        
        # Grid of key performance indicator cards
        kpis = [
            ("Total Waste Collected", f"{metrics['total_waste_collected_kg']} kg", "♻️"),
            ("Total Bins Serviced", f"{metrics['total_bins_serviced']} Bins", "🗑️"),
            ("Active Fleet Count", f"{metrics['active_vehicles']} Trucks", "🚚"),
            ("Active Facilities", f"{metrics['total_facilities_active']} Units", "🏭"),
            ("Current Emergencies", f"{metrics['current_emergencies']}", "⚠️")
        ]
        
        card_frame = tk.Frame(frame, bg=bg)
        card_frame.pack(fill=tk.X, pady=15)
        
        for idx, (label, val, icon) in enumerate(kpis):
            card = tk.LabelFrame(card_frame, text=icon, font=("Segoe UI", 12), bg=card_bg, fg=fg, bd=1, relief=tk.SOLID)
            card.grid(row=0, column=idx, padx=10, pady=5, sticky="nsew")
            card_frame.grid_columnconfigure(idx, weight=1)
            
            tk.Label(card, text=label, font=("Segoe UI", 10, "bold"), fg=fg, bg=card_bg).pack(pady=5)
            tk.Label(card, text=val, font=("Segoe UI", 14, "bold"), fg="#10B981" if label != "Current Emergencies" or metrics['current_emergencies'] == 0 else "red", bg=card_bg).pack(pady=(0, 5))

        # Chart Slot: Waste Category Distribution
        chart_container = tk.Frame(frame, bg=bg)
        chart_container.pack(fill=tk.BOTH, expand=True, pady=10)
        self.plot_waste_distribution(chart_container)

    def render_facilities_tab(self, frame):
        """Populates the Facilities tab with a list of facilities and manual stop/start controls."""
        self.clear_frame(frame)
        bg = constants.DARK_MODE_BG if self.app.is_dark_mode else constants.LIGHT_MODE_BG
        fg = constants.DARK_MODE_FG if self.app.is_dark_mode else constants.LIGHT_MODE_FG
        card_bg = constants.DARK_MODE_INPUT if self.app.is_dark_mode else constants.LIGHT_MODE_INPUT
        
        metrics = self.get_facility_metrics()
        
        # Upper Layout: Text Metrics & Redirection Alerts
        top_frame = tk.Frame(frame, bg=bg)
        top_frame.pack(fill=tk.X, pady=10)
        
        info_panel = tk.LabelFrame(top_frame, text="Facility Efficiency Stats", bg=card_bg, fg=fg, bd=1, relief=tk.SOLID, padx=15, pady=10)
        info_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(info_panel, text=f"🔴 Suspended Facilities: {metrics['inactive_count']}", font=("Segoe UI", 10, "bold"), fg="red" if metrics['inactive_count'] > 0 else fg, bg=card_bg, anchor="w").pack(fill=tk.X, pady=2)
        tk.Label(info_panel, text=f"🔀 Waste Redirections (Failovers): {metrics['total_redirects']}", font=("Segoe UI", 10, "bold"), fg="#3B82F6", bg=card_bg, anchor="w").pack(fill=tk.X, pady=2)
        tk.Label(info_panel, text=f"✨ Most Efficient: Facility {metrics['most_efficient_id']} ({metrics['most_efficient_type']})", font=("Segoe UI", 10), fg=fg, bg=card_bg, anchor="w").pack(fill=tk.X, pady=2)
        tk.Label(info_panel, text=f"🚨 Most Polluting: Facility {metrics['most_polluting_id']} ({metrics['most_polluting_emissions']} kg CO2)", font=("Segoe UI", 10), fg=fg, bg=card_bg, anchor="w").pack(fill=tk.X, pady=2)
        
        redirections_box = tk.LabelFrame(top_frame, text="Failover/Redirection Log Alerts", bg=card_bg, fg=fg, bd=1, relief=tk.SOLID, padx=15, pady=10)
        redirections_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        fac_logs = csv_utils.read_csv(logger.FACILITY_LOG, as_dict=True)
        if not fac_logs:
            tk.Label(redirections_box, text="✅ All facilities operational. No failover events logged.", font=("Segoe UI", 9, "italic"), fg="green", bg=card_bg).pack(pady=10)
        else:
            for l in fac_logs[-3:]:
                log_txt = f"[{l.get('timestamp')[-8:]}] Facility {l.get('facility_id')} failed over! Waste routed to {l.get('redirected_to')}"
                tk.Label(redirections_box, text=log_txt, font=("Consolas", 9), fg="orange", bg=card_bg, anchor="w").pack(fill=tk.X, pady=1)

        # Middle Layout: Facility Registry treeview list (No Graph!)
        list_frame = tk.LabelFrame(frame, text="Processing Facility Operations Registry", bg=card_bg, fg=fg, bd=1, relief=tk.SOLID, padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        cols = ("Facility ID", "Type", "Current Load (kg)", "Max Capacity (kg)", "CO2 Emissions (kg)", "Processing Status", "Activity Status", "Backup Partner")
        tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def refresh_facilities():
            for i in tree.get_children():
                tree.delete(i)
            for f in self.engine.facilities:
                # Determine processing status
                if f.processing_time_left > 0:
                    proc_status = f"PROCESSING ({f.processing_time_left} ticks)"
                else:
                    proc_status = "READY" if (f.current_load / f.max_daily_capacity) >= f.efficiency_threshold else "WAITING"
                
                # Determine activity status and colors
                if not f.is_active:
                    if f.emissions >= f.emission_limit:
                        act_status = "🔴 SUSPENDED (HIGH EMISSIONS)"
                    else:
                        act_status = "⛔ STOPPED (MANUAL)"
                else:
                    act_status = "🟢 ACTIVE"
                
                # Find backup partner
                partner = self.engine.facility_allocator.get_partner_facility(f)
                partner_str = partner.facility_id if partner else "⚠️ NONE"
                    
                tree.insert('', 'end', values=(
                    f.facility_id,
                    f.facility_type,
                    f"{f.current_load:.1f}",
                    f"{f.max_daily_capacity:.1f}",
                    f"{f.emissions:.1f} / {f.emission_limit:.1f}",
                    proc_status,
                    act_status,
                    partner_str
                ))
                
        # Toggle start/stop button action
        def toggle_facility_status():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Please select a facility from the list.")
                return
            fid = tree.item(sel[0])['values'][0]
            facility = next((f for f in self.engine.facilities if f.facility_id == fid), None)
            
            if facility:
                if facility.is_active:
                    facility.is_active = False
                    logger.log_facility_event(facility.facility_id, "MANUAL_SHUTDOWN", 
                                                f"Facility manually stopped by administrator.")
                    
                    # Auto-reroute existing load to the partner facility
                    reroute_msg = ""
                    if facility.current_load > 0:
                        load_before = facility.current_load
                        partner = self.engine.facility_allocator.reroute_waste_on_shutdown(facility)
                        if partner:
                            reroute_msg = (f"\n\n🔀 {load_before:.1f}kg of waste has been "
                                          f"automatically rerouted to backup facility {partner.facility_id} "
                                          f"({partner.facility_type}).")
                        else:
                            reroute_msg = (f"\n\n⚠️ WARNING: No active backup facility available! "
                                          f"{load_before:.1f}kg of waste remains stranded.")
                    
                    messagebox.showinfo("Facility Stopped", 
                                       f"Facility {fid} has been shut down.{reroute_msg}")
                else:
                    # If high emissions exceeded, warn first or let it override
                    if facility.emissions >= facility.emission_limit:
                        if messagebox.askyesno("Warning", f"Facility {fid} exceeded its CO2 emissions limit ({facility.emissions:.1f} kg). Restarting will reset its emissions. Proceed?"):
                            facility.emissions = 0.0  # Reset emissions on manual override!
                            facility.is_active = True
                            logger.log_facility_event(facility.facility_id, "MANUAL_OVERRIDE_RESTART", 
                                                        f"Facility emissions reset. Manually restarted by administrator.")
                            messagebox.showinfo("Facility Restarted", f"Facility {fid} emissions reset and restarted successfully.")
                        else:
                            return
                    else:
                        facility.is_active = True
                        logger.log_facility_event(facility.facility_id, "MANUAL_RESTART", 
                                                    f"Facility manually restarted by administrator.")
                        messagebox.showinfo("Facility Started", f"Facility {fid} has been started successfully.")
                
                # Refresh dashboard and sync live monitoring tab views
                refresh_facilities()
                self.app.refresh_admin_ui()
                
        btn_bar = tk.Frame(list_frame, bg=card_bg)
        btn_bar.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_bar, text="⚡ Toggle Facility Status (Start / Stop)", command=toggle_facility_status).pack(side=tk.LEFT, padx=5)
        
        refresh_facilities()

    def render_residents_tab(self, frame):
        """Populates the Residents tab with Compliance KPIs and the Resident Accounts Directory (User management)."""
        self.clear_frame(frame)
        bg = constants.DARK_MODE_BG if self.app.is_dark_mode else constants.LIGHT_MODE_BG
        fg = constants.DARK_MODE_FG if self.app.is_dark_mode else constants.LIGHT_MODE_FG
        card_bg = constants.DARK_MODE_INPUT if self.app.is_dark_mode else constants.LIGHT_MODE_INPUT
        
        metrics = self.get_resident_metrics()
        
        # 1. Compliance Cards Frame (Top)
        top_frame = tk.Frame(frame, bg=bg)
        top_frame.pack(fill=tk.X, pady=10)
        
        kpis = [
            ("Average Contamination Level", f"{metrics['average_contamination_pct']}%", "☣️")
        ]
        
        for idx, (label, val, icon) in enumerate(kpis):
            card = tk.LabelFrame(top_frame, text=icon, font=("Segoe UI", 11), bg=card_bg, fg=fg, bd=1, relief=tk.SOLID)
            card.grid(row=0, column=idx, padx=10, pady=5, sticky="nsew")
            top_frame.grid_columnconfigure(idx, weight=1)
            
            tk.Label(card, text=label, font=("Segoe UI", 9, "bold"), fg=fg, bg=card_bg).pack(pady=5)
            
            color = "#10B981"
            tk.Label(card, text=val, font=("Segoe UI", 12, "bold"), fg=color, bg=card_bg).pack(pady=(0, 5))

        # 2. Resident Accounts Directory List Frame (Middle)
        list_frame = tk.LabelFrame(frame, text="Municipal Resident Accounts Directory", bg=card_bg, fg=fg, bd=1, relief=tk.SOLID, padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        cols = ("Name", "ID", "Role", "Zone", "Violation Score / Penalty")
        tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def refresh_list():
            for i in tree.get_children(): 
                tree.delete(i)
            try:
                self.app.user_manager._load_users()
                for u in self.app.user_manager.users:
                    role_str = str(u.role).capitalize() if u.role else "Resident"
                    zone_str = str(u.zone).capitalize() if u.zone else "N/A"
                    name_str = str(u.name) if u.name else "N/A"
                    uid_str = str(u.user_id) if u.user_id else "N/A"
                    violation_score = u.violation_score
                    
                    tree.insert('', 'end', values=(
                        name_str, 
                        uid_str, 
                        role_str, 
                        zone_str, 
                        violation_score
                    ))
            except Exception as e:
                print(f"[RECONCILE ERROR] Failed to load or populate resident list: {e}")
                
        # Attach refresh pointer so adding or editing users updates this exact list!
        frame.refresh_ptr = refresh_list
        
        # 3. Actions Button Bar (Bottom)
        btn_bar = tk.Frame(list_frame, bg=card_bg)
        btn_bar.pack(fill=tk.X, pady=5)
        
        def add_user_action():
            self.app.open_add_user_dialog(frame)
            
        def edit_user_action():
            self.app.open_edit_user_dialog(frame, {"tree": tree})
            
        def delete_user_action():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Please select an account to delete.")
                return
            uid = tree.item(sel[0])['values'][1]
            if str(uid) == self.app.current_user.user_id:
                messagebox.showerror("Error", "You cannot delete yourself!")
                return
            if messagebox.askyesno("Confirm Deletion", f"Permanently remove user ID '{uid}' from database?"):
                if self.app.user_manager.delete_user(uid):
                    refresh_list()
                    messagebox.showinfo("Success", "Account deleted successfully.")
                    
        ttk.Button(btn_bar, text="➕ Add Resident Account", command=add_user_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_bar, text="✏️ Edit Selected Account", command=edit_user_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_bar, text="🗑️ Delete Selected Account", command=delete_user_action).pack(side=tk.LEFT, padx=5)
        
        refresh_list()

    # -------------------------------------------------------------------------
    #  MATPLOTLIB CHARTING INTEGRATION
    # -------------------------------------------------------------------------
    def clear_frame(self, frame):
        """Removes existing widgets inside a frame for clean reloading."""
        for widget in frame.winfo_children():
            widget.destroy()

    def apply_chart_style(self, fig, ax):
        """Applies premium look matching Dark or Light mode UI."""
        is_dark = self.app.is_dark_mode
        bg_col = "#2b2b2b" if is_dark else "#f4f4f9"
        fg_col = "#ffffff" if is_dark else "#000000"
        ax_col = "#3c3f41" if is_dark else "#ffffff"
        
        fig.patch.set_facecolor(bg_col)
        ax.set_facecolor(ax_col)
        ax.tick_params(colors=fg_col, labelsize=9)
        ax.xaxis.label.set_color(fg_col)
        ax.yaxis.label.set_color(fg_col)
        ax.title.set_color(fg_col)
        for spine in ax.spines.values():
            spine.set_color(fg_col)
            
    def plot_waste_distribution(self, container):
        """Plots waste quantities by category (Pie chart). Fits screen perfectly without Matplotlib equal axis bug."""
        disposals = csv_utils.read_csv(logger.DISPOSAL_LOG, as_dict=True)
        
        data = {"Biodegradable": 0.0, "Recyclable": 0.0, "Hazardous": 0.0, "Electronic": 0.0}
        for d in disposals:
            cat = d.get("category", "").capitalize()
            if "e-waste" in cat.lower() or "electronic" in cat.lower():
                cat = "Electronic"
            if cat in data:
                try:
                    data[cat] += float(d.get("quantity", 0.0))
                except ValueError:
                    pass

        if sum(data.values()) == 0.0:
            for b in self.engine.bins:
                cat = b.waste_type.capitalize()
                if cat in data:
                    data[cat] += b.fill_level

        # Use a square aspect figure to prevent squashing, and avoid tight_layout constraint race
        fig = Figure(figsize=(5, 3.8), dpi=100)
        ax = fig.add_subplot(111)
        self.apply_chart_style(fig, ax)
        
        categories = list(data.keys())
        values = list(data.values())
        
        if sum(values) == 0.0:
            ax.text(0.5, 0.5, "No disposal operations data available yet.\nRun ticks in dashboard/admin to generate data.", 
                    horizontalalignment='center', verticalalignment='center', color='gray', transform=ax.transAxes)
            ax.set_axis_off()
        else:
            colors = ["#10B981", "#3B82F6", "#EF4444", "#F59E0B"]
            # Set aspect equal box to prevent clipping
            ax.set_aspect('equal', adjustable='box')
            ax.pie(values, labels=categories, colors=colors, autopct='%1.1f%%', startangle=140, 
                   textprops={'color': 'white' if self.app.is_dark_mode else 'black', 'fontsize': 8})
            ax.set_title("Operational Waste Processing Composition Ratio", fontsize=10, fontweight="bold", pad=10)
            
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        # Pack centered so it fits perfectly on all screen resolutions!
        canvas.get_tk_widget().pack(anchor=tk.CENTER, pady=10)
