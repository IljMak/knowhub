# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session
from db import db, QuizQuestion, Reward
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Initialisierung der Datenbank
db.init_app(app)

# Funktion zur Initialisierung der Datenbank
def init_db():
    if not os.path.exists('knowhub.db'):
        with app.app_context():
            db.create_all()
            print("Datenbank und Tabellen wurden erstellt.")
            insert_sample_data()

# Beispiel-Daten einfügen
def insert_sample_data():
    if not QuizQuestion.query.first():
        sample_questions = [
            QuizQuestion(question="Was ist VWL?", module="VWL", option_a="Volkswirtschaftslehre", option_b="Versicherung und Leben", option_c="Verbrauchswirtschaft", correct_answer="Volkswirtschaftslehre"),
            QuizQuestion(question="Was ist Rechnungswesen?", module="Rechnungswesen", option_a="Buchführung", option_b="Kostenmanagement", option_c="Alles oben Genannte", correct_answer="Alles oben Genannte")
        ]
        db.session.add_all(sample_questions)
        db.session.commit()
        print("Beispieldaten für Quizfragen wurden eingefügt.")
    
    if not Reward.query.first():
        sample_rewards = [
            Reward(name="Gutschein für Kaffee", cost=20),
            Reward(name="Freier Eintritt ins Museum", cost=50)
        ]
        db.session.add_all(sample_rewards)
        db.session.commit()
        print("Beispieldaten für Belohnungen wurden eingefügt.")

@app.before_first_request
def create_tables():
    init_db()

@app.route('/')
def home():
    return render_template('home.html')

# Route zur Modulauswahl-Seite
@app.route('/module-selection')
def module_selection():
    # Hier werden alle verfügbaren Module (z. B. VWL, Rechnungswesen) angezeigt
    modules = ['VWL', 'Rechnungswesen','Wirtschaftsrecht' ]  # Du kannst dies dynamisch aus der Datenbank holen
    return render_template('module_selection.html', modules=modules)

# Route zum Starten des Quiz für das gewählte Modul
@app.route('/quiz/<module>', methods=['GET', 'POST'])
def quiz(module):
    # Sicherstellen, dass Fragen für das Modul existieren
    questions = QuizQuestion.query.filter_by(module=module).all()

    if not questions:
        return render_template('error.html', message=f"Keine Fragen für das Modul '{module}' vorhanden."), 404

    question = random.choice(questions)

    if request.method == 'POST':
        question_id = int(request.form['question_id'])
        selected_answer = request.form['answer']

        question = QuizQuestion.query.get(question_id)

        if not question:
            return f"Frage mit ID {question_id} wurde nicht gefunden.", 404

        if question.correct_answer == selected_answer:
            session['points'] = session.get('points', 0) + 10
            return redirect(url_for('quiz', module=module))

    return render_template('quiz.html', question=question)

@app.route('/profile')
def profile():
    points = session.get('points', 0)
    if points == 0:
        message = "Du hast noch keine Punkte gesammelt."
    else:
        message = f"Du hast {points} Punkte."
    return render_template('profile.html', points=points, message=message)

@app.route('/rewards')
def rewards():
    points = session.get('points', 0)
    available_rewards = Reward.query.filter(Reward.cost <= points).all()

    if not available_rewards:
        message = "Keine Belohnungen verfügbar. Sammle mehr Punkte!"
    else:
        message = f"Du hast {points} Punkte."

    return render_template('rewards.html', points=points, rewards=available_rewards, message=message)

@app.route('/coop')
def coop():
    return render_template('coop.html')

if __name__ == '__main__':
    app.run(debug=True)
