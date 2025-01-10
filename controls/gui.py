import customtkinter as ctk
import tkinter as tk
import queue

from joystick_reader import JoystickReader
from device_communicator import DeviceCommunicator
from main import start_worker

from config import SerialConfig, MotorConfig


class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create a canvas widget for the scrollable area
        self.canvas = tk.Canvas(self, bg=self["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a vertical scrollbar
        self.scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview
        )
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.scrollable_frame_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Bind scrolling events
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_frame_configure(self, event):
        """Adjust the canvas scroll region to fit the scrollable frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize the scrollable frame to match the canvas width."""
        canvas_width = event.width
        self.canvas.itemconfig(self.scrollable_frame_id, width=canvas_width)

    def _on_mouse_wheel(self, event):
        """Scroll the canvas vertically when the mouse wheel is used."""
        self.canvas.yview_scroll(-int(event.delta / 120), "units")


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CRAMS Device Dashboard (Multithread)")
        self.geometry("1600x800")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Create queue for data exchange between worker and GUI
        self.data_queue = queue.Queue()

        # Create device / joystick
        self.device = DeviceCommunicator(port="COM3", baud_rate=115200, timeout=0.05)
        # self.device.connect()
        self.joystick = JoystickReader()
        self.prev_buttons = []  # previous button values for state changes

        # Start the worker thread
        self.worker_thread, self.stop_event = start_worker(
            self.joystick, self.device, self.data_queue, verbose=True
        )

        # Build the UI
        self._build_ui()

        # Start checking the queue
        self._poll_queue()

    def _build_ui(self):
        # Your existing layout code
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_columnconfigure(2, weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)

        # Panel A: PS4 Inputs (left)
        self.ps4_frame = ctk.CTkFrame(self, corner_radius=10)
        self.ps4_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Panel B: Configuration (middle)
        self.config_frame = ctk.CTkFrame(self, corner_radius=10)
        self.config_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Panel C: Device Messages (right)
        self.device_frame = ctk.CTkFrame(self, corner_radius=10)
        self.device_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        # Build sub-sections (the same code you had before)
        self._build_ps4_panel()
        self._build_config_panel()
        self._build_device_panel()

    def _build_ps4_panel(self):
        # Use the ScrollableFrame for the PS4 panel
        self.ps4_frame = ScrollableFrame(self)
        self.ps4_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Add title to the scrollable frame
        title_label = ctk.CTkLabel(
            self.ps4_frame.scrollable_frame,
            text="PS4 Controller State",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=5)

        # Axes Frame
        axes_frame = ctk.CTkFrame(self.ps4_frame.scrollable_frame)
        axes_frame.pack(fill="x", padx=10, pady=(0, 10))

        axes_title = ctk.CTkLabel(
            axes_frame,
            text="Joysticks & Triggers:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        axes_title.pack(anchor="w", padx=10, pady=5)

        self.axis_pair_labels = {}
        axis_pairs = [(0, 1), (2, 3), (4, 5)]
        axes_names = ["Left Stick", "Right Stick", "L2/R2 Triggers"]
        for pair, name in zip(axis_pairs, axes_names):
            pair_frame = ctk.CTkFrame(axes_frame)
            pair_frame.pack(fill="x", padx=10, pady=5)

            pair_label = ctk.CTkLabel(
                pair_frame, text=f"{name}:", width=100, anchor="w"
            )
            pair_label.pack(side="left", padx=(5, 0))

            value_label = ctk.CTkLabel(pair_frame, text="[0.00, 0.00]", anchor="w")
            value_label.pack(side="right", padx=(0, 5))

            self.axis_pair_labels[pair] = value_label

        # Buttons
        btn_frame = ctk.CTkFrame(self.ps4_frame.scrollable_frame)
        btn_frame.pack(fill="x", padx=10, pady=0)

        btn_title = ctk.CTkLabel(
            btn_frame,
            text="Buttons:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        btn_title.pack(anchor="w", padx=10, pady=(10, 5))

        self.button_groups = {
            "Face Buttons": [("X", 0), ("Circle", 1), ("Square", 2), ("Triangle", 3)],
            "System Buttons": [("Share", 4), ("PS4", 5), ("Options", 6)],
            "Stick Clicks": [("L Stick", 7), ("R Stick", 8)],
            "Shoulders": [("L1", 9), ("L2", 10)],
            "D-Pad": [("Up", 11), ("Down", 12), ("Left", 13), ("Right", 14)],
            "Touchpad": [("Touchpad", 15)],
        }

        self.checkbox_references = {}
        for group_name, items in self.button_groups.items():
            group_frame = ctk.CTkFrame(btn_frame)
            group_frame.pack(fill="x", padx=10, pady=5)

            group_label = ctk.CTkLabel(
                group_frame,
                text=group_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            )
            group_label.pack(anchor="w", padx=5, pady=(5, 2))

            row_frame = ctk.CTkFrame(group_frame)
            row_frame.pack(fill="x", padx=5, pady=5)

            for label_text, button_idx in items:
                cb = ctk.CTkCheckBox(row_frame, text=label_text, state="disabled")
                cb.pack(side="left", padx=(0, 10))
                self.checkbox_references[button_idx] = cb

    def _build_config_panel(self):
        title_label = ctk.CTkLabel(
            self.config_frame,
            text="Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=5)

        self.config_entries = {}

        config_items = [
            ("Thrust Offset", MotorConfig.THRUST_ZERO_SHIFT),
            ("Thrust Scaling", MotorConfig.THRUST_SCALING),
            ("Z Thrust Offset", MotorConfig.Z_THRUST_ZERO_SHIFT),
            ("Z Thrust Scaling", MotorConfig.Z_THRUST_SCALING),
        ]

        self.config_items = {key: val for key, val in config_items}

        for label_text, default_val in config_items:
            frame = ctk.CTkFrame(self.config_frame)
            frame.pack(fill="x", padx=10, pady=(5, 5))

            lbl = ctk.CTkLabel(frame, text=label_text, width=100)
            lbl.pack(side="left", padx=5)

            entry = ctk.CTkEntry(frame)
            entry.insert(0, default_val)
            entry.pack(side="right", expand=True, fill="x", padx=5)
            self.config_entries[label_text] = entry

        # Apply / Reset Buttons
        btn_frame = ctk.CTkFrame(self.config_frame)
        btn_frame.pack(pady=(10, 0))

        apply_btn = ctk.CTkButton(
            btn_frame, text="Apply Config", command=self._apply_config
        )
        apply_btn.pack(side="left", padx=5)

        reset_btn = ctk.CTkButton(
            btn_frame, text="Reset", fg_color="gray", command=self._reset_config
        )
        reset_btn.pack(side="left", padx=5)

    def _build_device_panel(self):
        title_label = ctk.CTkLabel(
            self.device_frame,
            text="Device Messages",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=5)

        # A text box for logs
        self.log_textbox = ctk.CTkTextbox(
            self.device_frame, width=300, height=400, wrap="word"
        )
        self.log_textbox.pack(padx=10, pady=5, expand=True, fill="both")

        # Buttons to clear or simulate a message
        btn_frame = ctk.CTkFrame(self.device_frame)
        btn_frame.pack(pady=(10, 0))

        clear_btn = ctk.CTkButton(
            btn_frame, text="Clear Log", fg_color="gray", command=self._clear_logs
        )
        clear_btn.pack(side="left", padx=5)

        test_msg_btn = ctk.CTkButton(
            btn_frame, text="Simulate Msg", command=self._simulate_msg
        )
        test_msg_btn.pack(side="left", padx=5)

    def append_log(self, message):
        """Append messages to the device messages Textbox."""
        self.log_textbox.insert("end", message)
        self.log_textbox.see("end")

    def _apply_config(self):
        """Collect config values and send to device"""

        config_values = {}
        for key, entry in self.config_entries.items():
            config_values[key] = entry.get()
        print("Applying Config:", config_values)
        # TODO: Send to device, save to file, etc.

    def _reset_config(self):
        """Resets config to last save (file)"""
        for key, entry in self.config_entries.items():
            entry.delete(0, "end")
            entry.insert(0, self.config_items[key])
        print("Config reset to last save.")

    def _clear_logs(self):
        self.log_textbox.delete("1.0", "end")

    def _simulate_msg(self):
        self.append_log("Simulated: Hello from Pico!\n")

    def append_log(self, message):
        self.log_textbox.insert("end", message)
        self.log_textbox.see("end")  # Auto-scroll

    def _poll_queue(self):
        try:
            # Keep reading until the queue is empty
            while True:
                msg_type, payload = self.data_queue.get_nowait()
                if msg_type == "device_response":
                    self.append_log(f"Response from device: {payload}\n")
                elif msg_type == "joystick_data":
                    axes, buttons = payload
                    self._update_axes_on_gui(axes)
                    self._update_buttons_on_gui(buttons)
        except queue.Empty:
            pass

        # Schedule to run again in 50ms
        self.after(50, self._poll_queue)

    def _update_axes_on_gui(self, axes):
        """
        Update the axis labels in the GUI.
        `axes` is a list or tuple of length 6:
          indices: 0..5
          pairs: (0,1) -> left stick, (2,3) -> right stick, (4,5) -> L2/R2
        """
        axis_pairs = [(0, 1), (2, 3), (4, 5)]
        for pair in axis_pairs:
            val1, val2 = axes[pair[0]], axes[pair[1]]
            label = self.axis_pair_labels[pair]  # The CTkLabel previously stored
            label.configure(text=f"[{val1:.2f}, {val2:.2f}]")

    def _update_buttons_on_gui(self, buttons):
        """
        Update the checkboxes to reflect pressed (1) or not pressed (0).
        `buttons` is a list or tuple of length 16 (0..15).
        """

        try:
            for idx, cb in self.checkbox_references.items():

                if len(buttons) == len(self.prev_buttons):
                    if buttons[idx] != self.prev_buttons[idx]:
                        if buttons[idx] == 1:
                            cb.select()
                        else:
                            cb.deselect()
                else:
                    if buttons[idx] == 1:
                        cb.select()
                    else:
                        cb.deselect()

            self.prev_buttons = buttons
        except Exception as e:
            print("Error in _update_buttons_on_gui:", e)

    def on_closing(self):
        """
        Called when the user closes the window.
        We set the stop_event so the worker thread can exit cleanly.
        """
        self.stop_event.set()  # signal the thread to stop
        self.destroy()


if __name__ == "__main__":
    print("Starting GUI...")
    app = Dashboard()
    print("GUI created, calling mainloop()...")
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    print("mainloop() has exited.")
