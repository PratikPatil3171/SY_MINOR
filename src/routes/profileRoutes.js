const express = require('express');
const router = express.Router();
const profileController = require('../controllers/profileController');
const { verifyToken } = require('../middlewares/authMiddleware');

// GET /api/profile/:email - Get student profile (protected)
router.get('/profile/:email', verifyToken, profileController.getProfile);

module.exports = router;
