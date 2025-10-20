import tkinter as tk
from tkinter import ttk
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import main  # main.py must only have run_servo(event_queue) function


class ServoDashboard(tk.Tk):
    def __init__(self, event_queue):
        super().__init__()

        self.title("Servo Motor Dashboard")
        self.geometry("800x600")
        self.event_queue = event_queue

        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for labels
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Labels
        self.current_angle_label = ttk.Label(
            left_frame, text="Current Angle: --", font=("Arial", 14)
        )
        self.current_angle_label.pack(pady=5)

        self.last_action_label = ttk.Label(
            left_frame, text="Last Action: --", font=("Arial", 12)
        )
        self.last_action_label.pack(pady=5)

        self.left_count_label = ttk.Label(
            left_frame, text="Left Presses: 0", font=("Arial", 12)
        )
        self.left_count_label.pack(pady=5)

        self.right_count_label = ttk.Label(
            left_frame, text="Right Presses: 0", font=("Arial", 12)
        )
        self.right_count_label.pack(pady=5)

        # Right frame for donut chart
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize counters
        self.left_count = 0
        self.right_count = 0

        # Create matplotlib figure for donut chart
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Create canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize the donut chart
        self.update_donut_chart()

        # Start updating GUI
        self.after(200, self.update_dashboard)

    def update_donut_chart(self):
        """Update the donut chart with current left/right press counts"""
        self.ax.clear()

        # Data for the donut chart
        sizes = [self.left_count, self.right_count]
        labels = ['Left Button', 'Right Button']
        colors = ['#ff6b6b', '#4ecdc4']  # Red for left, teal for right

        # Only show chart if there are presses
        if sum(sizes) > 0:
            wedges, texts, autotexts = self.ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85
            )

            # Create donut by adding a white circle in the center
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            self.ax.add_artist(centre_circle)

            # Add title
            self.ax.set_title('Button Press Distribution', fontsize=14, fontweight='bold')
        else:
            # Show empty state
            self.ax.text(
                0.5, 0.5, 'No button presses yet',
                horizontalalignment='center',
                verticalalignment='center',
                transform=self.ax.transAxes,
                fontsize=12
            )
            self.ax.set_title('Button Press Distribution', fontsize=14, fontweight='bold')

        # Set equal aspect ratio to make it circular
        self.ax.set_aspect('equal')

        # Refresh the canvas
        self.canvas.draw()

    def update_dashboard(self):
        while not self.event_queue.empty():
            event = self.event_queue.get()
            action, angle = event["action"], event["angle"]

            self.current_angle_label.config(text=f"Current Angle: {angle}°")
            self.last_action_label.config(text=f"Last Action: {action}")

            if action == "Rotated Left":
                self.left_count += 1
            elif action == "Rotated Right":
                self.right_count += 1

            self.left_count_label.config(text=f"Left Presses: {self.left_count}")
            self.right_count_label.config(text=f"Right Presses: {self.right_count}")

            # Update the donut chart
            self.update_donut_chart()

        self.after(200, self.update_dashboard)


if __name__ == "__main__":
    event_queue = Queue()

    # Start GUI first in main thread
    app = ServoDashboard(event_queue)

    # Start servo control in separate process
    servo_process = Process(target=main.run_servo, args=(event_queue,))
    servo_process.start()

    # Start Tkinter mainloop
    app.mainloop()

    # Clean up when GUI closes
    servo_process.terminate()
    servo_process.join()
