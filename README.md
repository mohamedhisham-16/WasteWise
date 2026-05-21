# WasteWise: Intelligent Urban Waste Management

WasteWise is an advanced urban waste management system designed to optimize waste collection, processing, and disposal in smart cities. It features a dual-facility redundancy architecture, real-time simulation, vehicle routing, and intelligent resource allocation.

## 🗄️ Project Structure

- **`src/`**: Core application code.
  - **`simulation/`**: Simulation engine and data management.
  - **`facilities/`**: Facility operations and allocation logic.
  - **`vehicles/`**: Vehicle fleet management.
  - **`analytics/`**: Performance monitoring and reporting.
  - **`contracts/`**: Contract management and compliance.
  - **`logs/`**: Persistent logs and data exports.
  - **`gui/`**: Graphical User Interface (Main window: `gui.py`).
- **`data/`**: Sample data and city configurations.
- **`docs/`**: Project documentation.
- **`requirements.txt`**: Python dependencies.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip (Python package installer)

### Installation

1. **Clone the repository** (or download the source code).

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

The application can be started using the **GUI launcher**: 

```bash
python gui.py
```

### Running Tests

To verify the system's core logic, use the provided test scripts:

```bash
# Facility failover tests (critical redundancy features)
python test_facility_failover.py

# Core system tests
python test_core_functionality.py

# All tests suite
python test_suite.py
```

## 📋 Key Features

### 🏭 Dual-Facility Redundancy
- Every facility has a designated **partner facility** for backup.
- Automatic failover ensures continuous operation when a facility is down.
- Waste is intelligently **rerouted** to the backup location during emergencies.

### 📊 Real-Time Simulation
- Step-by-step simulation of waste collection and processing.
- Real-time monitoring of facility loads, vehicle statuses, and costs.

### 🤖 Smart Resource Management
- **Facility Allocation**: Intelligent distribution of waste across facilities based on capacity and type.
- **Vehicle Routing**: Optimized routes to minimize distance and time.
- **Dynamic Scheduling**: Real-time adjustments to routes and schedules based on incidents and loads.

### 📑 Contract Management
- Monitor vendor compliance with service level agreements (SLAs).
- Automated penalty and reward calculations.

## 📂 Sample Data & Customization

- **Data Files**: Located in `data/`. These files define the city layout, facility capacities, and population waste generation profiles.
- **Configuration**: Modify data files to simulate different city scenarios or facility configurations.

## 📚 Documentation

For detailed information on the system architecture, design decisions, and user guide, please refer to the `docs/` folder.