/**
 * 投研智能问答助手 - 后端服务
 * 支持百炼 API 调用 + Demo 降级
 */
const http = require('http');
const https = require('https');
const url = require('url');
const fs = require('fs');
const path = require('path');

const PORT = 5000;
const DATA_DIR = path.join(__dirname, '..', 'data');

// 百炼 API 配置
const DASHSCOPE_API_KEY = process.env.DASHSCOPE_API_KEY || '';
const DASHSCOPE_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation';

// 确保数据目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

const SESSIONS_FILE = path.join(DATA_DIR, 'sessions.json');
const RECORDS_FILE = path.join(DATA_DIR, 'qa_records.json');

// 初始化数据文件
function initDataFiles() {
  if (!fs.existsSync(SESSIONS_FILE)) {
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify([], null, 2));
  }
  if (!fs.existsSync(RECORDS_FILE)) {
    fs.writeFileSync(RECORDS_FILE, JSON.stringify([], null, 2));
  }
}

initDataFiles();

// 生成 traceId
function generateTraceId() {
  return 'tr_' + Math.random().toString(36).substring(2, 34);
}

// 生成 UUID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 读取 JSON 文件
function readJSON(filepath) {
  try {
    const data = fs.readFileSync(filepath, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    return [];
  }
}

// 写入 JSON 文件
function writeJSON(filepath, data) {
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
}

// 模拟问答回答（Demo 降级）
function generateDemoAnswer(query) {
  const answers = [
    `关于"${query}"，根据最新的市场数据分析，该领域呈现出稳定增长的趋势。建议您关注相关的行业报告以获取更详细的信息。`,
    `针对您的问题"${query}"，我们的研究显示该主题涉及多个关键因素。主要观点包括市场动态、政策影响和技术发展等方面。`,
    `感谢您的提问。关于"${query}"，目前可获取的信息显示这是一个复杂的话题，需要综合考虑宏观经济环境和行业发展趋势。`,
    `根据当前可用的数据，"${query}"相关的问题可以从以下几个角度分析：1) 历史表现 2) 未来预期 3) 风险评估。建议您进一步深入研究。`
  ];
  return answers[Math.floor(Math.random() * answers.length)];
}

// 调用百炼 API
function callBailianAPI(query) {
  return new Promise((resolve, reject) => {
    if (!DASHSCOPE_API_KEY) {
      reject(new Error('DASHSCOPE_API_KEY not configured'));
      return;
    }

    const requestData = JSON.stringify({
      model: 'qwen-turbo',
      input: {
        messages: [
          { role: 'system', content: '你是一个专业的投研问答助手，擅长分析金融市场和投资相关问题。' },
          { role: 'user', content: query }
        ]
      },
      parameters: {
        result_format: 'message',
        max_tokens: 1500,
        temperature: 0.7
      }
    });

    const options = {
      hostname: 'dashscope.aliyuncs.com',
      path: '/api/v1/services/aigc/text-generation/generation',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(requestData)
      },
      timeout: 120000 // 120秒超时
    };

    const req = https.request(options, (res) => {
      let data = Buffer.alloc(0);
      res.on('data', (chunk) => data = Buffer.concat([data, chunk]));
      res.on('end', () => {
        const responseText = data.toString('utf8');
        try {
          const response = JSON.parse(responseText);
          if (response.output && response.output.choices && response.output.choices[0]) {
            resolve({
              answer: response.output.choices[0].message.content,
              model: response.model || 'qwen-turbo',
              usage: response.usage
            });
          } else if (response.message) {
            reject(new Error(response.message));
          } else {
            reject(new Error('Invalid response format'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.write(requestData);
    req.end();
  });
}

// CORS 头
function setCORSHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// 路由处理
const server = http.createServer((req, res) => {
  setCORSHeaders(res);
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const traceId = generateTraceId();

  console.log(`${req.method} ${path}`);

  // GET /api/v1/agent/capabilities
  if (path === '/api/v1/agent/capabilities' && req.method === 'GET') {
    const bailianConfigured = !!DASHSCOPE_API_KEY;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      traceId,
      data: {
        copaw_configured: false,
        bailian_configured: bailianConfigured,
        mode: bailianConfigured ? 'bailian' : 'demo',
        model: bailianConfigured ? 'qwen-turbo' : null,
        version: '0.1.0'
      }
    }));
    return;
  }

  // POST /api/v1/agent/ask
  if (path === '/api/v1/agent/ask' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const { query, session_id } = JSON.parse(body);
        const recordId = generateUUID();
        const startTime = Date.now();
        
        // 确保查询文本正确解码
        const decodedQuery = Buffer.from(query).toString('utf8');
        
        let answer, answerSource, llm, model;
        
        // 三级降级：百炼 -> Demo
        try {
          if (DASHSCOPE_API_KEY) {
            console.log(`[Bailian] Calling API for query: ${decodedQuery.substring(0, 50)}...`);
            const result = await callBailianAPI(decodedQuery);
            answer = result.answer;
            answerSource = 'bailian';
            llm = true;
            model = result.model;
            console.log(`[Bailian] Success, model: ${model}`);
          } else {
            throw new Error('Bailian not configured');
          }
        } catch (err) {
          console.log(`[Bailian] Failed: ${err.message}, falling back to Demo`);
          answer = generateDemoAnswer(decodedQuery);
          answerSource = 'demo';
          llm = false;
          model = null;
        }
        
        const elapsedMs = Date.now() - startTime;
        
        // 保存记录
        const records = readJSON(RECORDS_FILE);
        records.push({
          record_id: recordId,
          session_id: session_id,
          query: query,
          answer: answer,
          answer_source: answerSource,
          llm: llm,
          created_at: new Date().toISOString()
        });
        writeJSON(RECORDS_FILE, records);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          traceId,
          data: {
            record_id: recordId,
            answer: answer,
            answer_source: answerSource,
            llm: llm,
            model: model,
            elapsed_ms: elapsedMs
          }
        }));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          error: {
            code: 'INVALID_REQUEST',
            message: 'Invalid request body',
            details: {},
            traceId
          }
        }));
      }
    });
    return;
  }

  // GET /api/v1/agent/sessions
  if (path === '/api/v1/agent/sessions' && req.method === 'GET') {
    const sessions = readJSON(SESSIONS_FILE);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      traceId,
      data: { sessions }
    }));
    return;
  }

  // POST /api/v1/agent/sessions
  if (path === '/api/v1/agent/sessions' && req.method === 'POST') {
    const sessionId = generateUUID();
    const session = {
      session_id: sessionId,
      title: '新会话',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    const sessions = readJSON(SESSIONS_FILE);
    sessions.push(session);
    writeJSON(SESSIONS_FILE, sessions);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      traceId,
      data: session
    }));
    return;
  }

  // DELETE /api/v1/agent/sessions/:id
  const deleteMatch = path.match(/^\/api\/v1\/agent\/sessions\/([^\/]+)$/);
  if (deleteMatch && req.method === 'DELETE') {
    const sessionId = deleteMatch[1];
    let sessions = readJSON(SESSIONS_FILE);
    const initialLength = sessions.length;
    sessions = sessions.filter(s => s.session_id !== sessionId);
    writeJSON(SESSIONS_FILE, sessions);
    
    // 同时删除相关记录
    let records = readJSON(RECORDS_FILE);
    records = records.filter(r => r.session_id !== sessionId);
    writeJSON(RECORDS_FILE, records);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      traceId,
      data: { deleted: initialLength - sessions.length }
    }));
    return;
  }

  // GET /api/v1/agent/sessions/:id/records
  const recordsMatch = path.match(/^\/api\/v1\/agent\/sessions\/([^\/]+)\/records$/);
  if (recordsMatch && req.method === 'GET') {
    const sessionId = recordsMatch[1];
    const records = readJSON(RECORDS_FILE).filter(r => r.session_id === sessionId);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      traceId,
      data: { records }
    }));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    error: {
      code: 'NOT_FOUND',
      message: 'Endpoint not found',
      details: {},
      traceId
    }
  }));
});

server.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('投研智能问答助手 - 后端服务');
  console.log('='.repeat(50));
  console.log(`API 地址: http://localhost:${PORT}/api/v1/agent`);
  console.log(`百炼 API: ${DASHSCOPE_API_KEY ? '已配置 ✓' : '未配置 (Demo模式)'}`);
  console.log('='.repeat(50));
});
