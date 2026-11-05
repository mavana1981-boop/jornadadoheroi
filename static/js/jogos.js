/* Motor de jogos da Jornada do Herói.
   Cada tipo de atividade tem um "render" que desenha o desafio e chama fim(acertou, texto). */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const tela = $("#tela"), rodape = $("#rodape"), btnCont = $("#btn-continuar");
  const MODO = window.JOGO.modo;
  const FASES = {
    1: { nome: "Primeiros golpes", emoji: "🔥", texto: "Cartas mágicas e Verdade ou Mentira para esquentar!" },
    2: { nome: "Desafio", emoji: "⚔️", texto: "Jogos para treinar o que vai cair na prova." },
    3: { nome: "Chefão", emoji: "👾", texto: "Cada acerto tira vida do chefão!" },
  };
  const ELOGIOS = ["Mandou bem! 🎉", "Isso aí, herói! 💪", "Acertou em cheio! 🎯", "Que memória! 🧠", "Incrível! ⭐", "Golaço! ⚽"];
  const CONSOLO = ["Quase! Vamos aprender: ", "Tudo bem errar, herói! ", "Essa volta daqui a pouco! "];

  let D, fila = [], idx = 0, totalUnicos = 0, acertosPrimeira = 0, vistos = new Set(), faseAtual = 0;
  let hpChefe = 100, danoPorAcerto = 10;

  /* ------------------------- utilidades ------------------------- */
  const embaralhar = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const sorteio = a => a[Math.floor(Math.random() * a.length)];

  // sons: efeitos curtos (sem narração) — ver static/js/sons.js
  const som = (nome, ...x) => window.SONS && SONS.tocar(nome, ...x);
  let seguidas = 0;  // acertos seguidos (combo)

  function confete(dur = 2200) {
    const cv = $("#confete"), c = cv.getContext("2d");
    cv.width = innerWidth; cv.height = innerHeight;
    const cores = ["#ffbe0b", "#f15bb5", "#7c3aed", "#22c55e", "#1fa2ff", "#ff8a3d"];
    const ps = Array.from({ length: 140 }, () => ({ x: Math.random() * cv.width, y: -20 - Math.random() * cv.height * .5, r: 4 + Math.random() * 6, vy: 2 + Math.random() * 4, vx: -2 + Math.random() * 4, c: sorteio(cores), a: Math.random() * 6 }));
    const t0 = performance.now();
    (function q(t) {
      c.clearRect(0, 0, cv.width, cv.height);
      ps.forEach(p => { p.y += p.vy; p.x += p.vx; p.a += .1; c.save(); c.translate(p.x, p.y); c.rotate(p.a); c.fillStyle = p.c; c.fillRect(-p.r, -p.r / 2, p.r * 2, p.r); c.restore(); });
      if (t - t0 < dur) requestAnimationFrame(q); else c.clearRect(0, 0, cv.width, cv.height);
    })(t0);
  }

  function mostrarContinuar(txt = "Continuar ➜", acao = proximo) {
    rodape.style.display = "flex"; btnCont.textContent = txt; btnCont.onclick = () => { som("clique"); rodape.style.display = "none"; acao(); };
  }

  function cartao(item, conteudoHTML, enunciadoFala) {
    const tag = window.TIPOS_NOMES[item.tipo] || "";
    tela.innerHTML = `<div class="desafio">
      <span class="tag">${item.mundo.emoji} ${esc(item.materia)} · ${tag}</span>
      <div class="assunto-item">📘 ${esc(item.conteudo)}</div>
      ${(item.paginas || []).length ? `<button class="ver-livro" title="Ver as páginas do livro">📖 pág. ${esc(item.paginas_txt || "")}</button>` : ""}
      ${conteudoHTML}
      <div class="feedback" id="fb"></div></div>`;
    const vl = $(".ver-livro", tela);
    if (vl) vl.onclick = () => { som("clique"); abrirLivro(item.paginas, 0, item.conteudo); };
    return $(".desafio", tela);
  }

  window.TIPOS_NOMES = { quiz: "Desafio de escolha", vf: "Verdade ou Mentira", completar: "Complete a frase", contas: "Cálculo rápido",
    ligar: "Ligue os pares", memoria: "Jogo da memória", ordenar: "Coloque em ordem", categorizar: "Separe nos baús", flashcard: "Carta mágica" };


  /* ------------------------- ilustrações ------------------------- */
  // v = {svg} desenho exato do app | {img} imagem gerada/foto | undefined
  function vis(v, tam = "peq") {
    if (!v) return "";
    if (v.svg) { const d = window.ILUS ? ILUS.svg(v.svg) : ""; return d ? `<div class="ilus ${tam}">${d}</div>` : ""; }
    return `<div class="ilus ${tam}"><img src="${esc(v.img)}" alt="${esc(v.alt || "")}" loading="lazy" onerror="this.parentNode.classList.add('falhou')"></div>`;
  }
  // imagem do enunciado; se não houver (ou falhar), mostra o emoji
  const topo = (it, emoji) => it.visual
    ? `${vis(it.visual, "grande")}<div class="emoji-grande reserva">${esc(emoji || "")}</div>`
    : (emoji ? `<div class="emoji-grande">${esc(emoji)}</div>` : "");
  const temImg = (it, t) => !!(it.visuais && it.visuais[t]);
  const peca = (it, t) => `${vis(it.visuais && it.visuais[t])}<span class="peca-txt">${esc(t)}</span>`;

  /* --------------------------- renders --------------------------- */
  const R = {};

  R.quiz = (it, fim) => {
    const d = it.dados, ops = embaralhar(d.opcoes.map((t, i) => ({ t, ok: i === d.correta })));
    const comImg = ops.some(o => temImg(it, o.t));
    const el = cartao(it, `${topo(it, d.emoji)}
      <div class="enunciado">${esc(d.pergunta)}</div>
      <div class="opcoes ${comImg ? "com-img" : ops.every(o => o.t.length < 28) ? "duas" : ""}">${ops.map((o, i) => `<button class="op" data-i="${i}">${comImg ? peca(it, o.t) : esc(o.t)}</button>`).join("")}</div>`, d.pergunta + ". " + d.opcoes.join(", "));
    el.querySelectorAll(".op").forEach(b => b.onclick = () => {
      const o = ops[+b.dataset.i];
      el.querySelectorAll(".op").forEach((x, i) => { x.disabled = true; if (ops[i].ok) x.classList.add("certa"); });
      if (!o.ok) b.classList.add("errada");
      fim(o.ok, d.explicacao);
    });
  };

  R.completar = (it, fim) => {
    const d = it.dados, ops = embaralhar(d.opcoes.map((t, i) => ({ t, ok: i === d.correta })));
    const frase = esc(d.frase).replace("___", `<span class="lacuna" id="lac">?</span>`);
    const el = cartao(it, `${topo(it, "✏️")}<div class="enunciado">${frase}</div>
      <div class="opcoes duas">${ops.map((o, i) => `<button class="op" data-i="${i}">${esc(o.t)}</button>`).join("")}</div>`, d.frase);
    el.querySelectorAll(".op").forEach(b => b.onclick = () => {
      const o = ops[+b.dataset.i];
      $("#lac").textContent = ops.find(x => x.ok).t;
      el.querySelectorAll(".op").forEach((x, i) => { x.disabled = true; if (ops[i].ok) x.classList.add("certa"); });
      if (!o.ok) b.classList.add("errada");
      fim(o.ok, d.explicacao);
    });
  };

  R.vf = (it, fim) => {
    const d = it.dados;
    const el = cartao(it, `${topo(it, d.emoji || "🤔")}<div class="enunciado">${esc(d.afirmacao)}</div>
      <div class="vf"><button class="op" data-v="1">✅ Verdade</button><button class="op" data-v="0">❌ Mentira</button></div>`, d.afirmacao + ". Verdade ou mentira?");
    el.querySelectorAll(".op").forEach(b => b.onclick = () => {
      const escolha = b.dataset.v === "1", ok = escolha === d.resposta;
      el.querySelectorAll(".op").forEach(x => { x.disabled = true; if ((x.dataset.v === "1") === d.resposta) x.classList.add("certa"); });
      if (!ok) b.classList.add("errada");
      fim(ok, (d.resposta ? "É verdade! " : "É mentira! ") + (d.explicacao || ""));
    });
  };

  R.contas = (it, fim) => {
    const d = it.dados; let valor = "";
    const el = cartao(it, `${topo(it, d.emoji || "🧮")}<div class="enunciado">${esc(d.pergunta)}</div>
      <div class="visor"><span id="vis">_</span> <small>${esc(d.unidade || "")}</small></div>
      <div class="teclado">${[1, 2, 3, 4, 5, 6, 7, 8, 9, "⌫", 0, "✔"].map(k => `<button data-k="${k}">${k}</button>`).join("")}</div>`, d.pergunta);
    const vis = $("#vis", el);
    el.querySelectorAll(".teclado button").forEach(b => b.onclick = () => {
      const k = b.dataset.k; som("clique");
      if (k === "⌫") valor = valor.slice(0, -1);
      else if (k === "✔") {
        if (!valor) return;
        const ok = Number(valor) === Number(d.resposta);
        el.querySelectorAll(".teclado button").forEach(x => x.disabled = true);
        vis.parentElement.style.borderColor = ok ? "var(--ok)" : "var(--erro)";
        fim(ok, (ok ? "" : `A resposta é ${d.resposta} ${d.unidade || ""}. `) + (d.explicacao || ""));
        return;
      } else if (valor.length < 6) valor += k;
      vis.textContent = valor || "_";
    });
  };

  R.ligar = (it, fim) => {
    const d = it.dados, esq = embaralhar(d.pares.map((p, i) => ({ t: p[0], i }))), dir = embaralhar(d.pares.map((p, i) => ({ t: p[1], i })));
    let sel = null, erros = 0, feitos = 0;
    const el = cartao(it, `<div class="enunciado">🔗 ${esc(d.titulo)}</div><p class="mini">Toque em um item da esquerda e depois no par dele à direita.</p>
      <div class="colunas"><div class="opcoes">${esq.map(o => `<button class="op" data-l="${o.i}">${peca(it, o.t)}</button>`).join("")}</div>
      <div class="opcoes">${dir.map(o => `<button class="op" data-r="${o.i}">${peca(it, o.t)}</button>`).join("")}</div></div>`, d.titulo);
    el.querySelectorAll("[data-l]").forEach(b => b.onclick = () => { el.querySelectorAll("[data-l]").forEach(x => x.classList.remove("sel")); b.classList.add("sel"); sel = b; som("clique"); });
    el.querySelectorAll("[data-r]").forEach(b => b.onclick = () => {
      if (!sel) return;
      if (sel.dataset.l === b.dataset.r) {
        [sel, b].forEach(x => { x.classList.remove("sel"); x.classList.add("certa"); x.disabled = true; });
        sel = null; feitos++; som("par");
        if (feitos === d.pares.length) fim(erros <= 1, erros ? `Você completou com ${erros} erro(s).` : "Todos os pares de primeira!");
      } else {
        erros++; som("erro"); b.classList.add("errada"); setTimeout(() => b.classList.remove("errada"), 450);
      }
    });
  };

  R.memoria = (it, fim) => {
    const d = it.dados, cartas = embaralhar(d.pares.flatMap((p, i) => [{ t: p[0], i }, { t: p[1], i }]));
    let abertas = [], pares = 0, jogadas = 0, travado = false;
    const el = cartao(it, `<div class="enunciado">🧠 ${esc(d.titulo)}</div><p class="mini">Vire duas cartas e encontre os pares que combinam.</p>
      <div class="memoria">${cartas.map((c, k) => `<div class="carta-m" data-k="${k}"><div class="in"><div class="f">❓</div><div class="v ${temImg(it, c.t) ? "com-img" : ""}">${peca(it, c.t)}</div></div></div>`).join("")}</div>`, d.titulo);
    el.querySelectorAll(".carta-m").forEach(cv => cv.onclick = () => {
      if (travado || cv.classList.contains("virada")) return;
      cv.classList.add("virada"); abertas.push(cv); som("virar");
      if (abertas.length === 2) {
        jogadas++; travado = true;
        const [a, b] = abertas;
        if (cartas[a.dataset.k].i === cartas[b.dataset.k].i) {
          a.classList.add("par"); b.classList.add("par"); abertas = []; travado = false; pares++; som("par");
          if (pares === d.pares.length) fim(jogadas <= d.pares.length * 2 + 1, `Você achou tudo em ${jogadas} jogadas!`);
        } else setTimeout(() => { a.classList.remove("virada"); b.classList.remove("virada"); abertas = []; travado = false; }, 900);
      }
    });
  };

  R.ordenar = (it, fim) => {
    const d = it.dados, itens = embaralhar(d.itens.map((t, i) => ({ t, i })));
    const montada = [];
    const el = cartao(it, `<div class="enunciado">🔢 ${esc(d.titulo)}</div><p class="mini">Toque nos itens na ordem certa (do primeiro ao último).</p>
      <div class="ordem-alvo" id="alvo"></div><div class="opcoes">${itens.map((o, k) => `<button class="op op-linha" data-k="${k}">${peca(it, o.t)}</button>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn peq branco" id="limpar">↺ Recomeçar</button></div>`, d.titulo + ". " + d.itens.join(", "));
    const alvo = $("#alvo", el);
    const desenhar = () => alvo.innerHTML = montada.map((o, n) => `<div class="op sel op-linha"><b>${n + 1}.</b> ${peca(it, o.t)}</div>`).join("");
    el.querySelectorAll("[data-k]").forEach(b => b.onclick = () => {
      montada.push(itens[+b.dataset.k]); b.classList.add("feito"); som("clique"); desenhar();
      if (montada.length === itens.length) {
        const ok = montada.every((o, n) => o.i === n);
        $("#limpar", el).remove();
        el.querySelectorAll("[data-k]").forEach(x => x.remove());
        alvo.innerHTML = d.itens.map((t, n) => `<div class="op op-linha ${montada[n].i === n ? "certa" : "errada"}"><b>${n + 1}.</b> ${peca(it, t)}</div>`).join("");
        fim(ok, (ok ? "Ordem perfeita! " : "Veja a ordem certa acima. ") + (d.explicacao || ""));
      }
    });
    $("#limpar", el).onclick = () => { montada.length = 0; desenhar(); el.querySelectorAll("[data-k]").forEach(x => x.classList.remove("feito")); };
  };

  R.categorizar = (it, fim) => {
    const d = it.dados, itens = embaralhar(d.itens), coresBau = ["#7c3aed", "#f15bb5", "#1fa2ff"];
    let k = 0, erros = 0; const cont = d.categorias.map(() => 0);
    const el = cartao(it, `<div class="enunciado">🧺 ${esc(d.titulo)}</div><p class="mini">Coloque cada item no baú certo.</p>
      <div class="item-vez" id="vez"></div>
      <div class="baus">${d.categorias.map((c, i) => `<button class="bau-cat" data-c="${i}" style="background:${coresBau[i]}">🧰 ${esc(c)}<span class="cont" id="cnt${i}">0 itens</span></button>`).join("")}</div>`, d.titulo + ". Categorias: " + d.categorias.join(", "));
    const vez = $("#vez", el);
    const mostrar = () => { vez.innerHTML = temImg(it, itens[k].texto) ? `${vis(it.visuais[itens[k].texto], "medio")}<span>${esc(itens[k].texto)}</span>` : esc(itens[k].texto); vez.style.animation = "none"; vez.offsetHeight; vez.style.animation = ""; };
    mostrar();
    el.querySelectorAll(".bau-cat").forEach(b => b.onclick = () => {
      if (k >= itens.length) return;
      const ci = +b.dataset.c;
      if (d.categorias[ci] === itens[k].categoria) {
        som("par"); cont[ci]++; $("#cnt" + ci, el).textContent = cont[ci] + " itens"; k++;
        if (k === itens.length) { vez.textContent = "Baús cheios! 🎉"; fim(erros <= 1, erros ? `Você terminou com ${erros} erro(s).` : "Tudo no lugar certo!"); }
        else mostrar();
      } else {
        erros++; som("erro"); vez.style.borderColor = "var(--erro)"; vez.classList.add("op", "errada");
        setTimeout(() => { vez.classList.remove("op", "errada"); vez.style.borderColor = ""; }, 450);
      }
    });
  };

  R.flashcard = (it, fim) => {
    const d = it.dados;
    const el = cartao(it, `<div class="flash" id="fl"><div class="in">
        <div class="f">${it.visual ? `<div class="flash-img">${vis(it.visual, "medio")}</div>` : `<div style="font-size:56px">${esc(d.emoji || "🃏")}</div>`}${esc(d.frente)}<div class="dica">Pense na resposta… depois toque para virar!</div></div>
        <div class="v">${esc(d.verso)}</div></div></div>
      <div class="opcoes duas" id="auto" style="display:none"><button class="op" data-s="1">😎 Eu sabia!</button><button class="op" data-s="0">🤔 Preciso treinar</button></div>`, d.frente);
    $("#fl", el).onclick = () => { $("#fl", el).classList.add("virada"); $("#auto", el).style.display = "grid"; som("virar"); };
    el.querySelectorAll("[data-s]").forEach(b => b.onclick = () => {
      el.querySelectorAll("[data-s]").forEach(x => x.disabled = true);
      b.classList.add(b.dataset.s === "1" ? "certa" : "sel");
      fim(b.dataset.s === "1", b.dataset.s === "1" ? "" : "Essa carta vai voltar para você memorizar!", true);
    });
  };


  /* ----------------- páginas do livro (Aquecimento do Herói) ----------------- */
  function abrirLivro(fotos, inicio = 0, titulo = "") {
    if (!fotos || !fotos.length) return;
    let i = inicio, zoom = false, x0 = null;
    const ov = document.createElement("div");
    ov.className = "livro-ov";
    ov.innerHTML = `<div class="livro-topo"><div><b id="lv-pag"></b><div class="lv-tit">${esc(titulo)}</div></div><button class="livro-x" title="Fechar">✕</button></div>
      <div class="livro-area" id="lv-area"><img id="lv-img" alt=""></div>
      <div class="livro-pe"><button class="btn peq branco" id="lv-ant">◀</button><span class="mini" style="color:#fff">Toque na página para ampliar</span><button class="btn peq branco" id="lv-prox">▶</button></div>`;
    document.body.appendChild(ov);
    document.body.style.overflow = "hidden";
    const img = $("#lv-img", ov), area = $("#lv-area", ov);
    const mostrar = () => {
      zoom = false; img.classList.remove("zoom"); area.scrollTo(0, 0);
      img.src = fotos[i].url; img.alt = "Página " + fotos[i].n;
      $("#lv-pag", ov).textContent = `Página ${fotos[i].n}` + (fotos.length > 1 ? `  (${i + 1} de ${fotos.length})` : "");
      $("#lv-ant", ov).disabled = i === 0; $("#lv-prox", ov).disabled = i === fotos.length - 1;
      if (i + 1 < fotos.length) { const pre = new Image(); pre.src = fotos[i + 1].url; }
    };
    const fechar = () => { ov.remove(); document.body.style.overflow = ""; document.removeEventListener("keydown", tecla); };
    const ir = d => { const n = i + d; if (n >= 0 && n < fotos.length) { i = n; mostrar(); } };
    const tecla = e => { if (e.key === "Escape") fechar(); if (e.key === "ArrowRight") ir(1); if (e.key === "ArrowLeft") ir(-1); };
    $(".livro-x", ov).onclick = fechar;
    $("#lv-ant", ov).onclick = () => ir(-1);
    $("#lv-prox", ov).onclick = () => ir(1);
    img.onclick = () => { zoom = !zoom; img.classList.toggle("zoom", zoom); };
    area.addEventListener("touchstart", e => { x0 = zoom ? null : e.touches[0].clientX; }, { passive: true });
    area.addEventListener("touchend", e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 60) ir(dx < 0 ? 1 : -1);
    });
    document.addEventListener("keydown", tecla);
    mostrar();
  }

  const negrito = t => esc(t).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  const semMarcas = t => String(t || "").replace(/\*\*/g, "");

  function leitura() {
    const blocos = D.leitura || [];
    if (!blocos.length || MODO === "cartas") return proximo();
    window.scrollTo({ top: 0 });
    const txt = blocos.length === 1
      ? "Antes do desafio, leia o Resumo do Herói. Se quiser, abra as páginas do livro!"
      : `Antes do desafio, leia o Resumo do Herói de cada um dos ${blocos.length} assuntos. As páginas do livro ficam guardadas no botão 📖.`;
    tela.innerHTML = `<div class="fase-banner" style="padding-bottom:10px"><div class="grande">📖</div><h2>Aquecimento do Herói</h2></div>
      <div class="mentor" style="margin-bottom:14px"><div class="coruja">🦉</div><div class="balao">${esc(txt)}</div></div>
      ${blocos.map((b, bi) => {
        const r = b.resumo || { topicos: [] };
        return `<div class="leitura-bloco" data-b="${bi}" style="--c1:${b.mundo.cor};--c2:${b.mundo.cor2}">
        <div class="lb-topo"><span class="lb-emoji">${esc(b.emoji)}</span><div><b>${esc(b.titulo)}</b><div class="mini">${esc(b.materia)}${b.paginas ? " · pág. " + esc(b.paginas) : ""}</div></div><span class="lb-ok" id="ok${bi}"></span></div>
        ${r.topicos.length ? `<div class="resumo-heroi">
          <div class="rh-topo"><b>⚡ Resumo do Herói</b></div>
          <ul>${r.topicos.map(t => `<li><span class="rh-emoji">${esc(t.emoji)}</span><span>${negrito(t.texto)}</span></li>`).join("")}</ul>
          ${r.lembre ? `<div class="rh-lembre">💡 <b>Lembre:</b> ${negrito(r.lembre)}</div>` : ""}
        </div>` : ""}
        ${b.fotos.length ? `<button class="lb-livro" data-b="${bi}">📖 Ver no livro (${b.fotos.length} ${b.fotos.length === 1 ? "página" : "páginas"})</button>
          <div class="lb-tira" id="tira${bi}" hidden>${b.fotos.map((f, fi) => `<button class="lb-pag" data-b="${bi}" data-f="${fi}"><img src="${f.url}" alt="Página ${f.n}" loading="lazy"><span>pág. ${f.n}</span></button>`).join("")}</div>` : ""}
      </div>`;
      }).join("")}`;
    const marcar = bi => { $("#ok" + bi).textContent = "✅"; };
    tela.querySelectorAll(".lb-livro").forEach(el => el.onclick = () => {
      const t = $("#tira" + el.dataset.b);
      t.hidden = !t.hidden; som("clique");
      el.textContent = t.hidden ? el.textContent.replace("Esconder", "Ver no livro").replace("🙈", "📖") : el.textContent.replace("Ver no livro", "Esconder").replace("📖", "🙈");
    });
    tela.querySelectorAll(".lb-pag").forEach(el => el.onclick = () => {
      const b = +el.dataset.b, f = +el.dataset.f;
      som("clique"); marcar(b);
      abrirLivro(blocos[b].fotos, f, blocos[b].titulo);
    });
    mostrarContinuar("Já li! Começar o desafio ⚔️", proximo);
  }

  /* ---------------------------- fluxo ---------------------------- */
  function atualizarHud() {
    $("#barra").style.width = Math.round(100 * Math.min(vistos.size, totalUnicos) / Math.max(1, totalUnicos)) + "%";
    $("#placar").textContent = "⭐ " + acertosPrimeira;
  }

  function desenharArena() {
    const a = $("#arena");
    if (faseAtual !== 3 || MODO !== "missao") { a.innerHTML = ""; return; }
    const h = D.heroi;
    a.innerHTML = `<div class="arena">
      <div class="lado"><div class="avatar" style="--cor:${h.cor};margin:0 auto">${h.avatar}</div><div style="font-weight:800">${esc(h.nome)}</div></div>
      <div class="vs">VS</div>
      <div class="lado"><span class="monstro" id="monstro">${D.chefe.emoji}</span><div style="font-weight:800">${esc(D.chefe.nome)}</div>
      <div class="hp"><i id="hpchefe" style="width:${hpChefe}%"></i></div></div></div>`;
  }

  function intro() {
    const h = D.heroi;
    tela.innerHTML = `<div class="fase-banner">
      <div class="avatar grande" style="--cor:${h.cor};margin:0 auto 12px">${h.avatar}${(h.itens || []).map((e, i) => `<span class="equip e${i}">${e}</span>`).join("")}</div>
      <h2>${esc(D.tipo === "batalha_final" ? "⚔️ Batalha Final" : D.titulo || "Missão")}</h2></div>
      <div class="mentor"><div class="coruja">🦉</div><div class="balao">${esc(D.historia)}</div></div>`;
    if (D.dia && D.dia !== D.hoje) {
      const [a, m, d] = D.dia.split("-");
      tela.insertAdjacentHTML("afterbegin", `<div class="selo-adiantada${D.adiantada ? "" : " passada"}">${D.adiantada ? "⏩ Missão adiantada" : "⏪ Missão de um dia anterior"} · ${d}/${m}</div>`);
    }
    tela.insertAdjacentHTML("beforeend", quadroAssuntos(D.assuntos, D.tipo));
    if (D.status === "concluida") {
      tela.insertAdjacentHTML("beforeend", `<p style="color:#fff;text-align:center;font-weight:800;margin-top:16px">Você já cumpriu essa missão! Pode jogar de novo para treinar (sem novas recompensas de missão).</p>`);
    }
    mostrarContinuar(D.itens.length ? "Começar! ▶" : "Voltar", D.itens.length ? leitura : () => history.back());
  }

  // lista dos assuntos cobrados na missão, separada em "desafio" e "chefão"
  function quadroAssuntos(lista, tipo) {
    if (!lista || !lista.length) return "";
    const linha = a => `<li><span class="as-emoji">${esc(a.emoji)}</span><span class="as-txt"><b>${esc(a.titulo)}</b>
        <small>${esc(a.mundo_emoji)} ${esc(a.prova)}${a.paginas ? ` · pág. ${esc(a.paginas)}` : ""}</small></span></li>`;
    if (tipo === "batalha_final") {
      return `<div class="quadro-assuntos"><h3>📋 Tudo o que cai na prova</h3><ul>${lista.map(linha).join("")}</ul></div>`;
    }
    const desafio = lista.filter(a => a.fases.some(f => f < 3)), chefe = lista.filter(a => !a.fases.some(f => f < 3));
    return `<div class="quadro-assuntos"><h3>📋 Assuntos de hoje</h3><ul>${desafio.map(linha).join("")}</ul>
      ${chefe.length ? `<h4>${esc(D.chefe.emoji)} No Chefão também cai:</h4><ul>${chefe.map(linha).join("")}</ul>` : ""}</div>`;
  }

  function mostrarCombo(n) {
    const el = document.createElement("div");
    el.className = "combo-pop";
    el.innerHTML = `🔥 ${n} seguidas!<small>${n >= 10 ? "Imparável!" : n >= 5 ? "Pegando fogo!" : "Que sequência!"}</small>`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1600);
  }

  function bannerFase(f, depois) {
    const F = FASES[f];
    const nome = f === 3 ? `Chefão: ${D.chefe.nome}` : F.nome;
    tela.innerHTML = `<div class="fase-banner"><div class="grande">${f === 3 ? D.chefe.emoji : F.emoji}</div><h2>Fase ${f}: ${esc(nome)}</h2><p style="font-size:18px">${F.texto}</p></div>`;
    som("fase");
    mostrarContinuar("Vamos! ⚡", depois);
  }

  function proximo() {
    if (idx >= fila.length) return terminar();
    const item = fila[idx];
    if (MODO === "missao" && item.fase !== faseAtual) {
      faseAtual = item.fase;
      if (faseAtual === 3) {
        const n3 = fila.filter(x => x.fase === 3 && !x._retry).length || 1;
        danoPorAcerto = Math.ceil(100 / n3);
      }
      desenharArena();
      return bannerFase(faseAtual, () => mostrarItem(item));
    }
    mostrarItem(item);
  }

  function mostrarItem(item) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    const render = R[item.tipo];
    if (!render) { idx++; return proximo(); }
    render(item, (acertou, texto, silencioso) => resolver(item, acertou, texto, silencioso));
  }

  function resolver(item, acertou, texto, silencioso) {
    const primeira = !vistos.has(item.id);
    if (primeira) { vistos.add(item.id); if (acertou) acertosPrimeira++; }
    // a pré-visualização dos pais não grava nada
    if (MODO !== "previa") {
      fetch("/api/responder", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ atividade_id: item.id, acertou, missao_id: D.missao_id, modo: MODO === "missao" ? "missao" : "treino" }) });
    }
    const fb = $("#fb");
    if (acertou) {
      seguidas++;
      if (seguidas >= 2) window.SONS && SONS.combo(seguidas); else som("acerto");
      const fogo = seguidas >= 3 ? `<span class="combo">🔥 ${seguidas} seguidas!</span>` : "";
      fb.className = "feedback ok"; fb.innerHTML = `${fogo}<b>${sorteio(ELOGIOS)}</b> ${esc(texto || "")}`;
      if ([3, 5, 10, 15].includes(seguidas)) mostrarCombo(seguidas);
      if (faseAtual === 3 && MODO === "missao") {
        hpChefe = Math.max(0, hpChefe - danoPorAcerto);
        const m = $("#monstro"); if (m) { m.classList.remove("dano"); void m.offsetWidth; m.classList.add("dano"); som("dano"); }
        const hp = $("#hpchefe"); if (hp) hp.style.width = hpChefe + "%";
      }
    } else {
      seguidas = 0;
      som("erro"); fb.className = "feedback nao"; fb.innerHTML = `<b>${sorteio(CONSOLO)}</b>${esc(texto || "")}`;
      // repetição imediata: o desafio errado volta no fim da fase (uma vez)
      if (!item._retry) {
        const copia = Object.assign({}, item, { _retry: true });
        let pos = fila.length;
        for (let i = idx + 1; i < fila.length; i++) if (fila[i].fase !== item.fase) { pos = i; break; }
        fila.splice(pos, 0, copia);
      }
    }
    atualizarHud(); idx++;
    mostrarContinuar(idx >= fila.length ? "Ver recompensas 🎁" : "Continuar ➜");
  }

  async function terminar() {
    $("#arena").innerHTML = "";
    $("#barra").style.width = "100%";
    if (MODO === "previa") { tela.innerHTML = `<div class="final"><h2>Fim da prévia</h2></div>`; return mostrarContinuar("Voltar", () => history.back()); }
    const r = await fetch("/api/concluir", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ missao_id: D.missao_id, modo: MODO === "missao" ? "missao" : "treino", acertos: acertosPrimeira, total: totalUnicos }) });
    const j = await r.json();
    window.SONS && SONS.festa(j.estrelas); confete(j.estrelas >= 2 ? 3600 : 1800);
    const msg = j.estrelas === 3 ? "Missão perfeita! Você é uma lenda!" : j.estrelas === 2 ? "Muito bem! O chefão está fraquinho!" : "Missão completa! Amanhã você fica ainda mais forte!";
    tela.innerHTML = `<div class="final">
      <div class="estrelas">${[1, 2, 3].map(n => `<span class="estr-final ${n <= j.estrelas ? "ganha" : ""}" style="animation-delay:${1.5 + n * 0.35}s">${n <= j.estrelas ? "⭐" : "☆"}</span>`).join("")}</div>
      <h2 style="font-size:36px">${msg}</h2>
      <p style="font-size:20px">Você acertou <b>${acertosPrimeira}</b> de <b>${totalUnicos}</b> de primeira.</p>
      <div><span class="premio">⭐ +${j.bonus_xp + acertosPrimeira * (MODO === "missao" ? 10 : 5)} XP</span>
        <span class="premio">🪙 +${j.bonus_moedas + acertosPrimeira} moedas</span>
        ${MODO === "missao" ? `<span class="premio">🔥 ${j.streak} dia(s) seguidos</span>` : ""}</div>
      ${j.subiu_nivel ? `<h2 style="margin-top:18px">🎊 Subiu para o nível ${j.nivel}: ${esc(j.titulo)}!</h2>` : ""}
      ${(j.conquistas || []).map(c => `<div class="premio" style="background:#ffbe0b33">${c.emoji} Nova conquista: ${esc(c.nome)}</div>`).join("")}
    </div>`;
    for (let n = 0; n < j.estrelas; n++) setTimeout(() => som("estrela", n), 1850 + n * 350);
    setTimeout(() => som("moeda"), 2000 + j.estrelas * 350);
    if (j.subiu_nivel) setTimeout(() => { som("nivel"); confete(2500); }, 3000 + j.estrelas * 350);    if (MODO === "missao" && D.tem_proxima) {
      tela.insertAdjacentHTML("beforeend", `<div style="text-align:center;margin-top:14px">
        <a class="btn branco" href="/missao/proxima" onclick="SONS && SONS.tocar('clique')">⚔️ Próxima missão agora</a>
        <p class="mini" style="color:#fff;opacity:.85;margin-top:6px">Adianta a missão do próximo dia da trilha.</p></div>`);
    }
    mostrarContinuar(MODO === "missao" ? "Ver o herói andar no mapa 🧭" : "Voltar ao mapa 🗺️",
      () => location.href = MODO === "missao" ? "/?andou=1" : "/");
  }

  /* ------------------------------ início ------------------------------ */
  fetch(window.JOGO.api).then(r => r.json()).then(dados => {
    D = dados;
    fila = D.itens.slice();
    totalUnicos = fila.length;
    if (MODO !== "missao") fila.forEach(i => i.fase = 2);
    atualizarHud();
    if (MODO === "previa") return proximo();
    intro();
  }).catch(() => { tela.innerHTML = `<div class="fase-banner"><h2>Ops! Não consegui carregar a missão.</h2></div>`; });
})();
