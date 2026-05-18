# src/gui.py
# Backward-compatible entry point launcher for the WasteWise GUI Application

import sys
import os

# Guarantee src folder path is in python system path to resolve module namespaces
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from gui.gui import main

if __name__ == "__main__":
    main()
