import boto3
import subprocess
import requests
import json
import os
import threading

with open('../.openapi_credentials') as f:
    contents = f.read()

for line in contents.split('\n'):
    if line.startswith('api_key='):
        API_KEY = line[len('api_key='):]
    elif line.startswith('bot_token='):
        BOT_TOKEN = line[len('api_secret='):]

# Open api autentication files in ~/.openapi_credentials
# api_key=
# api_secret=None

# Amazon Poly credentials in ~/.aws/credentials
# [default]
# aws_access_key_id = 
# aws_secret_access_key = 
# region=us-east-1

# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
MODEL = 'text-davinci-003'

# Defining the bot's personality using adjectives
BOT_PERSONALITY = 'Resuma em Português do Brasil, e depois adicione ponto final em todas as linhas. \n'
# Define Prompt file
PROMPT_FILE = 'prompt.txt'
#Define response file
RESPONSE_FILE = 'responseGPT.txt'

MP3_PLAYER = 'afplay -r 1.5'

def polly_speak(response_file):
    # Crie uma instância do cliente da API Polly
    polly_client = boto3.client('polly')

    # Defina as configurações de voz e linguagem
    voice_id = 'Camila'
    language_code = 'pt-BR'
    engine = 'neural'


    # Defina o texto que será sintetizado em fala
    with open(response_file, "r") as file:
        text = file.read()

    # Use o método synthesize_speech() da API Polly para sintetizar o texto em fala
    response = polly_client.synthesize_speech(
        OutputFormat='mp3',
        Text=text,
        VoiceId=voice_id,
        LanguageCode=language_code,
        Engine=engine
        )

    # Salve o áudio sintetizado em um arquivo mp3
    with open('output.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
        f.close()

    mp3_file = "output.mp3"
    command = MP3_PLAYER + " " + mp3_file
    subprocess.run(command, shell=True)

# 2a. Function that gets the response from OpenAI's chatbot
def open_ai(prompt):
    # Make the request to the OpenAI API
    response = requests.post(
        'https://api.openai.com/v1/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model': MODEL, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 3500}
    )

    result = response.json()
    final_result = ''.join(choice['text'] for choice in result['choices'])
    return final_result

# Run the main function
if __name__ == "__main__":
    with open(PROMPT_FILE, "r") as file:
        prompts = file.read()

    with open(RESPONSE_FILE, "w") as file:
        file.write("")
    
    promptList = prompts.split('\n') 

    for prompt in promptList:
        prompt = prompt.replace('\n', '. ')
        bot_response = open_ai(f"{BOT_PERSONALITY}{prompt}")

        with open(RESPONSE_FILE, "a") as file:
            file.write(bot_response)
        bot_response = ""

    polly_speak(RESPONSE_FILE)
