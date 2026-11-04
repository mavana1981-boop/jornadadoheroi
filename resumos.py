"""Resumo do Herói: versão curtinha e visual de cada conteúdo, lida no Aquecimento.

- O Gemini escreve o resumo uma vez (em segundo plano) e ele fica guardado no banco.
- Se o resumo do conteúdo for editado no Painel dos Pais, o Resumo do Herói é refeito.
- Enquanto o Gemini não escreveu (ou se ele estiver desligado), o app mostra uma versão automática,
  feita com as frases do próprio resumo do conteúdo.
"""
import hashlib
import json
import re
import threading

import gemini
from models import Conteudo, Heroi, ResumoHeroi, db

_estado = {"rodando": False}
_EMOJIS = ["⭐", "💡", "📌", "🔎", "✨", "🧠"]


def assinatura(c):
    return hashlib.sha1(f"{c.titulo}\n{c.resumo}".encode("utf-8")).hexdigest()[:16]


def automatico(c):
    """Versão sem IA: as primeiras frases do resumo do conteúdo, uma por tópico."""
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", c.resumo or "") if len(f.strip()) > 3]
    topicos = [{"emoji": _EMOJIS[i % len(_EMOJIS)], "texto": f[:240]} for i, f in enumerate(frases[:5])]
    return {"topicos": topicos, "lembre": "", "automatico": True}


def obter(c):
    r = ResumoHeroi.query.filter_by(conteudo_id=c.id).first()
    if r and r.base == assinatura(c):
        try:
            return json.loads(r.dados)
        except ValueError:
            pass
    return automatico(c)


def faltando(conteudos):
    prontos = {r.conteudo_id: r.base for r in
               ResumoHeroi.query.filter(ResumoHeroi.conteudo_id.in_([c.id for c in conteudos])).all()}
    return [c.id for c in conteudos if prontos.get(c.id) != assinatura(c) and (c.resumo or "").strip()]


def gerar(c):
    """Pede o resumo ao Gemini e guarda. Devolve o resumo ou None."""
    novo = gemini.resumo_para_crianca(c.prova.materia, c.titulo, c.resumo, Heroi.query.first())
    if not novo:
        return None
    r = ResumoHeroi.query.filter_by(conteudo_id=c.id).first() or ResumoHeroi(conteudo_id=c.id)
    r.dados, r.base = json.dumps(novo, ensure_ascii=False), assinatura(c)
    db.session.add(r)
    db.session.commit()
    return novo


def _laco(app, ids):
    with app.app_context():
        try:
            for cid in ids:
                c = db.session.get(Conteudo, cid)
                if not c:
                    continue
                try:
                    gerar(c)
                except Exception:  # noqa: BLE001 — um erro não para os outros resumos
                    db.session.rollback()
        finally:
            _estado["rodando"] = False
            db.session.remove()


def gerar_em_segundo_plano(app, conteudos=None):
    """Escreve os resumos que faltam sem travar a tela. Só roda com o Gemini configurado."""
    if _estado["rodando"] or not gemini.disponivel():
        return False
    conteudos = conteudos if conteudos is not None else Conteudo.query.all()
    ids = faltando(conteudos)
    if not ids:
        return False
    _estado["rodando"] = True
    threading.Thread(target=_laco, args=(app, ids), daemon=True).start()
    return True
