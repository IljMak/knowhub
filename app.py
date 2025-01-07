# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db, User, QuizQuestion, Reward  # Hier importieren wir das User-Modell
from werkzeug.security import generate_password_hash, check_password_hash
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash

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
    # Prüfe ob user_id in der Session ist
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('home.html', logged_in=True, user=user)
    return render_template('home.html', logged_in=False)

# Route zur Modulauswahl-Seite
@app.route('/module-selection')
def module_selection():
    # Hier werden alle verfügbaren Module (z. B. VWL, Rechnungswesen) angezeigt
    modules = ['VWL', 'Rechnungswesen']  # Du kannst dies dynamisch aus der Datenbank holen
    return render_template('module_selection.html', modules=modules)

# Route zum Starten des Quiz für das gewählte Modul
@app.route('/quiz/<module>', methods=['GET', 'POST'])
def quiz(module):
    # Überprüfen ob User eingeloggt ist
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

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
            flash('Richtige Antwort! +10 Punkte')
        else:
            flash('Leider falsch. Versuche es noch einmal!')
            
        return redirect(url_for('quiz', module=module))

    return render_template('quiz.html', question=question)

# Route für die Registrierung
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)


        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Benutzername bereits vergeben, bitte wähle einen anderen.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrierung erfolgreich! Du kannst dich nun einloggen.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route für das Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Erfolgreich eingeloggt!')
            return redirect(url_for('home'))
        
        flash('Ungültiger Benutzername oder Passwort!')
        return redirect(url_for('login'))

    # Wenn der Benutzer bereits eingeloggt ist, leite zur Home-Seite weiter
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    return render_template('login.html')


# Logout 
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Du wurdest ausgeloggt.')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    points = session.get('points', 0)
    
    if points == 0:
        message = "Du hast noch keine Punkte gesammelt."
    else:
        message = f"Du hast {points} Punkte."
    
    return render_template('profile.html', user=user, points=points, message=message)

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
