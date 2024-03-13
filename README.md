
## Projeto Plataforma Comunicação de Comunicação 

### Resumo do Escopo do projeto
Desenvolvimento três endpoints relacionados ao envio de comunicações da empresa: agendamento, consulta e cancelamento.
Os agendamentos serão armazenados em um banco de dados e enviados para uma fila de mensagens. As APIs devem seguir o modelo RESTful, utilizar JSON e realizar testes unitários.
O desenvolvimento será realizado em Python, com suporte para PostgreSQL como banco de dados e RabbitMQ como sistema de mensageria. 



### Requisitos Funcionais e Não Funcionais do Projeto
De acordo com o escopo desse projeto, foram levantados os seguintes requisitos funcionais e não funcionais, listados na figura a seguir:

![Requisitos Funcionais e Não Funcionais](./Images/RequisitosNFN.png)

Para modelar o banco de dados, foi criadada a tabela nomeada **Agendamento**, com os seguintes atributos:

- id: PRIMARY KEY
- data_hora_envio: TIMESTAMP
- destinario:TEXT
- mensagem: TEXT
- status: TEXT DEFAULT `agendado`

### Arquitetura

Para o desenvolvimento da task, após o levantamento de requisitos, foi implementada a seguinte arquitetura:

![Arquitetura](./Images/Arquitetura.png)

Explicação:
1 - A comunicação é feita com a aplicação, onde é escolhido qual operação realizar: Realizar Agendamento, Consultar Informação, Cancelar Agendamento

2 - A escolha é enviada para API REST

**Se a operação for do tipo: Realizar Agendamento, ela será 3.a**

3.a A solicitação é enviada para o RabbitMQ onde fica em uma fila para em seguida, ser registrada no banco de dados relacional

4.a ser registrada no banco de dados relacional

5.a E então é enviada para api rest

6.a o resultado então chega na aplicação

**Se a operação for do tipo: Consultar informação, cancelar agendamento**

3-b a api rest envia uma solicitação para informação ser consultada no banco de dados

4-b a api rest retorna o resultado para a aplicação

5-b a aplicação exibe a resposta da solicitação

### Estrutura do diretorio

```
.
├── Images
│   ├── Arquitetura.png
│   ├── Diagrama_De_Classe.png
│   └── RequisitosNFN.png
├── README.md
└── source
    └── rest_api
        ├── README.md
        ├── db
        │   ├── config.py
        │   └── initial_config.py
        ├── main.py
        ├── models
        │   └── request_model.py
        ├── rabbitmq
        │   └── rabbitmq.py
        └── test.py
        ├── requirements.txt
```


### Configuração do ambiente de desenvolvimento

O aquivo `.env.example` deve ser preenchido com suas proprias credenciais e deve ser renomeada para `env`.

#### Supabase (Banco de dados)

Para uso do postgresql, foi criado um banco através do supbase (https://supabase.com/)

Para utilizado:
1. Realize o cadastro ou faça o login caso já possua uma conta
2. Na página inicial, clique em `New Project`
3. Agora preencha o formulario com informações do seu projeto, para esse projeto, o nome escolhido foi `ml_bd`
4. Em seguida, escolha uma senha
5. A localização do seu banco de dados (escolha a região mais próxima de você por questões de latência)
6. Em seguida um plano
7. Clique em `Create new project`
   
Através do menu lateral, acesse as configurações e clique em database, use suas credenciais para preencher o arquivo que você renomeou como `env`


### Entendendo as rotas da aplicação

- /agendamento 
  
Tipo de rota: POST

Exemplo de requisição: http://127.0.0.1:5000/agendamento

Corpo JSON:
```
.
{
	"data_hora_envio": "2024-03-12T10:44:40",
	"destinatario": "nathalia@mail.com",
	"mensagem": "testando agendamento de comunicação"
}
```

Resultado esperado:
```
.
{
	"mensagem": "Agendamento realizado com sucesso"
}
```

- /consulta/<destinatario>

Tipo de rota: GET

Exemplo de requisição:
`
http://127.0.0.1:5000/consulta/nathalia@mail.com
`

Resultado esperado:

```
.
	{
		"data_hora_envio": "Tue, 12 Mar 2024 10:44:40 GMT",
		"destinatario": "nathalia@mail.com",
		"id": 33,
		"mensagem": "testando agendamento de comunicação",
		"status": "agendado"
	}
```


**cancelamento/<int:id>**

Exemplo de requisição: http://127.0.0.1:5000/cancelamento/31

Resultado esperado: 

.
{
	"mensagem": "Cancelamento realizado com sucesso"
}
`


### Meios de utilizar a aplicação de forma local


#### Utilizando Docker desktop

Essa aplicação conta com uma imagem **Docker** dentro de seu diretório `/source/rest_api`

**-> É necessário que você possua Docker instalado em sua maquina.**

-> Para mais informações sobre Docker, você pode consultar os links abaixo:
-  O que é docker? https://www.redhat.com/pt-br/topics/containers/what-is-docker
-  Documentação oficial Docker (Disponivel em Inglês) https://docs.docker.com

No diretório do projeto, `/rest_api` e execute seguinte comando:

`docker build . -t app`

Com este comando, estamos construindo uma imagem em sua na pasta atual e utilizar a tag **br-nommad**

Para testar sua aplicação localmente, no mesmo terminal execute o seguinte comando.

`docker run -d -p 5000:5000 app`

******************************************************************************************************************************
-d Este comando executa o conteiner no modo desacoplado (-d),sem bloquear o seu terminal.

-p Este comando especifica as portas a serem utilizadas na aplicação 8000 na porta interna e externa do conteiner.

******************************************************************************************************************************

Para parar sua aplicação, execute o seguinte comando em seu terminal:

`docker kill <PRIMEIROS_NUMEROS_DO_ID_DA_APLICACAO>`

**-> Para pegar os numeros do id da sua aplicação execute `docker ps`**


#### Utilizando Visual Studio Code ou o seu editor preferido.

Ao abrir o seu projeto no seu editor, execute o segundo comando:

para versões do Python 3
`pip3 install -r requirements.txt`

ou

Para versões do Python <3:
`pip install -r requirements.txt.`

Em seguida execute:

`python3 main.py`

ou 

`python main.py`

Utilize o Insomia ou uma aplicação de uma preferência para testar as rodas com base na saída.

-> Para saber mais sobre o Insomia: https://docs.insomnia.rest (Disponível em Inglês)


