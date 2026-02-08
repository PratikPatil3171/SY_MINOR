const express = require('express');
const router = express.Router();
const recommendationController = require('../controllers/recommendationController');

// POST /api/recommendations - Get career recommendations
router.post('/recommendations', recommendationController.getRecommendations);

module.exports = router;
