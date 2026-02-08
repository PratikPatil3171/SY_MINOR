const pythonEngineService = require('../services/pythonEngineService');

/**
 * Get career recommendations for a student
 */
exports.getRecommendations = async (req, res) => {
  try {
    const studentData = req.body;

    if (!studentData.email) {
      return res.status(400).json({
        ok: false,
        message: "Student email is required",
      });
    }

    console.log(`\n🎯 Generating career recommendations for: ${studentData.email}`);

    // Forward request to Python recommendation engine
    const recommendations = await pythonEngineService.getRecommendations(studentData);
    
    console.log(`✓ Generated ${recommendations.recommendations?.length || 0} recommendations`);
    
    res.json({
      ok: true,
      ...recommendations,
    });
  } catch (err) {
    console.error("Error generating recommendations:", err);
    res.status(500).json({
      ok: false,
      message: "Unable to generate recommendations at this time. Please ensure the Python recommendation engine is running.",
    });
  }
};
