/* Desenhos exatos da Jornada do Herói (formas geométricas, medidas e frações).
   ILUS.svg("cubo") → string <svg>…</svg>. Os desenhos mostram o assunto sem escrever a resposta. */
(() => {
  const TINTA = "#1f1a3d", OURO = "#fbbf24", VERMELHO = "#ef4444";
  const AZUL = ["#bfdbfe", "#93c5fd", "#60a5fa"], ROXO = ["#ddd6fe", "#c4b5fd", "#a78bfa"];
  const VERDE = ["#bbf7d0", "#86efac", "#4ade80"], LARANJA = ["#fed7aa", "#fdba74", "#fb923c"];
  const f = n => Math.round(n * 10) / 10;
  const pts = p => p.map(([x, y]) => `${f(x)},${f(y)}`).join(" ");
  const pol = (p, fill, extra = "") => `<polygon points="${pts(p)}" fill="${fill}" stroke="${TINTA}" stroke-width="2.5" stroke-linejoin="round" ${extra}/>`;
  const lin = (a, b, o = {}) => `<line x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(b[0])}" y2="${f(b[1])}" stroke="${o.cor || TINTA}" stroke-width="${o.w || 2.5}" stroke-linecap="round" ${o.tracejado ? 'stroke-dasharray="6 6"' : ""}/>`;
  const txt = (x, y, t, o = {}) => `<text x="${f(x)}" y="${f(y)}" font-family="Nunito,system-ui,sans-serif" font-size="${o.tam || 14}" font-weight="800" fill="${o.cor || TINTA}" text-anchor="${o.ancora || "middle"}" dominant-baseline="middle">${t}</text>`;
  const svg = (w, h, corpo, alt = "") => `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${alt}">${corpo}</svg>`;

  /* ---------------- sólidos ---------------- */
  function cubo(dest, cores = AZUL) {
    const A = [45, 150], B = [125, 150], C = [125, 70], D = [45, 70], dx = 40, dy = -32;
    const s = p => [p[0] + dx, p[1] + dy], A2 = s(A), B2 = s(B), C2 = s(C), D2 = s(D);
    let o = pol([A, B, C, D], dest === "face" ? OURO : cores[1]) + pol([D, C, C2, D2], cores[0]) + pol([B, B2, C2, C], cores[2]);
    o += lin(A, A2, { tracejado: 1, w: 2 }) + lin(A2, B2, { tracejado: 1, w: 2 }) + lin(A2, D2, { tracejado: 1, w: 2 });
    if (dest === "aresta") o += lin(B, C, { cor: VERMELHO, w: 7 });
    if (dest === "vertice") o += `<circle cx="${C[0]}" cy="${C[1]}" r="8" fill="${VERMELHO}" stroke="#fff" stroke-width="2"/>`;
    return o;
  }
  function paralelepipedo(dest, cores = LARANJA) {
    const A = [25, 150], B = [140, 150], C = [140, 88], D = [25, 88], dx = 50, dy = -38;
    const s = p => [p[0] + dx, p[1] + dy], A2 = s(A), B2 = s(B), C2 = s(C), D2 = s(D);
    let o = pol([A, B, C, D], cores[1]) + pol([D, C, C2, D2], cores[0]) + pol([B, B2, C2, C], cores[2]);
    o += lin(A, A2, { tracejado: 1, w: 2 }) + lin(A2, B2, { tracejado: 1, w: 2 }) + lin(A2, D2, { tracejado: 1, w: 2 });
    if (dest === "aresta") [[A, B], [B, C], [C, D], [D, A], [D, D2], [C, C2], [B, B2], [D2, C2], [C2, B2]].forEach(([p, q]) => o += lin(p, q, { cor: VERMELHO, w: 4 }));
    return o;
  }
  // polígono da base visto em perspectiva
  const base = (n, cx, cy, rx, ry) => Array.from({ length: n }, (_, k) => {
    const t = Math.PI / 2 + 2 * Math.PI * k / n;
    return { p: [cx + rx * Math.cos(t), cy + ry * Math.sin(t)], s: Math.sin(t) };
  });
  function piramide(n, cores = ROXO) {
    n = Math.max(3, Math.min(8, +n || 4));
    const V = base(n, 110, 140, 78, 24), ap = [110, 22];
    const xs = V.map(v => v.p[0]), min = Math.min(...xs), max = Math.max(...xs);
    const silh = v => v.p[0] === min || v.p[0] === max;
    let fundo = `<polygon points="${pts(V.map(v => v.p))}" fill="${cores[0]}" opacity=".55"/>`, faces = "", esc = "";
    V.forEach((v, k) => {
      const w = V[(k + 1) % n], meio = (v.s + w.s) / 2;
      if (meio <= -0.05) esc += lin(v.p, w.p, { tracejado: 1, w: 2 });
      else faces += pol([ap, v.p, w.p], cores[1 + (k % 2)]);
      if (v.s < -0.02 && !silh(v)) esc += lin(ap, v.p, { tracejado: 1, w: 2 });
    });
    return fundo + faces + esc;
  }
  function prisma(n, cores = VERDE) {
    n = Math.max(3, Math.min(8, +n || 3));
    const B = base(n, 110, 145, 72, 22), T = base(n, 110, 55, 72, 22);
    const xs = B.map(v => v.p[0]), min = Math.min(...xs), max = Math.max(...xs);
    let esc = "", faces = "";
    B.forEach((v, k) => {
      const w = B[(k + 1) % n], meio = (v.s + w.s) / 2;
      if (meio <= -0.05) esc += lin(v.p, w.p, { tracejado: 1, w: 2 });
      else faces += pol([v.p, w.p, T[(k + 1) % n].p, T[k].p], cores[1 + (k % 2)]);
      if (v.s < -0.02 && v.p[0] !== min && v.p[0] !== max) esc += lin(v.p, T[k].p, { tracejado: 1, w: 2 });
    });
    return faces + pol(T.map(v => v.p), cores[0]) + esc;
  }
  function cilindro() {
    const cx = 110, rx = 62, ry = 18, yt = 42, yb = 145;
    return `<defs><linearGradient id="gcil" x1="0" x2="1"><stop offset="0" stop-color="#7dd3fc"/><stop offset=".45" stop-color="#e0f2fe"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>
      <path d="M ${cx - rx} ${yt} L ${cx - rx} ${yb} A ${rx} ${ry} 0 0 0 ${cx + rx} ${yb} L ${cx + rx} ${yt} Z" fill="url(#gcil)" stroke="${TINTA}" stroke-width="2.5"/>
      <path d="M ${cx - rx} ${yb} A ${rx} ${ry} 0 0 1 ${cx + rx} ${yb}" fill="none" stroke="${TINTA}" stroke-width="2" stroke-dasharray="6 6"/>
      <ellipse cx="${cx}" cy="${yt}" rx="${rx}" ry="${ry}" fill="#bae6fd" stroke="${TINTA}" stroke-width="2.5"/>`;
  }
  function cone() {
    const cx = 110, rx = 66, ry = 20, yb = 145, ap = [110, 22];
    return `<defs><linearGradient id="gcone" x1="0" x2="1"><stop offset="0" stop-color="#fca5a5"/><stop offset=".45" stop-color="#fee2e2"/><stop offset="1" stop-color="#f87171"/></linearGradient></defs>
      <path d="M ${cx - rx} ${yb} A ${rx} ${ry} 0 0 1 ${cx + rx} ${yb}" fill="none" stroke="${TINTA}" stroke-width="2" stroke-dasharray="6 6"/>
      <path d="M ${ap[0]} ${ap[1]} L ${cx - rx} ${yb} A ${rx} ${ry} 0 0 0 ${cx + rx} ${yb} Z" fill="url(#gcone)" stroke="${TINTA}" stroke-width="2.5" stroke-linejoin="round"/>`;
  }
  function esfera() {
    return `<defs><radialGradient id="gesf" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#fff7d6"/><stop offset=".5" stop-color="#fcd34d"/><stop offset="1" stop-color="#f59e0b"/></radialGradient></defs>
      <circle cx="110" cy="92" r="70" fill="url(#gesf)" stroke="${TINTA}" stroke-width="2.5"/>
      <path d="M 40 92 A 70 20 0 0 1 180 92" fill="none" stroke="${TINTA}" stroke-width="1.6" stroke-dasharray="5 6" opacity=".7"/>
      <path d="M 40 92 A 70 20 0 0 0 180 92" fill="none" stroke="${TINTA}" stroke-width="1.8" opacity=".8"/>`;
  }
  const SOLIDOS = { cubo: d => cubo(d), paralelepipedo: d => paralelepipedo(d), piramide: n => piramide(n), prisma: n => prisma(n), cilindro, cone, esfera };

  /* ---------------- planificações ---------------- */
  function planificacao(qual) {
    const q = (x, y, l, c) => `<rect x="${x}" y="${y}" width="${l}" height="${l}" fill="${c}" stroke="${TINTA}" stroke-width="2.5"/>`;
    if (qual === "cubo" || qual === "5q") {
      // cubo: 4 quadrados em linha + 1 em cima + 1 embaixo; "5q": uma cruz de 5 quadrados
      const l = 40, n = qual === "cubo" ? 4 : 3, x0 = (220 - n * l) / 2, y0 = 70;
      let o = "";
      for (let i = 0; i < n; i++) o += q(x0 + i * l, y0, l, i % 2 ? AZUL[1] : AZUL[0]);
      return o + q(x0 + l, y0 - l, l, AZUL[2]) + q(x0 + l, y0 + l, l, AZUL[2]);
    }
    if (qual === "piramide4") {
      const c = [110, 90], h = 28, l = 56, x = c[0] - h, y = c[1] - h;
      return q(x, y, l, ROXO[0]) + pol([[x, y], [x + l, y], [c[0], y - 50]], ROXO[1]) + pol([[x + l, y], [x + l, y + l], [x + l + 50, c[1]]], ROXO[2]) +
        pol([[x, y + l], [x + l, y + l], [c[0], y + l + 50]], ROXO[1]) + pol([[x, y], [x, y + l], [x - 50, c[1]]], ROXO[2]);
    }
    if (qual === "4tri") {
      const A = [110, 18], B = [30, 162], C = [190, 162], m = (p, r) => [(p[0] + r[0]) / 2, (p[1] + r[1]) / 2];
      const ab = m(A, B), ac = m(A, C), bc = m(B, C);
      return pol([A, ab, ac], ROXO[1]) + pol([ab, B, bc], ROXO[1]) + pol([ac, bc, C], ROXO[1]) + pol([ab, bc, ac], ROXO[2]);
    }
    if (qual === "cilindro") {
      return `<circle cx="110" cy="30" r="24" fill="#bae6fd" stroke="${TINTA}" stroke-width="2.5"/>
        <rect x="35" y="54" width="150" height="64" fill="#7dd3fc" stroke="${TINTA}" stroke-width="2.5"/>
        <circle cx="110" cy="142" r="24" fill="#bae6fd" stroke="${TINTA}" stroke-width="2.5"/>`;
    }
    return "";
  }

  /* ---------------- medidas ---------------- */
  function regua(n) {
    if (n === "mm") {
      const x0 = 20, esc = 90; // 1 cm = 90 px
      let o = `<rect x="10" y="70" width="200" height="56" rx="6" fill="#fde68a" stroke="${TINTA}" stroke-width="2.5"/>`;
      for (let mm = 0; mm <= 20; mm++) {
        const x = x0 + mm * esc / 10, h = mm % 10 === 0 ? 26 : mm % 5 === 0 ? 18 : 11;
        o += lin([x, 70], [x, 70 + h], { w: mm % 10 === 0 ? 2.5 : 1.6 });
        if (mm % 10 === 0) o += txt(x, 112, mm / 10, { tam: 16 });
      }
      o += `<path d="M ${x0} 58 L ${x0} 50 L ${x0 + esc} 50 L ${x0 + esc} 58" fill="none" stroke="${VERMELHO}" stroke-width="3"/>` + txt(x0 + esc / 2, 36, "1 cm", { cor: VERMELHO, tam: 16 });
      return o;
    }
    const comp = n ? Math.max(10, +n + 1) : 10, x0 = 18, larg = 186, esc = larg / comp;
    let o = `<rect x="8" y="88" width="206" height="54" rx="6" fill="#fde68a" stroke="${TINTA}" stroke-width="2.5"/>`;
    for (let c = 0; c <= comp; c++) {
      const x = x0 + c * esc;
      o += lin([x, 88], [x, 108], { w: 2 });
      if (c < comp) o += lin([x + esc / 2, 88], [x + esc / 2, 98], { w: 1.4 });
      if (comp <= 12 || c % 2 === 0) o += txt(x, 124, c, { tam: comp > 12 ? 11 : 13 });
    }
    if (n && +n > 0) {
      const xf = x0 + (+n) * esc;
      o += `<rect x="${x0}" y="58" width="${f(xf - x0 - 14)}" height="18" rx="4" fill="#60a5fa" stroke="${TINTA}" stroke-width="2"/>
        <polygon points="${f(xf - 14)},58 ${f(xf)},67 ${f(xf - 14)},76" fill="#fde68a" stroke="${TINTA}" stroke-width="2"/>
        <rect x="${x0 - 6}" y="58" width="10" height="18" rx="3" fill="#1e3a8a"/>` +
        lin([x0, 80], [x0, 88], { cor: VERMELHO, w: 2 }) + lin([xf, 80], [xf, 88], { cor: VERMELHO, w: 2 });
    }
    return o;
  }
  function metro(k) {
    k = Math.max(1, Math.min(10, +k || 1));
    const x0 = 15, L = 190, y = 70, cores = [OURO, "#fff7d6"];
    let o = txt(110, 40, "1 metro", { tam: 18 });
    o += `<path d="M ${x0} 52 L ${x0} 46 L ${x0 + L} 46 L ${x0 + L} 52" fill="none" stroke="${TINTA}" stroke-width="2"/>`;
    for (let i = 0; i < k; i++) o += `<rect x="${f(x0 + i * L / k)}" y="${y}" width="${f(L / k)}" height="40" fill="${k === 1 ? "#fde68a" : cores[i % 2]}" stroke="${TINTA}" stroke-width="2.5"/>`;
    if (k === 1) for (let c = 1; c < 10; c++) o += lin([x0 + c * L / 10, y], [x0 + c * L / 10, y + 12], { w: 1.6 });
    else for (let i = 0; i < k; i++) o += txt(x0 + (i + .5) * L / k, y + 62, "?", { tam: 16, cor: i ? "#9ca3af" : VERMELHO });
    return o;
  }
  function balanca(valor) {
    return `<ellipse cx="110" cy="58" rx="74" ry="14" fill="#e5e7eb" stroke="${TINTA}" stroke-width="2.5"/>
      <path d="M 70 52 Q 110 10 150 52 Z" fill="#fca5a5" stroke="${TINTA}" stroke-width="2.5"/>
      <rect x="104" y="66" width="12" height="16" fill="#9ca3af" stroke="${TINTA}" stroke-width="2"/>
      <path d="M 40 82 L 180 82 L 196 150 L 24 150 Z" fill="#cbd5e1" stroke="${TINTA}" stroke-width="2.5" stroke-linejoin="round"/>
      <rect x="54" y="96" width="112" height="38" rx="6" fill="#0f172a" stroke="${TINTA}" stroke-width="2"/>
      ${txt(110, 116, String(valor || "").replace(/^(\d)(\d{3})(?=\D|$)/, "$1 $2"), { tam: 20, cor: "#4ade80" })}`;
  }
  function jarra(ml, x = 50, y = 30, w = 120, h = 130, mostrarRotulo = true) {
    const nivel = Math.max(0, Math.min(1, (+ml || 0) / 1000));
    const topo = y + 18, fundo = y + h, alt = fundo - topo;
    const agua = fundo - alt * nivel;
    let o = `<path d="M ${x + w} ${y + 30} q ${w * .35} 8 ${w * .3} 40 q -4 30 -${w * .3} 34" fill="none" stroke="${TINTA}" stroke-width="5"/>`;
    o += `<rect x="${x}" y="${f(agua)}" width="${w}" height="${f(fundo - agua)}" fill="#7dd3fc" opacity=".9"/>`;
    o += `<path d="M ${x - 6} ${y} L ${x + w} ${y} L ${x + w} ${fundo} L ${x} ${fundo} L ${x} ${y + 8} Z" fill="#e0f2fe" fill-opacity=".25" stroke="${TINTA}" stroke-width="2.5" stroke-linejoin="round"/>`;
    for (let q = 1; q <= 4; q++) {
      const yy = fundo - alt * q / 4;
      o += lin([x + w - (q === 4 ? 34 : q === 2 ? 26 : 18), yy], [x + w, yy], { w: 2.2 });
    }
    if (mostrarRotulo) o += txt(x + w - 52, topo + 2, "1 L", { tam: 15 });
    return o;
  }
  function jarras(total) {
    const n = Math.ceil((+total || 0) / 1000), w = Math.min(70, 300 / n - 12);
    let o = "";
    for (let i = 0; i < n; i++) o += jarra(Math.min(1000, total - i * 1000), 14 + i * (w + 22), 40, w, 110, true);
    return { corpo: o, largura: Math.max(220, 14 + n * (w + 22) + 10) };
  }

  /* ---------------- quantidades e frações ---------------- */
  function partes(n) {
    n = Math.max(1, Math.min(12, +n || 2));
    const cx = 110, cy = 92, r = 72, cores = ["#fbbf24", "#fde68a"];
    if (n === 1) return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${cores[0]}" stroke="${TINTA}" stroke-width="2.5"/>`;
    let o = "";
    for (let i = 0; i < n; i++) {
      const a1 = -Math.PI / 2 + 2 * Math.PI * i / n, a2 = a1 + 2 * Math.PI / n;
      o += `<path d="M ${cx} ${cy} L ${f(cx + r * Math.cos(a1))} ${f(cy + r * Math.sin(a1))} A ${r} ${r} 0 0 1 ${f(cx + r * Math.cos(a2))} ${f(cy + r * Math.sin(a2))} Z" fill="${cores[i % 2]}" stroke="${TINTA}" stroke-width="2.5" stroke-linejoin="round"/>`;
    }
    return o;
  }
  const bolinhas = (n, x, y, w, cor) => {
    const col = Math.min(n, n <= 4 ? 2 : 3), lin_ = Math.ceil(n / col), d = Math.min(26, (w - 10) / col);
    let o = "";
    for (let i = 0; i < n; i++) o += `<circle cx="${f(x + (w - col * d) / 2 + d / 2 + (i % col) * d)}" cy="${f(y + d / 2 + Math.floor(i / col) * d)}" r="${f(d * .38)}" fill="${cor}" stroke="${TINTA}" stroke-width="1.8"/>`;
    return { o, h: lin_ * d };
  };
  function pontos(n, k) {
    n = +n || 1; k = +k || 1;
    const w = Math.min(90, 300 / k - 10), L = k * (w + 10) + 10, cores = ["#f472b6", "#60a5fa", "#34d399"];
    let o = "", hmax = 0;
    for (let i = 0; i < k; i++) {
      const b = bolinhas(n, 10 + i * (w + 10), 30, w, cores[i % 3]); hmax = Math.max(hmax, b.h);
      o += b.o;
    }
    for (let i = 0; i < k; i++) o = `<rect x="${f(6 + i * (w + 10))}" y="20" width="${f(w + 8)}" height="${f(hmax + 22)}" rx="14" fill="#fff" stroke="${TINTA}" stroke-width="2" stroke-dasharray="5 5"/>` + o;
    return { corpo: o, largura: Math.max(220, L), altura: hmax + 60 };
  }
  function dividir(n, k) {
    n = +n || 1; k = +k || 1;
    const todas = bolinhas(n, 10, 10, 200, "#f59e0b");
    const por = Math.floor(n / k), w = Math.min(90, 300 / k - 10);
    let grupos = "", hmax = 0;
    for (let i = 0; i < k; i++) {
      const b = bolinhas(por, 10 + i * (w + 10), 0, w, "#f59e0b"); hmax = Math.max(hmax, b.h);
      grupos += b.o;
    }
    const y2 = todas.h + 60;
    let caixas = "";
    for (let i = 0; i < k; i++) caixas += `<rect x="${f(6 + i * (w + 10))}" y="${f(y2 - 8)}" width="${f(w + 8)}" height="${f(hmax + 16)}" rx="14" fill="#fff7d6" stroke="${TINTA}" stroke-width="2" stroke-dasharray="5 5"/>`;
    const L = Math.max(220, k * (w + 10) + 10);
    const corpo = `<g transform="translate(${f((L - 220) / 2)},0)">${todas.o}</g>` +
      `<path d="M ${L / 2} ${todas.h + 16} L ${L / 2} ${todas.h + 42}" stroke="${TINTA}" stroke-width="3"/><polygon points="${L / 2 - 8},${todas.h + 38} ${L / 2 + 8},${todas.h + 38} ${L / 2},${todas.h + 48}" fill="${TINTA}"/>` +
      caixas + `<g transform="translate(0,${f(y2)})">${grupos}</g>`;
    return { corpo, largura: L, altura: y2 + hmax + 20 };
  }

  /* ---------------- perímetro ---------------- */
  const num = s => parseFloat(String(s).replace(",", ".")) || 1;
  function perimetro(forma, a, b, c, d) {
    const contorno = `stroke="#f97316" stroke-width="5" stroke-dasharray="10 6" fill="#fff7ed" stroke-linejoin="round"`;
    if (forma === "ret" || forma === "quad") {
      if (forma === "quad") b = a;
      const r = Math.max(.35, Math.min(1, num(b) / num(a))), W = 120, H = Math.max(50, Math.min(110, W * r));
      const x = (220 - W) / 2, y = (170 - H) / 2;
      return `<rect x="${x}" y="${f(y)}" width="${W}" height="${f(H)}" ${contorno}/>` +
        txt(110, y - 14, a) + txt(110, y + H + 16, a) + txt(x - 6, y + H / 2, b, { ancora: "end" }) + txt(x + W + 6, y + H / 2, b, { ancora: "start" });
    }
    if (forma === "tri") {
      const P = [[110, 22], [45, 148], [175, 148]];
      return `<polygon points="${pts(P)}" ${contorno}/>` + txt(66, 82, a, { ancora: "end" }) + txt(154, 82, b, { ancora: "start" }) + txt(110, 166, c);
    }
    if (forma === "trap") {
      const P = [[75, 40], [145, 40], [180, 140], [40, 140]];
      return `<polygon points="${pts(P)}" ${contorno}/>` + txt(110, 26, a) + txt(170, 88, b, { ancora: "start" }) + txt(110, 158, c) + txt(50, 88, d, { ancora: "end" });
    }
    return "";
  }

  /* ---------------- outros ---------------- */
  const circulo = () => `<circle cx="110" cy="90" r="66" fill="#fff7ed" stroke="#f97316" stroke-width="7"/><circle cx="110" cy="90" r="4" fill="${TINTA}"/>`;
  function barras() {
    const h = [40, 95, 60, 130, 75], cor = h.map(v => v === 130 ? OURO : "#a5b4fc");
    let o = lin([25, 15], [25, 155]) + lin([25, 155], [205, 155]);
    h.forEach((v, i) => o += `<rect x="${38 + i * 34}" y="${155 - v}" width="24" height="${v}" fill="${cor[i]}" stroke="${TINTA}" stroke-width="2"/>`);
    return o;
  }

  /* ---------------- grupos de sólidos ---------------- */
  function grupo(nome) {
    const lista = nome === "redondos" ? [esfera(), cone(), cilindro()] : [cubo(), piramide(4), prisma(3)];
    return { corpo: lista.map((s, i) => `<g transform="translate(${i * 110},10) scale(.5)">${s}</g>`).join(""), largura: 330, altura: 100 };
  }

  /* ---------------- entrada ---------------- */
  function desenhar(spec) {
    const [nome, ...a] = String(spec || "").split(":");
    try {
      if (SOLIDOS[nome]) return svg(220, 175, SOLIDOS[nome](a[0]), nome);
      if (nome === "plan") return svg(220, 180, planificacao(a[0]), "planificação");
      if (nome === "regua") return svg(222, 150, regua(a[0]), "régua");
      if (nome === "metro") return svg(220, 150, metro(a[0]), "metro");
      if (nome === "balanca") return svg(220, 165, balanca(a.join(":")), "balança");
      if (nome === "jarra") return svg(220, 170, jarra(a[0]), "jarra medidora");
      if (nome === "jarras") { const j = jarras(+a[0]); return svg(j.largura, 165, j.corpo, "jarras"); }
      if (nome === "partes") return svg(220, 180, partes(a[0]), "partes iguais");
      if (nome === "pontos") { const p = pontos(a[0], a[1]); return svg(p.largura, p.altura, p.corpo, "grupos"); }
      if (nome === "dividir") { const p = dividir(a[0], a[1]); return svg(p.largura, p.altura, p.corpo, "dividir"); }
      if (nome === "perim") return `<svg viewBox="-30 0 280 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="contorno da figura">${perimetro(...a)}</svg>`;
      if (nome === "circulo") return svg(220, 180, circulo(), "circunferência");
      if (nome === "barras") return svg(220, 165, barras(), "gráfico de barras");
      if (nome === "grupo") { const g = grupo(a[0]); return svg(g.largura, g.altura, g.corpo, "sólidos"); }
    } catch (e) { console.warn("ilustração", spec, e); }
    return "";
  }

  window.ILUS = { svg: desenhar };
})();
