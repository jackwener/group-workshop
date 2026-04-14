import sys
import os
import io
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wsgi import create_app

BASE = '/api/v1/agent'


@pytest.fixture
def client(tmp_path):
    app = create_app(data_dir=str(tmp_path))
    app.config['TESTING'] = True
    for fname in ['sessions.json', 'qa_records.json', 'reports.json']:
        fpath = os.path.join(str(tmp_path), fname)
        if not os.path.exists(fpath):
            with open(fpath, 'w') as f:
                f.write('[]')
    with app.test_client() as c:
        yield c


def _create_session(client, title="测试会话"):
    resp = client.post(f'{BASE}/sessions', json={"title": title})
    data = resp.get_json()
    return data['data']


def _create_report(client, tmp_path=None):
    """创建一个测试用的 PDF 研报"""
    data = io.BytesIO(b'%PDF-1.4 test content with rating: buy target: 50yuan')
    resp = client.post(f'{BASE}/reports', data={
        'file': (data, 'test_report.pdf'),
        'title': '测试研报'
    }, content_type='multipart/form-data')
    return resp.get_json()['data']


def _assert_trace_id(resp_json):
    """断言 traceId 存在"""
    if 'traceId' in resp_json:
        assert resp_json['traceId']
    elif 'error' in resp_json and 'traceId' in resp_json['error']:
        assert resp_json['error']['traceId']


# ========== 3.1 问答提交（4条）==========

def test_ask_normal(client):
    """TC-M01-001: POST /ask 正常问答"""
    session = _create_session(client)
    resp = client.post(f'{BASE}/ask', json={
        'query': '什么是投资评级？',
        'session_id': session['session_id']
    })
    assert resp.status_code == 200
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['success'] is True
    assert 'answer' in data['data']
    assert 'llm_used' in data['data']
    assert 'answer_source' in data['data']


def test_ask_empty_query(client):
    """TC-M01-002: 空 query → 400, EMPTY_QUERY"""
    session = _create_session(client)
    resp = client.post(f'{BASE}/ask', json={
        'query': '',
        'session_id': session['session_id']
    })
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['error']['code'] == 'EMPTY_QUERY'


def test_ask_long_query(client):
    """TC-M01-003: query > 500 字符 → 400, INVALID_QUERY"""
    session = _create_session(client)
    resp = client.post(f'{BASE}/ask', json={
        'query': 'x' * 501,
        'session_id': session['session_id']
    })
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['error']['code'] == 'INVALID_QUERY'


def test_ask_demo_mode(client):
    """TC-M01-004: 无 API Key → demo 模式"""
    session = _create_session(client)
    resp = client.post(f'{BASE}/ask', json={
        'query': '测试问题',
        'session_id': session['session_id']
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['data']['answer_source'] == 'demo'
    assert data['data']['llm_used'] is False


# ========== 3.2 会话管理（6条）==========

def test_get_sessions(client):
    """TC-M01-020: GET /sessions → 200, sessions 倒序"""
    _create_session(client, "会话1")
    import time; time.sleep(1.1)
    _create_session(client, "会话2")
    resp = client.get(f'{BASE}/sessions')
    assert resp.status_code == 200
    data = resp.get_json()
    _assert_trace_id(data)
    sessions = data['data']['sessions']
    assert len(sessions) == 2
    assert sessions[0]['title'] == '会话2'  # 最新的在前


def test_create_session(client):
    """TC-M01-021: POST /sessions → 201"""
    resp = client.post(f'{BASE}/sessions', json={"title": "新会话"})
    assert resp.status_code == 201
    data = resp.get_json()
    _assert_trace_id(data)
    assert 'session_id' in data['data']
    assert data['data']['title'] == '新会话'


def test_delete_session_cascade(client):
    """TC-M01-022: DELETE → 200, 级联删除"""
    session = _create_session(client)
    sid = session['session_id']
    # 添加一条问答记录
    client.post(f'{BASE}/ask', json={'query': '问题', 'session_id': sid})
    # 删除
    resp = client.delete(f'{BASE}/sessions/{sid}')
    assert resp.status_code == 200
    _assert_trace_id(resp.get_json())
    # 验证记录也被删除
    resp2 = client.get(f'{BASE}/sessions/{sid}/records')
    assert resp2.status_code == 404  # SESSION_NOT_FOUND


def test_delete_nonexistent_session(client):
    """TC-M01-023: DELETE 不存在 → 404, SESSION_NOT_FOUND"""
    resp = client.delete(f'{BASE}/sessions/nonexistent-id')
    assert resp.status_code == 404
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['error']['code'] == 'SESSION_NOT_FOUND'


def test_update_session(client):
    """TC-M01-024: PUT → 200, title 更新"""
    session = _create_session(client)
    resp = client.put(f'{BASE}/sessions/{session["session_id"]}', json={"title": "新标题"})
    assert resp.status_code == 200
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['data']['title'] == '新标题'


def test_create_session_title_too_long(client):
    """TC-M01-025: title > 100 → 400"""
    resp = client.post(f'{BASE}/sessions', json={"title": "a" * 101})
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_trace_id(data)


# ========== 3.3 问答记录（3条）==========

def test_get_records_with_data(client):
    """TC-M01-030: GET /records → 200, 有记录"""
    session = _create_session(client)
    sid = session['session_id']
    client.post(f'{BASE}/ask', json={'query': '问题', 'session_id': sid})
    resp = client.get(f'{BASE}/sessions/{sid}/records')
    assert resp.status_code == 200
    data = resp.get_json()
    _assert_trace_id(data)
    records = data['data']['records']
    assert len(records) >= 1
    assert 'query' in records[0]
    assert 'answer' in records[0]
    assert 'answer_source' in records[0]


def test_get_records_empty(client):
    """TC-M01-031: GET /records → 200, 无记录"""
    session = _create_session(client)
    resp = client.get(f'{BASE}/sessions/{session["session_id"]}/records')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['data']['records'] == []


def test_get_records_nonexistent(client):
    """TC-M01-032: GET /records 不存在 session → 404"""
    resp = client.get(f'{BASE}/sessions/bad-id/records')
    assert resp.status_code == 404
    data = resp.get_json()
    _assert_trace_id(data)
    assert data['error']['code'] == 'SESSION_NOT_FOUND'


# ========== 3.4 研报管理（10条）==========

def test_upload_report(client):
    """TC-M01-048: POST /reports 上传 PDF → 201"""
    data = io.BytesIO(b'%PDF-1.4 test content')
    resp = client.post(f'{BASE}/reports', data={
        'file': (data, 'test.pdf'),
        'title': '测试研报'
    }, content_type='multipart/form-data')
    assert resp.status_code == 201
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert json_data['data']['status'] == 'pending'


def test_upload_invalid_type(client):
    """TC-M01-049: 非 PDF/HTML → 400, INVALID_FILE_TYPE"""
    data = io.BytesIO(b'text content')
    resp = client.post(f'{BASE}/reports', data={
        'file': (data, 'test.txt'),
    }, content_type='multipart/form-data')
    assert resp.status_code == 400
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert json_data['error']['code'] == 'INVALID_FILE_TYPE'


def test_get_reports(client):
    """TC-M01-050: GET /reports → 200"""
    # 先上传一个
    data = io.BytesIO(b'%PDF-1.4 test')
    client.post(f'{BASE}/reports', data={'file': (data, 'test.pdf')}, content_type='multipart/form-data')
    resp = client.get(f'{BASE}/reports')
    assert resp.status_code == 200
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert 'items' in json_data['data']


def test_get_report_detail(client):
    """TC-M01-051: GET /reports/<id> → 200"""
    report = _create_report(client)
    resp = client.get(f'{BASE}/reports/{report["report_id"]}')
    assert resp.status_code == 200
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert json_data['data']['report_id'] == report['report_id']


def test_delete_report(client):
    """TC-M01-052: DELETE /reports/<id> → 200"""
    report = _create_report(client)
    resp = client.delete(f'{BASE}/reports/{report["report_id"]}')
    assert resp.status_code == 200
    _assert_trace_id(resp.get_json())
    # 验证已删除
    resp2 = client.get(f'{BASE}/reports/{report["report_id"]}')
    assert resp2.status_code == 404


def test_mark_report(client):
    """TC-M01-053: PUT /reports/<id>/mark → 200"""
    report = _create_report(client)
    resp = client.put(f'{BASE}/reports/{report["report_id"]}/mark', json={
        'is_marked': True,
        'mark_status': 'important'
    })
    assert resp.status_code == 200
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert json_data['data']['is_marked'] is True


def test_parse_report(client):
    """TC-M01-054: POST /reports/<id>/parse → 200"""
    # 创建一个包含评级关键词的 HTML 研报
    html_content = b'<html><body><h1>Test Report</h1><p>rating: buy target: 50yuan core view 1</p><p>investment rating: recommend</p></body></html>'
    resp = client.post(f'{BASE}/reports', data={
        'file': (io.BytesIO(html_content), 'test.html'),
        'title': 'HTML研报'
    }, content_type='multipart/form-data')
    report = resp.get_json()['data']
    
    resp2 = client.post(f'{BASE}/reports/{report["report_id"]}/parse')
    assert resp2.status_code == 200
    json_data = resp2.get_json()
    _assert_trace_id(json_data)
    assert 'title' in json_data['data']


def test_parse_report_time(client):
    """TC-M01-055: 解析耗时 < 5000ms"""
    html_content = b'<html><body><h1>Performance Test</h1><p>content</p></body></html>'
    resp = client.post(f'{BASE}/reports', data={
        'file': (io.BytesIO(html_content), 'perf.html'),
    }, content_type='multipart/form-data')
    report = resp.get_json()['data']
    
    resp2 = client.post(f'{BASE}/reports/{report["report_id"]}/parse')
    assert resp2.status_code == 200
    json_data = resp2.get_json()
    assert json_data['data'].get('parse_time_ms', 0) < 5000


def test_compare_reports(client):
    """TC-M01-056: POST /reports/compare 2-10份 → 200"""
    # 创建两个研报
    r1 = _create_report(client)
    r2 = _create_report(client)
    
    resp = client.post(f'{BASE}/reports/compare', json={
        'report_ids': [r1['report_id'], r2['report_id']]
    })
    assert resp.status_code == 200
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert 'headers' in json_data['data']
    assert 'rows' in json_data['data']


def test_compare_too_few(client):
    """TC-M01-057: compare < 2份 → 400, INVALID_REPORT_SELECTION"""
    r1 = _create_report(client)
    resp = client.post(f'{BASE}/reports/compare', json={
        'report_ids': [r1['report_id']]
    })
    assert resp.status_code == 400
    json_data = resp.get_json()
    _assert_trace_id(json_data)
    assert json_data['error']['code'] == 'INVALID_REPORT_SELECTION'
