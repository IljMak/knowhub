-- Erstelle die Tabelle für Benutzer
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    points INTEGER DEFAULT 0
);

-- Erstelle die Tabelle für Quizfragen
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    module TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    correct_answer TEXT NOT NULL
);

-- Erstelle die Tabelle für Belohnungen
CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cost INTEGER NOT NULL
);

-- Beispiel-Daten für die Tabelle quiz_questions
INSERT OR IGNORE INTO quiz_questions (question, module, option_a, option_b, option_c, correct_answer) VALUES
('Was ist VWL?', 'VWL', 'Volkswirtschaftslehre', 'Versicherung und Leben', 'Verbrauchswirtschaft', 'Volkswirtschaftslehre'),
('Was ist Rechnungswesen?', 'Rechnungswesen', 'Buchführung', 'Kostenmanagement', 'Alles oben Genannte', 'Alles oben Genannte');

-- Beispiel-Daten für die Tabelle rewards
INSERT OR IGNORE INTO rewards (name, cost) VALUES
('Gutschein für Kaffee', 20),
('Freier Eintritt ins Museum', 50);