import os
import eel

from Backend.features import *
from Backend.command import *

def start():
    eel.init('Ui')
    playAiSound()
    os.system('start chrome.exe --app="http://localhost:8000/index.html"')
    eel.start('index.html', mode='none', host='localhost', block=True)
