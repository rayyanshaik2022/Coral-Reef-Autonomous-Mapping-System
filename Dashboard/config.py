class SerialConfig:
  PORT = "COM3"
  BAUD_RATE = 115200
  TIMEOUT = 0.05 # Timeout does affect the data transfer rate between computer and Pico
  
class MotorConfig:
  THRUST_SCALING = 1000
  THRUST_ZERO_SHIFT = 3300 # The neutral value for X/Y-Thrust Motors
  Z_THRUST_SCALING = 1000
  Z_THRUST_ZERO_SHIFT = 5200 # The neutral value for Z-Thrust Motors