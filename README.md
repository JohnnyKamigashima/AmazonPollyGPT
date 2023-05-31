# AmazonPollyGPT
Resume texto com chatgpt em portugues e le com Amazon Polly.

O Arquivo de entrada com o texto será 
- prompt.txt 

e o arquivo de saída da resposta será 
- responseGPT.txt

Configure as varáveis de ambiente conforme necessário. Nesta versão o aplicativo de reprodução de audio será o afplay do MAC.

- Você precisa ter uma conta Amazon S3 com Polly configurado e token do api
- Você precisa ter conta no OpenAI API com token configurado nas pastas

# Open api autentication files em ~/.openapi_credentials
```
api_key=
api_secret=None
```

# Amazon Poly credentials em ~/.aws/credentials
```
[default]
aws_access_key_id = 
aws_secret_access_key = 
region=us-east-1
```
