/* Cópia do progresso guardada no celular (localStorage).
   - Na tela inicial: baixa o progresso do servidor e guarda (sem nunca trocar uma cópia maior por uma menor).
   - Se o servidor tiver menos progresso que a cópia (banco apagado), oferece "Recuperar meu progresso". */
(() => {
  const K = "jornada_copia_progresso";
  const ler = () => { try { return JSON.parse(localStorage.getItem(K) || "null"); } catch (e) { return null; } };
  const gravar = b => { try { localStorage.setItem(K, JSON.stringify(b)); } catch (e) { } };
  const feitas = b => (b.missoes || []).filter(m => m.status === "concluida").length;
  const peso = b => (b && b.heroi ? (b.heroi.xp || 0) + 50 * feitas(b) : -1);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));

  function oferecer(copia, onde) {
    if (!onde || document.getElementById("recuperar")) return;
    const h = copia.heroi, quando = (copia.gerado_em || "").slice(0, 16).replace("T", " às ");
    onde.insertAdjacentHTML("afterbegin", `<div class="recuperar" id="recuperar">
      <div style="font-size:42px">${esc(h.avatar)}</div>
      <div><b>Encontrei o progresso de ${esc(h.nome)} guardado neste celular!</b>
        <small>⭐ ${h.xp} XP · 🪙 ${h.moedas} moedas · ${feitas(copia)} ${feitas(copia) === 1 ? "missão" : "missões"} · cópia de ${esc(quando)}</small>
        <button class="btn verde peq" id="rec-btn">♻️ Recuperar meu progresso</button></div></div>`);
    document.getElementById("rec-btn").onclick = async e => {
      e.target.disabled = true; e.target.textContent = "Recuperando…";
      const r = await fetch("/api/restaurar-local", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(copia)});
      if (r.ok) { window.SONS && SONS.festa(3); setTimeout(() => location.href = "/", 1200); }
      else { const j = await r.json().catch(() => ({})); e.target.textContent = j.erro || "Não deu certo"; }
    };
  }

  addEventListener("DOMContentLoaded", async () => {
    const copia = ler();
    const pagina = document.body.dataset.pagina;
    if (pagina === "criar-heroi") {           // banco sem herói
      if (copia && copia.heroi) oferecer(copia, document.querySelector(".wrap"));
      return;
    }
    if (pagina !== "inicio") return;
    try {
      const r = await fetch("/api/backup", {cache: "no-store"});
      if (!r.ok) return;
      const atual = await r.json();
      if (!copia || peso(atual) >= peso(copia)) gravar(atual);
      else oferecer(copia, document.querySelector(".wrap"));   // servidor perdeu progresso
    } catch (e) { }
  });
})();
