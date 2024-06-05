import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from models.database import mongo
from controllers import routes
import ssl

app = Flask(__name__, template_folder='views')

# Configurações do MongoDB
app.config['MONGO_URI'] = 'mongodb+srv://api_livros:zEiWficU9ohh185c@veridioculi.qqcq3.mongodb.net/api_livros'
app.config['MONGO_OPTIONS'] = {'ssl': False, 'ssl_cert_reqs': ssl.CERT_NONE}
mongo.init_app(app)

# Configurações do JWT
app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta_deve_ser_muito_segura'  # Defina uma chave secreta forte
jwt = JWTManager(app)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializar as rotas
routes.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        # Verificar e criar a coleção de usuários se necessário
        if 'users' not in mongo.db.list_collection_names():
            mongo.db.users.insert_one({
                'nome': 'admin',
                'email': 'admin@example.com',
                'senha': 'admin'
            })
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "users" verificada.')

        # Verificar e criar a coleção de favoritos se necessário
        if 'favorites' not in mongo.db.list_collection_names():
            mongo.db.favorites.insert_one({
                'email': 'example@example.com',
                'livro_id': 'example_id',
                'titulo': 'Exemplo de Título',
                'autores': ['Autor Exemplo'],
                'descricao': 'Exemplo de Descrição',
                'capa': 'http://example.com/capa.jpg'
            })
            mongo.db.favorites.delete_one({'email': 'example@example.com'})  # Remover exemplo de documento após criação
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "favorites" verificada.')

        # Verificar e criar a coleção de empréstimos se necessário
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
            mongo.db.loans.delete_one({'email': 'example@example.com'})  # Remover exemplo de documento após criação
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "loans" verificada.')

    # Iniciar o servidor Flask
    app.run(host='localhost', port=5000, debug=True)
    logger.debug('Servidor iniciado com sucesso no endereço http://localhost:5000')
