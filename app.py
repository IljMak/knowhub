from flask import Flask, render_template, request, redirect, url_for, session
from db import db, QuizQuestion, Reward
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/quiz/<module>', methods=['GET', 'POST'])
def quiz(module):
    if request.method == 'POST':
        question_id = int(request.form['question_id'])
        selected_answer = request.form['answer']
        question = QuizQuestion.query.get(question_id)
        if question.correct_answer == selected_answer:
            session['points'] = session.get('points', 0) + 10
            return redirect(url_for('quiz', module=module))
    question = random.choice(QuizQuestion.query.filter_by(module=module).all())
    return render_template('quiz.html', question=question)

@app.route('/profile')
def profile():
    points = session.get('points', 0)
    return render_template('profile.html', points=points)

@app.route('/rewards')
def rewards():
    points = session.get('points', 0)
    available_rewards = Reward.query.filter(Reward.cost <= points).all()
    return render_template('rewards.html', points=points, rewards=available_rewards)

@app.route('/coop')
def coop():
    return render_template('coop.html')

if __name__ == '__main__':
    app.run(debug=True)
