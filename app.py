import hashlib
import json

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'


@app.route('/inicio')
def index(msg='', tipoMsg=''):
    if logado():
        return render_template("index.html", msg=msg, tipoMsg=tipoMsg)
    else:
        return redirect(url_for('login'))

@app.route('/estado')
def estado():
    if logado():
        url = "https://covid19-brazil-api.now.sh/api/report/v1/brazil/uf/"
        uf = request.args.get("q")
        if(uf):
            url += uf

        response = requests.get(url)
        dados = response.json()

        return render_template("estado.html", info=dados)

    else:
        return redirect(url_for('login'))


@app.route('/estados')
def estados():
    if logado():
        url = "https://covid19-brazil-api.now.sh/api/report/v1"
        response = requests.get(url)
        dados = response.json()

        return render_template("estados.html", info=dados)

    else:
        return redirect(url_for('login'))


@app.route('/paises')
def paises():
    if logado():
        url = "https://covid19-brazil-api.now.sh/api/report/v1/countries"
        response = requests.get(url)
        dados = response.json()

        return render_template("paises.html", info=dados)

    else:
        return redirect(url_for('login'))


#cadastro e login

@app.route('/', methods=['POST', 'GET'])
def login():
    if not logado():
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            senha = hashlib.sha256(senha.encode()).hexdigest()

            aut = autenticar(email, senha)

            if aut['login']:
                return redirect(url_for('index'))
            else:
                msg = aut['msg']
                tipoMsg = aut['tipoMsg']
        else:
            msg = ''
            tipoMsg = ''

        return render_template('login.html', msg=msg, tipoMsg=tipoMsg)

    else:
        return redirect(url_for('index'))


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if not logado():
        if request.method == 'POST':
            email = request.form.get('email')
            senha = hashlib.sha256(request.form.get('senha').encode()).hexdigest()

            cadastrar(email, senha)
            session['username'] = email
            flash(u'Cadastro realizado com sucesso! Seja bem-vindo(a)', 'success')

            return redirect(url_for('index'))

        return render_template('cadastro.html')

    else:
        return redirect(url_for('index'))


@app.route('/sair')
def sair():
    session.pop('username', None)
    return redirect(url_for('login'))


def cadastrar(email, senha):
    usuario = {'email': email, 'senha': senha}

    arquivo = './usuarios.json'
    dados = abreArquivo(arquivo, 'r')
    dados.append(usuario)

    gravaArquivo(arquivo, 'w', dados)

    return True


def autenticar(email, senha):
    dados = abreArquivo('./usuarios.json', 'r')

    tipoMsg = 'danger'
    login = False

    if dados:
        for usuario in dados:
            if usuario['email'] == email:
                if usuario['senha'] == senha:
                    msg = 'Seja bem-vindo(a), '+email+'!'
                    tipoMsg = 'success'
                    login = True
                    session['username'] = email
                    break
                else:
                    msg = 'Senha Incorreta!'
                    break
            else:
                msg = 'Usuário ' + email + ' não existe!'
    else:
        msg = 'Usuário ' + email + ' não existe!'

    flash(msg, tipoMsg)
    aut = { 'login' : login, 'msg' : msg, 'tipoMsg' : tipoMsg }

    return aut


def logado():
    if 'username' in session:
        return True

    return False


def abreArquivo(arquivo, modo):
    arquivo = arquivo
    arq = open(arquivo, mode=modo)
    dados = json.load(arq)
    arq.close()

    dados = [d for d in dados]

    return dados


def gravaArquivo(arquivo, modo, dados):
    arq = open(arquivo, mode=modo)
    arq.write(json.dumps(dados))
    arq.close()

    return True


if __name__ == '__main__':
    app.run()
