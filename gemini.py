"""Integração com a API do Gemini: gera atividades, lê fotos do livro e escreve a história do dia."""
import base64
import json
import os
import re

import requests

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def modelo():
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def disponivel():
    return bool(os.environ.get("GEMINI_API_KEY"))


class GeminiErro(Exception):
    pass


def _chamar(partes, json_saida=True, temperatura=0.8, timeout=90):
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise GeminiErro("Defina a variável GEMINI_API_KEY para usar o Gemini.")
    corpo = {
        "contents": [{"role": "user", "parts": partes}],
        "generationConfig": {"temperature": temperatura},
    }
    if json_saida:
        corpo["generationConfig"]["responseMimeType"] = "application/json"
    r = requests.post(GEMINI_URL.format(model=modelo()), params={"key": chave},
                      json=corpo, timeout=timeout)
    if r.status_code != 200:
        raise GeminiErro(f"Gemini respondeu {r.status_code}: {r.text[:300]}")
    try:
        texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise GeminiErro("Resposta vazia do Gemini.")
    if not json_saida:
        return texto.strip()
    texto = re.sub(r"^```(json)?|```$", "", texto.strip(), flags=re.M).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        raise GeminiErro("O Gemini não devolveu um JSON válido. Tente de novo.")


# ---------------------------------------------------------------------------
# Formato de cada tipo de atividade (o mesmo usado pelo motor de jogos)
# ---------------------------------------------------------------------------
FORMATOS = """
Tipos aceitos e o formato JSON de "dados" de cada um:
- "quiz": {"pergunta": str, "opcoes": [3 ou 4 strings], "correta": índice da opção certa (0..), "explicacao": str, "emoji": str}
- "vf": {"afirmacao": str, "resposta": true|false, "explicacao": str, "emoji": str}
- "completar": {"frase": str com "___" no lugar da lacuna, "opcoes": [3 ou 4 strings], "correta": índice, "explicacao": str}
- "contas": {"pergunta": str, "resposta": número, "unidade": str (ex. "cm", "reais", "" se nenhuma), "explicacao": str, "emoji": str}
- "ligar": {"titulo": str, "pares": [[esquerda, direita], ... 3 a 5 pares]}
- "memoria": {"titulo": str, "pares": [[carta A, carta B], ... 4 a 6 pares; textos curtos, pode usar emoji]}
- "ordenar": {"titulo": str, "itens": [3 a 5 strings JÁ na ordem correta], "explicacao": str}
- "categorizar": {"titulo": str, "categorias": [2 ou 3 strings], "itens": [{"texto": str, "categoria": uma das categorias}, ... 5 a 8 itens]}
- "flashcard": {"frente": str (pergunta curta), "verso": str (resposta curta), "emoji": str}

ILUSTRAÇÕES (muito importante — o jogo é bem visual):
- Em qualquer tipo, inclua "imagem": descrição curta, em português, de uma ilustração que ajude a entender o enunciado
  (ex.: "menina andando de bicicleta", "corte do solo mostrando as camadas"). Não descreva a resposta.
- Em "memoria", "ligar", "ordenar", "categorizar" e nas opções de "quiz", inclua "imagens": {"texto exato da carta/item": "descrição da ilustração"}
  para tudo que puder ser desenhado (objetos, animais, lugares, ações, alimentos). Em jogos de pares, ilustre só um lado de cada par.
- Para formas geométricas use exatamente: "svg:cubo", "svg:paralelepipedo", "svg:piramide:3" (ou 4, 5, 6 = lados da base),
  "svg:prisma:3", "svg:cilindro", "svg:cone", "svg:esfera". Para medidas exatas use "svg:balanca:500 g", "svg:jarra:250" (mL, até 1000),
  "svg:regua:14" (cm). Para frações use "svg:partes:4" (círculo em 4 partes iguais).
"""

PUBLICO = """Público: criança de 8 anos, 3º ano do Ensino Fundamental, no Brasil.
Linguagem: português do Brasil, frases curtas, vocabulário simples, tom de aventura e de jogo.
Cada atividade deve ter forte apelo visual: ilustrações (campos "imagem"/"imagens") e emojis que ajudem a lembrar a ideia.
Seja fiel ao conteúdo escolar informado — nada de inventar fatos. Respostas sem ambiguidade."""


def _personalizacao(heroi):
    if not heroi:
        return ""
    txt = f"O herói se chama {heroi.nome}."
    if heroi.interesses:
        txt += (f" Ele gosta de: {heroi.interesses}. Quando fizer sentido, use esses interesses"
                f" nos exemplos e situações (sem mudar o conteúdo da matéria).")
    return txt


def gerar_atividades(materia, titulo, resumo, tipos, quantidade, heroi=None, imagens=None):
    prompt = f"""Você cria fases de um jogo educativo de revisão para prova, no estilo "jornada do herói".
{PUBLICO}
{_personalizacao(heroi)}

Matéria: {materia}
Conteúdo: {titulo}
Resumo do conteúdo (base obrigatória):
{resumo or '(use as fotos do livro anexadas)'}

Crie {quantidade} atividades variadas, distribuídas entre estes tipos: {', '.join(tipos)}.
{FORMATOS}
Responda APENAS com JSON no formato: {{"atividades": [{{"tipo": "...", "dados": {{...}}}}]}}"""
    partes = [{"text": prompt}] + _partes_imagens(imagens)
    saida = _chamar(partes)
    brutas = saida.get("atividades", []) if isinstance(saida, dict) else saida
    return [a for a in (validar(x.get("tipo"), x.get("dados")) for x in brutas if isinstance(x, dict)) if a]


def extrair_de_fotos(materia, imagens, heroi=None, quantidade=10):
    """Lê fotos das páginas do livro e devolve título, resumo e atividades."""
    prompt = f"""Estas são fotos de páginas do livro escolar ({materia}) de uma criança do 3º ano.
Leia o texto das páginas (ignore respostas escritas à mão que possam estar erradas) e:
1) dê um título curto ao conteúdo;
2) escreva um resumo fiel, em tópicos, com os conceitos que podem cair na prova (até 15 linhas);
3) crie {quantidade} atividades de revisão variadas.
{PUBLICO}
{_personalizacao(heroi)}
{FORMATOS}
Responda APENAS com JSON: {{"titulo": str, "emoji": str, "resumo": str, "atividades": [{{"tipo": "...", "dados": {{...}}}}]}}"""
    saida = _chamar([{"text": prompt}] + _partes_imagens(imagens), timeout=150)
    atividades = [a for a in (validar(x.get("tipo"), x.get("dados"))
                              for x in saida.get("atividades", []) if isinstance(x, dict)) if a]
    return {
        "titulo": str(saida.get("titulo", "Novo conteúdo"))[:150],
        "emoji": str(saida.get("emoji", "📘"))[:8],
        "resumo": str(saida.get("resumo", "")),
        "atividades": atividades,
    }


def historia_da_missao(heroi, mundos, conteudos, tipo="diaria", dias_prova=None):
    prompt = f"""Escreva a abertura da missão de hoje de um jogo educativo (jornada do herói) para uma criança de 8 anos.
Herói: {heroi.nome}. Interesses: {heroi.interesses or 'aventura'}.
Mundos visitados hoje: {', '.join(mundos)}.
Conteúdos que ele vai revisar: {', '.join(conteudos)}.
{'É a BATALHA FINAL: a prova é amanhã ou hoje!' if tipo == 'batalha_final' else ''}
{f'Faltam {dias_prova} dias para a próxima prova.' if dias_prova is not None else ''}
O mentor é a Coruja Sábia 🦉. Fale direto com o herói pelo nome, com entusiasmo, em 3 ou 4 frases curtas,
com 2 ou 3 emojis. Sem títulos, só o texto."""
    return _chamar([{"text": prompt}], json_saida=False, temperatura=1.0, timeout=30)


def _partes_imagens(imagens):
    partes = []
    for img in imagens or []:
        dados, mime = img
        partes.append({"inline_data": {"mime_type": mime or "image/jpeg",
                                       "data": base64.b64encode(dados).decode()}})
    return partes


# ---------------------------------------------------------------------------
# Validação: garante que tudo que entra no banco o jogo consegue renderizar
# ---------------------------------------------------------------------------
def _s(v, n=300):
    return str(v).strip()[:n] if v is not None else ""


def validar(tipo, d):
    """Devolve {"tipo","dados"} normalizado ou None se inválido."""
    if not isinstance(d, dict):
        return None
    try:
        if tipo in ("quiz", "completar"):
            campo = "pergunta" if tipo == "quiz" else "frase"
            ops = [_s(o, 120) for o in d.get("opcoes", []) if _s(o)]
            c = int(d.get("correta", -1))
            if not _s(d.get(campo)) or len(ops) < 2 or not 0 <= c < len(ops):
                return None
            if tipo == "completar" and "___" not in d[campo]:
                return None
            out = {campo: _s(d[campo]), "opcoes": ops, "correta": c,
                   "explicacao": _s(d.get("explicacao")), "emoji": _s(d.get("emoji"), 12)}
        elif tipo == "vf":
            if not _s(d.get("afirmacao")) or not isinstance(d.get("resposta"), bool):
                return None
            out = {"afirmacao": _s(d["afirmacao"]), "resposta": d["resposta"],
                   "explicacao": _s(d.get("explicacao")), "emoji": _s(d.get("emoji"), 12)}
        elif tipo == "contas":
            resp = float(str(d.get("resposta")).replace(",", "."))
            if not _s(d.get("pergunta")):
                return None
            out = {"pergunta": _s(d["pergunta"]), "resposta": int(resp) if resp.is_integer() else resp,
                   "unidade": _s(d.get("unidade"), 20), "explicacao": _s(d.get("explicacao")),
                   "emoji": _s(d.get("emoji"), 12)}
        elif tipo in ("ligar", "memoria"):
            pares = [[_s(p[0], 80), _s(p[1], 80)] for p in d.get("pares", [])
                     if isinstance(p, (list, tuple)) and len(p) == 2 and _s(p[0]) and _s(p[1])]
            if len(pares) < 2:
                return None
            out = {"titulo": _s(d.get("titulo")) or ("Ligue os pares" if tipo == "ligar" else "Encontre os pares"),
                   "pares": pares[:6]}
        elif tipo == "ordenar":
            itens = [_s(i, 100) for i in d.get("itens", []) if _s(i)]
            if len(itens) < 3:
                return None
            out = {"titulo": _s(d.get("titulo")) or "Coloque em ordem", "itens": itens[:6],
                   "explicacao": _s(d.get("explicacao"))}
        elif tipo == "categorizar":
            cats = [_s(c, 40) for c in d.get("categorias", []) if _s(c)]
            itens = [{"texto": _s(i.get("texto"), 80), "categoria": _s(i.get("categoria"), 40)}
                     for i in d.get("itens", []) if isinstance(i, dict)]
            itens = [i for i in itens if i["texto"] and i["categoria"] in cats]
            if len(cats) < 2 or len(itens) < 3:
                return None
            out = {"titulo": _s(d.get("titulo")) or "Separe nos baús", "categorias": cats[:3], "itens": itens[:10]}
        elif tipo == "flashcard":
            if not _s(d.get("frente")) or not _s(d.get("verso")):
                return None
            out = {"frente": _s(d["frente"]), "verso": _s(d["verso"]), "emoji": _s(d.get("emoji"), 12)}
        else:
            return None
    except (TypeError, ValueError):
        return None
    # ilustrações opcionais: "imagem" (do enunciado) e "imagens" ({texto exato: descrição})
    if _s(d.get("imagem")):
        out["imagem"] = _s(d["imagem"], 200)
    if isinstance(d.get("imagens"), dict):
        imgs = {_s(k, 120): _s(v, 200) for k, v in d["imagens"].items() if _s(k) and _s(v)}
        if imgs:
            out["imagens"] = dict(list(imgs.items())[:12])
    return {"tipo": tipo, "dados": out}


# ---------------------------------------------------------------------------
# Geração de imagens (ilustrações das atividades)
# ---------------------------------------------------------------------------
MODELOS_IMAGEM = ["gemini-nano-banana-2.1", "gemini-3.1-flash-lite-image", "gemini-3.1-flash-image",
                  "gemini-2.5-flash-image"]

ESTILO_IMAGEM = ("Ilustração para livro didático infantil: desenho colorido, traço limpo e simples, "
                 "cores vivas, fundo branco liso, um único assunto centralizado e bem reconhecível, "
                 "SEM nenhum texto, letra, número ou marca d'água. Assunto: ")


class GeminiSemFaturamento(GeminiErro):
    """A chave não pode gerar imagens (sem faturamento ou sem permissão)."""


def gerar_imagem(descricao, modelo_preferido=None):
    """Gera uma ilustração. Devolve (bytes, mime, modelo_usado)."""
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise GeminiSemFaturamento("GEMINI_API_KEY não definida.")
    modelos = [m for m in [os.environ.get("GEMINI_IMAGE_MODEL"), modelo_preferido] if m] + MODELOS_IMAGEM
    vistos, ultimo = set(), ""
    for m in modelos:
        if m in vistos:
            continue
        vistos.add(m)
        for modalidades in (["IMAGE"], ["TEXT", "IMAGE"]):
            corpo = {"contents": [{"role": "user", "parts": [{"text": ESTILO_IMAGEM + descricao}]}],
                     "generationConfig": {"responseModalities": modalidades,
                                          "imageConfig": {"aspectRatio": "1:1"}}}
            r = requests.post(GEMINI_URL.format(model=m), params={"key": chave}, json=corpo, timeout=120)
            if r.status_code == 200:
                for cand in r.json().get("candidates", []):
                    for parte in (cand.get("content") or {}).get("parts", []):
                        dado = parte.get("inlineData") or parte.get("inline_data")
                        if dado and dado.get("data"):
                            return (base64.b64decode(dado["data"]),
                                    dado.get("mimeType") or dado.get("mime_type") or "image/png", m)
                ultimo = "o modelo não devolveu imagem"
                break  # tenta o próximo modelo
            txt = r.text[:300]
            ultimo = f"{r.status_code}: {txt}"
            if r.status_code == 400 and ("responseModalities" in txt or "modalit" in txt.lower()):
                continue  # tenta com outra combinação de modalidades
            if r.status_code == 404 or (r.status_code == 400 and "not found" in txt.lower()):
                break  # modelo não existe: tenta o próximo
            if r.status_code in (401, 403) or "billing" in txt.lower() or (
                    r.status_code == 429 and "free" in txt.lower() and "limit: 0" in txt.lower()):
                raise GeminiSemFaturamento(f"A chave do Gemini não pode gerar imagens ({ultimo}).")
            raise GeminiErro(f"Erro ao gerar imagem ({ultimo}).")
    raise GeminiErro(f"Nenhum modelo de imagem disponível ({ultimo}).")
