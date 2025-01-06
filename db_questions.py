from app import db, QuizQuestion

# Datenbanktabellen erstellen (nur wenn nicht vorhanden)
db.create_all()

# Beispiel-Fragen hinzufügen
questions = [
    QuizQuestion(
        question="Was ist VWL?",
        module="VWL",
        option_a="Volkswirtschaftslehre",
        option_b="Versicherung und Leben",
        option_c="Verbrauchswirtschaft",
        correct_answer="Volkswirtschaftslehre"
    ),
    QuizQuestion(
        question="Was ist Rechnungswesen?",
        module="Rechnungswesen",
        option_a="Buchführung",
        option_b="Kostenmanagement",
        option_c="Alles oben Genannte",
        correct_answer="Alles oben Genannte"
    )
]

# Daten in die Datenbank schreiben
for question in questions:
    db.session.add(question)

db.session.commit()
print("Datenbank erfolgreich befüllt.")