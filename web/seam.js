(() => {
  const SIZE = 640;

  function colorDistance(a, b) {
    return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]);
  }

  function dominantCornerColor(ctx) {
    const points = [[0, 0], [SIZE - 1, 0], [0, SIZE - 1], [SIZE - 1, SIZE - 1]];
    const colors = points.map(([x, y]) => Array.from(ctx.getImageData(x, y, 1, 1).data));
    return colors.reduce((best, candidate) => {
      const score = colors.reduce((sum, color) => sum + colorDistance(candidate, color), 0);
      return !best || score < best.score ? { color: candidate, score } : best;
    }, null).color;
  }

  function edgeAnchors(canvas) {
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const pixels = ctx.getImageData(0, 0, SIZE, SIZE).data;
    const pixel = (x, y) => {
      const i = (y * SIZE + x) * 4;
      return [pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3]];
    };
    const background = dominantCornerColor(ctx);
    const hits = [];
    for (let y = 0; y < SIZE; y += 2) {
      for (let x = SIZE - 1; x >= SIZE - 22; x -= 2) {
        const sample = pixel(x, y);
        if (sample[3] > 20 && colorDistance(sample, background) > 95) {
          hits.push({ y, color: `rgb(${sample[0]} ${sample[1]} ${sample[2]})` });
          break;
        }
      }
    }
    const clusters = [];
    for (const hit of hits) {
      const last = clusters.at(-1);
      if (last && hit.y - last.maxY <= 7) {
        last.values.push(hit);
        last.maxY = hit.y;
      } else {
        clusters.push({ values: [hit], maxY: hit.y });
      }
    }
    return clusters.slice(0, 6).map(cluster => {
      const y = Math.round(cluster.values.reduce((sum, item) => sum + item.y, 0) / cluster.values.length);
      const boundary = pixel(SIZE - 1, y);
      const color = colorDistance(boundary, background) > 95
        ? `rgb(${boundary[0]} ${boundary[1]} ${boundary[2]})`
        : cluster.values[Math.floor(cluster.values.length / 2)].color;
      return { y, color, width: Math.max(3, Math.min(18, cluster.values.length * 1.4)) };
    });
  }

  function matchBackground() {
    const prompt = document.querySelector('#promptCanvas');
    const response = document.querySelector('#responseCanvas');
    if (!prompt || !response) return;
    const pctx = prompt.getContext('2d', { willReadFrequently: true });
    const rctx = response.getContext('2d', { willReadFrequently: true });
    const promptBackground = dominantCornerColor(pctx);
    const responseBackground = dominantCornerColor(rctx);
    if (colorDistance(promptBackground, responseBackground) < 12) return;
    const image = rctx.getImageData(0, 0, SIZE, SIZE);
    for (let i = 0; i < image.data.length; i += 4) {
      const sample = [image.data[i], image.data[i + 1], image.data[i + 2]];
      if (colorDistance(sample, responseBackground) < 22) {
        image.data[i] = promptBackground[0];
        image.data[i + 1] = promptBackground[1];
        image.data[i + 2] = promptBackground[2];
        image.data[i + 3] = promptBackground[3];
      }
    }
    rctx.putImageData(image, 0, 0);
  }

  function stitchResponse() {
    matchBackground();
    const strategy = document.querySelector('#strategyLabel')?.textContent.trim();
    if (!strategy || strategy === 'in attesa' || strategy === 'contraddizione') return;
    const prompt = document.querySelector('#promptCanvas');
    const response = document.querySelector('#responseCanvas');
    const anchors = edgeAnchors(prompt);
    if (!anchors.length) return;
    const ctx = response.getContext('2d');
    anchors.forEach((anchor, index) => {
      const direction = index % 2 ? -1 : 1;
      ctx.save();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = anchor.color;
      ctx.lineWidth = anchor.width;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(0, anchor.y);
      ctx.bezierCurveTo(45, anchor.y, 80, anchor.y + direction * 28, 145, anchor.y + direction * 18);
      ctx.stroke();
      ctx.fillStyle = anchor.color;
      ctx.fillRect(0, anchor.y, 1, 1);
      ctx.restore();
    });
    if (window.__VISUAL_DIALOGUE_STATE__) {
      window.__VISUAL_DIALOGUE_STATE__.seamAnchors = anchors.map(anchor => Math.round(anchor.y));
      window.__VISUAL_DIALOGUE_STATE__.seamConnected = true;
    }
    const status = document.querySelector('#status');
    if (status) status.textContent += ` ${anchors.length} punto${anchors.length > 1 ? 'i' : ''} di bordo cucito${anchors.length > 1 ? 'i' : ''}.`;
  }

  window.addEventListener('DOMContentLoaded', () => {
    matchBackground();
    const generate = document.querySelector('#generateButton');
    generate?.addEventListener('click', () => window.setTimeout(stitchResponse, 720));
    const disclosure = document.querySelector('.disclosure p');
    if (disclosure) disclosure.textContent += ' Lo sfondo della risposta eredita deterministicamente il colore dominante del prompt: non viene mai scelto a caso. Se un segno raggiunge il bordo destro, una risposta non contraddittoria può riprenderlo dal bordo sinistro alla stessa altezza.';
  });
})();
