"""Backup do progresso do herói (JSON) e restauração.

Guarda: herói (XP, moedas, sequência, itens), missões e respostas, domínio e revisões de cada conteúdo,
estatísticas das atividades, provas (datas), conteúdos e atividades criados no app, e configurações.
Não guarda fotos de páginas nem ilustrações (podem ser enviadas/geradas de novo).

As atividades são identificadas por uma "chave" (tipo + dados), e os conteúdos pelo título,
para o backup funcionar mesmo num banco novo, em que os números (ids) mudam.
"""
import hashlib
import json
from datetime import date, datetime

import relogio
from models import Atividade, Config, Conteudo, Heroi, Missao, Prova, Resposta, db

VERSAO = 1
CONFIGS = ["atividades_por_missao", "historia_gemini"]


def chave(tipo, dados):
    return hashlib.sha1(f"{tipo}|{dados}".encode("utf-8")).hexdigest()[:16]


def _d(v):
    return v.isoformat() if isinstance(v, (date, datetime)) else v


def _data(v):
    return date.fromisoformat(v) if v else None


def _dt(v):
    return datetime.fromisoformat(v) if v else None


def exportar():
    h = Heroi.query.first()
    if not h:
        return None
    ativ = {a.id: a for a in Atividade.query.all()}
    k = {i: chave(a.tipo, a.dados) for i, a in ativ.items()}
    missoes = Missao.query.order_by(Missao.data).all()
    data_da_missao = {m.id: m.data.isoformat() for m in missoes}
    return {
        "app": "jornada-do-heroi", "versao": VERSAO, "gerado_em": relogio.agora().isoformat(timespec="seconds"),
        "heroi": {"nome": h.nome, "avatar": h.avatar, "cor": h.cor, "interesses": h.interesses, "xp": h.xp,
                  "moedas": h.moedas, "streak": h.streak, "ultimo_dia": _d(h.ultimo_dia), "itens": h.itens,
                  "equipados": h.equipados, "criado_em": _d(h.criado_em)},
        "provas": [{"titulo": p.titulo, "materia": p.materia, "data": _d(p.data), "ativa": p.ativa}
                   for p in Prova.query.all()],
        "conteudos": [{"prova": c.prova.titulo, "titulo": c.titulo, "resumo": c.resumo, "paginas": c.paginas,
                       "emoji": c.emoji, "ordem": c.ordem, "caixa": c.caixa,
                       "proxima_revisao": _d(c.proxima_revisao), "ultima_revisao": _d(c.ultima_revisao),
                       "acertos": c.acertos, "erros": c.erros} for c in Conteudo.query.all()],
        "atividades": [{"conteudo": a.conteudo.titulo, "chave": k[a.id], "tipo": a.tipo, "origem": a.origem,
                        "ativa": a.ativa, "vezes": a.vezes, "acertos": a.acertos, "ultima_vez": _d(a.ultima_vez),
                        # o texto completo só das que não vêm do livro (as do livro são recriadas pelo app)
                        **({"dados": a.dados} if a.origem != "livro" else {})} for a in ativ.values()],
        "missoes": [{"data": m.data.isoformat(), "tipo": m.tipo, "titulo": m.titulo, "historia": m.historia,
                     "itens": [{"chave": k.get(i["atividade_id"]), "fase": i["fase"]} for i in m.lista_itens()
                               if i["atividade_id"] in k],
                     "status": m.status, "acertos": m.acertos, "total": m.total, "estrelas": m.estrelas,
                     "xp_ganho": m.xp_ganho, "concluida_em": _d(m.concluida_em)} for m in missoes],
        "respostas": [[data_da_missao.get(r.missao_id), k.get(r.atividade_id), bool(r.acertou), r.modo,
                       _d(r.criado_em)] for r in Resposta.query.order_by(Resposta.id).all() if r.atividade_id in k],
        "config": {c: Config.get(c) for c in CONFIGS if Config.get(c) is not None},
    }


def resumo(b):
    """Texto curto para mostrar antes de restaurar."""
    h = b.get("heroi", {})
    feitas = sum(1 for m in b.get("missoes", []) if m.get("status") == "concluida")
    return {"nome": h.get("nome"), "xp": h.get("xp", 0), "moedas": h.get("moedas", 0), "streak": h.get("streak", 0),
            "missoes": feitas, "gerado_em": b.get("gerado_em")}


def validar(b):
    return isinstance(b, dict) and b.get("app") == "jornada-do-heroi" and isinstance(b.get("heroi"), dict)


def restaurar(b):
    """Substitui o progresso atual pelo do backup. Provas, conteúdos e atividades que faltarem são criados."""
    if not validar(b):
        raise ValueError("Arquivo de backup inválido.")
    # ---- provas e conteúdos (cria os que não existem; ajusta datas e revisões)
    provas = {p.titulo: p for p in Prova.query.all()}
    for pb in b.get("provas", []):
        p = provas.get(pb["titulo"])
        if not p:
            p = Prova(titulo=pb["titulo"], materia=pb["materia"])
            db.session.add(p)
            provas[p.titulo] = p
        p.data, p.ativa = _data(pb.get("data")), pb.get("ativa", True)
    db.session.flush()
    conteudos = {c.titulo: c for c in Conteudo.query.all()}
    for cb in b.get("conteudos", []):
        c = conteudos.get(cb["titulo"])
        if not c:
            prova = provas.get(cb["prova"])
            if not prova:
                continue
            c = Conteudo(prova=prova, titulo=cb["titulo"], resumo=cb.get("resumo", ""), paginas=cb.get("paginas", ""),
                         emoji=cb.get("emoji", "📘"), ordem=cb.get("ordem", 0))
            db.session.add(c)
            conteudos[c.titulo] = c
        c.caixa, c.acertos, c.erros = cb.get("caixa", 0), cb.get("acertos", 0), cb.get("erros", 0)
        c.proxima_revisao, c.ultima_revisao = _data(cb.get("proxima_revisao")), _data(cb.get("ultima_revisao"))
    db.session.flush()
    # ---- atividades: recria as que não são do livro e devolve as estatísticas
    por_chave = {chave(a.tipo, a.dados): a for a in Atividade.query.all()}
    for ab in b.get("atividades", []):
        a = por_chave.get(ab["chave"])
        if not a and ab.get("dados") and ab.get("conteudo") in conteudos:
            a = Atividade(conteudo=conteudos[ab["conteudo"]], tipo=ab["tipo"], dados=ab["dados"],
                          origem=ab.get("origem", "manual"))
            db.session.add(a)
            por_chave[ab["chave"]] = a
        if a:
            a.ativa = ab.get("ativa", True)
            a.vezes, a.acertos, a.ultima_vez = ab.get("vezes", 0), ab.get("acertos", 0), _data(ab.get("ultima_vez"))
    db.session.flush()
    ids = {k: a.id for k, a in por_chave.items()}
    # ---- missões e respostas (substitui tudo)
    Resposta.query.delete()
    Missao.query.delete()
    db.session.flush()
    por_data = {}
    for mb in b.get("missoes", []):
        itens = [{"atividade_id": ids[i["chave"]], "fase": i["fase"]} for i in mb.get("itens", []) if i.get("chave") in ids]
        m = Missao(data=_data(mb["data"]), tipo=mb.get("tipo", "diaria"), titulo=mb.get("titulo", ""),
                   historia=mb.get("historia", ""), itens=json.dumps(itens), status=mb.get("status", "nova"),
                   acertos=mb.get("acertos", 0), total=mb.get("total", 0), estrelas=mb.get("estrelas", 0),
                   xp_ganho=mb.get("xp_ganho", 0), concluida_em=_dt(mb.get("concluida_em")))
        db.session.add(m)
        por_data[mb["data"]] = m
    db.session.flush()
    for dia, k, ok, modo, quando in b.get("respostas", []):
        if k in ids:
            m = por_data.get(dia)
            db.session.add(Resposta(missao_id=m.id if m else None, atividade_id=ids[k], acertou=bool(ok),
                                    modo=modo or "missao", criado_em=_dt(quando) or datetime.utcnow()))
    # ---- herói
    hb = b["heroi"]
    h = Heroi.query.first() or Heroi(nome=hb.get("nome") or "Herói")
    db.session.add(h)
    for campo in ("nome", "avatar", "cor", "interesses", "xp", "moedas", "streak", "itens", "equipados"):
        if campo in hb and hb[campo] is not None:
            setattr(h, campo, hb[campo])
    h.ultimo_dia = _data(hb.get("ultimo_dia"))
    for c, v in b.get("config", {}).items():
        if c in CONFIGS:
            Config.set(c, v)
    db.session.commit()
    return resumo(b)
