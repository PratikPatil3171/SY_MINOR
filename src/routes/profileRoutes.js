const express = require('express');
const router = express.Router();
const profileController = require('../controllers/profileController');

// GET /api/profile/:email - Get student profile
router.get('/profile/:email', profileController.getProfile);

module.exports = router;
