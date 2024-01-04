from flask import Flask, request, render_template, make_response, jsonify
from pip._vendor import requests
from main import get_clientes, Post_DadosApi
import pyodbc
app = Flask(__name__)
formData = {}
DadosApi = {}


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


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':

        DadosApi = {
            "Token": request.form['Token'],
            "Instancia": request.form['Instancia'],
            "Registros": request.form['Registros'],
            "DataLigar": request.form['DataLigar'], }
        Post_DadosApi(DadosApi)
    if request.method == 'GET':
        dadosapi.clear()
        cursor = cnxn.cursor()
        GetDadosAPI = f"select Id,Token,Instancia, Registros, DataliGar from tblAPIDados"
        cursor.execute(GetDadosAPI)
        data = cursor.fetchall()
        for dados in data:
            dadosapi.append({
                "Id": dados[0],
                "Token": dados[1],
                "Instancia": dados[2],
                "Registros": dados[3],
            })

        headings = ("ID", "Token", "Instancia", "Registros")

        return render_template('home.html', headings=headings, data=dadosapi)

    else:
        return render_template('home.html')


@app.route('/EnviarMsg', methods=['POST'])
def EnviarMsg():
    get_clientes()


def get_clientes():
    DataLigar = request.form['DataLigar']
    Registros = request.form['Registros']
    queryinsert = f"exec uspGerarNumerosDiscador @Operacao='GND', @DataLigar='{DataLigar}', @RegistrosGerar={Registros};"
    cursor = cnxn.cursor()
    lista = cursor.execute(
        queryinsert
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


def post_clientes(clientes):
    DadosToken = list()
    queryinsert = f"select top 1  Id,Token,Instancia, Registros, DataliGar from DadosAPI;"
    cursor2 = cnxn.cursor()
    lista2 = cursor2.execute(
        queryinsert
    )
    DadosApiToken = lista2.fetchall()
    for DadosToken in DadosApiToken:
        token = DadosToken[1]
        intancia = DadosToken[2]

    for i in clientes:
        ddd = i["DDTelefone"]
        telcli = i["Telefone"]
        if (ddd is None or telcli is None):
            print("DDD ou tel em Branco")

        else:
            tel = ddd + telcli
            nomecliente = i["nomecliente"]
            IdTelemarketing = i["IdTelemarketing"]
            Authorization = token
            InstanciaForm = intancia

            message = f"Olá Boa tarde! {nomecliente} , tudo bem? Aqui é a Jade da  Empresa Acquasoft purificadores de água, consta em nosso sistema que já se encontra no prazo de realizar a troca do refil, o Sr(a) deseja agendar? Temos disponibilidade a partir de amanhã.Seu Id {IdTelemarketing} """
            url = f"https://v5.chatpro.com.br/{InstanciaForm}/api/v1/send_message"
            payload = {

                "number": "21967445985",  # "21967445985",#"21985550409", #tel
                "message": message

            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": Authorization,
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                data = response.json()
                if response.status_code == 201:
                    for result in data["resposeMessage"]:
                        id = result.get["id"]
                        qinsert = f"insert StatusMsgAPI values({IdTelemarketing},{tel},'{nomecliente}','{id}','MensagemEnviada') ;"
                        # exec uspAPIStatusMsg

                        # @Operacao = 'inc',

                        # b@IDTelemarketing =3,

                        # @TelCliente  ='(21)99922-3344',

                        # @NomeCliente ='VH3',

                        # @Mensagem ='Teste3',

                        # @Status ='OK'

                        cursor2 = cnxn.cursor()
                        cursor2.execute(qinsert)

                        status = "Msg Enviada"
                        return render_template('home.html', status=status)
                else:
                    print("Nao enviada")
            except requests.exceptions.RequestException as e:
                with open("log.txt", "w") as arquivo:
                    arquivo.write(
                        f"Status {response.status_code} retornou com  '{response.content}',  falha no envio da msg.")
                    # print(f"Status {response.status_code} retornou com  '{response.content}',  falha no envio da msg.")

if __name__ == "__main__":
    app.run(port=8085, host='0.0.0.0', debug=True, threaded=True)
