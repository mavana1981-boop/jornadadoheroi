"""Modelos de dados da Jornada do Herói."""
import json
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Mundos da jornada: cada matéria vira um mundo com tema, cores e um "chefão".
MUNDOS = {
    "Matemática": {
        "nome": "Montanhas dos Números", "emoji": "⛰️", "cor": "#ff8a3d", "cor2": "#ffd166",
        "chefao": "Golem das Contas", "chefao_emoji": "🗿", "cenario": "🏔️🌋🪨",
    },
    "Português": {
        "nome": "Floresta das Palavras", "emoji": "🌳", "cor": "#2bb673", "cor2": "#a8e063",
        "chefao": "Dragão do Esquecimento", "chefao_emoji": "🐉", "cenario": "🌲🍄🌿",
    },
    "Ciências": {
        "nome": "Vale da Natureza", "emoji": "🌱", "cor": "#1fa2ff", "cor2": "#12d8fa",
        "chefao": "Polvo da Poluição", "chefao_emoji": "🐙", "cenario": "💧🌦️🪴",
    },
    "Geografia e História": {
        "nome": "Reino do Município", "emoji": "🏰", "cor": "#9b5de5", "cor2": "#f15bb5",
        "chefao": "Rei Consumista", "chefao_emoji": "👑", "cenario": "🏘️🚜🏭",
    },
}
MUNDO_PADRAO = {
    "nome": "Ilha Misteriosa", "emoji": "🏝️", "cor": "#00bbf9", "cor2": "#00f5d4",
    "chefao": "Sombra da Dúvida", "chefao_emoji": "👻", "cenario": "🌴🗺️⭐",
}


def mundo_de(materia):
    return MUNDOS.get(materia, MUNDO_PADRAO)


TIPOS = {
    "quiz": "Desafio de escolha",
    "vf": "Verdade ou Mentira",
    "completar": "Complete a frase",
    "contas": "Cálculo rápido",
    "ligar": "Ligue os pares",
    "memoria": "Jogo da memória",
    "ordenar": "Coloque em ordem",
    "categorizar": "Separe nos baús",
    "flashcard": "Carta mágica",
}


class Heroi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    avatar = db.Column(db.String(16), default="🦸‍♂️")
    cor = db.Column(db.String(16), default="#ff8a3d")
    interesses = db.Column(db.String(300), default="")
    xp = db.Column(db.Integer, default=0)
    moedas = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    ultimo_dia = db.Column(db.Date)
    itens = db.Column(db.Text, default="[]")       # itens comprados
    equipados = db.Column(db.Text, default="[]")   # itens em uso
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    NIVEIS = ["Aprendiz", "Explorador", "Aventureiro", "Cavaleiro", "Guardião", "Mestre", "Lenda"]

    @property
    def nivel(self):
        return self.xp // 300 + 1

    @property
    def titulo(self):
        return self.NIVEIS[min(self.nivel - 1, len(self.NIVEIS) - 1)]

    @property
    def xp_no_nivel(self):
        return self.xp % 300

    def lista_itens(self):
        return json.loads(self.itens or "[]")

    def lista_equipados(self):
        return json.loads(self.equipados or "[]")


class Prova(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    materia = db.Column(db.String(60), nullable=False)
    titulo = db.Column(db.String(120), default="")
    data = db.Column(db.Date)
    ativa = db.Column(db.Boolean, default=True)
    conteudos = db.relationship("Conteudo", backref="prova", cascade="all, delete-orphan",
                                order_by="Conteudo.ordem")

    @property
    def mundo(self):
        return mundo_de(self.materia)

    @property
    def dias_restantes(self):
        if not self.data:
            return None
        return (self.data - date.today()).days

    @property
    def dominio(self):
        """0-100: média do domínio dos conteúdos."""
        if not self.conteudos:
            return 0
        return round(sum(c.dominio for c in self.conteudos) / len(self.conteudos))


class Conteudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prova_id = db.Column(db.Integer, db.ForeignKey("prova.id"), nullable=False)
    titulo = db.Column(db.String(160), nullable=False)
    resumo = db.Column(db.Text, default="")
    paginas = db.Column(db.String(60), default="")
    emoji = db.Column(db.String(16), default="📘")
    ordem = db.Column(db.Integer, default=0)
    # repetição espaçada (caixas de Leitner: 0 = novo, 5 = dominado)
    caixa = db.Column(db.Integer, default=0)
    proxima_revisao = db.Column(db.Date)
    ultima_revisao = db.Column(db.Date)
    acertos = db.Column(db.Integer, default=0)
    erros = db.Column(db.Integer, default=0)
    atividades = db.relationship("Atividade", backref="conteudo", cascade="all, delete-orphan")

    @property
    def dominio(self):
        """0-100: média do aproveitamento de cada atividade ativa (acertos ÷ tentativas).
        Atividade nunca jogada conta 0, então o domínio cresce com acertos e com cobertura."""
        ativas = self.atividades_ativas()
        if not ativas:
            return 0
        soma = sum(a.acertos / a.vezes for a in ativas if a.vezes)
        return round(100 * soma / len(ativas))

    @property
    def estrelas(self):
        """0 a 5 estrelas a partir do domínio (cada estrela = 20%)."""
        d = self.dominio
        return 0 if d == 0 else max(1, min(5, round(d / 20)))

    def atividades_ativas(self):
        return [a for a in self.atividades if a.ativa]


class Atividade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo_id = db.Column(db.Integer, db.ForeignKey("conteudo.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    dados = db.Column(db.Text, nullable=False)
    origem = db.Column(db.String(20), default="livro")  # livro | gemini | manual
    ativa = db.Column(db.Boolean, default=True)
    vezes = db.Column(db.Integer, default=0)
    acertos = db.Column(db.Integer, default=0)
    ultima_vez = db.Column(db.Date)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

    def d(self):
        return json.loads(self.dados)

    def to_dict(self):
        return {"id": self.id, "tipo": self.tipo, "dados": self.d(),
                "conteudo": self.conteudo.titulo, "conteudo_id": self.conteudo_id,
                "materia": self.conteudo.prova.materia}


class Missao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, unique=True, nullable=False)
    tipo = db.Column(db.String(20), default="diaria")  # diaria | batalha_final
    titulo = db.Column(db.String(160), default="")
    historia = db.Column(db.Text, default="")
    itens = db.Column(db.Text, default="[]")  # [{"atividade_id":..,"fase":..}]
    status = db.Column(db.String(20), default="nova")  # nova | concluida
    acertos = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    estrelas = db.Column(db.Integer, default=0)
    xp_ganho = db.Column(db.Integer, default=0)
    concluida_em = db.Column(db.DateTime)

    def lista_itens(self):
        return json.loads(self.itens or "[]")


class Resposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    missao_id = db.Column(db.Integer, db.ForeignKey("missao.id"))
    atividade_id = db.Column(db.Integer, db.ForeignKey("atividade.id"))
    acertou = db.Column(db.Boolean, default=False)
    modo = db.Column(db.String(20), default="missao")  # missao | treino
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class Config(db.Model):
    chave = db.Column(db.String(60), primary_key=True)
    valor = db.Column(db.String(500))

    @staticmethod
    def get(chave, padrao=None):
        c = db.session.get(Config, chave)
        return c.valor if c else padrao

    @staticmethod
    def set(chave, valor):
        c = db.session.get(Config, chave)
        if c:
            c.valor = str(valor)
        else:
            db.session.add(Config(chave=chave, valor=str(valor)))
