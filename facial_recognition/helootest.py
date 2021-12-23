import speech_recognition as sr 
def takeCommand():
    #It takes microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as mic:
        print("Listening...")
        r.adjust_for_ambient_noise(mic)
        audio = r.listen(mic, 4)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception:
        print("Say that again please...")
        return "None"
    return query
def check(code):
    if (code=="hello"):
        print("yes")


a = takeCommand()
check(a)