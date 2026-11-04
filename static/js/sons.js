/* Efeitos sonoros da Jornada do Herói (sem narração).
   Todos os sons são sintetizados no próprio navegador (Web Audio), sem arquivos.
   SONS.tocar("acerto"), SONS.tocar("erro"), SONS.combo(n), SONS.festa(estrelas) …
   O botão 🔔/🔕 liga e desliga (fica lembrado no aparelho). */
(() => {
  let ctx = null, mestre = null;
  let mudo = false;
  try { mudo = localStorage.getItem("jornada_mudo") === "1"; } catch (e) { }

  function audio() {
    if (mudo) return null;
    try {
      if (!ctx) {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        const comp = ctx.createDynamicsCompressor();
        mestre = ctx.createGain(); mestre.gain.value = 0.55;
        mestre.connect(comp); comp.connect(ctx.destination);
      }
      if (ctx.state === "suspended") ctx.resume();
      return ctx;
    } catch (e) { return null; }
  }
  // o navegador só libera o som depois do primeiro toque na tela
  ["pointerdown", "keydown", "touchstart"].forEach(ev => addEventListener(ev, () => { if (!mudo) audio(); }, { once: true, passive: true }));

  /* nota com envelope: tipo de onda, frequência, início, duração, volume */
  function nota(f, t0, dur, { tipo = "sine", vol = 0.3, ataque = 0.008, deslize = 0, brilho = 0 } = {}) {
    const a = audio(); if (!a) return;
    const t = a.currentTime + t0;
    const o = a.createOscillator(), g = a.createGain();
    o.type = tipo; o.frequency.setValueAtTime(f, t);
    if (deslize) o.frequency.exponentialRampToValueAtTime(Math.max(30, f * deslize), t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + ataque);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(mestre);
    o.start(t); o.stop(t + dur + 0.02);
    if (brilho) {  // harmônico suave por cima: dá o "plim" de sininho
      const o2 = a.createOscillator(), g2 = a.createGain();
      o2.type = "sine"; o2.frequency.setValueAtTime(f * 2, t);
      g2.gain.setValueAtTime(0.0001, t); g2.gain.exponentialRampToValueAtTime(vol * brilho, t + ataque);
      g2.gain.exponentialRampToValueAtTime(0.0001, t + dur * 0.7);
      o2.connect(g2); g2.connect(mestre); o2.start(t); o2.stop(t + dur);
    }
  }
  /* ruído filtrado: estalos, “whoosh”, estouro de confete, palmas */
  function ruido(t0, dur, { vol = 0.25, de = 800, ate = 3000, tipo = "bandpass", q = 1 } = {}) {
    const a = audio(); if (!a) return;
    const t = a.currentTime + t0, n = Math.floor(a.sampleRate * dur);
    const buf = a.createBuffer(1, n, a.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    const s = a.createBufferSource(), f = a.createBiquadFilter(), g = a.createGain();
    s.buffer = buf; f.type = tipo; f.Q.value = q;
    f.frequency.setValueAtTime(de, t); f.frequency.exponentialRampToValueAtTime(ate, t + dur);
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.connect(f); f.connect(g); g.connect(mestre); s.start(t); s.stop(t + dur);
  }

  const N = { C5: 523.25, D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99, A5: 880, B5: 987.77, C6: 1046.5, D6: 1174.66, E6: 1318.5, G6: 1568, C4: 261.63, E4: 329.63, G4: 392 };

  const SONS = {
    // acerto: dois "plins" subindo, brilhante e rápido
    acerto() {
      nota(N.E5, 0, 0.16, { tipo: "triangle", vol: 0.32, brilho: 0.35 });
      nota(N.A5, 0.09, 0.32, { tipo: "triangle", vol: 0.34, brilho: 0.4 });
    },
    // erro: "bom-bom" grave e curto, sem ser assustador
    erro() {
      nota(311, 0, 0.16, { tipo: "triangle", vol: 0.28, deslize: 0.92 });
      nota(233, 0.13, 0.28, { tipo: "triangle", vol: 0.26, deslize: 0.85 });
    },
    clique() { nota(1400, 0, 0.05, { tipo: "sine", vol: 0.12 }); },
    // virar carta da memória
    virar() { ruido(0, 0.12, { vol: 0.18, de: 600, ate: 2600, q: 0.8 }); nota(900, 0.02, 0.06, { vol: 0.06 }); },
    // par encontrado / item no baú certo: um plim só
    par() { nota(N.G5, 0, 0.22, { tipo: "triangle", vol: 0.28, brilho: 0.4 }); nota(N.C6, 0.07, 0.3, { tipo: "sine", vol: 0.18 }); },
    // golpe no chefão
    dano() {
      ruido(0, 0.18, { vol: 0.4, de: 2400, ate: 200, tipo: "lowpass", q: 0.7 });
      nota(160, 0, 0.22, { tipo: "square", vol: 0.16, deslize: 0.5 });
    },
    // moeda / estrela aparecendo
    moeda() { nota(N.B5, 0, 0.08, { tipo: "square", vol: 0.12 }); nota(N.E6, 0.07, 0.3, { tipo: "square", vol: 0.12 }); },
    estrela(i = 0) { const f = [N.C6, N.E6, N.G6][i % 3]; nota(f, 0, 0.35, { tipo: "triangle", vol: 0.3, brilho: 0.5 }); ruido(0, 0.25, { vol: 0.08, de: 5000, ate: 9000, tipo: "highpass" }); },
    // começo de fase: chamada curta de trompete
    fase() {
      [[N.G4, 0], [N.C5, 0.1], [N.E5, 0.2], [N.G5, 0.3]].forEach(([f, t]) => nota(f, t, 0.18, { tipo: "sawtooth", vol: 0.11 }));
      nota(N.C6, 0.42, 0.38, { tipo: "sawtooth", vol: 0.12 });
    },
    // passo do herói no mapa
    passo(i = 0) { ruido(0, 0.07, { vol: 0.16, de: 300 + (i % 2) * 120, ate: 900, q: 2 }); },
    // chegada no dia de hoje no mapa
    chegada() { [N.C5, N.E5, N.G5, N.C6].forEach((f, i) => nota(f, i * 0.08, 0.3, { tipo: "triangle", vol: 0.26, brilho: 0.3 })); },
    // subir de nível
    nivel() {
      [N.C5, N.E5, N.G5, N.C6, N.E6, N.G6].forEach((f, i) => nota(f, i * 0.07, 0.25, { tipo: "square", vol: 0.1 }));
      nota(N.C6, 0.45, 0.7, { tipo: "triangle", vol: 0.3, brilho: 0.5 });
    },
  };

  // acertos seguidos: o "plim" vai subindo de tom (2, 3, 4… seguidas)
  function combo(n) {
    const escala = [N.C5, N.D5, N.E5, N.G5, N.A5, N.C6, N.D6, N.E6];
    const base = escala[Math.min(n - 1, escala.length - 1)];
    nota(base, 0, 0.14, { tipo: "triangle", vol: 0.3, brilho: 0.35 });
    nota(base * 1.5, 0.08, 0.3, { tipo: "triangle", vol: 0.32, brilho: 0.45 });
    if (n >= 5) nota(base * 2, 0.16, 0.35, { tipo: "sine", vol: 0.2 });
  }

  // festa: estouro de confete + fanfarra + palmas (mais caprichada com mais estrelas)
  function festa(estrelas = 3) {
    ruido(0, 0.25, { vol: 0.5, de: 4000, ate: 300, tipo: "lowpass" });          // POP!
    ruido(0.02, 0.6, { vol: 0.12, de: 6000, ate: 9000, tipo: "highpass" });       // confete chiando
    const tema = [[N.C5, 0.1, .14], [N.C5, 0.25, .14], [N.C5, 0.4, .14], [N.E5, 0.55, .3], [N.C5, 0.9, .18], [N.E5, 1.08, .18], [N.G5, 1.26, .6]];
    tema.forEach(([f, t, d]) => { nota(f, t, d, { tipo: "sawtooth", vol: 0.1 }); nota(f / 2, t, d, { tipo: "triangle", vol: 0.12 }); });
    [N.C4, N.E4, N.G4].forEach(f => nota(f, 1.26, 0.9, { tipo: "triangle", vol: 0.14 }));  // acorde final
    if (estrelas >= 2) [N.C6, N.E6, N.G6].forEach((f, i) => nota(f, 1.3 + i * 0.09, 0.4, { tipo: "triangle", vol: 0.2, brilho: 0.5 }));
    const palmas = estrelas >= 3 ? 14 : estrelas === 2 ? 9 : 5;
    for (let i = 0; i < palmas; i++) ruido(1.45 + i * 0.11 + Math.random() * 0.05, 0.08, { vol: 0.22, de: 1200, ate: 2400, q: 1.5 });
  }

  function tocar(nome, ...args) { try { (SONS[nome] || (() => { }))(...args); } catch (e) { } }

  function alternarMudo() {
    mudo = !mudo;
    try { localStorage.setItem("jornada_mudo", mudo ? "1" : "0"); } catch (e) { }
    if (!mudo) tocar("acerto");
    document.querySelectorAll("[data-som]").forEach(b => b.textContent = mudo ? "🔕" : "🔔");
    return mudo;
  }
  addEventListener("DOMContentLoaded", () => document.querySelectorAll("[data-som]").forEach(b => {
    b.textContent = mudo ? "🔕" : "🔔";
    b.title = "Ligar/desligar os sons";
    b.onclick = alternarMudo;
  }));

  window.SONS = { tocar, combo, festa, alternarMudo, get mudo() { return mudo; } };
})();
