import serial

def send_serial(baud_rate, port, number, zero_shift=3300):
    with serial.Serial(port, baud_rate, timeout=1) as ser:
        try:
              # Send the number to the Pico
              ser.write(f"{int(number + zero_shift)}\n".encode('utf-8'))
              
              # Wait for a response from the Pico
              response = ser.readline().decode('utf-8').strip()
              if response:
                  print(f"Response from Pico: {response}")
        except:
            print("Error sending serializationt to pico")

if __name__ == "__main__":
  # Replace this with the correct serial port for your USB-to-TTL adapter
  #port = '/dev/tty.usbserial-A50285BI'  # Example: '/dev/tty.usbserial-1410'
  port = "COM3" # For windows usb devices
  baud_rate = 115200

  with serial.Serial(port, baud_rate, timeout=1) as ser:
      print("Type an integer to send to the Pico. Type 'exit' to quit.")
      
      while True:
          # Get user input from the terminal
          user_input = input("Enter a number: ")
          
          if user_input.lower() == 'exit':  # Exit the program
              print("Exiting...")
              break
          
          try:
              # Ensure the input is a valid integer
              int(user_input)
              
              # Send the number to the Pico
              ser.write(f"{user_input}\n".encode('utf-8'))
              
              # Wait for a response from the Pico
              response = ser.readline().decode('utf-8').strip()
              if response:
                  print(f"Response from Pico: {response}")
          except ValueError:
              print("Please enter a valid integer!")