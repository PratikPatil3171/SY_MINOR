const express = require('express');
const router = express.Router();
const collegeController = require('../controllers/collegeController');

// GET /api/colleges/search?q=&districts=&branches=&hasWebsite=&page=&limit=&sort=
router.get('/colleges/search', collegeController.searchColleges);

module.exports = router;
