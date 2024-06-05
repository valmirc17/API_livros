from flask import request, jsonify, render_template
from models.database import User, mongo, authenticate_user

def init_app(app):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')

        if mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'E-mail já cadastrado, faça login!'}), 400

        user = User(nome, email, senha)
        user.save()

        return jsonify({'message': 'Usuário registrado com sucesso'}), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')

        user = authenticate_user(email, senha)
        if user:
            return jsonify({'message': 'Login realizado com sucesso', 'user': {'nome': user['nome'], 'email': user['email']}}), 200

        return jsonify({'error': 'E-mail ou senha inválido!'}), 401
