import { useState, useCallback } from 'react';
import { getRecords as apiGetRecords, submitQuestion as apiSubmitQuestion } from '../api/client';

export function useRecords() {
  const [records, setRecords] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchRecords = useCallback(async (sessionId) => {
    if (!sessionId) {
      setRecords([]);
      return;
    }
    const data = await apiGetRecords(sessionId);
    setRecords(data.records || []);
  }, []);

  const askQuestion = useCallback(async (query, sessionId) => {
    setIsLoading(true);
    try {
      const data = await apiSubmitQuestion(query, sessionId);
      setRecords(prev => [...prev, {
        record_id: data.record_id,
        query,
        answer: data.answer,
        answer_source: data.answer_source,
        llm_used: data.llm_used,
        model: data.model,
        response_time_ms: data.response_time_ms,
        timestamp: data.timestamp,
        sources: data.sources || [],
      }]);
      return data;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearRecords = useCallback(() => {
    setRecords([]);
  }, []);

  return { records, isLoading, fetchRecords, askQuestion, clearRecords };
}
