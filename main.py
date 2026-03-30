from gui.interface import SwaraApp
from swara_core.memory_db import init_db   # ✅ correct import

if __name__ == "__main__":
    init_db()     # initialize SQLite once
    SwaraApp().mainloop()
