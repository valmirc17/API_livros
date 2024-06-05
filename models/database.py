from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

mongo = PyMongo()

class User:
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)  # Encrypt the password

    def save(self):
        mongo.db.users.insert_one({
            'nome': self.nome,
            'email': self.email,
            'senha': self.senha
        })

def authenticate_user(email, senha):
    user = mongo.db.users.find_one({'email': email})
    if user and check_password_hash(user['senha'], senha):
        return user
    return None
