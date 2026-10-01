// Small colour helpers shared by the gumball machine demo.

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function parseHex(hex) {
  const clean = hex.replace("#", "").trim();
  const step = clean.length / 3;
  return [0, 1, 2].map((i) => parseInt(clean.slice(i * step, (i + 1) * step), 16));
}

export function mixHex(from, to, amount) {
  const [r1, g1, b1] = parseHex(from);
  const [r2, g2, b2] = parseHex(to);
  const t = clamp(amount, 0, 1);
  const channel = (a, b) => Math.round(a + (b - a) * t);
  return `#${[channel(r1, r2), channel(g1, g2), channel(b1, b2)]
    .map((c) => c.toString(16).padStart(2, "0"))
    .join("")}`;
}
