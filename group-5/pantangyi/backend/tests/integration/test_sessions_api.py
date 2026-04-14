"""Integration tests for Session API."""
import json


class TestSessionsAPI:
    """Test cases for Session API (TC-M01-020~025)."""
    
    def test_create_session(self, client):
        """TC-M01-020: POST /sessions -> 201 with id/title/type/created_at."""
        response = client.post('/api/v1/sessions',
                              data=json.dumps({"title": "测试会话", "type": "stock"}),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data["code"] == 201
        assert data["message"] == "created"
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["title"] == "测试会话"
        assert data["data"]["type"] == "stock"
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]
    
    def test_create_session_default_values(self, client):
        """TC-M01-020: POST /sessions with default values."""
        response = client.post('/api/v1/sessions',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data["data"]["title"] == "新会话"
        assert data["data"]["type"] == "general"
    
    def test_list_sessions(self, client, session_dao):
        """TC-M01-021: GET /sessions -> 200 with items array and total."""
        # Create test sessions
        session_dao.create_session(title="会话1")
        session_dao.create_session(title="会话2")
        
        response = client.get('/api/v1/sessions?limit=5&offset=0')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["code"] == 200
        assert "data" in data
        assert "total" in data["data"]
        assert "items" in data["data"]
        assert data["data"]["total"] >= 2
        assert isinstance(data["data"]["items"], list)
        
        # Check item structure
        if len(data["data"]["items"]) > 0:
            item = data["data"]["items"][0]
            assert "id" in item
            assert "title" in item
            assert "type" in item
            assert "created_at" in item
            assert "updated_at" in item
    
    def test_list_sessions_default_pagination(self, client):
        """TC-M01-021: GET /sessions with default pagination."""
        response = client.get('/api/v1/sessions')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Default limit is 5
        assert len(data["data"]["items"]) <= 5
    
    def test_delete_session(self, client, session_dao):
        """TC-M01-022: DELETE /sessions/{id} -> 200, status becomes deleted."""
        session = session_dao.create_session(title="待删除会话")
        
        response = client.delete(f'/api/v1/sessions/{session.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["code"] == 200
        
        # Verify status changed
        session = session_dao.get_session(session.id)
        assert session.status == "deleted"
    
    def test_delete_session_not_found(self, client):
        """TC-M01-023: DELETE /sessions/{不存在id} -> 404, error code 404001."""
        response = client.delete('/api/v1/sessions/sess_nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data["code"] == 404001
        assert "message" in data
    
    def test_get_session_detail(self, client, session_dao):
        """TC-M01-024: GET /sessions/{id} -> 200 with messages list."""
        session = session_dao.create_session(title="详情测试")
        
        # Add a message
        from app.models.message import Message
        message = Message.create(
            message_id="msg_test",
            session_id=session.id,
            role="user",
            content="测试消息",
            msg_type="text"
        )
        session_dao.add_message(session.id, message)
        
        response = client.get(f'/api/v1/sessions/{session.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["code"] == 200
        assert "data" in data
        assert "messages" in data["data"]
        assert isinstance(data["data"]["messages"], list)
        assert len(data["data"]["messages"]) == 1
    
    def test_get_session_not_found(self, client):
        """TC-M01-025: GET /sessions/{不存在id} -> 404, error code 404001."""
        response = client.get('/api/v1/sessions/sess_nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data["code"] == 404001
    
    def test_send_message(self, client, session_dao):
        """TC-M01-040: POST /sessions/{id}/messages -> 200 with assistant reply."""
        session = session_dao.create_session(title="消息测试")
        
        response = client.post(f'/api/v1/sessions/{session.id}/messages',
                              data=json.dumps({"content": "你好", "type": "text"}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data["code"] == 200
        assert "data" in data
        assert data["data"]["role"] == "assistant"
        assert "content" in data["data"]
        assert "timestamp" in data["data"]
    
    def test_send_message_empty_content(self, client, session_dao):
        """TC-M01-041: POST /messages with empty content -> 400, error code 400001."""
        session = session_dao.create_session(title="消息测试")
        
        response = client.post(f'/api/v1/sessions/{session.id}/messages',
                              data=json.dumps({"content": "", "type": "text"}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data["code"] == 400001
    
    def test_send_message_session_not_found(self, client):
        """TC-M01-042: POST /sessions/{不存在id}/messages -> 404, error code 404001."""
        response = client.post('/api/v1/sessions/sess_nonexistent/messages',
                              data=json.dumps({"content": "你好", "type": "text"}),
                              content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data["code"] == 404001
