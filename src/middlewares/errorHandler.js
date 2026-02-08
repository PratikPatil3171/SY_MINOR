/**
 * Global error handler middleware
 */
exports.errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // MongoDB validation error
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      ok: false,
      message: 'Validation error',
      errors: Object.values(err.errors).map(e => e.message)
    });
  }

  // MongoDB duplicate key error
  if (err.code === 11000) {
    return res.status(400).json({
      ok: false,
      message: 'Duplicate entry - email already exists'
    });
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      ok: false,
      message: 'Invalid token'
    });
  }

  // Default error
  res.status(err.status || 500).json({
    ok: false,
    message: err.message || 'Internal server error'
  });
};

/**
 * 404 Not Found handler
 */
exports.notFoundHandler = (req, res) => {
  res.status(404).json({
    ok: false,
    message: 'Route not found'
  });
};
