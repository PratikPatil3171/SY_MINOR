const express = require('express');
const router = express.Router();
const contactController = require('../controllers/contactController');

// POST /api/contact - Send contact form query email
router.post('/contact', contactController.sendContactQuery);

module.exports = router;
