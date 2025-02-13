# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import db, User, QuizQuestion, ShopItem, Purchase, DefinitionPair, TrueFalseQuestion, Test, UserTest, TestQuestion, UnlockedModule # Hier importieren wir das User-Modell
from werkzeug.security import generate_password_hash, check_password_hash
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
    # Quiz Questions
    if not QuizQuestion.query.first():
        sample_questions = [
            QuizQuestion(question="Was ist VWL?", module="VWL", option_a="Volkswirtschaftslehre", option_b="Versicherung und Leben", option_c="Verbrauchswirtschaft", correct_answer="Volkswirtschaftslehre"),
            QuizQuestion(question="Was ist Rechnungswesen?", module="Rechnungswesen", option_a="Buchführung", option_b="Kostenmanagement", option_c="Alles oben Genannte", correct_answer="Alles oben Genannte")
        ]
        db.session.add_all(sample_questions)
        db.session.commit()
        print("Beispieldaten für Quizfragen wurden eingefügt.")

    # Definition Pairs
    if not DefinitionPair.query.first():
        sample_pairs = [
            DefinitionPair(
                module="VWL",
                term="Angebot",
                definition="Die Menge an Gütern, die Produzenten zu einem bestimmten Preis verkaufen möchten"
            ),
            DefinitionPair(
                module="VWL",
                term="Nachfrage",
                definition="Die Menge an Gütern, die Konsumenten zu einem bestimmten Preis kaufen möchten"
            )
        ]
        db.session.add_all(sample_pairs)
        db.session.commit()

    # True/False Questions
    if not TrueFalseQuestion.query.first():
        sample_tf_questions = [
            TrueFalseQuestion(
                module="VWL",
                statement="Eine Erhöhung der Nachfrage führt bei gleichbleibendem Angebot zu einem höheren Preis",
                is_correct=True,
                explanation="Nach dem Gesetz von Angebot und Nachfrage steigt der Preis bei erhöhter Nachfrage."
            ),
            TrueFalseQuestion(
                module="Rechnungswesen",
                statement="Abschreibungen sind immer linear",
                is_correct=False,
                explanation="Abschreibungen können linear, degressiv oder nach Leistung erfolgen."
            )
        ]
        db.session.add_all(sample_tf_questions)
        db.session.commit()

    # Tests
    if not Test.query.first():
        vwl_test = Test(
            name="VWL Grundlagen Test",
            module="VWL",
            price=100
        )
        db.session.add(vwl_test)
        db.session.commit()
        
        questions = [
            TestQuestion(
                test_id=vwl_test.id,
                question="Erkläre den Begriff 'Opportunitätskosten' und gib ein Beispiel.",
                answer="Opportunitätskosten sind die entgangenen Erträge oder Nutzen der nächstbesten Alternative, auf die verzichtet wurde. Beispiel: Wenn du dich entscheidest, einen Nachmittag zu lernen statt arbeiten zu gehen, sind die Opportunitätskosten der entgangene Arbeitslohn."
            ),
            TestQuestion(
                test_id=vwl_test.id,
                question="Was versteht man unter einer Preiselastizität der Nachfrage? Erkläre anhand eines Beispiels.",
                answer="Die Preiselastizität der Nachfrage misst, wie stark sich die nachgefragte Menge eines Gutes bei einer Preisänderung verändert. Beispiel: Wenn bei einer Preiserhöhung von 10% die nachgefragte Menge um 20% sinkt, beträgt die Preiselastizität -2 (elastische Nachfrage)."
            )
        ]
        db.session.add_all(questions)
        db.session.commit()

@app.before_first_request
def create_tables():
    init_db()
@app.route('/')


@app.route('/')
def home():
    # Prüfe ob user_id in der Session ist
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Wenn User nicht gefunden wird, Session löschen
        if user is None:
            session.pop('user_id', None)
            return redirect(url_for('register'))
        return render_template('home.html', logged_in=True, user=user)
    return redirect(url_for('register'))


# Route zur Modulauswahl-Seite
@app.route('/module-selection')
def module_selection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user is None:
        session.pop('user_id', None)
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
    
    # Hole alle verfügbaren Module
    quiz_modules = db.session.query(QuizQuestion.module).distinct().all()
    definition_modules = db.session.query(DefinitionPair.module).distinct().all()
    tf_modules = db.session.query(TrueFalseQuestion.module).distinct().all()
    
    # Kombiniere alle Module und entferne Duplikate
    all_modules = set([m[0] for m in quiz_modules + definition_modules + tf_modules])
    
    # Hole die freigeschalteten Module des Users
    unlocked_modules = {um.module_name for um in user.unlocked_modules}
    
    return render_template('module_selection.html', 
                         modules=sorted(all_modules),
                         unlocked_modules=unlocked_modules,
                         free_unlocks=user.free_unlocks_remaining,
                         points=user.points)


@app.route('/unlock-module/<module>', methods=['POST'])
def unlock_module(module):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    unlock_type = request.form.get('unlock_type')
    
    existing_unlock = UnlockedModule.query.filter_by(
        user_id=user.id, 
        module_name=module
    ).first()
    
    if existing_unlock:
        flash('Dieses Modul ist bereits freigeschaltet!')
        return redirect(url_for('module_selection'))
    
    if unlock_type == 'free' and user.free_unlocks_remaining > 0:
        user.free_unlocks_remaining -= 1
        new_unlock = UnlockedModule(
            user_id=user.id,
            module_name=module,
            is_free=True
        )
        db.session.add(new_unlock)
        flash(f'Modul {module} wurde kostenlos freigeschaltet!')
        
    elif unlock_type == 'points' and user.points >= 50:
        user.points -= 50
        new_unlock = UnlockedModule(
            user_id=user.id,
            module_name=module,
            is_free=False
        )
        db.session.add(new_unlock)
        flash(f'Modul {module} wurde für 50 Punkte freigeschaltet!')
        
    else:
        if unlock_type == 'free':
            flash('Keine kostenlosen Freischaltungen mehr verfügbar!')
        else:
            flash('Nicht genügend Punkte! (50 Punkte benötigt)')
        return redirect(url_for('module_selection'))
    
    db.session.commit()
    return redirect(url_for('module_selection'))

@app.route('/module/<module>/games')
def module_games(module):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    is_unlocked = UnlockedModule.query.filter_by(
        user_id=user.id,
        module_name=module
    ).first() is not None
    
    if not is_unlocked:
        flash('Dieses Modul muss erst freigeschaltet werden!')
        return redirect(url_for('module_selection'))
    
    has_quiz = QuizQuestion.query.filter_by(module=module).first() is not None
    has_definitions = DefinitionPair.query.filter_by(module=module).first() is not None
    has_tf = TrueFalseQuestion.query.filter_by(module=module).first() is not None
    
    return render_template('module_games.html', 
                         module=module,
                         has_quiz=has_quiz,
                         has_definitions=has_definitions,
                         has_tf=has_tf)


# Updated route in app.py
@app.route('/definition-game/<module>', methods=['GET', 'POST'])
def definition_game(module):
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        time_expired = request.form.get('time_expired') == 'true'
        user_answers = request.form.getlist('answers[]')  # Liste der Antworten in der Form "definition_id"

        if time_expired:
            if user.points >= 5:
                user.points -= 5
                flash('Zeit abgelaufen! -5 Punkte')
                db.session.commit()
        else:
            # Überprüfe die Antworten
            score = 0
            total_questions = len(user_answers)
            
            for i, answer in enumerate(user_answers, 1):  # i beginnt bei 1
                if answer and int(answer) == i:  # Wenn die Position (i) mit der gewählten Definition-ID übereinstimmt
                    score += 1
            
            points_earned = (score / total_questions) * 10
            if score < total_questions and user.points >= 5:
                user.points -= 5
                flash('Nicht alle Zuordnungen waren korrekt! -5 Punkte')
            user.points += int(points_earned)
            db.session.commit()
            
            flash(f'Du hast {score} von {total_questions} richtig! +{int(points_earned)} Punkte')
        
        return redirect(url_for('definition_game', module=module))

    # Hole die Begriffe in fester Reihenfolge
    terms = DefinitionPair.query.filter_by(module=module).order_by(db.func.random()).limit(4).all()
    # Erstelle eine gemischte Liste der Definitionen
    definitions = [(p.id, p.definition) for p in terms]
    random.shuffle(definitions)
    
    return render_template('definition_game.html', terms=terms, definitions=definitions, timer_seconds=20)



#True or False Game
@app.route('/true-false-game/<module>', methods=['GET', 'POST'])
def true_false_game(module):
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    question = TrueFalseQuestion.query.filter_by(module=module).order_by(db.func.random()).first()

    if not question:
        return "Keine Fragen für dieses Modul verfügbar.", 404

    if request.method == 'POST':
        time_expired = request.form.get('time_expired') == 'true'
        
        if time_expired:
            if user.points >= 5:
                user.points -= 5
                flash('Zeit abgelaufen! -5 Punkte')
        else:
            user_answer = request.form.get('answer') == 'true'
            question_id = int(request.form.get('question_id'))
            question = TrueFalseQuestion.query.get(question_id)

            if question.is_correct == user_answer:
                user.points += 5
                flash(f'Richtig! +5 Punkte. {question.explanation}')
            else:
                if user.points >= 5:
                    user.points -= 5
                    flash(f'Falsch! -5 Punkte. {question.explanation}')

        db.session.commit()
        return redirect(url_for('true_false_game', module=module))

    return render_template('true_false_game.html', question=question, timer_seconds=10)


# Route zum Starten des Quiz für das gewählte Modul
@app.route('/quiz/<module>', methods=['GET', 'POST'])
def quiz(module):
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user is None:
        session.pop('user_id', None)
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
        
    # Rest der Route-Logik...
    questions = QuizQuestion.query.filter_by(module=module).all()

    if not questions:
        return render_template('error.html', message=f"Keine Fragen für das Modul '{module}' vorhanden."), 404

    question = random.choice(questions)

    if request.method == 'POST':
        question_id = int(request.form['question_id'])
        selected_answer = request.form.get('answer')
        time_expired = request.form.get('time_expired') == 'true'

        question = QuizQuestion.query.get(question_id)
        
        if not question:
            return f"Frage mit ID {question_id} wurde nicht gefunden.", 404

        if time_expired:
            if user.points >= 5:
                user.points -= 5
                flash('Zeit abgelaufen! -5 Punkte')
        elif not selected_answer:
            if user.points >= 5:
                user.points -= 5
                flash('Keine Antwort ausgewählt! -5 Punkte')
        elif question.correct_answer == selected_answer:
            user.points += 10
            flash('Richtige Antwort! +10 Punkte')
        else:
            if user.points >= 5:
                user.points -= 5
                flash('Falsche Antwort! -5 Punkte')
        
        db.session.commit()
        return redirect(url_for('quiz', module=module))

    return render_template('quiz.html', question=question, timer_seconds=10)


#Shop
@app.route('/shop')
def shop():
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user is None:
        session.pop('user_id', None)
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
    
    items = ShopItem.query.all()
    tests = Test.query.all()
    user_tests = UserTest.query.filter_by(user_id=user.id).all()
    purchased_test_ids = [ut.test_id for ut in user_tests]
    
    return render_template('shop.html', 
                         points=user.points, 
                         items=items, 
                         tests=tests,
                         purchased_test_ids=purchased_test_ids)


@app.route('/buy-test/<int:test_id>')
def buy_test(test_id):
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    test = Test.query.get(test_id)
    
    if not test:
        flash('Test nicht gefunden.')
        return redirect(url_for('shop'))
    
    # Prüfen ob der Test bereits gekauft wurde
    existing_purchase = UserTest.query.filter_by(user_id=user.id, test_id=test.id).first()
    if existing_purchase:
        flash('Du hast diesen Test bereits gekauft!')
        return redirect(url_for('shop'))
    
    if user.points < test.price:
        flash('Nicht genug Punkte!')
        return redirect(url_for('shop'))
    
    user.points -= test.price
    user_test = UserTest(user_id=user.id, test_id=test.id)
    db.session.add(user_test)
    db.session.commit()
    
    flash(f'Test "{test.name}" erfolgreich gekauft!')
    return redirect(url_for('shop'))


@app.route('/buy/<int:item_id>')
def buy_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    item = ShopItem.query.get(item_id)
    
    if not item:
        flash('Item nicht gefunden.')
        return redirect(url_for('shop'))
        
    if user.points < item.price:
        flash('Nicht genug Punkte!')
        return redirect(url_for('shop'))
    
    user.points -= item.price
    purchase = Purchase(user_id=user.id, item_id=item.id)
    db.session.add(purchase)
    db.session.commit()
    
    flash(f'{item.name} erfolgreich gekauft!')
    return redirect(url_for('shop'))


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


#Profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user is None:
        session.pop('user_id', None)
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))
        
    purchases = Purchase.query.filter_by(user_id=user.id).all()
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        
        if check_password_hash(user.password, current_password):
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Passwort erfolgreich geändert.')
        else:
            flash('Aktuelles Passwort ist falsch.')
    
    return render_template('profile.html', user=user, purchases=purchases)


@app.route('/start-test/<int:test_id>')
def start_test(test_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if not user_test:
        flash('Test nicht gefunden oder nicht gekauft.')
        return redirect(url_for('profile'))
        
    return redirect(url_for('show_test_question', test_id=test_id, question_number=1))


@app.route('/show-test-question/<int:test_id>/<int:question_number>')
def show_test_question(test_id, question_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    test = Test.query.get(test_id)
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if not user_test:
        flash('Test nicht gefunden oder nicht gekauft.')
        return redirect(url_for('profile'))
        
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    if not questions:
        flash('Keine Fragen für diesen Test gefunden.')
        return redirect(url_for('profile'))
    
    if question_number > len(questions):
        return redirect(url_for('profile'))
        
    current_question = questions[question_number-1]
    show_answer = question_number <= user_test.progress
    
    # Neue Variable für die letzte Frage
    is_last_question = question_number == len(questions)
    
    return render_template('test_question.html', 
                         test=test,
                         question=current_question,
                         question_number=question_number,
                         total_questions=len(questions),
                         show_answer=show_answer,
                         is_last_question=is_last_question)


@app.route('/show-answer/<int:test_id>/<int:question_number>')
def show_answer(test_id, question_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if not user_test:
        return redirect(url_for('profile'))
    
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    if question_number > user_test.progress:
        user_test.progress = question_number
        
        # Wenn wir die letzte Frage erreicht haben und die Antwort anzeigen,
        # markiere den Test als abgeschlossen
        if question_number == len(questions):
            user_test.completed = True
            flash('Test erfolgreich abgeschlossen!')
        
        db.session.commit()
    
    return redirect(url_for('show_test_question', 
                          test_id=test_id, 
                          question_number=question_number))


@app.route('/complete-test/<int:test_id>')
def complete_test(test_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if user_test and user_test.progress == TestQuestion.query.filter_by(test_id=test_id).count():
        user_test.completed = True
        db.session.commit()
        flash('Test erfolgreich abgeschlossen!')
        
    return redirect(url_for('profile'))


@app.route('/review-test/<int:test_id>')
def review_test(test_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if not user_test or not user_test.completed:
        flash('Test nicht verfügbar oder noch nicht abgeschlossen.')
        return redirect(url_for('profile'))
        
    test = Test.query.get(test_id)
    questions = TestQuestion.query.filter_by(test_id=test_id).all()
    
    return render_template('review_test.html', 
                         test=test,
                         questions=questions)


@app.route('/reset-test/<int:test_id>')
def reset_test(test_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    user_test = UserTest.query.filter_by(user_id=user.id, test_id=test_id).first()
    
    if user_test:
        user_test.progress = 0
        user_test.completed = False
        db.session.commit()
        flash('Test wurde zurückgesetzt.')
    
    return redirect(url_for('profile'))

#Rewards
@app.route('/rewards')
def rewards():
    if 'user_id' not in session:
        flash('Bitte logge dich erst ein.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    available_rewards = Reward.query.filter(Reward.cost <= user.points).all()

    if not available_rewards:
        message = "Keine Belohnungen verfügbar. Sammle mehr Punkte!"
    else:
        message = f"Du hast {user.points} Punkte."

    return render_template('rewards.html', points=user.points, rewards=available_rewards, message=message)


@app.route('/coop')
def coop():
    return render_template('coop.html')


if __name__ == '__main__':
    app.run(debug=True)
