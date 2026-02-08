const fetch = require('node-fetch');

const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:5000';

/**
 * Get career recommendations from Python recommendation engine
 * @param {Object} studentData - Student profile data
 * @returns {Promise<Object>} Recommendations object
 */
exports.getRecommendations = async (studentData) => {
  try {
    const pythonResponse = await fetch(`${PYTHON_ENGINE_URL}/api/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(studentData),
    });

    if (!pythonResponse.ok) {
      throw new Error(`Python engine returned status ${pythonResponse.status}`);
    }

    const recommendations = await pythonResponse.json();
    return recommendations;
  } catch (error) {
    console.error('Python engine service error:', error);
    throw new Error('Recommendation service temporarily unavailable');
  }
};
