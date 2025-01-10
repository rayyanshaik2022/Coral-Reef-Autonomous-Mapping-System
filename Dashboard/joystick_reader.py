import pygame


class JoystickReader:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = []
        self._init_joysticks()

        # Store some relevant axes/buttons
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        self.l2_trigger = 0.0
        self.r2_trigger = 0.0
        self.buttons = [0] * 16

    def _init_joysticks(self):
        """Detect and initialize all joysticks."""
        count = pygame.joystick.get_count()
        self.joysticks = []
        for i in range(count):
            js = pygame.joystick.Joystick(i)
            js.init()
            print(f"Joystick {js.get_id()} connected: {js.get_name()}")
            self.joysticks.append(js)

    def update(self):
        """Call once per frame or loop iteration to update joystick values."""
        # Must call event.get() or event.pump() to allow Pygame to handle events
        pygame.event.pump()

        if not self.joysticks:
            return

        # For simplicity, read from the first joystick
        joystick = self.joysticks[0]
        axes_count = joystick.get_numaxes()
        buttons_count = joystick.get_numbuttons()

        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # Read axes
        if axes_count >= 6:
            self.left_stick_x = joystick.get_axis(0)
            self.left_stick_y = joystick.get_axis(1)
            self.right_stick_x = joystick.get_axis(2)
            self.right_stick_y = joystick.get_axis(3)
            self.l2_trigger = (joystick.get_axis(4) + 1) * 0.5
            self.r2_trigger = (joystick.get_axis(5) + 1) * 0.5

        if len(buttons) >= 16:
            self.x_btn, self.circle_btn, self.square_btn, self.triangle_btn = buttons[
                0:4
            ]

            self.share_btn, self.ps4_btn, self.options_btn = buttons[4:7]

            self.left_stick_btn, self.right_stick_btn = buttons[7:9]
            self.l1_btn, self.l2_btn = buttons[9:11]

            self.up_btn, self.down_btn, self.left_btn, self.right_btn = buttons[11:15]

            self.touchpad_btn = buttons[15]

        # Read buttons
        for i in range(min(buttons_count, 16)):
            self.buttons[i] = joystick.get_button(i)

    def cleanup(self):
        """Cleanup when shutting down."""
        pygame.quit()

    def print_values(self, verbose=False):
        """Pretty print all (axis-corrected) values"""

        print(f"Left Stick X: <{self.left_stick_x}>")
        print(f"Left Stick Y: <{self.left_stick_y}>")
        print(f"Right Stick X: <{self.right_stick_x}>")
        print(f"Right Stick Y: <{self.right_stick_y}>")
        print(f"L2 Trigger: <{self.l2_trigger}>")
        print(f"R2 Trigger: <{self.r2_trigger}>")
