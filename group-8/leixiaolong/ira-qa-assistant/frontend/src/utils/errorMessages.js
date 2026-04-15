const ERROR_MESSAGES = {
  EMPTY_QUERY: '请输入问题',
  INVALID_QUERY: '问题过长（最多500字符）',
  INVALID_TITLE: '会话标题过长（最多100字符）',
  INVALID_SESSION_ID: '会话ID无效',
  SESSION_NOT_FOUND: '会话不存在，已自动刷新列表',
  PERMISSION_DENIED: '您没有访问权限，请联系管理员',
  FILE_TOO_LARGE: '文件大小超过10MB限制',
  UNSUPPORTED_FORMAT: '仅支持 PDF/Word/Excel 格式',
  LLM_UNAVAILABLE: 'AI服务暂时不可用，已切换到离线演示模式',
  UNKNOWN_ERROR: '请求失败，请稍后重试',
};

export function getErrorMessage(code) {
  return ERROR_MESSAGES[code] || ERROR_MESSAGES.UNKNOWN_ERROR;
}
