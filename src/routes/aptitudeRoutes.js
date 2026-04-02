const express = require('express');
const router = express.Router();
const aptitudeController = require('../controllers/aptitudeController');
const { verifyToken } = require('../middlewares/authMiddleware');

// POST /api/aptitude-questions - Generate aptitude questions (protected)
router.post('/aptitude-questions', verifyToken, aptitudeController.generateQuestions);

// POST /api/reset-question-pool - Reset user's question pool (protected)
router.post('/reset-question-pool', verifyToken, aptitudeController.resetQuestionPool);

// POST /api/submit-scores - Submit and save aptitude test scores (protected)
router.post('/submit-scores', verifyToken, aptitudeController.submitScores);

module.exports = router;
