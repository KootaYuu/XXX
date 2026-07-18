// 静态数据：拟饵、鱼种、推荐规则用的标签

// 拟饵类型库
// tags: topwater 水面系 / shallow 浅层 / mid 中层 / deep 深层 /
//       slow 适合慢速 / noisy 声响振动强 / weedless 防挂 / micro 微物
export const LURES = [
  {
    id: 'pencil', name: '铅笔（Pencil）', emoji: '✏️',
    tags: ['topwater'],
    technique: '匀速抽停走"之"字（Walking the dog），炸水不中鱼时停顿 1-2 秒再抽。',
  },
  {
    id: 'popper', name: '波扒（Popper）', emoji: '💥',
    tags: ['topwater', 'noisy'],
    technique: '短促下压竿尖让嘴部噗水，节奏"啵—停—啵"，停顿时最容易被攻击。',
  },
  {
    id: 'frog', name: '雷蛙（Frog）', emoji: '🐸',
    tags: ['topwater', 'weedless'],
    technique: '贴着草面小幅度点动、停顿，炸水后默数一秒确认吃深再扬竿。',
  },
  {
    id: 'minnow', name: '米诺（Minnow）', emoji: '🐠',
    tags: ['shallow', 'mid'],
    technique: '匀收为主，配合抽停（Twitch & Pause），停顿瞬间常出咬口。',
  },
  {
    id: 'crank', name: '摇摆胖子（Crank）', emoji: '🥎',
    tags: ['mid', 'deep', 'noisy'],
    technique: '匀速收线让其撞击结构后停顿上浮，"碰—停—收"是标准节奏。',
  },
  {
    id: 'vib', name: 'VIB / 颤沉饵', emoji: '📳',
    tags: ['mid', 'deep', 'noisy', 'slow'],
    technique: '数秒沉底后跳底或匀收，冬季用小幅度慢跳，感觉线一顿立刻扬竿。',
  },
  {
    id: 'spoon', name: '亮片（Spoon）', emoji: '🥄',
    tags: ['shallow', 'mid', 'deep'],
    technique: '远投数秒下沉到目标泳层匀收，或收两圈停一下做出飘落动作。',
  },
  {
    id: 'micro-spoon', name: '微物亮片 / 瓜子亮片', emoji: '🌰',
    tags: ['shallow', 'micro'],
    technique: '轻竿细线匀速快收，溪流中斜下游 45° 抛投让水流带动泳姿。',
  },
  {
    id: 'spinner', name: '旋转亮片（Spinner）', emoji: '🌀',
    tags: ['shallow', 'mid', 'noisy', 'micro'],
    technique: '入水即收保持叶片旋转，过深潭时先沉几秒再收。',
  },
  {
    id: 'spinnerbait', name: '复合亮片（Spinnerbait）', emoji: '⚙️',
    tags: ['shallow', 'mid', 'noisy', 'weedless'],
    technique: '沿障碍区匀收，碰到木桩水草让它撞一下再继续，浑水利器。',
  },
  {
    id: 'soft-worm', name: '软虫（德州 / 无铅）', emoji: '🪱',
    tags: ['deep', 'slow', 'weedless'],
    technique: '沉底后轻挑竿尖拖动，走走停停，大部分咬口在下落和停顿中。',
  },
  {
    id: 'jighead', name: '铅头钩 + 卷尾蛆', emoji: '🎏',
    tags: ['mid', 'deep', 'slow'],
    technique: '沉底慢拖或小跳，贴底"敲石头"，鳜鱼标配手法。',
  },
];

export const LURE_MAP = Object.fromEntries(LURES.map((l) => [l.id, l]));

// 鱼种库（图鉴 + 推荐共用）
// lures: { 拟饵id: 权重 1-5 }
export const SPECIES = [
  {
    id: 'qiaozui', name: '翘嘴', latin: '翘嘴鲌', emoji: '🐟', difficulty: 2,
    seasons: ['春', '夏', '秋'], layer: '中上层',
    habitat: '水库、湖泊、江河的开阔水面，喜追捕小鱼群。',
    tip: '清晨傍晚水面炸水时用铅笔、波扒；白天沿桦尖打米诺、亮片远投搜索。',
    lures: { pencil: 5, minnow: 5, spoon: 4, vib: 4, popper: 3, crank: 2 },
  },
  {
    id: 'guiyu', name: '鳜鱼', latin: '桂花鱼', emoji: '🐡', difficulty: 4,
    seasons: ['春', '秋'], layer: '底层',
    habitat: '乱石堆、桥墩、倒树等结构区，伏击型猎手。',
    tip: '贴底慢是关键：铅头钩卷尾蛆敲底、软虫倒吊在结构边慢磨。',
    lures: { jighead: 5, 'soft-worm': 5, vib: 3, crank: 3, minnow: 2 },
  },
  {
    id: 'heiyu', name: '黑鱼', latin: '乌鳢', emoji: '🐍', difficulty: 3,
    seasons: ['夏', '秋'], layer: '水面 / 草区',
    habitat: '重草区、藕塘、浮萍下，雷强专属对象鱼。',
    tip: '雷蛙贴草面点动，炸水后等一秒再大力扬竿，装备要用雷强竿 + 8 编 PE。',
    lures: { frog: 5, 'soft-worm': 2, spinnerbait: 2 },
  },
  {
    id: 'jiazhoulu', name: '加州鲈', latin: '大口黑鲈', emoji: '🎣', difficulty: 3,
    seasons: ['春', '夏', '秋'], layer: '全泳层',
    habitat: '坑塘、水库的障碍区和陡坎，全泳层觅食。',
    tip: '德州软虫打障碍、复合亮片搜边、天热早晚水面系，标准路亚全能对象鱼。',
    lures: { 'soft-worm': 5, spinnerbait: 4, crank: 4, minnow: 3, pencil: 3, frog: 3, vib: 3, jighead: 3 },
  },
  {
    id: 'makou', name: '马口', latin: '马口鱼', emoji: '🐠', difficulty: 1,
    seasons: ['春', '夏', '秋'], layer: '中上层',
    habitat: '山间溪流、清澈浅滩的流水中。',
    tip: '微物装备 + 瓜子亮片快收，急流缓流交界处是黄金标点。',
    lures: { 'micro-spoon': 5, spinner: 4, minnow: 2 },
  },
  {
    id: 'baitiao', name: '白条', latin: '䱗', emoji: '🐟', difficulty: 1,
    seasons: ['春', '夏', '秋'], layer: '上层',
    habitat: '几乎所有水域的上层，成群活动。',
    tip: '微物亮片入水就收，中上层快速搜索，练手感的最佳对象鱼。',
    lures: { 'micro-spoon': 5, spinner: 4 },
  },
  {
    id: 'hongwei', name: '红尾', latin: '蒙古鲌', emoji: '🦈', difficulty: 2,
    seasons: ['春', '夏', '秋'], layer: '中上层',
    habitat: '江河湖库的流水口、坝下，喜集群追饵。',
    tip: '亮片、小米诺远投快收，找到鱼群后连竿不是梦。',
    lures: { spoon: 5, minnow: 4, vib: 3, spinner: 3 },
  },
  {
    id: 'nianyu', name: '鲶鱼', latin: '鲇', emoji: '🐋', difficulty: 2,
    seasons: ['夏'], layer: '底层',
    habitat: '桥洞、涵洞、缓流深水区，昼伏夜出。',
    tip: '夜钓为主，软虫、深潜米诺贴底慢收，声响大的饵更占优。',
    lures: { 'soft-worm': 4, jighead: 4, crank: 3, vib: 3 },
  },
  {
    id: 'huangsang', name: '黄辣丁', latin: '黄颡鱼', emoji: '🐤', difficulty: 2,
    seasons: ['夏'], layer: '底层',
    habitat: '缓流泥沙底、乱石缝，夜间活跃。',
    tip: '小号软虫或卷尾蛆贴底慢拖，傍晚到夜里口最好。',
    lures: { jighead: 5, 'soft-worm': 4 },
  },
  {
    id: 'junyu', name: '军鱼', latin: '光倒刺鲃', emoji: '🪖', difficulty: 4,
    seasons: ['夏', '秋'], layer: '中层',
    habitat: '南方山区溪河的急流深潭，力气极大。',
    tip: '亮片、米诺打急流白沫区，中鱼后注意控鱼别让它钻石缝。',
    lures: { spoon: 5, minnow: 4, spinner: 3, 'micro-spoon': 3 },
  },
  {
    id: 'luofei', name: '罗非', latin: '罗非鱼', emoji: '🍥', difficulty: 2,
    seasons: ['夏', '秋'], layer: '中下层',
    habitat: '南方水域，护巢期极具攻击性。',
    tip: '小饵慢收：微物亮片、小软虫打巢区附近，护巢期见饵就咬。',
    lures: { 'micro-spoon': 4, spinner: 4, 'soft-worm': 3, jighead: 3 },
  },
  {
    id: 'hailu', name: '海鲈', latin: '花鲈', emoji: '🌊', difficulty: 3,
    seasons: ['春', '秋', '冬'], layer: '中上层',
    habitat: '入海口、码头、矶岸的流水交汇处。',
    tip: '涨落潮前后窗口期用米诺、VIB 顺流搜索，夜钓码头灯影边缘是标点。',
    lures: { minnow: 5, vib: 4, pencil: 3, spoon: 3, 'soft-worm': 2 },
  },
];

export const SPECIES_MAP = Object.fromEntries(SPECIES.map((s) => [s.id, s]));

// 装备分类
export const GEAR_CATEGORIES = ['鱼竿', '渔轮', '线 / 前导', '拟饵', '其他'];

// PE — 碳线 / 尼龙 对照表（近似值）
export const LINE_TABLE = [
  { pe: '0.4', peLb: 8,  dia: '0.104', carbon: '1.0 号 / 4lb' },
  { pe: '0.6', peLb: 12, dia: '0.128', carbon: '1.5 号 / 6lb' },
  { pe: '0.8', peLb: 16, dia: '0.148', carbon: '2.0 号 / 8lb' },
  { pe: '1.0', peLb: 20, dia: '0.165', carbon: '2.5 号 / 10lb' },
  { pe: '1.2', peLb: 24, dia: '0.185', carbon: '3.0 号 / 12lb' },
  { pe: '1.5', peLb: 30, dia: '0.205', carbon: '3.5 号 / 14lb' },
  { pe: '2.0', peLb: 40, dia: '0.235', carbon: '4.0 号 / 16lb' },
  { pe: '3.0', peLb: 55, dia: '0.285', carbon: '6.0 号 / 22lb' },
  { pe: '4.0', peLb: 60, dia: '0.330', carbon: '8.0 号 / 30lb' },
];

// 常见钓组图解（SVG 在工具页内联绘制）
export const RIGS = [
  {
    id: 'texas', name: '德州钓组',
    desc: '子弹铅 + 曲柄钩 + 软虫，钩尖藏进虫身防挂，打草区、乱石区首选。',
    usage: '沉底后轻挑慢拖，走走停停；感觉一顿或线横移立刻扬竿。',
  },
  {
    id: 'dropshot', name: '倒吊钓组（DS）',
    desc: '钩在上、铅在下，软虫悬浮在离底固定高度，针对底层伏击鱼。',
    usage: '铅不离底，原地抖动竿尖让软虫"跳舞"，鳜鱼、鲈鱼低温期利器。',
  },
  {
    id: 'jighead', name: '铅头钩钓组',
    desc: '铅与钩一体，装卷尾蛆或 T 尾软虫，最简单直接的软饵钓组。',
    usage: '数秒沉底后匀收或小跳，贴底"敲石头"找鳜鱼。',
  },
  {
    id: 'ned', name: '倒钓 / Ned 钓组',
    desc: '蘑菇头铅 + 短粗软虫，落底后软虫直立，微压力时的秘密武器。',
    usage: '几乎不动，落底后轻轻拖 10 厘米停 3 秒，靠软虫自身直立姿态诱鱼。',
  },
  {
    id: 'carolina', name: '卡罗莱纳钓组',
    desc: '铅在前、经挡珠和八字环接一段子线再到钩，软虫自然漂离底部。',
    usage: '大范围慢速搜底，铅走软虫飘，适合大面积找鱼。',
  },
];
