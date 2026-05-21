# 1. Abstract
WasteWise is an advanced, modular urban waste management application developed in Python. It provides a comprehensive solution for simulating, monitoring, and optimizing city-wide waste collection, segregation, and processing operations. The system features a real-time simulation engine, automated dual-facility redundancy with emission-based failover, dynamic vehicle routing, and an interactive Tkinter/Matplotlib dashboard. By enforcing segregation rules, optimizing fleet logistics to reduce carbon footprint, and tracking real-time facility operations, WasteWise demonstrates a modern software approach to sustainable smart-city administration.

# 2. Introduction
Urban waste management is a complex, multi-stage process involving waste generation, segregation, collection, transportation, processing, and disposal. Inefficiencies in these areas can lead to environmental hazards, public health issues, and increased operational costs.

WasteWise was developed to address these inefficiencies by implementing a Smart Urban Waste Collection and Processing Optimization System. Built with Python 3.10+, this system transitions from a basic static collection model to a dynamic, data-driven architecture. Key capabilities include a randomized simulation engine representing resident disposal patterns, an intelligent vehicle routing module using graph algorithms, and an automated failover system that disables processing facilities when they exceed safe CO2 emission limits. The platform includes a premium Graphical User Interface (GUI) to provide administrators with live operational metrics, resident violation leaderboards, and graphical data visualizations.

# 3. Problem Statement
The objective of this project is to design an intelligent system that efficiently manages waste flow across city zones, ensures timely collection, optimizes processing facility usage, and adapts dynamically to varying waste generation patterns and disruptions.

A standard city grid consists of waste sources (households, commercial units), bins, processing facilities, and collection vehicles. The goal is to optimize the system such that:
*   Waste is correctly segregated into predefined categories (biodegradable, recyclable, hazardous, electronic).
*   Bins are serviced before they exceed their maximum capacity to prevent health hazards.
*   Processing units operate within their capacity and emission limits.
*   Collection routes minimize total travel distance and operational costs.

**Constraints:**
1.  **Waste Segregation Accuracy**: Contaminated waste must be flagged for penalties.
2.  **Bin Capacity Constraints**: Collection must occur before overflow; high-fill bins (e.g., >70%) get priority.
3.  **Processing Facility Capacity & Emissions**: Facilities have daily limits and an emission threshold (e.g., 150.0 kg CO2). Excess waste must trigger failover.
4.  **Vehicle Compatibility Constraints**: Specialized vehicles handle specific waste (e.g., Hazardous).
5.  **Route Optimization Constraint**: Routes must be calculated to minimize distance while satisfying bin priority.
6.  **Priority Zone Handling**: Critical zones get higher priority for waste collection.

# 4. Exploration of Problem Statement
## 4.1 Key Functionalities
*   **Real-Time Simulation**: Step-by-step engine simulating city-wide waste disposal, capacity tracking, and automated generation of emergencies.
*   **Automated Environmental Failover**: A facility failover system that tracks accumulating emissions. If a facility exceeds its limit, it is shut down, and subsequent trucks are redirected to a backup facility.
*   **Dynamic Vehicle Routing**: Fleet management logic that pairs available vehicles with high-priority bins and calculates optimal paths using distance graphs (Dijkstra's heuristic approaches).
*   **Analytics Dashboard**: A robust Tkinter UI embedding Matplotlib charts to display live KPIs across Operations, Facilities, Residents, Routing, and Emergencies.
*   **Resident & Penalty Tracking**: Monitors user disposal actions, flags contamination, and maintains a penalty ledger saved to persistent CSV logs.

## 4.2 Challenges & Constraints
*   **Dynamic Data Synchronization**: Integrating the backend simulation tick with the frontend Tkinter UI requires careful state management to ensure charts and grids update in real-time without locking the main thread.
*   **Routing Complexity**: Dynamic routing requires recalculating shortest paths continuously as bin priorities and facility states (active/inactive) change during the simulation.
*   **Decoupled Architecture**: Transitioning from a monolithic script to a 10-package modular structure (Analytics, Auth, Data, Emergency, Facilities, GUI, Models, Routing, Simulation, Utils) required eliminating circular dependencies and building centralized utilities (e.g., unified loggers).

# 5. Limitations of Existing Systems
## 5.1 Focus on Static Collection Schedules
Traditional waste management systems rely on fixed, static schedules regardless of actual bin fill levels. This leads to either overflowing bins (health hazards) or trucks visiting empty bins (wasted fuel). WasteWise addresses this by adopting a dynamic, priority-based dispatch model.
## 5.2 Future Expansion
*   **IoT Sensor Integration**: Replacing simulated disposal events with real-world smart bin weight and volume sensors.
*   **AI-Driven Predictive Analytics**: Utilizing machine learning models on historical CSV data to predict waste generation surges before they happen.
*   **Mobile Application Port**: Creating a driver-facing mobile app for live route navigation and field reporting.

# 6. Architecture Diagram with Explanation
The application is split into 10 cohesive packages that communicate through centralized data models and unified utilities.

*   `src/gui.py` / `src/main.py` - Application Entry points (GUI and CLI).
*   `src/simulation/` - Orchestrates the lifecycle (engine, monitoring, priority scoring, dispatch).
*   `src/routing/` - Manages distance graphs and route optimizers.
*   `src/facilities/` & `src/emergency/` - Handle route-to-processing allocation, failovers, and critical overflows.
*   `src/analytics/` - Powers the dashboard logic, calculations and layouts.
*   `src/models/` - Centralized data models (Bins, Vehicles, Facilities).
*   `src/utils/` - Centralized loggers, CSV CRUD helpers, and system constants.

*(Insert Architecture Diagram Here)*

# 7. Function Flowcharts
## 7.1 Automated Failover Logic
```
START 
  -> Vehicle needs to unload 
  -> Find Primary Closest Facility 
  -> Is Primary Active & Has Capacity? 
      -> [YES] Unload at Primary
      -> [NO / Emissions Exceeded] 
          -> Trigger Failover Redirection 
          -> Find Next Best Active Facility 
          -> Route Vehicle 
          -> Log Event 
  -> END
```

## 7.2 Core Simulation Engine Tick
```
START 
  -> Generate Citizen Disposals 
  -> Update Bin Capacities 
  -> Check for Overflow Emergencies 
  -> Run Priority Scoring 
  -> Dispatch Vehicles 
  -> Calculate Routes 
  -> Unload at Facilities 
  -> Update Analytics Dashboard 
  -> END
```

# 8. Modules with Constraints
## 8.1 Simulation Module
*   **Description**: Orchestrates the timeline of the city. Processes inputs and ticks the system forward.
*   **Constraints**: Must accurately update capacities without exceeding 100%. Handles concurrent disposal events gracefully.

## 8.2 Routing & Allocation Module
*   **Description**: Implemented in `distance_graph.py` and `route_optimizer.py`. Uses graph networks to navigate trucks.
*   **Constraints**: Vehicles are strictly constrained by their own weight capacity. They must return to depots or facilities when full.

## 8.3 Facilities & Environmental Module
*   **Description**: Manages processing units. Tracks CO2 equivalent emissions per waste type.
*   **Constraints**: Emissions accumulate. `EMISSION_LIMIT = 150.0`. Upon breach, facility is suspended, initiating failover.

## 8.4 Analytics Dashboard Module
*   **Description**: The visual frontend built with Tkinter.
*   **Constraints**: Must redraw Matplotlib charts on every simulation tick. Relies on `constants.py` for dynamic Light/Dark mode HSL theming.

# 9. Implementation
## 9.1 Data Organisation
All persistence is managed via directory-safe CSV handlers in `data/`:
*   `users.csv`: Resident registry.
*   `login_history.csv`: Authentication sessions.
*   `disposal_events.csv`: Live transaction logs.
*   `emergency_logs.csv`: Incident records.
*   `facility_logs.csv`: Failovers and emission flags.
*   `waste_mapping.json`: Standard composition and zone boundaries.

## 9.2 Development Tools
*   **Language**: Python 3.10+
*   **Environment**: Cross-platform (Windows / Linux / macOS)
*   **Execution**: CLI (`python src/main.py`) or GUI (`python src/gui.py`)

## 9.3 Libraries Used
*   **Standard Python Libraries**: `tkinter`, `csv`, `json`, `datetime`, `os`, `sys`, `math`.
*   **Third-Party Libraries**: `matplotlib` (for dynamic dashboard charting).

## 9.4 User Interface Design
*   **Dynamic Theme**: HSL-inspired palette switching between Dark Mode (obsidian background, emerald highlights) and Light Mode (platinum background, teal accents).
*   **5-Tab Layout**: Operations (KPIs, Pie Charts), Facilities (Bar Charts, Failover feeds), Residents (Leaderboards, Line Graphs), Routing (Logistics Grid), and Emergencies (Incident Tables).
*   **Real-time Sync**: Synchronous redrawing of Matplotlib figures on simulation ticks.

## 9.5 Code Implementation
**Automated Failover Emission Check snippet (`Facility` Class):**
```python
if self.emissions >= self.emission_limit:
    self.is_active = False
    logger.log_facility_event(self.facility_id, "EMISSION_LIMIT_EXCEEDED", "Facility suspended.")
```

# 10. Observations with Respect to Society
## 10.1 Environmental Impact
By tracking specific emissions (e.g., Hazardous waste generates more CO2 than Biodegradable) and limiting facility processing, the system enforces ecological safety. Optimized routing drastically reduces the fleet's carbon footprint.
## 10.2 Public Health and Sanitation
The emergency module prioritizes overflowing bins, ensuring hazardous waste or high-density organic waste does not become a public health hazard.
## 10.3 Civic Accountability
The resident penalty leaderboard creates an automated framework for tracking user contamination, encouraging proper at-home segregation.

# 11. Legal and Ethical Perspectives
## 11.1 Data Privacy
Resident profiles, disposal histories, and login sessions are securely managed. The system ensures that personal identification is decoupled from broad municipal analytics.
## 11.2 Fair Enforcement
Automated penalty processing removes human bias from enforcing segregation violations, though it requires robust appeal mechanisms in a real-world scenario.
## 11.3 Environmental Compliance
The hardcoded `EMISSION_LIMIT` acts as a strict regulatory compliance mechanism, ensuring local processing plants do not violate municipal air quality standards.

# 12. Limitations and Future Enhancements
## 12.1 Limitations
*   The current Dijkstra routing graph assumes static travel times and ignores live traffic data.
*   Bin capacities are simulated rather than reading from physical hardware.
*   Single-threaded UI can occasionally lag if processing extremely large CSV logs over thousands of ticks.

## 12.2 Future Enhancements
*   Integration with live API traffic services (e.g., Google Maps API).
*   Transitioning from CSV file storage to a robust relational database (PostgreSQL/SQLite).
*   Mobile companion app for residents to check their penalty score and bin collection schedule.

# 13. Learning Outcomes
*   **Software Architecture**: Successfully modularizing a monolithic codebase into decoupled, scalable packages.
*   **Data Structures & Algorithms**: Applying graph traversal (Dijkstra) and heuristic algorithms to solve dynamic vehicle routing problems.
*   **UI/UX Engineering**: Integrating complex Matplotlib data visualizations into native Tkinter desktop environments.
*   **Systems Design**: Modeling real-world constraints (capacities, emissions, speeds) into object-oriented Python classes.

# 14. Bibliography
[1] Python Software Foundation, "Tkinter — Python interface to Tcl/Tk," Python 3 Documentation. [Online]. Available: https://docs.python.org/3/library/tkinter.html
[2] J. D. Hunter, "Matplotlib: A 2D Graphics Environment," Computing in Science & Engineering, vol. 9, no. 3, pp. 90-95, 2007.
[3] E. W. Dijkstra, "A note on two problems in connexion with graphs," Numerische Mathematik, vol. 1, pp. 269–271, 1959.
