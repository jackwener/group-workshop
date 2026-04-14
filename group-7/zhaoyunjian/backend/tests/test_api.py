import pytest
import uuid
import json

class TestCapabilitiesAPI:
    """能力探测API测试"""
    
    def test_get_capabilities(self, client):
        """TC-M01-020: 获取能力配置"""
        response = client.get('/api/v1/agent/capabilities')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert 'caps' in data
        assert 'copaw_configured' in data['caps']
        assert 'bailian_configured' in data['caps']

class TestSessionAPI:
    """会话管理API测试"""
    
    def test_create_session(self, client):
        """TC-M01-020: 新建会话"""
        response = client.post('/api/v1/agent/sessions',
                              data=json.dumps({'title': '测试会话'}),
                              content_type='application/json')
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert 'session_id' in data
        assert data['title'] == '测试会话'
        assert data['query_count'] == 0
        assert 'created_at' in data
    
    def test_create_session_default_title(self, client):
        """TC-M01-020: 新建会话默认标题"""
        response = client.post('/api/v1/agent/sessions',
                              data=json.dumps({}),
                              content_type='application/json')
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['title'] == '新会话'
    
    def test_create_session_title_too_long(self, client):
        """TC-M01-020: 标题超过100字符"""
        response = client.post('/api/v1/agent/sessions',
                              data=json.dumps({'title': 'x' * 101}),
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_TITLE'
    
    def test_get_sessions(self, client):
        """TC-M01-021: 会话列表"""
        # 先创建会话
        client.post('/api/v1/agent/sessions',
                   data=json.dumps({'title': '会话1'}),
                   content_type='application/json')
        
        response = client.get('/api/v1/agent/sessions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
    
    def test_get_sessions_pagination(self, client):
        """TC-M01-021: 会话列表分页"""
        response = client.get('/api/v1/agent/sessions?page=1&page_size=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['page'] == 1
        assert data['page_size'] == 10
    
    def test_delete_session(self, client):
        """TC-M01-023: 删除会话"""
        # 创建会话
        create_response = client.post('/api/v1/agent/sessions',
                                     data=json.dumps({'title': '待删除会话'}),
                                     content_type='application/json')
        session_id = json.loads(create_response.data)['session_id']
        
        # 删除会话
        response = client.delete(f'/api/v1/agent/sessions/{session_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['deleted'] is True
        assert data['session_id'] == session_id
    
    def test_delete_session_not_found(self, client):
        """TC-M01-024: 删除不存在的会话"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f'/api/v1/agent/sessions/{fake_id}')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'SESSION_NOT_FOUND'
    
    def test_delete_session_invalid_id(self, client):
        """TC-M01-024: 删除会话ID格式错误"""
        response = client.delete('/api/v1/agent/sessions/invalid-id')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_SESSION_ID'

class TestQAAPI:
    """问答API测试"""
    
    def test_ask_question(self, client):
        """TC-M01-030: 问答提交"""
        # 创建会话
        create_response = client.post('/api/v1/agent/sessions',
                                     data=json.dumps({}),
                                     content_type='application/json')
        session_id = json.loads(create_response.data)['session_id']
        
        # 提交问题
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': session_id,
                                  'query': '测试问题'
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert 'answer' in data
        assert 'llm_used' in data
        assert 'model' in data
        assert 'response_time_ms' in data
        assert 'answer_source' in data
    
    def test_ask_empty_query(self, client):
        """TC-M01-031: 空问题"""
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': str(uuid.uuid4()),
                                  'query': ''
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'EMPTY_QUERY'
    
    def test_ask_query_too_long(self, client):
        """TC-M01-032: 问题超过500字符"""
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': str(uuid.uuid4()),
                                  'query': 'x' * 501
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_QUERY'
    
    def test_ask_empty_session_id(self, client):
        """TC-M01-033: 空会话ID"""
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': '',
                                  'query': '测试问题'
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'EMPTY_SESSION_ID'
    
    def test_ask_invalid_session_id(self, client):
        """TC-M01-034: 会话ID格式错误"""
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': 'invalid-id',
                                  'query': '测试问题'
                              }),
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_SESSION_ID'
    
    def test_ask_session_not_found(self, client):
        """TC-M01-035: 会话不存在"""
        response = client.post('/api/v1/agent/ask',
                              data=json.dumps({
                                  'session_id': str(uuid.uuid4()),
                                  'query': '测试问题'
                              }),
                              content_type='application/json')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error']['code'] == 'SESSION_NOT_FOUND'
    
    def test_get_session_records(self, client):
        """TC-M01-036: 问答记录查询"""
        # 创建会话并提问
        create_response = client.post('/api/v1/agent/sessions',
                                     data=json.dumps({}),
                                     content_type='application/json')
        session_id = json.loads(create_response.data)['session_id']
        
        client.post('/api/v1/agent/ask',
                   data=json.dumps({
                       'session_id': session_id,
                       'query': '测试问题'
                   }),
                   content_type='application/json')
        
        # 查询记录
        response = client.get(f'/api/v1/agent/sessions/{session_id}/records')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert data['session_id'] == session_id
        assert 'total' in data
        assert 'records' in data
        assert isinstance(data['records'], list)

class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """TC-M01-080: 健康检查"""
        response = client.get('/api/v1/agent/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'traceId' in data
        assert 'status' in data
        assert data['status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'timestamp' in data
        assert 'services' in data
        assert 'metrics' in data
