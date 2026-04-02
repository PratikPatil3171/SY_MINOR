const collegeSearchService = require('../services/collegeSearchService');

function searchColleges(req, res) {
  try {
    const data = collegeSearchService.searchColleges(req.query || {});

    return res.status(200).json({
      ok: true,
      ...data,
    });
  } catch (error) {
    console.error('College search failed:', error);
    return res.status(500).json({
      ok: false,
      message: 'Failed to search colleges',
    });
  }
}

module.exports = {
  searchColleges,
};
