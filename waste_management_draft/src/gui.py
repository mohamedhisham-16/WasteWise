import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import threading
import sys
import os

# Add src path ensuring we can import backend logic
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from data_loader import load_all
from engine import SimulationEngine

class WasteWiseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("WasteWise - Urban Simulation Dashboard")
        self.geometry("1100x700")
        self.configure(bg="#f4f4f9")
        
        # System Styles
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background="#f4f4f9")
        style.configure("TLabel", background="#f4f4f9", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        
        # Load Simulation
        self.init_simulation()
        
        # Build UI
        self.build_ui()
        self.refresh_ui()
        
        self.log_message("System Initialized Successfully.")

    def init_simulation(self):
        bins, vehicles, facilities, graph = load_all()
        self.engine = SimulationEngine(bins, vehicles, facilities, graph)
        self.engine.reset_all()

    def build_ui(self):
        # Master frames
        self.left_panel = ttk.Frame(self, padding=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_panel = ttk.Frame(self, padding=10)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- LEFT PANEL: Bins & Facilities --- #
        # Bins Area
        ttk.Label(self.left_panel, text="City Waste Bins", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.bins_frame = ttk.Frame(self.left_panel)
        self.bins_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.bin_widgets = {} # Stores progress bars and labels by bin_id
        
        for i, b in enumerate(self.engine.bins):
            row_frame = ttk.Frame(self.bins_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            lbl = ttk.Label(row_frame, text=f"{b.bin_id} ({b.waste_type})", width=25)
            lbl.pack(side=tk.LEFT)
            
            pb = ttk.Progressbar(row_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
            pb.pack(side=tk.LEFT, padx=10)
            
            val_lbl = ttk.Label(row_frame, text="0.0%", width=8)
            val_lbl.pack(side=tk.LEFT)
            
            self.bin_widgets[b.bin_id] = {"pb": pb, "val": val_lbl}

        # Facilities Area
        ttk.Label(self.left_panel, text="Processing Facilities", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        columns_fac = ('ID', 'Type', 'Processed Load')
        self.tree_fac = ttk.Treeview(self.left_panel, columns=columns_fac, show='headings', height=5)
        for col in columns_fac:
            self.tree_fac.heading(col, text=col)
            self.tree_fac.column(col, width=120)
        self.tree_fac.pack(fill=tk.X)
        
        # --- RIGHT PANEL: Fleet, Logs, Controls --- #
        # Fleet Area
        ttk.Label(self.right_panel, text="Fleet Status", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        columns_veh = ('ID', 'Type', 'Load', 'Status')
        self.tree_veh = ttk.Treeview(self.right_panel, columns=columns_veh, show='headings', height=5)
        for col in columns_veh:
            self.tree_veh.heading(col, text=col)
            self.tree_veh.column(col, width=100)
        self.tree_veh.pack(fill=tk.X, pady=(0, 15))
        
        # Logs Area
        ttk.Label(self.right_panel, text="Live Events Log", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(self.right_panel, height=15, width=50, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Controls Area
        controls_frame = ttk.Frame(self.right_panel)
        controls_frame.pack(fill=tk.X)
        
        self.btn_simulate = ttk.Button(controls_frame, text="1. Advance Time (Add Waste)", command=self.simulate_step)
        self.btn_simulate.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.btn_optimize = ttk.Button(controls_frame, text="2. Run Dispatch Engine", command=self.run_optimization)
        self.btn_optimize.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.btn_reset = ttk.Button(controls_frame, text="Reset System", command=self.reset_system)
        self.btn_reset.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto scroll to bottom
        self.update_idletasks()
        
    def refresh_ui(self):
        # Update Bins
        for b in self.engine.bins:
            fill = b.get_fill_percentage()
            widgets = self.bin_widgets[b.bin_id]
            widgets["pb"]["value"] = fill
            widgets["val"].config(text=f"{fill:.1f}%")
            
            # Change color conceptually using standard themes (Hard in Tkinter but we can at least show it)
            if fill >= 90:
                widgets["val"].config(foreground='red', font=("Segoe UI", 10, "bold"))
            elif fill >= 70:
                widgets["val"].config(foreground='orange', font=("Segoe UI", 10, "bold"))
            else:
                widgets["val"].config(foreground='black', font=("Segoe UI", 10))

        # Update Facilities
        for item in self.tree_fac.get_children():
            self.tree_fac.delete(item)
            
        for f in self.engine.facilities:
            self.tree_fac.insert('', 'end', values=(
                f.facility_id, 
                f.facility_type, 
                f"{f.current_load:.1f} / {f.max_daily_capacity:.1f} kg"
            ))

        # Update Fleet
        for item in self.tree_veh.get_children():
            self.tree_veh.delete(item)
            
        for v in self.engine.vehicles:
            # Assuming 'Idle' if current_load is 0, else 'Active'
            status = "Idle" if v.current_load == 0 else "Loaded"
            self.tree_veh.insert('', 'end', values=(
                v.vehicle_id, 
                v.vehicle_type, 
                f"{v.current_load:.1f} / {v.total_capacity:.1f} kg",
                status
            ))

    def simulate_step(self):
        self.log_message("\n--- TIME TICK: Adding Waste ---")
        for b in self.engine.bins:
            if random.random() > 0.3:
                amount = round(random.uniform(10.0, 40.0), 2)
                self.engine.add_waste(b.bin_id, b.waste_type, amount, user_id=f"SimUser")
                
                # Fetch recent engine logs purely for displaying here instead of modifying engine right now
                # Or we can just log a summary
                self.log_message(f"  -> Added {amount}kg to {b.bin_id} ({b.waste_type})")
                
        self.log_message("Waste levels increased across the city.")
        self.refresh_ui()

    def run_optimization(self):
        self.log_message("\n[ENGINE CHECK] Scanning for full bins...")
        
        # Engine execution might be slightly intensive, but for 10 bins it's instantaneous.
        summary = self.engine.run_optimization(alert_threshold=70.0)
        
        # Retrieve logs generated by engine
        # We process the recent event logs the engine made 
        # (Alternatively, we can just print the summary).
        if summary["bins_detected"] == 0:
            self.log_message("System healthy. No dispatches required.")
        else:
            self.log_message(f"Engine Dispatch Complete:")
            self.log_message(f" > Collected {summary['bins_collected']} overloaded bins.")
            self.log_message(f" > Trucks Unloaded: {summary['vehicles_unloaded']}")
            if summary['failed_allocations']:
                self.log_message(f" > FAILED TO ALLOCATE: {len(summary['failed_allocations'])}")
        
        self.refresh_ui()

    def reset_system(self):
        self.engine.reset_all()
        self.log_message("\n[SYSTEM SYSTEM_RESET] All bins and vehicles reverted to starting state.")
        self.refresh_ui()

if __name__ == "__main__":
    app = WasteWiseGUI()
    app.mainloop()
