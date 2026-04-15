import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Session API
export const sessionApi = {
  createSession: (title?: string, type?: string) =>
    api.post('/sessions', { title, type }),
  
  listSessions: (limit?: number, offset?: number) =>
    api.get('/sessions', { params: { limit, offset } }),
  
  getSession: (id: string) =>
    api.get(`/sessions/${id}`),
  
  deleteSession: (id: string) =>
    api.delete(`/sessions/${id}`),
  
  sendMessage: (sessionId: string, content: string, type: string = 'text') =>
    api.post(`/sessions/${sessionId}/messages`, { content, type }),
}

// Analysis API
export const analysisApi = {
  analyzeReport: (sessionId: string, files: File[], extractKeywords: boolean = true, compareReports: boolean = false) => {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('extract_keywords', String(extractKeywords))
    formData.append('compare_reports', String(compareReports))
    files.forEach(file => formData.append('files', file))
    
    return api.post('/analysis/report', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  analyzeStock: (sessionId: string, stockCode: string, stockName?: string, analysisType: string = 'full') =>
    api.post('/analysis/stock', { session_id: sessionId, stock_code: stockCode, stock_name: stockName, analysis_type: analysisType }),
}

// Report API
export const reportApi = {
  downloadReport: (reportId: string, format: 'pdf' | 'json' = 'pdf') =>
    api.get(`/reports/${reportId}/download`, { 
      params: { format },
      responseType: 'blob',
    }),
  
  generateReport: (analysisId: string) =>
    api.post('/reports', { analysis_id: analysisId }),
}

// Health API
export const healthApi = {
  checkHealth: () =>
    api.get('/health'),
}

export default api
