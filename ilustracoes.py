"""Ilustrações das atividades.

Cada texto que aparece num jogo (carta da memória, par, item, opção) ou cada enunciado pode ter um "visual":
- "g:<descrição>|<termo da Wikipédia>"  → imagem gerada pelo Gemini (uma vez, guardada no banco);
                                          se o Gemini não puder gerar, usa uma foto livre da Wikipédia/Commons.
- "w:<termo>"                           → foto livre da Wikipédia/Commons (cédulas, moedas, animais, pessoas).
- "svg:<desenho>:<parâmetros>"          → desenho exato feito pelo próprio app (formas, medidas, frações).

Regra didática: a imagem mostra o assunto, mas não entrega a resposta.
"""
import re
import unicodedata

# ---------------------------------------------------------------------------
# Normalização dos textos (tira emojis e espaços extras, deixa minúsculo)
# ---------------------------------------------------------------------------
def _sem_emoji(t):
    out = []
    for ch in t:
        cat = unicodedata.category(ch)
        if cat in ("So", "Sk", "Cs", "Co", "Mn") and not ch.isalnum():
            continue
        if ch in "‍️︎":
            continue
        out.append(ch)
    return "".join(out)


def norm(t):
    t = str(t or "")
    s = re.sub(r"\s+", " ", _sem_emoji(t)).strip().lower()
    return s or t.strip()


# ---------------------------------------------------------------------------
# Peças (cartas, pares, itens, opções)
# ---------------------------------------------------------------------------
_P = {
    # ---------- Geografia ----------
    "luz do sol": "g:o Sol brilhando forte num céu azul|Sol",
    "vento": "g:vento forte soprando folhas e girando um cata-vento|Vento",
    "frutas e plantas": "g:cesta com frutas variadas e plantas verdes|Fruta",
    "diamante": "g:um diamante brilhante lapidado|Diamante",
    "carvão mineral": "g:pedras pretas de carvão mineral|Carvão mineral",
    "petróleo": "g:barril de petróleo ao lado de uma torre de extração de petróleo|Petróleo",
    "remover matas e florestas": "g:floresta sendo derrubada, com troncos de árvores cortadas no chão|Desmatamento",
    "plantar árvores": "g:crianças plantando mudas de árvore na terra|Reflorestamento",
    "limpar o rio": "g:pessoas recolhendo lixo da margem de um rio|Rio",
    "separar o lixo": "g:criança separando o lixo nas lixeiras coloridas de reciclagem|Coleta seletiva",
    "plantar árvores em locais desmatados": "g:fileiras de mudas de árvores plantadas num terreno desmatado|Reflorestamento",
    "cortar árvores": "g:lenhador cortando uma árvore com motosserra|Desmatamento",
    "construir prédios": "g:prédio em construção com guindaste e operários|Construção civil",
    "asfaltar ruas": "g:máquina passando asfalto quente numa rua|Asfalto",
    "vender pães e remédios": "g:padaria e farmácia lado a lado numa rua do bairro|Comércio",
    "comércio": "g:loja com vendedor atendendo um cliente no balcão|Comércio",
    "fabricar carros": "g:fábrica de carros com braços robóticos montando um carro|Indústria automobilística",
    "indústria": "g:fábrica grande com chaminés e operários trabalhando|Indústria",
    "plantar arroz e feijão": "g:agricultor cuidando de uma plantação de arroz|Agricultura",
    "agricultura": "g:plantação verde com um trator trabalhando no campo|Agricultura",
    "criar gado": "g:vacas pastando no campo com um vaqueiro|Pecuária",
    "pecuária": "g:fazenda com vacas, bois e galinhas|Pecuária",
    "fazer queijo e suco": "g:pequena fábrica produzindo queijos e caixas de suco com frutas do campo|Agroindústria",
    "agroindústria": "g:queijos, caixas de suco e potes de doce feitos com produtos do campo|Agroindústria",
    "sucos, queijos e doces": "g:caixas de suco, queijos e potes de doce lado a lado|Queijo",
    "carros e celulares": "g:um carro e um celular lado a lado|Automóvel",
    "casas": "g:casas coloridas numa rua|Casa",
    "salão de beleza": "g:cabeleireira cortando o cabelo de uma cliente no salão|Salão de beleza",
    "turismo": "g:turistas com mala e câmera fotográfica visitando um ponto turístico|Turismo",
    "tirar férias": "g:família de férias na praia com guarda-sol|Férias",
    "desastres naturais": "g:enchente alagando as ruas de uma cidade|Enchente",
    "mudanças tecnológicas": "g:robô trabalhando numa fábrica no lugar das pessoas|Robótica",
    "falta de salário": "g:carteira de dinheiro vazia e aberta|Carteira (acessório)",
    "papel": "g:folhas de papel e jornais empilhados|Papel",
    "plástico": "g:garrafas e embalagens de plástico|Plástico",
    "metal": "g:latas de metal amassadas|Metal",
    "vidro": "g:garrafas e potes de vidro|Vidro",
    "orgânico": "g:cascas de frutas e restos de comida|Resíduo orgânico",
    "jornal": "g:jornal dobrado|Jornal",
    "caixa de papelão": "g:caixa de papelão marrom|Papelão",
    "garrafa pet": "g:garrafa PET de plástico vazia|Politereftalato de etileno",
    "sacolinha": "g:sacola plástica de supermercado|Sacola plástica",
    "lata de refrigerante": "g:lata de refrigerante de alumínio em pé|Lata de alumínio",
    "tampinha de metal": "g:tampinhas de garrafa de metal|Tampa",
    "repensar": "g:criança pensativa diante de uma vitrine de brinquedos, decidindo se precisa mesmo comprar",
    "🤔": "g:criança pensativa diante de uma vitrine de brinquedos, decidindo se precisa mesmo comprar",
    "recusar": "g:criança recusando uma sacola plástica com a mão e segurando uma sacola de pano",
    "✋": "g:criança recusando uma sacola plástica com a mão e segurando uma sacola de pano",
    "reduzir": "g:criança fechando a torneira para economizar água",
    "📉": "g:criança fechando a torneira para economizar água",
    "reutilizar": "g:pote de vidro reaproveitado como porta-lápis",
    "🔁": "g:pote de vidro reaproveitado como porta-lápis",
    "reciclar": "g:lixeiras coloridas de reciclagem com o símbolo de reciclagem|Reciclagem",
    "♻️": "g:lixeiras coloridas de reciclagem com o símbolo de reciclagem|Reciclagem",
    "celular e pilhas": "g:celular velho e pilhas usadas|Lixo eletrônico",
    "eletrônico": "g:monte de lixo eletrônico com celulares, computadores velhos e fios|Lixo eletrônico",
    "seringas e agulhas": "g:seringa de vacina com agulha|Seringa",
    "hospitalar": "g:caixa amarela de descarte hospitalar com símbolo de risco biológico|Resíduo hospitalar",
    "galhos e grama": "g:galhos e grama cortada amontoados no jardim|Poda",
    "restos de fábrica": "g:sucata e restos de material de uma fábrica|Resíduo industrial",
    "industrial": "g:caçamba cheia de resíduos de fábrica|Resíduo industrial",
    "embalagens de ração": "g:sacos vazios de ração animal|Ração",
    "agrícola": "g:embalagens vazias de adubo numa fazenda ao lado de um trator|Agricultura",
    # ---------- História ----------
    "médico no hospital": "g:médico atendendo uma criança no hospital|Médico",
    "professora na escola": "g:professora ensinando alunos na sala de aula|Professor",
    "pintor de paredes": "g:pintor pintando uma parede com rolo de tinta|Pintor",
    "cuidar da própria casa": "g:pessoa varrendo e arrumando a própria casa|Trabalho doméstico",
    "voluntário no hospital": "g:voluntário lendo histórias para crianças num hospital|Voluntariado",
    "ajudar a comunidade": "g:vizinhos limpando juntos uma praça do bairro|Voluntariado",
    "brincar no parque": "g:crianças brincando no escorregador e no balanço do parque|Parque infantil",
    "carvoeiro": "g:carvoeiro de antigamente carregando um saco de carvão nas costas|Carvão vegetal",
    "vendia carvão": "g:carroça antiga carregada de sacos de carvão|Carvão vegetal",
    "vassoureiro": "g:vendedor de rua de antigamente carregando muitas vassouras de palha|Vassoura",
    "vendia vassouras": "g:vassouras de palha à venda|Vassoura",
    "pregão": "g:vendedor de rua de antigamente gritando para anunciar seus produtos",
    "anúncio em voz alta": "g:vendedor de rua de antigamente gritando para anunciar seus produtos",
    "leiteiro com carroça (1930)": "g:leiteiro de antigamente entregando leite numa carroça puxada por cavalo|Leiteiro",
    "leiteiro de porta em porta": "g:leiteiro de antigamente entregando garrafas de leite na porta das casas|Leiteiro",
    "caminhão de entregas": "g:caminhão de entregas|Caminhão",
    "motoboy de aplicativo (2024)": "g:entregador de moto com mochila térmica de entregas|Motoboy",
    "motoboy de aplicativo": "g:entregador de moto com mochila térmica de entregas|Motoboy",
    "acendedor de lampiões": "g:homem de antigamente acendendo um lampião de rua com uma vara comprida, ao entardecer|Lampião",
    "bonde puxado": "g:bonde antigo puxado por burros numa rua de pedras|Bonde",
    "pagamento por pix": "g:pessoa pagando uma compra com o celular apontado para um QR code|Pix (sistema de pagamentos)",
    "fábrica com robôs": "g:braços robóticos montando produtos numa fábrica moderna|Robô industrial",
    "abraço da família": "g:família dando um abraço apertado|Família",
    "ter uma casa": "g:família feliz em frente à sua casa|Casa",
    "brincar no museu e no parque": "g:crianças visitando um museu com dinossauro|Museu",
    "ir à escola": "g:crianças de mochila chegando na escola|Escola",
    "praça": "g:praça pública com bancos, árvores, chafariz e pessoas|Praça",
    "parque": "g:parque público com árvores, gramado e lago|Parque",
    "parque da cidade": "g:parque público com árvores, gramado e lago|Parque",
    "praia": "g:praia com areia, mar azul e guarda-sol|Praia",
    "quadra do bairro": "g:quadra de esportes pública do bairro com crianças jogando|Quadra",
    "shopping": "g:corredor de shopping center com lojas|Shopping center",
    "cinema": "g:sala de cinema com tela grande e poltronas vermelhas|Cinema",
    "clube": "g:clube com piscina e escorregador|Clube",
    "teatro particular": "g:teatro com palco e cortinas vermelhas|Teatro",
    # ---------- Inglês ----------
    "play soccer": "g:criança jogando futebol|Futebol",
    "jogar futebol": "g:criança jogando futebol|Futebol",
    "ride a bike": "g:criança andando de bicicleta|Bicicleta",
    "andar de bicicleta": "g:criança andando de bicicleta|Bicicleta",
    "read books": "g:criança lendo um livro sentada|Leitura",
    "ler livros": "g:criança lendo um livro sentada|Leitura",
    "draw": "g:criança desenhando com lápis de cor|Desenho",
    "desenhar": "g:criança desenhando com lápis de cor|Desenho",
    "swim": "g:criança nadando na piscina|Natação",
    "nadar": "g:criança nadando na piscina|Natação",
    "dance": "g:criança dançando alegre|Dança",
    "dançar": "g:criança dançando alegre|Dança",
    "sing": "g:criança cantando com um microfone|Canto",
    "cantar": "g:criança cantando com um microfone|Canto",
    "cook": "g:criança de avental cozinhando com uma panela|Culinária",
    "cozinhar": "g:criança de avental cozinhando com uma panela|Culinária",
    "watch tv": "g:criança assistindo televisão no sofá|Televisão",
    "assistir tv": "g:criança assistindo televisão no sofá|Televisão",
    "skate": "g:criança andando de skate|Skate",
    "andar de skate": "g:criança andando de skate|Skate",
    "play video games": "g:criança jogando videogame com controle na mão|Jogo eletrônico",
    "jogar videogame": "g:criança jogando videogame com controle na mão|Jogo eletrônico",
    "apple": "g:uma maçã vermelha|Maçã", "maçã": "g:uma maçã vermelha|Maçã",
    "orange": "g:uma laranja|Laranja (fruta)", "laranja": "g:uma laranja|Laranja (fruta)",
    "grapes": "g:um cacho de uvas roxas|Uva", "uvas": "g:um cacho de uvas roxas|Uva",
    "strawberry": "g:um morango vermelho|Morango", "morango": "g:um morango vermelho|Morango",
    "watermelon": "g:uma melancia com uma fatia cortada|Melancia", "melancia": "g:uma melancia com uma fatia cortada|Melancia",
    "carrot": "g:uma cenoura com folhas|Cenoura", "cenoura": "g:uma cenoura com folhas|Cenoura",
    "tomato": "g:um tomate vermelho|Tomate", "tomate": "g:um tomate vermelho|Tomate",
    "lettuce": "g:um pé de alface verde|Alface", "alface": "g:um pé de alface verde|Alface",
    "potato": "g:batatas|Batata", "batata": "g:batatas|Batata",
    "broccoli": "g:um brócolis verde|Brócolis", "brócolis": "g:um brócolis verde|Brócolis",
    "onion": "g:uma cebola|Cebola", "cebola": "g:uma cebola|Cebola",
    "banana": "g:um cacho de bananas amarelas|Banana",
    "pineapple": "g:um abacaxi|Abacaxi",
    "não há cebolas": "g:cesta de palha completamente vazia",
    "há muitas cebolas": "g:cesta de palha transbordando de cebolas",
    "há algumas cebolas": "g:cesta de palha com apenas três cebolas",
    "eu gosto de cebolas": "g:criança sorrindo e abraçando uma cebola gigante",
    # ---------- Ciências ----------
    "pelo desgaste das rochas ao longo de milhares de anos": "g:rocha rachada se quebrando em pedacinhos que viram terra",
    "areia e argila": "g:um montinho de areia clara ao lado de um montinho de argila vermelha|Argila",
    "restos de plantas": "g:folhas secas e galhos se decompondo sobre a terra|Húmus",
    "água": "g:copo de água transparente|Água",
    "ar": "g:vento soprando e levantando folhas no ar|Ar",
    "asfalto": "g:rua asfaltada|Asfalto",
    "restos de plantas e animais": "g:folhas secas, galhos e minhocas se decompondo no solo|Matéria orgânica",
    "pedaços de plástico": "g:pedaços de plástico espalhados|Plástico",
    "rocha inteira": "g:uma grande rocha inteira na paisagem|Rocha",
    "calor, chuva e vento desgastam a rocha": "g:sol, chuva e vento batendo numa rocha rachada",
    "a rocha vira pedacinhos": "g:rocha quebrada em muitos pedacinhos e cascalho",
    "restos de seres vivos se misturam": "g:pedacinhos de rocha misturados com folhas secas e minhocas",
    "forma-se o solo": "g:solo fértil escuro com plantas crescendo|Solo",
    "plantação": "g:plantação de milho|Milho",
    "cultivo de alimentos": "g:horta com fileiras de verduras|Horta",
    "gado no campo": "g:gado pastando no campo|Gado",
    "pasto para animais": "g:pasto verde cercado com vacas ao longe|Pastagem",
    "telhas e tijolos": "g:pilha de telhas e tijolos de barro|Tijolo",
    "materiais para construção": "g:pilha de telhas e tijolos de barro|Tijolo",
    "variar o tipo de planta após cada colheita": "g:campo dividido em faixas com plantações diferentes de milho, feijão e soja|Rotação de culturas",
    "rotação de culturas": "g:campo dividido em faixas com plantações diferentes de milho, feijão e soja|Rotação de culturas",
    "plantar sempre a mesma coisa": "g:campo enorme com uma única plantação de soja até o horizonte|Monocultura",
    "girar a terra com trator": "g:trator arando a terra|Arado",
    "usar muito agrotóxico": "g:avião pulverizando agrotóxico sobre uma plantação|Agrotóxico",
    "agrotóxico em excesso": "g:avião pulverizando agrotóxico sobre uma plantação|Agrotóxico",
    "quando chuva ou vento levam o solo descoberto": "g:morro sem plantas com a chuva levando a terra e abrindo buracos|Erosão",
    "quando plantamos árvores": "g:crianças plantando mudas de árvore na terra|Reflorestamento",
    "quando chove pouco": "g:terra seca e rachada|Seca",
    "fertilizante orgânico": "g:composteira com restos de comida virando adubo|Compostagem",
    "jogar lixo no chão": "g:lixo jogado no chão de um parque",
    "desmatar": "g:floresta sendo derrubada, com troncos de árvores cortadas no chão|Desmatamento",
    "nos mares e oceanos (salgada)": "g:oceano azul imenso com ondas|Oceano",
    "nos rios": "g:rio correndo entre árvores|Rio",
    "nas geleiras": "g:geleira enorme de gelo azulado|Glaciar",
    "nas nuvens": "g:nuvens brancas no céu|Nuvem",
    "água limpa e própria para beber": "g:copo de água limpa e transparente|Água potável",
    "qualquer água de rio": "g:rio com água barrenta|Rio",
    "água do mar": "g:ondas do mar|Mar",
    "água da chuva no chão": "g:poça de água da chuva no chão|Poça",
    "mar": "g:mar azul com ondas|Mar",
    "oceano": "g:oceano imenso visto do alto|Oceano",
    "rio": "g:rio correndo entre árvores|Rio",
    "lago": "g:lago tranquilo cercado de árvores|Lago",
    "geleira": "g:geleira enorme de gelo azulado|Glaciar",
    "água subterrânea": "g:corte do solo mostrando água guardada embaixo da terra e um poço|Água subterrânea",
    "evaporação": "g:sol esquentando um lago e vapor subindo para o céu|Evaporação",
    "condensação": "g:vapor subindo e formando nuvens no céu|Condensação",
    "precipitação": "g:chuva caindo de uma nuvem escura|Precipitação",
    "infiltração e escoamento": "g:água da chuva entrando no solo e escorrendo morro abaixo até um rio",
    "infiltração": "g:água da chuva entrando no solo entre as raízes das plantas|Infiltração",
    "escoamento": "g:água da chuva escorrendo pela rua até o bueiro|Escoamento superficial",
    "erosão": "g:morro sem vegetação com a terra sendo levada pela chuva|Erosão",
    "☀️": "g:o Sol brilhando forte num céu azul|Sol",
    "☁️": "g:nuvens brancas no céu|Nuvem",
    "🌧️": "g:chuva caindo de uma nuvem escura|Chuva",
    "🕳️": "g:água da chuva entrando num buraco no solo|Infiltração",
    "gelo": "g:cubos de gelo|Gelo",
    "água do rio": "g:água de rio correndo entre pedras|Rio",
    "vapor": "g:vapor saindo de uma panela no fogão|Vapor",
    "agricultura e pecuária": "g:fazenda com plantação e vacas|Agropecuária",
    "distribuição": "g:caminhão levando caixas de alimentos para o mercado",
    "consumidores": "g:família fazendo compras no supermercado|Supermercado",
    "espiga de milho": "g:espiga de milho|Milho",
    "ovo": "g:ovos de galinha|Ovo",
    "milho em conserva": "g:lata aberta de milho em conserva|Milho",
    "queijo": "g:pedaço de queijo|Queijo",
    "salgadinho de pacote": "g:pacote de salgadinho com salgadinhos espalhados",
    "refrigerante": "g:garrafa de refrigerante|Refrigerante",
    "biscoito recheado": "g:biscoitos recheados de chocolate|Biscoito",
    "proteínas": "g:ovos, carne, frango, peixe e feijão juntos|Proteína",
    "carboidratos": "g:arroz, pão, batata e macarrão juntos|Carboidrato",
    "vitaminas": "g:frutas e verduras bem coloridas|Vitamina",
    "minerais": "g:copo de leite, queijo e folhas verde-escuras|Sal mineral",
    "fibras": "g:aveia, pão integral e frutas com casca|Fibra alimentar",
    "mandioca": "g:raízes de mandioca|Mandioca",
    "feijão": "g:prato de feijão|Feijão",
    "arroz": "g:prato de arroz branco|Arroz",
    "madeira": "g:tábuas de madeira empilhadas|Madeira",
    "construir casas e móveis": "g:casa de madeira e móveis de madeira|Móvel",
    "plantas medicinais": "g:plantas medicinais em vasos, como babosa, hortelã e camomila|Planta medicinal",
    "remédios": "g:frascos e caixinhas de remédio|Medicamento",
    "andiroba": "g:sementes de andiroba e um vidrinho de óleo|Andiroba",
    "cosméticos": "g:cremes, sabonetes e frascos de perfume|Cosmético",
    "lavanda": "g:flores roxas de lavanda|Lavanda",
    "dar cheiro (aromatizante)": "g:saquinhos perfumados de lavanda|Lavanda",
    "fruto": "g:desenho de uma planta inteira com o FRUTO destacado por um círculo amarelo|Fruto",
    "raiz": "g:desenho de uma planta inteira com a RAIZ, embaixo da terra, destacada por um círculo amarelo|Raiz",
    "folha": "g:desenho de uma planta inteira com uma FOLHA destacada por um círculo amarelo|Folha",
    "caule": "g:desenho de uma planta inteira com o CAULE destacado por um círculo amarelo|Caule",
    "flor": "g:desenho de uma planta inteira com a FLOR destacada por um círculo amarelo|Flor",
    # ---------- Português ----------
    "passarinho": "g:passarinho cantando num galho|Pássaro",
    "buzina": "g:carro buzinando no trânsito|Buzina",
    "batida na porta": "g:mão batendo numa porta de madeira|Porta",
    "sono": "g:criança dormindo na cama|Sono",
    "explosão": "g:explosão colorida de fogos de artifício em estilo de desenho|Fogos de artifício",
    "🐶": "g:cachorro latindo|Cão",
    "🐱": "g:gato miando|Gato",
    "⏰": "g:relógio despertador|Despertador",
    "🤧": "g:criança espirrando|Espirro",
    "☎️": "g:telefone antigo tocando|Telefone",
    "🐸": "g:sapo coaxando numa folha|Sapo",
    "perto de mim": "g:criança segurando um livro nas próprias mãos e olhando para ele",
    "perto de você": "g:criança apontando para um livro que está na mão do amigo à sua frente",
    "longe de nós": "g:duas crianças apontando juntas para uma árvore bem distante",
    "baleia": "g:baleia nadando no mar|Baleia",
    "areia": "g:areia da praia com conchinhas|Areia",
    "peixe": "g:peixes coloridos nadando|Peixe",
    "querido diário, hoje fui à praia!": "g:diário aberto com desenho de uma praia",
    "era uma vez um dragão…": "g:dragão de conto de fadas perto de um castelo",
    "notícia: chuva forte atinge a cidade": "g:jornal mostrando a foto de uma chuva forte na cidade",
    "ingredientes: 2 ovos e farinha": "g:ovos e saco de farinha numa mesa de cozinha",
    "estava ansiosa para ver o mar": "g:menina acordada na cama à noite, sonhando com o mar",
    "estava doente": "g:menina doente na cama com termômetro",
    "tinha prova": "g:menina estudando para a prova com livros",
    "perdeu o diário": "g:menina procurando um diário perdido embaixo da cama",
    # ---------- Matemática: sólidos (desenhos exatos) ----------
    "cubo": "svg:cubo", "pirâmide": "svg:piramide:4", "paralelepípedo": "svg:paralelepipedo",
    "prisma": "svg:prisma:3", "esfera": "svg:esfera", "cilindro": "svg:cilindro", "cone": "svg:cone",
    "pirâmide quadrada": "svg:piramide:4", "pirâmide triangular": "svg:piramide:3",
    "pirâmide de base quadrada": "svg:piramide:4",
    "face": "svg:cubo:face", "aresta": "svg:cubo:aresta", "vértice": "svg:cubo:vertice",
    "6 quadrados": "svg:plan:cubo", "4 triângulos": "svg:plan:4tri",
    "2 círculos e 1 retângulo": "svg:plan:cilindro", "5 quadrados": "svg:plan:5q",
    "caixa de presente": "g:caixa de presente com laço vermelho|Presente",
    "chapéu de festa": "g:chapéu de festa de aniversário em forma de cone|Chapéu de festa",
    "bola": "g:bola de futebol|Bola de futebol",
    "tijolo": "g:um tijolo de barro|Tijolo",
    "caixa de pizza": "g:caixa de pizza de papelão fechada|Pizza",
    # ---------- Matemática: medidas ----------
    "comprimento de uma formiga": "g:formiga|Formiga",
    "comprimento de um lápis": "g:lápis amarelo|Lápis",
    "altura da porta": "g:porta de madeira|Porta",
    "distância entre cidades": "g:estrada longa ligando duas cidades vistas de longe|Rodovia",
    "régua": "svg:regua", "fita métrica": "g:fita métrica de costura enrolada|Fita métrica",
    "trena": "g:trena de metal|Trena", "balança": "svg:balanca:1 kg",
    "copo medidor": "svg:jarra:500", "jarra graduada": "svg:jarra:750",
    "carne": "g:pedaço de carne crua|Carne", "suco": "g:copo de suco de laranja|Suco",
    "leite": "g:caixa de leite e um copo de leite|Leite", "ovos": "g:caixa de ovos|Ovo",
    "lápis": "g:lápis amarelo|Lápis",
    "garrafão de 5 l": "g:garrafão de água de 5 litros|Garrafão",
    "garrafinha de 500 ml": "g:garrafinha de água pequena|Garrafa",
    "copo de 200 ml": "g:copo de água|Copo",
    "xícara de 100 ml": "g:xícara pequena de café|Xícara",
    "galão de água": "g:galão de água mineral de 20 litros|Garrafão",
    "caixa-d'água": "g:caixa-d'água azul no telhado de uma casa|Caixa-d'água",
    "balde": "g:balde de plástico|Balde",
    "colher de remédio": "g:colher de remédio com xarope|Colher",
    "xícara de café": "g:xícara de café|Xícara",
    "copinho de iogurte": "g:copinho de iogurte|Iogurte",
    "1 litro": "svg:jarra:1000", "meio litro": "svg:jarra:500", "um quarto de litro": "svg:jarra:250",
    "um litro e meio": "svg:jarras:1500", "3 litros e meio": "svg:jarras:3500",
    "dobro de 6": "svg:pontos:6:2", "triplo de 6": "svg:pontos:6:3",
    "metade de 6": "svg:dividir:6:2", "terça parte de 6": "svg:dividir:6:3",
    "2 partes iguais": "svg:partes:2", "3 partes iguais": "svg:partes:3",
    "4 partes iguais": "svg:partes:4", "10 partes iguais": "svg:partes:10",
    "1 kg de batata-doce": "g:batatas-doces|Batata-doce",
    "meio quilo de inhame": "g:inhames|Inhame",
    "um quarto de quilo de alho": "g:cabeças de alho|Alho",
    "um quilo e meio de cuscuz": "g:pacote de flocos de milho e um prato de cuscuz|Cuscuz",
    "formiga": "g:formiga|Formiga", "celular": "g:celular|Telefone celular",
    "criança de 8 anos": "g:menino de 8 anos sorrindo|Criança",
    "cadeira": "g:cadeira de madeira|Cadeira",
    "saco de 5 kg de arroz": "g:saco grande de arroz|Arroz",
    "mamão": "g:mamão cortado ao meio|Mamão", "carambola": "g:carambolas|Carambola",
    # ---------- Matemática: dinheiro (fotos reais) ----------
    "2 reais": "w:cédula 2 reais segunda família do real", "5 reais": "w:cédula 5 reais segunda família do real",
    "10 reais": "w:cédula 10 reais segunda família do real", "20 reais": "w:cédula 20 reais segunda família do real",
    "50 reais": "w:cédula 50 reais segunda família do real", "200 reais": "w:cédula 200 reais lobo-guará",
    "tartaruga-marinha": "w:Tartaruga-marinha", "garça": "w:Garça-branca-grande", "arara": "w:Arara-vermelha",
    "mico-leão-dourado": "w:Mico-leão-dourado", "onça-pintada": "w:Onça-pintada", "lobo-guará": "w:Lobo-guará",
    "garoupa": "w:Garoupa",
    "1 centavo": "w:moeda 1 centavo real Cabral", "5 centavos": "w:moeda 5 centavos real Tiradentes",
    "10 centavos": "w:moeda 10 centavos real Pedro I", "25 centavos": "w:moeda 25 centavos real Deodoro",
    "50 centavos": "w:moeda 50 centavos real Rio Branco", "1 real": "w:moeda 1 real brasil",
    "pedro álvares cabral": "w:Pedro Álvares Cabral", "tiradentes": "w:Tiradentes",
    "d. pedro i": "w:Pedro I do Brasil", "deodoro da fonseca": "w:Deodoro da Fonseca",
    "barão do rio branco": "w:José Paranhos, Barão do Rio Branco",
    "pix": "g:celular mostrando um QR code de pagamento|Pix (sistema de pagamentos)",
    "cartão de crédito": "g:cartão de crédito|Cartão de crédito",
    "boleto": "g:papel de boleto com código de barras|Boleto bancário",
    "dinheiro": "g:cédulas e moedas de dinheiro|Dinheiro",
    "pagar tudo de uma vez": "g:pessoa entregando um maço de dinheiro de uma vez no caixa da loja",
    "pagar em parcelas": "g:calendário com vários meses e uma moeda em cada mês",
}

# ---------------------------------------------------------------------------
# Enunciados: trecho do texto (minúsculo) → visual. O primeiro que casar vale.
# ---------------------------------------------------------------------------
_E = [
    # Geografia
    ("o que é desmatamento", "g:floresta sendo derrubada, com troncos de árvores cortadas no chão|Desmatamento"),
    ("o que é reflorestamento", "g:crianças plantando mudas de árvore na terra|Reflorestamento"),
    ("solo desmatado fica mais exposto", "g:morro sem plantas com a chuva levando a terra e abrindo buracos|Erosão"),
    ("recursos não renováveis", "g:barril de petróleo e pedras de carvão mineral|Petróleo"),
    ("agroindústria transforma", "g:frutas e leite do campo entrando numa pequena fábrica|Agroindústria"),
    ("campo e a cidade dependem", "g:caminhão levando alimentos do campo para a cidade"),
    ("criação de animais para obter", "g:fazenda com vacas, bois e galinhas|Pecuária"),
    ("o que é desemprego", "g:pessoa preocupada procurando emprego no jornal"),
    ("desemprego afeta toda a comunidade", "g:rua do bairro com várias lojas fechadas"),
    ("consumo e consumismo", "g:pessoa carregando muitas sacolas de compras|Consumismo"),
    ("o que é reciclagem", "g:lixeiras coloridas de reciclagem com o símbolo de reciclagem|Reciclagem"),
    ("propagandas tentam", "g:criança olhando uma propaganda de brinquedo na televisão|Publicidade"),
    ("lixeira azul", "g:cinco lixeiras de coleta seletiva coloridas: azul, vermelha, verde, amarela e marrom|Coleta seletiva"),
    ("consumo sustentável", "g:sacola de pano reutilizável cheia de frutas|Consumo sustentável"),
    # História
    ("o que é trabalho remunerado", "g:trabalhador recebendo seu pagamento no fim do mês"),
    ("construir ruas, praças", "g:operários construindo uma rua e uma praça|Construção civil"),
    ("sem pedreiros, coletores", "g:pedreiro, coletor de lixo e médico lado a lado"),
    ("acendedor de lampiões acabou", "g:homem de antigamente acendendo um lampião de rua com uma vara comprida, ao entardecer|Lampião"),
    ("máquinas e tecnologia no trabalho", "g:braços robóticos montando produtos numa fábrica moderna|Robô industrial"),
    ("iluminação das ruas antigamente", "g:rua antiga à noite iluminada por lampiões a gás|Lampião"),
    ("trabalho infantil prejudica", "g:crianças felizes estudando e brincando na escola"),
    ("lugar de criança", "g:crianças felizes numa sala de aula|Escola"),
    ("não danificar os brinquedos", "g:crianças brincando com cuidado num parquinho|Parque infantil"),
    ("lazer na natureza", "g:família fazendo trilha numa floresta|Trilha"),
    ("espaço público e privado", "g:praça pública ao lado de um clube particular com piscina"),
    # Inglês
    ("soccer every day", "g:menina jogando futebol|Futebol"),
    ("books at night", "g:criança lendo um livro na cama à noite|Leitura"),
    ("tv after school", "g:menino assistindo televisão no sofá|Televisão"),
    ("like pizza", "g:pizza|Pizza"),
    ("like music", "g:criança ouvindo música com fones de ouvido|Música"),
    ("does she dance", "g:menina dançando alegre|Dança"),
    ("do they swim", "g:duas crianças nadando na piscina|Natação"),
    ("he play video games", "g:menino jogando videogame com controle na mão|Jogo eletrônico"),
    ("apples on the table", "g:maçãs vermelhas sobre uma mesa|Maçã"),
    ("bananas.", "g:fruteira vazia|Fruteira"),
    ("are there ___ carrots", "g:cenouras com folhas|Cenoura"),
    ("grapes in the basket", "g:cesta cheia de cachos de uvas|Uva"),
    ("any tomatoes", "g:tomates vermelhos|Tomate"),
    ("lots of", "g:cesta transbordando de frutas"),
    # Ciências
    ("camadas do solo", "g:corte do solo mostrando as camadas de terra, da superfície até a rocha|Horizonte do solo"),
    ("como o solo é formado", "g:corte do solo mostrando as camadas de terra, da superfície até a rocha|Solo"),
    ("asfalto impede", "g:chuva caindo sobre uma rua asfaltada com água empoçada|Asfalto"),
    ("matéria orgânica do solo", "g:folhas secas, galhos e minhocas se decompondo no solo|Matéria orgânica"),
    ("o que é o solo", "g:corte do solo com raízes de plantas e minhocas|Solo"),
    ("rotação de culturas", "g:campo dividido em faixas com plantações diferentes de milho, feijão e soja|Rotação de culturas"),
    ("o que é erosão", "g:morro sem vegetação com a terra sendo levada pela chuva|Erosão"),
    ("árvores e gramíneas", "g:morro coberto de grama e árvores, protegido da chuva"),
    ("monocultura", "g:campo enorme com uma única plantação de soja até o horizonte|Monocultura"),
    ("maior parte da água do planeta", "g:planeta Terra visto do espaço mostrando os oceanos azuis|Terra"),
    ("o que é água potável", "g:criança bebendo um copo de água limpa|Água potável"),
    ("toda água doce pode ser bebida", "g:rio com água barrenta|Rio"),
    ("contaminada por bactérias", "g:copo de água suja com micróbios desenhados|Bactéria"),
    ("boa parte da água doce", "g:geleira enorme de gelo azulado|Glaciar"),
    ("água vira vapor", "g:sol esquentando um lago e vapor subindo para o céu|Evaporação"),
    ("vapor esfria e forma as nuvens", "g:vapor subindo e formando nuvens no céu|Condensação"),
    ("chuva caindo das nuvens", "g:chuva caindo de uma nuvem escura|Chuva"),
    ("neve e granizo", "g:neve e pedras de granizo no chão|Granizo"),
    ("ciclo da água", "g:ciclo da água com sol, mar, vapor subindo, nuvens, chuva e rio, com setas|Ciclo hidrológico"),
    ("prato saudável", "g:prato saudável com arroz, feijão, frango e salada|Alimentação saudável"),
    ("muita gordura", "g:batata frita e hambúrguer gordurosos|Gordura"),
    ("ultraprocessados", "g:salgadinho de pacote, refrigerante e biscoito recheado juntos|Alimento ultraprocessado"),
    ("o caqui é", "g:caquis maduros pendurados no galho do caquizeiro|Caqui"),
    ("a mandioca é", "g:mandiocas descascadas|Mandioca"),
    ("plantas medicinais têm", "g:plantas medicinais em vasos, como babosa, hortelã e camomila|Planta medicinal"),
    ("açaí", "g:cachos de açaí na palmeira|Açaí"),
    ("tu youyou", "g:cientista estudando plantas num laboratório"),
    ("usos das plantas", "g:móvel de madeira, frasco de remédio e perfume de flores lado a lado"),
    # Português
    ("segurando o livro", "g:criança segurando um livro nas próprias mãos"),
    ("apontando para longe", "g:criança apontando para uma árvore alta bem longe na floresta"),
    ("que você tem na mão", "g:criança apontando para um objeto na mão do amigo"),
    ("'aquilo' indica", "g:duas crianças apontando juntas para uma montanha bem distante"),
    ("azul e agitado", "g:mar azul e agitado com ondas grandes|Mar"),
    ("muitos peixes", "g:peixes coloridos nadando no mar|Peixe"),
    ("a bola é", "g:bola colorida|Bola"),
    ("as baleias são", "g:baleia enorme nadando no mar|Baleia"),
    ("água do mar é", "g:ondas do mar|Mar"),
    ("começar um diário", "g:diário aberto com uma caneta|Diário"),
    ("mariana não conseguia dormir", "g:menina acordada na cama à noite, olhando pela janela|Insônia"),
    ("diário de viagem", "g:diário de viagem aberto com mapa e fotos coladas|Diário"),
    ("diário é escrito em 1ª pessoa", "g:criança escrevendo num diário|Diário"),
    # Matemática — sólidos
    ("faces tem um cubo", "svg:cubo:face"),
    ("vértices tem um cubo", "svg:cubo:vertice"),
    ("caixa de sapato", "svg:paralelepipedo:aresta"),
    ("pirâmide de base quadrada", "svg:piramide:4"),
    ("esfera é um corpo redondo", "svg:esfera"),
    ("nas pirâmides, as faces laterais", "svg:piramide:4"),
    ("o cilindro é um poliedro", "svg:cilindro"),
    ("no prisma, as duas faces", "svg:prisma:3"),
    ("o que é um poliedro", "svg:grupo:poliedros"),
    ("corpos redondos", "svg:grupo:redondos"),
    ("planificação do cubo", "svg:cubo"),
    ("1 quadrado e 4 triângulos", "svg:plan:piramide4"),
    ("planificar um sólido", "svg:plan:cubo"),
    # Matemática — comprimento e perímetro
    ("milímetros tem 1 centímetro", "svg:regua:mm"),
    ("centímetros tem 1 metro", "svg:metro:1"),
    ("metros tem 1 quilômetro", "g:estrada longa ligando duas cidades vistas de longe|Rodovia"),
    ("meio metro tem", "svg:metro:2"),
    ("um quarto de metro", "svg:metro:4"),
    ("metade de 1 metro", "svg:metro:2"),
    ("muro tem 1 metro", "g:muro de tijolos|Muro"),
    ("medição com a régua", "svg:regua"),
    ("medir com passos", "g:duas crianças de tamanhos diferentes medindo a mesma distância com passos"),
    ("contorno de uma figura plana", "svg:perim:ret:3 m:2 m"),
    ("mesa tem 2 m", "svg:perim:ret:2 m:1 m"),
    ("canteiro triangular", "svg:perim:tri:4 m:4 m:3 m"),
    ("4 m, 5 m, 6 m e 5 m", "svg:perim:trap:4 m:5 m:6 m:5 m"),
    ("quadrado tem 3 cm", "svg:perim:quad:3 cm"),
    ("195 m por 120 m", "svg:perim:ret:195 m:120 m"),
    ("como calcular o perímetro", "svg:perim:ret:5 cm:3 cm"),
    ("circunferência", "svg:circulo"),
    ("medindo com os pés", "g:duas crianças medindo a distância entre duas árvores com os pés"),
    ("palmo, pé e passo", "g:mão medindo uma mesa com palmos"),
    ("altura da parede", "g:criança em pé ao lado da parede alta de uma sala"),
    ("comprimento de um celular", "g:celular|Telefone celular"),
    ("caneta vai do 0 até o 14", "svg:regua:14"),
    ("distância exata entre duas árvores", "g:trena medindo a distância entre duas árvores|Trena"),
    # Matemática — dinheiro
    ("desde que ano usamos o real", "w:cédulas do real segunda família"),
    ("centavos tem 1 real", "w:moeda 1 real brasil"),
    ("moedas de 50 centavos formam", "w:moeda 50 centavos real Rio Branco"),
    ("moedas de 25 centavos formam", "w:moeda 25 centavos real Deodoro"),
    ("moeda de 1 centavo", "w:moeda 1 centavo real Cabral"),
    ("o lado da moeda com o rosto", "w:moeda 1 real brasil"),
    ("4 notas de 10 reais", "w:cédula 10 reais segunda família do real"),
    ("sistema monetário", "w:cédulas do real segunda família"),
    ("livro custa 30 reais", "g:livro infantil colorido|Livro"),
    ("brinquedo custa 45 reais", "g:ursinho de pelúcia|Urso de pelúcia"),
    ("água custa 4 reais", "g:garrafinha de água|Garrafa"),
    ("bicicleta custa", "g:bicicleta infantil|Bicicleta"),
    ("sofá custa", "g:sofá|Sofá"),
    ("quebra-cabeça de 45 reais", "g:caixa de quebra-cabeça com peças|Quebra-cabeça"),
    ("o que é troco", "g:caixa de loja devolvendo moedas de troco para uma criança|Troco"),
    ("8 moedas de 1 real", "w:moeda 1 real brasil"),
    ("2 moedas de 25 centavos", "w:moeda 25 centavos real Deodoro"),
    ("50 centavos formam 2 reais", "w:moeda 50 centavos real Rio Branco"),
    ("gráfico de barras", "svg:barras"),
    ("100 centavos equivalem", "w:moeda 1 real brasil"),
    # Matemática — massa
    ("gramas tem 1 quilograma", "svg:balanca:1 kg"),
    ("miligramas tem 1 grama", "g:comprimido de remédio pequenino sobre a ponta de um dedo"),
    ("lucas nasceu com 3 kg", "g:bebê numa balança de bebê|Bebê"),
    ("pessoa e uma xícara com alface", "g:pessoa numa balança de banheiro e uma xícara com alface numa balança de cozinha"),
    ("algodão tem a mesma massa", "g:balança de dois pratos equilibrada com uma bola grande de algodão e um pequeno peso de ferro|Balança"),
    ("meio quilograma tem", "svg:balanca:500 g"),
    ("um quarto de quilograma", "svg:balanca:250 g"),
    ("quilograma e meio de cuscuz", "svg:balanca:1,5 kg"),
    ("laranja 203 g", "g:laranja, mamão e carambola lado a lado"),
    ("três frutas juntas", "g:laranja, mamão e carambola juntos numa balança de cozinha"),
    ("meio quilo de uvas", "g:uvas, morangos e ameixas na barraca da feira|Feira livre"),
    ("quarto de quilo de fruta custa", "g:uvas, morangos e ameixas na barraca da feira|Feira livre"),
    ("bebê tem 3 385 g", "svg:balanca:3385 g"),
    ("prato de comida de seu joão", "svg:balanca:1265 g"),
    ("1 250 g", "svg:balanca:1250 g"),
    ("dividindo 1 quilograma", "svg:balanca:1 kg"),
    ("meio quilo e um quarto de quilo", "svg:balanca:500 g"),
    # Matemática — capacidade
    ("mililitros tem 1 litro", "svg:jarra:1000"),
    ("garrafa de 5 litros", "g:garrafão de água de 5 litros|Garrafão"),
    ("copos de 250 ml", "svg:jarra:250"),
    ("1 000 ml de água igualmente entre 4", "svg:jarra:1000"),
    ("500 ml divididos por 2", "svg:jarra:500"),
    ("400 ml é menos", "svg:jarra:400"),
    ("meio litro tem", "svg:jarra:500"),
    ("um quarto de litro tem", "svg:jarra:250"),
    ("encheu 5 copos", "g:jarra de suco e cinco copos iguais|Jarra"),
    ("2 garrafas de 450 ml", "g:duas garrafinhas de água iguais|Garrafa"),
    ("bolo leva um litro e meio", "g:bolo de maçã|Bolo"),
    ("bebedouro do caramelo", "g:cão-guia labrador bebendo água numa vasilha|Cão-guia"),
    ("dividindo 1 litro", "svg:jarra:1000"),
    ("dois copos de meio litro", "svg:jarra:500"),
    ("meio litro e um quarto de litro", "svg:jarra:500"),
    # Matemática — dobro, triplo, metade e terça parte
    ("dobro de 4", "svg:pontos:4:2"),
    ("triplo de 4", "svg:pontos:4:3"),
    ("30 sanduíches", "g:sanduíches e seis bandejas vazias|Sanduíche"),
    ("metade de 10", "svg:dividir:10:2"),
    ("terça parte de 9", "svg:dividir:9:3"),
    ("terça parte de 12", "svg:dividir:12:3"),
    ("lavar a louça", "g:pia com louça suja e torneira aberta|Pia"),
    ("entre ele e três amigos", "g:garrafa de água e quatro copos vazios|Copo"),
    ("terça parte é dividir", "svg:partes:3"),
]

# palavras de geometria → desenho, para atividades novas (ex.: criadas pelo Gemini)
_GEOMETRIA = [
    ("pirâmide de base pentagonal", "svg:piramide:5"), ("pirâmide de base hexagonal", "svg:piramide:6"),
    ("pirâmide de base triangular", "svg:piramide:3"), ("pirâmide", "svg:piramide:4"),
    ("paralelepípedo", "svg:paralelepipedo"), ("prisma", "svg:prisma:3"), ("cubo", "svg:cubo"),
    ("cilindro", "svg:cilindro"), ("cone", "svg:cone"), ("esfera", "svg:esfera"),
]

PECAS = {norm(k): v for k, v in _P.items()}


def visual_peca(texto, extra=None):
    """Visual de uma peça de jogo. `extra` = mapa {texto: visual} vindo da própria atividade."""
    if extra:
        for k, v in extra.items():
            if norm(k) == norm(texto):
                return _spec(v)
    n = norm(texto)
    if n in PECAS:
        return PECAS[n]
    for chave, spec in _GEOMETRIA:
        if n == chave:
            return spec
    return None


def visual_enunciado(texto, extra=None):
    if extra:
        return _spec(extra)
    t = str(texto or "").lower()
    for trecho, spec in _E:
        if trecho in t:
            return spec
    for chave, spec in _GEOMETRIA:
        if re.search(r"\b" + re.escape(chave) + r"\b", t):
            return spec
    return None


def _spec(v):
    """Uma descrição livre (vinda do Gemini) vira pedido de imagem gerada."""
    v = str(v or "").strip()
    if not v:
        return None
    return v if v.startswith(("g:", "w:", "svg:")) else "g:" + v


def textos_da_atividade(tipo, d):
    """(enunciado, [peças]) de uma atividade."""
    if tipo in ("ligar", "memoria"):
        return d.get("titulo", ""), [x for p in d.get("pares", []) for x in p]
    if tipo == "ordenar":
        return d.get("titulo", ""), list(d.get("itens", []))
    if tipo == "categorizar":
        return d.get("titulo", ""), [i["texto"] for i in d.get("itens", [])]
    if tipo == "quiz":
        return d.get("pergunta", ""), list(d.get("opcoes", []))
    if tipo == "completar":
        return d.get("frase", ""), []
    if tipo == "vf":
        return d.get("afirmacao", ""), []
    if tipo == "contas":
        return d.get("pergunta", ""), []
    if tipo == "flashcard":
        return d.get("frente", ""), []
    return "", []


def visuais_da_atividade(tipo, d):
    """{'enunciado': spec|None, 'pecas': {texto: spec}}"""
    enun, pecas = textos_da_atividade(tipo, d)
    extra = d.get("imagens") if isinstance(d.get("imagens"), dict) else None
    ve = None
    if tipo not in ("ligar", "memoria", "ordenar", "categorizar"):
        ve = visual_enunciado(enun, d.get("imagem"))
    vp = {}
    for p in pecas:
        s = visual_peca(p, extra)
        if s:
            vp[p] = s
    # nos jogos de pares, se os dois lados teriam a mesma imagem, fica só no primeiro lado
    if tipo in ("ligar", "memoria"):
        for a, b in d.get("pares", []):
            if a in vp and b in vp and vp[a] == vp[b]:
                del vp[b]
    return {"enunciado": ve, "pecas": vp}


def specs_de_imagem(tipo, d):
    """Pedidos que precisam de imagem (Gemini ou Wikipédia), sem os desenhos svg."""
    v = visuais_da_atividade(tipo, d)
    todos = ([v["enunciado"]] if v["enunciado"] else []) + list(v["pecas"].values())
    return [s for s in todos if s.startswith(("g:", "w:"))]
