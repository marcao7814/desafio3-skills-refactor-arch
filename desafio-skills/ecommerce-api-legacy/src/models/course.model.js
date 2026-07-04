function findActiveById(db, id) {
    return new Promise((resolve, reject) => {
        db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id], (err, row) => {
            if (err) return reject(err);
            resolve(row || null);
        });
    });
}

function findAll(db) {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM courses', [], (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

module.exports = { findActiveById, findAll };
