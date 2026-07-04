function create(db, { userId, courseId }) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
            function insertCallback(err) {
                if (err) return reject(err);
                resolve(this.lastID);
            }
        );
    });
}

function findAll(db) {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM enrollments', [], (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

function findByUserId(db, userId) {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM enrollments WHERE user_id = ?', [userId], (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

function deleteByUserId(db, userId) {
    return new Promise((resolve, reject) => {
        db.run('DELETE FROM enrollments WHERE user_id = ?', [userId], (err) => {
            if (err) return reject(err);
            resolve();
        });
    });
}

module.exports = { create, findAll, findByUserId, deleteByUserId };
