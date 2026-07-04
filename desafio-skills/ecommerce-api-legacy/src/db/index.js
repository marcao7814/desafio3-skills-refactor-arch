const sqlite3 = require('sqlite3').verbose();
const settings = require('../config/settings');
const { hashPassword } = require('../utils/password');
const { COURSE_ACTIVE } = require('../config/constants');

function createDb() {
    return new sqlite3.Database(settings.dbPath);
}

function initSchema(db) {
    db.serialize(() => {
        db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
        db.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
        db.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
        db.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
        db.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

        db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]
        );
        db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Clean Architecture', 997.0, COURSE_ACTIVE]);
        db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Docker', 497.0, COURSE_ACTIVE]);
        db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
    });
}

module.exports = { createDb, initSchema };
