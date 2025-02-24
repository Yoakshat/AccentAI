from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from elevenlabs import save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment;
from dotenv import load_dotenv;
import os

app = Flask(__name__)
load_dotenv()

def create_ai_client(): 
    
    client = OpenAI(
        api_key=os.getenv("OPEN_AI_KEY"), 
    )
    return client

def create_eleven_client(): 
    # create the client
    client = ElevenLabs(
        api_key=os.getenv("ELEVEN_API_KEY")
    )
    return client

# give_feedback
@app.route('/process_input', methods=['POST'])
def process_input():
    data = request.get_json()
    print(data)

    user_input = data['input']
    sent = data['sentence']

    help_prompt = "In the sentence: " + "\"" + sent + "\" I am facing these \
        pronunciation difficulties: " + user_input + ". Briefly help me." 
    client = create_ai_client()


    # Here, we call on ChatGPT to help
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": help_prompt}]
    )
    
    chatgpt_response = response.choices[0].message.content
    # using chatGPT and elevensAI together
    gen_audio(chatgpt_response, "static/voice.mp3")
    

    # print(chatgpt_response)
    
    return '',204

# sentence next
@app.route('/next_sentence', methods=['POST'])
def next_sentence():
    data = request.get_json()
    sent = gen_sentence(data['lang'])
    
    # we also have to generate new audio
    gen_audio(sent)
    return jsonify(sent)

# come up with a sentence in language 
def gen_sentence(lang): 
    client = create_ai_client() 
    prompt = "Tell me a new sentence in " + lang \
          + " but in English alphabet and put [] brackets around it"

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user", 
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo",
    )

    new_sentence = response.choices[0].message.content
    
    # return new_sentence
    return new_sentence.split("[")[1].split("]")[0]


# generate multilingual audio 
def gen_audio(sentence, file="static/output.mp3"): 
    client = create_eleven_client()
    audio = client.generate(
        text = sentence, 
        voice = "Rachel", 
        model="eleven_multilingual_v2"
    )
    save(audio, file)

    

    audio = AudioSegment.from_file(file)
    
    # Increase volume by 5 dB
    louder_audio = audio + 15  # Increase volume (dB)
    louder_audio.export(file, format="mp3")


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle language selection and redirect to a new page
@app.route('/select_language')
def select_language():
    # Get the selected language from the URL parameters (query string)
    selected_language = request.args.get('lang')
    sent = gen_sentence(selected_language)
    # Generate accent-audio of sentence
    gen_audio(sent)



    # now render the new page with the argument
    return render_template('language_selected.html', language=selected_language, sent=sent)


# Running the app
if __name__ == '__main__':
    app.run(debug=True)
