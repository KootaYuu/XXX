/**
 * 静噪 —— 网页白噪音播放器
 *
 * 所有声音都由 Web Audio API 实时合成：底噪（白/粉红/布朗）来自循环的
 * 噪声缓冲区，自然音景则在噪声上叠加滤波器、低频振荡器和随机事件。
 * 因此整个应用不包含任何音频文件，离线可用。
 */
(() => {
  'use strict';

  /* ------------------------------------------------------------------ *
   * 噪声缓冲区
   * ------------------------------------------------------------------ */

  const noiseCache = new Map();
  const BUFFER_SECONDS = 6;
  const SEAM_SECONDS = 0.25; // 用于消除循环接缝的交叉淡化长度

  function generateNoise(type, total) {
    const out = new Float32Array(total);

    if (type === 'white') {
      for (let i = 0; i < total; i++) out[i] = Math.random() * 2 - 1;
      return out;
    }

    if (type === 'pink') {
      // Paul Kellet 的经济型粉红噪音滤波器
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < total; i++) {
        const w = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + w * 0.0555179;
        b1 = 0.99332 * b1 + w * 0.0750759;
        b2 = 0.96900 * b2 + w * 0.1538520;
        b3 = 0.86650 * b3 + w * 0.3104856;
        b4 = 0.55000 * b4 + w * 0.5329522;
        b5 = -0.7616 * b5 - w * 0.0168980;
        out[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11;
        b6 = w * 0.115926;
      }
      return out;
    }

    // brown：对白噪音做泄漏积分
    let last = 0;
    for (let i = 0; i < total; i++) {
      const w = Math.random() * 2 - 1;
      last = (last + 0.02 * w) / 1.02;
      out[i] = last * 3.5;
    }
    return out;
  }

  /** 生成一段首尾可无缝循环、去直流并归一化的噪声缓冲区（立体声）。 */
  function noiseBuffer(ctx, type) {
    const cached = noiseCache.get(type);
    if (cached) return cached;

    const length = Math.floor(ctx.sampleRate * BUFFER_SECONDS);
    const seam = Math.floor(ctx.sampleRate * SEAM_SECONDS);
    const buffer = ctx.createBuffer(2, length, ctx.sampleRate);

    for (let ch = 0; ch < 2; ch++) {
      // 多生成 seam 个样本，把这段尾巴交叉淡化回开头，循环点就听不出接缝
      const raw = generateNoise(type, length + seam);
      const data = raw.subarray(0, length);
      for (let i = 0; i < seam; i++) {
        const t = i / seam;
        data[i] = data[i] * t + raw[length + i] * (1 - t);
      }

      let sum = 0;
      for (let i = 0; i < length; i++) sum += data[i];
      const dc = sum / length;

      let peak = 0;
      for (let i = 0; i < length; i++) {
        data[i] -= dc;
        const abs = Math.abs(data[i]);
        if (abs > peak) peak = abs;
      }
      if (peak > 0) {
        const norm = 0.9 / peak;
        for (let i = 0; i < length; i++) data[i] *= norm;
      }

      buffer.copyToChannel(data, ch);
    }

    noiseCache.set(type, buffer);
    return buffer;
  }

  /* ------------------------------------------------------------------ *
   * 构建音景用的小工具
   * ------------------------------------------------------------------ */

  /** 交给每个音景定义使用的工厂；它同时登记所有需要回收的节点与定时器。 */
  function makeKit(ctx, junk) {
    const rand = (min, max) => min + Math.random() * (max - min);

    const kit = {
      ctx,
      rand,

      /** 循环播放的噪声源。 */
      noise(type) {
        const src = ctx.createBufferSource();
        src.buffer = noiseBuffer(ctx, type);
        src.loop = true;
        // 随机起点，避免多个音源的循环周期对齐后产生可听的节奏
        src.start(ctx.currentTime, Math.random() * BUFFER_SECONDS);
        junk.sources.add(src);
        return src;
      },

      filter(type, frequency, q = 0.7, gain = 0) {
        const node = ctx.createBiquadFilter();
        node.type = type;
        node.frequency.value = frequency;
        node.Q.value = q;
        node.gain.value = gain;
        return node;
      },

      gain(value = 1) {
        const node = ctx.createGain();
        node.gain.value = value;
        return node;
      },

      /** 低频振荡器，输出叠加到某个 AudioParam 上（param.value 作为基准值）。 */
      lfo(frequency, depth, param) {
        const osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.value = frequency;
        const amp = ctx.createGain();
        amp.gain.value = depth;
        osc.connect(amp);
        amp.connect(param);
        osc.start(ctx.currentTime + Math.random() * 4); // 错开相位
        junk.sources.add(osc);
        return osc;
      },

      /** 每隔 minMs~maxMs 随机触发一次 fn（雷声、柴火噼啪等）。 */
      every(minMs, maxMs, fn) {
        let id = 0;
        const tick = () => {
          junk.timers.delete(id); // 只保留当前这一个，否则集合会无限增长
          // 暂停期间 currentTime 不前进，此时排期只会让事件堆在同一刻，跳过即可
          if (state.playing) fn();
          id = setTimeout(tick, rand(minMs, maxMs));
          junk.timers.add(id);
        };
        id = setTimeout(tick, rand(minMs, maxMs) * 0.4);
        junk.timers.add(id);
      },

      /** 一次性的噪声爆发，带淡入淡出包络。 */
      burst(type, destination, { attack, hold, release, peak }) {
        const now = ctx.currentTime;
        const src = ctx.createBufferSource();
        src.buffer = noiseBuffer(ctx, type);
        src.loop = true;
        const env = ctx.createGain();
        env.gain.setValueAtTime(0.0001, now);
        env.gain.exponentialRampToValueAtTime(peak, now + attack);
        env.gain.setValueAtTime(peak, now + attack + hold);
        env.gain.exponentialRampToValueAtTime(0.0001, now + attack + hold + release);
        src.connect(env);
        env.connect(destination);
        src.start(now, Math.random() * BUFFER_SECONDS);
        src.stop(now + attack + hold + release + 0.05);
        junk.sources.add(src);
        src.onended = () => {
          junk.sources.delete(src);
          try { src.disconnect(); env.disconnect(); } catch (_) { /* 已断开 */ }
        };
        return env;
      },
    };

    return kit;
  }

  /* ------------------------------------------------------------------ *
   * 音景定义
   * ------------------------------------------------------------------ */

  const SOUNDS = [
    {
      id: 'white', name: '白噪音', icon: `<svg viewBox="0 0 24 24"><path d="M4 8v8M8 5v14M12 9v6M16 4v16M20 10v4"/></svg>`, group: '基础噪音', trim: 0.5,
      desc: '全频段能量均匀，最擅长盖住突然出现的声响。',
      build: (k, out) => { k.noise('white').connect(out); },
    },
    {
      id: 'pink', name: '粉红噪音', icon: `<svg viewBox="0 0 24 24"><path d="M4 4v16M8 6.5v11M12 9v6M16 10.5v3M20 11.2v1.6"/></svg>`, group: '基础噪音', trim: 0.8,
      desc: '高频随频率衰减，听感比白噪音柔和，适合长时间聆听。',
      build: (k, out) => { k.noise('pink').connect(out); },
    },
    {
      id: 'brown', name: '布朗噪音', icon: `<svg viewBox="0 0 24 24"><path d="M2 13c2.5 0 2.5-5 5-5s2.5 5 5 5 2.5-5 5-5 2.5 5 5 5"/></svg>`, group: '基础噪音', trim: 0.75,
      desc: '低沉厚重，像远处的瀑布或飞机舱内的轰鸣。',
      build: (k, out) => { k.noise('brown').connect(out); },
    },
    {
      id: 'rain', name: '雨声', icon: `<svg viewBox="0 0 24 24"><path d="M7.5 14.5a3.8 3.8 0 0 1 .6-7.56 5.3 5.3 0 0 1 10.1 1.54 3.2 3.2 0 0 1-.7 6.02z"/><path d="M8.5 17.5 7.2 20.5M12.6 17.5 11.3 20.5M16.7 17.5 15.4 20.5"/></svg>`, group: '自然', trim: 0.9,
      desc: '窗外连绵的中雨。',
      build: (k, out) => {
        const hp = k.filter('highpass', 440, 0.6);
        const lp = k.filter('lowpass', 6800, 0.5);
        const body = k.gain(0.85);
        k.noise('pink').connect(hp);
        hp.connect(lp);
        lp.connect(body);
        body.connect(out);
        // 两个不同步的慢速起伏，让雨势有疏密变化
        k.lfo(0.11, 0.12, body.gain);
        k.lfo(0.29, 0.06, body.gain);

        // 打在窗沿上的零星大颗雨滴
        const drop = k.filter('bandpass', 2400, 1.2);
        drop.connect(out);
        k.every(90, 420, () => {
          drop.frequency.value = k.rand(1500, 3600);
          k.burst('white', drop, { attack: 0.002, hold: 0.004, release: 0.05, peak: k.rand(0.05, 0.16) });
        });
      },
    },
    {
      id: 'thunder', name: '远雷', icon: `<svg viewBox="0 0 24 24"><path d="M7.5 13.5a3.8 3.8 0 0 1 .6-7.56 5.3 5.3 0 0 1 10.1 1.54 3.2 3.2 0 0 1-.7 6.02z"/><path d="M13 15.5 10.2 19.5h2.9L11.6 23"/></svg>`, group: '自然', trim: 1,
      desc: '每隔一阵滚过天边的闷雷，配雨声最佳。',
      build: (k, out) => {
        const lp = k.filter('lowpass', 190, 0.9);
        lp.connect(out);
        k.every(12000, 38000, () => {
          lp.frequency.setValueAtTime(k.rand(150, 260), k.ctx.currentTime);
          lp.frequency.linearRampToValueAtTime(70, k.ctx.currentTime + 5);
          k.burst('brown', lp, {
            attack: k.rand(0.25, 0.8),
            hold: k.rand(0.2, 0.9),
            release: k.rand(2.5, 5.5),
            peak: k.rand(0.5, 1),
          });
        });
      },
    },
    {
      id: 'ocean', name: '海浪', icon: `<svg viewBox="0 0 24 24"><path d="M2 8.5c2.6 0 2.6 2.4 5.2 2.4s2.6-2.4 5.2-2.4 2.6 2.4 5.2 2.4S20.4 8.5 22 8.5"/><path d="M2 14.5c2.6 0 2.6 2.4 5.2 2.4s2.6-2.4 5.2-2.4 2.6 2.4 5.2 2.4 2.6-2.4 4.4-2.4"/></svg>`, group: '自然', trim: 1.1,
      desc: '一进一退的潮声，周期约十几秒。',
      build: (k, out) => {
        const lp = k.filter('lowpass', 900, 0.4);
        const swell = k.gain(0.22);
        k.noise('brown').connect(lp);
        lp.connect(swell);
        swell.connect(out);
        // 音量与亮度同步起伏 —— 浪头拍下来时高频更多
        k.lfo(0.075, 0.2, swell.gain);
        k.lfo(0.075, 620, lp.frequency);
        k.lfo(0.019, 0.06, swell.gain);
      },
    },
    {
      id: 'stream', name: '溪流', icon: `<svg viewBox="0 0 24 24"><path d="M2 6.5c2 0 2 1.8 4 1.8s2-1.8 4-1.8 2 1.8 4 1.8 2-1.8 4-1.8 1.7 1.8 4 1.8"/><path d="M2 12c2 0 2 1.8 4 1.8S8 12 10 12s2 1.8 4 1.8S16 12 18 12s1.7 1.8 4 1.8"/><path d="M2 17.5c2 0 2 1.8 4 1.8s2-1.8 4-1.8 2 1.8 4 1.8 2-1.8 4-1.8 1.7 1.8 4 1.8"/></svg>`, group: '自然', trim: 0.55,
      desc: '浅滩上跳动的流水声。',
      build: (k, out) => {
        const bp = k.filter('bandpass', 1900, 0.45);
        const lp = k.filter('lowpass', 7200, 0.5);
        const body = k.gain(0.9);
        k.noise('white').connect(bp);
        bp.connect(lp);
        lp.connect(body);
        body.connect(out);
        k.lfo(0.7, 0.1, body.gain);
        k.lfo(0.23, 700, bp.frequency);

        // 水花的细碎气泡声
        const bubble = k.filter('bandpass', 3000, 3);
        bubble.connect(out);
        k.every(120, 600, () => {
          bubble.frequency.value = k.rand(1800, 4200);
          k.burst('white', bubble, { attack: 0.004, hold: 0.01, release: 0.09, peak: k.rand(0.08, 0.22) });
        });
      },
    },
    {
      id: 'wind', name: '风声', icon: `<svg viewBox="0 0 24 24"><path d="M3 8h9.5a3 3 0 1 0-3-3"/><path d="M3 12.5h12.5a3 3 0 1 1-3 3"/><path d="M3 17h7"/></svg>`, group: '自然', trim: 0.9,
      desc: '掠过旷野的长风，忽强忽弱。',
      build: (k, out) => {
        const bp = k.filter('bandpass', 260, 1.1);
        const body = k.gain(0.5);
        k.noise('brown').connect(bp);
        bp.connect(body);
        body.connect(out);
        k.lfo(0.045, 170, bp.frequency);
        k.lfo(0.045, 0.3, body.gain);
        k.lfo(0.013, 0.15, body.gain);
      },
    },
    {
      id: 'fire', name: '篝火', icon: `<svg viewBox="0 0 24 24"><path d="M12 21.5a5.8 5.8 0 0 0 5.8-5.8c0-4.8-3.9-5.8-3.9-9.7 0 0-3.9 1.5-3.9 5.8 0 1.5-1 1.9-1.6 1.2a3.5 3.5 0 0 0-2.2 2.7 5.8 5.8 0 0 0 5.8 5.8z"/></svg>`, group: '室内', trim: 0.8,
      desc: '低沉的火焰声，夹着木柴的噼啪。',
      build: (k, out) => {
        const lp = k.filter('lowpass', 620, 0.6);
        const body = k.gain(0.5);
        k.noise('brown').connect(lp);
        lp.connect(body);
        body.connect(out);
        k.lfo(0.35, 0.18, body.gain);
        k.lfo(1.4, 0.07, body.gain);

        const crack = k.filter('bandpass', 1600, 2.2);
        crack.connect(out);
        k.every(180, 1400, () => {
          crack.frequency.value = k.rand(900, 3200);
          k.burst('white', crack, { attack: 0.002, hold: 0.008, release: k.rand(0.04, 0.14), peak: k.rand(0.12, 0.4) });
        });
      },
    },
    {
      id: 'fan', name: '风扇', icon: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="1.5"/><path d="M12 10.5V3.6M13.3 12.8l6 3.4M10.7 12.8l-6 3.4"/></svg>`, group: '室内', trim: 0.65,
      desc: '老式落地扇的稳定气流与电机嗡鸣。',
      build: (k, out) => {
        const lp = k.filter('lowpass', 520, 0.8);
        const hum = k.filter('peaking', 112, 1.4, 11);
        const body = k.gain(0.75);
        k.noise('brown').connect(lp);
        lp.connect(hum);
        hum.connect(body);
        body.connect(out);
        // 扇叶扫过的轻微周期性振幅调制
        k.lfo(5.6, 0.05, body.gain);
      },
    },
    {
      id: 'cafe', name: '咖啡馆', icon: `<svg viewBox="0 0 24 24"><path d="M4 8.5h12.5v5.8a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M16.5 10.5h1.8a2.6 2.6 0 0 1 0 5.2h-1.8"/><path d="M8 3.5v2.2M12.3 3.5v2.2"/></svg>`, group: '室内', trim: 0.7,
      desc: '邻桌听不清内容的人声嗡嗡，偶尔一声杯碟轻碰。',
      build: (k, out) => {
        const bp = k.filter('bandpass', 620, 0.55);
        const lp = k.filter('lowpass', 2600, 0.6);
        const body = k.gain(0.8);
        k.noise('pink').connect(bp);
        bp.connect(lp);
        lp.connect(body);
        body.connect(out);
        k.lfo(0.31, 0.22, body.gain);
        k.lfo(0.09, 190, bp.frequency);

        const clink = k.filter('bandpass', 5200, 9);
        clink.connect(out);
        k.every(2500, 11000, () => {
          clink.frequency.value = k.rand(3800, 7200);
          k.burst('white', clink, { attack: 0.001, hold: 0.004, release: k.rand(0.15, 0.4), peak: k.rand(0.03, 0.1) });
        });
      },
    },
  ];

  const SOUND_BY_ID = new Map(SOUNDS.map((s) => [s.id, s]));

  const BUILT_IN_PRESETS = [
    { name: '专注', mix: { pink: 0.5, rain: 0.35 } },
    { name: '助眠', mix: { brown: 0.45, ocean: 0.4 } },
    { name: '雷雨夜', mix: { rain: 0.6, thunder: 0.5, wind: 0.2 } },
    { name: '山间溪谷', mix: { stream: 0.55, wind: 0.25 } },
    { name: '壁炉旁', mix: { fire: 0.6, wind: 0.18 } },
    { name: '咖啡馆', mix: { cafe: 0.55, pink: 0.12 } },
  ];

  /* ------------------------------------------------------------------ *
   * 播放引擎
   * ------------------------------------------------------------------ */

  const RAMP = 0.08; // 参数过渡时间，避免咔哒声

  const engine = {
    ctx: null,
    master: null,
    analyser: null,
    layers: new Map(), // id -> { gain, junk }

    /** AudioContext 只能在用户手势里创建，所以延迟到第一次播放。 */
    ensure() {
      if (this.ctx) return this.ctx;
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return null;

      this.ctx = new Ctor();
      this.master = this.ctx.createGain();
      this.master.gain.value = 0;

      this.analyser = this.ctx.createAnalyser();
      this.analyser.fftSize = 1024;
      this.analyser.smoothingTimeConstant = 0.82;

      // 限幅，防止多个音源叠加后削顶
      const limiter = this.ctx.createDynamicsCompressor();
      limiter.threshold.value = -8;
      limiter.knee.value = 6;
      limiter.ratio.value = 12;
      limiter.attack.value = 0.004;
      limiter.release.value = 0.25;

      this.master.connect(limiter);
      limiter.connect(this.analyser);
      this.analyser.connect(this.ctx.destination);
      return this.ctx;
    },

    /** 惰性创建某个音景的节点图。 */
    layer(id) {
      const existing = this.layers.get(id);
      if (existing) return existing;

      const def = SOUND_BY_ID.get(id);
      if (!def || !this.ctx) return null;

      const junk = { sources: new Set(), timers: new Set() };
      const gain = this.ctx.createGain();
      gain.gain.value = 0;
      gain.connect(this.master);
      def.build(makeKit(this.ctx, junk), gain);

      const layer = { gain, junk, trim: def.trim ?? 1 };
      this.layers.set(id, layer);
      return layer;
    },

    dropLayer(id) {
      const layer = this.layers.get(id);
      if (!layer) return;
      layer.junk.timers.forEach(clearTimeout);
      layer.junk.sources.forEach((src) => {
        try { src.onended = null; src.stop(); } catch (_) { /* 可能已停止 */ }
        try { src.disconnect(); } catch (_) { /* 可能已断开 */ }
      });
      try { layer.gain.disconnect(); } catch (_) { /* 已断开 */ }
      this.layers.delete(id);
    },

    setLayerVolume(id, value) {
      if (!this.ctx) return;
      if (value <= 0) {
        const layer = this.layers.get(id);
        if (layer) {
          // 先淡出再拆掉节点，避免突然掐断
          layer.gain.gain.setTargetAtTime(0, this.ctx.currentTime, RAMP / 3);
          setTimeout(() => {
            if (state.mix[id] <= 0) this.dropLayer(id);
          }, 400);
        }
        return;
      }
      const layer = this.layer(id);
      if (!layer) return;
      // 音量滑块做感知补偿：平方曲线比线性更接近人耳
      layer.gain.gain.setTargetAtTime(value * value * layer.trim, this.ctx.currentTime, RAMP);
    },

    setMaster(value) {
      if (!this.ctx) return;
      this.master.gain.setTargetAtTime(value * value, this.ctx.currentTime, RAMP);
    },
  };

  /* ------------------------------------------------------------------ *
   * 状态与持久化
   * ------------------------------------------------------------------ */

  const STORE_KEY = 'jingzao.v1';

  const state = {
    playing: false,
    master: 0.7,
    lastMaster: 0.7,
    mix: {},          // id -> 0..1
    timerMinutes: 0,
    timerEndsAt: 0,
    presets: [],      // 用户保存的混音
  };

  SOUNDS.forEach((s) => { state.mix[s.id] = 0; });

  function save() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        master: state.master,
        mix: state.mix,
        presets: state.presets,
      }));
    } catch (_) { /* 隐私模式下可能不可用，忽略即可 */ }
  }

  function load() {
    let raw = null;
    try { raw = localStorage.getItem(STORE_KEY); } catch (_) { return; }
    if (!raw) return;
    try {
      const data = JSON.parse(raw);
      if (typeof data.master === 'number') {
        state.master = clamp(data.master, 0, 1);
        state.lastMaster = state.master || 0.7;
      }
      if (data.mix && typeof data.mix === 'object') {
        SOUNDS.forEach((s) => {
          const v = data.mix[s.id];
          if (typeof v === 'number') state.mix[s.id] = clamp(v, 0, 1);
        });
      }
      if (Array.isArray(data.presets)) {
        state.presets = data.presets
          .filter((p) => p && typeof p.name === 'string' && p.mix && typeof p.mix === 'object')
          .slice(0, 24);
      }
    } catch (_) { /* 数据损坏就当没存过 */ }
  }

  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));

  /* ------------------------------------------------------------------ *
   * 界面
   * ------------------------------------------------------------------ */

  const el = {
    grid: document.getElementById('grid'),
    presetList: document.getElementById('preset-list'),
    savePreset: document.getElementById('save-preset'),
    reset: document.getElementById('reset'),
    play: document.getElementById('play'),
    master: document.getElementById('master'),
    masterVal: document.getElementById('master-val'),
    timer: document.getElementById('timer'),
    timerVal: document.getElementById('timer-val'),
    viz: document.getElementById('viz'),
  };

  const cards = new Map(); // id -> { card, slider, value }

  function renderSounds() {
    const groups = [];
    SOUNDS.forEach((s) => {
      let group = groups.find((g) => g.name === s.group);
      if (!group) { group = { name: s.group, items: [] }; groups.push(group); }
      group.items.push(s);
    });

    const frag = document.createDocumentFragment();
    groups.forEach((group) => {
      const heading = document.createElement('h3');
      heading.className = 'group-title';
      heading.textContent = group.name;
      frag.appendChild(heading);

      const row = document.createElement('div');
      row.className = 'group-row';

      group.items.forEach((def) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.id = def.id;

        const head = document.createElement('button');
        head.type = 'button';
        head.className = 'card-head';
        head.title = def.desc;
        head.setAttribute('aria-pressed', 'false');
        head.innerHTML = `<span class="card-icon" aria-hidden="true">${def.icon}</span>
          <span class="card-name">${def.name}</span>`;
        // 点击名称＝在 0 和默认音量之间切换
        head.addEventListener('click', () => {
          setMix(def.id, state.mix[def.id] > 0 ? 0 : 0.5, { autoplay: true });
        });

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0';
        slider.max = '100';
        slider.step = '1';
        slider.className = 'card-slider';
        slider.setAttribute('aria-label', `${def.name} 音量`);
        slider.addEventListener('input', () => {
          setMix(def.id, Number(slider.value) / 100, { autoplay: true });
        });

        const value = document.createElement('span');
        value.className = 'card-value';

        const desc = document.createElement('p');
        desc.className = 'card-desc';
        desc.textContent = def.desc;

        const controls = document.createElement('div');
        controls.className = 'card-controls';
        controls.append(slider, value);

        card.append(head, controls, desc);
        row.appendChild(card);
        cards.set(def.id, { card, slider, value, head });
      });

      frag.appendChild(row);
    });

    el.grid.appendChild(frag);
  }

  function syncCard(id) {
    const ui = cards.get(id);
    if (!ui) return;
    const v = state.mix[id];
    ui.slider.value = String(Math.round(v * 100));
    ui.value.textContent = v > 0 ? `${Math.round(v * 100)}%` : '—';
    ui.card.classList.toggle('active', v > 0);
    ui.head.setAttribute('aria-pressed', v > 0 ? 'true' : 'false');
  }

  function setMix(id, value, { autoplay = false } = {}) {
    state.mix[id] = clamp(value, 0, 1);
    syncCard(id);
    engine.setLayerVolume(id, state.mix[id]);
    if (autoplay && state.mix[id] > 0 && !state.playing) start();
    save();
  }

  function applyMix(mix) {
    SOUNDS.forEach((s) => {
      setMix(s.id, typeof mix[s.id] === 'number' ? mix[s.id] : 0);
    });
  }

  function anyActive() {
    return SOUNDS.some((s) => state.mix[s.id] > 0);
  }

  /* --------------------------- 场景预设 --------------------------- */

  function renderPresets() {
    el.presetList.textContent = '';
    const all = [
      ...BUILT_IN_PRESETS.map((p) => ({ ...p, builtin: true })),
      ...state.presets.map((p) => ({ ...p, builtin: false })),
    ];

    all.forEach((preset, index) => {
      const chip = document.createElement('div');
      chip.className = 'chip';

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chip-main';
      btn.textContent = preset.name;
      btn.addEventListener('click', () => {
        applyMix(preset.mix);
        if (!state.playing) start();
      });
      chip.appendChild(btn);

      if (!preset.builtin) {
        const del = document.createElement('button');
        del.type = 'button';
        del.className = 'chip-del';
        del.setAttribute('aria-label', `删除场景 ${preset.name}`);
        del.textContent = '×';
        del.addEventListener('click', () => {
          state.presets.splice(index - BUILT_IN_PRESETS.length, 1);
          save();
          renderPresets();
        });
        chip.appendChild(del);
      }

      el.presetList.appendChild(chip);
    });
  }

  /* --------------------------- 播放控制 --------------------------- */

  function start() {
    const ctx = engine.ensure();
    if (!ctx) {
      alert('当前浏览器不支持 Web Audio API，无法播放。');
      return;
    }
    if (ctx.state === 'suspended') ctx.resume();

    if (!anyActive()) {
      // 什么都没选时给一个默认起点，避免点了播放却没声音
      setMix('rain', 0.45);
      setMix('brown', 0.25);
    }

    SOUNDS.forEach((s) => engine.setLayerVolume(s.id, state.mix[s.id]));
    engine.setMaster(state.master);

    state.playing = true;
    syncTransport();
    startViz();
  }

  function stop() {
    state.playing = false;
    if (engine.ctx) {
      engine.master.gain.setTargetAtTime(0, engine.ctx.currentTime, RAMP);
      // 等淡出结束再挂起，省电且不会留下尾音
      setTimeout(() => {
        if (!state.playing && engine.ctx && engine.ctx.state === 'running') engine.ctx.suspend();
      }, 350);
    }
    syncTransport();
  }

  function toggle() {
    if (state.playing) stop(); else start();
  }

  function syncTransport() {
    el.play.classList.toggle('playing', state.playing);
    el.play.setAttribute('aria-pressed', state.playing ? 'true' : 'false');
    el.play.setAttribute('aria-label', state.playing ? '暂停' : '播放');
    document.body.classList.toggle('is-playing', state.playing);
  }

  function setMaster(value, { remember = true } = {}) {
    state.master = clamp(value, 0, 1);
    if (remember && state.master > 0) state.lastMaster = state.master;
    el.master.value = String(Math.round(state.master * 100));
    el.masterVal.textContent = `${Math.round(state.master * 100)}%`;
    engine.setMaster(state.master);
    save();
  }

  /* --------------------------- 睡眠定时 --------------------------- */

  const FADE_SECONDS = 30; // 结束前的淡出时长

  function setTimer(minutes) {
    state.timerMinutes = minutes;
    state.timerEndsAt = minutes > 0 ? Date.now() + minutes * 60000 : 0;
    if (minutes > 0 && !state.playing) start();
    tickTimer();
  }

  function tickTimer() {
    if (!state.timerEndsAt) {
      el.timerVal.textContent = '';
      return;
    }

    const remain = state.timerEndsAt - Date.now();
    if (remain <= 0) {
      state.timerEndsAt = 0;
      state.timerMinutes = 0;
      el.timer.value = '0';
      el.timerVal.textContent = '';
      stop();
      setMaster(state.lastMaster); // 恢复淡出前的音量，方便下次直接播
      return;
    }

    const total = Math.ceil(remain / 1000);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    el.timerVal.textContent = h > 0
      ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
      : `${m}:${String(s).padStart(2, '0')}`;

    // 最后 30 秒平滑淡出
    if (remain <= FADE_SECONDS * 1000 && state.playing) {
      const ratio = remain / (FADE_SECONDS * 1000);
      setMaster(state.lastMaster * ratio, { remember: false });
    }
  }

  setInterval(tickTimer, 500);

  /* --------------------------- 可视化 --------------------------- */

  let vizFrame = 0;

  function startViz() {
    if (vizFrame || !engine.analyser) return;
    const canvas = el.viz;
    const ctx2d = canvas.getContext('2d');
    const bins = engine.analyser.frequencyBinCount;
    const data = new Uint8Array(bins);
    const BARS = 44;
    const nyquist = engine.ctx.sampleRate / 2;
    const accent = getComputedStyle(document.documentElement)
      .getPropertyValue('--accent').trim() || '#7aa2f7';

    // 20Hz~16kHz 的对数刻度，否则低频挤在最左边、右半边永远空着
    const edges = [];
    for (let i = 0; i <= BARS; i++) {
      const freq = 20 * Math.pow(16000 / 20, i / BARS);
      edges.push(clamp(Math.round((freq / nyquist) * bins), 0, bins - 1));
    }

    const draw = () => {
      if (!state.playing) {
        ctx2d.clearRect(0, 0, canvas.width, canvas.height);
        vizFrame = 0;
        return;
      }
      vizFrame = requestAnimationFrame(draw);

      engine.analyser.getByteFrequencyData(data);
      ctx2d.clearRect(0, 0, canvas.width, canvas.height);

      const barWidth = canvas.width / BARS;
      for (let i = 0; i < BARS; i++) {
        const from = edges[i];
        const to = Math.max(from + 1, edges[i + 1]);
        let sum = 0;
        for (let j = from; j < to; j++) sum += data[j];
        const level = (sum / (to - from)) / 255;
        const h = Math.max(2, level * canvas.height);
        ctx2d.globalAlpha = 0.3 + level * 0.7;
        ctx2d.fillStyle = accent;
        ctx2d.fillRect(i * barWidth + 1, canvas.height - h, barWidth - 2, h);
      }
      ctx2d.globalAlpha = 1;
    };

    vizFrame = requestAnimationFrame(draw);
  }

  /* --------------------------- 事件绑定 --------------------------- */

  el.play.addEventListener('click', toggle);

  el.master.addEventListener('input', () => {
    setMaster(Number(el.master.value) / 100);
  });

  el.timer.addEventListener('change', () => {
    setTimer(Number(el.timer.value));
  });

  el.reset.addEventListener('click', () => {
    applyMix({});
    stop();
  });

  el.savePreset.addEventListener('click', () => {
    if (!anyActive()) {
      alert('先调出一个混音，再保存为场景。');
      return;
    }
    const name = (prompt('给这个场景起个名字：', '我的场景') || '').trim();
    if (!name) return;

    const mix = {};
    SOUNDS.forEach((s) => { if (state.mix[s.id] > 0) mix[s.id] = state.mix[s.id]; });

    const existing = state.presets.findIndex((p) => p.name === name);
    if (existing >= 0) state.presets[existing] = { name, mix };
    else state.presets.push({ name, mix });

    save();
    renderPresets();
  });

  document.addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    const target = e.target instanceof HTMLElement ? e.target : null;
    const tag = target ? target.tagName : '';
    const isRange = tag === 'INPUT' && target.type === 'range';
    // 文本框、下拉框会吞掉按键；滑块和按钮则各自只吞掉一部分
    const editing = target?.isContentEditable
      || tag === 'TEXTAREA'
      || tag === 'SELECT'
      || (tag === 'INPUT' && !isRange);

    if (editing) return;

    if (e.code === 'Space') {
      if (tag === 'BUTTON') return; // 空格在按钮上本来就是“点击”
      e.preventDefault();
      toggle();
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      if (isRange) return; // 让方向键继续调整聚焦的那个滑块
      e.preventDefault();
      setMaster(state.master + (e.key === 'ArrowUp' ? 0.05 : -0.05));
    } else if (e.key === 'm' || e.key === 'M') {
      setMaster(state.master > 0 ? 0 : state.lastMaster, { remember: false });
    }
  });

  /* --------------------------- 启动 --------------------------- */

  load();
  renderSounds();
  renderPresets();
  SOUNDS.forEach((s) => syncCard(s.id));
  el.master.value = String(Math.round(state.master * 100));
  el.masterVal.textContent = `${Math.round(state.master * 100)}%`;
  syncTransport();
})();
