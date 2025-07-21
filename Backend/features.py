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
from dotenv import load_dotenv
load_dotenv()

AI_Name = "Luna"

# Use GOOGLE_API_KEY for compatibility with the official Gemini API SDK
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# for model in genai.list_models():
#     print(model.name)

con = sqlite3.connect('database.db')
cursor = con.cursor()

@eel.expose
def playAiSound():
    try:
        music_dir = "Frontend/assets/audio/N.E.C. Voice.mp3"
        playsound(music_dir)
    except Exception as e:
        print(f"Error playing AI sound: {str(e)}")

    
def openCommand(query):
    try:
        query = query.replace(AI_Name, "").replace("open", "").strip().lower()
        
        if not query:
            speak("Please specify what to open")
            return

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

def hotword():
    try:
        # Create a speech recognition object
        r = sr.Recognizer()

        # Loop for streaming
        while True:
            # Use the microphone as the audio source
            with sr.Microphone() as source:
                # Listen for audio
                audio = r.listen(source)
                try:
                    # Recognize the spoken word
                    spoken_word = r.recognize_google(audio, language="en-US")
                    # Check if the spoken word is "Luna" or a closely related pronunciation
                    if spoken_word.lower() in ["luna", "luuna", "louna", "loona", "lounaa", "loonaah", "lunaa"]:
                        print("Luna detected")
                        # Press the shortcut key win+j
                        pyautogui.keyDown("win")
                        pyautogui.press("j")
                        time.sleep(2)
                        pyautogui.keyUp("win")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results; {0}".format(e))
                
    except Exception as e:
        print("An error occurred: ", str(e))

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

