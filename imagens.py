"""Imagens das atividades: cadastro dos pedidos, geração em segundo plano e entrega ao jogo.

- Pedidos "g:" são gerados pelo Gemini. Se a chave não puder gerar imagens (sem faturamento),
  o app passa a usar fotos livres da Wikipédia/Commons para todos os pedidos que faltam.
- Pedidos "w:" vêm direto da Wikipédia/Commons.
- Cada imagem é reduzida (512 px) e guardada no banco: é gerada uma vez só.
"""
import hashlib
import io
import threading
import time

import requests
from flask import url_for

import gemini
import ilustracoes
from models import Atividade, Config, Imagem, db

UA = {"User-Agent": "JornadaDoHeroi/1.0 (app educativo infantil)"}
CUSTO_GEMINI_US = 0.034
TIPOS = ("g:", "w:", "k:", "c:")   # ilustração | foto livre | castelo recortado | cenário vertical
_estado = {"rodando": False, "feitas": 0, "inicio": None}
_trava = threading.Lock()


def chave(spec):
    return hashlib.sha1(spec.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Cadastro dos pedidos
# ---------------------------------------------------------------------------
def registrar(specs):
    """Garante uma linha para cada pedido de imagem (não gera nada)."""
    specs = {s for s in specs if s and s.startswith(TIPOS)}
    if not specs:
        return
    existentes = {c for (c,) in db.session.query(Imagem.chave).filter(Imagem.chave.in_([chave(s) for s in specs]))}
    for s in specs:
        if chave(s) not in existentes:
            db.session.add(Imagem(chave=chave(s), spec=s[:400]))
    db.session.commit()


def registrar_todas():
    specs = set(ilustracoes.specs_do_mapa())
    for a in Atividade.query.filter_by(ativa=True).all():
        specs.update(ilustracoes.specs_de_imagem(a.tipo, a.d()))
    registrar(specs)


# ---------------------------------------------------------------------------
# Entrega ao jogo
# ---------------------------------------------------------------------------
_cache_ok = {"quando": 0, "chaves": set()}


def _prontas():
    if time.time() - _cache_ok["quando"] > 20:
        _cache_ok["chaves"] = {c for (c,) in db.session.query(Imagem.chave).filter_by(status="ok")}
        _cache_ok["quando"] = time.time()
    return _cache_ok["chaves"]


def resolver(spec, legenda=""):
    """Visual pronto para o navegador: {'svg': spec} | {'img': url} | None (ainda não gerada)."""
    if not spec:
        return None
    if spec.startswith("svg:"):
        return {"svg": spec[4:], "alt": legenda}
    if not spec.startswith(TIPOS):
        return None
    if chave(spec) in _prontas():
        return {"img": url_for("ilustracao", chave=chave(spec)), "alt": legenda}
    return None


def visuais_para(atividade):
    v = ilustracoes.visuais_da_atividade(atividade.tipo, atividade.d())
    faltam = [s for s in ([v["enunciado"]] + list(v["pecas"].values())) if s and s.startswith(TIPOS)]
    if faltam:
        registrar(faltam)  # atividades novas entram na fila sozinhas
    return {"visual": resolver(v["enunciado"]),
            "visuais": {t: r for t, s in v["pecas"].items() if (r := resolver(s, t))}}


# ---------------------------------------------------------------------------
# Geração
# ---------------------------------------------------------------------------
def _recortar_fundo(bruto):
    """Castelo: remove o fundo branco a partir das bordas e devolve um PNG transparente."""
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.open(io.BytesIO(bruto)).convert("RGB")
    im.thumbnail((640, 640))
    w, h = im.size
    marca = (255, 0, 255)
    trab = im.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        r, g, b = trab.getpixel((x, y))
        if min(r, g, b) > 200 and trab.getpixel((x, y)) != marca:
            ImageDraw.floodfill(trab, (x, y), marca, thresh=48)
    alfa = Image.new("L", (w, h), 255)
    px, pa = trab.load(), alfa.load()
    for yy in range(h):
        for xx in range(w):
            if px[xx, yy] == marca:
                pa[xx, yy] = 0
    alfa = alfa.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out_im = im.convert("RGBA")
    out_im.putalpha(alfa)
    caixa = alfa.point(lambda v: 255 if v > 20 else 0).getbbox()
    if caixa:
        out_im = out_im.crop(caixa)
    out_im.thumbnail((512, 512))
    out = io.BytesIO()
    out_im.save(out, "PNG", optimize=True)
    return out.getvalue()


def _reduzir(bruto, maximo=(512, 512), qualidade=82):
    from PIL import Image, ImageOps
    im = Image.open(io.BytesIO(bruto))
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, "white")
        fundo.paste(im, mask=im.split()[-1])
        im = fundo
    else:
        im = im.convert("RGB")
    im.thumbnail(maximo)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=qualidade, optimize=True, progressive=True)
    return out.getvalue()


def _wikipedia(termo):
    """URL de uma foto livre: imagem principal do artigo da Wikipédia ou busca no Commons."""
    for base in ("https://pt.wikipedia.org/w/api.php", "https://en.wikipedia.org/w/api.php"):
        r = requests.get(base, params={"action": "query", "titles": termo, "prop": "pageimages",
                                       "piprop": "thumbnail", "pithumbsize": 600, "redirects": 1,
                                       "format": "json"}, headers=UA, timeout=20)
        if r.ok:
            for pag in r.json().get("query", {}).get("pages", {}).values():
                src = (pag.get("thumbnail") or {}).get("source")
                if src:
                    return src
    r = requests.get("https://commons.wikimedia.org/w/api.php",
                     params={"action": "query", "generator": "search", "gsrsearch": termo, "gsrnamespace": 6,
                             "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|mime", "iiurlwidth": 600,
                             "format": "json"}, headers=UA, timeout=20)
    if r.ok:
        paginas = sorted(r.json().get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
        for pag in paginas:
            info = (pag.get("imageinfo") or [{}])[0]
            if info.get("mime") in ("image/jpeg", "image/png") and info.get("thumburl"):
                return info["thumburl"]
    return None


def _baixar(url):
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r.content


def gerar_uma(img):
    """Gera/baixa uma imagem. Atualiza a linha. Devolve True se ficou pronta."""
    img.tentativas = (img.tentativas or 0) + 1
    tipo, _, resto = img.spec.partition(":")
    descricao, _, termo_wiki = resto.partition("|")
    bloqueado = Config.get("imagens_gemini_bloqueado")
    try:
        img.mime = "image/jpeg"
        if tipo in ("g", "k", "c") and gemini.disponivel() and not bloqueado:
            estilo = {"k": gemini.ESTILO_CASTELO, "c": gemini.ESTILO_CENARIO}.get(tipo)
            try:
                bruto, _mime, modelo = gemini.gerar_imagem(descricao, Config.get("imagens_modelo"), estilo=estilo,
                                                           proporcao="9:16" if tipo == "c" else "1:1")
                if tipo == "k":
                    img.dados, img.mime = _recortar_fundo(bruto), "image/png"
                elif tipo == "c":
                    img.dados = _reduzir(bruto, (720, 1280), 78)
                else:
                    img.dados = _reduzir(bruto)
                img.origem = "gemini"
                Config.set("imagens_modelo", modelo)
            except gemini.GeminiSemFaturamento as e:
                Config.set("imagens_gemini_bloqueado", str(e)[:480])
                db.session.commit()
                return gerar_uma(img) if img.tentativas < 3 else False
        else:
            if tipo == "c":
                raise RuntimeError("cenários só podem ser gerados pelo Gemini (o mapa usa as cores do mundo enquanto isso)")
            termo = descricao if tipo == "w" else (termo_wiki or descricao)
            url = _wikipedia(termo)
            if not url:
                raise RuntimeError(f"nenhuma foto livre encontrada para “{termo}”")
            img.dados, img.origem = _reduzir(_baixar(url)), "wikipedia"
        img.status, img.erro = "ok", ""
        db.session.commit()
        _cache_ok["quando"] = 0
        return True
    except Exception as e:  # noqa: BLE001 — qualquer falha vira "falha" e o lote continua
        db.session.rollback()
        img = db.session.get(Imagem, img.id)
        img.status, img.erro = "falha", str(e)[:300]
        db.session.commit()
        return False


def _laco(app):
    with app.app_context():
        try:
            while True:
                with _trava:
                    # castelos e cenários do mapa primeiro (são poucos e aparecem logo na tela inicial)
                    prioridade = db.case((Imagem.spec.like("k:%"), 0), (Imagem.spec.like("c:%"), 0), else_=1)
                    img = Imagem.query.filter_by(status="pendente").order_by(prioridade, Imagem.id).first()
                    if not img:
                        break
                    img.status = "gerando"
                    db.session.commit()
                gerar_uma(img)
                _estado["feitas"] += 1
                time.sleep(0.5)
        finally:
            _estado["rodando"] = False
            db.session.remove()


def iniciar(app):
    """Começa a gerar em segundo plano. Devolve False se já estava rodando."""
    if _estado["rodando"]:
        return False
    # linhas presas em "gerando" (o servidor reiniciou no meio) voltam para a fila
    Imagem.query.filter_by(status="gerando").update({"status": "pendente"})
    db.session.commit()
    _estado.update(rodando=True, feitas=0, inicio=time.time())
    threading.Thread(target=_laco, args=(app,), daemon=True).start()
    return True


def refazer_falhas():
    n = Imagem.query.filter_by(status="falha").update({"status": "pendente"})
    db.session.commit()
    return n


def situacao():
    contagem = dict(db.session.query(Imagem.status, db.func.count(Imagem.id)).group_by(Imagem.status).all())
    pend_g = (Imagem.query.filter(Imagem.status.in_(["pendente", "gerando"]),
                                  db.or_(Imagem.spec.like("g:%"), Imagem.spec.like("k:%"), Imagem.spec.like("c:%"))).count())
    origens = dict(db.session.query(Imagem.origem, db.func.count(Imagem.id)).filter_by(status="ok")
                   .group_by(Imagem.origem).all())
    bloqueado = Config.get("imagens_gemini_bloqueado") or ""
    return {
        "prontas": contagem.get("ok", 0), "pendentes": contagem.get("pendente", 0) + contagem.get("gerando", 0),
        "falhas": contagem.get("falha", 0), "total": sum(contagem.values()),
        "gemini": origens.get("gemini", 0), "wikipedia": origens.get("wikipedia", 0),
        "custo_estimado": round(pend_g * CUSTO_GEMINI_US, 2) if gemini.disponivel() and not bloqueado else 0,
        "rodando": _estado["rodando"], "feitas_agora": _estado["feitas"],
        "bloqueado": bloqueado, "gemini_ok": gemini.disponivel(), "modelo": Config.get("imagens_modelo") or "",
        "ultimas_falhas": [{"spec": i.spec[:80], "erro": i.erro} for i in
                           Imagem.query.filter_by(status="falha").order_by(Imagem.id.desc()).limit(5)],
    }


def visuais_do_mapa(materia):
    """URLs prontas do castelo e do cenário de um mundo (ou None enquanto não foram geradas)."""
    m = ilustracoes.mapa_do_mundo(materia)
    if not m:
        return {"castelo_img": None, "cenario_img": None}
    c, k = resolver(m["cenario"]), resolver(m["castelo"])
    return {"castelo_img": k["img"] if k else None, "cenario_img": c["img"] if c else None}
