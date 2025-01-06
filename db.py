from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

def insert_sample_data():
    """Beispieldaten in die Datenbank einfügen."""
    # Überprüfe, ob es bereits Daten gibt
    if not QuizQuestion.query.first():
        # Beispiel-Daten einfügen (Quizfragen)
        sample_questions = [
            QuizQuestion(question="Was ist VWL?", module="VWL", option_a="Volkswirtschaftslehre", option_b="Versicherung und Leben", option_c="Verbrauchswirtschaft", correct_answer="Volkswirtschaftslehre"),
            QuizQuestion(question="Was ist Rechnungswesen?", module="Rechnungswesen", option_a="Buchführung", option_b="Kostenmanagement", option_c="Alles oben Genannte", correct_answer="Alles oben Genannte")
        ]
        db.session.add_all(sample_questions)
        db.session.commit()
        print("Beispieldaten für Fragen wurden eingefügt.")

    # Überprüfe, ob es bereits Belohnungen gibt
    if not Reward.query.first():
        # Beispiel-Daten für Belohnungen
        sample_rewards = [
            Reward(name="Gutschein für Kaffee", cost=20),
            Reward(name="Freier Eintritt ins Museum", cost=50)
        ]
        db.session.add_all(sample_rewards)
        db.session.commit()
       print("Beispieldaten für Belohnungen wurden eingefügt.") 