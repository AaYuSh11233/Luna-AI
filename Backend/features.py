import os
import re
from shlex import quote
import sqlite3
import struct
import subprocess
import webbrowser
from playsound import playsound
import eel
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
from Backend.command import speak
import google.generativeai as genai
import time
import speech_recognition as sr
import shutil
import winshell
import numpy as np
from dotenv import load_dotenv
load_dotenv()

AI_Name = "Vortex"

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model_name = os.getenv("GEMINI_MODEL_NAME")
model = genai.GenerativeModel(model_name)

con = sqlite3.connect('database.db')
cursor = con.cursor()

@eel.expose
def playAiSound():
    try:
        music_dir = "Frontend/assets/audio/N.E.C. Voice.mp3"
        playsound(music_dir)
    except Exception as e:
        print(f"Error playing AI sound: {str(e)}")

    
def list_desktop_apps():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    return [f for f in os.listdir(desktop_path) if os.path.isfile(os.path.join(desktop_path, f))]

def list_start_menu_apps():
    start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
    apps = []
    for root, dirs, files in os.walk(start_menu):
        for file in files:
            if file.endswith('.lnk'):
                apps.append(file[:-4].lower())
    return apps

def open_browser_by_name(name):
    browsers = {
        "chrome": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "edge": r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "firefox": r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"
    }
    for key, path in browsers.items():
        if key in name:
            if os.path.exists(path):
                os.startfile(path)
                return True
    return False

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        speak(f"Folder created at {path}")
    except Exception as e:
        speak(f"Failed to create folder: {str(e)}")

def create_file(path, content=""):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        speak(f"File created at {path}")
    except Exception as e:
        speak(f"Failed to create file: {str(e)}")

def write_code_to_file(path, code):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        speak(f"Code written to {path}")
    except Exception as e:
        speak(f"Failed to write code: {str(e)}")

def open_recycle_bin():
    try:
        os.system("start shell:RecycleBinFolder")
        speak("Recycle bin opened")
    except Exception as e:
        speak(f"Failed to open recycle bin: {str(e)}")

def restore_recycle_bin():
    try:
        for item in winshell.recycle_bin():
            item.restore()
        speak("All items restored from recycle bin")
    except Exception as e:
        speak(f"Failed to restore items: {str(e)}")

def empty_recycle_bin():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        speak("Recycle bin emptied")
    except Exception as e:
        speak(f"Failed to empty recycle bin: {str(e)}")

# Fallback URLs for common sites
FALLBACK_URLS = {
    "github": "https://github.com",
    "canva": "https://canva.com",
    "pinterest": "https://pinterest.com",
    "chatgpt": "https://chat.openai.com",
    "youtube": "https://youtube.com"
}

# Common app install paths
COMMON_APPS = {
    "discord": r"C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\Update.exe",
    "valorant": r"C:\\Riot Games\\Riot Client\\RiotClientServices.exe",
    "oracle virtualbox": r"C:\\Program Files\\Oracle\\VirtualBox\\VirtualBox.exe"
}

def open_common_app(name):
    for app, path in COMMON_APPS.items():
        if app in name:
            resolved_path = os.path.expandvars(path)
            if os.path.exists(resolved_path):
                os.startfile(resolved_path)
                speak(f"Opening {app}")
                return True
    return False

def close_window():
    try:
        import pyautogui
        pyautogui.hotkey('alt', 'f4')
        speak("Closed the active window")
    except Exception as e:
        speak(f"Failed to close window: {str(e)}")

def close_app_by_name(name):
    try:
        os.system(f'taskkill /im {name}.exe /f')
        speak(f"Closed {name}")
    except Exception as e:
        speak(f"Failed to close {name}: {str(e)}")

def notepad_write_gemini(text):
    try:
        os.system('start notepad')
        time.sleep(1.5)
        import pyperclip, pyautogui
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        speak("Draft pasted into Notepad")
    except Exception as e:
        speak(f"Failed to write in Notepad: {str(e)}")

def chain_vs_code_folder_files_code(folder_name, files_and_code):
    try:
        folder_path = os.path.join(os.getcwd(), folder_name)
        os.makedirs(folder_path, exist_ok=True)
        for fname, code in files_and_code.items():
            fpath = os.path.join(folder_path, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(code)
        os.system(f'start code "{folder_path}"')
        speak(f"Created folder {folder_name} with files and opened in VS Code")
    except Exception as e:
        speak(f"Failed to chain VS Code folder/files: {str(e)}")

def youtube_playback_control(action):
    # Stub: Selenium-based control can be added here
    speak(f"YouTube {action} control is not yet implemented.")

# Update openCommand to support new automations and chaining

def openCommand(query):
    try:
        query = query.replace(AI_Name, "").replace("open", "").strip().lower()
        if not query:
            speak("Please specify what to open")
            return
        # Empty recycle bin
        if "empty recycle bin" in query or "delete recycle bin" in query:
            empty_recycle_bin()
            return
        # Close window/app
        if "close window" in query:
            close_window()
            return
        if query.startswith("close "):
            app_name = query.replace("close ", "").strip()
            close_app_by_name(app_name)
            return
        # Command chaining: VS Code, folder, files, code
        if "vs code" in query and "create folder" in query and "create file" in query and "write code" in query:
            # Example: open vs code, create folder test, create file a.py, b.py, write code
            import re
            folder_match = re.search(r'create folder ([\w\-]+)', query)
            file_matches = re.findall(r'create file ([\w\.]+)', query)
            code_matches = re.findall(r'write code ([\w\.]+)', query)
            files_and_code = {}
            for fname in file_matches:
                # For demo, use Hello World code
                files_and_code[fname] = "print('Hello from ' + __file__)"
            if folder_match:
                chain_vs_code_folder_files_code(folder_match.group(1), files_and_code)
            else:
                speak("Please specify folder name for chaining.")
            return
        # Notepad + Gemini
        if "notepad" in query and ("write" in query or "mail" in query or "email" in query):
            # Use Gemini to generate text
            prompt = query.replace("notepad", "").replace("write", "").replace("mail", "").replace("email", "").strip()
            text = chatBot(prompt)
            notepad_write_gemini(text)
            return
        # YouTube playback controls
        if "youtube" in query and any(x in query for x in ["pause", "play", "next"]):
            if "pause" in query:
                youtube_playback_control("pause")
            elif "play" in query:
                youtube_playback_control("play")
            elif "next" in query:
                youtube_playback_control("next")
            return
        # Improved app detection
        if open_common_app(query):
            return
        # Desktop/Start Menu app
        desktop_apps = list_desktop_apps()
        start_menu_apps = list_start_menu_apps()
        if query in desktop_apps or query in start_menu_apps:
            try:
                os.startfile(query)
                speak(f"Opening {query}")
                return
            except Exception as e:
                speak(f"Failed to open {query}: {str(e)}")
                return
        # Browser
        if open_browser_by_name(query):
            speak(f"Opening {query} browser")
            return
        # Fallback for common websites
        for key, url in FALLBACK_URLS.items():
            if key in query:
                speak(f"Opening {key}")
                webbrowser.open(url)
                return
        # Recycle bin
        if "recycle bin" in query:
            open_recycle_bin()
            return
        if "restore recycle bin" in query or "restore deleted" in query:
            restore_recycle_bin()
            return
        # VS Code automation
        if "vs code" in query or "visual studio code" in query:
            os.system("start code")
            speak("Opening Visual Studio Code")
            return
        # Folder creation
        if "create folder" in query:
            folder_name = query.replace("create folder", "").strip()
            if not folder_name:
                speak("Please specify folder name")
            else:
                create_folder(os.path.join(os.getcwd(), folder_name))
            return
        # File creation
        if "create file" in query:
            file_name = query.replace("create file", "").strip()
            if not file_name:
                speak("Please specify file name")
            else:
                create_file(os.path.join(os.getcwd(), file_name))
            return
        # Write code
        if "write code" in query:
            parts = query.split("write code")
            if len(parts) > 1:
                file_name = parts[1].strip()
                # For demo, write a hello world
                code = "print('Hello, World!')"
                write_code_to_file(os.path.join(os.getcwd(), file_name), code)
            else:
                speak("Please specify file name to write code")
            return
        # Fallback to previous logic
        # First check system commands
        cursor.execute('SELECT path FROM sys_command WHERE name = ?', (query,))
        result = cursor.fetchone()
        if result:
            speak(f"Opening {query}")
            os.startfile(result[0])
            return
        # Then check web commands
        cursor.execute('SELECT url FROM web_command WHERE name = ?', (query,))
        result = cursor.fetchone()
        if result:
            speak(f"Opening {query}")
            webbrowser.open(result[0])
            return
        # If not found in database, try system command
        speak(f"Opening {query}")
        try:
            os.system(f'start {query}')
        except:
            speak(f"Could not find {query}")
    except Exception as e:
        print(f"Error in openCommand: {str(e)}")
        speak("Error opening the application")
    
def PlayYoutube(query):
    try:
        search_term = extract_yt_term(query)
        if search_term:
            speak(f"Playing {search_term} on YouTube")
            kit.playonyt(search_term)
        else:
            speak("Could not understand what to play on YouTube")
    except Exception as e:
        print(f"Error playing YouTube: {str(e)}")
        speak("Error playing YouTube video")

def extract_yt_term(command):
    try:
        # Remove common phrases
        command = command.lower()
        command = command.replace("play", "")
        command = command.replace("on youtube", "")
        command = command.replace("youtube", "")
        
        # Clean up the search term
        search_term = command.strip()
        if search_term:
            return search_term
        return None
    except Exception as e:
        print(f"Error extracting YouTube term: {str(e)}")
        return None

def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string

def hotword(queue):
    try:
        # Path to your custom model
        keyword_path = "Backend/models/Vortex_ai.ppn"
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for 'Vortex'...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = np.frombuffer(pcm, dtype=np.int16)
            result = porcupine.process(pcm)
            if result >= 0:
                print("Vortex detected!")
                queue.put("wakeword_detected")
                # Optionally play a sound or give feedback here
                time.sleep(1)  # Prevent spamming
    except Exception as e:
        print("An error occurred: ", str(e))
    finally:
        if 'audio_stream' in locals():
            audio_stream.close()
        if 'pa' in locals():
            pa.terminate()
        if 'porcupine' in locals():
            porcupine.delete()

# Whatsapp Message Sending
def findContact(query):
    
    
    words_to_remove = [AI_Name, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name

    # Encode the message for URL
    encoded_message = quote(message)

    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
def chatBot(query):
    try:
        # Generate response using Gemini
        response = model.generate_content(query)
        
        # Clean and format the response
        formatted_response = response.text.strip()
        # Remove multiple spaces
        formatted_response = ' '.join(formatted_response.split())
        # Keep only essential punctuation
        formatted_response = re.sub(r'[^\w\s,.!?]', '', formatted_response)
        
        print(formatted_response)
        speak(formatted_response)
        return formatted_response
        
    except Exception as e:
        print(f"Error in chatBot: {str(e)}")
        error_message = "I apologize, I'm having trouble processing that request. Please try again."
        speak(error_message)
        return error_message

