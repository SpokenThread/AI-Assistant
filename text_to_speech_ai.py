import requests
import pyttsx3
from bs4 import BeautifulSoup
from gpt4all import GPT4All

# Text to speech engine
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

# Weather Scraper Credit to https://www.geeksforgeeks.org/how-to-extract-weather-data-from-google-in-python/
# Creating URL and making requests instance

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
# Note: (Leave the part about weather data intact if you want that to function properly)
system_prompt = f"""
                 You're a helpful AI assistant.
                 Please keep responses clear and concise.
                 Try to remain very professional regardless of what you're prompted by. 
                 You have access to current weather data which you can provide upon request.
                 Do not mention the weather data unless it is explicitely asked for{other_data}{data}{sky}{time}{temp}{pos}
                """

# AI model initalization
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", device="cuda")
prompt_template = "### Instruction:\n{0}\n### Response:\n"

with model.chat_session(prompt_template=prompt_template, system_prompt=system_prompt):
    while True:

        # Get User In
        user_input = input("You: ")

        # Check for exit command
        if user_input == "exit":
            break

        # Generate response
        response = model.generate(user_input, temp=0.7, top_k=40, top_p=0.4, min_p=0.1)

        # Print response
        print(f"System: {response}")

        # Trigger text to speech
        engine.say(response)
        engine.runAndWait()
