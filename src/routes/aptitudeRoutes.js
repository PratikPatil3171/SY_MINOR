const express = require('express');
const router = express.Router();
const aptitudeController = require('../controllers/aptitudeController');

// POST /api/aptitude-questions - Generate aptitude questions
router.post('/aptitude-questions', aptitudeController.generateQuestions);

// POST /api/reset-question-pool - Reset user's question pool
router.post('/reset-question-pool', aptitudeController.resetQuestionPool);

// POST /api/submit-scores - Submit and save aptitude test scores
router.post('/submit-scores', aptitudeController.submitScores);

module.exports = router;
