import logging
from flask import Flask
from models.database import mongo
from controllers import routes

app = Flask(__name__, template_folder='views')

app.config['MONGO_URI'] = 'mongodb+srv://api_livros:zEiWficU9ohh185c@veridioculi.qqcq3.mongodb.net/api_livros'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mongo.init_app(app)

routes.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        if 'api_livros' not in mongo.db.list_collection_names():
            mongo.db.users.insert_one({
                'nome': '',
                'email': '',
                'senha': ''
            })
        logger.debug('Conexão com o banco de dados realizada com sucesso e coleção "users" verificada.')

    app.run(host='localhost', port=5000, debug=True)
    logger.debug('Servidor iniciado com sucesso no endereço http://localhost:5000')
