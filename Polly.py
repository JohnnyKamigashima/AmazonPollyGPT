import boto3
import subprocess
import requests
import json
import os
import threading
import telebot
import  sys

with open('../.openapi_credentials') as f:
    contents = f.read()

for line in contents.split('\n'):
    if line.startswith('api_key='):
        API_KEY = line[len('api_key='):]
    elif line.startswith('bot_token='):
        BOT_TOKEN = line[len('bot_token='):]

# Open api autentication files in ~/.openapi_credentials
# api_key=
# api_secret=None

# Amazon Poly credentials in ~/.aws/credentials
# [default]
# aws_access_key_id = 
# aws_secret_access_key = 
# region=us-east-1

# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
MODEL = 'gpt-3.5-turbo'

# Defining the bot's personality using adjectives
BOT_PERSONALITY = 'Resuma o texto para Português do Brasil: '

#Define response file
RESPONSE_FILE = './responses/responseGPT'
CHAT_ID= "-1001899083389"
QUEUE_FILE = 'queue.txt'
MP3_PLAYER = 'afplay -r 1.5'

# Define Prompt file
if len(sys.argv) < 2:
    print("Não foi fornecido argumento, usando lista queue.txt")
    with open(QUEUE_FILE, 'r') as file:
            PROMPT_FILE = file.readline().strip()

    with open(QUEUE_FILE, 'r') as file:
        lines = file.readlines()

    with open(QUEUE_FILE, 'w') as file:
        file.writelines(lines[1:])
else:
    PROMPT_FILE = sys.argv[1]

def polly_speak(response_file):
    # Crie uma instância do cliente da API Polly
    polly_client = boto3.client('polly')

    # Defina as configurações de voz e linguagem
    voice_id = 'Camila'
    language_code = 'pt-BR'
    engine = 'neural'


    # Defina o texto que será sintetizado em fala
    with open(response_file + '.txt', "r") as file:
        text = file.read()

    # Use o método synthesize_speech() da API Polly para sintetizar o texto em fala
    response = polly_client.synthesize_speech(
        OutputFormat='ogg_vorbis',
        Text=text,
        VoiceId=voice_id,
        LanguageCode=language_code,
        Engine=engine
        )

    # Salve o áudio sintetizado em um arquivo audio
    audio_file = response_file + ".ogg"
    with open(audio_file, 'wb') as f:
        f.write(response['AudioStream'].read())
        f.close()
    audio_send(CHAT_ID, audio_file)

    command = MP3_PLAYER + " " + audio_file
    #subprocess.run(command, shell=True)

# 2a. Function that gets the response from OpenAI's chatbot
def open_ai(prompt):
    # Make the request to the OpenAI API
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model': MODEL, 'messages': prompt, 'temperature': 0.01}
    )

    result = response.json()
    final_result = ''.join(choice['message'].get('content') for choice in result['choices'])
    return final_result

def audio_send(chat_id, output_audio):
    """
    Sends an audio file to a Telegram bot chat. 

    :param OUTPUT_AUDIO: a string representing the path to the audio file
    :param chat_id: an integer representing the chat id
    :return: None
    """
    bot = telebot.TeleBot(BOT_TOKEN)
    audio_file=open(output_audio,'rb')
    bot.send_audio(chat_id, audio_file)

# Run the main function
if __name__ == "__main__":
    with open(PROMPT_FILE, "r") as file:
        prompts = file.read().strip()

    promptList = prompts.split('\n\n') 

    for index, prompt in enumerate(promptList):
        if len(prompt) > 10:
            bot_response = open_ai([{'role': 'user', 'content': f'{BOT_PERSONALITY} {prompt}'}])
            
            bot_response = bot_response.replace('\n', '. ').strip()
            bot_response = bot_response.replace('..', '.')

            with open(RESPONSE_FILE + str(index) + ".txt", "w") as file:
                file.write(bot_response)
            
            polly_speak(RESPONSE_FILE + str(index))
            os.remove(RESPONSE_FILE + str(index) + ".txt")
            os.remove(RESPONSE_FILE + str(index) + ".ogg")
        bot_response = ""
    os.remove(PROMPT_FILE)  

