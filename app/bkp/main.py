from flask import Flask, make_response, jsonify, request, abort
from pip._vendor import requests
from flask_cors import CORS
import pyodbc


app = Flask(__name__)
CORS(app)


app.config["JSON_SORT_KEYS"] = False

server = 'srv-dev-sql-acquasoft.database.windows.net'
database = 'BackupBolinho'
username = 'saadmin'
password = 'hw7CsBhUALD-n6!'

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE=' +
                      database+';ENCRYPT=no;UID='+username+';PWD=' + password)
print("Conexão Bem Sucedida")

clientes = list()


@app.route('/clientes', methods=['GET'])
def get_clientes():
    cursor = cnxn.cursor()
    lista = cursor.execute(
        "exec uspGerarNumerosDiscador @Operacao='GND', @DataLigar='2017/12/05', @RegistrosGerar=2;")
    contatos = lista.fetchall()

    for cliente in contatos:
        clientes.append(
            {
                'IdTelemarketing': cliente[0],
                'nomecliente': cliente[2],
                'DDTelefone': cliente[3],
                'Telefone': cliente[4],
            }
        )
    post_clientes(clientes)
    return make_response(
        jsonify(clientes)
    )


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        return 'sucess,200'
    else:
        abort(403)


def post_clientes(clientes):

    for i in clientes:

        tel = i['DDTelefone'] + i['Telefone']
        nomecliente = i['nomecliente']
        IdTelemarketing = i['IdTelemarketing']

        message = f"Olá Boa tarde! {nomecliente} , tudo bem? Aqui é a Jade da  Empresa Acquasoft purificadores de água, consta em nosso sistema que já se encontra no prazo de realizar a troca do refil, o Sr deseja agendar? Temos disponibilidade a partir de amanhã.Seu Id {IdTelemarketing}"
        url = "https://v5.chatpro.com.br/chatpro-6790d7a23d/api/v1/send_button_message"
        payload = {
            "buttons": [
                {
                    "id": "1",
                    "text": "Sim"
                },
                {
                    "id": "2",
                    "text": "Não"
                }
            ],
            "number": tel,  # "21985550409",
            "message": message,
            "title": "Agendar?"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "f9484f1e859abd063c6195fcd0eae254"
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)


if __name__ == '__main__':
    app.run(port=8085, host='0.0.0.0', debug=True, threaded=True)
