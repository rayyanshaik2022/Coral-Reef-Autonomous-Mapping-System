import serial
import json


class DeviceCommunicator:
    def __init__(self, port="COM3", baud_rate=115200, timeout=0.05):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        """Open the serial connection."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            print(f"Connected to device on {self.port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
            self.ser = None

    def disconnect(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")
        self.ser = None

    def is_connected(self):
        """Check if the serial device is ready."""
        return self.ser is not None and self.ser.is_open

    def send_data(self, data_dict):
        """Send a dictionary to the device as JSON, followed by a newline."""
        if not self.is_connected():
            return
        try:
            json_string = json.dumps(data_dict) + "\n"
            self.ser.write(json_string.encode("utf-8"))
        except Exception as e:
            print(f"Error sending data: {e}")

    def read_response(self):
        """Non-blocking read for a line from the device."""
        if not self.is_connected():
            return None
        try:
            line = self.ser.readline().decode("utf-8").strip()
            return line if line else None
        except Exception as e:
            print(f"Error reading data: {e}")
            return None
