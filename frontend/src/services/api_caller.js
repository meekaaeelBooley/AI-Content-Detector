// CSC3003S Capstone Project - AI Content Detector
// Year: 2025
// Author: Meekaaeel Booley

import axios from 'axios';

// const API_BASE_URL = 'http://16.171.92.37:5000/api';

// For development with local backend, use:
const API_BASE_URL = 'http://127.0.0.1:5000/api';
const API_KEY = import.meta.env.REACT_APP_API_KEY || 'jackboys25';

// Storage key for session ID
const SESSION_STORAGE_KEY = 'aicd_session_id';

// Function to get stored session ID
const getStoredSessionId = () => {
  // Try localStorage first, then sessionStorage
  return localStorage.getItem(SESSION_STORAGE_KEY) || 
         sessionStorage.getItem(SESSION_STORAGE_KEY);
};

// Function to store session ID
const storeSessionId = (sessionId) => {
  // Store in both localStorage and sessionStorage for reliability
  localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  sessionStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  console.log('Stored session ID:', sessionId);
};

// Function to clear session ID
const clearStoredSessionId = () => {
  localStorage.removeItem(SESSION_STORAGE_KEY);
  sessionStorage.removeItem(SESSION_STORAGE_KEY);
  console.log('Cleared stored session ID');
};

// axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  withCredentials: true,
  crossDomain: true
});

// Request interceptor - ADD SESSION ID TO HEADERS
apiClient.interceptors.request.use(function(config) {
  console.log('Making request to:', config.url);
  
  // Get stored session ID and add to headers if it exists
  const sessionId = getStoredSessionId();
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
    console.log('Added X-Session-ID header:', sessionId);
  } else {
    console.log('No session ID stored, will create new session');
  }
  
  console.log('Request headers:', config.headers);
  return config;
}, function(error) {
  console.log('Request error:', error);
  return Promise.reject(error);
});

// Response interceptor - EXTRACT AND STORE SESSION ID FROM RESPONSES
apiClient.interceptors.response.use(function(response) {
  console.log('Got response:', response.status);
  
  // Check if response has a session ID and store it
  if (response.data && response.data.session_id) {
    const newSessionId = response.data.session_id;
    console.log('Session ID from response:', newSessionId);
    
    // Store the session ID
    storeSessionId(newSessionId);
    
    // Also update the axios default headers for future requests
    apiClient.defaults.headers.common['X-Session-ID'] = newSessionId;
  }
  
  // Log any cookies from response
  if (response.headers['set-cookie']) {
    console.log('Set-Cookie headers:', response.headers['set-cookie']);
  }
  
  return response;
}, function(error) {
  console.log('Response error:', error);
  if (error.response) {
    console.log('Error response headers:', error.response.headers);
    
    // If it's a session-related error, clear stored session
    if (error.response.status === 404 && error.response.data.error === 'Session not found') {
      console.log('Clearing invalid session ID');
      clearStoredSessionId();
    }
  }
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
    
    // For file uploads, we need to manually set the session header
    const sessionId = getStoredSessionId();
    const headers = {
      'Content-Type': 'multipart/form-data',
      'X-API-Key': API_KEY
    };
    
    if (sessionId) {
      headers['X-Session-ID'] = sessionId;
    }
    
    return apiClient.post('/detect', formData, { headers });
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
  
  // Get current session ID (for debugging)
  getCurrentSessionId: function() {
    return getStoredSessionId();
  },
  
  // Clear session (for logout or testing)
  clearSession: function() {
    clearStoredSessionId();
    delete apiClient.defaults.headers.common['X-Session-ID'];
    return Promise.resolve();
  }
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
      return data.error || 'File too big (max 500KB)';
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