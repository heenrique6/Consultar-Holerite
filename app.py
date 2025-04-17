from flask import Flask, request, render_template, jsonify, send_from_directory
import os

# Configuração do Flask
app = Flask(__name__)

# Configuração do diretório para uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Armazenar dados dos funcionários
funcionarios = {}  # Inicialmente vazio

# Página inicial para cadastro de funcionários
@app.route('/')
def home():
    return render_template('index.html')

# Rota para cadastrar um funcionário
@app.route('/funcionarios', methods=['POST'])
def cadastrar_funcionario():
    cpf = request.form['cpf']
    nome = request.form['nome']
    arquivo = request.files['arquivo']

    if not cpf or not nome or not arquivo:
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400

    # Salvar o arquivo PDF no diretório de uploads
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{cpf}_holerite.pdf")
    arquivo.save(filepath)

    # Registrar o funcionário no dicionário
    funcionarios[cpf] = {'nome': nome, 'arquivo': filepath}

    # Renderizar uma mensagem de sucesso
    return render_template('index.html', mensagem='Funcionário cadastrado com sucesso!')

# Rota para consulta de holerite
@app.route('/consultar', methods=['GET', 'POST'])
def consultar_holerite():
    if request.method == 'POST':
        cpf = request.form['cpf']

        # Verificar se o CPF está cadastrado
        funcionario = funcionarios.get(cpf)
        if funcionario:
            return render_template('consultar.html', funcionario=funcionario, cpf=cpf)
        else:
            return render_template('consultar.html', error='Funcionário não encontrado.')

    # Página inicial de consulta
    return render_template('consultar.html')

# Rota para download do holerite
@app.route('/holerites/download/<cpf>', methods=['GET'])
def download_holerite(cpf):
    funcionario = funcionarios.get(cpf)
    if not funcionario:
        return jsonify({'error': 'Funcionário não encontrado!'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], f"{cpf}_holerite.pdf", as_attachment=True)

# Configuração para o Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



