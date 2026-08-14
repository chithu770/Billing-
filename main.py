"""
Category-Wise Billing Software
Main Application Entry Point Script.
"""
import sys
import os

# Ensure current directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app_window import AppWindow

def main():
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
