"""Jornada do Herói — app de revisão gamificada para o 3º ano (Flask)."""
import io
import json
import os
import random
import re
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (Flask, abort, flash, jsonify, redirect, render_template, request,
                   send_file, session, url_for)

import gemini
import imagens
import missoes
from conteudo_inicial import PROVAS
from models import (MUNDOS, TIPOS, Atividade, Config, Conteudo, Heroi, Missao, PaginaFoto, Prova,
                    Resposta, db, mundo_de)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave")
url_db = os.environ.get("DATABASE_URL", "sqlite:///jornada.db")
if url_db.startswith("postgres://"):
    url_db = url_db.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = url_db
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024
db.init_app(app)

AVATARES = ["🦸‍♂️", "🧙‍♂️", "🥷", "🧑‍🚀", "🤴", "🦊", "🐲", "🤖", "🦁", "🐼", "⚽", "🦖"]
CORES = ["#ff8a3d", "#2bb673", "#1fa2ff", "#9b5de5", "#f15bb5", "#ef476f", "#ffbe0b"]

# Loja: itens comprados com moedas e mostrados ao redor do herói
LOJA = [
    {"id": "capa", "nome": "Capa Vermelha", "emoji": "🧣", "preco": 30},
    {"id": "escudo", "nome": "Escudo do Saber", "emoji": "🛡️", "preco": 50},
    {"id": "espada", "nome": "Espada da Memória", "emoji": "🗡️", "preco": 60},
    {"id": "bota", "nome": "Botas Velozes", "emoji": "👟", "preco": 40},
    {"id": "coroa", "nome": "Coroa de Campeão", "emoji": "👑", "preco": 120},
    {"id": "varinha", "nome": "Varinha Mágica", "emoji": "🪄", "preco": 80},
    {"id": "bola", "nome": "Bola de Ouro", "emoji": "🏆", "preco": 150},
    {"id": "pet_coruja", "nome": "Pet Corujinha", "emoji": "🦉", "preco": 90},
    {"id": "pet_dragao", "nome": "Pet Dragãozinho", "emoji": "🐉", "preco": 200},
    {"id": "pet_cachorro", "nome": "Pet Cãozinho", "emoji": "🐶", "preco": 70},
    {"id": "foguete", "nome": "Foguete Turbo", "emoji": "🚀", "preco": 180},
    {"id": "estrela", "nome": "Estrela Brilhante", "emoji": "🌟", "preco": 100},
]
LOJA_POR_ID = {i["id"]: i for i in LOJA}

CONQUISTAS = [
    ("primeira", "Primeira Missão", "🎯", lambda h, s: s["missoes"] >= 1),
    ("tres_dias", "3 dias seguidos", "🔥", lambda h, s: h.streak >= 3),
    ("semana", "7 dias seguidos", "🌋", lambda h, s: h.streak >= 7),
    ("cem", "100 acertos", "💯", lambda h, s: s["acertos"] >= 100),
    ("perfeita", "Missão perfeita", "⭐", lambda h, s: s["perfeitas"] >= 1),
    ("nivel3", "Chegou ao nível 3", "🏅", lambda h, s: h.nivel >= 3),
    ("dominio", "Dominou um conteúdo", "🧠", lambda h, s: s["dominados"] >= 1),
    ("colecionador", "Comprou 3 itens", "🎒", lambda h, s: len(h.lista_itens()) >= 3),
]


# ---------------------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------------------
VERSAO_CONTEUDO = "3-partes-kg-litro"


def _nova_atividade(cont, tipo, dados):
    v = gemini.validar(tipo, dados)
    if v:
        db.session.add(Atividade(conteudo=cont, tipo=v["tipo"], dados=json.dumps(v["dados"], ensure_ascii=False),
                                 origem="livro"))


def carregar_conteudo_inicial():
    """Banco vazio: cria as provas do Orientador de Estudos com todo o conteúdo."""
    from datetime import date as d_
    for p in PROVAS:
        prova = Prova(materia=p["materia"], titulo=p["titulo"], data=d_.fromisoformat(p["data"]))
        db.session.add(prova)
        for ordem, c in enumerate(p["conteudos"]):
            cont = Conteudo(prova=prova, titulo=c["titulo"], resumo=c["resumo"], paginas=c.get("paginas", ""),
                            emoji=c.get("emoji", "📘"), ordem=ordem)
            db.session.add(cont)
            for tipo, dados in c["atividades"]:
                _nova_atividade(cont, tipo, dados)
    Config.set("datas_provisorias", "0")
    Config.set("conteudo_versao", VERSAO_CONTEUDO)
    db.session.commit()


def sincronizar_conteudo():
    """Banco já existente: reorganiza nas provas do Orientador sem perder o progresso.

    Conteúdos e atividades já existentes são reaproveitados (mantêm acertos, erros e revisões);
    só o que é novo é criado. Provas antigas que ficarem vazias são removidas.
    """
    from datetime import date as d_
    # atividades do livro já existentes, por (tipo, dados) — serão movidas, não recriadas
    pool = {}
    for a in Atividade.query.filter_by(origem="livro").all():
        pool.setdefault((a.tipo, a.dados), []).append(a)
    usados = set()
    titulos_novos = {p["titulo"] for p in PROVAS}
    for p in PROVAS:
        prova = Prova.query.filter_by(titulo=p["titulo"]).first()
        if not prova:
            prova = Prova(titulo=p["titulo"], materia=p["materia"])
            db.session.add(prova)
        prova.materia = p["materia"]
        prova.data = d_.fromisoformat(p["data"])
        prova.ativa = True
        for ordem, c in enumerate(p["conteudos"]):
            nomes = [c["titulo"]] + c.get("antes", [])
            cont = next((x for x in Conteudo.query.filter(Conteudo.titulo.in_(nomes)).order_by(Conteudo.id).all()
                         if x.id not in usados), None)
            if not cont:
                cont = Conteudo()
                db.session.add(cont)
            cont.prova = prova
            cont.titulo, cont.resumo = c["titulo"], c["resumo"]
            cont.paginas, cont.emoji, cont.ordem = c.get("paginas", ""), c.get("emoji", "📘"), ordem
            db.session.flush()
            usados.add(cont.id)
            for tipo, dados in c["atividades"]:
                v = gemini.validar(tipo, dados)
                if not v:
                    continue
                chave = (v["tipo"], json.dumps(v["dados"], ensure_ascii=False))
                if pool.get(chave):
                    pool[chave].pop(0).conteudo = cont
                else:
                    db.session.add(Atividade(conteudo=cont, tipo=chave[0], dados=chave[1], origem="livro"))
    db.session.flush()
    for prova in Prova.query.all():
        for c in list(prova.conteudos):
            if c.id not in usados and not c.atividades:
                db.session.delete(c)
    db.session.flush()
    for prova in Prova.query.all():
        if prova.titulo not in titulos_novos and not prova.conteudos:
            db.session.delete(prova)
    Config.set("datas_provisorias", "0")
    Config.set("conteudo_versao", VERSAO_CONTEUDO)
    db.session.commit()
    m = Missao.query.filter_by(data=date.today()).first()
    if m and m.status != "concluida":
        Resposta.query.filter_by(missao_id=m.id).delete()
        db.session.delete(m)
        db.session.commit()


with app.app_context():
    db.create_all()
    if not Prova.query.first():
        carregar_conteudo_inicial()
    elif Config.get("conteudo_versao") != VERSAO_CONTEUDO:
        sincronizar_conteudo()
    imagens.registrar_todas()  # cadastra as ilustrações que faltam (não gera nada sozinho)

# ---------------------------------------------------------------------------
# Páginas do livro (fotos) — para o "Aquecimento do Herói"
# ---------------------------------------------------------------------------
PASTA_PAGINAS = os.path.join(app.root_path, "static", "paginas")


def _paginas_estaticas():
    try:
        return {int(m.group(1)) for f in os.listdir(PASTA_PAGINAS) if (m := re.fullmatch(r"p(\d+)\.jpg", f))}
    except FileNotFoundError:
        return set()


PAGINAS_ESTATICAS = _paginas_estaticas()


def livro_de(materia):
    """Inglês usa outro livro: as páginas dele não se misturam com as do livro principal."""
    return "ingles" if materia == "Inglês" else "principal"


def numeros_paginas(txt):
    """'112, 118-119' → [112, 118, 119]. Ignora textos entre parênteses, como '(Unit 6)'."""
    txt = re.sub(r"\([^)]*\)", "", txt or "")
    nums = []
    for a, b in re.findall(r"(\d+)(?:\s*[-–a]\s*(\d+))?", txt):
        a = int(a)
        b = int(b) if b else a
        if b < a or b - a > 40:
            b = a
        for n in range(a, b + 1):
            if n not in nums:
                nums.append(n)
    return nums


def _fotos_enviadas(livro):
    return {p for (p,) in db.session.query(PaginaFoto.pagina).filter_by(livro=livro).all()}


def paginas_de(conteudo, cache=None):
    """Fotos disponíveis das páginas de um conteúdo: [{'n': 112, 'url': ...}] e as que faltam."""
    livro = livro_de(conteudo.prova.materia)
    if cache is not None and livro in cache:
        enviadas = cache[livro]
    else:
        enviadas = _fotos_enviadas(livro)
        if cache is not None:
            cache[livro] = enviadas
    fotos, faltam = [], []
    for n in numeros_paginas(conteudo.paginas):
        if n in enviadas or (livro == "principal" and n in PAGINAS_ESTATICAS):
            fotos.append({"n": n, "url": url_for("pagina_foto", livro=livro, n=n)})
        else:
            faltam.append(n)
    return {"fotos": fotos, "faltam": faltam}


def leitura_de(conteudos):
    """Lista para a tela de leitura: um bloco por conteúdo que tem fotos."""
    cache, out = {}, []
    for c in conteudos:
        p = paginas_de(c, cache)
        if p["fotos"]:
            out.append({"id": c.id, "titulo": c.titulo, "emoji": c.emoji, "materia": c.prova.materia,
                        "paginas": c.paginas, "fotos": p["fotos"], "mundo": c.prova.mundo})
    return out


@app.get("/pagina/<livro>/<int:n>.jpg")
def pagina_foto(livro, n):
    f = PaginaFoto.query.filter_by(livro=livro, pagina=n).order_by(PaginaFoto.id.desc()).first()
    if f:
        r = send_file(io.BytesIO(f.dados), mimetype=f.mime)
    elif livro == "principal" and n in PAGINAS_ESTATICAS:
        r = send_file(os.path.join(PASTA_PAGINAS, f"p{n}.jpg"), mimetype="image/jpeg")
    else:
        abort(404)
    r.headers["Cache-Control"] = "public, max-age=86400"
    return r


def _preparar_foto(bruto):
    """Gira conforme o celular, reduz e comprime a foto (≈150 KB)."""
    try:
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(bruto))).convert("RGB")
        im.thumbnail((1100, 1500))
        out = io.BytesIO()
        im.save(out, "JPEG", quality=72, optimize=True, progressive=True)
        return out.getvalue()
    except Exception:
        return None



@app.context_processor
def contexto():
    return {"heroi_global": Heroi.query.first(), "TIPOS": TIPOS, "hoje": date.today(),
            "LOJA_POR_ID": LOJA_POR_ID}


@app.template_filter("data_br")
def data_br(d):
    if not d:
        return "sem data"
    dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
    return f"{dias[d.weekday()]}, {d.strftime('%d/%m')}"


def precisa_heroi(f):
    @wraps(f)
    def w(*a, **k):
        if not Heroi.query.first():
            return redirect(url_for("criar_heroi"))
        return f(*a, **k)
    return w


def precisa_pais(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("pais"):
            return redirect(url_for("pais_login", proximo=request.path))
        return f(*a, **k)
    return w


def estatisticas(heroi):
    concl = Missao.query.filter_by(status="concluida").all()
    return {
        "missoes": len(concl),
        "acertos": Resposta.query.filter_by(acertou=True).count(),
        "perfeitas": sum(1 for m in concl if m.total and m.acertos == m.total),
        "dominados": sum(1 for c in Conteudo.query.all() if c.estrelas >= 5),
    }


def conquistas_de(heroi):
    s = estatisticas(heroi)
    return [{"id": i, "nome": n, "emoji": e, "ok": bool(f(heroi, s))} for i, n, e, f in CONQUISTAS]


# ---------------------------------------------------------------------------
# Área da criança
# ---------------------------------------------------------------------------
@app.route("/criar-heroi", methods=["GET", "POST"])
def criar_heroi():
    heroi = Heroi.query.first()
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()[:60] or "Herói"
        if not heroi:
            heroi = Heroi(nome=nome)
            db.session.add(heroi)
        heroi.nome = nome
        heroi.avatar = request.form.get("avatar") or AVATARES[0]
        heroi.cor = request.form.get("cor") or CORES[0]
        heroi.interesses = request.form.get("interesses", "").strip()[:300]
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("criar_heroi.html", heroi=heroi, avatares=AVATARES, cores=CORES)


@app.route("/")
@precisa_heroi
def inicio():
    heroi = Heroi.query.first()
    provas = Prova.query.filter_by(ativa=True).order_by(Prova.data).all()
    hoje = date.today()
    missao = Missao.query.filter_by(data=hoje).first()
    tem_futuras = bool(missoes.provas_futuras(hoje))
    return render_template("inicio.html", heroi=heroi, provas=provas, missao=missao,
                           tem_futuras=tem_futuras, conquistas=conquistas_de(heroi), **contexto_jornada())


@app.route("/mundo/<int:prova_id>")
@precisa_heroi
def mundo(prova_id):
    prova = db.get_or_404(Prova, prova_id)
    return render_template("mundo.html", prova=prova, m=prova.mundo)


@app.route("/missao")
@precisa_heroi
def missao():
    m = missoes.gerar_missao()
    if not m:
        flash("Não há provas com data marcada. Peça para um adulto colocar as datas no Painel dos Pais.")
        return redirect(url_for("inicio"))
    return render_template("jogar.html", modo="missao", missao=m, titulo=m.titulo,
                           api=url_for("api_missao_itens"))


@app.route("/treino/<int:conteudo_id>")
@precisa_heroi
def treino(conteudo_id):
    c = db.get_or_404(Conteudo, conteudo_id)
    return render_template("jogar.html", modo="treino", missao=None, titulo=c.titulo, conteudo=c,
                           api=url_for("api_treino_itens", conteudo_id=c.id))


@app.route("/cartas/<int:prova_id>")
@precisa_heroi
def cartas(prova_id):
    prova = db.get_or_404(Prova, prova_id)
    return render_template("jogar.html", modo="cartas", missao=None, titulo=f"Cartas mágicas — {prova.materia}",
                           api=url_for("api_cartas_itens", prova_id=prova.id))


# --------------------------- Mapa da jornada --------------------------------
def plano_jornada(hoje=None):
    """Um ponto por dia, de quando a jornada começou até a última prova.

    Segue a mesma regra das missões: na véspera de uma prova a missão vira Batalha Final;
    no dia da prova, o castelo da prova aparece antes da missão do dia.
    """
    hoje = hoje or date.today()
    provas = (Prova.query.filter(Prova.ativa.is_(True), Prova.data.isnot(None))
              .order_by(Prova.data).all())
    if not provas:
        return None
    primeira = Missao.query.order_by(Missao.data).first()
    inicio = min(primeira.data if primeira else hoje, hoje, provas[-1].data)
    feitas = {m.data: m for m in Missao.query.filter(Missao.data >= inicio).all()}
    dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
    nos, d = [], inicio
    while d <= provas[-1].data:
        rotulo = {"data": d.isoformat(), "dia": d.day, "semana": dias[d.weekday()], "data_br": d.strftime("%d/%m")}
        for p in provas:
            if p.data == d:
                m = p.mundo
                nos.append({**rotulo, "tipo": "prova", "titulo": p.nome, "materia": p.materia,
                            "mundo": m["nome"], "emoji": m["emoji"], "cor": m["cor"], "cor2": m["cor2"],
                            "chefao": m["chefao"], "chefao_emoji": m["chefao_emoji"], "dominio": p.dominio,
                            "status": "feita" if d < hoje else ("hoje" if d == hoje else "futura"),
                            "url": url_for("mundo", prova_id=p.id), "conteudos": len(p.conteudos)})
        futuras = [p for p in provas if p.data > d]
        if futuras:
            alvo = futuras[0]
            m = feitas.get(d)
            batalha = (m.tipo == "batalha_final") if m else (alvo.data - d).days <= 1
            if m and m.status == "concluida":
                status = "feita"
            elif d == hoje:
                status = "hoje"
            else:
                status = "perdida" if d < hoje else "futura"
            mundo = alvo.mundo
            nos.append({**rotulo, "tipo": "batalha" if batalha else "missao", "status": status,
                        "estrelas": m.estrelas if m and m.status == "concluida" else 0,
                        "acertos": m.acertos if m else 0, "total": m.total if m else 0,
                        "alvo": alvo.nome, "alvo_data": alvo.data.strftime("%d/%m"), "faltam": (alvo.data - d).days,
                        "cor": mundo["cor"], "cor2": mundo["cor2"], "emoji_mundo": mundo["emoji"],
                        "chefao": mundo["chefao"], "chefao_emoji": mundo["chefao_emoji"]})
        d += timedelta(days=1)
    return nos


def contexto_jornada():
    """Dados do mapa da jornada para os templates (tela inicial e /jornada)."""
    heroi = Heroi.query.first()
    nos = plano_jornada() or []
    hoje = date.today().isoformat()
    # onde o herói está: a missão de hoje; se a jornada acabou, no último ponto
    pos = next((i for i, n in enumerate(nos) if n["data"] == hoje and n["tipo"] != "prova"), None)
    if pos is None:
        pos = next((i for i, n in enumerate(nos) if n["data"] == hoje), None)
    if pos is None:
        pos = len(nos) - 1 if nos and nos[-1]["data"] < hoje else 0
    missoes_ = [n for n in nos if n["tipo"] != "prova"]
    proxima = next((n for n in nos if n["tipo"] == "prova" and n["data"] >= hoje), None)
    resumo = {
        "dia": sum(1 for n in missoes_ if n["data"] <= hoje), "total": len(missoes_),
        "feitas": sum(1 for n in missoes_ if n["status"] == "feita"),
        "proxima": proxima,
        "faltam": (date.fromisoformat(proxima["data"]) - date.today()).days if proxima else None,
    }
    equip = [LOJA_POR_ID[i]["emoji"] for i in heroi.lista_equipados() if i in LOJA_POR_ID]
    return {"nos": nos, "pos": pos, "resumo": resumo, "equip": equip,
            "andou": request.args.get("andou") == "1"}


@app.route("/jornada")
@precisa_heroi
def jornada():
    return render_template("jornada.html", heroi=Heroi.query.first(), **contexto_jornada())

@app.route("/loja")
@precisa_heroi
def loja():
    return render_template("loja.html", heroi=Heroi.query.first(), loja=LOJA)


# --------------------------- API do jogo -----------------------------------
def _pacote(itens_atividade, fases=None):
    out, cache, pags = [], {}, {}
    for i, a in enumerate(itens_atividade):
        d = a.to_dict()
        d["fase"] = fases[i] if fases else 2
        d["mundo"] = mundo_de(d["materia"])
        if a.conteudo_id not in pags:
            pags[a.conteudo_id] = paginas_de(a.conteudo, cache)["fotos"]
        d["paginas"] = pags[a.conteudo_id]
        d["paginas_txt"] = a.conteudo.paginas
        d.update(imagens.visuais_para(a))
        out.append(d)
    return out


def _conteudos_em_ordem(itens_atividade):
    vistos, out = set(), []
    for a in itens_atividade:
        if a.conteudo_id not in vistos:
            vistos.add(a.conteudo_id)
            out.append(a.conteudo)
    return out


@app.get("/api/missao/hoje")
def api_missao_itens():
    m = missoes.gerar_missao()
    if not m:
        return jsonify({"erro": "sem missão"}), 404
    ids = [i["atividade_id"] for i in m.lista_itens()]
    mapa = {a.id: a for a in Atividade.query.filter(Atividade.id.in_(ids)).all()} if ids else {}
    pares = [(mapa[i["atividade_id"]], i["fase"]) for i in m.lista_itens() if i["atividade_id"] in mapa]
    pares.sort(key=lambda x: x[1])
    heroi = Heroi.query.first()
    alvo = missoes.provas_futuras(date.today())
    chefe = alvo[0].mundo if alvo else mundo_de("")
    return jsonify({
        "missao_id": m.id, "tipo": m.tipo, "status": m.status, "historia": m.historia, "titulo": m.titulo,
        "heroi": {"nome": heroi.nome, "avatar": heroi.avatar, "cor": heroi.cor,
                  "itens": [LOJA_POR_ID[i]["emoji"] for i in heroi.lista_equipados() if i in LOJA_POR_ID]},
        "chefe": {"nome": chefe["chefao"], "emoji": chefe["chefao_emoji"]},
        "itens": _pacote([p[0] for p in pares], [p[1] for p in pares]),
        "leitura": leitura_de(_conteudos_em_ordem([p[0] for p in pares])),
    })


@app.get("/api/treino/<int:conteudo_id>")
def api_treino_itens(conteudo_id):
    c = db.get_or_404(Conteudo, conteudo_id)
    ativas = c.atividades_ativas()
    random.shuffle(ativas)
    heroi = Heroi.query.first()
    return jsonify({"missao_id": None, "tipo": "treino", "historia":
                    f"Treino livre, {heroi.nome}! 🦉 Vamos fortalecer o conteúdo: {c.titulo}.",
                    "titulo": c.titulo,
                    "heroi": {"nome": heroi.nome, "avatar": heroi.avatar, "cor": heroi.cor,
                              "itens": [LOJA_POR_ID[i]["emoji"] for i in heroi.lista_equipados() if i in LOJA_POR_ID]},
                    "chefe": {"nome": c.prova.mundo["chefao"], "emoji": c.prova.mundo["chefao_emoji"]},
                    "itens": _pacote(ativas[:10]), "leitura": leitura_de([c])})


@app.get("/api/cartas/<int:prova_id>")
def api_cartas_itens(prova_id):
    prova = db.get_or_404(Prova, prova_id)
    cartas_ = [a for c in prova.conteudos for a in c.atividades_ativas() if a.tipo == "flashcard"]
    random.shuffle(cartas_)
    heroi = Heroi.query.first()
    return jsonify({"missao_id": None, "tipo": "cartas", "historia":
                    f"{heroi.nome}, vire cada carta mágica e diga a resposta em voz alta antes de olhar! 🃏",
                    "titulo": prova.materia,
                    "heroi": {"nome": heroi.nome, "avatar": heroi.avatar, "cor": heroi.cor, "itens": []},
                    "chefe": {"nome": prova.mundo["chefao"], "emoji": prova.mundo["chefao_emoji"]},
                    "itens": _pacote(cartas_[:15])})


@app.post("/api/responder")
def api_responder():
    dados = request.get_json(force=True)
    a = db.get_or_404(Atividade, int(dados["atividade_id"]))
    acertou = bool(dados.get("acertou"))
    a.vezes += 1
    a.acertos += 1 if acertou else 0
    a.ultima_vez = date.today()
    modo = dados.get("modo", "missao")
    db.session.add(Resposta(missao_id=dados.get("missao_id"), atividade_id=a.id, acertou=acertou, modo=modo))
    heroi = Heroi.query.first()
    if acertou:
        heroi.xp += 10 if modo == "missao" else 5
        heroi.moedas += 1
    db.session.commit()
    return jsonify({"ok": True, "xp": heroi.xp, "moedas": heroi.moedas})


@app.post("/api/concluir")
def api_concluir():
    dados = request.get_json(force=True)
    heroi = Heroi.query.first()
    modo = dados.get("modo", "missao")
    acertos, total = int(dados.get("acertos", 0)), int(dados.get("total", 0))
    taxa = acertos / total if total else 0
    estrelas = 3 if taxa >= 0.9 else 2 if taxa >= 0.7 else 1
    bonus_xp, bonus_moedas, nivel_antes = 0, 0, heroi.nivel
    conquistas_antes = {c["id"] for c in conquistas_de(heroi) if c["ok"]}

    if modo == "missao" and dados.get("missao_id"):
        m = db.get_or_404(Missao, int(dados["missao_id"]))
        if m.status != "concluida":
            hoje = date.today()
            # repetição espaçada por conteúdo (só primeira resposta de cada atividade)
            primeiras = {}
            for r in Resposta.query.filter_by(missao_id=m.id).order_by(Resposta.id).all():
                primeiras.setdefault(r.atividade_id, r.acertou)
            por_conteudo = {}
            for aid, ok in primeiras.items():
                a = db.session.get(Atividade, aid)
                if a:
                    t = por_conteudo.setdefault(a.conteudo_id, [0, 0])
                    t[0] += 1 if ok else 0
                    t[1] += 1
            for cid, (ac, tt) in por_conteudo.items():
                missoes.atualizar_revisao(db.session.get(Conteudo, cid), ac, tt, hoje)
            # sequência de dias
            if heroi.ultimo_dia == hoje - timedelta(days=1):
                heroi.streak += 1
            elif heroi.ultimo_dia != hoje:
                heroi.streak = 1
            heroi.ultimo_dia = hoje
            bonus_xp = 30 + estrelas * 10 + min(heroi.streak, 7) * 5
            bonus_moedas = estrelas * 5 + (10 if m.tipo == "batalha_final" else 0)
            m.status, m.acertos, m.estrelas = "concluida", acertos, estrelas
            m.xp_ganho, m.concluida_em = bonus_xp, datetime.utcnow()
    else:
        bonus_xp, bonus_moedas = 10, 2

    heroi.xp += bonus_xp
    heroi.moedas += bonus_moedas
    db.session.commit()
    novas = [c for c in conquistas_de(heroi) if c["ok"] and c["id"] not in conquistas_antes]
    return jsonify({"estrelas": estrelas, "bonus_xp": bonus_xp, "bonus_moedas": bonus_moedas,
                    "xp": heroi.xp, "moedas": heroi.moedas, "streak": heroi.streak,
                    "subiu_nivel": heroi.nivel > nivel_antes, "nivel": heroi.nivel, "titulo": heroi.titulo,
                    "conquistas": novas})


@app.post("/api/loja/<item_id>")
def api_loja(item_id):
    item = LOJA_POR_ID.get(item_id) or abort(404)
    heroi = Heroi.query.first()
    itens, equip = heroi.lista_itens(), heroi.lista_equipados()
    if item_id in itens:  # alterna equipar
        if item_id in equip:
            equip.remove(item_id)
        else:
            equip = (equip + [item_id])[-4:]
    else:
        if heroi.moedas < item["preco"]:
            return jsonify({"erro": f"Faltam {item['preco'] - heroi.moedas} moedas!"}), 400
        heroi.moedas -= item["preco"]
        itens.append(item_id)
        equip = (equip + [item_id])[-4:]
    heroi.itens, heroi.equipados = json.dumps(itens), json.dumps(equip)
    db.session.commit()
    return jsonify({"moedas": heroi.moedas, "itens": itens, "equipados": equip})


# --------------------------- Ilustrações ------------------------------------
@app.get("/ilustracao/<chave>.jpg")
def ilustracao(chave):
    from models import Imagem
    img = Imagem.query.filter_by(chave=chave, status="ok").first()
    if not img or not img.dados:
        abort(404)
    r = send_file(io.BytesIO(img.dados), mimetype=img.mime or "image/jpeg")
    r.headers["Cache-Control"] = "public, max-age=604800"
    return r


@app.post("/pais/imagens/gerar")
@precisa_pais
def pais_imagens_gerar():
    if request.form.get("refazer_falhas"):
        imagens.refazer_falhas()
    if request.form.get("tentar_gemini"):
        Config.set("imagens_gemini_bloqueado", "")
        db.session.commit()
    imagens.registrar_todas()
    if imagens.iniciar(app):
        flash("Gerando as imagens em segundo plano. Pode continuar usando o app; o progresso aparece aqui.")
    else:
        flash("A geração de imagens já está em andamento.")
    return redirect(url_for("pais") + "#imagens")


@app.get("/pais/imagens/situacao")
@precisa_pais
def pais_imagens_situacao():
    return jsonify(imagens.situacao())


# ---------------------------------------------------------------------------
# Painel dos pais
# ---------------------------------------------------------------------------
@app.route("/pais/login", methods=["GET", "POST"])
def pais_login():
    if request.method == "POST":
        if request.form.get("pin") == os.environ.get("PARENT_PIN", "1234"):
            session["pais"] = True
            return redirect(request.args.get("proximo") or url_for("pais"))
        flash("PIN incorreto.")
    return render_template("pais/login.html")


@app.route("/pais/sair")
def pais_sair():
    session.pop("pais", None)
    return redirect(url_for("inicio"))


@app.route("/pais")
@precisa_pais
def pais():
    provas = Prova.query.order_by(Prova.data).all()
    ultimas = Missao.query.order_by(Missao.data.desc()).limit(14).all()
    return render_template("pais/painel.html", provas=provas, ultimas=ultimas, plano=missoes.plano_de_revisao,
                           gemini_ok=gemini.disponivel(), modelo=gemini.modelo(),
                           tamanho=missoes.tamanho_missao(), heroi=Heroi.query.first(),
                           provisorias=Config.get("datas_provisorias") == "1", materias=list(MUNDOS.keys()),
                           img=imagens.situacao())


@app.post("/pais/config")
@precisa_pais
def pais_config():
    Config.set("atividades_por_missao", request.form.get("atividades_por_missao", 12))
    Config.set("historia_gemini", "1" if request.form.get("historia_gemini") else "0")
    heroi = Heroi.query.first()
    if heroi:
        heroi.interesses = request.form.get("interesses", heroi.interesses)[:300]
    db.session.commit()
    flash("Configurações salvas.")
    return redirect(url_for("pais"))


@app.post("/pais/prova")
@precisa_pais
def pais_prova_salvar():
    pid = request.form.get("id")
    prova = db.session.get(Prova, int(pid)) if pid else Prova()
    prova.materia = request.form.get("materia", "").strip() or "Outra"
    prova.titulo = request.form.get("titulo", "").strip() or f"Prova de {prova.materia}"
    dt = request.form.get("data")
    prova.data = date.fromisoformat(dt) if dt else None
    prova.ativa = bool(request.form.get("ativa", "1"))
    if not pid:
        db.session.add(prova)
    Config.set("datas_provisorias", "0")
    db.session.commit()
    _refazer_missao_de_hoje()
    flash("Prova salva. A missão de hoje foi recalculada.")
    return redirect(url_for("pais"))


@app.post("/pais/datas")
@precisa_pais
def pais_datas():
    for prova in Prova.query.all():
        v = request.form.get(f"data_{prova.id}")
        if v is not None:
            prova.data = date.fromisoformat(v) if v else None
        prova.ativa = bool(request.form.get(f"ativa_{prova.id}"))
    Config.set("datas_provisorias", "0")
    db.session.commit()
    _refazer_missao_de_hoje()
    flash("Datas atualizadas. As missões passam a seguir o novo calendário.")
    return redirect(url_for("pais"))


@app.post("/pais/prova/<int:prova_id>/excluir")
@precisa_pais
def pais_prova_excluir(prova_id):
    db.session.delete(db.get_or_404(Prova, prova_id))
    db.session.commit()
    _refazer_missao_de_hoje()
    return redirect(url_for("pais"))


def _refazer_missao_de_hoje():
    m = Missao.query.filter_by(data=date.today()).first()
    if m and m.status != "concluida":
        Resposta.query.filter_by(missao_id=m.id).delete()
        db.session.delete(m)
        db.session.commit()


@app.post("/pais/missao/refazer")
@precisa_pais
def pais_missao_refazer():
    _refazer_missao_de_hoje()
    flash("A missão de hoje será gerada de novo quando o herói entrar.")
    return redirect(url_for("pais"))


@app.route("/pais/conteudo/<int:conteudo_id>", methods=["GET", "POST"])
@precisa_pais
def pais_conteudo(conteudo_id):
    c = db.get_or_404(Conteudo, conteudo_id)
    if request.method == "POST":
        c.titulo = request.form.get("titulo", c.titulo)[:160]
        c.emoji = request.form.get("emoji", c.emoji)[:8]
        c.paginas = request.form.get("paginas", c.paginas)[:60]
        c.resumo = request.form.get("resumo", c.resumo)
        db.session.commit()
        flash("Conteúdo atualizado.")
        return redirect(url_for("pais_conteudo", conteudo_id=c.id))
    livro = livro_de(c.prova.materia)
    enviadas = _fotos_enviadas(livro)
    return render_template("pais/conteudo.html", c=c, gemini_ok=gemini.disponivel(),
                           exemplos=EXEMPLOS_JSON, pags=paginas_de(c), livro=livro, enviadas=enviadas)


@app.post("/pais/conteudo/novo")
@precisa_pais
def pais_conteudo_novo():
    prova = db.get_or_404(Prova, int(request.form["prova_id"]))
    fotos = [(f.read(), f.mimetype) for f in request.files.getlist("fotos") if f and f.filename]
    titulo = request.form.get("titulo", "").strip()
    resumo = request.form.get("resumo", "").strip()
    c = Conteudo(prova=prova, titulo=titulo or "Novo conteúdo", resumo=resumo,
                 paginas=request.form.get("paginas", ""), ordem=len(prova.conteudos))
    db.session.add(c)
    if fotos or (resumo and request.form.get("gerar")):
        if not gemini.disponivel():
            flash("Conteúdo criado, mas o Gemini não está configurado (GEMINI_API_KEY).")
        else:
            try:
                qtd = int(request.form.get("quantidade", 10))
                if fotos:
                    r = gemini.extrair_de_fotos(prova.materia, fotos, Heroi.query.first(), qtd)
                    c.titulo = titulo or r["titulo"]
                    c.emoji = r["emoji"]
                    c.resumo = (resumo + "\n\n" if resumo else "") + r["resumo"]
                    novas = r["atividades"]
                else:
                    novas = gemini.gerar_atividades(prova.materia, c.titulo, resumo, list(TIPOS.keys()), qtd,
                                                    Heroi.query.first())
                for v in novas:
                    db.session.add(Atividade(conteudo=c, tipo=v["tipo"], origem="gemini",
                                             dados=json.dumps(v["dados"], ensure_ascii=False)))
                flash(f"Conteúdo criado com {len(novas)} atividades geradas pelo Gemini.")
            except gemini.GeminiErro as e:
                flash(f"Conteúdo criado, mas o Gemini falhou: {e}")
    db.session.commit()
    return redirect(url_for("pais_conteudo", conteudo_id=c.id))


@app.post("/pais/conteudo/<int:conteudo_id>/excluir")
@precisa_pais
def pais_conteudo_excluir(conteudo_id):
    db.session.delete(db.get_or_404(Conteudo, conteudo_id))
    db.session.commit()
    return redirect(url_for("pais"))


@app.post("/pais/conteudo/<int:conteudo_id>/gerar")
@precisa_pais
def pais_gerar(conteudo_id):
    c = db.get_or_404(Conteudo, conteudo_id)
    tipos = request.form.getlist("tipos") or list(TIPOS.keys())
    qtd = max(1, min(25, int(request.form.get("quantidade", 8))))
    fotos = [(f.read(), f.mimetype) for f in request.files.getlist("fotos") if f and f.filename]
    try:
        novas = gemini.gerar_atividades(c.prova.materia, c.titulo, c.resumo, tipos, qtd,
                                        Heroi.query.first(), fotos)
        for v in novas:
            db.session.add(Atividade(conteudo=c, tipo=v["tipo"], origem="gemini",
                                     dados=json.dumps(v["dados"], ensure_ascii=False)))
        db.session.commit()
        flash(f"{len(novas)} novas atividades criadas pelo Gemini. Confira e desative as que não gostar.")
    except gemini.GeminiErro as e:
        flash(str(e))
    return redirect(url_for("pais_conteudo", conteudo_id=c.id))


@app.post("/pais/conteudo/<int:conteudo_id>/paginas")
@precisa_pais
def pais_paginas(conteudo_id):
    """Envia fotos de páginas do livro. Os números vão na mesma ordem das fotos."""
    c = db.get_or_404(Conteudo, conteudo_id)
    livro = livro_de(c.prova.materia)
    arquivos = [f for f in request.files.getlist("fotos") if f and f.filename]
    numeros = numeros_paginas(request.form.get("numeros", ""))
    if not arquivos:
        flash("Escolha pelo menos uma foto.")
        return redirect(url_for("pais_conteudo", conteudo_id=c.id) + "#paginas")
    if len(numeros) != len(arquivos):
        flash(f"Você enviou {len(arquivos)} foto(s) e {len(numeros)} número(s) de página. Informe um número para cada foto, na mesma ordem.")
        return redirect(url_for("pais_conteudo", conteudo_id=c.id) + "#paginas")
    ok = 0
    for f, n in zip(arquivos, numeros):
        dados = _preparar_foto(f.read())
        if not dados:
            continue
        PaginaFoto.query.filter_by(livro=livro, pagina=n).delete()
        db.session.add(PaginaFoto(livro=livro, pagina=n, dados=dados))
        ok += 1
    # garante que as páginas enviadas façam parte do conteúdo
    atuais = numeros_paginas(c.paginas)
    novas = [n for n in numeros if n not in atuais]
    if novas:
        c.paginas = ((c.paginas + ", ") if c.paginas else "") + ", ".join(map(str, novas))
        c.paginas = c.paginas[:60]
    db.session.commit()
    flash(f"{ok} página(s) salvas. Elas já aparecem no Aquecimento do Herói.")
    return redirect(url_for("pais_conteudo", conteudo_id=c.id) + "#paginas")


@app.post("/pais/pagina/<livro>/<int:n>/excluir")
@precisa_pais
def pais_pagina_excluir(livro, n):
    PaginaFoto.query.filter_by(livro=livro, pagina=n).delete()
    db.session.commit()
    flash(f"Foto enviada da página {n} removida." + (" A foto original do app continua." if livro == "principal" and n in PAGINAS_ESTATICAS else ""))
    return redirect(request.form.get("voltar") or url_for("pais"))


@app.post("/pais/conteudo/<int:conteudo_id>/manual")
@precisa_pais
def pais_manual(conteudo_id):
    c = db.get_or_404(Conteudo, conteudo_id)
    tipo = request.form.get("tipo")
    try:
        dados = json.loads(request.form.get("dados", "{}"))
    except json.JSONDecodeError:
        flash("JSON inválido. Confira as aspas e vírgulas.")
        return redirect(url_for("pais_conteudo", conteudo_id=c.id))
    v = gemini.validar(tipo, dados)
    if not v:
        flash("A atividade não está no formato esperado para esse tipo.")
    else:
        db.session.add(Atividade(conteudo=c, tipo=tipo, origem="manual",
                                 dados=json.dumps(v["dados"], ensure_ascii=False)))
        db.session.commit()
        flash("Atividade adicionada.")
    return redirect(url_for("pais_conteudo", conteudo_id=c.id))


@app.post("/pais/atividade/<int:aid>/alternar")
@precisa_pais
def pais_atividade_alternar(aid):
    a = db.get_or_404(Atividade, aid)
    a.ativa = not a.ativa
    db.session.commit()
    return redirect(url_for("pais_conteudo", conteudo_id=a.conteudo_id) + f"#a{a.id}")


@app.post("/pais/atividade/<int:aid>/excluir")
@precisa_pais
def pais_atividade_excluir(aid):
    a = db.get_or_404(Atividade, aid)
    cid = a.conteudo_id
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for("pais_conteudo", conteudo_id=cid))


@app.route("/pais/previa/<int:aid>")
@precisa_pais
def pais_previa(aid):
    a = db.get_or_404(Atividade, aid)
    return render_template("jogar.html", modo="previa", missao=None, titulo="Prévia",
                           api=url_for("api_previa", aid=a.id))


@app.get("/api/previa/<int:aid>")
@precisa_pais
def api_previa(aid):
    a = db.get_or_404(Atividade, aid)
    heroi = Heroi.query.first()
    return jsonify({"missao_id": None, "tipo": "previa", "historia": "Prévia da atividade.", "titulo": "Prévia",
                    "heroi": {"nome": heroi.nome if heroi else "Herói", "avatar": heroi.avatar if heroi else "🦸‍♂️",
                              "cor": "#ff8a3d", "itens": []},
                    "chefe": {"nome": "Chefão", "emoji": "👾"}, "itens": _pacote([a])})


@app.post("/pais/resetar-tudo")
@precisa_pais
def pais_resetar_tudo():
    """Começa a jornada do zero: apaga o herói, missões, respostas, domínio, XP, moedas e itens.
    Mantém as provas, os conteúdos e as atividades."""
    Resposta.query.delete()
    Missao.query.delete()
    Heroi.query.delete()
    for c in Conteudo.query.all():
        c.caixa, c.proxima_revisao, c.ultima_revisao, c.acertos, c.erros = 0, None, None, 0, 0
    for a in Atividade.query.all():
        a.vezes, a.acertos, a.ultima_vez = 0, 0, None
    db.session.commit()
    session.pop("pais", None)
    flash("Jornada resetada. Crie um novo herói para começar do zero!")
    return redirect(url_for("criar_heroi"))


EXEMPLOS_JSON = {
    "quiz": {"pergunta": "Quantas faces tem o cubo?", "opcoes": ["6", "4", "8"], "correta": 0, "explicacao": "", "emoji": "🎲"},
    "vf": {"afirmacao": "O cone é um corpo redondo.", "resposta": True, "explicacao": "", "emoji": "🍦"},
    "completar": {"frase": "1 metro tem ___ centímetros.", "opcoes": ["100", "10", "1000"], "correta": 0, "explicacao": ""},
    "contas": {"pergunta": "Qual é o dobro de 7?", "resposta": 14, "unidade": "", "explicacao": "2 × 7 = 14", "emoji": "✌️"},
    "ligar": {"titulo": "Ligue", "pares": [["Gelo", "Sólido"], ["Vapor", "Gasoso"], ["Chuva", "Líquido"]]},
    "memoria": {"titulo": "Memória", "pares": [["🐶", "AU-AU"], ["🐱", "MIAU"], ["🐦", "PIU-PIU"]]},
    "ordenar": {"titulo": "Ordene", "itens": ["Evaporação", "Condensação", "Precipitação"], "explicacao": ""},
    "categorizar": {"titulo": "Separe", "categorias": ["Público", "Privado"],
                    "itens": [{"texto": "Praça", "categoria": "Público"}, {"texto": "Clube", "categoria": "Privado"},
                              {"texto": "Parque", "categoria": "Público"}]},
    "flashcard": {"frente": "O que é perímetro?", "verso": "A medida do contorno de uma figura.", "emoji": "🔲"},
}


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
