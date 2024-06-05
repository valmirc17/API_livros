from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.database import User, mongo, authenticate_user
import requests

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
            access_token = create_access_token(identity=email)
            return jsonify({'message': 'Login realizado com sucesso', 'access_token': access_token, 'user': {'nome': user['nome'], 'email': user['email']}}), 200

        return jsonify({'error': 'E-mail ou senha inválido!'}), 401

    @app.route('/search', methods=['GET'])
    @jwt_required()
    def search_books():
        query = request.args.get('q')
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}')
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao buscar livros'}), response.status_code

        books = response.json().get('items', [])
        book_list = []
        for book in books:
            volume_info = book.get('volumeInfo', {})
            book_data = {
                'id_livro': book.get('id'),
                'titulo': volume_info.get('title'),
                'autores': volume_info.get('authors', []),
                'descricao': volume_info.get('description'),
                'capa': volume_info.get('imageLinks', {}).get('thumbnail')
            }
            book_list.append(book_data)

        return jsonify(book_list), 200

    @app.route('/favorite', methods=['POST'])
    @jwt_required()
    def favorite_book():
        data = request.get_json()
        book_id = data.get('book_id')
        email = get_jwt_identity()

        if not mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
        if response.status_code != 200:
            return jsonify({'error': 'Livro não encontrado'}), response.status_code

        book = response.json()
        volume_info = book.get('volumeInfo', {})
        favorite_data = {
            'email': email,
            'id_livro': book_id,
            'titulo': volume_info.get('title'),
            'autores': volume_info.get('authors', []),
            'descricao': volume_info.get('description'),
            'capa': volume_info.get('imageLinks', {}).get('thumbnail')
        }

        mongo.db.favorites.insert_one(favorite_data)
        return jsonify({'message': 'Livro favoritado com sucesso'}), 201

    @app.route('/favorites', methods=['GET'])
    @jwt_required()
    def get_favorites():
        email = get_jwt_identity()
        if not mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        favorites = mongo.db.favorites.find({'email': email})
        favorite_books = []
        for fav in favorites:
            favorite_books.append({
                'id_livro': fav['id_livro'],
                'titulo': fav['titulo'],
                'autores': fav['autores'],
                'descricao': fav['descricao'],
                'capa': fav['capa']
            })
        return jsonify(favorite_books), 200

    @app.route('/add_to_cart', methods=['POST'])
    @jwt_required()
    def add_to_cart():
        data = request.get_json()
        book_id = data.get('book_id')
        email = get_jwt_identity()

        if not mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        response = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}')
        if response.status_code != 200:
            return jsonify({'error': 'Livro não encontrado'}), response.status_code

        book = response.json()
        volume_info = book.get('volumeInfo', {})
        cart_data = {
            'email': email,
            'id_livro': book_id,
            'titulo': volume_info.get('title'),
            'autores': volume_info.get('authors', []),
            'descricao': volume_info.get('description'),
            'capa': volume_info.get('imageLinks', {}).get('thumbnail'),
            'status': 'in_cart'
        }

        mongo.db.loans.insert_one(cart_data)
        return jsonify({'message': 'Livro adicionado ao carrinho com sucesso'}), 201

    @app.route('/checkout', methods=['POST'])
    @jwt_required()
    def checkout():
        email = get_jwt_identity()

        if not mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        mongo.db.loans.update_many({'email': email, 'status': 'in_cart'}, {'$set': {'status': 'checked_out'}})
        return jsonify({'message': 'Empréstimo realizado com sucesso'}), 200

    @app.route('/loans', methods=['GET'])
    @jwt_required()
    def get_loans():
        email = get_jwt_identity()
        if not mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        loans = mongo.db.loans.find({'email': email, 'status': 'checked_out'})
        loan_books = []
        for loan in loans:
            loan_books.append({
                'id_livro': loan['id_livro'],
                'titulo': loan['titulo'],
                'autores': loan['autores'],
                'descricao': loan['descricao'],
                'capa': loan['capa']
            })
        return jsonify(loan_books), 200
