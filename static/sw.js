/* Service worker da Jornada do Herói.
   - Páginas: tenta a internet primeiro; sem conexão, mostra a última versão salva (ou o aviso offline).
   - Arquivos fixos, páginas do livro e ilustrações: usa a cópia salva e atualiza por trás.
   - Respostas do jogo (/api) e do Painel dos Pais nunca são guardadas. */
const VERSAO = "jornada-v1";
const FIXOS = ["/static/css/style.css", "/static/js/jogos.js", "/static/js/ilustracoes.js",
  "/static/icones/icone-192.png", "/static/icones/icone-512.png", "/offline"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(FIXOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const guardavel = url => url.pathname.startsWith("/static/") || url.pathname.startsWith("/pagina/") ||
  url.pathname.startsWith("/ilustracao/");

self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/pais")) return;

  if (guardavel(url)) {
    e.respondWith(caches.open(VERSAO).then(async c => {
      const salvo = await c.match(req);
      const rede = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => salvo);
      return salvo || rede;
    }));
    return;
  }

  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(VERSAO).then(c => c.put(req, copia)); }
      return r;
    }).catch(async () => (await caches.match(req)) || caches.match("/offline")));
  }
});
