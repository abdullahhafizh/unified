import keyboard

def on_key_event(event):
    # Check if the event is a key press event        
    # Print the name of the pressed key
    print("Pressed key:", event.name)


if __name__ == '__main__':
    # Set up the keyboard event listener
    keyboard.on_press(on_key_event)

    # Keep the script running to continue listening for events
    keyboard.wait('esc')