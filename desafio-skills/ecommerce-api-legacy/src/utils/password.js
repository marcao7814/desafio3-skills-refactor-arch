const crypto = require('crypto');
const { PASSWORD_HASH_KEYLEN } = require('../config/constants');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derivedKey = crypto.scryptSync(password, salt, PASSWORD_HASH_KEYLEN);
    return `${salt}:${derivedKey.toString('hex')}`;
}

function verifyPassword(password, storedHash) {
    const [salt, key] = storedHash.split(':');
    const derivedKey = crypto.scryptSync(password, salt, PASSWORD_HASH_KEYLEN);
    return crypto.timingSafeEqual(Buffer.from(key, 'hex'), derivedKey);
}

module.exports = { hashPassword, verifyPassword };
