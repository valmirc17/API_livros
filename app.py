import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from models.database import mongo
from controllers import routes

app = Flask(__name__, template_folder='views')

# Configuração do MongoDB URI
# app.config['MONGO_URI'] = 'mongodb+srv://api_livros:zEiWficU9ohh185c@veridioculi.qqcq3.mongodb.net/api_livros'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/api_livros'

# Inicializando o MongoDB com o app Flask
mongo.init_app(app)

# Configurações do JWT
app.config['JWT_SECRET_KEY'] = 'api_livros'
jwt = JWTManager(app)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializa as rotas
routes.init_app(app)

@app.route('/test_connection')
def test_connection():
    try:
        mongo.db.list_collection_names()
        return "Conexão com o banco de dados realizada com sucesso", 200
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco de dados: {e}")
        return "Erro ao conectar com o banco de dados", 500

if __name__ == '__main__':
    with app.app_context():
        if 'users' not in mongo.db.list_collection_names():
            mongo.db.users.insert_one({
                'nome': 'admin',
                'email': 'admin@example.com',
                'senha': 'admin'
            })
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "users" verificada.')

        if 'favorites' not in mongo.db.list_collection_names():
            mongo.db.favorites.insert_one({
                'email': 'example@example.com',
                'livro_id': 'example_id',
                'titulo': 'Exemplo de Título',
                'autores': ['Autor Exemplo'],
                'descricao': 'Exemplo de Descrição',
                'capa': 'http://example.com/capa.jpg'
            })
            mongo.db.favorites.delete_one({'email': 'example@example.com'})
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "favorites" verificada.')

        if 'loans' not in mongo.db.list_collection_names():
            mongo.db.loans.insert_one({
                'email': 'example@example.com',
                'livro_id': 'example_id',
                'titulo': 'Exemplo de Título',
                'autores': ['Autor Exemplo'],
                'descricao': 'Exemplo de Descrição',
                'capa': 'http://example.com/capa.jpg',
                'status': 'in_cart'
            })
            mongo.db.loans.delete_one({'email': 'example@example.com'})  
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "loans" verificada.')

    app.run(host='localhost', port=5000, debug=True)
    logger.debug('Servidor iniciado com sucesso no endereço http://localhost:5000')
