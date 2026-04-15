# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | VO-001 |
| 模块名称 | Vibe Oracle 命运卡仪式体验 |
| 文档版本 | v0.2 |
| 阶段 | Design（契约真源） |
| Base URL | N/A（纯前端应用，无后端 API） |

---

> **本文档说明**：Vibe Oracle 是一个纯前端应用，无后端服务。本文档定义应用内部的**模块间接口契约**，包括：
> - React 自定义 Hooks 接口（状态管理）
> - 数据结构定义
> - 工具函数接口
> - 存储接口（localStorage）

## 1. 接口总览

| # | 接口类型 | 名称 | 功能 | 所在文件 |
|---|----------|------|------|----------|
| 1 | Hook | useRitualState | 全局仪式状态管理 | hooks/useRitualState.js |
| 2 | Data | tarotCardPool | 塔罗牌池数据 | data/mockData.js |
| 3 | Data | fatePhases | 命运三阶段配置 | data/mockData.js |
| 4 | Data | diceResults | 骰子结果数据 | data/mockData.js |
| 5 | Data | fateAttributes | 命运属性配置 | data/mockData.js |
| 6 | Data | reportQuotes | 报告引言数据 | data/mockData.js |
| 7 | Storage | localStorage | 历史记录持久化 | utils/storage.js |

## 2. 状态枚举定义

### 2.1 GameState（游戏阶段）

```typescript
type GameState = 'loading' | 'dice' | 'draw' | 'reveal' | 'report';

const STATES = {
  LOADING: 'loading',   // 加载页/入口页
  DICE: 'dice',         // 骰子仪式
  DRAW: 'draw',         // 抽卡阶段
  REVEAL: 'reveal',     // 揭示命运
  REPORT: 'report',     // 结局报告
} as const;
```

### 2.2 FateChoice（命运选择）

```typescript
type FateChoice = 'change' | 'accept' | null;
```

| 值 | 说明 |
|---|---|
| 'change' | 用户选择改命 |
| 'accept' | 用户接受命运 |
| null | 尚未做出选择 |

## 3. 核心数据结构

### 3.1 Card（塔罗牌）

```typescript
interface Card {
  id: number;           // 卡牌ID（1-9）
  name: string;         // 卡牌名称，如"咸鱼翻身失败"
  description: string;  // 卡牌描述
}
```

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | number | 卡牌唯一标识 | 1 |
| name | string | 卡牌标题（2-10字符） | "咸鱼翻身失败" |
| description | string | 卡牌描述（5-30字符） | "翻了个身，还是咸鱼。" |

### 3.2 FatePhase（命运阶段）

```typescript
interface FatePhase {
  key: 'past' | 'present' | 'future';
  label: string;        // 中文标签
  labelEn: string;      // 英文标签
  subLabel: string;     // 副标签
  rarity: string;       // 稀有度
}
```

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| key | string | 阶段标识 | 'past' |
| label | string | 中文标签 | "过去" |
| labelEn | string | 英文标签 | "PAST" |
| subLabel | string | 副标签 | "起因" |
| rarity | string | 稀有度 | "普通" |

### 3.3 DiceResult（骰子结果）

```typescript
interface DiceResult {
  face: number;         // 骰子面值（1-6）
  label: string;        // 结果标签
  rot: string;          // 3D旋转CSS值
}
```

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| face | number | 骰子面值 | 1 |
| label | string | 结果标签 | "命定之虚无" |
| rot | string | 3D旋转值 | "rotateX(0deg) rotateY(0deg)" |

### 3.4 FateAttribute（命运属性）

```typescript
interface FateAttribute {
  key: string;          // 属性标识
  label: string;        // 属性名称
  icon: string;         // Material Icons图标名
  value: number;        // 属性值（0-100）
  color: 'primary' | 'secondary' | 'tertiary';  // 颜色主题
  unit: string;         // 单位（"%" 或 "MAX"）
}
```

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| key | string | 属性标识 | 'luck' |
| label | string | 属性名称 | "运势" |
| icon | string | 图标名 | "star" |
| value | number | 属性值 | 88 |
| color | string | 颜色主题 | 'primary' |
| unit | string | 单位 | "%" |

### 3.5 ReportQuote（报告引言）

```typescript
interface ReportQuote {
  text: string;         // 引言文本
  highlights: {         // 高亮词配置
    word: string;       // 高亮词
    color: string;      // CSS类名
  }[];
}
```

## 4. useRitualState Hook 接口

### 4.1 返回值类型

```typescript
interface UseRitualStateReturn {
  // 状态
  currentState: GameState;
  selectedCards: number[];      // 选中的卡牌索引数组
  diceResult: DiceResult | null;
  fateChoice: FateChoice;
  
  // 状态常量
  STATES: typeof STATES;
  
  // 操作方法
  goToNextState: () => void;
  skipDice: () => void;
  selectCard: (cardIndex: number) => void;
  changeFate: () => void;
  acceptFate: () => void;
  restart: () => void;
  setDiceResult: (result: DiceResult) => void;
}
```

### 4.2 方法清单

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| goToNextState | - | void | 进入下一阶段（loading→dice→draw→reveal→report） |
| skipDice | - | void | 跳过骰子阶段，直接进入抽卡 |
| selectCard | cardIndex: number | void | 选择/取消选择卡牌（toggle逻辑） |
| changeFate | - | void | 选择改命，进入报告页 |
| acceptFate | - | void | 接受命运，进入报告页 |
| restart | - | void | 重置所有状态，回到加载页 |
| setDiceResult | result: DiceResult | void | 设置骰子结果 |

### 4.3 状态转换规则

```
loading → dice → draw → reveal → report → loading（循环）
                  ↑
                  └── skipDice 可直接跳到此处
```

| 当前状态 | goToNextState 目标 | 说明 |
|----------|-------------------|------|
| loading | dice | 加载完成进入骰子仪式 |
| dice | draw | 骰子完成进入抽卡 |
| draw | reveal | 抽卡完成进入揭示 |
| reveal | report | 揭示完成进入报告 |
| report | loading | 报告完成重新开始 |

### 4.4 selectCard 行为

```typescript
// 选择逻辑：toggle模式，最多选3张
selectCard(cardIndex: number) {
  if (selectedCards.includes(cardIndex)) {
    // 已选中则取消
    selectedCards = selectedCards.filter(i => i !== cardIndex);
  } else if (selectedCards.length < 3) {
    // 未满3张则添加
    selectedCards = [...selectedCards, cardIndex];
  }
  // 已满3张且不在数组中则忽略
}
```

## 5. 数据配置清单

### 5.1 tarotCardPool（塔罗牌池）

共9张卡牌，所有阶段共用：

| ID | 名称 | 描述 |
|----|------|------|
| 1 | 咸鱼翻身失败 | 翻了个身，还是咸鱼。 |
| 2 | 疯狂摸鱼中 | 鱼没摸到，水被搅浑了。 |
| 3 | 宇宙级摆烂 | 万物归寂，我亦不动。 |
| 4 | 进击的咸鱼 | 虽然是咸鱼，但在冲刺。 |
| 5 | 凌晨三点的猫头鹰 | 夜越深，我越清醒。 |
| 6 | 发光的热干面 | 不是每碗面都值得发光。 |
| 7 | 量子纠缠的袜子 | 总有一只在另一个维度。 |
| 8 | 薛定谔的KPI | 不看就既完成又没完成。 |
| 9 | 反向锦鲤 | 许的愿反着来。 |

### 5.2 fatePhases（命运阶段）

| key | label | labelEn | subLabel | rarity |
|-----|-------|---------|----------|--------|
| past | 过去 | PAST | 起因 | 普通 |
| present | 现在 | PRESENT | 纠缠 | 稀有 |
| future | 未来 | FUTURE | 劫数 | 传说 |

### 5.3 fateAttributes（命运属性）

| key | label | icon | value | color | unit |
|-----|-------|------|-------|-------|------|
| luck | 运势 | star | 88 | primary | % |
| madness | 发疯值 | psychology | 100 | tertiary | MAX |
| action | 行动力 | bolt | 12 | secondary | % |

## 6. Storage 接口

```typescript
interface StorageAPI {
  get: <T>(key: string, defaultValue?: T) => T | null;
  set: <T>(key: string, value: T) => boolean;
  remove: (key: string) => void;
  clear: () => void;
}

const STORAGE_KEYS = {
  HISTORY: 'vibe-oracle-history',
  PREFERENCES: 'vibe-oracle-prefs',
} as const;
```

| 方法 | 键 | 说明 |
|------|-----|------|
| getHistory | vibe-oracle-history | 获取历史记录数组 |
| setHistory | vibe-oracle-history | 保存历史记录数组 |
| getPreferences | vibe-oracle-prefs | 获取用户偏好 |
| setPreferences | vibe-oracle-prefs | 保存用户偏好 |

## 7. 错误处理

| 场景 | 错误类型 | 处理方式 |
|------|----------|----------|
| 存储空间不足 | QuotaExceededError | 清理旧记录后重试 |
| 数据解析失败 | SyntaxError | 返回默认值，console.warn |
| localStorage不可用 | TypeError | 使用内存存储，无持久化 |

## 8. 参数校验规则

| 接口 | 参数 | 规则 | 失败处理 |
|------|------|------|----------|
| selectCard | cardIndex | number类型，0-8范围内 | 忽略操作 |
| setDiceResult | result | 非null对象 | 忽略操作 |
| Storage.set | value | 可JSON序列化 | 返回false |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.2 | 2026-04-15 | 根据前端实现重构，简化接口设计 |
| v0.1 | 2026-04-15 | 首版（纯前端应用，定义内部接口契约） |
