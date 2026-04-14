"""
API 集成测试
对齐 13-测试策略与质量门禁.md TC-004 系列
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestCapabilitiesAPI:
    """健康检查 API 测试"""
    
    def test_get_capabilities(self, client):
        """TC-004-01: 能力探测接口"""
        response = client.get('/api/v1/capabilities')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'traceId' in data
        assert 'copaw_configured' in data
        assert 'bailian_configured' in data
        assert isinstance(data['copaw_configured'], bool)
        assert isinstance(data['bailian_configured'], bool)


class TestSessionAPI:
    """会话管理 API 测试"""
    
    def test_create_session(self, client):
        """TC-001-01: 创建会话接口"""
        response = client.post('/api/v1/sessions',
                              data=json.dumps({'title': '测试会话'}),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'session_id' in data
        assert data['title'] == '测试会话'
        assert data['status'] == 'active'
    
    def test_get_sessions(self, client):
        """TC-001-01: 获取会话列表接口"""
        # 先创建一个会话
        client.post('/api/v1/sessions',
                   data=json.dumps({'title': '测试'}),
                   content_type='application/json')
        
        response = client.get('/api/v1/sessions')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)
    
    def test_delete_session_not_found(self, client):
        """TC-001-03: 删除不存在的会话"""
        response = client.delete('/api/v1/sessions/non-existent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == 'SESSION_NOT_FOUND'


class TestAskAPI:
    """问答提交 API 测试"""
    
    def test_ask_empty_query(self, client):
        """TC-002-02: 空问题校验"""
        response = client.post('/api/v1/ask',
                              data=json.dumps({
                                  'query': '',
                                  'session_id': 'test-id'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'EMPTY_QUERY'
    
    def test_ask_query_too_long(self, client):
        """TC-002-02: 问题超长校验"""
        response = client.post('/api/v1/ask',
                              data=json.dumps({
                                  'query': 'x' * 501,
                                  'session_id': 'test-id'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'INVALID_QUERY'
    
    def test_ask_session_not_found(self, client):
        """TC-002-02: 会话不存在校验"""
        response = client.post('/api/v1/ask',
                              data=json.dumps({
                                  'query': '测试问题',
                                  'session_id': 'non-existent-id'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'SESSION_NOT_FOUND'
    
    def test_ask_success(self, client):
        """TC-002-02: 问答提交成功"""
        # 先创建会话
        session_res = client.post('/api/v1/sessions',
                                  data=json.dumps({'title': '测试'}),
                                  content_type='application/json')
        session_data = json.loads(session_res.data)
        session_id = session_data['session_id']
        
        # 提交问题
        response = client.post('/api/v1/ask',
                              data=json.dumps({
                                  'query': '这是一个测试问题',
                                  'session_id': session_id
                              }),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'answer' in data
        assert 'llm_used' in data
        assert 'answer_source' in data
        assert 'response_time_ms' in data


class TestRecordsAPI:
    """问答记录 API 测试"""
    
    def test_get_records_session_not_found(self, client):
        """TC-003-01: 获取不存在会话的记录"""
        response = client.get('/api/v1/sessions/non-existent-id/records')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['error']['code'] == 'SESSION_NOT_FOUND'
