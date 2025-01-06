# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db, User, QuizQuestion, Reward
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melde dich zuerst an.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@app.before_request
def create_tables():
    if not os.path.exists('instance/knowhub.db'):
        init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Benutzername bereits vergeben')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrierung erfolgreich!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Erfolgreich eingeloggt!')
            return redirect(url_for('home'))
        
        flash('Falscher Benutzername oder Passwort')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich ausgeloggt!')
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=session.get('username'))

@app.route('/module-selection')
@login_required
def module_selection():
    modules = ["Rechnungswesen", "VWL", "Wirtschaftsrecht"]
    return render_template('module_selection.html', modules=modules)

@app.route('/quiz/<module>', methods=['GET', 'POST'])
@login_required
def quiz(module):
    questions = QuizQuestion.query.filter_by(module=module).all()
    
    if not questions:
        flash(f"Keine Fragen für das Modul '{module}' verfügbar.")
        return redirect(url_for('module_selection'))
    
    question = random.choice(questions)
    
    if request.method == 'POST':
        try:
            question_id = int(request.form.get('question_id'))
            selected_answer = request.form.get('answer')
            
            if not selected_answer:
                flash("Bitte wähle eine Antwort aus.")
                return render_template('quiz.html', question=question)
            
            current_question = QuizQuestion.query.get_or_404(question_id)
            
            if current_question.correct_answer == selected_answer:
                session['points'] = session.get('points', 0) + 10
                flash("Richtig! +10 Punkte")
            else:
                flash(f"Falsch. Die richtige Antwort war: {current_question.correct_answer}")
            
            return redirect(url_for('quiz', module=module))
            
        except Exception as e:
            flash("Ein Fehler ist aufgetreten. Bitte versuche es erneut.")
            return redirect(url_for('home'))
    
    return render_template('quiz.html', question=question)

@app.route('/profile')
@login_required
def profile():
    points = session.get('points', 0)
    message = "Du hast noch keine Punkte gesammelt." if points == 0 else f"Du hast {points} Punkte."
    return render_template('profile.html', points=points, message=message)

@app.route('/rewards')
@login_required
def rewards():
    points = session.get('points', 0)
    available_rewards = Reward.query.all()
    message = f"Du hast {points} Punkte."
    return render_template('rewards.html', points=points, rewards=available_rewards, message=message)

@app.route('/coop')
@login_required
def coop():
    return render_template('coop.html')

if __name__ == '__main__':
    app.run(debug=True)