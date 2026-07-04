function findByEmail(db, email) {
    return new Promise((resolve, reject) => {
        db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
            if (err) return reject(err);
            resolve(row || null);
        });
    });
}

function findById(db, id) {
    return new Promise((resolve, reject) => {
        db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
            if (err) return reject(err);
            resolve(row || null);
        });
    });
}

function findAll(db) {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM users', [], (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

function create(db, { name, email, passwordHash }) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
            function insertCallback(err) {
                if (err) return reject(err);
                resolve(this.lastID);
            }
        );
    });
}

function remove(db, id) {
    return new Promise((resolve, reject) => {
        db.run('DELETE FROM users WHERE id = ?', [id], (err) => {
            if (err) return reject(err);
            resolve();
        });
    });
}

module.exports = { findByEmail, findById, findAll, create, remove };
