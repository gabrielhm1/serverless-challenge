from PIL import Image
import json
import urllib.parse
import boto3
import operator


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('serverless-challenge-dev') #Tabela do dynamodb
s3 = boto3.client('s3')

def extractMetadata(event, context):
    for record in event['Records']: #Percorre todos os novos eventos do bucket 

        #Capturando a chave, bucket e tamanho da imagem
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8') 
        bucket = record['s3']['bucket']['name']
        size = record['s3']['object']['size']

        try:
            download_path = '/tmp/{}'.format(key)
            s3.download_file(bucket,key, download_path)
            openim = open(download_path, 'rb') #Abre a imagem apos fazer o download
            im = Image.open(openim)
            width, height = im.size #Atribuindo as dimensoes da imagem

            size,width,height = str(size), str(width), str(height) #Passa todos os dados da imagem para string
            table.put_item( #Atribui o novo item ao banco de dados
                Item={
                    's3objectkey':key,
                    'size':size,
                    'width':width,
                    'height':height
                }
            )

            body = key + " inserido com sucesso"

            return{
                'statusCode':200,
                'body':body
            }        

        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}.'.format(key, bucket))
            raise e

def getImage(s3objectkey,context):
    key = s3objectkey['s3objectkey']
    download_path = './{}'.format(key)
    s3.download_file('mychallengersolvimmb',key,download_path)

def getMetadata(event,context):
    s3objectkey = event['pathParameters']['s3objectkey'] #Captura a URI
    try:
        data = table.get_item( #Fazendo a consulta ao banco de dados
            Key={
                's3objectkey':s3objectkey
            }
        )
        response = {
            "statusCode": 200,
            "body": json.dumps(data['Item']) #Retorna todos os dados da imagem
        }
        return response
    except: 
        response = {
        "statusCode": 400,
        "body": "Not Found"
        }
        return response


def infoImages(event, context):
    try:
        allItems = table.scan()
        listImageType= [] #Lista para os tipos de imagem 
        dicImageType = {} #Dicionario para contagem de cada tipo de imagem -Key = extensao da imagem -Value = ocorrencia no DB
        objectSize ={}    #Dicionario com o tamanho de cada imagem -Key = s3obcketkey -Value = Tamanho da imagem
        for item in allItems['Items']: #Percorre todos os items no DB
            Itemtype = str.lower(item['s3objectkey'].split('.')[-1]) # lower case
            #Faz a contagem
            if Itemtype in dicImageType:
                dicImageType[Itemtype]+=1 
            else:
                dicImageType[Itemtype] = 1
                listImageType.append(Itemtype)

            objectSize[item['s3objectkey']] = int(item['size']) #Faz atribuicao da s3objectkey com o tamanho da imagem
        

        maxSize = max(objectSize.items(), key=operator.itemgetter(1))[0] #Maior imagem
        minSize = min(objectSize.items(), key=operator.itemgetter(1))[0] #Menor imagem
        
        body = {
            'Maior tamanho': maxSize,
            'Menor tamanho': minSize,
            'Tipos de imagens':listImageType,
            'Quantidade de imagens': dicImageType,
        }
        return {
            'statusCode': 200,
            'body':json.dumps(body)   
        }
    except:
        response = {
            "statusCode": 400,
            "body": "Not Found"
        }
        return response
