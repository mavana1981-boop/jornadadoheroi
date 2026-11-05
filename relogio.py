"""Data de "hoje" no horário de Brasília.

O servidor (Railway) roda em UTC: depois das 21h em Brasília o servidor já está no dia seguinte.
Todo o app usa relogio.hoje() em vez de date.today(). O fuso pode ser trocado pela variável FUSO.
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo(os.environ.get("FUSO", "America/Sao_Paulo"))


def agora():
    return datetime.now(FUSO)


def hoje():
    return agora().date()
