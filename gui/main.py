import customtkinter as ctk
import tkinter as tk

# A mock function to simulate updating the PS4 axes and button states.
# Replace this with your real joystick reading code.
def update_ps4_inputs():
    # Return 6 axes in [-1..1], 16 buttons in [0..1] (mock)
    axes = [0.0, -0.5, 1.0, 0.2, -1.0, 0.25]
    buttons = [1 if i % 2 == 0 else 0 for i in range(16)]
    return axes, buttons


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CRAMS Device Dashboard")
        self.geometry("1600x800")

        # === Theme / Appearance ===
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # === Main Layout (3 columns, 1 row) ===
        # You can adjust row/column weights as needed
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

        # Build sub-sections
        self._build_ps4_panel()
        self._build_config_panel()
        self._build_device_panel()

        # Start a periodic update of the PS4 inputs
        self._update_loop()

    # -------------------------------------------------------------------------
    # Panel A: PS4 Inputs (Grouped Axes and Buttons with Indicators)
    # -------------------------------------------------------------------------
    def _build_ps4_panel(self):
        title_label = ctk.CTkLabel(
            self.ps4_frame,
            text="PS4 Controller State",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=5)

        # === Axes Grouping ===
        axes_frame = ctk.CTkFrame(self.ps4_frame)
        axes_frame.pack(fill="x", padx=10, pady=(0, 10))

        axes_title = ctk.CTkLabel(
            axes_frame,
            text="Joysticks & Triggers:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        axes_title.pack(anchor="w", padx=10, pady=5)

        self.axis_pair_labels = {}
        axis_pairs = [(0,1), (2,3), (4,5)]
        axes_names = ["Left Stick", "Right Stick", "L2/R2 Triggers"]
        for pair, name in zip(axis_pairs, axes_names):
            pair_frame = ctk.CTkFrame(axes_frame)
            pair_frame.pack(fill="x", padx=10, pady=5)

            pair_label = ctk.CTkLabel(
                pair_frame, 
                text=f"{name}:", 
                width=100, 
                anchor="w"
            )
            pair_label.pack(side="left", padx=(5, 0))

            value_label = ctk.CTkLabel(
                pair_frame, 
                text=f"[{0.0}, {0.0}]", 
                anchor="w"
            )
            value_label.pack(side="right", padx=(0, 5))

            # Store for updating in _update_loop
            self.axis_pair_labels[pair] = value_label

        # === Button Grouping with Indicators ===
        btn_frame = ctk.CTkFrame(self.ps4_frame)
        btn_frame.pack(fill="x", padx=10, pady=0)

        btn_title = ctk.CTkLabel(
            btn_frame,
            text="Buttons (Grouped with Indicators):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_title.pack(anchor="w", padx=10, pady=(10, 5))

        # We define logical groups for the 16 buttons:
        # Face Buttons (0..3), System (4..6), Stick Clicks (7..8),
        # Shoulders (9..10), D-Pad (11..14), Touchpad (15)
        self.button_groups = {
            "Face Buttons": [
                ("X", 0),
                ("Circle", 1),
                ("Square", 2),
                ("Triangle", 3),
            ],
            "System Buttons": [
                ("Share", 4),
                ("PS4", 5),
                ("Options", 6),
            ],
            "Stick Clicks": [
                ("L Stick", 7),
                ("R Stick", 8),
            ],
            "Shoulders": [
                ("L1", 9),
                ("L2", 10),
            ],
            "D-Pad": [
                ("Up", 11),
                ("Down", 12),
                ("Left", 13),
                ("Right", 14),
            ],
            "Touchpad": [
                ("Touchpad", 15),
            ],
        }

        # We'll store references to each checkbox so we can update them
        self.checkbox_references = {}

        for group_name, items in self.button_groups.items():
            group_frame = ctk.CTkFrame(btn_frame)
            group_frame.pack(fill="x", padx=10, pady=5)

            group_label = ctk.CTkLabel(
                group_frame,
                text=group_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            group_label.pack(anchor="w", padx=5, pady=(5, 2))

            row_frame = ctk.CTkFrame(group_frame)
            row_frame.pack(fill="x", padx=5, pady=5)

            for (label_text, button_idx) in items:
                cb = ctk.CTkCheckBox(
                    row_frame,
                    text=label_text,
                    state="disabled"  # user can't toggle, only for display
                )
                cb.pack(side="left", padx=(0, 10))
                self.checkbox_references[button_idx] = cb

    # -------------------------------------------------------------------------
    # Panel B: Config Editor
    # -------------------------------------------------------------------------
    def _build_config_panel(self):
        title_label = ctk.CTkLabel(
            self.config_frame,
            text="Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=5)

        # Example config fields (you can add more as needed)
        self.config_entries = {}

        config_items = [
            ("Motor Offset", "3300"),
            ("Motor Scaling", "1000"),
            ("Z Motor Offset", "5200"),
            ("Z Motor Scaling", "1000"),
        ]

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

    # Example: Called when "Apply Config" is pressed
    def _apply_config(self):
        # Normally, you'd collect the config values and send them to your device
        config_values = {}
        for key, entry in self.config_entries.items():
            config_values[key] = entry.get()
        print("Applying Config:", config_values)
        # TODO: Send to device, save to file, etc.

    # Example: Called when "Reset" is pressed
    def _reset_config(self):
        for key, entry in self.config_entries.items():
            entry.delete(0, "end")
            entry.insert(0, "0")
        print("Config reset to zeros (demo).")

    # -------------------------------------------------------------------------
    # Panel C: Device Messages / Logs
    # -------------------------------------------------------------------------
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

    def _clear_logs(self):
        self.log_textbox.delete("1.0", "end")

    def _simulate_msg(self):
        self.append_log("Simulated: Hello from Pico!\n")

    def append_log(self, message):
        self.log_textbox.insert("end", message)
        self.log_textbox.see("end")  # Auto-scroll

    # -------------------------------------------------------------------------
    # Periodic Update Loop (e.g., for PS4 Inputs)
    # -------------------------------------------------------------------------
    def _update_loop(self):
        # Replace this with real joystick reading logic
        axes, buttons = update_ps4_inputs()

        # Update each axis pair label
        for (a1, a2), label in self.axis_pair_labels.items():
            val1, val2 = axes[a1], axes[a2]
            label.configure(text=f"[{val1:.2f}, {val2:.2f}]")

        # Update checkboxes for buttons
        for idx, cb in self.checkbox_references.items():
            if buttons[idx] == 1:
                cb.select()
            else:
                cb.deselect()

        # Re-run after 100 ms (adjust as needed)
        self.after(100, self._update_loop)


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
