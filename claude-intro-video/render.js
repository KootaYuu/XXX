// Renders index.html frame by frame with Playwright and pipes the frames into ffmpeg.
//
// Usage:
//   node render.js                       -> claude-intro.mp4 (silent video track)
//   node render.js --preview 3,12,20     -> preview-<t>.png stills at the given seconds
//
// Env: FPS (default 30), FFMPEG (path to ffmpeg binary, default "ffmpeg").
const path = require("path");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const FPS = +(process.env.FPS || 30);
const FFMPEG = process.env.FFMPEG || "ffmpeg";
const OUT_DIR = process.env.OUT_DIR || __dirname;

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(__dirname, "index.html"), { waitUntil: "networkidle" });
  await page.evaluate(() => window.ready);
  const duration = await page.evaluate(() => window.DURATION);

  const pi = process.argv.indexOf("--preview");
  if (pi !== -1) {
    for (const t of process.argv[pi + 1].split(",").map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(OUT_DIR, `preview-${t}.png`) });
    }
    await browser.close();
    return;
  }

  const out = path.join(OUT_DIR, "video-only.mp4");
  const ff = spawn(FFMPEG, [
    "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", out,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const total = Math.round(duration * FPS);
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % 150 === 0) console.log(`frame ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error("ffmpeg exit " + c)))));
  await browser.close();
  console.log("wrote", out);
}

main().catch(e => { console.error(e); process.exit(1); });
