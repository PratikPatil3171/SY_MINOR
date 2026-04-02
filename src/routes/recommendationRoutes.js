const express = require('express');
const router = express.Router();
const recommendationController = require('../controllers/recommendationController');
const { verifyToken } = require('../middlewares/authMiddleware');

// POST /api/recommendations - Get career recommendations (protected)
router.post('/recommendations', verifyToken, recommendationController.getRecommendations);

module.exports = router;
