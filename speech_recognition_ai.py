import requests
import pyttsx3
import speech_recognition as sr
from bs4 import BeautifulSoup
from gpt4all import GPT4All

# Text to speech and voice recognition engine
recog = sr.Recognizer()
engine = pyttsx3.init()

# Rate of speech
rate = engine.getProperty("rate")
engine.setProperty("rate", 200)

# Volume control
volume = engine.getProperty("volume")
engine.setProperty("volume", 1.0)

# Voice type
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

# Weather Scraper Credit to:
# https://www.geeksforgeeks.org/how-to-extract-weather-data-from-google-in-python/
try:

    # Change to your city
    city = "denton"

    # Creating URL and making requests instance
    url = "https://www.google.com/search?q=" + "weather" + city
    web = requests.get(url)

    # Check for bad status
    web.raise_for_status()

    html = web.content

    # Getting raw data using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Extracting the temperature
    temp = soup.find("div", attrs={"class": "BNeawe iBp4i AP7Wnd"}).text

    # Extracting the time and sky description
    str_ = soup.find("div", attrs={"class": "BNeawe tAd8D AP7Wnd"}).text
    data = str_.split("\n")
    time = data[0]
    sky = data[1]

    # Getting all div tags with the specific class name
    listdiv = soup.findAll("div", attrs={"class": "BNeawe s3v9rd AP7Wnd"})

    # Extracting other required data
    strd = listdiv[5].text
    pos = strd.find("Wind")
    other_data = strd[pos:]

# Exception Handling
except requests.exceptions.HTTPError as http_err:
    print(f"Error gathering weather data {http_err}")
except Exception as err:
    print(f"Error gathering weather data {err}")
    other_data = data = sky = time = temp = pos = "error"

# System Prompt for chatbot. Configure however you'd like the AI to behave.
# Note:(Leave the part about weather data intact in order to function properly)
system_prompt = f"""
                 You're a helpful AI assistant.
                 Please keep responses clear and concise.
                 Try to remain very professional regardless of what you're prompted by. 
                 You have access to current weather data which you can provide upon request.
                 Do not mention the weather data unless it is explicitely asked for
                 {other_data}{data}{sky}{time}{temp}{pos}
                 """

# Model initialization
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", device="cuda")
prompt_template = "### Instruction:\n{0}\n### Response:\n"

with model.chat_session(prompt_template=prompt_template, system_prompt=system_prompt):
    # Wake word loop
    while True:

        # Get User In via speech recognition
        try:
            with sr.Microphone() as source2:
                # Set wake word in all lowercase
                wake_word = "hello"

                # Adjust for surrounding noise level
                recog.adjust_for_ambient_noise(source2, duration=0.2)

                # Listening for wake word
                print("Listening for wake word...")

                audio2 = recog.listen(source2)

                # Use google to recognize wake word
                initail_command = recog.recognize_google(audio2)
                initail_command = initail_command.lower()

                # Checking for wake word
                if wake_word in initail_command:
                    # User Input & Response loop
                    while True:

                        # Listening for user input
                        print("Listening...")
                        audio3 = recog.listen(
                            source2,
                            phrase_time_limit=10,
                        )

                        # Use google to recognize audio
                        user_input = recog.recognize_google(audio3)
                        user_input = user_input.lower()

                        # Print user input
                        print(f"You: {user_input}")

                        # Check for stop command
                        if "stop listening" in user_input:
                            print("System: Goodbye")
                            # Trigger text to speech
                            engine.say("Goodbye")
                            engine.runAndWait()
                            break

                        # Generate Response
                        response = model.generate(
                            user_input, temp=0.7, top_k=40, top_p=0.4, min_p=0.1
                        )

                        # Print response
                        print(f"System: {response}")

                        # Trigger text to speech
                        engine.say(response)
                        engine.runAndWait()

        # Exception Handling
        except sr.RequestError as e:
            print(f"Could not request {e}")
        except sr.UnknownValueError:
            print("An unknown error occurred")
        except sr.WaitTimeoutError:
            print("Timeout")
