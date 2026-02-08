const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// POST /api/signup - Register or update user
router.post('/signup', authController.signup);

// POST /api/login - Authenticate user
router.post('/login', authController.login);

module.exports = router;
