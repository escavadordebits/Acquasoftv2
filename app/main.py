from flask import Flask, make_response, jsonify, request, render_template, abort
from pip._vendor import requests
from flask_cors import CORS
import pyodbc


app = Flask(__name__)
CORS(app)

app.config["JSON_SORT_KEYS"] = False

server = "vhsql01.vh.com.br,8533"
database = "BD_CORE_EVEREST"
username = "userAcquaAPI"
password = "hw7CsBhUALD-n6!"

cnxn = pyodbc.connect(
    "DRIVER={SQL Server};SERVER="
    + server
    + ";DATABASE="
    + database
    + ";ENCRYPT=no;UID="
    + username
    + ";PWD="
    + password
)
print("Conexão Bem Sucedida")

clientes = list()
dadosapi = list()


def Post_DadosApi(DadosAPI):

    cursor = cnxn.cursor()
    Token = DadosAPI['Token']
    InsereDadosApi = f"INSERT INTO  DadosAPI(Token, Instancia, Registros,DataLigar) VALUES ('{DadosAPI['Token']}','{DadosAPI['Instancia']}','{DadosAPI['Registros']}','{DadosAPI['DataLigar']}')"
    cursor.execute(InsereDadosApi)
    cursor.commit()


def Get_DadosAPI():
    cursor = cnxn.cursor()
    GetDadosAPI = f"select Id,Token,Instancia, Registros, DataliGar from DadosAPI"
    cursor.execute(GetDadosAPI)
   # data = cursor.fetchall()
   # headings = ("ID","Token","Instancia", "Registros")
    headings = ("ID", "Token", "Instancia")
    data = (("1", "TokenTeste", "Inst.Testes", "RegistroTeste"))
    return headings


@app.route("/clientes", methods=["GET"])
def get_clientes():
    cursor = cnxn.cursor()
    lista = cursor.execute(
        "exec uspGerarNumerosDiscador @Operacao='GND', @DataLigar='2022/07/14', @RegistrosGerar=2;"
    )
    contatos = lista.fetchall()
    clientes.clear()
    for cliente in contatos:
        clientes.append(
            {
                "IdTelemarketing": cliente[0],
                "nomecliente": cliente[2],
                "DDTelefone": cliente[3],
                "Telefone": cliente[4],
            }
        )
    post_clientes(clientes)
    return make_response(jsonify(clientes))


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        dataret = request.get_json()
        info = dataret['Body']['Text']

    else:
        abort(404)


def post_clientes(clientes):

    for i in clientes:
        ddd = i["DDTelefone"]
        telcli = i["Telefone"]
        if (ddd is None or telcli is None):
            print("DDD ou tel em Branco")

        else:
            tel = ddd + telcli
            nomecliente = i["nomecliente"]
            IdTelemarketing = i["IdTelemarketing"]

            message = f"Olá Boa tarde! {nomecliente} , tudo bem? Aqui é a Jade da  Empresa Acquasoft purificadores de água, consta em nosso sistema que já se encontra no prazo de realizar a troca do refil, o Sr(a) deseja agendar? Temos disponibilidade a partir de amanhã.Seu Id {IdTelemarketing} """
            url = "https://v5.chatpro.com.br/chatpro-1034a36039/api/v1/send_message"
            payload = {

                "number": "21 99993-1578",  # "21967445985",#"21985550409", #tel
                "message": message

            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "bb805f8a708f387ca4c139d384c9b7c4",
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                data = response.json()
                if response.status_code == 201:
                    for result in data["resposeMessage"]:
                        id = result["id"]
                        cursor2 = cnxn.cursor()
                        qinsert = f"insert StatusMsgAPI values({IdTelemarketing},{tel},'{nomecliente}','{id}','MensagemEnviada') ;"
                        # cursor2.execute(qinsert)

                        print(response.text)
                else:
                    print("Nao enviada")
            except requests.exceptions.RequestException as e:
                with open("log.txt", "w") as arquivo:
                    arquivo.write(
                        f"Status {response.status_code} retornou com  '{response.content}',  falha no envio da msg.")
                    # print(f"Status {response.status_code} retornou com  '{response.content}',  falha no envio da msg.")


if __name__ == "__main__":
    app.run()
