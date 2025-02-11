import time  # Fix: Import time module directly instead of from datetime
import pyttsx3
import speech_recognition as sr
import eel

def speak(text):
    try:
        text = str(text)
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 174)
        eel.DisplayMessage(text)
        engine.say(text)
        eel.receiverText(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {str(e)}")
        eel.DisplayMessage("Error in speech synthesis")

def takeCommand():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            eel.DisplayMessage("Listening...")
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

            print("Recognizing...")
            eel.DisplayMessage("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            eel.DisplayMessage(query)
            time.sleep(2)  # Fix: Now time.sleep will work
            return query.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""
    except Exception as e:
        print(f"Error in takeCommand: {str(e)}")
        return ""

@eel.expose
def allCommands(message=1):
    try:
        query = ""
        if message == 1:
            query = takeCommand()
            if query:  # Only send if query is not empty
                print("User Query:", query)
                eel.senderText(query)
        else:
            query = str(message).lower()
            eel.senderText(query)

        if not query:  # If query is empty, return early
            print("No command detected")
            return

        # Command processing
        if 'open' in query:
            from Backend.features import openCommand
            openCommand(query)
            
        elif 'youtube' in query:  # Fix: Changed condition to be more flexible
            from Backend.features import PlayYoutube
            PlayYoutube(query)
            
        elif any(cmd in query for cmd in ["send message", "phone call", "video call"]):
            from Backend.features import findContact, whatsApp
            contact_no, name = findContact(query)
            if contact_no != 0:
                if "send message" in query:
                    speak("what message to send")
                    message_text = takeCommand()
                    if message_text:  # Only proceed if we got a message
                        whatsApp(contact_no, message_text, 'message', name)
                elif "phone call" in query:
                    whatsApp(contact_no, "", 'call', name)
                else:
                    whatsApp(contact_no, "", 'video call', name)
        else:
            from Backend.features import chatBot
            chatBot(query)

    except Exception as e:
        print(f"Error in allCommands: {str(e)}")
        speak("I encountered an error processing that request")
    finally:
        eel.ShowHood()

