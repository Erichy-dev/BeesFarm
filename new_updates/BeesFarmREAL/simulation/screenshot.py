import os
from PyQt5 import QtCore
from simulation.simulation_config import ENABLE_SCREENSHOTS

class ScreenshotManager:
    def __init__(self, fig):
        self.fig = fig
        self.screenshot_counter = 0
        self.screenshot_timer = None
        
    def initialize_timer(self, interval):
        if ENABLE_SCREENSHOTS:
            self.screenshot_timer = QtCore.QTimer()
            self.screenshot_timer.timeout.connect(self.take_screenshot)
            self.screenshot_timer.start(interval)  # milliseconds
    
    def take_screenshot(self):
        # Import here to get the current value, not the value at module import time
        from simulation.simulation_config import SIMULATION_COMPLETE
        
        if not ENABLE_SCREENSHOTS or SIMULATION_COMPLETE:
            self.stop_timer()  # Actively stop the timer when simulation completes
            return
            
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            
        self.screenshot_counter += 1
        
        # Get the figure canvas (Qt widget)
        canvas = self.fig.canvas
        
        try:
            # Option 1: Use Qt's grabFramebuffer for a clean screenshot
            if hasattr(canvas, 'grab'):
                # For Qt5
                pixmap = canvas.grab()
                pixmap.save(f"screenshots/screenshot_{self.screenshot_counter}.png")
                print(f"Screenshot saved: screenshots/screenshot_{self.screenshot_counter}.png")
            else:
                # Option 2: Fallback to matplotlib's savefig
                self.fig.savefig(f"screenshots/screenshot_{self.screenshot_counter}.png")
                print(f"Screenshot saved using matplotlib: screenshots/screenshot_{self.screenshot_counter}.png")
        except Exception as e:
            print(f"Screenshot error: {e}")
            
    def stop_timer(self):
        if self.screenshot_timer and self.screenshot_timer.isActive():
            print("Screenshot timer stopped")
            self.screenshot_timer.stop() 