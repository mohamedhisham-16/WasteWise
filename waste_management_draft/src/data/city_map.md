# WasteWise City Network Map

This document presents a high-fidelity visual map of the **WasteWise Smart Urban Collection Network**. It illustrates depots, waste generation zones (residential, commercial, industrial, and medical), and specialized processing facilities with accurate travel distances.

---

## Interactive City Topology Map

```mermaid
graph TD
    %% Define Nodes with Styles and Descriptions
    NorthDepot["North Depot (Base)"]
    SouthDepot["South Depot (Base)"]
    Greenwood["Greenwood Suburb (Residential)"]
    PineHeights["Pine Heights (Residential)"]
    MetroHospital["Metro Hospital (Medical)"]
    CompostCenter["Compost Center (Facility)"]
    DowntownMarket["Downtown Market (Commercial)"]
    CentralPlaza["Central Plaza (Commercial)"]
    HazmatDisposal["Hazmat Disposal (Facility)"]
    IndustrialZone["Industrial Zone (Industrial)"]
    RecyclingHub["Recycling Hub (Facility)"]
    EWasteHub["E-Waste Hub (Facility)"]

    %% Connect Row 1
    NorthDepot --- |3 km| Greenwood
    Greenwood --- |4 km| PineHeights
    PineHeights --- |2 km| MetroHospital

    %% Connect Row 2
    CompostCenter --- |5 km| DowntownMarket
    DowntownMarket --- |3 km| CentralPlaza
    CentralPlaza --- |4 km| HazmatDisposal

    %% Connect Row 3
    SouthDepot --- |3 km| IndustrialZone
    IndustrialZone --- |6 km| RecyclingHub
    RecyclingHub --- |2 km| EWasteHub

    %% Vertical Connections
    NorthDepot --- |4 km| CompostCenter
    CompostCenter --- |5 km| SouthDepot

    Greenwood --- |3 km| DowntownMarket
    DowntownMarket --- |4 km| IndustrialZone

    PineHeights --- |2 km| CentralPlaza
    CentralPlaza --- |5 km| RecyclingHub

    MetroHospital --- |3 km| HazmatDisposal
    HazmatDisposal --- |4 km| EWasteHub

    %% Styling Theme matching premium Glassmorphism / Dark mode
    style NorthDepot fill:#4338ca,stroke:#818cf8,stroke-width:2px,color:#fff
    style SouthDepot fill:#4338ca,stroke:#818cf8,stroke-width:2px,color:#fff
    
    style Greenwood fill:#15803d,stroke:#4ade80,stroke-width:2px,color:#fff
    style PineHeights fill:#15803d,stroke:#4ade80,stroke-width:2px,color:#fff
    style MetroHospital fill:#be123c,stroke:#fda4af,stroke-width:2px,color:#fff
    
    style DowntownMarket fill:#b45309,stroke:#fbbf24,stroke-width:2px,color:#fff
    style CentralPlaza fill:#b45309,stroke:#fbbf24,stroke-width:2px,color:#fff
    style IndustrialZone fill:#6b7280,stroke:#d1d5db,stroke-width:2px,color:#fff
    
    style CompostCenter fill:#0369a1,stroke:#38bdf8,stroke-width:2px,color:#fff
    style RecyclingHub fill:#0369a1,stroke:#38bdf8,stroke-width:2px,color:#fff
    style HazmatDisposal fill:#0369a1,stroke:#38bdf8,stroke-width:2px,color:#fff
    style EWasteHub fill:#0369a1,stroke:#38bdf8,stroke-width:2px,color:#fff
```

---

## Location Properties Summary

### Depots & Bases
*   **North Depot**: Home depot for compactors `V001`, `V002`, and mini-truck `V005`.
*   **South Depot**: Home depot for hazmat truck `V003` and electronic e-waste carrier `V004`.

### Waste Generation Zones
*   **Greenwood Suburb & Pine Heights**: Residential area generating Biodegradable, Recyclable, and Hazardous waste.
*   **Metro Hospital**: Hospital zone generating Hazardous and Biodegradable waste.
*   **Downtown Market & Central Plaza**: Commercial centers generating Recyclable, Electronic, and Biodegradable waste.
*   **Industrial Zone**: Industrial area generating Hazardous and Electronic waste.

### Processing Facilities
*   **Compost Center (`F001`)**: Processes biodegradable materials (capacity: 1000 kg).
*   **Recycling Hub (`F002`)**: Processes recyclables (capacity: 1500 kg).
*   **Hazmat Disposal (`F003`)**: Sanitizes and processes hazardous elements (capacity: 500 kg).
*   **E-Waste Hub (`F004`)**: Recycles electronic materials (capacity: 300 kg).
