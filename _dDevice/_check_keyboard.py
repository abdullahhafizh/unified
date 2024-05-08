import keyboard
# import time

chars = ''

def on_key_event(event):
    global chars
    # Check if the event is a key press event        
    # Print the name of the pressed key
    # print("Pressed key:", event.name)
    if (event.name == 'enter'):
        print(chars)
        reset_state()
    if len(event.name) == 1:
        chars += event.name


def reset_state():
    global chars
    chars = ''

if __name__ == '__main__':
    keyboard.on_press(on_key_event)
    keyboard.wait()
