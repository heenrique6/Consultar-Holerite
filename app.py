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

# Rota para excluir funcionário e seu holerite
@app.route('/excluir/<cpf>', methods=['GET'])
def excluir_funcionario(cpf):
    funcionario = funcionarios.get(cpf)
    if funcionario:
        # Excluir o arquivo de holerite
        arquivo_path = funcionario['arquivo']
        if os.path.exists(arquivo_path):
            os.remove(arquivo_path)

        # Remover o funcionário do dicionário
        del funcionarios[cpf]
        return jsonify({'success': f'Funcionário {cpf} excluído com sucesso!'}), 200
    return jsonify({'error': 'Funcionário não encontrado!'}), 404

# Rota para atualizar dados de um funcionário
@app.route('/atualizar/<cpf>', methods=['POST'])
def atualizar_funcionario(cpf):
    nome = request.form['nome']
    arquivo = request.files['arquivo']

    funcionario = funcionarios.get(cpf)
    if funcionario:
        # Atualizar nome
        if nome:
            funcionario['nome'] = nome

        # Atualizar o arquivo de holerite
        if arquivo:
            # Remover o antigo arquivo de holerite
            if funcionario['arquivo'] and os.path.exists(funcionario['arquivo']):
                os.remove(funcionario['arquivo'])

            # Salvar o novo arquivo de holerite
            novo_arquivo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{cpf}_holerite.pdf")
            arquivo.save(novo_arquivo_path)
            funcionario['arquivo'] = novo_arquivo_path

        return jsonify({'success': f'Dados do funcionário {cpf} atualizados com sucesso!'}), 200
    return jsonify({'error': 'Funcionário não encontrado!'}), 404

# Configuração para o Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
