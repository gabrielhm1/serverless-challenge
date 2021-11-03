# serverless-challenge
Build a serverless architecture for image analysis 

![Screenshot](Architecture.png)

<h2>Configurações inicias</h2>

 O deploy so será feito após adicionar um **profile** válido nas configurações. O nome do profile também deve ser alterado no 'serveless.yml'.
 
 ```
 sls config credentials --provider aws --key {AWS_ACCESS_KEY_ID} --secret {AWS_SECRET_KEY} --profile {AWS_PROFILE}
 ```

Logo em seguida, faça o deploy:
 ```
 sls deploy
 ```
 
 <h2>Modificações Necessárias</h2>
  
  1. Durante o desenvolvimento não encontrei uma forma de subir bibliotecas externas junto no deploy da aplicação. Para que as funções lambda funcione corretamente é preciso importar a biblioteca **Pillow**.
    - Adicione uma layer em cada função lambda existente no projeto. Importe o arquivo python.zip com a biblioteca para criar uma layer, em **runtime** selecione `python3.6`, `python3.7`, `python3.8`.  

 2. Acesse **IAM** e na role da aplicaçãos `serverless-challenge-dev-us-east-1-lambdaRole` adicione a permissao `AmazonS3FullAccess`

<h2>Funções<h2>
<h3>extractMetadata</h3>
  Essa função é executada toda vez que um novo evento ocorre no bucket. Após adicionar uma imagem na raiz do bucket, verifique se os dados foram inseridos no dynamoDb.
  Outra forma de testar a função, é utilizando o evento "s3 put" disponivel na área de "event test" do AWS. Nele basta fazer as seguintes alterarações no json:
  
   - Altere o **nome** do bucket `"name": "seubucketname"`  
   - Altere a **key** com o nome da sua imagem `"key": "logo.png"`, em object. Para que o teste retorne o codigo abaixo é necessario que a imagem esteja na raiz do seu bucket, caso contrário a função irá retorna um erro.
 Saida esperada:
  ```
 {
  "statusCode": 200,
  "body": "logo.png inserido com sucesso"'
}
```
  <h3>getMetadata</h3>
  A função getMetadata pode ser chamada através da URI, passando como endpoint o nome da imagem junto com sua extensão.
  Exemplo do end point gerado:
  
  ```
  https://endpointinformationapi.amazonaws.com/dev/images/{s3objectkey}
  ```
  O api gateway gera uma URL única, altere o endpoint com o nome da imagem e sua extensão para receber os dados.
  ```
  https://endpointinformationapi.amazonaws.com/dev/images/logo.png
  
  Retorno:
  {"s3objectkey": "logo.png", "size": "1024", "width": "320", "height": "238"}
  ```
  
  <h3>infoImages</h3>
  Pode ser executada através da URI que irá retorna as informação pertinentes do banco de dados
  Executando a URI a seguinte retorno é esperado:
  
  ```
  https://nbgen03ruh.execute-api.us-east-1.amazonaws.com/dev/imageInfo
  Retorno:
  
  {"Maior tamanho": "logo-5.png", "Menor tamanho": "logo.png", "Tipos de imagens": ["png", "jpg"], "Quantidade de imagens": {"png": 7, "jpg": 2}}
  
  ```
