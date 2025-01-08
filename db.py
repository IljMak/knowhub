#db

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)
    tests = db.relationship('UserTest', backref='user', lazy=True)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    
class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Integer, nullable=False)
    purchases = db.relationship('Purchase', backref='item', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class DefinitionPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100), nullable=False)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.String(500), nullable=False)

class TrueFalseQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100), nullable=False)
    statement = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    explanation = db.Column(db.String(500))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    questions = db.relationship('TestQuestion', backref='test', lazy=True)

class TestQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)

class UserTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Speichert den Fortschritt (welche Fragen bereits aufgedeckt wurden)
    completed = db.Column(db.Boolean, default=False)
    purchase_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    test = db.relationship('Test', backref='user_tests', lazy=True)
