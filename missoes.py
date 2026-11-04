"""Motor das missões diárias.

Regras:
- Considera só provas ativas com data de hoje em diante.
- Escolhe conteúdos por urgência: novos e atrasados primeiro, provas mais próximas pesam mais,
  conteúdos com baixo domínio voltam mais vezes, e alterna matérias (não repete o do dia anterior).
- Cada missão tem 3 fases: Aquecimento (cartas e verdade/mentira), Desafio (jogos variados)
  e Chefão (perguntas da prova mais próxima).
- Na véspera e no dia da prova: Batalha Final só com o conteúdo daquela prova.
- Repetição espaçada (caixas de Leitner), sempre trazendo a revisão para antes da prova.
"""
import json
import random
from datetime import date, timedelta

import gemini
from models import db, Atividade, Config, Conteudo, Heroi, Missao, Prova, Resposta

INTERVALOS = {0: 1, 1: 1, 2: 2, 3: 3, 4: 5, 5: 7}
TIPOS_AQUECIMENTO = ("flashcard", "vf")
TIPOS_DESAFIO = ("ligar", "memoria", "categorizar", "ordenar", "completar", "quiz")
TIPOS_CHEFAO = ("quiz", "contas", "completar", "vf")


def tamanho_missao():
    try:
        return max(6, min(30, int(Config.get("atividades_por_missao", 12))))
    except ValueError:
        return 12


def provas_futuras(dia):
    """Provas depois de hoje. No dia de uma prova, a missão já prepara a próxima."""
    return (Prova.query.filter(Prova.ativa.is_(True), Prova.data.isnot(None), Prova.data > dia)
            .order_by(Prova.data).all())


def _pontuacao(conteudo, dia, usados_ontem):
    prova = conteudo.prova
    dias = max((prova.data - dia).days, 0)
    p = 0.0
    if conteudo.proxima_revisao is None:
        p += 6                                   # nunca visto
    else:
        atraso = (dia - conteudo.proxima_revisao).days
        p += 4 + atraso if atraso >= 0 else -3   # vencido x ainda não é hora
    p += 10 / (dias + 1)                         # prova perto pesa mais
    p += (5 - conteudo.caixa) * 0.8              # pouco domínio pesa mais
    if conteudo.id in usados_ontem:
        p -= 4                                   # alterna
    return p + random.random()


def _escolher_atividades(conteudo, tipos, n, ja):
    ativas = [a for a in conteudo.atividades_ativas() if a.id not in ja]
    preferidas = [a for a in ativas if a.tipo in tipos] or ativas
    # menos vistas e mais erradas primeiro, misturando os tipos
    preferidas.sort(key=lambda a: (a.ultima_vez or date(2000, 1, 1), a.vezes, random.random()))
    escolhidas, tipos_usados = [], set()
    for a in preferidas:
        if len(escolhidas) >= n:
            break
        if a.tipo in tipos_usados and len(tipos_usados) < len({x.tipo for x in preferidas}):
            continue
        escolhidas.append(a)
        tipos_usados.add(a.tipo)
    for a in preferidas:  # completa se faltou
        if len(escolhidas) >= n:
            break
        if a not in escolhidas:
            escolhidas.append(a)
    return escolhidas


def _usados_ontem(dia):
    m = Missao.query.filter_by(data=dia - timedelta(days=1)).first()
    if not m:
        return set()
    ids = [i["atividade_id"] for i in m.lista_itens()]
    return {a.conteudo_id for a in Atividade.query.filter(Atividade.id.in_(ids)).all()} if ids else set()


def gerar_missao(dia=None, forcar=False):
    dia = dia or date.today()
    existente = Missao.query.filter_by(data=dia).first()
    if existente and not forcar:
        return existente
    if existente and forcar:
        Resposta.query.filter_by(missao_id=existente.id).delete()
        db.session.delete(existente)
        db.session.flush()

    provas = provas_futuras(dia)
    if not provas:
        return None
    total = tamanho_missao()
    heroi = Heroi.query.first()
    proxima = provas[0]
    itens, ja = [], set()

    # ---------------- Batalha final (véspera ou dia da prova) ----------------
    if (proxima.data - dia).days <= 1 and proxima.conteudos:
        conteudos = sorted(proxima.conteudos, key=lambda c: (c.caixa, random.random()))
        alvo_total = total + 4
        # rodadas: 1 atividade de cada conteúdo por vez (os mais fracos primeiro) até encher
        while len(itens) < alvo_total:
            antes = len(itens)
            for c in conteudos:
                if len(itens) >= alvo_total:
                    break
                sel = _escolher_atividades(c, TIPOS_CHEFAO + TIPOS_DESAFIO, 1, ja)
                if sel:
                    ja.add(sel[0].id)
                    itens.append({"atividade_id": sel[0].id, "fase": 3})
            if len(itens) == antes:
                break
        random.shuffle(itens)
        tipo = "batalha_final"
        titulo = f"Batalha Final: {proxima.mundo['chefao']}"
        nomes_conteudos = [c.titulo for c in conteudos]
        mundos = [proxima.mundo["nome"]]
    else:
        # ---------------- Missão diária: 3 fases ----------------
        usados = _usados_ontem(dia)
        candidatos = [c for p in provas for c in p.conteudos if c.atividades_ativas()]
        candidatos.sort(key=lambda c: _pontuacao(c, dia, usados), reverse=True)
        escolhidos, materias = [], {}
        for c in candidatos:              # variedade: no máximo 2 conteúdos por matéria
            m = c.prova.materia
            if materias.get(m, 0) >= 2:
                continue
            escolhidos.append(c)
            materias[m] = materias.get(m, 0) + 1
            if len(escolhidos) == 3:
                break
        if not escolhidos:
            return None

        n_aq = max(2, total // 4)
        n_des = max(3, total // 2)
        n_chefe = max(2, total - n_aq - n_des)
        # fase 1 e 2: conteúdos escolhidos
        for fase, n, tipos in ((1, n_aq, TIPOS_AQUECIMENTO), (2, n_des, TIPOS_DESAFIO)):
            for i in range(n):
                c = escolhidos[i % len(escolhidos)]
                sel = _escolher_atividades(c, tipos, 1, ja)
                if sel:
                    ja.add(sel[0].id)
                    itens.append({"atividade_id": sel[0].id, "fase": fase})
        # fase 3: chefão da prova mais próxima (mistura conteúdos dela)
        alvo = sorted(proxima.conteudos, key=lambda c: (c.caixa, random.random()))
        for i in range(n_chefe):
            if not alvo:
                break
            c = alvo[i % len(alvo)]
            sel = _escolher_atividades(c, TIPOS_CHEFAO, 1, ja)
            if sel:
                ja.add(sel[0].id)
                itens.append({"atividade_id": sel[0].id, "fase": 3})
        tipo = "diaria"
        titulo = " • ".join(dict.fromkeys(c.prova.mundo["nome"] for c in escolhidos))
        nomes_conteudos = [c.titulo for c in escolhidos]
        mundos = list(dict.fromkeys(c.prova.mundo["nome"] for c in escolhidos))

    historia = _historia(heroi, mundos, nomes_conteudos, tipo, (proxima.data - dia).days)
    missao = Missao(data=dia, tipo=tipo, titulo=titulo, historia=historia,
                    itens=json.dumps(itens), total=len(itens))
    db.session.add(missao)
    db.session.commit()
    return missao


def _historia(heroi, mundos, conteudos, tipo, dias):
    nome = heroi.nome if heroi else "Herói"
    if heroi and gemini.disponivel() and Config.get("historia_gemini", "1") == "1":
        try:
            return gemini.historia_da_missao(heroi, mundos, conteudos, tipo, dias)
        except Exception:
            pass
    if tipo == "batalha_final":
        return (f"{nome}, chegou a hora! 🦉 O chefão do {mundos[0]} apareceu. "
                f"Use tudo o que você treinou nesses dias. Eu acredito em você! ⚔️")
    falta = f"Faltam {dias} dias para a próxima prova." if dias > 1 else "A prova está chegando!"
    return (f"Olá, {nome}! 🦉 Hoje a sua jornada passa por: {', '.join(mundos)}. "
            f"{falta} Cada resposta certa enfraquece o Monstro do Esquecimento. Vamos nessa? 🗺️✨")


def atualizar_revisao(conteudo, acertos, total, dia=None):
    """Leitner: ≥80% sobe uma caixa; 50-79% mantém; <50% volta para a caixa 1."""
    dia = dia or date.today()
    if total == 0:
        return
    taxa = acertos / total
    if taxa >= 0.8:
        conteudo.caixa = min(5, conteudo.caixa + 1)
    elif taxa < 0.5:
        conteudo.caixa = 1
    else:
        conteudo.caixa = max(1, conteudo.caixa)
    intervalo = INTERVALOS[conteudo.caixa]
    proxima = dia + timedelta(days=intervalo)
    prova = conteudo.prova
    if prova.data and prova.data > dia:
        limite = prova.data - timedelta(days=1)   # sempre revisar antes da prova
        if proxima > limite:
            proxima = max(dia + timedelta(days=1), limite)
    conteudo.proxima_revisao = proxima
    conteudo.ultima_revisao = dia
    conteudo.acertos += acertos
    conteudo.erros += total - acertos


def plano_de_revisao(prova, dia=None):
    """Lista conteúdos com status, para o painel dos pais."""
    dia = dia or date.today()
    linhas = []
    for c in prova.conteudos:
        if c.proxima_revisao is None:
            status = "novo"
        elif c.proxima_revisao <= dia:
            status = "para hoje"
        else:
            status = f"em {(c.proxima_revisao - dia).days} dia(s)"
        linhas.append({"c": c, "status": status})
    return linhas


def assuntos(missao):
    """Conteúdos cobrados numa missão, na ordem em que aparecem.

    Cada item: {id, titulo, emoji, materia, prova, mundo_emoji, paginas, fases}
    (fases: 1 = primeiros golpes, 2 = desafio, 3 = chefão/batalha).
    """
    if not missao:
        return []
    itens = missao.lista_itens()
    ids = [i["atividade_id"] for i in itens]
    if not ids:
        return []
    ativ = {a.id: a for a in Atividade.query.filter(Atividade.id.in_(ids)).all()}
    out = {}
    for i in sorted(itens, key=lambda x: x["fase"]):
        a = ativ.get(i["atividade_id"])
        if not a:
            continue
        c = a.conteudo
        if c.id not in out:
            out[c.id] = {"id": c.id, "titulo": c.titulo, "emoji": c.emoji, "materia": c.prova.materia,
                         "prova": c.prova.nome, "mundo_emoji": c.prova.mundo["emoji"],
                         "paginas": c.paginas or "", "fases": []}
        if i["fase"] not in out[c.id]["fases"]:
            out[c.id]["fases"].append(i["fase"])
    return list(out.values())


def assuntos_da_prova(prova):
    return [{"id": c.id, "titulo": c.titulo, "emoji": c.emoji, "materia": prova.materia, "prova": prova.nome,
             "mundo_emoji": prova.mundo["emoji"], "paginas": c.paginas or "", "fases": [3]}
            for c in prova.conteudos if c.atividades_ativas()]
