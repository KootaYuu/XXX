// 拟饵推荐规则引擎
import { LURES, LURE_MAP, SPECIES_MAP } from './data.js';

// 根据月份推断默认季节
export function currentSeason() {
  const m = new Date().getMonth() + 1;
  if (m >= 3 && m <= 5) return '春';
  if (m >= 6 && m <= 8) return '夏';
  if (m >= 9 && m <= 11) return '秋';
  return '冬';
}

/**
 * @param {object} input
 * @param {string} input.speciesId 对象鱼 id
 * @param {string} input.season 春/夏/秋/冬
 * @param {string} input.timeOfDay 清晨/白天/傍晚/夜晚
 * @param {string} input.clarity 清澈/微浊/浑浊
 * @param {string} input.water 水库/湖泊/河流/野塘/溪流/海边
 * @returns {{results: Array, colorAdvice: string, seasonNote: string}}
 */
export function recommend(input) {
  const species = SPECIES_MAP[input.speciesId];
  if (!species) return { results: [], colorAdvice: '', seasonNote: '' };

  const scores = new Map();
  for (const [lureId, weight] of Object.entries(species.lures)) {
    scores.set(lureId, weight * 2); // 基础分：鱼种偏好 ×2
  }

  const bump = (pred, delta) => {
    for (const lure of LURES) {
      if (scores.has(lure.id) && pred(lure)) {
        scores.set(lure.id, scores.get(lure.id) + delta);
      }
    }
  };
  const hasTag = (t) => (l) => l.tags.includes(t);

  // 季节修正
  if (input.season === '冬') {
    bump(hasTag('slow'), 3);
    bump(hasTag('deep'), 2);
    bump(hasTag('topwater'), -5);
  } else if (input.season === '夏') {
    if (input.timeOfDay === '清晨' || input.timeOfDay === '傍晚') {
      bump(hasTag('topwater'), 3);
    } else if (input.timeOfDay === '白天') {
      bump(hasTag('deep'), 2);
      bump(hasTag('topwater'), -2);
    }
  } else if (input.season === '春') {
    bump(hasTag('shallow'), 2); // 浅滩洄游
  } else if (input.season === '秋') {
    bump(hasTag('noisy'), 1); // 疯狂觅食期，大动作饵占优
  }

  // 时段修正
  if (input.timeOfDay === '夜晚') {
    bump(hasTag('noisy'), 2);
    bump(hasTag('micro'), -2);
  }

  // 水色修正：浑水靠声响振动
  if (input.clarity === '浑浊') {
    bump(hasTag('noisy'), 3);
    bump(hasTag('micro'), -2);
  } else if (input.clarity === '微浊') {
    bump(hasTag('noisy'), 1);
  }

  // 水域修正
  if (input.water === '溪流') {
    bump(hasTag('micro'), 3);
    bump(hasTag('deep'), -2);
  } else if (input.water === '野塘') {
    bump(hasTag('weedless'), 3); // 障碍多，防挂优先
  } else if (input.water === '水库' || input.water === '湖泊') {
    bump((l) => l.id === 'spoon' || l.id === 'vib', 1); // 大水面远投搜索
  }

  const results = [...scores.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([lureId, score], i) => ({
      rank: i + 1,
      lure: LURE_MAP[lureId],
      score,
      stars: Math.max(1, Math.min(5, Math.round(score / 3))),
    }));

  return {
    results,
    colorAdvice: colorAdvice(input),
    seasonNote: seasonNote(input.season),
    speciesTip: species.tip,
  };
}

function colorAdvice(input) {
  if (input.timeOfDay === '夜晚') {
    return '夜钓选黑色剪影或夜光色，水面背光看轮廓，声响振动比颜色更重要。';
  }
  if (input.clarity === '浑浊') {
    return '浑水用高对比：亮橙、亮黄、金色、夜光，配合响珠或大振幅泳姿让鱼"听"到饵。';
  }
  if (input.clarity === '微浊') {
    return '微浊水选金色、鲫鱼色、白色等中等亮度，兼顾可见度和真实感。';
  }
  return '清水用自然色：枯骨色、鲫鱼色、透明壳、银色，动作放小更不易惊鱼。';
}

function seasonNote(season) {
  const notes = {
    春: '春季鱼群上浅滩觅食产卵，优先搜浅水缓坡和洄湾，中午水温升高后窗口更好。',
    夏: '夏季抓早晚两个窗口，白天鱼下深或躲阴凉，可打桥墩阴影、深潭和活水口。',
    秋: '秋季是全年黄金期，鱼疯狂储食，全天有口，大饵大动作往往能出大鱼。',
    冬: '冬季鱼聚深水少动，饵要小、要慢、要贴底，一个标点多磨几竿，中鱼多在停顿中。',
  };
  return notes[season] || '';
}
