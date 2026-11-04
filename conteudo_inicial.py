"""Conteúdo pré-carregado a partir das páginas do livro (3º ano).

Cada conteúdo traz um resumo (base para o Gemini criar mais atividades) e atividades prontas.
As provas e datas seguem o Orientador de Estudos – Avaliações Globalizantes (3º trimestre/2026, 3º ano).
"""
import copy


def Q(pergunta, opcoes, correta, explicacao="", emoji=""):
    return ("quiz", {"pergunta": pergunta, "opcoes": opcoes, "correta": correta,
                     "explicacao": explicacao, "emoji": emoji})


def VF(afirmacao, resposta, explicacao="", emoji=""):
    return ("vf", {"afirmacao": afirmacao, "resposta": resposta, "explicacao": explicacao, "emoji": emoji})


def C(frase, opcoes, correta, explicacao=""):
    return ("completar", {"frase": frase, "opcoes": opcoes, "correta": correta, "explicacao": explicacao})


def N(pergunta, resposta, unidade="", explicacao="", emoji=""):
    return ("contas", {"pergunta": pergunta, "resposta": resposta, "unidade": unidade,
                       "explicacao": explicacao, "emoji": emoji})


def L(titulo, pares):
    return ("ligar", {"titulo": titulo, "pares": pares})


def M(titulo, pares):
    return ("memoria", {"titulo": titulo, "pares": pares})


def O(titulo, itens, explicacao=""):
    return ("ordenar", {"titulo": titulo, "itens": itens, "explicacao": explicacao})


def K(titulo, grupos):
    cats = list(grupos.keys())
    itens = [{"texto": t, "categoria": c} for c, lista in grupos.items() for t in lista]
    return ("categorizar", {"titulo": titulo, "categorias": cats, "itens": itens})


def F(frente, verso, emoji=""):
    return ("flashcard", {"frente": frente, "verso": verso, "emoji": emoji})


_BANCO = [
    # =====================================================================
    {"materia": "Matemática", "titulo": "Prova de Matemática", "data": "2026-11-23", "conteudos": [
        {"titulo": "Sólidos geométricos: poliedros e corpos redondos", "emoji": "🧊", "paginas": "34-39",
         "resumo": "Poliedros: sólidos com faces planas, arestas e vértices (cubo, paralelepípedo, prismas, pirâmides). "
                   "Corpos redondos: têm superfície curva e podem rolar (cilindro, cone, esfera). "
                   "Prisma: duas faces iguais e paralelas chamadas bases; as outras faces são quadriláteros. "
                   "Pirâmide: uma face é a base e as outras faces são triângulos que se encontram num vértice. "
                   "Objetos do dia a dia lembram sólidos: caixa de presente = cubo, lata = cilindro, chapéu de festa = cone, bola = esfera, tijolo = paralelepípedo. "
                   "As pirâmides do Egito têm faces em forma de triângulo.",
         "atividades": [
             K("Poliedro ou corpo redondo?", {"Poliedro": ["Cubo", "Pirâmide", "Paralelepípedo", "Prisma"],
                                              "Corpo redondo": ["Esfera", "Cilindro", "Cone"]}),
             L("Qual sólido o objeto lembra?", [["🎁 Caixa de presente", "Cubo"], ["🥫 Lata de refrigerante", "Cilindro"],
                                                ["🥳 Chapéu de festa", "Cone"], ["⚽ Bola", "Esfera"], ["🧱 Tijolo", "Paralelepípedo"]]),
             Q("Qual destes sólidos é um POLIEDRO?", ["Esfera", "Cone", "Pirâmide", "Cilindro"], 2,
               "A pirâmide só tem faces planas, arestas e vértices. Por isso é um poliedro.", "🔺"),
             Q("Por que a esfera é um corpo redondo?", ["Porque tem superfície curva", "Porque tem 6 faces",
               "Porque tem vértices pontudos", "Porque é feita de papel"], 0, "Corpos redondos têm superfície curva e rolam.", "⚽"),
             VF("Nas pirâmides, as faces laterais são triângulos.", True, "A base pode variar, mas as outras faces são sempre triângulos.", "🔺"),
             VF("O cilindro é um poliedro.", False, "O cilindro tem superfície curva: é um corpo redondo.", "🥫"),
             C("No prisma, as duas faces iguais e paralelas são chamadas de ___.", ["bases", "vértices", "arestas"], 0,
               "As duas faces iguais e paralelas do prisma são as bases."),
             F("O que é um poliedro?", "Sólido formado só por faces planas, com arestas e vértices.", "🧊"),
             F("Cite 3 corpos redondos.", "Cilindro, cone e esfera.", "🟠"),
         ]},
        {"titulo": "Faces, vértices, arestas e planificação", "emoji": "📦", "paginas": "40-42",
         "resumo": "Face: cada superfície plana do sólido. Aresta: encontro de duas faces (a 'linha'). Vértice: ponto onde as arestas se encontram (a 'ponta'). "
                   "Cubo e paralelepípedo: 6 faces, 8 vértices e 12 arestas. Pirâmide de base quadrada: 5 faces, 5 vértices, 8 arestas. "
                   "Pirâmide de base triangular: 4 faces, 4 vértices, 6 arestas. Caixa de pizza octogonal: 10 faces, 16 vértices, 24 arestas. "
                   "Planificação é desmontar o sólido e mostrar todas as faces abertas no plano. A planificação do cubo tem 6 quadrados.",
         "atividades": [
             N("Quantas faces tem um cubo?", 6, "faces", "O cubo tem 6 faces quadradas, como um dado.", "🎲"),
             N("Quantos vértices tem um cubo?", 8, "vértices", "São 8 'pontinhas': 4 em cima e 4 embaixo.", "🎲"),
             N("Quantas arestas tem uma caixa de sapato (paralelepípedo)?", 12, "arestas", "Igual ao cubo: 12 arestas.", "👟"),
             N("Quantas faces tem uma pirâmide de base quadrada?", 5, "faces", "1 base quadrada + 4 triângulos = 5 faces.", "🔺"),
             L("Ligue cada parte ao que ela é", [["Face", "Superfície plana do sólido"], ["Aresta", "Encontro de duas faces"],
                                                ["Vértice", "Ponto onde as arestas se encontram"]]),
             Q("A planificação do cubo é formada por…", ["6 quadrados", "4 triângulos", "2 círculos e 1 retângulo", "5 quadrados"], 0,
               "Ao desmontar o cubo, aparecem as suas 6 faces quadradas.", "📐"),
             Q("A planificação com 1 quadrado e 4 triângulos forma qual sólido?", ["Pirâmide de base quadrada", "Cubo", "Cone", "Prisma"], 0,
               "Base quadrada + 4 faces triangulares = pirâmide de base quadrada.", "🔺"),
             M("Sólido e número de faces", [["🎲 Cubo", "6 faces"], ["🔺 Pirâmide quadrada", "5 faces"],
                                            ["🔻 Pirâmide triangular", "4 faces"], ["🍕 Caixa de pizza", "10 faces"]]),
             F("O que é planificar um sólido?", "Abrir o sólido no plano, mostrando todas as suas faces.", "✂️"),
         ]},
        {"titulo": "Medidas de comprimento: metro, centímetro, milímetro e quilômetro", "emoji": "📏", "paginas": "44-49, 244-248",
         "resumo": "Para medir comprimento usamos régua, fita métrica e trena; a medição começa no zero. "
                   "O metro (m) é a unidade-padrão. 1 m = 100 cm. 1 cm = 10 mm. Meio metro = 50 cm. Um quarto de metro = 25 cm. "
                   "Para grandes distâncias usamos o quilômetro (km): 1 km = 1 000 m; 2 000 m = 2 km; 1 500 m = 1 km e 500 m. "
                   "Antigamente as pessoas mediam com partes do corpo (palmo, pé, passos), mas cada pessoa tem um tamanho diferente, por isso as medidas mudavam.",
         "atividades": [
             N("Quantos centímetros tem 1 metro?", 100, "cm", "1 m = 100 cm.", "📏"),
             N("Quantos milímetros tem 1 centímetro?", 10, "mm", "1 cm = 10 mm.", "📏"),
             N("Quantos metros tem 1 quilômetro?", 1000, "m", "1 km = 1 000 m.", "🛣️"),
             N("Meio metro tem quantos centímetros?", 50, "cm", "Metade de 100 cm é 50 cm.", "✂️"),
             N("Um quarto de metro tem quantos centímetros?", 25, "cm", "100 dividido em 4 partes iguais = 25 cm.", "🍰"),
             N("Um muro tem 1 metro e 50 centímetros. Quantos centímetros são?", 150, "cm", "100 cm + 50 cm = 150 cm.", "🧱"),
             L("Qual unidade usar?", [["🐜 Comprimento de uma formiga", "milímetro"], ["✏️ Comprimento de um lápis", "centímetro"],
                                      ["🚪 Altura da porta", "metro"], ["🚗 Distância entre cidades", "quilômetro"]]),
             Q("Onde a medição com a régua deve começar?", ["No número 0", "No número 1", "No meio da régua", "Em qualquer lugar"], 0,
               "Sempre começamos a medir no zero!", "📐"),
             VF("Medir com passos dá sempre o mesmo resultado para todas as pessoas.", False,
                "Cada pessoa tem um tamanho de passo diferente. Por isso usamos instrumentos como a régua.", "👣"),
             C("2 000 metros é o mesmo que ___ quilômetros.", ["2", "20", "200"], 0, "Cada 1 000 m = 1 km."),
             F("Qual é o símbolo do metro, do centímetro e do quilômetro?", "m, cm e km (em letras minúsculas).", "🔤"),
         ]},
        {"titulo": "Perímetro", "emoji": "🔲", "paginas": "47-49",
         "resumo": "Perímetro é a medida do contorno de uma figura plana: somamos as medidas de todos os lados. "
                   "Mesa de 2 m por 1 m: 2 + 1 + 2 + 1 = 6 m de fita. Canteiro triangular de lados 4 m, 4 m e 3 m: 11 m de cerca. "
                   "Canteiro de lados 4, 5, 6 e 5 m: 20 m de cerca. Praça de 195 m por 120 m: 630 m em uma volta. "
                   "Nas figuras circulares o contorno se chama circunferência.",
         "atividades": [
             Q("Quando medimos o contorno de uma figura plana, calculamos o…", ["perímetro", "peso", "volume", "troco"], 0,
               "Perímetro = medida do contorno.", "🔲"),
             N("Uma mesa tem 2 m de comprimento e 1 m de largura. Quantos metros de fita para contorná-la?", 6, "m",
               "2 + 1 + 2 + 1 = 6 m.", "🎀"),
             N("Um canteiro triangular tem lados de 4 m, 4 m e 3 m. Quantos metros de cerca?", 11, "m", "4 + 4 + 3 = 11 m.", "🌱"),
             N("Um canteiro tem lados de 4 m, 5 m, 6 m e 5 m. Qual é o perímetro?", 20, "m", "4 + 5 + 6 + 5 = 20 m.", "🥕"),
             N("Um quadrado tem 3 cm de lado. Qual é o seu perímetro?", 12, "cm", "3 + 3 + 3 + 3 = 12 cm.", "🟩"),
             N("Carlos deu 1 volta numa praça de 195 m por 120 m. Quantos metros andou?", 630, "m",
               "195 + 120 + 195 + 120 = 630 m.", "🏃"),
             F("Como calcular o perímetro?", "Somando as medidas de todos os lados da figura.", "➕"),
             VF("O contorno de uma figura circular se chama circunferência.", True, "", "⭕"),
         ]},
        {"titulo": "Medidas de massa: grama, quilograma e miligrama", "emoji": "⚖️", "paginas": "103-105",
         "resumo": "Massa é medida com a balança. As unidades mais usadas são o grama (g) e o quilograma (kg). 1 kg = 1 000 g. "
                   "Se dividirmos 1 grama em 1 000 partes, cada parte é 1 miligrama (mg): 1 g = 1 000 mg. "
                   "No dia a dia o arroz é vendido pela massa, o ovo por unidade e a água pela capacidade. "
                   "Lucas nasceu com 3 kg (3 000 g); aos 4 anos tinha 16 kg: a diferença é 13 kg. "
                   "Dobro = 2 vezes a quantidade; triplo = 3 vezes. Pessoa e xícara podem marcar o mesmo número na balança, mas com unidades diferentes (50 kg e 50 g).",
         "atividades": [
             N("Quantos gramas tem 1 quilograma?", 1000, "g", "1 kg = 1 000 g.", "⚖️"),
             N("Quantos miligramas tem 1 grama?", 1000, "mg", "1 g = 1 000 mg.", "💊"),
             N("Lucas nasceu com 3 kg. Aos 4 anos tinha 16 kg. Quantos quilos ele ganhou?", 13, "kg", "16 − 3 = 13 kg.", "👶"),
             Q("Qual instrumento mede a massa?", ["Balança", "Régua", "Fita métrica", "Copo medidor"], 0, "A balança mede a massa.", "⚖️"),
             K("Como cada coisa é vendida?", {"Por massa (kg/g)": ["Arroz", "Feijão", "Carne"],
                                              "Por capacidade (L/mL)": ["Água", "Suco", "Leite"],
                                              "Por unidade": ["Ovos", "Lápis"]}),
             Q("Uma pessoa e uma xícara com alface marcam 50 na balança. Elas têm a mesma massa?",
               ["Não: a pessoa tem 50 kg e a xícara 50 g", "Sim, as duas têm 50 kg", "Sim, as duas têm 50 g", "Não dá para saber"], 0,
               "O número é igual, mas as unidades são diferentes: kg é muito mais que g.", "🥗"),
             VF("1 kg de algodão tem a mesma massa que 1 kg de ferro.", True, "Os dois têm 1 kg! Só o tamanho é diferente.", "☁️"),
             F("Qual é o símbolo do grama e do quilograma?", "g e kg (letras minúsculas, sem ponto).", "🔤"),
         ]},
        {"titulo": "Medidas de capacidade: litro e mililitro", "emoji": "🥤", "paginas": "108-112, 118-120, 251",
         "resumo": "Capacidade é a quantidade de líquido que cabe num recipiente. Usamos o litro (L) para recipientes maiores (garrafas, galões) e o mililitro (mL) para menores (copos, xícaras). "
                   "1 L = 1 000 mL. 5 L = 5 000 mL. 4 copos de 250 mL = 1 000 mL = 1 L. Metade de 1 L = 500 mL. "
                   "Copo medidor e jarras graduadas medem capacidade. 1 000 mL dividido para 4 pessoas = 250 mL para cada. "
                   "Uma garrafa de 2 L enche 5 embalagens de 400 mL.",
         "atividades": [
             N("Quantos mililitros tem 1 litro?", 1000, "mL", "1 L = 1 000 mL.", "🧃"),
             N("Quantos mililitros cabem numa garrafa de 5 litros?", 5000, "mL", "5 × 1 000 = 5 000 mL.", "🫙"),
             N("Quantos copos de 250 mL enchemos com 1 litro?", 4, "copos", "250 + 250 + 250 + 250 = 1 000 mL.", "🥛"),
             N("Gustavo dividiu 1 000 mL de água igualmente entre 4 amigos. Quanto cada um recebeu?", 250, "mL", "1 000 ÷ 4 = 250 mL.", "💧"),
             N("500 mL divididos por 2 dão quantos mL?", 250, "mL", "Metade de 500 é 250.", "🥤"),
             Q("Qual embalagem cabe MAIS água?", ["Garrafão de 5 L", "Garrafinha de 500 mL", "Copo de 200 mL", "Xícara de 100 mL"], 0,
               "5 L = 5 000 mL, muito mais que 500 mL.", "🚰"),
             K("Litro ou mililitro?", {"Litro (L)": ["Galão de água", "Caixa-d'água", "Balde"],
                                       "Mililitro (mL)": ["Colher de remédio", "Xícara de café", "Copinho de iogurte"]}),
             VF("400 mL é menos que 1 litro.", True, "1 L = 1 000 mL, e 400 é menor que 1 000.", "🧴"),
             F("Qual instrumento mede capacidade?", "Copo medidor (ou jarra graduada).", "🥛"),
         ]},
        {"titulo": "Sistema monetário: cédulas e moedas do Real", "emoji": "💵", "paginas": "172-182",
         "resumo": "Sistema monetário: conjunto de moedas e cédulas de um país. O dinheiro do Brasil é o real (R$), em circulação desde 1994. "
                   "Antes do real existiram outras moedas, como cruzeiro e cruzado. A primeira Casa da Moeda foi criada em 1694, na Bahia. O pau-brasil foi a primeira mercadoria de troca. "
                   "Animais das cédulas: 2 reais tartaruga-marinha; 5 reais garça; 10 reais arara; 20 reais mico-leão-dourado; 50 reais onça-pintada; 100 reais garoupa; 200 reais lobo-guará. "
                   "Todas as notas têm a efígie da República. Moedas: 1 centavo (Pedro Álvares Cabral, não é mais fabricada), 5 centavos (Tiradentes), 10 centavos (D. Pedro I), "
                   "25 centavos (Deodoro da Fonseca), 50 centavos (Barão do Rio Branco), 1 real (efígie da República). 1 real = 100 centavos; duas moedas de 50 centavos = 1 real. "
                   "Cara é o lado com o rosto; coroa é o lado com o valor.",
         "atividades": [
             M("Cédula e seu animal", [["💵 2 reais", "🐢 Tartaruga-marinha"], ["💵 5 reais", "🦩 Garça"], ["💵 10 reais", "🦜 Arara"],
                                       ["💵 20 reais", "🐒 Mico-leão-dourado"], ["💵 50 reais", "🐆 Onça-pintada"], ["💵 200 reais", "🐺 Lobo-guará"]]),
             Q("Qual animal aparece na nota de 100 reais?", ["Garoupa", "Arara", "Onça-pintada", "Garça"], 0, "A garoupa é um peixe.", "🐟"),
             Q("Desde que ano usamos o real?", ["1994", "1822", "1694", "2010"], 0, "O real surgiu em 1994.", "📅"),
             N("Quantos centavos tem 1 real?", 100, "centavos", "1 real = 100 centavos.", "🪙"),
             N("Quantas moedas de 50 centavos formam 1 real?", 2, "moedas", "50 + 50 = 100 centavos = 1 real.", "🪙"),
             N("Quantas moedas de 25 centavos formam 1 real?", 4, "moedas", "25 + 25 + 25 + 25 = 100 centavos.", "🪙"),
             L("Moeda e personagem", [["1 centavo", "Pedro Álvares Cabral"], ["5 centavos", "Tiradentes"], ["10 centavos", "D. Pedro I"],
                                      ["25 centavos", "Deodoro da Fonseca"], ["50 centavos", "Barão do Rio Branco"]]),
             VF("A moeda de 1 centavo ainda é fabricada.", False, "Ela não é mais fabricada.", "🪙"),
             C("O lado da moeda com o rosto é a ___ e o lado com o valor é a coroa.", ["cara", "efígie", "borda"], 0),
             N("Com 4 notas de 10 reais, quanto dinheiro temos?", 40, "reais", "10 + 10 + 10 + 10 = 40.", "💵"),
             F("O que é sistema monetário?", "Conjunto de moedas e cédulas de um país, usado para pagar e medir valor.", "🏦"),
         ]},
        {"titulo": "Troco, pagamento à vista e a prazo", "emoji": "🛒", "paginas": "176-187",
         "resumo": "Troco: quando pagamos com valor maior, recebemos a diferença. Pagando 50 reais por algo de 30, o troco é 20. "
                   "Formas de pagamento: dinheiro (cédulas e moedas), cartão de débito (sai na hora da conta) ou crédito (paga depois), PIX (pelo celular, sai na hora) e boleto (papel com código de barras). "
                   "À vista: paga tudo de uma vez, muitas vezes com desconto. A prazo: paga em partes (parcelas). "
                   "Bicicleta de 1 430 reais: à vista com desconto de 130 = 1 300 reais; a prazo 10 × 143 = 1 430 reais. "
                   "Sofá por 900 reais em 3 parcelas iguais = 300 cada; outra loja 4 × 220 = 880 reais: diferença de 20 reais. "
                   "TV: loja A 1 350 à vista; loja B 5 × 246 = 1 230: a loja B é mais vantajosa.",
         "atividades": [
             N("Um livro custa 30 reais. Você paga com uma nota de 50. Qual é o troco?", 20, "reais", "50 − 30 = 20.", "📚"),
             N("Um brinquedo custa 45 reais. Você paga com 50 reais. Qual é o troco?", 5, "reais", "50 − 45 = 5.", "🧸"),
             N("Uma água custa 4 reais. Paula pagou com 5 reais. Qual é o troco?", 1, "real", "5 − 4 = 1 real (ou duas moedas de 50 centavos).", "💧"),
             N("Uma bicicleta custa 1 430 reais. À vista tem 130 de desconto. Quanto pago à vista?", 1300, "reais", "1 430 − 130 = 1 300.", "🚲"),
             N("Um sofá custa 900 reais em 3 parcelas iguais. Qual o valor de cada parcela?", 300, "reais", "900 ÷ 3 = 300.", "🛋️"),
             N("Um sofá custa 4 parcelas de 220 reais. Qual é o preço total?", 880, "reais", "4 × 220 = 880.", "🛋️"),
             N("Quantas notas de 10 reais são necessárias para pagar um quebra-cabeça de 45 reais?", 5, "notas",
               "4 notas = 40 (não dá). 5 notas = 50, e sobra troco de 5.", "🧩"),
             L("Forma de pagamento", [["PIX", "Pelo celular, o dinheiro sai na hora"], ["Cartão de crédito", "O pagamento é feito depois"],
                                      ["Boleto", "Papel com código de barras"], ["Dinheiro", "Cédulas e moedas"]]),
             K("À vista ou a prazo?", {"À vista": ["Pagar tudo de uma vez", "Pode ter desconto"],
                                       "A prazo": ["Pagar em parcelas", "10 × 143 reais"]}),
             F("O que é troco?", "É o valor que recebemos de volta quando pagamos com mais dinheiro do que o preço.", "💰"),
         ]},
        {"titulo": "Dobro, triplo e divisão", "emoji": "✖️", "paginas": "105, 112, 118",
         "resumo": "Dobro é duas vezes a quantidade (multiplicar por 2): dobro de 4 = 8. Triplo é três vezes (multiplicar por 3): triplo de 4 = 12. "
                   "Dividir é repartir o todo em partes iguais. 30 sanduíches em 6 bandejas = 5 em cada. 2 L em 4 partes iguais = 500 mL cada.",
         "atividades": [
             N("Qual é o dobro de 4?", 8, "", "2 × 4 = 8.", "✌️"),
             N("Qual é o triplo de 4?", 12, "", "3 × 4 = 12.", "🍎"),
             N("Qual é o dobro de 15?", 30, "", "2 × 15 = 30.", "⚽"),
             N("Maria fez 30 sanduíches e quer dividir igualmente em 6 bandejas. Quantos em cada?", 5, "sanduíches", "30 ÷ 6 = 5.", "🥪"),
             N("Flávio dividiu 2 litros (2 000 mL) em 4 partes iguais. Quantos mL em cada parte?", 500, "mL", "2 000 ÷ 4 = 500.", "🧴"),
             C("Dobro significa ___ vezes a quantidade.", ["duas", "três", "quatro"], 0),
             C("Triplo significa ___ vezes a quantidade.", ["três", "duas", "dez"], 0),
             F("Qual o símbolo da divisão?", "÷", "➗"),
         ]},
    ]},
    # =====================================================================
    {"materia": "Português", "titulo": "Prova de Português", "data": "2026-11-24", "conteudos": [
        {"titulo": "Pronomes demonstrativos", "emoji": "👉", "paginas": "158-162",
         "resumo": "Pronomes substituem ou acompanham substantivos e evitam repetir palavras. Pronomes demonstrativos indicam de que ou de quem se fala, mostrando a posição. "
                   "Este, esta, isto: perto de quem fala (1ª pessoa). Esse, essa, isso: perto de quem ouve (2ª pessoa). Aquele, aquela, aquilo: longe dos dois (3ª pessoa). "
                   "Exemplo: 'Este peixe aqui é pequeno'; 'Esse peixe aí é grande'; 'Aquele peixe lá é enorme'. "
                   "Texto da mandioca: 'A verdade é esta: várias regiões do Brasil utilizam a raiz em pratos típicos' — 'esta' se refere a algo que vai ser dito.",
         "atividades": [
             K("Onde está a coisa?", {"Perto de quem fala": ["este", "esta", "isto"], "Perto de quem ouve": ["esse", "essa", "isso"],
                                      "Longe dos dois": ["aquele", "aquela", "aquilo"]}),
             C("(Segurando o livro) — ___ livro fala sobre os indígenas.", ["Este", "Aquele", "Esse"], 0,
               "O livro está com quem fala: usamos ESTE."),
             C("(Apontando para longe) — ___ árvore lá no alto é a mais antiga da floresta.", ["Aquela", "Esta", "Essa"], 0,
               "Longe de quem fala e de quem ouve: AQUELA."),
             C("— O que é ___ que você tem na mão?", ["isso", "isto", "aquilo"], 0, "Está perto de quem ouve: ISSO."),
             Q("Os pronomes demonstrativos servem para…", ["indicar de que ou de quem se fala", "dar ordem às frases",
               "imitar sons", "contar quantidades"], 0, "", "👉"),
             VF("'Aquilo' indica algo longe de quem fala e de quem ouve.", True, "", "🔭"),
             VF("'Esta' é usado para algo perto de quem ouve.", False, "Perto de quem ouve usamos 'essa'. 'Esta' é perto de quem fala.", "🙋"),
             M("Pronome e posição", [["este 🙋", "perto de mim"], ["esse 🫵", "perto de você"], ["aquele 🔭", "longe de nós"],
                                     ["isto", "1ª pessoa"], ["isso", "2ª pessoa"], ["aquilo", "3ª pessoa"]]),
             F("Para que servem os pronomes?", "Para substituir ou acompanhar substantivos, evitando repetições.", "🔁"),
         ]},
        {"titulo": "Onomatopeias e histórias em quadrinhos", "emoji": "💥", "paginas": "163-165",
         "resumo": "Histórias em quadrinhos (HQs) misturam textos e imagens em quadrinhos. Usam balões de fala, de pensamento e de grito, tamanhos e cores de letras para mostrar emoções. "
                   "Onomatopeias são palavras que imitam sons de objetos, fenômenos da natureza, animais ou pessoas. Exemplos: TRIM (telefone), BOOM (explosão), PIU-PIU (passarinho), "
                   "BI-BI (buzina), TOC-TOC (bater na porta), ZZZ (sono), AU-AU (cachorro), ATCHIM (espirro), TIC-TAC (relógio), PLUFT/POF (algo caindo). "
                   "Letras repetidas como 'rááápidos' indicam que a palavra é dita de forma alongada, com ênfase.",
         "atividades": [
             L("Que som é esse?", [["PIU-PIU", "🐦 Passarinho"], ["BI-BI", "🚗 Buzina"], ["TOC-TOC", "🚪 Batida na porta"],
                                   ["ZZZ", "😴 Sono"], ["BOOM", "💥 Explosão"]]),
             M("Encontre a onomatopeia", [["🐶", "AU-AU"], ["🐱", "MIAU"], ["⏰", "TIC-TAC"], ["🤧", "ATCHIM"], ["☎️", "TRIM-TRIM"], ["🐸", "CROAC"]]),
             Q("O que é onomatopeia?", ["Palavra que imita um som", "Palavra que indica lugar", "Palavra que dá qualidade",
               "O título da história"], 0, "", "🔊"),
             Q("Na HQ, a palavra escrita 'rááápidos' indica que…", ["a palavra é dita de forma alongada, com ênfase",
               "houve erro de escrita", "o personagem está dormindo", "é uma pergunta"], 0, "", "🏃"),
             VF("Nas HQs, o tamanho e a cor das letras podem mostrar emoções, como raiva ou susto.", True, "", "😱"),
             C("A palavra 'BOOM!' num balão representa o barulho de uma ___.", ["explosão", "chuva fraquinha", "risada"], 0),
             F("Dê 3 exemplos de onomatopeias.", "Piu-piu, bi-bi, toc-toc (também: au-au, tic-tac, boom).", "💥"),
         ]},
        {"titulo": "Adjetivos e concordância", "emoji": "🌈", "paginas": "228-230",
         "resumo": "Adjetivos são palavras que dão características aos substantivos. Ex.: Mar (substantivo) → bonito, agitado, enorme e azul (adjetivos). "
                   "Os adjetivos concordam com o substantivo em gênero (masculino/feminino) e número (singular/plural): 'muitos peixes coloridos', 'a bola colorida e redonda'. "
                   "Também podem variar em grau: normal, aumentativo e diminutivo. "
                   "Exemplos: 'A baleia é muito grande e pesada'; 'A água do mar é salgada'; 'A areia da praia pode ser fina ou grossa'.",
         "atividades": [
             Q("Na frase 'O mar é azul e agitado', quais palavras são adjetivos?", ["azul e agitado", "mar e é", "o e mar", "é e azul"], 0,
               "Azul e agitado dão características ao mar.", "🌊"),
             C("No mar existem muitos peixes ___.", ["coloridos", "colorida", "colorido"], 0, "Peixes é masculino e plural: coloridos."),
             C("A bola é ___ e redonda.", ["colorida", "coloridos", "coloridas"], 0, "Bola é feminino e singular: colorida."),
             C("As baleias são muito ___.", ["grandes", "grande", "grandezinho"], 0, "Baleias está no plural: grandes."),
             K("Substantivo ou adjetivo?", {"Substantivo": ["mar", "baleia", "areia", "peixe"],
                                            "Adjetivo": ["salgada", "enorme", "fina", "colorido"]}),
             VF("Adjetivo é a palavra que dá característica ao substantivo.", True, "", "🌈"),
             Q("Qual adjetivo combina com 'A água do mar é…'?", ["salgada", "salgados", "salgado", "salgadas"], 0, "Água: feminino singular.", "🧂"),
             F("O que é um adjetivo?", "Palavra que dá características ao substantivo (ex.: mar azul).", "🎨"),
         ]},
        {"titulo": "Gênero diário (pessoal e de viagem)", "emoji": "📔", "paginas": "223-227, 231",
         "resumo": "No diário registramos acontecimentos especiais do dia a dia, como se fosse um amigo íntimo ('Querido diário', 'Meu diário'). "
                   "Características: escrito em 1ª pessoa (eu, nós); estrutura com data, saudação, desenvolvimento e despedida; relatos de experiências vividas, viagens, desejos, desabafos e sonhos; "
                   "expressa sentimentos. O diário de viagem registra passeios e lugares visitados. "
                   "No livro, Mariana escreve sobre o mar e a festa-surpresa de aniversário; ela não conseguia dormir de ansiedade. "
                   "NÃO são características do diário: ser escrito em 3ª pessoa, ter a função de informar a sociedade (isso é notícia), ser composto de histórias imaginárias.",
         "atividades": [
             O("Monte a estrutura do diário", ["Data", "Saudação (Querido diário)", "Desenvolvimento (o que aconteceu)", "Despedida"],
               "Todo diário segue essa ordem."),
             K("É do diário ou não?", {"É do diário": ["Escrito em 1ª pessoa", "Tem data e saudação", "Relata experiências vividas", "Mostra sentimentos"],
                                       "Não é do diário": ["Escrito em 3ª pessoa", "Informa a sociedade, como notícia", "Só histórias imaginárias"]}),
             Q("Qual frase poderia começar um diário?", ["Querido diário, hoje fui à praia!", "Era uma vez um dragão…",
               "Notícia: chuva forte atinge a cidade", "Ingredientes: 2 ovos e farinha"], 0, "", "📔"),
             VF("O diário é escrito em 1ª pessoa.", True, "Quem escreve conta o que viveu: eu fui, eu senti…", "✍️"),
             VF("O diário serve para informar a população sobre fatos da cidade.", False, "Isso é função da notícia.", "📰"),
             Q("Por que Mariana não conseguia dormir?", ["Estava ansiosa para ver o mar", "Estava doente", "Tinha prova", "Perdeu o diário"], 0,
               "Ela estava ansiosa e curiosa para conhecer o mar.", "🌊"),
             F("O que é um diário de viagem?", "Um diário em que registramos passeios, lugares visitados e o que sentimos.", "🧳"),
         ]},
    ]},
    # =====================================================================
    {"materia": "Ciências", "titulo": "Prova de Ciências", "data": "2026-11-25", "conteudos": [
        {"titulo": "O solo: formação e composição", "emoji": "🪨", "paginas": "72-75",
         "resumo": "O solo é a camada superficial do planeta, onde pisamos, plantamos e construímos. É formado ao longo de milhares de anos pelo desgaste das rochas, pela ação do calor, da chuva, do vento e dos seres vivos. "
                   "Forma-se em camadas chamadas horizontes. É composto de minerais (pedaços de rochas, areia, argila), matéria orgânica (restos de plantas e animais), água e ar. "
                   "O húmus é rico em nutrientes para as plantas. Nas cidades o solo fica coberto por asfalto e pisos, a água da chuva não é absorvida e por isso existem bueiros para evitar inundações. "
                   "O Museu de Solos do Rio Grande do Sul é dedicado à ciência do solo.",
         "atividades": [
             Q("Como o solo é formado?", ["Pelo desgaste das rochas ao longo de milhares de anos", "Em poucos dias pela chuva",
               "Pelas fábricas", "Pelo asfalto das ruas"], 0, "Calor, chuva, vento e seres vivos desgastam as rochas por milhares de anos.", "🪨"),
             C("As camadas do solo são chamadas de ___.", ["horizontes", "rochas", "raízes"], 0),
             K("O que faz parte do solo?", {"Faz parte do solo": ["Areia e argila", "Restos de plantas", "Água", "Ar"],
                                            "Não faz parte": ["Plástico", "Asfalto"]}),
             VF("Nas cidades, o asfalto impede a água da chuva de ser absorvida pelo solo.", True,
                "Por isso existem bueiros, que ajudam a evitar inundações.", "🌧️"),
             Q("O que é a matéria orgânica do solo?", ["Restos de plantas e animais", "Pedaços de plástico", "Asfalto", "Vidro"], 0, "", "🍂"),
             O("Como o solo se forma", ["Rocha inteira", "Calor, chuva e vento desgastam a rocha", "A rocha vira pedacinhos",
                                        "Restos de seres vivos se misturam", "Forma-se o solo"]),
             F("O que é o solo?", "A camada superficial do planeta, formada por minerais, matéria orgânica, água e ar.", "🌍"),
         ]},
        {"titulo": "Usos do solo, erosão e proteção", "emoji": "🚜", "paginas": "73, 211-214",
         "resumo": "Usamos o solo para cultivar alimentos (agricultura), como pasto para animais, para retirar materiais de construção (argila para telhas e tijolos) e para construir casas. "
                   "Nem todo solo serve para plantar: precisa de nutrientes, água, sol e temperatura adequada. "
                   "Monocultura (plantar um só tipo de vegetal) empobrece o solo. Rotação de culturas: variar os tipos de plantas após cada colheita, enriquecendo o solo. "
                   "Erosão: quando a chuva ou o vento levam o solo descoberto para rios e córregos. Raízes de árvores e gramíneas protegem o solo. "
                   "Agrotóxicos em excesso prejudicam o ambiente, animais e pessoas. Para proteger o solo: reduzir produtos industrializados, separar o lixo e reciclar, usar fertilizante orgânico e não jogar lixo no chão. "
                   "Uso sustentável: práticas que preservam o solo a longo prazo.",
         "atividades": [
             L("Ligue o uso do solo", [["🌽 Plantação", "Cultivo de alimentos"], ["🐄 Gado no campo", "Pasto para animais"],
                                       ["🧱 Telhas e tijolos", "Materiais para construção"]]),
             Q("O que é rotação de culturas?", ["Variar o tipo de planta após cada colheita", "Plantar sempre a mesma coisa",
               "Girar a terra com trator", "Usar muito agrotóxico"], 0, "Variar as plantas enriquece o solo.", "🔄"),
             Q("O que é erosão?", ["Quando chuva ou vento levam o solo descoberto", "Quando o solo fica mais forte",
               "Quando plantamos árvores", "Quando chove pouco"], 0, "", "🌪️"),
             VF("Plantar árvores e gramíneas ajuda a proteger o solo da erosão.", True, "As raízes seguram o solo.", "🌳"),
             VF("Plantar sempre o mesmo tipo de vegetal (monocultura) deixa o solo mais rico.", False, "A monocultura empobrece o solo.", "🌾"),
             K("Protege ou prejudica o solo?", {"Protege": ["Separar o lixo", "Fertilizante orgânico", "Plantar árvores", "Rotação de culturas"],
                                                "Prejudica": ["Jogar lixo no chão", "Desmatar", "Agrotóxico em excesso"]}),
             F("O que é monocultura?", "Plantar um só tipo de vegetal no mesmo local. Empobrece o solo.", "🌾"),
         ]},
        {"titulo": "A água no planeta e a água potável", "emoji": "🌊", "paginas": "142",
         "resumo": "A maior parte da água do planeta é salgada e está nos mares e oceanos. A água doce é pouca, e boa parte dela está congelada (geleiras e neve) ou embaixo do solo (águas subterrâneas). "
                   "Também há água doce em rios, lagos, na atmosfera e nos seres vivos. Nem toda água doce é potável: água potável é limpa, livre de poluição e contaminação, própria para beber. "
                   "Beber água contaminada por microrganismos, como bactérias, pode causar doenças.",
         "atividades": [
             Q("Onde está a MAIOR parte da água do planeta?", ["Nos mares e oceanos (salgada)", "Nos rios", "Nas geleiras", "Nas nuvens"], 0, "", "🌊"),
             Q("O que é água potável?", ["Água limpa e própria para beber", "Qualquer água de rio", "Água do mar", "Água da chuva no chão"], 0, "", "🚰"),
             VF("Toda água doce pode ser bebida sem perigo.", False, "Só a água potável: limpa e sem contaminação.", "⚠️"),
             VF("Beber água contaminada por bactérias pode causar doenças.", True, "", "🦠"),
             K("Água doce ou salgada?", {"Salgada": ["Mar", "Oceano"], "Doce": ["Rio", "Lago", "Geleira", "Água subterrânea"]}),
             F("Onde está boa parte da água doce?", "Congelada nas geleiras e embaixo do solo (águas subterrâneas).", "🧊"),
         ]},
        {"titulo": "Ciclo da água e estados físicos", "emoji": "🌦️", "paginas": "143-146",
         "resumo": "A água pode estar nos estados sólido (gelo, neve), líquido (rios, chuva) e gasoso (vapor). "
                   "Ciclo da água: 1) Evaporação: a energia do Sol aquece a água líquida, que vira vapor (gasoso) e sobe para a atmosfera. "
                   "2) Condensação: o vapor esfria e forma gotinhas que formam as nuvens. 3) Precipitação: as gotas ficam pesadas e caem como chuva (ou neve/granizo, no estado sólido). "
                   "4) Infiltração e escoamento: a água penetra no solo ou escorre pela superfície até rios e mares, e o ciclo recomeça. "
                   "A diminuição das chuvas pode causar seca em rios e lagos, prejudicando populações como os ribeirinhos da Amazônia.",
         "atividades": [
             O("Monte o ciclo da água", ["☀️ Evaporação", "☁️ Condensação", "🌧️ Precipitação", "🏞️ Infiltração e escoamento"],
               "O Sol aquece, o vapor vira nuvem, a chuva cai e a água volta para o solo e os rios."),
             L("Estado físico da água", [["🧊 Gelo", "Sólido"], ["💧 Água do rio", "Líquido"], ["♨️ Vapor", "Gasoso"]]),
             Q("Como se chama a etapa em que a água vira vapor por causa do calor do Sol?", ["Evaporação", "Precipitação", "Infiltração", "Condensação"], 0, "", "☀️"),
             Q("Quando o vapor esfria e forma as nuvens, acontece a…", ["condensação", "evaporação", "infiltração", "erosão"], 0, "", "☁️"),
             Q("A chuva caindo das nuvens é chamada de…", ["precipitação", "evaporação", "condensação", "escoamento"], 0, "", "🌧️"),
             VF("Neve e granizo são a água no estado sólido.", True, "", "❄️"),
             M("Etapa e símbolo", [["☀️", "Evaporação"], ["☁️", "Condensação"], ["🌧️", "Precipitação"], ["🕳️", "Infiltração"]]),
             F("O que é o ciclo da água?", "O movimento da água na natureza: evaporação, condensação, precipitação e infiltração.", "🔁"),
         ]},
        {"titulo": "Alimentos: cadeia produtiva e alimentação saudável", "emoji": "🥗", "paginas": "211, 282-283",
         "resumo": "Cadeia produtiva: agricultura e pecuária (frutas, hortaliças, carnes, ovos, leite) → indústria (embala ou transforma) → distribuição (caminhões, barcos) → consumidores (supermercados, feiras). "
                   "Alimentos in natura: sem processo (espiga de milho, frutas). Processados: passaram por alguma transformação (milho em conserva). "
                   "Ultraprocessados: muitos ingredientes e aditivos (salgadinho de pacote, balas, sucos de pó, biscoito recheado) — devem ser evitados, pois o excesso de gordura, açúcar e sal prejudica a saúde. "
                   "Nutrientes: proteínas (crescimento — carne, ovo, feijão); carboidratos (energia — arroz, pão, batata, mandioca); vitaminas e minerais (frutas e folhas — defesa do corpo; minerais para ossos e dentes); "
                   "fibras (digestão); gorduras em pequena quantidade (óleos, azeite, castanhas). Prato saudável: proteínas, carboidratos, legumes e verduras.",
         "atividades": [
             O("Caminho do alimento até sua casa", ["🚜 Agricultura e pecuária", "🏭 Indústria", "🚚 Distribuição", "🛒 Consumidores"]),
             K("Qual é o tipo de alimento?", {"In natura": ["Espiga de milho", "Banana", "Ovo"], "Processado": ["Milho em conserva", "Queijo"],
                                              "Ultraprocessado": ["Salgadinho de pacote", "Refrigerante", "Biscoito recheado"]}),
             L("Nutriente e função", [["💪 Proteínas", "Ajudam no crescimento"], ["⚡ Carboidratos", "Dão energia"],
                                      ["🛡️ Vitaminas", "Defesa do corpo"], ["🦷 Minerais", "Ossos e dentes"], ["🌀 Fibras", "Ajudam a digestão"]]),
             Q("Qual alimento é rico em carboidratos (energia)?", ["Mandioca", "Alface", "Ovo", "Água"], 0, "Mandioca, arroz, pão e batata dão energia.", "🥔"),
             Q("Qual alimento devemos evitar?", ["Salgadinho de pacote", "Feijão", "Maçã", "Arroz"], 0, "Ultraprocessados têm muito sal, açúcar e gordura.", "🚫"),
             VF("Um prato saudável tem proteínas, carboidratos, legumes e verduras.", True, "", "🍽️"),
             VF("Devemos comer muita gordura todos os dias.", False, "O corpo precisa de gordura, mas em pequena quantidade.", "🫒"),
             F("O que são alimentos ultraprocessados?", "Alimentos com muitos ingredientes e aditivos, como salgadinhos e refrigerantes. Devemos evitar.", "🍟"),
         ]},
        {"titulo": "Plantas: usos e partes", "emoji": "🌿", "paginas": "158, 212",
         "resumo": "Além da alimentação, as plantas são usadas em produtos de limpeza, cosméticos (cremes, sabonetes, xampus — ex.: óleo de andiroba) e medicamentos (plantas medicinais). "
                   "Algumas emprestam seu cheiro: lavanda, eucalipto e hortelã (aromatizantes). Das árvores tiramos madeira para construir casas e móveis. "
                   "O caqui é um fruto. A cientista chinesa Tu Youyou ganhou o prêmio Nobel ao estudar plantas e encontrar um remédio para a malária. "
                   "A mandioca é uma raiz muito importante para os povos indígenas; com ela se faz beiju e farinha. O açaí é o fruto do açaizeiro, planta da Amazônia. "
                   "Os indígenas nos ensinaram a usar mandioca, cará, batata-doce, milho, açaí, bacaba e cupuaçu.",
         "atividades": [
             L("Para que usamos a planta?", [["🌲 Madeira", "Construir casas e móveis"], ["🌿 Plantas medicinais", "Remédios"],
                                             ["🧴 Andiroba", "Cosméticos"], ["💜 Lavanda", "Dar cheiro (aromatizante)"]]),
             Q("O caqui é qual parte da planta?", ["Fruto", "Raiz", "Folha", "Caule"], 0, "", "🍅"),
             Q("A mandioca é qual parte da planta?", ["Raiz", "Fruto", "Flor", "Folha"], 0, "Com a raiz da mandioca se faz farinha e beiju.", "🥔"),
             VF("Plantas medicinais têm substâncias que ajudam a tratar doenças.", True, "", "🌿"),
             VF("O açaí é o fruto de uma planta da Amazônia.", True, "Ele vem do açaizeiro.", "🫐"),
             C("A cientista Tu Youyou encontrou um remédio para a ___ estudando plantas.", ["malária", "gripe", "cárie"], 0),
             F("Cite 3 usos das plantas além da alimentação.", "Remédios, cosméticos e madeira para construção (também produtos de limpeza e aromas).", "🌱"),
         ]},
    ]},
    # =====================================================================
    {"materia": "Geografia e História", "titulo": "Prova de Geografia e História", "data": "2026-11-26", "conteudos": [
        {"titulo": "Trabalho e atividades econômicas do município", "emoji": "👷", "paginas": "125-126, 201-203",
         "resumo": "Trabalho é toda atividade realizada para atender às necessidades humanas, produzir mercadorias ou oferecer serviços. "
                   "Trabalho remunerado: a pessoa recebe pagamento (médico, professor, pintor). Não remunerado: sem pagamento (cuidar da própria casa, ajudar a comunidade, trabalho voluntário). "
                   "O trabalho é fundamental para formar os municípios: construção de ruas, avenidas, prédios, praças e meios de transporte. "
                   "Atividades econômicas: comércio (venda de produtos: farmácias, padarias, restaurantes); indústria (fábricas de eletrodomésticos, carros, brinquedos); "
                   "agricultura (arroz, feijão, milho, frutas); pecuária (criação de animais para leite, carne, couro e ovos); agroindústria (transforma produtos agrícolas em sucos, queijos e doces); turismo. "
                   "Economia: atividades de produção, distribuição e consumo de mercadorias. O campo e a cidade dependem um do outro.",
         "atividades": [
             K("Remunerado ou não remunerado?", {"Remunerado": ["Médico no hospital", "Professora na escola", "Pintor de paredes"],
                                                 "Não remunerado": ["Cuidar da própria casa", "Voluntário no hospital", "Ajudar a comunidade"]}),
             L("Atividade econômica", [["🏪 Vender pães e remédios", "Comércio"], ["🏭 Fabricar carros", "Indústria"],
                                       ["🌾 Plantar arroz e feijão", "Agricultura"], ["🐄 Criar gado", "Pecuária"], ["🧀 Fazer queijo e suco", "Agroindústria"]]),
             Q("O que é trabalho remunerado?", ["Trabalho em que a pessoa recebe pagamento", "Trabalho sem pagamento",
               "Brincar no parque", "Trabalho só de crianças"], 0, "", "💰"),
             Q("A agroindústria transforma produtos agrícolas em…", ["sucos, queijos e doces", "carros e celulares", "roupas de plástico", "casas"], 0, "", "🧃"),
             VF("O campo e a cidade dependem um do outro.", True, "O campo produz alimentos; a cidade produz máquinas, roupas e serviços.", "🤝"),
             C("A criação de animais para obter leite, carne e ovos se chama ___.", ["pecuária", "comércio", "turismo"], 0),
             F("O que é economia?", "O conjunto de atividades de produção, distribuição e consumo de mercadorias.", "📊"),
         ]},
        {"titulo": "O trabalho muda com o tempo", "emoji": "⏳", "paginas": "124-128",
         "resumo": "Os lugares se transformam pelo trabalho humano e o trabalho também muda com o passar do tempo. "
                   "Exemplo: o leiteiro que entregava leite em 1930 e o motoboy que entrega comida em 2024. O leite passou a ser industrializado e embalado. "
                   "Algumas profissões deixaram de existir: o acendedor de lampiões acendia a iluminação a gás das ruas; foi extinta porque chegou a energia elétrica. "
                   "Na música 'Lampião de gás', aparecem o carvoeiro (vendia carvão) e o vassoureiro (vendia vassouras) com seu pregão (anúncio feito em voz alta). "
                   "Hoje há mais tecnologia; antes havia mais pessoas trabalhando no lugar das máquinas. A Estação da Luz, em São Paulo, inaugurada em 1901, levava café do interior até o Porto de Santos.",
         "atividades": [
             Q("Por que a profissão de acendedor de lampiões acabou?", ["Por causa da energia elétrica", "Porque faltou gás",
               "Porque proibiram", "Porque ninguém gostava"], 0, "A iluminação elétrica substituiu os lampiões a gás.", "💡"),
             L("Palavras da música 'Lampião de gás'", [["Carvoeiro", "Vendia carvão"], ["Vassoureiro", "Vendia vassouras"],
                                                       ["Pregão", "Anúncio em voz alta"]]),
             O("Do passado para o presente: entregas", ["🐴 Leiteiro com carroça (1930)", "🚚 Caminhão de entregas", "🏍️ Motoboy de aplicativo (2024)"]),
             VF("Hoje usamos mais máquinas e tecnologia no trabalho do que antigamente.", True, "", "🤖"),
             K("Passado ou presente?", {"Passado": ["Acendedor de lampiões", "Leiteiro de porta em porta", "Bonde puxado"],
                                        "Presente": ["Motoboy de aplicativo", "Pagamento por PIX", "Fábrica com robôs"]}),
             F("Como era a iluminação das ruas antigamente?", "Com lampiões a gás, acesos pelo acendedor de lampiões.", "🏮"),
         ]},
        {"titulo": "Direitos das crianças e trabalho infantil", "emoji": "🧒", "paginas": "195-198",
         "resumo": "O ECA (Estatuto da Criança e do Adolescente) reúne os direitos das crianças e adolescentes do Brasil. Foi publicado em 13 de julho de 1990, dois anos depois da Constituição. "
                   "Criança: até 12 anos. Adolescente: entre 12 e 18 anos. Direitos: educação, saúde, moradia, lazer, brincar, amor e compreensão, cuidados de uma família. "
                   "A Declaração Universal dos Direitos da Criança foi adotada em 1959. "
                   "Trabalho infantil é proibido: prejudica a infância, impede de estudar, brincar e descansar, e afeta a saúde. Adolescentes a partir de 14 anos só podem trabalhar como aprendizes, estudando. "
                   "12 de junho: Dia Mundial contra o Trabalho Infantil ('Cartão vermelho ao trabalho infantil'). A fiscalização ajudou a reduzir o trabalho infantil em 2023. "
                   "Lugar de criança é na escola! O ECA em tirinhas é um livro gratuito da Câmara dos Deputados.",
         "atividades": [
             Q("O que significa ECA?", ["Estatuto da Criança e do Adolescente", "Escola de Crianças Animadas",
               "Estudo de Contas e Adição", "Espaço de Cultura e Arte"], 0, "", "📜"),
             Q("Em que ano o ECA foi publicado?", ["1990", "1959", "2023", "1822"], 0, "13 de julho de 1990.", "📅"),
             C("Toda criança tem direito a ___ e se divertir.", ["brincar", "trabalhar", "dirigir"], 0),
             C("O Estatuto da Criança e do Adolescente diz que as crianças não podem ___.", ["trabalhar", "estudar", "brincar"], 0),
             VF("O trabalho infantil prejudica a infância e impede a criança de estudar e brincar.", True, "", "🟥"),
             VF("Adolescente tem entre 12 e 18 anos.", True, "", "🧑"),
             L("Direito e exemplo", [["❤️ Amor e compreensão", "Abraço da família"], ["🏠 Moradia", "Ter uma casa"],
                                     ["🎨 Lazer", "Brincar no museu e no parque"], ["📚 Educação", "Ir à escola"]]),
             Q("Qual dia é o Dia Mundial contra o Trabalho Infantil?", ["12 de junho", "12 de outubro", "1º de maio", "25 de dezembro"], 0, "", "🟥"),
             F("Qual é o lugar de criança?", "Na escola! Estudando, brincando e se desenvolvendo com segurança.", "🏫"),
         ]},
        {"titulo": "Desemprego", "emoji": "📉", "paginas": "201-203",
         "resumo": "Desemprego é a situação de uma pessoa que não está trabalhando no momento, ou seja, que procura emprego e não encontra. "
                   "Causas: problemas econômicos, conflitos ou guerras, desastres naturais e mudanças tecnológicas. "
                   "Consequências: a renda das famílias diminui (falta salário para se sustentar), afeta a saúde física e mental e o acesso a necessidades básicas. Afeta toda a comunidade.",
         "atividades": [
             Q("O que é desemprego?", ["Situação de quem não está trabalhando no momento", "Nome de uma profissão da indústria",
               "Uma atividade econômica dos municípios", "Tirar férias"], 0, "", "📉"),
             K("Causa ou consequência do desemprego?", {"Causa": ["Problemas econômicos", "Desastres naturais", "Mudanças tecnológicas"],
                                                        "Consequência": ["Falta de salário", "Renda da família diminui", "Afeta a saúde"]}),
             VF("O desemprego afeta toda a comunidade, não só a pessoa desempregada.", True, "", "🏘️"),
             F("Cite uma consequência do desemprego.", "Falta de salário para sustentar a família (também afeta a saúde).", "💸"),
         ]},
        {"titulo": "Espaços de lazer: públicos e privados", "emoji": "🎡", "paginas": "266-268",
         "resumo": "Lazer são atividades agradáveis e divertidas. Os espaços de lazer proporcionam diversão, bem-estar físico e mental, descanso, criatividade e convívio com família e amigos. "
                   "Espaços públicos: abertos a todos, mantidos pelo governo (praças, parques, praias, quadras, ruas de lazer). "
                   "Espaços privados: pertencem a uma pessoa ou empresa (clubes, cinemas, shoppings, teatros, hotéis-fazenda). "
                   "Ecoturismo: atividades de lazer na natureza, respeitando o meio ambiente. Devemos respeitar as regras de convivência e cuidar dos espaços. "
                   "Nas festas de rua conhecemos a diversidade de pessoas e culturas.",
         "atividades": [
             K("Público ou privado?", {"Público": ["Praça", "Parque", "Praia", "Quadra do bairro"],
                                       "Privado": ["Shopping", "Cinema", "Clube", "Teatro particular"]}),
             Q("Qual é um espaço de lazer PÚBLICO?", ["Parque da cidade", "Shopping", "Cinema", "Clube"], 0, "Aberto a todos.", "🌳"),
             VF("Nos espaços de lazer devemos respeitar as regras e não danificar os brinquedos.", True, "", "🛝"),
             C("Atividades de lazer na natureza, respeitando o meio ambiente, chamam-se ___.", ["ecoturismo", "consumismo", "comércio"], 0),
             F("Diferença entre espaço público e privado?", "Público é aberto a todos; privado pertence a uma pessoa ou empresa.", "🔑"),
         ]},
        {"titulo": "Consumo, consumismo, resíduos e reciclagem", "emoji": "♻️", "paginas": "268-275",
         "resumo": "Consumo é comprar o que é necessário (alimentos, roupas, remédios) e também para o lazer. Consumismo é consumir de forma exagerada, além das necessidades, achando que a felicidade depende disso. "
                   "As propagandas tentam nos convencer a comprar. Consumo consciente e sustentável: atender às necessidades sem prejudicar as gerações futuras. "
                   "Resíduos: industrial (fabricação: metal, borracha, plástico), hospitalar (seringas, agulhas, curativos — podem ser tóxicos), eletrônico (celulares, computadores, pilhas e baterias), "
                   "verde (poda: galhos, grama, folhas), agrícola (rações, embalagens, fertilizantes). "
                   "Coleta seletiva — cores: azul papel, vermelho plástico, amarelo metal, verde vidro, marrom orgânico. "
                   "Reciclagem: um objeto descartado se transforma em outro produto ou em matéria-prima. Os coletores de lixo são muito importantes. "
                   "5Rs: Repensar, Recusar, Reduzir, Reutilizar e Reciclar. O 'cemitério de roupas' no deserto do Atacama mostra o problema do consumismo.",
         "atividades": [
             L("Cor da lixeira", [["🔵 Azul", "Papel"], ["🔴 Vermelho", "Plástico"], ["🟡 Amarelo", "Metal"], ["🟢 Verde", "Vidro"], ["🟤 Marrom", "Orgânico"]]),
             K("Em qual lixeira?", {"🔵 Papel": ["Jornal", "Caixa de papelão"], "🔴 Plástico": ["Garrafa PET", "Sacolinha"],
                                    "🟡 Metal": ["Lata de refrigerante", "Tampinha de metal"]}),
             M("Os 5Rs", [["Repensar", "🤔"], ["Recusar", "✋"], ["Reduzir", "📉"], ["Reutilizar", "🔁"], ["Reciclar", "♻️"]]),
             L("Tipo de resíduo", [["📱 Celular e pilhas", "Eletrônico"], ["💉 Seringas e agulhas", "Hospitalar"], ["🍂 Galhos e grama", "Verde"],
                                   ["🏭 Restos de fábrica", "Industrial"], ["🚜 Embalagens de ração", "Agrícola"]]),
             Q("Qual é a diferença entre consumo e consumismo?", ["Consumismo é comprar além do necessário", "São a mesma coisa",
               "Consumo é proibido", "Consumismo é economizar"], 0, "", "🛍️"),
             Q("O que é reciclagem?", ["Transformar um objeto descartado em outro produto", "Jogar tudo no mesmo saco",
               "Queimar o lixo", "Comprar coisas novas"], 0, "", "♻️"),
             VF("As propagandas tentam nos convencer a comprar coisas que às vezes não precisamos.", True, "", "📺"),
             VF("A lixeira azul é para vidro.", False, "Azul é para papel. Vidro vai na verde.", "🗑️"),
             F("O que é consumo sustentável?", "Consumir só o necessário, preservando os recursos para as gerações futuras.", "🌎"),
         ]},
        {"titulo": "Recursos naturais e a degradação do solo", "emoji": "🌍", "paginas": "62-63",
         "resumo": "O solo é um recurso natural formado pela camada mais externa da Terra; dele tiramos ferro, petróleo, ouro e prata, e nele plantamos alimentos. "
                   "Recursos renováveis não têm fim, como a energia do Sol e dos ventos. Recursos não renováveis podem se esgotar (exaurir) em algum momento, como o carvão mineral e o diamante. "
                   "O solo é um recurso não renovável: sua exploração excessiva leva ao esgotamento. "
                   "Problemas: lixo descartado de forma errada, agroquímicos (produtos para controlar pragas), desmatamento (remover matas e florestas) — o solo fica exposto à erosão, enchentes e deslizamentos. "
                   "Reflorestamento: plantio de árvores em locais desmatados. Degradação: ação de estragar, destruir ou perder a qualidade.",
         "atividades": [
             K("Renovável ou não renovável?", {"Renovável": ["☀️ Luz do Sol", "🌬️ Vento", "🍎 Frutas e plantas"],
                                               "Não renovável": ["💎 Diamante", "⚫ Carvão mineral", "🛢️ Petróleo"]}),
             Q("O que é desmatamento?", ["Remover matas e florestas", "Plantar árvores", "Limpar o rio", "Separar o lixo"], 0, "", "🪓"),
             Q("O que é reflorestamento?", ["Plantar árvores em locais desmatados", "Cortar árvores", "Construir prédios", "Asfaltar ruas"], 0, "", "🌳"),
             VF("O solo desmatado fica mais exposto à erosão e a deslizamentos.", True, "", "⛰️"),
             C("Degradação significa a ação de estragar, destruir ou perder a ___.", ["qualidade", "cor", "altura"], 0),
             F("O que são recursos não renováveis?", "Recursos que podem se esgotar, como carvão mineral, petróleo e diamante.", "⛏️"),
         ]},
    ]},
]


# =========================================================================
# Provas conforme o Orientador de Estudos (3º trimestre/2026)
# =========================================================================
_C = {c["titulo"]: c for p in _BANCO for c in p["conteudos"]}


def _copia(titulo, **mudancas):
    d = copy.deepcopy(_C[titulo])
    d.update(mudancas)
    return d


_TRAB = _C["Trabalho e atividades econômicas do município"]["atividades"]

_GEO_ATIVIDADES_ECONOMICAS = {
    "titulo": "Atividades econômicas no campo e na cidade", "emoji": "🚜", "paginas": "201-203",
    "resumo": "As atividades econômicas produzem o que usamos no dia a dia e é por meio delas que os empregos são gerados. "
              "No campo: agricultura (arroz, feijão, milho, frutas), pecuária (criação de animais para leite, carne, couro e ovos) e agroindústria "
              "(transforma produtos agrícolas em sucos, queijos e doces). Na cidade: comércio (farmácias, padarias, restaurantes, salões de beleza) e "
              "indústria (fábricas de eletrodomésticos, carros e brinquedos). O turismo acontece tanto no campo quanto na cidade e gera empregos em hotéis e restaurantes. "
              "Economia: conjunto de atividades de produção, distribuição e consumo de mercadorias. O campo e a cidade dependem um do outro.",
    "atividades": [_TRAB[1], _TRAB[3], _TRAB[4], _TRAB[5], _TRAB[6],
                   K("Campo ou cidade?", {"Mais comum no campo": ["🌾 Agricultura", "🐄 Pecuária", "🧀 Agroindústria"],
                                          "Mais comum na cidade": ["🏪 Comércio", "🏭 Indústria", "💇 Salão de beleza"]}),
                   VF("É por meio das atividades econômicas que os empregos são gerados.", True, "", "👷"),
                   Q("Qual atividade acontece tanto no campo quanto na cidade?", ["Turismo", "Pecuária", "Agricultura", "Agroindústria"], 0,
                     "Pessoas visitam paisagens bonitas, museus e festivais no campo e na cidade.", "🧳")],
}

_HIST_TRABALHO = {
    "titulo": "Nossas ações transformam o município: trabalho remunerado e não remunerado", "emoji": "👷",
    "paginas": "125-126", "antes": ["Trabalho e atividades econômicas do município"],
    "resumo": "Trabalho é toda atividade realizada para atender às necessidades humanas: produzir mercadorias, oferecer serviços ou cuidar dos outros. "
              "Trabalho remunerado: a pessoa recebe pagamento (salário), como médico, professor e pintor. "
              "Não remunerado: sem pagamento, como cuidar da própria casa, ajudar a comunidade e o trabalho voluntário em hospitais ou cuidando de animais. "
              "O trabalho está presente em todos os espaços do município e é fundamental para formá-lo: graças a ele foram construídos ruas, avenidas, prédios, praças e meios de transporte.",
    "atividades": [_TRAB[0], _TRAB[2],
                   VF("O trabalho foi fundamental para construir ruas, praças, prédios e meios de transporte do município.", True, "", "🏗️"),
                   Q("O que aconteceria numa cidade sem pedreiros, coletores de lixo e médicos?",
                     ["Muita coisa deixaria de ser feita", "Nada mudaria", "A cidade ficaria mais limpa", "As casas se construiriam sozinhas"], 0,
                     "Sem o trabalho das pessoas, nada é feito na sociedade.", "🧱"),
                   C("Cuidar da própria casa e ser voluntário são exemplos de trabalho ___.", ["não remunerado", "remunerado", "industrial"], 0),
                   F("O que é trabalho?", "Toda atividade feita para atender às necessidades humanas: produzir, oferecer serviços ou cuidar dos outros.", "🛠️")],
}

_MAT_GRAFICOS = {
    "titulo": "Gráficos com dinheiro", "emoji": "📊", "paginas": "183",
    "resumo": "Num gráfico de barras, cada barra mostra uma quantidade: a barra mais alta é a maior quantidade e a mais baixa, a menor. "
              "Sempre leia o título (do que fala o gráfico), os eixos (o que está sendo contado) e a fonte (de onde vieram os dados). "
              "No gráfico das moedas do caixa de Ana, havia mais moedas de 1 real (8 moedas) e menos moedas de 25 centavos (2 moedas). "
              "Para saber o valor total, multiplicamos a quantidade pelo valor de cada moeda: 8 moedas de 1 real = 8 reais; 2 moedas de 25 centavos = 50 centavos. 100 centavos = 1 real.",
    "atividades": [
        Q("No gráfico das moedas do caixa de Ana, qual moeda aparecia em MAIOR quantidade?",
          ["1 real", "5 centavos", "25 centavos", "10 centavos"], 0, "A barra do 1 real era a mais alta: 8 moedas.", "📊"),
        Q("E qual moeda aparecia em MENOR quantidade?", ["25 centavos", "1 real", "50 centavos", "5 centavos"], 0,
          "A barra dos 25 centavos era a mais baixa: 2 moedas.", "📉"),
        N("Ana tinha 8 moedas de 1 real. Quantos reais são?", 8, "reais", "8 × 1 = 8 reais.", "🪙"),
        N("E 2 moedas de 25 centavos dão quantos centavos?", 50, "centavos", "25 + 25 = 50 centavos.", "🪙"),
        N("Quantas moedas de 50 centavos formam 2 reais?", 4, "moedas", "2 moedas de 50 centavos = 1 real; para 2 reais, 4 moedas.", "💰"),
        VF("Num gráfico de barras, a barra mais alta mostra a maior quantidade.", True, "", "📈"),
        C("Para saber do que fala um gráfico, lemos primeiro o seu ___.", ["título", "troco", "perímetro"], 0),
        C("100 centavos equivalem a ___.", ["1 real", "10 reais", "50 centavos"], 0),
        F("O que é a fonte de um gráfico?", "É de onde vieram os dados (por exemplo, o contador de moedas).", "🔎"),
    ],
}

_MAT_METADE = {
    "titulo": "Metade e terça parte", "emoji": "🍕", "paginas": "112, 118-119",
    "resumo": "Metade é dividir em 2 partes iguais (÷ 2): metade de 10 é 5; meio metro é metade de 100 cm, ou seja, 50 cm. "
              "Terça parte é dividir em 3 partes iguais (÷ 3): a terça parte de 9 é 3. Pedro gastava 60 L de água e quer gastar só a terça parte: 60 ÷ 3 = 20 L. "
              "Dobro e metade são operações opostas: o dobro de 5 é 10 e a metade de 10 é 5. Triplo e terça parte também: o triplo de 4 é 12 e a terça parte de 12 é 4.",
    "atividades": [
        N("Qual é a metade de 10?", 5, "", "10 ÷ 2 = 5.", "✂️"),
        N("Qual é a metade de 50?", 25, "", "50 ÷ 2 = 25.", "🍰"),
        N("Qual é a terça parte de 9?", 3, "", "9 ÷ 3 = 3.", "🍕"),
        N("Qual é a terça parte de 12?", 4, "", "12 ÷ 3 = 4.", "🍪"),
        N("Pedro gastava 60 litros de água para lavar a louça e quer gastar só a terça parte. Quantos litros vai gastar?", 20, "litros",
          "60 ÷ 3 = 20 litros.", "🚰"),
        N("Gustavo tem 1 000 mL de água e vai dividir em partes iguais entre ele e três amigos. Quantos mL para cada um?", 250, "mL",
          "São 4 pessoas: 1 000 ÷ 4 = 250 mL.", "💧"),
        C("A metade de 1 metro é ___ centímetros.", ["50", "25", "100"], 0, "100 ÷ 2 = 50 cm."),
        L("Faça as contas com o número 6", [["Dobro de 6", "12"], ["Triplo de 6", "18"], ["Metade de 6", "3"], ["Terça parte de 6", "2"]]),
        Q("Achar a terça parte é dividir em…", ["3 partes iguais", "2 partes iguais", "4 partes iguais", "10 partes iguais"], 0, "", "➗"),
        F("Dobro × metade", "O dobro multiplica por 2; a metade divide por 2. Uma desfaz a outra!", "🔁"),
    ],
}

_MAT_INSTRUMENTOS = {
    "titulo": "Medidas não padronizadas e instrumentos de medida", "emoji": "👣", "paginas": "244-246",
    "resumo": "Antigamente as pessoas usavam o corpo para medir: palmo da mão, pé e passos. Jaqueline e André mediram a distância entre duas árvores com os pés "
              "e encontraram resultados diferentes (8 e 6 pés), porque cada pessoa tem um tamanho de pé diferente. São medidas NÃO padronizadas. "
              "Para ter uma medida exata, usamos instrumentos e unidades padronizadas: régua, fita métrica e trena medem comprimento; "
              "a balança mede a massa; o copo medidor ou a jarra graduada medem a capacidade. Na régua, a medição começa no zero.",
    "atividades": [
        Q("Por que Jaqueline e André acharam números diferentes medindo com os pés?",
          ["Porque cada pessoa tem um pé de tamanho diferente", "Porque as árvores se mexeram", "Porque um deles contou errado de propósito", "Porque mediram em dias diferentes"], 0,
          "O pé não é uma medida padronizada.", "👣"),
        K("Qual instrumento usar?", {"Comprimento": ["📏 Régua", "🎗️ Fita métrica", "📐 Trena"],
                                     "Massa": ["⚖️ Balança"], "Capacidade": ["🥛 Copo medidor", "🫗 Jarra graduada"]}),
        VF("Palmo, pé e passo são medidas padronizadas, iguais para todas as pessoas.", False, "Elas mudam de uma pessoa para outra.", "✋"),
        L("O que mede?", [["Régua", "Comprimento"], ["Balança", "Massa"], ["Copo medidor", "Capacidade"]]),
        Q("A altura da parede da sala mede mais ou menos que 1 metro?", ["Mais", "Menos"], 0, "Uma parede é bem mais alta que 1 metro.", "🧱"),
        Q("O comprimento de um celular mede mais ou menos que 1 metro?", ["Menos", "Mais"], 0, "Um celular tem poucos centímetros.", "📱"),
        N("Na régua, a caneta vai do 0 até o 14. Quantos centímetros ela tem?", 14, "cm", "Começando no zero, a medida é 14 cm.", "🖊️"),
        F("Como medir a distância exata entre duas árvores?", "Usando um instrumento padronizado, como a trena ou a fita métrica.", "🌳"),
    ],
}

_ING_HOBBIES = {
    "titulo": "Unit 6 – Hobbies e Simple Present (he/she)", "emoji": "🎨", "paginas": "68-73 (Unit 6)",
    "resumo": "Vocabulário de hobbies: play soccer (jogar futebol), ride a bike (andar de bicicleta), read books (ler livros), draw (desenhar), dance (dançar), "
              "sing (cantar), swim (nadar), play video games (jogar videogame), watch TV (assistir TV), cook (cozinhar), skate (andar de skate). "
              "Simple Present: com I, you, we, they o verbo fica igual (I play, they swim). Com he, she, it o verbo ganha -s (he plays, she dances, it swims); "
              "alguns ganham -es (watch → watches, go → goes). Perguntas: Do you like…? Yes, I do. / No, I don't. Does he/she like…? Yes, he does. / No, she doesn't. "
              "Negativa: I don't play. She doesn't swim (com doesn't o verbo volta sem -s).",
    "atividades": [
        L("Hobby em inglês", [["⚽ play soccer", "jogar futebol"], ["🚲 ride a bike", "andar de bicicleta"], ["📚 read books", "ler livros"],
                              ["🎨 draw", "desenhar"], ["🏊 swim", "nadar"]]),
        M("Memória dos hobbies", [["dance", "💃 dançar"], ["sing", "🎤 cantar"], ["cook", "🍳 cozinhar"], ["watch TV", "📺 assistir TV"],
                                  ["skate", "🛹 andar de skate"], ["play video games", "🎮 jogar videogame"]]),
        C("She ___ soccer every day.", ["plays", "play", "playing"], 0, "Com she, o verbo ganha -s."),
        C("I ___ books at night.", ["read", "reads", "reading"], 0, "Com I, o verbo fica igual."),
        C("He ___ TV after school.", ["watches", "watch", "watchs"], 0, "Watch ganha -es: watches."),
        C("___ he like pizza?", ["Does", "Do", "Is"], 0, "Com he/she usamos Does."),
        C("___ you like music?", ["Do", "Does", "Are"], 0, "Com you usamos Do."),
        Q("Does she dance? — Yes, she ___.", ["does", "do", "dances"], 0, "Resposta curta: Yes, she does.", "💃"),
        Q("Do they swim? — No, they ___.", ["don't", "doesn't", "aren't"], 0, "Resposta curta: No, they don't.", "🏊"),
        VF("A frase “He play video games.” está correta.", False, "O certo é “He plays video games.”", "🎮"),
        K("O verbo fica igual ou ganha -s?", {"I / You / We / They": ["play", "draw", "swim"], "He / She / It": ["plays", "draws", "swims"]}),
        F("Qual é a regra do he/she/it no Simple Present?", "O verbo ganha -s ou -es: he plays, she watches. Na pergunta usamos Does.", "🔤"),
    ],
}

_ING_FRUTAS = {
    "titulo": "Unit 7 – Fruits, vegetables, there are/aren't e quantifiers", "emoji": "🍎", "paginas": "80-85 (Unit 7)",
    "resumo": "Frutas (fruits): apple (maçã), banana, orange (laranja), grapes (uvas), strawberry (morango), watermelon (melancia), pineapple (abacaxi). "
              "Verduras e legumes (vegetables): carrot (cenoura), tomato (tomate), lettuce (alface), potato (batata), broccoli (brócolis), onion (cebola). "
              "There are = há/existem (plural): There are some apples. There aren't = não há: There aren't any bananas. Pergunta: Are there any carrots? Yes, there are. / No, there aren't. "
              "Quantifiers: some (alguns) nas frases afirmativas; any nas negativas e perguntas; lots of / a lot of = muitos (There are lots of grapes).",
    "atividades": [
        L("Frutas", [["🍎 apple", "maçã"], ["🍊 orange", "laranja"], ["🍇 grapes", "uvas"], ["🍓 strawberry", "morango"], ["🍉 watermelon", "melancia"]]),
        M("Memória das verduras", [["carrot", "🥕 cenoura"], ["tomato", "🍅 tomate"], ["lettuce", "🥬 alface"], ["potato", "🥔 batata"],
                                   ["broccoli", "🥦 brócolis"], ["onion", "🧅 cebola"]]),
        K("Fruit or vegetable?", {"Fruits": ["🍌 banana", "🍍 pineapple", "🍓 strawberry"], "Vegetables": ["🥕 carrot", "🥬 lettuce", "🥔 potato"]}),
        C("There are ___ apples on the table.", ["some", "any", "a"], 0, "Afirmativa: some."),
        C("There aren't ___ bananas.", ["any", "some", "lots"], 0, "Negativa: any."),
        C("Are there ___ carrots?", ["any", "some", "a lot"], 0, "Pergunta: any."),
        C("There are ___ grapes in the basket. (muitas)", ["lots of", "any", "an"], 0, "Lots of / a lot of = muitos."),
        Q("Are there any tomatoes? — Yes, there ___.", ["are", "is", "do"], 0, "Yes, there are.", "🍅"),
        Q("O que significa “There aren't any onions”?", ["Não há cebolas", "Há muitas cebolas", "Há algumas cebolas", "Eu gosto de cebolas"], 0, "", "🧅"),
        VF("“A lot of” e “lots of” significam “muitos”.", True, "", "🧺"),
        F("Quando usar some e any?", "Some nas frases afirmativas; any nas negativas e nas perguntas.", "🔤"),
    ],
}


_MAT_PARTES_LITRO = {
    "titulo": "Partes do litro e mililitros em litros", "emoji": "🫗", "paginas": "251-254",
    "resumo": "1 litro = 1 000 mililitros (1 L = 1 000 mL). Se dividirmos 1 litro em 1 000 partes iguais, cada parte é 1 mililitro. "
              "Meio litro é a metade do litro: 500 mL. Um quarto de litro é o litro dividido em 4 partes iguais: 250 mL. "
              "Vinícius encheu 5 copos iguais com 1 litro de suco: cada copo tem 200 mL (200 × 5 = 1 000). "
              "Marina bebeu 2 garrafas de 450 mL: 900 mL, menos que 1 litro. "
              "O bolo de Marcos leva um litro e meio de suco (1 500 mL) na massa e um quarto de litro (250 mL) no recheio: 1 750 mL ao todo. "
              "O bebedouro do Caramelo, o cão-guia, tem 3 500 mL = 3 000 mL + 500 mL = 3 litros e meio.",
    "atividades": [
        N("Meio litro tem quantos mililitros?", 500, "mL", "1 000 ÷ 2 = 500 mL.", "🥛"),
        N("Um quarto de litro tem quantos mililitros?", 250, "mL", "1 000 ÷ 4 = 250 mL.", "🍶"),
        N("Vinícius encheu 5 copos iguais com 1 litro de suco. Quantos mL cabem em cada copo?", 200, "mL",
          "1 000 ÷ 5 = 200 mL (200 × 5 = 1 000).", "🧃"),
        Q("Marina bebeu 2 garrafas de 450 mL. Ela bebeu mais ou menos de 1 litro?", ["Menos de 1 litro", "Mais de 1 litro", "Exatamente 1 litro"], 0,
          "450 + 450 = 900 mL, e 900 é menor que 1 000 mL.", "🍾"),
        N("O bolo leva um litro e meio de suco na massa e um quarto de litro no recheio. Quantos mL ao todo?", 1750, "mL",
          "1 500 + 250 = 1 750 mL.", "🍰"),
        Q("O bebedouro do Caramelo tem 3 500 mL. Isso é o mesmo que…",
          ["3 litros e meio", "35 litros", "3 litros e um quarto", "350 litros"], 0, "3 500 mL = 3 000 mL + 500 mL = 3 L e meio.", "🐕‍🦺"),
        L("Ligue as medidas iguais", [["1 litro", "1 000 mL"], ["Meio litro", "500 mL"], ["Um quarto de litro", "250 mL"], ["Um litro e meio", "1 500 mL"]]),
        C("Dividindo 1 litro em 1 000 partes iguais, cada parte é 1 ___.", ["mililitro", "grama", "quilômetro"], 0),
        VF("Dois copos de meio litro enchem 1 litro.", True, "500 + 500 = 1 000 mL = 1 L.", "🥤"),
        O("Do menor para o maior", ["250 mL", "Meio litro", "1 litro", "3 litros e meio"], "250 mL < 500 mL < 1 000 mL < 3 500 mL."),
        F("Quanto vale meio litro e um quarto de litro?", "Meio litro = 500 mL; um quarto de litro = 250 mL.", "🫗"),
    ],
}

_MAT_PARTES_KG = {
    "titulo": "Partes do quilograma e gramas em quilogramas", "emoji": "🍉", "paginas": "256-261",
    "resumo": "Nas embalagens, a massa vem em gramas (g) ou quilogramas (kg): arroz 1 kg, café 250 g, pipoca 500 g, farinha 5 kg. "
              "1 kg = 1 000 g: dividindo 1 quilograma em 1 000 partes iguais, cada parte é 1 grama. "
              "Meio quilograma é o quilo dividido em 2 partes iguais: 500 g. Um quarto de quilograma é o quilo dividido em 4: 250 g. "
              "Um quilograma e meio = 1 500 g. Formiga e celular têm menos de 1 kg; criança de 8 anos e cadeira têm mais. "
              "Na balança: laranja 203 g, mamão 638 g, carambola 107 g; juntos dão 948 g, menos de 1 kg. "
              "A avó comprou meio quilo de uvas, um quarto de morangos e um quarto de ameixas: 500 + 250 + 250 = 1 000 g = 1 kg; "
              "se cada quarto de quilo custa 2 reais, ela paga 8 reais. O bebê com 3 385 g tem 3 kg e 385 g. "
              "O prato de 1 265 g tem mais de 1 kg. Dona Ana fez 1 250 g de frango (um quilograma e um quarto); o dobro é 2 500 g.",
    "atividades": [
        N("Meio quilograma tem quantos gramas?", 500, "g", "1 000 ÷ 2 = 500 g.", "🎃"),
        N("Um quarto de quilograma tem quantos gramas?", 250, "g", "1 000 ÷ 4 = 250 g.", "🍉"),
        N("Um quilograma e meio de cuscuz tem quantos gramas?", 1500, "g", "1 000 + 500 = 1 500 g.", "🌽"),
        L("Escreva em gramas", [["1 kg de batata-doce", "1 000 g"], ["Meio quilo de inhame", "500 g"],
                               ["Um quarto de quilo de alho", "250 g"], ["Um quilo e meio de cuscuz", "1 500 g"]]),
        K("Mais ou menos de 1 kg?", {"Menos de 1 kg": ["🐜 Formiga", "📱 Celular", "🍊 Laranja"],
                                     "Mais de 1 kg": ["👦 Criança de 8 anos", "🪑 Cadeira", "🍚 Saco de 5 kg de arroz"]}),
        Q("Laranja 203 g, mamão 638 g e carambola 107 g. Qual fruta tem a MAIOR massa?", ["Mamão", "Laranja", "Carambola"], 0,
          "638 g é o maior número.", "🥭"),
        Q("E as três frutas juntas têm mais ou menos de 1 kg?", ["Menos de 1 kg", "Mais de 1 kg"], 0,
          "203 + 638 + 107 = 948 g, menos que 1 000 g.", "⚖️"),
        N("A avó comprou meio quilo de uvas, um quarto de quilo de morangos e um quarto de quilo de ameixas. Quantos gramas ao todo?", 1000, "g",
          "500 + 250 + 250 = 1 000 g = 1 kg.", "🍇"),
        N("Se cada quarto de quilo de fruta custa 2 reais, quanto a avó paga por 1 kg de frutas?", 8, "reais",
          "1 kg tem 4 quartos: 4 × 2 = 8 reais.", "💰"),
        Q("O bebê tem 3 385 g. Isso é o mesmo que…", ["3 kg e 385 g", "33 kg e 85 g", "338 kg e 5 g", "3 g e 385 kg"], 0,
          "3 385 g = 3 000 g + 385 g = 3 kg e 385 g.", "👶"),
        Q("O prato de comida de Seu João tem 1 265 g. Ele tem mais ou menos de 1 kg?", ["Mais de 1 kg", "Menos de 1 kg"], 0,
          "1 265 g é mais que 1 000 g.", "🍽️"),
        N("Dona Ana preparou 1 250 g de frango. Se fizer o dobro, quantos gramas serão?", 2500, "g", "1 250 + 1 250 = 2 500 g.", "🍗"),
        VF("1 250 g é o mesmo que um quilograma e um quarto.", True, "1 000 g + 250 g.", "🍗"),
        C("Dividindo 1 quilograma em 1 000 partes iguais, cada parte é 1 ___.", ["grama", "litro", "metro"], 0),
        F("Quanto vale meio quilo e um quarto de quilo?", "Meio quilo = 500 g; um quarto de quilo = 250 g.", "⚖️"),
    ],
}


PROVAS = [
    {"materia": "Geografia", "titulo": "Prova de Geografia", "data": "2026-11-12", "conteudos": [
        _copia("Recursos naturais e a degradação do solo"),
        _GEO_ATIVIDADES_ECONOMICAS,
        _copia("Desemprego"),
        _copia("Consumo, consumismo, resíduos e reciclagem"),
    ]},
    {"materia": "História", "titulo": "Prova de História", "data": "2026-11-13", "conteudos": [
        _HIST_TRABALHO,
        _copia("O trabalho muda com o tempo"),
        _copia("Direitos das crianças e trabalho infantil", paginas="194-199"),
        _copia("Espaços de lazer: públicos e privados", paginas="266-267"),
    ]},
    {"materia": "Inglês", "titulo": "Prova de Inglês", "data": "2026-11-16", "conteudos": [
        _ING_HOBBIES,
        _ING_FRUTAS,
    ]},
    {"materia": "Ciências", "titulo": "Prova de Ciências", "data": "2026-11-17", "conteudos": [
        _copia("O solo: formação e composição", paginas="72, 73, 75"),
        _copia("Usos do solo, erosão e proteção", paginas="73, 210-214"),
        _copia("A água no planeta e a água potável", paginas="139, 142"),
        _copia("Ciclo da água e estados físicos"),
        _copia("Alimentos: cadeia produtiva e alimentação saudável"),
        _copia("Plantas: usos e partes", paginas="212"),
    ]},
    {"materia": "Português", "titulo": "Prova de Português B3", "data": "2026-11-18", "conteudos": [
        _copia("Onomatopeias e histórias em quadrinhos"),
        _copia("Pronomes demonstrativos"),
        _copia("Adjetivos e concordância", paginas="228-231"),
    ]},
    {"materia": "Português", "titulo": "Prova de Português A3", "data": "2026-11-23", "conteudos": [
        _copia("Onomatopeias e histórias em quadrinhos"),
        _copia("Gênero diário (pessoal e de viagem)", paginas="222-224, 226-227"),
    ]},
    {"materia": "Matemática", "titulo": "Prova de Matemática A3", "data": "2026-11-24", "conteudos": [
        _copia("Sólidos geométricos: poliedros e corpos redondos", paginas="34-36, 39"),
        _copia("Faces, vértices, arestas e planificação"),
        _copia("Medidas de comprimento: metro, centímetro, milímetro e quilômetro", paginas="44, 45, 47-49"),
        _copia("Perímetro"),
        _copia("Sistema monetário: cédulas e moedas do Real"),
        _copia("Troco, pagamento à vista e a prazo"),
        _MAT_GRAFICOS,
    ]},
    {"materia": "Matemática", "titulo": "Prova de Matemática B3", "data": "2026-11-25", "conteudos": [
        _copia("Medidas de massa: grama, quilograma e miligrama", paginas="103-105"),
        _copia("Medidas de capacidade: litro e mililitro", paginas="108-111, 120"),
        _MAT_PARTES_LITRO,
        _copia("Dobro, triplo e divisão"),
        _MAT_METADE,
        _copia("Medidas de comprimento: metro, centímetro, milímetro e quilômetro", paginas="244-248"),
        _MAT_INSTRUMENTOS,
        _MAT_PARTES_KG,
    ]},
]
