import os
import eel
import time
from Backend.features import *
from Backend.command import *

def start(queue=None):
    eel.init('Frontend')
    playAiSound()
    os.system('start chrome.exe --app="http://localhost:8000/index.html"')
    # Start eel in a non-blocking way
    import threading
    eel_thread = threading.Thread(target=eel.start, args=('index.html',), kwargs={'mode': 'none', 'host': 'localhost', 'block': False})
    eel_thread.start()
    # Main loop: check for wakeword
    if queue is not None:
        while True:
            try:
                if not queue.empty():
                    msg = queue.get()
                    if msg == 'wakeword_detected':
                        print('Wakeword detected! Activating assistant...')
                        playAiSound()
                        # Optionally, trigger UI or start listening for a command here
                        # For example, call allCommands() to start voice command
                        allCommands()
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
    else:
        eel_thread.join()
