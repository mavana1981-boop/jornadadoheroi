# Jornada do Herói

App de revisão gamificada para o 3º ano do Fundamental (Flask + SQLAlchemy + HTML/JS).

## Como funciona
- **Mundos** = matérias (Matemática ⛰️, Português 🌳, Ciências 🌱, Geografia e História 🏰), cada um com um chefão.
- **Missão diária** (≈12 desafios, 15–20 min) em 3 fases: Aquecimento → Desafio → Chefão.
- **Repetição espaçada**: cada conteúdo tem 5 níveis de domínio; os fracos voltam mais vezes e tudo é revisado antes da data da prova. Desafio errado volta no fim da fase.
- **Véspera da prova**: Batalha Final só com o conteúdo daquela prova.
- **9 tipos de jogo**: escolha, verdade ou mentira, completar, cálculo com teclado, ligar pares, memória, ordenar, separar nos baús e cartas mágicas. Todos com leitura em voz alta (🔊).
- **Recompensas**: XP, níveis, moedas, sequência de dias, conquistas e loja de itens para o herói.
- **Painel dos Pais** (`/pais`, PIN): datas das provas, conteúdos, desempenho, prévia de cada atividade, criação manual ou pelo Gemini (inclusive a partir de **fotos das páginas do livro**).

Vem com 26 conteúdos e 203 desafios tirados das páginas do livro. As datas das provas são provisórias — ajuste no painel.

## Variáveis de ambiente (Railway)
| Variável | Para quê |
|---|---|
| `DATABASE_URL` | Postgres do Railway (sem ela usa SQLite local) |
| `SECRET_KEY` | chave da sessão |
| `PARENT_PIN` | PIN do Painel dos Pais (padrão `1234`) |
| `GEMINI_API_KEY` | chave da API do Gemini (Google AI Studio) |
| `GEMINI_MODEL` | opcional, padrão `gemini-2.5-flash` |

## Rodar local
```bash
pip install -r requirements.txt
python app.py
```
