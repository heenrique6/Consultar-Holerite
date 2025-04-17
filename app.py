from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for
import os
import csv

# Configuração do Flask
app = Flask(__name__)

# Configuração do diretório para uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Armazenar dados dos funcionários
funcionarios = {}

# Página inicial para cadastro de funcionários
@app.route('/')
def home():
    return render_template('index.html')

# Rota para upload de CSV e holerites
@app.route('/upload_dados', methods=['GET', 'POST'])
def upload_dados():
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        holerites_folder = request.files.getlist('holerites')

        if not csv_file or not holerites_folder:
            return jsonify({'error': 'É necessário enviar tanto o arquivo CSV quanto os arquivos de holerites!'}), 400
        
        # Salvar o arquivo CSV
        csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'dados_funcionarios.csv')
        csv_file.save(csv_filepath)

        # Processar o CSV para adicionar os funcionários
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cpf = row['cpf']
                nome = row['nome']
                funcionarios[cpf] = {'nome': nome, 'arquivo': None}

        # Salvar os arquivos de holerites
        for holerite in holerites_folder:
            holerite_path = os.path.join(app.config['UPLOAD_FOLDER'], holerite.filename)
            holerite.save(holerite_path)

            # Associar o holerite ao funcionário baseado no CPF
            cpf = holerite.filename.split('.')[0]
            if cpf in funcionarios:
                funcionarios[cpf]['arquivo'] = holerite_path

        return jsonify({'success': 'Funcionários e holerites cadastrados com sucesso!'}), 200

    return render_template('upload_dados.html')

# Rota para consultar holerite
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



