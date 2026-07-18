// 天气自动获取：浏览器定位 + Open-Meteo（免费、无需密钥）
const WMO = {
  0: '晴', 1: '晴', 2: '多云', 3: '阴', 45: '雾', 48: '雾',
  51: '毛毛雨', 53: '毛毛雨', 55: '毛毛雨', 56: '冻雨', 57: '冻雨',
  61: '小雨', 63: '中雨', 65: '大雨', 66: '冻雨', 67: '冻雨',
  71: '小雪', 73: '中雪', 75: '大雪', 77: '霰',
  80: '阵雨', 81: '阵雨', 82: '强阵雨', 85: '阵雪', 86: '阵雪',
  95: '雷阵雨', 96: '雷阵雨', 99: '雷暴',
};

function windDir(deg) {
  const dirs = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
  return dirs[Math.round(deg / 45) % 8] + '风';
}

// km/h → 蒲福风级
function windLevel(kmh) {
  const bounds = [1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117];
  let level = 0;
  while (level < bounds.length && kmh > bounds[level]) level++;
  return level;
}

export function fetchLocalWeather() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('设备不支持定位'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords;
          const url =
            'https://api.open-meteo.com/v1/forecast' +
            `?latitude=${latitude.toFixed(3)}&longitude=${longitude.toFixed(3)}` +
            '&current=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m,surface_pressure';
          const res = await fetch(url);
          if (!res.ok) throw new Error('天气服务不可用');
          const cur = (await res.json()).current;
          const parts = [
            WMO[cur.weather_code] ?? '',
            `${Math.round(cur.temperature_2m)}℃`,
            `${windDir(cur.wind_direction_10m)}${windLevel(cur.wind_speed_10m)}级`,
            `${Math.round(cur.surface_pressure)}hPa`,
          ].filter(Boolean);
          resolve(parts.join(' · '));
        } catch (err) {
          reject(err);
        }
      },
      () => reject(new Error('定位失败，请允许定位权限')),
      { timeout: 10000, maximumAge: 600000 }
    );
  });
}
