// Configuration for API endpoints
export const config = {
  // Use environment variable for API URL, fallback to local API endpoint
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || '',
  
  // API endpoints
  endpoints: {
    chat: '/api/chat',
    health: '/api/health'
  }
}

// Helper function to get full API URL
export const getApiUrl = (endpoint: string) => {
  return `${config.apiBaseUrl}${endpoint}`
} 