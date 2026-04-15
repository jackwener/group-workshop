# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | VO-001 |
| 模块名称 | Vibe Oracle 命运卡仪式体验 |
| 文档版本 | v0.1 |
| 阶段 | Design（契约真源） |
| Base URL | N/A（纯前端应用，无后端 API） |

---

> **本文档说明**：Vibe Oracle 是一个纯前端应用，无后端服务。本文档定义应用内部的**模块间接口契约**，包括：
> - React Context API（状态管理接口）
> - 自定义 Hooks 接口
> - 工具函数接口
> - 存储接口（localStorage）

## 1. 接口总览

| # | 接口类型 | 名称 | 功能 | 所在文件 |
|---|----------|------|------|----------|
| 1 | Context | GameContext | 全局游戏状态管理 | store/GameContext.tsx |
| 2 | Hook | useGame | 游戏主逻辑操作 | hooks/useGame.ts |
| 3 | Hook | useCards | 卡牌管理 | hooks/useCards.ts |
| 4 | Hook | useHistory | 历史记录管理 | hooks/useHistory.ts |
| 5 | Hook | usePerformance | 性能检测 | hooks/usePerformance.ts |
| 6 | Storage | localStorage | 数据持久化 | utils/storage.ts |

## 2. 统一响应规范

### 成功响应

```typescript
interface HookResult<T> {
  data: T;
  loading: boolean;
  error: Error | null;
}

interface ContextState<T> {
  state: T;
  dispatch: Dispatch<Action>;
}
```

### 错误响应

```typescript
interface AppError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

const ErrorCodes = {
  STORAGE_ERROR: '存储操作失败',
  STATE_ERROR: '状态操作无效',
  VALIDATION_ERROR: '参数验证失败',
  RENDER_ERROR: '渲染异常',
} as const;
```

## 3. GameContext 接口

### 3.1 状态定义

```typescript
interface GameState {
  phase: GamePhase;
  selectedCards: Card[];
  availableCards: Card[];
  currentReveal: number;
  ending: Ending | null;
  personality: Personality | null;
  warmUpResult: WarmUpResult | null;
  isChangingFate: boolean;
}

type GamePhase =
  | 'landing'
  | 'ritual'
  | 'altar'
  | 'revealing'
  | 'choice'
  | 'ending'
  | 'report'
  | 'share';
```

### 3.2 Action 定义

| Action | 参数 | 功能 |
|--------|------|------|
| START_RITUAL | - | 从入口页进入仪式动画 |
| COMPLETE_RITUAL | - | 仪式动画完成，进入祭坛 |
| SELECT_CARD | cardId: string | 选择一张卡牌 |
| REVEAL_COMPLETE | - | 当前卡牌揭示完成 |
| ACCEPT_FATE | - | 接受命运，进入结局 |
| CHANGE_FATE | - | 尝试改命，重新抽取 |
| SHOW_REPORT | - | 显示人格报告 |
| SHOW_SHARE | - | 显示分享卡 |
| RESET_GAME | - | 重置游戏状态 |
| SET_WARMUP_RESULT | result: WarmUpResult | 设置暖场结果 |

## 4. useGame Hook 接口

```typescript
interface UseGameReturn {
  phase: GamePhase;
  selectedCards: Card[];
  currentEnding: Ending | null;
  currentPersonality: Personality | null;

  startRitual: () => void;
  completeRitual: () => void;
  selectCard: (cardId: string) => Promise<void>;
  acceptFate: () => void;
  changeFate: () => void;
  showReport: () => void;
  showShare: () => void;
  resetGame: () => void;

  canSelectCard: (cardId: string) => boolean;
  isRevealing: boolean;
}
```

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| startRitual | - | void | 开始仪式动画 |
| completeRitual | - | void | 仪式完成，显示祭坛 |
| selectCard | cardId: string | Promise<void> | 选择卡牌，包含翻转动画 |
| acceptFate | - | void | 接受命运 |
| changeFate | - | void | 改命，重新抽取结果卡 |
| showReport | - | void | 显示人格报告 |
| showShare | - | void | 显示分享卡 |
| resetGame | - | void | 重置游戏 |
| canSelectCard | cardId: string | boolean | 检查卡牌是否可选 |

## 5. useCards Hook 接口

```typescript
interface UseCardsReturn {
  availableCards: Card[];
  selectedCards: Card[];
  currentCardPool: Card[];

  shuffleCards: () => void;
  drawCard: (type: CardType) => Card;
  revealCard: (cardId: string) => Promise<void>;
  resetCards: () => void;

  getCardById: (cardId: string) => Card | undefined;
  getCardsByType: (type: CardType) => Card[];
}

type CardType = 'state' | 'desire' | 'result';
```

## 6. useHistory Hook 接口

```typescript
interface UseHistoryReturn {
  records: HistoryRecord[];

  addRecord: (record: Omit<HistoryRecord, 'id' | 'timestamp'>) => void;
  deleteRecord: (recordId: string) => void;
  clearHistory: () => void;

  getRecordById: (recordId: string) => HistoryRecord | undefined;
}
```

## 7. usePerformance Hook 接口

```typescript
interface UsePerformanceReturn {
  level: 1 | 2 | 3 | 4;
  deviceMemory?: number;
  hardwareConcurrency?: number;
  prefersReducedMotion: boolean;

  enable3D: boolean;
  enableParticles: boolean;
  enableAnimations: boolean;
}
```

## 8. Storage 接口

```typescript
interface StorageAPI {
  get: <T>(key: string, defaultValue?: T) => T | null;
  set: <T>(key: string, value: T) => boolean;
  remove: (key: string) => void;
  clear: () => void;

  getHistory: () => HistoryRecord[];
  setHistory: (records: HistoryRecord[]) => boolean;
  getPreferences: () => UserPreferences;
  setPreferences: (prefs: UserPreferences) => boolean;
}

const STORAGE_KEYS = {
  HISTORY: 'vibe-oracle-history',
  PREFERENCES: 'vibe-oracle-prefs',
} as const;
```

| 场景 | 错误码 | 处理方式 |
|------|--------|----------|
| 存储空间不足 | STORAGE_FULL | 清理旧记录后重试 |
| 数据解析失败 | PARSE_ERROR | 返回默认值，记录日志 |
| 存储不可用 | NOT_AVAILABLE | 使用内存存储，无持久化 |

## 9. 参数校验规则汇总

| 接口 | 参数 | 规则 | 失败处理 |
|------|------|------|----------|
| selectCard | cardId | 非空字符串，存在于 availableCards | 忽略操作 |
| drawCard | type | 必须是 'state' | 'desire' | 'result' | 抛出错误 |
| addRecord | record.cards | 长度必须为 3 | 拒绝添加 |
| set | value | 可序列化为 JSON | 返回 false |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-15 | 首版（纯前端应用，定义内部接口契约） |
