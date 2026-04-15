// 塔罗牌池（9张卡供抽取）
export const tarotCardPool = [
  { id: 1, name: '咸鱼翻身失败', description: '翻了个身，还是咸鱼。' },
  { id: 2, name: '疯狂摸鱼中', description: '鱼没摸到，水被搅浑了。' },
  { id: 3, name: '宇宙级摆烂', description: '万物归寂，我亦不动。' },
  { id: 4, name: '进击的咸鱼', description: '虽然是咸鱼，但在冲刺。' },
  { id: 5, name: '凌晨三点的猫头鹰', description: '夜越深，我越清醒。' },
  { id: 6, name: '发光的热干面', description: '不是每碗面都值得发光。' },
  { id: 7, name: '量子纠缠的袜子', description: '总有一只在另一个维度。' },
  { id: 8, name: '薛定谔的KPI', description: '不看就既完成又没完成。' },
  { id: 9, name: '反向锦鲤', description: '许的愿反着来。' },
];

// 命运三阶段配置
export const fatePhases = [
  { key: 'past', label: '过去', labelEn: 'PAST', subLabel: '起因', rarity: '普通' },
  { key: 'present', label: '现在', labelEn: 'PRESENT', subLabel: '纠缠', rarity: '稀有' },
  { key: 'future', label: '未来', labelEn: 'FUTURE', subLabel: '劫数', rarity: '传说' },
];

// 骰子结果
export const diceResults = [
  { face: 1, label: '命定之虚无', rot: 'rotateX(0deg) rotateY(0deg)' },
  { face: 2, label: '二元对立', rot: 'rotateX(-90deg) rotateY(0deg)' },
  { face: 3, label: '三重真理', rot: 'rotateY(-90deg) rotateZ(0deg)' },
  { face: 4, label: '四大基本力', rot: 'rotateY(90deg) rotateZ(0deg)' },
  { face: 5, label: '五维震荡', rot: 'rotateX(90deg) rotateY(0deg)' },
  { face: 6, label: '命运超活跃', rot: 'rotateY(180deg) rotateZ(0deg)' },
];

// 命运属性
export const fateAttributes = [
  { key: 'luck', label: '运势', icon: 'star', value: 88, color: 'primary', unit: '%' },
  { key: 'madness', label: '发疯值', icon: 'psychology', value: 100, color: 'tertiary', unit: 'MAX' },
  { key: 'action', label: '行动力', icon: 'bolt', value: 12, color: 'secondary', unit: '%' },
];

// 报告页引言
export const reportQuotes = [
  {
    text: '你的命运就像掉在沙滩上的冰淇淋，虽然可惜，但很有艺术感。',
    highlights: [
      { word: '冰淇淋', color: 'text-tertiary' },
      { word: '艺术感', color: 'text-secondary italic underline' },
    ],
  },
];

// 系统术语
export const systemTerms = {
  karmaPoints: '+1,204',
  dimensionRank: '混沌',
};
