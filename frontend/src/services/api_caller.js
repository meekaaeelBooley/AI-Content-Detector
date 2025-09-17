import axios from 'axios';

// const API_BASE_URL = 'http://16.171.92.37:5000/api';
const API_BASE_URL = 'http://127.0.0.1:5000/api';
// For development with local backend, use: 'http://127.0.0.1:5000/api'

const API_KEY = import.meta.env.REACT_APP_API_KEY || 'jackboys25';

// axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  withCredentials: true,
  crossDomain: true
});

// Simple request logger
apiClient.interceptors.request.use(function(config) {
  console.log('Making request to:', config.url);
  return config;
}, function(error) {
  console.log('Request error:', error);
  return Promise.reject(error);
});

// Simple response logger
apiClient.interceptors.response.use(function(response) {
  console.log('Got response:', response.status);
  return response;
}, function(error) {
  console.log('Response error:', error);
  return Promise.reject(error);
});

// API functions
export const apiService = {
  // Health check
  healthCheck: function() {
    return apiClient.get('/health');
  },
  
  // AI detection with text
  detectAI: function(text, forceSingleAnalysis) {
    if (forceSingleAnalysis === undefined) {
      forceSingleAnalysis = false;
    }
    
    return apiClient.post('/detect', {
      text: text,
      force_single_analysis: forceSingleAnalysis
    });
  },
  
  // AI detection with file
  detectAIFile: function(file, forceSingleAnalysis) {
    if (forceSingleAnalysis === undefined) {
      forceSingleAnalysis = false;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    if (forceSingleAnalysis) {
      formData.append('force_single_analysis', 'true');
    }
    
    return apiClient.post('/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-API-Key': API_KEY
      }
    });
  },
  
  // Get history
  getHistory: function() {
    return apiClient.get('/history');
  },
  
  // Get specific analysis
  getAnalysis: function(analysisId) {
    return apiClient.get('/analysis/' + analysisId);
  },
  
  // Get session info
  getSessionInfo: function() {
    return apiClient.get('/session');
  },
  
  // Clear history
  clearHistory: function() {
    return apiClient.delete('/clear-history');
  },
};

// error handler
export const handleApiError = function(error) {
  if (error.response) {
    // Server gave us an error response
    var status = error.response.status;
    var data = error.response.data;
    
    if (status === 400) {
      return data.error || 'Bad request - check your input';
    } else if (status === 401) {
      return data.error || 'Invalid API key';
    } else if (status === 404) {
      return data.error || 'Page not found';
    } else if (status === 413) {
      return data.error || 'File too big (max 5MB)';
    } else if (status === 500) {
      return data.error || 'Server error';
    } else {
      return data.error || 'Something went wrong';
    }
  } else if (error.request) {
    // Request was made but no response
    return 'Cannot connect to server. Check your internet.';
  } else {
    // Other error
    return error.message || 'Unknown error';
  }
};

// Check if backend is working
export const checkBackendConnection = function() {
  return apiService.healthCheck()
    .then(function(response) {
      return {
        connected: true,
        data: response.data,
        message: 'Backend is working!'
      };
    })
    .catch(function(error) {
      return {
        connected: false,
        error: handleApiError(error),
        message: 'Cannot connect to backend'
      };
    });
};

// Default export
export default apiService;