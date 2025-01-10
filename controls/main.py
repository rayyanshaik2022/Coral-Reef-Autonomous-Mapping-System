import time
import threading


def device_worker_loop(stop_event, data_queue, joystick, device, verbose=False):
    """
    Runs in a background thread. Loops until `stop_event` is set.
      - Reads joystick
      - Sends data to device
      - Reads response
      - Publishes relevant data to `data_queue` for the GUI
    """
    while not stop_event.is_set():
        # 1) Update joystick data
        joystick.update()

        # 2) Build our data payload
        left_thrust_power = int(
            joystick.r2_trigger * 1000 * min(1, 1 - joystick.left_stick_x) + 3300
        )
        right_thrust_power = int(
            joystick.r2_trigger * 1000 * min(1, 1 + joystick.left_stick_x) + 3300
        )
        z_thrust_power = int(joystick.right_stick_y * 1000 + 5200)

        data_to_send = {
            "left_thrust_power": left_thrust_power,
            "right_thrust_power": right_thrust_power,
            "z_thrust_power": z_thrust_power,
        }

        # 3) If device is connected, send data and read response
        if device.is_connected():
            device.send_data(data_to_send)
            response = device.read_response()
            if response and verbose:
                # Put the response in the queue for the GUI
                data_queue.put(("device_response", response))

        # 4) Also push the current joystick data to the queue so the GUI can update
        # We'll pass axes and buttons
        axes_data = [
            joystick.left_stick_x,
            joystick.left_stick_y,
            joystick.right_stick_x,
            joystick.right_stick_y,
            joystick.l2_trigger,
            joystick.r2_trigger,
        ]
        buttons_data = joystick.buttons[:]

        data_queue.put(("joystick_data", (axes_data, buttons_data)))

        # 5) Throttle the loop
        time.sleep(0.01)

    # Cleanup
    joystick.cleanup()
    device.disconnect()
    print("Worker thread exiting cleanly.")


def start_worker(joystick, device, data_queue, verbose=False):
    """
    Spawns the worker thread, returns (thread, stop_event).
    """
    stop_event = threading.Event()
    thread = threading.Thread(
        target=device_worker_loop,
        args=(stop_event, data_queue, joystick, device, verbose),
        daemon=True,
    )
    thread.start()
    return thread, stop_event
