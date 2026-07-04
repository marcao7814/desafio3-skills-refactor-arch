function create(db, { enrollmentId, amount, status }) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status],
            function insertCallback(err) {
                if (err) return reject(err);
                resolve(this.lastID);
            }
        );
    });
}

function findAll(db) {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM payments', [], (err, rows) => {
            if (err) return reject(err);
            resolve(rows);
        });
    });
}

function deleteByEnrollmentIds(db, enrollmentIds) {
    if (!enrollmentIds.length) return Promise.resolve();

    const placeholders = enrollmentIds.map(() => '?').join(', ');
    return new Promise((resolve, reject) => {
        db.run(
            `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
            enrollmentIds,
            (err) => {
                if (err) return reject(err);
                resolve();
            }
        );
    });
}

module.exports = { create, findAll, deleteByEnrollmentIds };
