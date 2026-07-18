// 静态数据：拟饵、鱼种、推荐规则用的标签

// 拟饵类型库
// tags: topwater 水面系 / shallow 浅层 / mid 中层 / deep 深层 /
//       slow 适合慢速 / noisy 声响振动强 / weedless 防挂 / micro 微物
// detail: 拟饵百科详细用法
export const LURES = [
  {
    id: 'pencil', name: '铅笔（Pencil）', emoji: '✏️',
    tags: ['topwater'],
    technique: '匀速抽停走"之"字（Walking the dog），炸水不中鱼时停顿 1-2 秒再抽。',
    detail: {
      intro: '水面系代表，模仿垂死小鱼在水面逃窜，视觉刺激极强，炸水瞬间是路亚最上瘾的画面。',
      steps: [
        '抛过标点 2-3 米，等波纹散开再开始操作',
        '竿尖朝下有节奏地小幅抽动，同时匀速收线，让饵左右摆头走"之"字',
        '每走 3-5 步停 1-2 秒，炸水多出现在停顿瞬间',
        '炸水没中鱼不要收回，原地停 2 秒再继续抽，经常有回头咬',
      ],
      scenes: '平静或微风的水面、晨昏窗口期；翘嘴、鲈鱼追小鱼炸水时效果最佳。',
      gear: 'ML-M 调远投竿，PE 主线 + 短碳前导；PE 浮水性好，更容易做出漂亮的"之"字。',
      tips: '中鱼靠鱼的自重挂钩——看到炸水别急着扬竿，感到重量再发力，否则十打九空。',
    },
  },
  {
    id: 'popper', name: '波扒（Popper）', emoji: '💥',
    tags: ['topwater', 'noisy'],
    technique: '短促下压竿尖让嘴部噗水，节奏"啵—停—啵"，停顿时最容易被攻击。',
    detail: {
      intro: '嘴部凹槽推水发出"啵啵"声和水花，靠声音把鱼从远处、深处"叫"上来。',
      steps: [
        '抛到标点后先等 2-3 秒，让鱼注意到落水声',
        '竿尖短促下压让嘴部噗一口水，随即送线让饵回位',
        '基础节奏"啵—停 2 秒—啵"，风浪天可以连续快啵加大动静',
        '攻击大多在停顿时发生，停顿期间保持注意力',
      ],
      scenes: '有轻微风浪的水面、障碍区边缘；鱼上浮但不肯追快饵的时候特别好用。',
      gear: 'ML-M 调竿即可，前导可短一些，不影响出水声。',
      tips: '波扒是慢节奏水面系，宁慢勿快；炸水不中先停住，再轻啵一口常能补中。',
    },
  },
  {
    id: 'frog', name: '雷蛙（Frog）', emoji: '🐸',
    tags: ['topwater', 'weedless'],
    technique: '贴着草面小幅度点动、停顿，炸水后默数一秒确认吃深再扬竿。',
    detail: {
      intro: '双钩上翻贴背的全防挂设计，唯一能直接打进重草区的水面饵，黑鱼（雷强）专属武器。',
      steps: [
        '直接抛进草洞、草缝或浮萍区，不用怕挂',
        '竿尖小幅抖动让蛙原地点头、拨水，慢慢拖过草面',
        '经过草洞、亮水边缘时停 2-3 秒，这是最容易炸口的位置',
        '炸水后默数一秒，感到线绷紧再全力扬竿',
      ],
      scenes: '重草塘、藕塘、浮萍区，夏秋高温季的黑鱼；亮水区的鲈鱼也吃蛙。',
      gear: '雷强专用竿（XH 以上）+ 4-8 号 PE 直连不加前导，水滴轮刹车锁死。',
      tips: '空枪是常态，别灰心；扬竿要狠——把钩从蛙背压进鱼嘴需要很大力量。',
    },
  },
  {
    id: 'minnow', name: '米诺（Minnow）', emoji: '🐠',
    tags: ['shallow', 'mid'],
    technique: '匀收为主，配合抽停（Twitch & Pause），停顿瞬间常出咬口。',
    detail: {
      intro: '泳姿最接近真实小鱼的硬饵，浮水 / 悬停 / 沉水三种类型覆盖不同泳层和季节，硬饵入门首选。',
      steps: [
        '基础手法匀速收线即可，舌板会自动做出摆尾泳姿',
        '进阶用抽停：连抽两三下让饵左右乱窜，然后停 1-3 秒',
        '悬停米诺停顿时会定在水层中，低温期停 3-5 秒往往才出口',
        '过障碍前减速，让饵慢慢飘过去再恢复节奏',
      ],
      scenes: '桦尖、陡坎、亮水与障碍交界处；翘嘴、海鲈、鳜鱼通杀；悬停米诺是早春晚秋利器。',
      gear: 'L-M 调竿按饵重选择，碳线前导 1-1.5 米降低惊鱼概率。',
      tips: '咬口大多出现在停顿和再启动的瞬间——节奏变化比一直匀收重要得多。',
    },
  },
  {
    id: 'crank', name: '摇摆胖子（Crank）', emoji: '🥎',
    tags: ['mid', 'deep', 'noisy'],
    technique: '匀速收线让其撞击结构后停顿上浮，"碰—停—收"是标准节奏。',
    detail: {
      intro: '大摆幅、强水波的胖身硬饵，靠碰撞结构触发反射性咬口，扇形搜索效率极高。',
      steps: [
        '选潜深略大于结构深度的型号，让饵能撞到底或障碍',
        '匀速收线，感到"咚"地撞上障碍后停一下，让饵浮起躲过再收',
        '"碰—停—收"的节奏变化就是最大的诱鱼点',
        '长距离平抛，扇形覆盖整片水域快速找鱼',
      ],
      scenes: '乱石区、倒树、桥墩等硬质结构；鲈鱼、鳜鱼、翘嘴白天下层觅食时。',
      gear: '玻璃钢竿或软调性 Crank 专用竿更好——硬竿容易把浅口拉豁。',
      tips: '圆唇撞到障碍会翻滚躲挂，比想象中不容易挂底，敢打结构才有鱼。',
    },
  },
  {
    id: 'vib', name: 'VIB / 颤沉饵', emoji: '📳',
    tags: ['mid', 'deep', 'noisy', 'slow'],
    technique: '数秒沉底后跳底或匀收，冬季用小幅度慢跳，感觉线一顿立刻扬竿。',
    detail: {
      intro: '全泳层可控的高频颤动饵，远投能力和搜索速度第一，也是冬季跳底的头号选择。',
      steps: [
        '抛出后读秒下沉（约每秒 0.3-0.5 米），按读秒分层搜索',
        '匀速收线即有高频颤动，快收搜上层、慢收搜下层',
        '冬季用跳底：沉底后轻挑竿尖 20-30 厘米，再压竿让它飘落',
        '咬口常在下落中——线突然停住或横移，立刻扬竿',
      ],
      scenes: '大水面远投找鱼、冬季深水翘嘴 / 鲈鱼、水浑需要振动传导的时候。',
      gear: 'M 调以上远投竿，PE 主线兼顾抛投距离和底部灵敏度。',
      tips: '三本钩朝下容易挂底，石头多的地方换单钩版本或减少触底时间。',
    },
  },
  {
    id: 'spoon', name: '亮片（Spoon）', emoji: '🥄',
    tags: ['shallow', 'mid', 'deep'],
    technique: '远投数秒下沉到目标泳层匀收，或收两圈停一下做出飘落动作。',
    detail: {
      intro: '金属饵鼻祖，反光 + 摆动模仿受伤小鱼，便宜、耐用、全泳层通杀。',
      steps: [
        '远投后数秒下沉到目标泳层，开始匀速收线',
        '收两三圈停一下，亮片会侧身飘落反光——这是标志性诱鱼动作',
        '逆流抛让水流带动泳姿，顺流收更自然',
        '没口就改变读秒数换一个泳层重新搜',
      ],
      scenes: '水库湖泊远投搜翘嘴红尾、急流里打军鱼；几乎所有掠食性鱼都吃亮片。',
      gear: '按克重配竿，碳线前导能减少金属反光对线组的暴露。',
      tips: '亮片旋转容易拧线，连接处加一个八字环基本可以解决。',
    },
  },
  {
    id: 'micro-spoon', name: '微物亮片 / 瓜子亮片', emoji: '🌰',
    tags: ['shallow', 'micro'],
    technique: '轻竿细线匀速快收，溪流中斜下游 45° 抛投让水流带动泳姿。',
    detail: {
      intro: '1-5 克的迷你亮片，微物钓法的核心，专攻马口、白条等小型掠食鱼。',
      steps: [
        '溪流中朝下游斜 45° 抛，让水流把饵摆到对岸缓流区',
        '保持匀速快收，让亮片贴着水面下高频摆动',
        '急流与缓流交界、白沫线边缘多打几竿',
        '鱼追而不咬时突然加速或减速，触发攻击',
      ],
      scenes: '山涧溪流、清澈浅滩；马口、白条、小军鱼、溪哥。',
      gear: 'UL 超软微物竿 + 0.3-0.6 号 PE（或 2-3 磅尼龙直连）+ 微物纺车轮。',
      tips: '细线中了大物别硬拉，靠泄力和竿身弹性慢慢遛。',
    },
  },
  {
    id: 'spinner', name: '旋转亮片（Spinner）', emoji: '🌀',
    tags: ['shallow', 'mid', 'noisy', 'micro'],
    technique: '入水即收保持叶片旋转，过深潭时先沉几秒再收。',
    detail: {
      intro: '旋转叶片产生强烈闪光和振动，入水即工作，新手最容易上鱼的饵之一。',
      steps: [
        '入水后立刻带一下竿，确认叶片开始旋转',
        '全程匀速收线，速度以手上能感到叶片"嗡嗡"抖动为准',
        '过深潭时先读秒下沉再开始收',
        '偶尔停顿让叶片停转再启动，"启停闪光"能激怒跟随的鱼',
      ],
      scenes: '浅水快速搜索、溪流小水面；马口、白条、翘嘴、鲈鱼见了都咬。',
      gear: 'UL-L 调竿，务必用八字环连接防止拧线。',
      tips: '叶片不转就没有诱鱼力——手上感觉不到振动说明收速太慢或挂了杂物。',
    },
  },
  {
    id: 'spinnerbait', name: '复合亮片（Spinnerbait）', emoji: '⚙️',
    tags: ['shallow', 'mid', 'noisy', 'weedless'],
    technique: '沿障碍区匀收，碰到木桩水草让它撞一下再继续，浑水利器。',
    detail: {
      intro: '上臂叶片闪光振动、下臂铅头裙摆的复合结构，半防挂设计，浑水和障碍区的搜索利器。',
      steps: [
        '沿倒树、木桩、水草边缘平行抛投',
        '匀速收线让叶片持续工作；贴底慢收（Slow Rolling）专出大鱼',
        '故意让上臂撞击障碍物，弹开的瞬间常有反射咬口',
        '也可以让它沉底后像汲铅一样跳动',
      ],
      scenes: '浑水、光线差、障碍密集的水域；鲈鱼、翘嘴、鳜鱼。',
      gear: 'M-MH 枪柄水滴轮组合，碳前导 20 磅以上，敢往结构里打。',
      tips: '上钩臂就是防挂梁、钩尖朝上，绝大部分障碍都能爬过去，别不敢抛。',
    },
  },
  {
    id: 'soft-worm', name: '软虫（德州 / 无铅）', emoji: '🪱',
    tags: ['deep', 'slow', 'weedless'],
    technique: '沉底后轻挑竿尖拖动，走走停停，大部分咬口在下落和停顿中。',
    detail: {
      intro: '路亚的最后底牌——鱼口再差也能靠软虫磨出来，德州和无铅是最常用的两种挂法。',
      steps: [
        '德州钓组抛进障碍 / 草区，看线松弛确认到底',
        '竿尖从 9 点方向慢慢挑到 11 点拖动软虫，再收回余线，走走停停',
        '无铅挂法下落极慢，专攻浅水和鱼悬浮的局面，全程盯线',
        '线突然横移、加速或手感一"咚"——先快速收紧余线，再大力扬竿',
      ],
      scenes: '障碍区、草区、高压钓场，以及低温或钓场被打惊后的"磨口"局面。',
      gear: 'M-MH 快调竿保证扬竿刺鱼力度，碳线主线读咬口更灵敏。',
      tips: '慢就是快——大部分人软虫不上鱼，是因为动作做得太快、太大。',
    },
  },
  {
    id: 'jighead', name: '铅头钩 + 卷尾蛆', emoji: '🎏',
    tags: ['mid', 'deep', 'slow'],
    technique: '沉底慢拖或小跳，贴底"敲石头"，鳜鱼标配手法。',
    detail: {
      intro: '铅头与钩一体的最简软饵系统，直接感知底况，配卷尾蛆就是鳜鱼的标配。',
      steps: [
        '按水深流速选克重：能稳定到底、又不死沉为佳',
        '到底后小跳：短促挑竿让饵跳起 10-20 厘米，随后压竿跟线让它落底',
        '中层可以匀收，T 尾 / 卷尾自带摆动泳姿',
        '沿石缝、桥墩底部"敲石头"，手感异样一顿立刻扬竿',
      ],
      scenes: '乱石底、桥墩、深潭底层；鳜鱼、鲈鱼、鲶鱼、黄辣丁。',
      gear: 'L-M 调竿按克重选择，PE + 碳前导的组合传导底部信息最清晰。',
      tips: '挂底和咬口的区别：挂底是死沉，咬口往往带"活"的一顿或线横走。',
    },
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
