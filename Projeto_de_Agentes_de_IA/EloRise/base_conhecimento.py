"""
base_conhecimento.py — Base de conhecimento própria do tutor (conceitos de League of
Legends), consultável pelo agente para fundamentar a mentoria e os planos de treino.

É a FONTE DE VERDADE tática: ataca a alucinação de CONCEITOS (os guard rails existentes
só cobrem números). O corpus é curado e estruturado; a busca (Opção A) é por palavra-chave
e pode ser trocada por busca semântica (Opção B, rag.py) mantendo a mesma interface.
"""
import re
import json
import unicodedata
from pathlib import Path

from config import METRIC_LABELS, ROLE_LABELS

# Conhecimento factual gerado do Data Dragon (itens/runas/campeões/feitiços).
# Produzido por `datadragon.py`; opcional — se não existir, a base usa só o curado.
_ARQ_DDRAGON = Path(__file__).resolve().parent / "conhecimento_datadragon.json"


# ──────────────────────────────────────────────
# Corpus curado: cada entrada é um trecho autocontido de conhecimento.
# topico padronizado: "rota:<ROTA>", "macro", "metrica:<m>", "conceito:<x>",
#                     "itemizacao", "runas", "erros_elo:<ELO>".
# tags inclui sinônimos/jargões para a busca por palavra-chave casar paráfrases.
# ──────────────────────────────────────────────
CONHECIMENTO: list[dict] = [
    # ---- Conceitos de macro ----
    {
        "id": "macro_wave",
        "titulo": "Wave management (Gestão de Ondas)",
        "topico": "conceito:wave",
        "tags": ["wave", "onda", "leva", "minions", "freeze", "congelar", "slow push",
                 "fast push", "empurrar", "segurar", "lane", "rota", "farm"],
        "texto": ("Controlar a onda de minions dita o ritmo do jogo. "
                  "COMO FAZER FREEZE (Congelar): Deixe exatamente 3 a 4 minions magos inimigos vivos fora do alcance da sua torre. Dê apenas o 'last hit' no último milissegundo. O freeze nega farm ao inimigo e o expõe a ganks. "
                  "COMO FAZER SLOW PUSH: Mate apenas os minions magos da leva inimiga e deixe os guerreiros. Sua onda vai acumular 2 ou 3 levas, criando um exército perfeito para um dive ou para ganhar tempo para um objetivo. "
                  "COMO FAZER FAST PUSH: Use todas as suas habilidades em área (AoE) para limpar a leva instantaneamente. Faça isso APENAS antes de ir base (recall), rotacionar (roam) ou se o inimigo não estiver na rota, para que a onda bata na torre e ele perca o XP/Ouro."),
    },
    {
        "id": "macro_rotacao",
        "titulo": "Rotação e Roam (Sair da Rota)",
        "topico": "macro",
        "tags": ["rotacao", "rotacionar", "roam", "roaming", "girar", "mapa", "presenca",
                 "ajudar", "gank", "mid", "atirador", "suporte"],
        "texto": ("Roam é criar vantagem numérica no mapa, mas deve ser feito sem perder recursos. "
                  "COMO EXECUTAR O ROAM PERFEITO: 1) Faça um Fast Push para jogar sua onda na torre inimiga. 2) Entre na névoa de guerra (fog) pelo rio. 3) Avalie no meio do caminho: a rota alvo está avançada? Se sim, continue e execute o gank. Se o inimigo recuou, aborte imediatamente e volte para a sua rota. "
                  "REGRA DE OURO: Um roam não pode durar mais do que 30 segundos, caso contrário você perderá a próxima onda de minions na sua própria rota, transformando um gank bem-sucedido em um prejuízo de XP."),
    },
    {
        "id": "macro_visao",
        "titulo": "Visão e Controle de Objetivos",
        "topico": "macro",
        "tags": ["visao", "ward", "sentinela", "wards", "controle", "dragao", "arauto",
                 "baron", "objetivo", "objetivos", "trinket", "varredura", "sweeper", "pink"],
        "texto": ("Ter visão não é só colocar wards aleatórias, é iluminar o próximo objetivo. "
                  "COMO CONTROLAR A VISÃO: 1) Timing: Posicione as sentinelas entre 45 a 30 segundos ANTES do Dragão/Barão nascer. 2) Posicionamento: Não warde apenas o covil; warde os 'choke points' (entradas da selva inimiga) para ver o inimigo chegando. "
                  "COMO LIMPAR VISÃO: Ao usar a Lente do Oráculo (Sweeper), ande em zigue-zague pelas entradas. Sempre coloque uma Sentinela de Controle (Pink Ward) no fundo do covil do objetivo para garantir que o inimigo não tenha visão durante a luta."),
    },
    {
        "id": "macro_tempo",
        "titulo": "Controle de Tempo (Tempos de Base e Powerspikes)",
        "topico": "macro",
        "tags": ["tempo", "timing", "recall", "base", "powerspike", "pico de poder",
                 "canhao", "back", "compra", "tilt"],
        "texto": ("O 'Tempo' em LoL é a janela de oportunidade que você tem para agir antes do inimigo. "
                  "COMO DAR UM BOM RECALL (Ir base): O recall perfeito é feito empurrando uma onda de Catapa (Minion Canhão) para a torre inimiga. Como o canhão aguenta muitos tiros da torre, você ganha tempo suficiente para ir à base, comprar seus itens e voltar andando para a rota sem perder nenhum minion da próxima leva. "
                  "POWER SPIKES: Pressione TAB e olhe o inventário. Nunca inicie uma luta se você tem 2000 de ouro na bolsa e o inimigo acabou de voltar da base com um item completo. Lute apenas após gastar seu ouro."),
    },
    {
        "id": "itemizacao",
        "titulo": "Itemização Adaptativa e Situacional",
        "topico": "itemizacao",
        "tags": ["item", "itens", "itemizacao", "build", "construcao", "resistencia magica",
                 "armadura", "antcura", "anti-cura", "antiheal", "defensivo", "situacional", "corta cura"],
        "texto": ("Comprar itens no automático é o maior erro de adaptação. "
                  "COMO ITEMIZAR CORRETAMENTE: Pressione TAB e identifique QUEM está forte (com mais ouro/abates) no time inimigo, não apenas a composição geral. Se um Mago Assassino está 5/0, faça itens de Resistência Mágica (ex: Hexdrinker, Passos de Mercúrio) imediatamente, antes de fechar seu item de dano. "
                  "COMO USAR ANTI-CURA: Compre o componente básico de corta-cura (Chamado do Carrasco, Colete Espinhoso ou Orbe do Oblívio) no início do jogo se enfrentar campeões de cura massiva (Aatrox, Soraka, Sylas). MAS ATENÇÃO: não evolua esse componente para o item completo até o late game. Os status do item completo têm baixo custo-benefício."),
    },
    {
        "id": "runas",
        "titulo": "Runas: Escolha por Matchup",
        "topico": "runas",
        "tags": ["runa", "runas", "primaria", "secundaria", "fragmentos", "matchup",
                 "contra", "poke", "anti-poke", "sustain", "resolve", "precisao",
                 "dominacao", "feiticaria"],
        "texto": ("Runas devem responder à seguinte pergunta: 'Como eu sobrevivo ou ganho essa rota específica?'. "
                  "COMO ESCOLHER RUNAS: Se você vai enfrentar um campeão de muito poke (que ataca à distância, como Xerath ou Teemo), escolha a árvore de Determinação (Ventos Revigorantes) ou feitiços de roubo de vida. "
                  "FRAGMENTOS: Sempre adapte os fragmentos menores de status. Jogue de Armadura contra dano físico e Resistência Mágica contra dano mágico. Nunca jogue no automático copiando de sites."),
    },

    # ---- Conceitos por rota ----
    {
        "id": "rota_top",
        "titulo": "Top: 1v1, Controle de Wave e Split Push",
        "topico": "rota:TOP",
        "tags": ["top", "topo", "ilha", "tp", "teleporte", "split", "split push", "1v1",
                 "trade", "trades", "duelo", "tank", "bruiser", "pressao"],
        "texto": ("O Top é a rota mais punitiva do jogo. Um erro de wave pode acabar com sua partida. "
                  "COMO JOGAR A ROTA: Nunca lute (trade) se a onda de minions do inimigo for maior que a sua. Os minions causam dano massivo nos níveis 1 a 4. "
                  "COMO FAZER SPLIT PUSH: O objetivo não é apenas bater na torre, é dividir o mapa. Avance a sua rota APENAS quando o seu time estiver posicionado para pegar o Dragão ou pressionar o lado oposto do mapa. Se inimigos sumirem do mapa, recue para a névoa de guerra e espere eles aparecerem no meio/bot para voltar a pressionar."),
    },
    {
        "id": "rota_jungle",
        "titulo": "Selva: Pathing, Rastreamento e Ganks",
        "topico": "rota:JUNGLE",
        "tags": ["jungle", "selva", "jungler", "clear", "pathing", "rota da selva", "gank",
                 "ganks", "contra-gank", "objetivo", "dragao", "arauto", "invade", "tracking"],
        "texto": ("O Caçador é o maestro do jogo inicial. "
                  "COMO DEFINIR O PATHING (Rota de Farm): Na tela de carregamento, identifique qual rota sua tem controle de grupo (Stun/Enraizamento) e qual rota inimiga é frágil (sem mobilidade). Comece o seu farm no lado OPOSTO do mapa para terminar o seu percurso exatamente perto dessa rota vulnerável. "
                  "COMO RASTREAR O CAÇADOR INIMIGO: Olhe para o minimapa no nível 1. A rota inimiga que chegar atrasada na lane foi a que ajudou o caçador no primeiro monstro (leash). Sabendo onde ele começou, você prevê que ele estará no lado oposto do mapa aos 3 minutos para disputar o Aronguejo."),
    },
    {
        "id": "rota_mid",
        "titulo": "Meio: Prioridade, Controle de Magia e Rio",
        "topico": "rota:MIDDLE",
        "tags": ["mid", "meio", "middle", "prioridade", "prio", "roam", "wave", "side",
                 "lateral", "burst", "controle", "rio", "nível 2", "level 2"],
        "texto": ("O Meio é a rota mais curta, a chave aqui é ditar o ritmo do mapa. "
                  "COMO GARANTIR PRIORIDADE (Prio): Use suas habilidades não no campeão inimigo, mas nos minions assim que a rota começar para atingir o nível 2 antes dele (é necessário a primeira onda inteira + 1 minion guerreiro da segunda onda). Quem pega nível 2 primeiro, ganha a prioridade da rota e o controle do rio. "
                  "COMO JOGAR NO MID GAME: Após cair a primeira torre, você não deve ficar dividindo farm com seu ADC no meio. Vá para a rota lateral (side lane), limpe a onda passando do meio do mapa, e então caminhe para perto do seu time na selva para flanquear lutas ou garantir visão."),
    },
    {
        "id": "rota_bot",
        "titulo": "Atirador (ADC): Posicionamento, Kiting e Sobrevivência",
        "topico": "rota:BOTTOM",
        "tags": ["adc", "atirador", "bot", "bottom", "carry", "farm", "cs",
                 "posicionamento", "kite", "kiting", "teamfight", "dps", "dano", "espaçamento"],
        "texto": ("O Atirador é a principal fonte de Dano por Segundo (DPS) contínuo do time. "
                  "COMO FAZER KITING: Nunca fique parado atirando (Isso o torna um alvo fácil para magias de controle). O ciclo correto é: Clique no inimigo (Ataque) -> Clique no chão para se afastar (Movimento) durante a animação de recarga do seu ataque básico -> Repita. "
                  "COMO SE POSICIONAR EM LUTAS: Seu alvo NÃO é obrigatoriamente o atirador ou mago inimigo. Seu alvo é o campeão inimigo MAIS PRÓXIMO de você. Se o tanque inimigo pular em você, bata no tanque. Sobreviver para continuar causando DPS seguro é melhor do que morrer tentando um abate milagroso."),
    },
    {
        "id": "rota_sup",
        "titulo": "Suporte: Presença na Rota, Peel vs Engage",
        "topico": "rota:UTILITY",
        "tags": ["suporte", "support", "sup", "utility", "visao", "ward", "roam", "engage",
                 "peel", "proteger", "carry", "cc", "controle de grupo", "brush"],
        "texto": ("O Suporte carrega a fase de rotas inicial. Ficar atrás do seu ADC sem fazer nada é o erro mais passivo possível. "
                  "COMO DOMINAR A ROTA: Controle os arbustos (brushes). Fique andando dentro dos arbustos laterais para ameaçar o inimigo e tirar a pressão do seu atirador. Mantenha o 'Triângulo da Rota': você e seu ADC devem estar na mesma linha horizontal imaginária. "
                  "COMO LUTAR (PEEL vs ENGAGE): Em lutas de equipe, avalie a composição inimiga. Se eles possuem um assassino focado no seu Atirador, guarde TODAS as suas habilidades de Controle (Stun/Slow) para parar esse assassino (Isso se chama Peel). Se eles não tiverem assassinos, use seu CC para iniciar a luta no alvo vulnerável (Engage)."),
    },
    # Os erros comuns por elo agora vivem em ERROS_COMUNS_POR_ELO (separados por tier) e
    # entram no corpus de busca via _entradas_erros_elo().
]


# ──────────────────────────────────────────────
# Erros mais comuns SEPARADOS por elo (um por tier, do Ferro ao Challenger). Usados como
# "dicas extras" na aba de Evolução e indexados no RAG. Cada item: 2 erros/correções curtas.
# ──────────────────────────────────────────────
ERROS_COMUNS_POR_ELO: dict[str, dict] = {
    "IRON": {"nome": "Ferro", "dicas": [
        "Jogue mais seguro: no Ferro, cada morte custa caro. Evite arriscar e farme com calma.",
        "Treine dar o último golpe nos minions — um farm constante já te tira do Ferro.",
    ]},
    "BRONZE": {"nome": "Bronze", "dicas": [
        "Pare de avançar demais sem visão: a maioria das mortes vem de ser pego com o caçador fora do mapa.",
        "Compre uma Sentinela de Controle toda vez que voltar à base — visão simples evita muita morte.",
    ]},
    "SILVER": {"nome": "Prata", "dicas": [
        "Depois dos 15 minutos, não fique se agrupando no meio à toa: vá farmar uma rota lateral segura.",
        "Escolha 1 ou 2 campeões e repita — trocar de campeão toda partida trava sua evolução.",
    ]},
    "GOLD": {"nome": "Ouro", "dicas": [
        "Converta abates em vantagem: depois de matar, empurre a onda ou pegue um objetivo, não volte pra base no automático.",
        "Não lute por lutar: só gaste seus feitiços quando houver um objetivo ou uma torre em jogo.",
    ]},
    "PLATINUM": {"nome": "Platina", "dicas": [
        "Melhore o tempo de objetivo: esteja perto do dragão/arauto antes de ele nascer, com a onda empurrada.",
        "Pare de entrar em luta em desvantagem numérica: cheque o minimapa antes de iniciar.",
    ]},
    "EMERALD": {"nome": "Esmeralda", "dicas": [
        "Trabalhe o controle de ondas (congelar e empurrar na hora certa) pra criar vantagem sem depender de abate.",
        "Acompanhe o Flash do oponente e jogue mais agressivo enquanto ele está sem o feitiço.",
    ]},
    "DIAMOND": {"nome": "Diamante", "dicas": [
        "Refine o macro: saiba trocar pressão (abrir mão de uma torre pra pegar um objetivo maior).",
        "Reduza erros de posicionamento em luta — neste elo, um passo errado já decide o combate.",
    ]},
    "MASTER": {"nome": "Mestre", "dicas": [
        "Busque consistência: o nível alto vem de errar menos, não de jogadas brilhantes. Diminua as partidas ruins.",
        "Domine o estado das ondas e o tempo de volta pra base pra nunca perder farm nem tempo de mapa.",
    ]},
    "GRANDMASTER": {"nome": "Grão-Mestre", "dicas": [
        "Lidere o time: comunique tempos de objetivo e habilidades importantes em recarga.",
        "Adapte itens e runas a cada partida — no topo, esse ajuste fino faz diferença.",
    ]},
    "CHALLENGER": {"nome": "Challenger", "dicas": [
        "A margem é mínima: foque em constância mental e em revisar replays com frequência.",
        "Antecipe o macro do inimigo: leia as rotações e prepare flancos antes de a luta começar.",
    ]},
}


def _tier_do_elo(elo: str) -> str:
    """Extrai o tier principal (IRON, GOLD, MASTER, ...) de um elo como 'GOLD_II'."""
    return (elo or "").upper().split("_")[0]


def erros_comuns_do_elo(elo: str) -> dict | None:
    """Erros mais comuns do tier do jogador: {'nome': 'Ouro', 'dicas': [...]} ou None."""
    return ERROS_COMUNS_POR_ELO.get(_tier_do_elo(elo))


def _entradas_erros_elo() -> list[dict]:
    """Indexa os erros comuns de cada elo no corpus de busca (um documento por tier)."""
    entradas = []
    for tier, info in ERROS_COMUNS_POR_ELO.items():
        entradas.append({
            "id": f"erros_elo_{tier.lower()}",
            "titulo": f"Erros Comuns no elo {info['nome']}",
            "topico": f"erros_elo:{tier}",
            "tags": ["erro", "erros", "comum", "comuns", info["nome"].lower(), tier.lower()],
            "texto": f"Erros mais comuns no elo {info['nome']} e como corrigir: "
                     + " ".join(info["dicas"]),
        })
    return entradas


# ──────────────────────────────────────────────
# Drills por métrica (consolidados aqui como fonte única; usados pelo plano de treino
# e expostos na base como entradas "metrica:<m>").
# ──────────────────────────────────────────────
# Cada drill é uma META principal + sub-metas concretas (cada uma vira uma caixinha na UI;
# quando todas as sub-metas são marcadas, a meta principal conclui sozinha). Linguagem
# simples, voltada ao jogador comum.
DRILLS: dict[str, list[dict]] = {
    "kda": [
        {"tema": "minimapa",
         "meta": "Olhe o minimapa a cada poucos segundos pra não ser pego de surpresa.",
         "submetas": [
             "Dê uma olhada no minimapa toda vez que der o último golpe num minion.",
             "Se o caçador inimigo some do mapa, recue e jogue assumindo que ele vem pra cima de você.",
         ]},
        {"tema": "flash_seguro",
         "meta": "Guarde o Flash pra escapar, não pra forçar um abate arriscado.",
         "submetas": [
             "Antes de gastar o Flash atacando, confirme onde estão os 5 inimigos.",
             "No Modo Prática, treine seus combos com Flash até saírem sem você pensar.",
         ]},
        {"tema": "teto_mortes",
         "meta": "Estabeleça um teto de mortes e respeite durante a partida.",
         "submetas": [
             "Mire em no máximo 4 mortes nas próximas 3 partidas.",
             "Ao chegar perto desse teto, jogue recuado em vez de buscar troca.",
         ]},
        {"tema": "iniciar_troca",
         "meta": "Só inicie uma troca quando tem vantagem clara.",
         "submetas": [
             "Espere o inimigo errar ou gastar a habilidade principal pra então atacar.",
             "Evite trocar quando a onda está do lado dele — é onde você mais leva gank.",
         ]},
        {"tema": "posicao_luta", "requer": ["Marksman", "Mage", "adc_mago", "sup_protetor", "sup_mago"],
         "meta": "Em lutas em equipe, fique na borda, nunca no meio do time inimigo.",
         "submetas": [
             "Posicione-se atrás da sua linha de frente, perto de uma rota de fuga.",
             "Não corra pro meio do time inimigo atrás de um único abate.",
         ]},
    ],
    "cs_min": [
        {"tema": "treino_lasthit",
         "meta": "Treine o último golpe (last hit) no Modo Prática todo dia.",
         "submetas": [
             "10 minutos por dia mirando 80 de farm aos 10 min só com ataque básico.",
             "Quando bater a meta, repita usando também as habilidades.",
         ]},
        {"tema": "farm_sob_pressao",
         "meta": "Pegue o farm mesmo quando o inimigo está te ameaçando.",
         "submetas": [
             "Dê o último golpe no instante em que ele iria te bater — assim ele não revida.",
             "Foque a barra de vida dos minions e deixe o inimigo na visão periférica.",
         ]},
        {"tema": "nao_largar_onda",
         "meta": "Não abandone farm que dá pra pegar.",
         "submetas": [
             "Antes de sair pra ajudar outra rota, empurre a onda que vem pra sua torre.",
             "Só troque farm por roam quando o roam rende abate ou objetivo.",
         ]},
        {"tema": "farm_pos_rota",
         "meta": "Continue farmando no meio e fim de jogo, não só na rota.",
         "submetas": [
             "Sem luta acontecendo, limpe ondas das laterais em vez de ficar parado.",
             "Não deixe ondas baterem de graça na sua torre — é ouro perdido.",
         ]},
    ],
    "ouro_min": [
        {"tema": "recall_com_ouro",
         "meta": "Volte pra base só quando fecha um item que faz diferença.",
         "submetas": [
             "Decore o preço dos seus 3 itens principais pra decidir rápido.",
             "Pare de voltar pra base com pouco ouro e sem comprar peça forte.",
         ]},
        {"tema": "placas_torre",
         "meta": "Pegue as placas da torre (cada uma dá ouro extra).",
         "submetas": [
             "Depois de forçar o oponente a recuar, empurre e leve pelo menos 1 placa.",
             "Mire em 3 ou mais placas por partida e confira o total no fim.",
         ]},
        {"tema": "ouro_parado",
         "meta": "Não ande com ouro parado: gaste assim que fechar uma peça.",
         "submetas": [
             "Compre na primeira ida à base em que dá pra fechar um item de impacto.",
             "Ouro guardado no bolso não dá vantagem nenhuma na luta.",
         ]},
        {"tema": "limpar_mapa_ouro",
         "meta": "No meio e fim de jogo, não fique parado no meio do mapa.",
         "submetas": [
             "Sem dragão ou barão no próximo minuto, vá limpar uma rota lateral.",
             "Evite ficar agrupado com o time sem um objetivo claro.",
         ]},
    ],
    "visao_min": [
        {"tema": "sentinela_controle",
         "meta": "Tenha sempre uma Sentinela de Controle (rosa) ativa no mapa.",
         "submetas": [
             "Compre 1 toda vez que voltar à base e reserve um slot pra ela.",
             "Mantenha pelo menos uma ativa num ponto de passagem o tempo todo.",
         ]},
        {"tema": "ward_objetivo",
         "meta": "Coloque visão ANTES do objetivo nascer, não depois.",
         "submetas": [
             "De 45 a 30s antes do dragão/arauto, warde o rio e a entrada da selva inimiga.",
             "Decore esses pontos num personalizado pra wardar rápido sem perder farm.",
         ]},
        {"tema": "limpar_visao",
         "meta": "Destrua a visão do inimigo, não só coloque a sua.",
         "submetas": [
             "Use a Sentinela de Controle e a Lente do Oráculo pra limpar wards inimigas.",
             "Limpe o caminho por onde o time vai passar, não só em cima do objetivo.",
         ]},
    ],
    "dano_min": [
        {"tema": "foco_alvo",
         "meta": "Na luta, ataque quem dá pra alcançar com segurança, não o alvo mais no fundo.",
         "submetas": [
             "Mire primeiro a ameaça mais próxima de você.",
             "Nunca seja o jogador mais avançado do seu time numa luta.",
         ]},
        {"tema": "power_spike",
         "meta": "Force as lutas no seu pico de poder.",
         "submetas": [
             "Descubra em que nível e itens o seu campeão fica mais forte.",
             "Provoque as lutas nesse pico e evite-as quando estiver fraco.",
         ]},
        {"tema": "kiting", "requer": ["Marksman", "adc"],
         "meta": "Treine o atacar-e-andar (kiting) até virar automático.",
         "submetas": [
             "No Modo Prática, alterne ataque e movimento por 10 min sem parar de andar.",
             "Na luta, dê um passo após cada ataque em vez de ficar parado batendo.",
         ]},
        {"tema": "poke", "requer": ["Mage", "mid_control_mage", "adc_mago", "sup_mago", "Marksman"],
         "meta": "Machuque os inimigos antes da luta começar.",
         "submetas": [
             "Use suas habilidades de longe pra tirar 20% a 30% da vida antes do confronto.",
             "Mire o inimigo-chave pra ele chegar na luta já fraco.",
         ]},
    ],
    "dano_objetivos": [
        {"tema": "converter_vantagem",
         "meta": "Transforme vantagem em objetivo (dragão ou arauto).",
         "submetas": [
             "Após um abate ou luta vencida, dê ping e comece o objetivo com o time.",
             "Conte quantos objetivos você ajudou a começar por partida e tente aumentar.",
         ]},
        {"tema": "timing_objetivo",
         "meta": "Comece o objetivo quando o caçador inimigo está longe.",
         "submetas": [
             "Inicie o objetivo do seu lado assim que o caçador inimigo aparece do outro lado.",
             "Num personalizado, veja quanto da vida do objetivo seu time tira por segundo.",
         ]},
        {"tema": "setup_seguro",
         "meta": "Só comece o objetivo com o caminho seguro.",
         "submetas": [
             "Empurre as ondas das rotas vizinhas antes de bater no dragão/barão.",
             "Confirme no mapa que os inimigos não têm como chegar pra contestar.",
         ]},
    ],
    "dano_torres": [
        {"tema": "onda_canhao_torre",
         "meta": "Use a onda com o minion de canhão pra bater na torre.",
         "submetas": [
             "Espere o canhão: ele segura os tiros da torre e te dá tempo de bater.",
             "Aprenda quando o canhão chega (a cada 3 ondas no começo) pra planejar.",
         ]},
        {"tema": "luta_vira_torre",
         "meta": "Toda luta vencida deve virar torre ou objetivo.",
         "submetas": [
             "Depois de uma luta ganha, agrupe e leve a torre na hora, em vez de recuar.",
             "Não deixe nenhuma luta vencida acabar 'em nada'.",
         ]},
        {"tema": "arauto_torre", "requer": ["JUNGLE"],
         "meta": "Use o Arauto onde ele derruba a primeira torre.",
         "submetas": [
             "Solte o Arauto na rota mais perto de cair a primeira torre.",
             "Treine soltar e recolher o Arauto num personalizado pra não desperdiçar.",
         ]},
    ],
    "kpa": [
        {"tema": "presenca_lutas",
         "meta": "Esteja presente nas brigas do time.",
         "submetas": [
             "Programe-se pelo mapa: esteja perto quando uma luta por objetivo for começar.",
             "Tente estar nas 3 primeiras lutas de objetivo da partida.",
         ]},
        {"tema": "roam", "requer": ["TOP", "MIDDLE", "BOTTOM", "UTILITY"],
         "meta": "Ajude as outras rotas quando elas estão lutando.",
         "submetas": [
             "Empurre sua onda e role pra topo/base pegar abates que não viriam na sua rota.",
             "Decore bons pontos de chegada, a pé ou de Teleporte.",
         ]},
        {"tema": "nao_andar_sozinho",
         "meta": "Não ande sozinho no meio do jogo.",
         "submetas": [
             "Ande junto dos aliados em vez de ir sozinho pra selva.",
             "Reveja no replay onde você se separou do grupo e morreu.",
         ]},
    ],
}

DRILLS_GENERICO: list[dict] = [
    {"tema": "replay",
     "meta": "Aprenda com seus erros assistindo ao replay.",
     "submetas": [
         "Reveja suas últimas 3 partidas e pause em cada morte sua.",
         "Anote a causa que mais se repete e leve só UMA correção pra próxima partida.",
     ]},
    {"tema": "meta_partida",
     "meta": "Defina uma meta simples antes de cada partida.",
     "submetas": [
         "Antes de entrar na fila, escolha UMA meta (ex.: não morrer nos 10 primeiros minutos).",
         "No fim, avalie se cumpriu — não importa se ganhou ou perdeu.",
     ]},
]


# Banco extra de drills: amplia o repertório de cada métrica (para REGENERAR trazer drills
# diferentes) E cobre as métricas/arquétipos específicos. Cada drill pode declarar `requer`
# (etiquetas de rota/classe/arquétipo) — só entra no plano se casar com o jogador (ver
# plano_treino._drill_aplicavel). Mesclado em DRILLS no carregamento do módulo; chaves novas
# (métricas sem banco base) passam a existir via setdefault.
_DRILLS_EXTRA: dict[str, list[dict]] = {
    "cs_min": [
        {"tema": "farm_sob_torre",
         "meta": "Aprenda a farmar embaixo da sua própria torre.",
         "submetas": [
             "Minion corpo a corpo: deixe a torre bater 2 vezes e finalize.",
             "Minion de longe: deixe a torre bater 1 vez e dê o último golpe.",
         ]},
        {"tema": "onda_canhao",
         "meta": "Não perca a onda de canhão (ela vale mais ouro).",
         "submetas": [
             "Evite voltar pra base exatamente na onda que traz o minion de canhão.",
             "Limpe a onda de canhão antes de recuar.",
         ]},
        {"tema": "progressao_treino",
         "meta": "Aumente a dificuldade do treino de farm aos poucos.",
         "submetas": [
             "Comece dando last hit sem habilidade; quando acertar ~90%, dificulte.",
             "Só suba de nível (sob pressão, se movendo) quando mantiver a precisão.",
         ]},
    ],
    "cs_rota_10m": [
        {"tema": "meta_cs10",
         "meta": "Mire numa meta clara de farm aos 10 minutos.",
         "submetas": [
             "Combine de bater 70 a 80 de CS aos 10 min sem morrer.",
             "Confira o número no fim de cada partida e ajuste pra próxima.",
         ]},
        {"tema": "trade_e_farm",
         "meta": "Troque dano sem perder o próximo último golpe.",
         "submetas": [
             "Bata no inimigo no mesmo movimento em que ia dar o last hit.",
             "Não largue 2 ou 3 minions só pra acertar um ataque a mais nele.",
         ]},
        {"tema": "controle_onda_lane",
         "meta": "Controle a onda pra farmar seguro nos 10 primeiros minutos.",
         "submetas": [
             "Empurre só quando quer recuar ou roamar; senão, segure a onda.",
             "Onda parada perto da sua torre é farm protegido e menos gank.",
         ]},
    ],
    "cs_jungle_10m": [
        {"tema": "clear_eficiente", "requer": ["JUNGLE"],
         "meta": "Limpe a selva rápido sem tomar dano à toa.",
         "submetas": [
             "Treine a ordem de clear do seu campeão no Modo Prática.",
             "Use as habilidades pra reduzir o dano que os monstros te causam.",
         ]},
        {"tema": "full_clear_vs_gank", "requer": ["JUNGLE"],
         "meta": "Decida entre clear cheio e gank pelo estado das rotas.",
         "submetas": [
             "Com as rotas empurradas pra você, faça full clear e suba de nível.",
             "Com uma rota com prioridade e inimigo avançado, gankeie cedo.",
         ]},
        {"tema": "nao_perder_camps", "requer": ["JUNGLE"],
         "meta": "Não deixe acampamentos prontos sem coletar.",
         "submetas": [
             "Passe pegando camps no caminho entre ganks e objetivos.",
             "Roube/limpe a selva inimiga quando o caçador deles está longe.",
         ]},
    ],
    "kda": [
        {"tema": "constancia_campeao",
         "meta": "Reduza mortes jogando poucos campeões que você domina.",
         "submetas": [
             "Escolha 1 ou 2 campeões e foque neles por várias partidas.",
             "Evite trocar de campeão a cada jogo: constância diminui erros.",
         ]},
        {"tema": "replay_mortes",
         "meta": "Descubra o padrão das suas mortes no replay.",
         "submetas": [
             "Reveja as últimas 3 partidas e pause em cada morte sua.",
             "Anote a causa que mais se repete e corrija só ela na próxima.",
         ]},
        {"tema": "assassino_saida", "requer": ["mid_assassino", "jg_assassino", "Assassin"],
         "meta": "Como assassino, planeje a saída ANTES de entrar.",
         "submetas": [
             "Confirme uma rota de fuga (Flash, dash ou parede) antes do all-in.",
             "Se não tem como sair vivo, espere o próximo ângulo em vez de forçar.",
         ]},
        {"tema": "tank_frontline", "requer": ["top_tank", "jg_tank", "Tank", "sup_engajador"],
         "meta": "Como linha de frente, sua morte tem que comprar a luta.",
         "submetas": [
             "Absorva o dano e o CC inimigo pra proteger seus carries.",
             "Não inicie 5v5 sem seus carries por perto pra capitalizar.",
         ]},
    ],
    "ouro_min": [
        {"tema": "timing_recall", "requer": ["TOP", "MIDDLE", "BOTTOM"],
         "meta": "Limpe a onda antes de voltar pra perder menos farm.",
         "submetas": [
             "Empurre a leva inteira logo antes de recuar.",
             "Nunca recue bem na onda de canhão — é a que dá mais ouro.",
         ]},
        {"tema": "freeze_ouro", "requer": ["TOP", "MIDDLE", "BOTTOM"],
         "meta": "Congele a onda pra farmar seguro e negar ouro ao inimigo.",
         "submetas": [
             "Segure a onda perto da sua torre dando só o último golpe.",
             "Assim você farma protegido e ainda tira farm do oponente.",
         ]},
        {"tema": "recall_objetivo",
         "meta": "Esteja com o ouro gasto e de volta antes dos objetivos.",
         "submetas": [
             "Programe o recall pra voltar 1 min antes de dragão/arauto/barão.",
             "Voltar na hora do objetivo custa prioridade e farm.",
         ]},
    ],
    "visao_min": [
        {"tema": "qualidade_ward",
         "meta": "Priorize qualidade da visão, não quantidade.",
         "submetas": [
             "Warde locais de passagem: rio, entradas da selva e arbustos-chave.",
             "Uma ward que vê movimento vale mais que três em canto morto.",
         ]},
        {"tema": "nao_acumular_cargas",
         "meta": "Não deixe as cargas de ward acumuladas no máximo.",
         "submetas": [
             "O trinket guarda 2 cargas — use e mantenha sempre recarregando.",
             "Carga parada é ward que você deixou de colocar na partida.",
         ]},
        {"tema": "ward_ofensiva",
         "meta": "Warde de forma ofensiva, no território inimigo.",
         "submetas": [
             "Coloque visão nas entradas da selva inimiga e perto dos buffs.",
             "Isso revela o caçador inimigo e diminui a adivinhação.",
         ]},
    ],
    "pink_wards": [
        {"tema": "comprar_rosa", "requer": ["UTILITY", "sup_engajador", "sup_protetor", "sup_mago"],
         "meta": "Compre uma Sentinela de Controle em toda ida à base.",
         "submetas": [
             "Reserve ouro pra 1 rosa sempre que voltar pra base.",
             "Reserve um slot do inventário só pra ela.",
         ]},
        {"tema": "posicionar_rosa", "requer": ["UTILITY", "sup_engajador", "sup_protetor", "sup_mago"],
         "meta": "Coloque a rosa onde ela sobrevive e nega visão.",
         "submetas": [
             "Ponha em arbustos do rio e entradas da selva, não no meio aberto.",
             "Perto de objetivos ela cega o inimigo e protege o seu setup.",
         ]},
        {"tema": "caçar_visao", "requer": ["UTILITY", "sup_engajador", "sup_protetor", "sup_mago"],
         "meta": "Use a rosa pra caçar a visão inimiga.",
         "submetas": [
             "Antes de um objetivo, limpe as wards da área com a rosa e a lente.",
             "Reponha a sua rosa assim que ela for destruída.",
         ]},
    ],
    "dano_min": [
        {"tema": "agressao",
         "meta": "Não jogue passivo demais: trocar dano rende mais que só sobreviver.",
         "submetas": [
             "Dê micro-passos pra frente e ataque em vez de recuar totalmente.",
             "Chegue cedo na luta e comece a causar dano de um ângulo seguro.",
         ]},
        {"tema": "auto_weave", "requer": ["Marksman", "adc", "top_lutador", "jg_lutador", "Fighter"],
         "meta": "Encaixe um ataque básico entre cada habilidade.",
         "submetas": [
             "No Modo Prática, bata num boneco alternando habilidade e ataque por 5 min.",
             "Repita até o ritmo sair sozinho e repare o dano total subir.",
         ]},
        {"tema": "espacamento", "requer": ["Marksman", "adc", "mid_control_mage", "adc_mago", "sup_mago", "Mage"],
         "meta": "Fique na borda do alcance do inimigo (controle a distância).",
         "submetas": [
             "Posicione-se no limite do seu alcance, fora do alcance da ameaça dele.",
             "Se ele avança, seu time pune; se não, você acerta de graça.",
         ]},
        {"tema": "control_mage_area", "requer": ["mid_control_mage", "adc_mago", "sup_mago", "Mage"],
         "meta": "Como mago, acerte habilidades em vários alvos de longe.",
         "submetas": [
             "Mire as habilidades de área onde 2 ou mais inimigos vão passar.",
             "Jogue no alcance máximo pra dar dano sem entrar no perigo.",
         ]},
        {"tema": "assassino_alvo", "requer": ["mid_assassino", "jg_assassino", "Assassin"],
         "meta": "Como assassino, escolha o alvo certo e elimine de uma vez.",
         "submetas": [
             "Foque o carry inimigo mais frágil e isolado, não o tanque.",
             "Espere ele gastar o Flash/escudo antes de iniciar o all-in.",
         ]},
        {"tema": "juggernaut_grudar", "requer": ["juggernaut", "top_lutador", "Fighter"],
         "meta": "Como lutador, grude no alvo e mantenha o dano constante.",
         "submetas": [
             "Use seu CC/lentidão pra não deixar o alvo sair do seu alcance.",
             "Mire quem está mais perto; não persiga quem você nunca alcança.",
         ]},
    ],
    "solo_kills": [
        {"tema": "vencer_matchup", "requer": ["TOP", "MIDDLE", "top_lutador", "top_carry", "mid_assassino", "juggernaut"],
         "meta": "Estude o seu confronto pra ganhar o 1v1 na rota.",
         "submetas": [
             "Saiba os níveis e itens em que você vence o oponente.",
             "Force a troca nesses picos e respeite o confronto fora deles.",
         ]},
        {"tema": "setup_solokill", "requer": ["TOP", "MIDDLE", "top_lutador", "top_carry", "mid_assassino", "juggernaut"],
         "meta": "Monte o solo kill com onda e cooldowns.",
         "submetas": [
             "Empurre a onda pra cima dele e ataque com as defensivas dele no CD.",
             "Acompanhe o Flash do oponente: com ele no CD, o all-in fica bem mais forte.",
         ]},
        {"tema": "punir_erro", "requer": ["TOP", "MIDDLE", "top_lutador", "top_carry", "mid_assassino"],
         "meta": "Puna cada erro de posicionamento do oponente.",
         "submetas": [
             "Quando ele dá um passo a mais pra farmar, encaixe seu combo na hora.",
             "Não dê o all-in às cegas — espere a brecha aparecer.",
         ]},
    ],
    "dano_objetivos": [
        {"tema": "prioridade_dragao",
         "meta": "Priorize os dragões que mais ajudam o seu time.",
         "submetas": [
             "Os bônus de dragão se acumulam — não os entregue de graça.",
             "Combine com o time qual contestar e qual deixar passar.",
         ]},
        {"tema": "visao_objetivo",
         "meta": "Garanta visão na área do objetivo antes de começar.",
         "submetas": [
             "Encha a região de Sentinelas de Controle pra cegar o inimigo.",
             "Visão de objetivo é tarefa do time todo, não só do caçador.",
         ]},
        {"tema": "erros_barao",
         "meta": "Evite os erros clássicos ao começar o barão.",
         "submetas": [
             "Não comece com ondas soltas nem sem visão na área.",
             "Não divida o time: ou todos focam o objetivo, ou todos lutam.",
         ]},
        {"tema": "smite_seguro", "requer": ["JUNGLE"],
         "meta": "Garanta o objetivo com o Smite e a visão certa.",
         "submetas": [
             "Treine o dano do Smite + do seu campeão pra saber a hora de smitar.",
             "Com o caçador inimigo por perto, warde os dois lados do objetivo antes.",
         ]},
    ],
    "dano_torres": [
        {"tema": "split_push", "requer": ["top_lutador", "top_carry", "juggernaut", "Fighter", "Assassin", "jg_lutador"],
         "meta": "Aprenda a empurrar sozinho numa lateral (split push).",
         "submetas": [
             "Vá pra uma rota sem defesa e empurre pra forçar o inimigo a responder.",
             "Só faça com visão no caminho — empurrar às cegas é perigoso.",
         ]},
        {"tema": "cerco_barao",
         "meta": "Aproveite o buff de barão pra cercar as torres.",
         "submetas": [
             "Depois do barão, agrupe e pressione o máximo de torres com os minions reforçados.",
             "Empurre junto dos minions, não na frente deles.",
         ]},
        {"tema": "forcar_escolha",
         "meta": "Force a escolha do inimigo com a onda empurrada.",
         "submetas": [
             "Empurre uma onda forte antes de bater na torre.",
             "O inimigo terá que escolher entre defender e perder farm.",
         ]},
    ],
    "pct_dano_time": [
        {"tema": "sobreviver_pra_dar_dano", "requer": ["BOTTOM", "adc", "adc_mago", "Marksman"],
         "meta": "Seu dano só conta se você sobrevive pra dá-lo.",
         "submetas": [
             "Posicione-se atrás do time e mire o alvo seguro mais próximo.",
             "Saia da luta vivo: dano dado morto não soma.",
         ]},
        {"tema": "itens_de_dano_primeiro", "requer": ["BOTTOM", "adc", "adc_mago", "mid_control_mage", "Marksman", "Mage"],
         "meta": "Priorize os itens que mais aumentam o seu dano.",
         "submetas": [
             "Feche os seus 2 primeiros itens de dano o quanto antes.",
             "Adie itens defensivos pra quando já tiver dano relevante.",
         ]},
        {"tema": "dano_continuo", "requer": ["BOTTOM", "adc", "Marksman"],
         "meta": "Dê dano contínuo na luta, não só uma rajada.",
         "submetas": [
             "Mantenha os ataques básicos saindo durante toda a luta.",
             "Não gaste tudo num alvo e some — fique batendo de um lugar seguro.",
         ]},
    ],
    "tempo_cc": [
        {"tema": "cc_no_alvo_certo", "requer": ["TOP", "JUNGLE", "UTILITY", "sup_engajador", "top_tank", "jg_tank", "Tank", "Fighter"],
         "meta": "Acerte o controle de grupo no alvo que decide a luta.",
         "submetas": [
             "Mire o CC no carry inimigo, não no tanque deles.",
             "Não gaste todo o CC de uma vez — escalone pra prender por mais tempo.",
         ]},
        {"tema": "engage_angulo", "requer": ["TOP", "JUNGLE", "UTILITY", "sup_engajador", "top_tank", "jg_tank", "Tank"],
         "meta": "Encontre o ângulo de iniciar antes de engajar.",
         "submetas": [
             "Use arbustos e visão pra pegar o inimigo desprevenido.",
             "Só inicie com o time pronto pra ir junto atrás de você.",
         ]},
        {"tema": "cc_chain", "requer": ["TOP", "JUNGLE", "UTILITY", "sup_engajador", "top_tank", "jg_tank", "Tank", "Fighter"],
         "meta": "Encadeie o controle de grupo com o time (CC chain).",
         "submetas": [
             "Combine quem dá o primeiro CC e quem dá o seguinte.",
             "Avise por ping antes de iniciar pra ninguém desperdiçar o seu CC.",
         ]},
    ],
    "dano_mitigado": [
        {"tema": "absorver_no_tempo", "requer": ["TOP", "UTILITY", "top_tank", "jg_tank", "Tank", "sup_engajador", "juggernaut"],
         "meta": "Como linha de frente, absorva o dano na hora certa.",
         "submetas": [
             "Entre quando o inimigo gasta as habilidades, pra comer o dano pelos carries.",
             "Recue pra regenerar e volte — não fique parado apanhando à toa.",
         ]},
        {"tema": "itens_resistencia", "requer": ["TOP", "UTILITY", "top_tank", "jg_tank", "Tank", "sup_engajador"],
         "meta": "Compre resistência contra a maior ameaça inimiga.",
         "submetas": [
             "Mais armadura se o dano forte é físico; mais resistência mágica se é mágico.",
             "Adapte a build à comp inimiga, não compre sempre os mesmos itens.",
         ]},
        {"tema": "corpo_entre", "requer": ["TOP", "UTILITY", "top_tank", "jg_tank", "Tank", "sup_engajador"],
         "meta": "Ponha o seu corpo entre o inimigo e o seu carry.",
         "submetas": [
             "Fique na frente pra bloquear investidas e habilidades no seu carry.",
             "Use o CC pra afastar quem tenta passar por você.",
         ]},
    ],
    "cura_total": [
        {"tema": "cura_no_carry", "requer": ["UTILITY", "sup_protetor", "Support"],
         "meta": "Gaste cura e escudo no carry, não em você.",
         "submetas": [
             "Priorize manter vivo quem está dando o dano do time.",
             "Não jogue o escudo cedo demais — espere o dano vir.",
         ]},
        {"tema": "peel_no_carry", "requer": ["UTILITY", "sup_protetor", "Support"],
         "meta": "Fique perto do carry pra protegê-lo (peel).",
         "submetas": [
             "Posicione-se junto do seu carry, não na frente caçando abate.",
             "Use suas habilidades pra afastar quem pula nele.",
         ]},
        {"tema": "timing_cura", "requer": ["UTILITY", "sup_protetor", "Support"],
         "meta": "Cure no momento de maior dano, não antes.",
         "submetas": [
             "Segure a cura/escudo até o pico do dano inimigo.",
             "Cura jogada cedo é cura desperdiçada.",
         ]},
    ],
    "kpa": [
        {"tema": "jogar_ultimate",
         "meta": "Jogue em volta da sua ultimate.",
         "submetas": [
             "Se a sua ult muda a luta, use-a pra participar dos confrontos importantes.",
             "Force presença quando ela está disponível.",
         ]},
        {"tema": "empurrar_antes", "requer": ["TOP", "MIDDLE", "BOTTOM", "UTILITY"],
         "meta": "Empurre a onda antes de ir pra uma luta.",
         "submetas": [
             "Deixe sua onda empurrada pra rotacionar sem perder farm.",
             "Chegar atrasado por causa de farm custa o abate.",
         ]},
        {"tema": "roam_mid", "requer": ["MIDDLE", "mid_assassino", "mid_control_mage"],
         "meta": "Do meio, role pras laterais pra criar vantagem.",
         "submetas": [
             "Empurre a onda e role quando o inimigo do meio sumir ou recuar.",
             "Avise (ping) o aliado antes de chegar pra vocês irem juntos.",
         ]},
        {"tema": "engage_kpa", "requer": ["sup_engajador", "jg_tank", "Tank"],
         "meta": "Inicie as lutas que o seu time consegue vencer.",
         "submetas": [
             "Escolha o alvo e o momento em que o time está pronto pra ir junto.",
             "Não inicie sozinho sem dano por perto pra capitalizar.",
         ]},
    ],
}

_GENERICO_EXTRA: list[dict] = [
    {"tema": "um_de_cada_vez",
     "meta": "Foque num fundamento de cada vez pra evoluir.",
     "submetas": [
         "Escolha um único fundamento pra treinar por semana (ex.: farm).",
         "Não tente consertar tudo de uma vez.",
     ]},
    {"tema": "mental",
     "meta": "Cuide da sua cabeça durante a partida.",
     "submetas": [
         "Depois de morrer, evite a revanche emocional — jogue a próxima jogada com calma.",
         "Faça pausas entre partidas pra não acumular cansaço e tilt.",
     ]},
]

# Mescla os extras na fonte única. Chaves novas (métricas sem banco base, ex.: solo_kills,
# tempo_cc, cura_total) passam a existir aqui via setdefault.
for _m, _extra in _DRILLS_EXTRA.items():
    DRILLS.setdefault(_m, []).extend(_extra)
DRILLS_GENERICO.extend(_GENERICO_EXTRA)


def drills_da_metrica(metrica: str) -> list[dict]:
    """Drills de treino para uma métrica (fonte única, usada pelo plano de treino).
    Cada drill é {"meta": str, "submetas": [str, ...]}."""
    return DRILLS.get(metrica, DRILLS_GENERICO)


def _drill_em_texto(drill: dict) -> str:
    """Achata um drill (meta + sub-metas) em texto corrido para busca/RAG."""
    subs = "; ".join(drill.get("submetas", []))
    return drill["meta"] + (f" Como treinar: {subs}" if subs else "")


# Drills entram na base como entradas pesquisáveis "metrica:<m>".
def _entradas_drills() -> list[dict]:
    entradas = []
    for metrica, drills in DRILLS.items():
        label = METRIC_LABELS.get(metrica, metrica.replace("_", " "))
        corpo = "\n- ".join(_drill_em_texto(d) for d in drills)
        entradas.append({
            "id": f"metrica_{metrica}",
            "titulo": f"Plano de Treinamento e Drills: {label}",
            "topico": f"metrica:{metrica}",
            "tags": ["treinar", "treino", "drill", "melhorar", "como", "estrategia", metrica,
                     *label.lower().split()],
            "texto": "Exerça as seguintes técnicas de treinamento focadas em evoluir em " + label + ":\n- " + corpo,
        })
    return entradas


def _carregar_datadragon() -> list[dict]:
    """Carrega as entradas factuais geradas do Data Dragon, se o arquivo existir."""
    if _ARQ_DDRAGON.exists():
        try:
            return json.loads(_ARQ_DDRAGON.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


# Corpus completo, pesquisável (conceitos curados + drills + erros por elo + factual do DDragon).
_CORPUS: list[dict] = (
    CONHECIMENTO + _entradas_drills() + _entradas_erros_elo() + _carregar_datadragon()
)


def entradas() -> list[dict]:
    """Todas as entradas pesquisáveis (conceitos + drills). Usado pelo RAG (Opção B)."""
    return _CORPUS


def texto_indexavel(entrada: dict) -> str:
    """Texto representativo de uma entrada para embedding/busca (título + tags + texto)."""
    tags = " ".join(entrada.get("tags", []))
    return f"{entrada.get('titulo', '')}. {tags}. {entrada.get('texto', '')}"


# ──────────────────────────────────────────────
# Busca por palavra-chave (Opção A)
# ──────────────────────────────────────────────
def _normalizar(texto: str) -> str:
    """Minúsculas, sem acento, só alfanumérico e espaços."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texto)


# Termos curtos (<=2 letras) que são jargão relevante de LoL e NÃO devem ser descartados
# como stopword (ex.: "cs" = farm, "ad"/"ap" = tipo de dano, "tp" = teleporte).
_TERMOS_CURTOS = {"cs", "cc", "ad", "ap", "tp", "mr", "xp", "hp"}


def _termos(texto: str) -> set[str]:
    """Conjunto de palavras normalizadas, ignorando micro-palavras (stopwords leves),
    mas preservando o jargão curto de LoL (`_TERMOS_CURTOS`)."""
    return {t for t in _normalizar(texto).split() if len(t) > 2 or t in _TERMOS_CURTOS}


# Conhecimento curado (conceitos/rotas/drills) tem prioridade sobre o factual cru do Data
# Dragon (item:/campeao:/runa:/feitico:/habilidade:): num empate de relevância o conceito
# tático ganha, sem sobrepor um match forte por nome (ex.: buscar um item específico, que
# pontua muito). habilidade: também é factual do DDragon — sem ele, as 860 habilidades eram
# tratadas como "curadas" e ganhavam o BOOST_CURADO indevidamente.
_PREFIXOS_FACTUAIS = ("item:", "campeao:", "runa:", "feitico:", "habilidade:")
BOOST_CURADO = 1.5


def eh_curado(entrada: dict) -> bool:
    """True para conceitos curados; False para o factual cru do Data Dragon."""
    return not entrada.get("topico", "").startswith(_PREFIXOS_FACTUAIS)


def _pontuar(consulta_termos: set[str], entrada: dict) -> float:
    """Score por sobreposição de termos, com peso maior para tags (5x) e título (4x) que
    para o corpo (1x), e leve prioridade ao conhecimento curado (`BOOST_CURADO`)."""
    if not consulta_termos:
        return 0.0

    tags_termos = set()
    for tag in entrada.get("tags", []):
        tags_termos |= _termos(tag)
    titulo_termos = _termos(entrada.get("titulo", ""))
    texto_termos = _termos(entrada.get("texto", "")) | _termos(entrada.get("topico", ""))

    score = (5 * len(consulta_termos & tags_termos)
             + 4 * len(consulta_termos & titulo_termos)
             + 1 * len(consulta_termos & texto_termos))
    if score and eh_curado(entrada):
        score *= BOOST_CURADO
    return score


def ranquear(consulta: str, limite: int = 20) -> list[dict]:
    """Ranking completo (até `limite`) das entradas por palavra-chave, da mais para a menos
    relevante — usado pela busca híbrida (fusão de rankings). Só entradas com score > 0."""
    termos = _termos(consulta or "")
    if not termos:
        return []
    pontuadas = [(e, _pontuar(termos, e)) for e in _CORPUS]
    pontuadas = [(e, s) for e, s in pontuadas if s > 0]
    pontuadas.sort(key=lambda es: es[1], reverse=True)
    return [e for e, _ in pontuadas[:limite]]


def buscar(consulta: str, k: int = 4) -> list[dict]:
    """Retorna as k entradas mais relevantes para a consulta (busca por palavra-chave).
    Mesma assinatura da busca semântica (Opção B), para troca transparente do backend."""
    return ranquear(consulta, limite=k)


# ──────────────────────────────────────────────
# Expansão de consulta (jargão/sinônimos) — usada na recuperação corretiva (CRAG-lite):
# quando a busca crua não acha nada, reformula a query trazendo sinônimos do domínio.
# ──────────────────────────────────────────────
_SINONIMOS: dict[str, list[str]] = {
    "cs": ["farm", "minions", "last hit", "ultimo golpe"],
    "farm": ["cs", "minions", "last hit"],
    "minions": ["cs", "farm", "onda", "leva"],
    "onda": ["wave", "leva", "minions"],
    "wave": ["onda", "leva", "wave management"],
    "gank": ["emboscada", "roam", "caçador"],
    "roam": ["rotacao", "rotacionar", "girar", "gank"],
    "visao": ["ward", "sentinela", "wards"],
    "ward": ["visao", "sentinela"],
    "morrer": ["mortes", "morte", "kda", "posicionamento"],
    "morrendo": ["mortes", "kda", "posicionamento"],
    "dano": ["dps", "burst", "poke"],
    "itens": ["itemizacao", "build", "item"],
    "runa": ["runas"],
    "objetivo": ["dragao", "arauto", "baron", "barao"],
    "posicionar": ["posicionamento", "kiting"],
    "posicionamento": ["kiting", "posicionar"],
}


def expandir_consulta(consulta: str) -> str:
    """Reformula a consulta acrescentando sinônimos/jargão dos termos reconhecidos. Retorna a
    consulta original + termos extras (ou a original, se nada casar)."""
    termos = _termos(consulta or "")
    extras: list[str] = []
    for t in termos:
        for syn in _SINONIMOS.get(t, []):
            if syn not in extras:
                extras.append(syn)
    return (consulta + " " + " ".join(extras)).strip() if extras else (consulta or "")


def por_rota(rota: str) -> list[dict]:
    """Entradas de conhecimento específicas de uma rota."""
    alvo = f"rota:{(rota or '').upper()}"
    return [e for e in _CORPUS if e.get("topico") == alvo]


def formatar_resultados(itens: list[dict]) -> str:
    """Texto enxuto dos resultados para o LLM consumir."""
    if not itens:
        return ("Nada encontrado na base de conhecimento para essa consulta. "
                "Responda com cautela e não invente conceitos.")
    blocos = []
    for e in itens:
        blocos.append(f"• {e['titulo']} [{e['topico']}]\n  {e['texto']}")
    return "BASE DE CONHECIMENTO (fonte de verdade tática):\n" + "\n".join(blocos)


# ──────────────────────────────────────────────
# Características de campeão (para a análise de evolução)
# ──────────────────────────────────────────────
# Metadados úteis das classes do Data Dragon (em PT-BR) para interpretar uma comp/partida:
# como cada classe costuma escalar e qual é o seu papel típico na luta.
_PERFIL_CLASSE = {
    "Fighter": "lutador (corpo a corpo, dano e resistência equilibrados; força em escaramuças)",
    "Tank": "tanque (inicia lutas e absorve dano; fraco em dano puro)",
    "Mage": "mago (dano mágico em área/à distância; frágil, depende de posicionamento)",
    "Assassin": "assassino (alvo único, picos de dano para eliminar carries; snowball)",
    "Marksman": "atirador (dano físico contínuo à distância; escala com itens, frágil cedo)",
    "Support": "suporte (utilidade, visão e proteção; pouco ouro/dano próprio)",
}


def _texto_funcoes(classes: list[str]) -> str:
    """Descreve as classes do campeão (ex.: 'lutador ...; tanque ...')."""
    descrita = [_PERFIL_CLASSE.get(c, c) for c in classes]
    return "; ".join(descrita)


# Lookup preguiçoso championName/nome → entrada de campeão do Data Dragon.
_INDICE_CAMPEOES: dict | None = None


def _indexar_campeoes() -> dict:
    """Mapeia identificadores de campeão (nome de exibição e id interno da Riot, ambos
    normalizados) para a entrada `campeao_*` do corpus. Construído uma única vez."""
    global _INDICE_CAMPEOES
    if _INDICE_CAMPEOES is not None:
        return _INDICE_CAMPEOES
    indice: dict = {}
    for e in _CORPUS:
        if not e.get("topico", "").startswith("campeao:"):
            continue
        # tags = ["campeao", "campeoes", nome, nome_id, *classes]; as duas primeiras
        # após os rótulos fixos são o nome de exibição e o id interno (ex.: MonkeyKing).
        ids = [t for t in e.get("tags", [])[2:4] if t]
        for ident in ids:
            indice.setdefault(_normalizar(ident), e)
    _INDICE_CAMPEOES = indice
    return indice


def caracteristicas_campeao(nome_ou_id: str) -> dict | None:
    """Características de um campeão a partir do nome de exibição OU do championName interno
    da Riot (ex.: 'MonkeyKing' → Wukong). Retorna {nome, titulo, classes, funcoes_desc,
    descricao} ou None se o campeão não estiver no Data Dragon."""
    if not nome_ou_id:
        return None
    entrada = _indexar_campeoes().get(_normalizar(nome_ou_id))
    if not entrada:
        return None
    # Classes = tags após os 4 rótulos fixos (campeao, campeoes, nome, nome_id).
    classes = [t for t in entrada.get("tags", [])[4:] if t]
    titulo = entrada.get("titulo", "").replace("Campeão: ", "")
    return {
        "nome": titulo.split(" — ")[0] if " — " in titulo else titulo,
        "titulo": titulo,
        "classes": classes,
        "funcoes_desc": _texto_funcoes(classes),
        "descricao": entrada.get("texto", ""),
    }


def classes_dos_campeoes(nomes: list[str]) -> set[str]:
    """Conjunto de classes (Marksman, Mage, Tank, ...) dos campeões informados (nome de
    exibição ou championName interno da Riot), via Data Dragon. Vazio se nada reconhecido."""
    classes: set[str] = set()
    for nome in nomes or []:
        info = caracteristicas_campeao(nome)
        if info:
            classes.update(info["classes"])
    return classes


# ──────────────────────────────────────────────
# Arquétipos de jogador (rota + classe) — usados para escolher drills específicos.
# ──────────────────────────────────────────────
# O Data Dragon só dá a classe AMPLA (Tank, Mage, Support, ...), que não separa, p.ex.,
# suporte protetor (Lulu) de suporte de poke (Brand) — ambos vêm como Support+Mage.
# Estas listas curadas refinam os casos ambíguos pelo championName interno da Riot.
_SUP_ENCANTADORES = {  # suportes de proteção/cura/escudo (peel)
    "Lulu", "Janna", "Soraka", "Nami", "Sona", "Yuumi", "Karma", "Milio",
    "Renata", "Seraphine", "Taric", "Ivern", "Sona",
}
_SUP_ENGAJADORES = {  # suportes de iniciar / CC pesado
    "Leona", "Nautilus", "Rell", "Alistar", "Thresh", "Blitzcrank", "Pyke",
    "Rakan", "Braum", "Maokai", "Amumu", "Galio", "TahmKench",
}
_JUGGERNAUTS = {  # lutadores corpo a corpo lentos, resistentes, sem mobilidade
    "Darius", "Garen", "Sett", "Mordekaiser", "Illaoi", "Urgot", "Nasus",
    "Yorick", "Trundle", "Volibear", "Aatrox",
}


def _tags_de_arquetipo(posicao: str, classes, nomes=None) -> set[str]:
    """Resolve os 'arquétipos' de um jogador a partir da rota + classes (+ nomes para os
    casos ambíguos). Retorna um conjunto de etiquetas (rota, classes amplas e arquétipos
    refinados como 'mid_assassino', 'sup_protetor') contra o qual o campo `requer` de cada
    drill é casado. Quando a classe é desconhecida, devolve só a rota (degrada com graça)."""
    pos = (posicao or "").upper()
    cs = set(classes or [])
    nomes_norm = {_normalizar(n) for n in (nomes or [])}
    tags: set[str] = set()
    if pos:
        tags.add(pos)
    tags |= cs

    def tem_nome(conjunto) -> bool:
        return any(_normalizar(c) in nomes_norm for c in conjunto)

    if tem_nome(_JUGGERNAUTS):
        tags.add("juggernaut")

    if pos == "JUNGLE":
        if "Assassin" in cs:
            tags.add("jg_assassino")
        if "Tank" in cs:
            tags.add("jg_tank")
        if "Fighter" in cs:
            tags.add("jg_lutador")
        if "Mage" in cs:
            tags.add("jg_mago")
    elif pos == "TOP":
        if "Tank" in cs:
            tags.add("top_tank")
        if "Fighter" in cs:
            tags.add("top_lutador")
        if "Mage" in cs:
            tags.add("top_mago")
        if "Marksman" in cs or "Assassin" in cs:
            tags.add("top_carry")
    elif pos == "MIDDLE":
        if "Mage" in cs:
            tags.add("mid_control_mage")
        if "Assassin" in cs:
            tags.add("mid_assassino")
        if "Marksman" in cs:
            tags.add("mid_atirador")
    elif pos == "BOTTOM":
        if "Marksman" in cs:
            tags.add("adc")
        if "Mage" in cs:
            tags.add("adc_mago")
    elif pos in ("UTILITY", "SUPPORT"):
        engajador = tem_nome(_SUP_ENGAJADORES) or bool(cs & {"Tank", "Fighter"})
        protetor = tem_nome(_SUP_ENCANTADORES)
        if engajador:
            tags.add("sup_engajador")
        if protetor:
            tags.add("sup_protetor")
        # Mago de suporte (poke/burst, ex.: Brand/Xerath/Zyra): Support+Mage que não é
        # encantador conhecido nem engajador.
        if "Mage" in cs and not protetor and not engajador:
            tags.add("sup_mago")
        # Support+Mage sem nome conhecido: assume protetor (caso mais comum no elo baixo).
        if "Support" in cs and "Mage" in cs and not protetor and not engajador:
            tags.add("sup_protetor")
    return tags


def tags_do_jogador(perfil: dict) -> set[str]:
    """Etiquetas de arquétipo do jogador a partir do diagnóstico (rota + campeões de
    referência). Usado pelo plano de treino para filtrar drills por relevância."""
    nomes = perfil.get("campeoes_referencia") or []
    classes = classes_dos_campeoes(nomes)
    return _tags_de_arquetipo(perfil.get("posicao", ""), classes, nomes)
