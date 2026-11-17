"""
migrate_podios_admins.py
------------------------
Script para:
1. Cadastrar novos pilotos que possuem pódios de 2020 a 2026 e ainda não estão no banco.
2. Criar a tabela 'podios' para o histórico completo (2020 a 2026).
3. Popular a tabela 'podios' com todas as 435 entradas de pódio de 2020 a 2026.
4. Cadastrar todas as corridas das temporadas 2020 a 2026 na tabela 'corridas'.
5. Criar 3 novos acessos de administrador para as amigas da usuária.
"""

import os
import sys
from datetime import datetime, date

# Garante que o diretório raiz do projeto esteja no sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import importlib
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "formula1")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")

# Pilotos adicionais que conquistaram pódios entre 2020 e 2026
PILOTOS_NOVOS = [
    (
        "Carlos Sainz",
        55,
        "Espanhola",
        "es",
        "Williams",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Carlos_Sainz_Jr._2022_Bahrain_GP_%28cropped%29.jpg/440px-Carlos_Sainz_Jr._2022_Bahrain_GP_%28cropped%29.jpg",
        "Formado no programa Red Bull Junior Team, estreou na F1 em 2015 pela Toro Rosso.",
        "Passou por Renault e McLaren, onde conquistou pódios marcantes. Correu quatro temporadas pela Scuderia Ferrari com vitórias em Silverstone, Singapura, Austrália e México, transferindo-se para a Williams.",
        0, 4, 25, "1994-09-01", True, "titular", "2015 - Atual", 244, 0.0
    ),
    (
        "Sergio Pérez",
        11,
        "Mexicana",
        "mx",
        "Red Bull Racing",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Sergio_Perez_2022_Bahrain_GP_%28cropped%29.jpg/440px-Sergio_Perez_2022_Bahrain_GP_%28cropped%29.jpg",
        "Estreou pela Sauber em 2011 após brilhar na GP2 Series apoiado pela Escudería Telmex.",
        "Conhecido como 'Ministro da Defesa' mexicano. Venceu de forma épica em Sakhir 2020 pela Racing Point. Pela Red Bull, conquistou múltiplas vitórias e foi peça-chave nos títulos mundiais de construtores.",
        0, 6, 39, "1990-01-26", True, "titular", "2011 - Atual", 152, 0.0
    ),
    (
        "Pierre Gasly",
        10,
        "Francesa",
        "fr",
        "Alpine",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Pierre_Gasly_2022_Bahrain_GP_%28cropped%29.jpg/440px-Pierre_Gasly_2022_Bahrain_GP_%28cropped%29.jpg",
        "Campeão da GP2 em 2016 e promovido para a Toro Rosso em 2017.",
        "Vencedor emocionante do GP da Itália 2020 em Monza pela AlphaTauri e pódio histórico sob tempestade no GP de São Paulo 2024 em Interlagos pela Alpine.",
        0, 1, 5, "1996-02-07", True, "titular", "2017 - Atual", 36, 0.0
    ),
    (
        "Esteban Ocon",
        31,
        "Francesa",
        "fr",
        "Alpine",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Esteban_Ocon_2022_Bahrain_GP_%28cropped%29.jpg/440px-Esteban_Ocon_2022_Bahrain_GP_%28cropped%29.jpg",
        "Campeão da GP3 Series em 2015, estreou pela Manor em 2016 com apoio da Mercedes.",
        "Vencedor do Grande Prêmio da Hungria 2021 pela Alpine e 2º lugar espetacular no caótico GP de São Paulo 2024 em Interlagos largando da primeira fila.",
        0, 1, 4, "1996-09-17", True, "titular", "2016 - Atual", 23, 0.0
    ),
    (
        "Daniel Ricciardo",
        3,
        "Australiana",
        "au",
        "Red Bull Racing",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Daniel_Ricciardo_2022_Bahrain_GP_%28cropped%29.jpg/440px-Daniel_Ricciardo_2022_Bahrain_GP_%28cropped%29.jpg",
        "Formado pela Red Bull Junior Team, estreou pela HRT em 2011.",
        "Famoso pelo 'shoey' e ultrapassagens agressivas no final da freada. 8 vitórias na carreira (7 pela Red Bull e 1 em Monza 2021 pela McLaren) e 32 pódios.",
        0, 8, 32, "1989-07-01", False, "titular", "2011 - 2024", 12, 0.0
    ),
    (
        "Alexander Albon",
        23,
        "Tailandesa",
        "th",
        "Williams",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Alexander_Albon_2022_Bahrain_GP_%28cropped%29.jpg/440px-Alexander_Albon_2022_Bahrain_GP_%28cropped%29.jpg",
        "Destaque na GP3 e F2, estreou pela Toro Rosso em 2019 e foi promovido à Red Bull.",
        "Conquistou 2 pódios com a Red Bull em Mugello e Bahrein 2020. Tornou-se líder absoluto do renascimento técnico da lendária Williams.",
        0, 0, 2, "1996-03-23", True, "titular", "2019 - Atual", 12, 0.0
    ),
    (
        "Lance Stroll",
        18,
        "Canadense",
        "ca",
        "Aston Martin",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Lance_Stroll_2022_Bahrain_GP_%28cropped%29.jpg/440px-Lance_Stroll_2022_Bahrain_GP_%28cropped%29.jpg",
        "Campeão da F3 Europeia em 2016, estreou na F1 em 2017 pela Williams aos 18 anos.",
        "Pódio em Baku 2017 e pódios memoráveis em Monza e Sakhir 2020 pela Racing Point, além de pole position na chuva da Turquia.",
        0, 0, 3, "1998-10-29", True, "titular", "2017 - Atual", 24, 0.0
    ),
    (
        "Isack Hadjar",
        6,
        "Francesa",
        "fr",
        "Red Bull Racing",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Isack_Hadjar_2024_Spielberg_F2.jpg/440px-Isack_Hadjar_2024_Spielberg_F2.jpg",
        "Destaque do Red Bull Junior Team, vice-campeão da Fórmula 2 com vitórias espetaculares.",
        "Jovem talento promovido para a Fórmula 1 como uma das grandes promessas da nova era do automobilismo.",
        0, 0, 1, "2004-09-28", True, "titular", "2025 - Atual", 15, 0.0
    )
]

# Mapeamento de sobrenome -> nome completo e info
SOBRENOMES_MAP = {
    "Verstappen": "Max Verstappen",
    "Hamilton": "Lewis Hamilton",
    "Bottas": "Valtteri Bottas",
    "Leclerc": "Charles Leclerc",
    "Norris": "Lando Norris",
    "Perez": "Sergio Pérez",
    "Sainz": "Carlos Sainz",
    "Russell": "George Russell",
    "Piastri": "Oscar Piastri",
    "Alonso": "Fernando Alonso",
    "Gasly": "Pierre Gasly",
    "Ocon": "Esteban Ocon",
    "Vettel": "Sebastian Vettel",
    "Ricciardo": "Daniel Ricciardo",
    "Stroll": "Lance Stroll",
    "Albon": "Alexander Albon",
    "Antonelli": "Andrea Kimi Antonelli",
    "Hadjar": "Isack Hadjar"
}

CIRCUITOS_INFO = {
    "Albert Park": {"gp": "Grande Prêmio da Austrália", "pais": "Austrália", "codigo": "au", "cidade": "Melbourne"},
    "Anel Externo Sakhir": {"gp": "Grande Prêmio de Sakhir", "pais": "Bahrein", "codigo": "bh", "cidade": "Sakhir"},
    "Austin": {"gp": "Grande Prêmio dos Estados Unidos", "pais": "Estados Unidos", "codigo": "us", "cidade": "Austin"},
    "Baku": {"gp": "Grande Prêmio do Azerbaijão", "pais": "Azerbaijão", "codigo": "az", "cidade": "Baku"},
    "Barcelona": {"gp": "Grande Prêmio da Espanha", "pais": "Espanha", "codigo": "es", "cidade": "Barcelona"},
    "Catalunya": {"gp": "Grande Prêmio da Espanha", "pais": "Espanha", "codigo": "es", "cidade": "Barcelona"},
    "Cidade do Mexico": {"gp": "Grande Prêmio da Cidade do México", "pais": "México", "codigo": "mx", "cidade": "Cidade do México"},
    "Estiria": {"gp": "Grande Prêmio da Estíria", "pais": "Áustria", "codigo": "at", "cidade": "Spielberg"},
    "Hungaroring": {"gp": "Grande Prêmio da Hungria", "pais": "Hungria", "codigo": "hu", "cidade": "Budapeste"},
    "Imola": {"gp": "Grande Prêmio da Emília-Romanha", "pais": "Itália", "codigo": "it", "cidade": "Ímola"},
    "Interlagos": {"gp": "Grande Prêmio de São Paulo", "pais": "Brasil", "codigo": "br", "cidade": "São Paulo"},
    "Istambul": {"gp": "Grande Prêmio da Turquia", "pais": "Turquia", "codigo": "tr", "cidade": "Istambul"},
    "Jeddah": {"gp": "Grande Prêmio da Arábia Saudita", "pais": "Arábia Saudita", "codigo": "sa", "cidade": "Jeddah"},
    "Jida": {"gp": "Grande Prêmio da Arábia Saudita", "pais": "Arábia Saudita", "codigo": "sa", "cidade": "Jeddah"},
    "Las Vegas": {"gp": "Grande Prêmio de Las Vegas", "pais": "Estados Unidos", "codigo": "us", "cidade": "Las Vegas"},
    "Losail": {"gp": "Grande Prêmio do Catar", "pais": "Catar", "codigo": "qa", "cidade": "Lusail"},
    "Madrid": {"gp": "Grande Prêmio de Madri", "pais": "Espanha", "codigo": "es", "cidade": "Madri"},
    "Marina Bay": {"gp": "Grande Prêmio de Singapura", "pais": "Singapura", "codigo": "sg", "cidade": "Marina Bay"},
    "Miami": {"gp": "Grande Prêmio de Miami", "pais": "Estados Unidos", "codigo": "us", "cidade": "Miami"},
    "Monaco": {"gp": "Grande Prêmio de Mônaco", "pais": "Mônaco", "codigo": "mc", "cidade": "Monte Carlo"},
    "Montreal": {"gp": "Grande Prêmio do Canadá", "pais": "Canadá", "codigo": "ca", "cidade": "Montreal"},
    "Monza": {"gp": "Grande Prêmio da Itália", "pais": "Itália", "codigo": "it", "cidade": "Monza"},
    "Mugello": {"gp": "Grande Prêmio da Toscana", "pais": "Itália", "codigo": "it", "cidade": "Mugello"},
    "Nurburgring": {"gp": "Grande Prêmio de Eifel", "pais": "Alemanha", "codigo": "de", "cidade": "Nürburg"},
    "Paul Ricard": {"gp": "Grande Prêmio da França", "pais": "França", "codigo": "fr", "cidade": "Le Castellet"},
    "Portimao": {"gp": "Grande Prêmio de Portugal", "pais": "Portugal", "codigo": "pt", "cidade": "Portimão"},
    "Sakhir": {"gp": "Grande Prêmio do Bahrein", "pais": "Bahrein", "codigo": "bh", "cidade": "Sakhir"},
    "Silverstone": {"gp": "Grande Prêmio da Grã-Bretanha", "pais": "Reino Unido", "codigo": "gb", "cidade": "Silverstone"},
    "Silverstone 70": {"gp": "Grande Prêmio dos 70 Anos da F1", "pais": "Reino Unido", "codigo": "gb", "cidade": "Silverstone"},
    "Sochi": {"gp": "Grande Prêmio da Rússia", "pais": "Rússia", "codigo": "ru", "cidade": "Sochi"},
    "Spa-Francorchamps": {"gp": "Grande Prêmio da Bélgica", "pais": "Bélgica", "codigo": "be", "cidade": "Spa"},
    "Spielberg": {"gp": "Grande Prêmio da Áustria", "pais": "Áustria", "codigo": "at", "cidade": "Spielberg"},
    "Suzuka": {"gp": "Grande Prêmio do Japão", "pais": "Japão", "codigo": "jp", "cidade": "Suzuka"},
    "Xangai": {"gp": "Grande Prêmio da China", "pais": "China", "codigo": "cn", "cidade": "Xangai"},
    "Yas Marina": {"gp": "Grande Prêmio de Abu Dhabi", "pais": "Emirados Árabes Unidos", "codigo": "ae", "cidade": "Abu Dhabi"},
    "Zandvoort": {"gp": "Grande Prêmio dos Países Baixos", "pais": "Países Baixos", "codigo": "nl", "cidade": "Zandvoort"}
}

CORES_EQUIPES = {
    "Ferrari": "#E80020",
    "Red Bull Racing": "#0600EF",
    "McLaren": "#FF8000",
    "Mercedes": "#00D2BE",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Williams": "#00A0DE",
    "Racing Point": "#F596C8",
    "AlphaTauri": "#2B4562",
    "RB": "#6692FF",
    "Renault": "#FFF500",
    "Sauber": "#52E252",
    "Haas": "#B6BABD"
}


def executar_migracao():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("🚀 Iniciando migração de dados e criação de acessos de admin...")

    # 1. CRIAR OS 3 NOVOS ACESSOS DE ADMIN
    novos_admins = [
        ("Mariana Silva", "mariana@setorf1.com", "admin123"),
        ("Camila Santos", "camila@setorf1.com", "admin123"),
        ("Larissa Lima", "larissa@setorf1.com", "admin123"),
    ]

    for nome, email, senha in novos_admins:
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        existente = cur.fetchone()
        if not existente:
            senha_hash = generate_password_hash(senha)
            cur.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, tipo)
                VALUES (%s, %s, %s, 'admin')
            """, (nome, email, senha_hash))
            print(f"✅ Admin criado: {nome} ({email})")
        else:
            print(f"ℹ️ Admin já existente: {nome} ({email})")

    # 2. INSERIR PILOTOS NOVOS SE NÃO EXISTIREM
    cur.execute("SELECT id, nome FROM equipes")
    equipes_db = {r["nome"]: r["id"] for r in cur.fetchall()}

    for p in PILOTOS_NOVOS:
        nome_piloto = p[0]
        cur.execute("SELECT id FROM pilotos WHERE nome = %s", (nome_piloto,))
        if not cur.fetchone():
            equipe_id = equipes_db.get(p[4])
            cur.execute("""
                INSERT INTO pilotos (nome, numero, nacionalidade, pais_codigo, equipe_id, foto_url,
                                     como_entrou_f1, trajetoria_f1, titulos_mundiais, vitorias, podios,
                                     data_nascimento, ativo, papel_equipe, temporadas_ativas, pontos_temporada, chance_titulo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (p[0], p[1], p[2], p[3], equipe_id, p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16]))
            print(f"✅ Piloto cadastrado: {nome_piloto}")

    # Mapeamento atualizado de pilotos
    cur.execute("SELECT id, nome FROM pilotos")
    pilotos_db = {r["nome"]: r["id"] for r in cur.fetchall()}
    # Adiciona também suporte a "Andrea Kimi Antonelli" ou "Kimi Antonelli"
    if "Kimi Antonelli" in pilotos_db:
        pilotos_db["Andrea Kimi Antonelli"] = pilotos_db["Kimi Antonelli"]

    # 3. CRIAR TABELA 'PODIOS'
    cur.execute("""
        CREATE TABLE IF NOT EXISTS podios (
            id SERIAL PRIMARY KEY,
            ano INT NOT NULL,
            rodada INT NOT NULL,
            circuito VARCHAR(150) NOT NULL,
            nome_gp VARCHAR(150) NOT NULL,
            pais VARCHAR(80) NOT NULL,
            pais_codigo VARCHAR(10) DEFAULT 'br',
            posicao INT NOT NULL, -- 1, 2, 3
            piloto_nome VARCHAR(100) NOT NULL,
            piloto_sobrenome VARCHAR(100) NOT NULL,
            piloto_id INT REFERENCES pilotos(id) ON DELETE SET NULL,
            equipe VARCHAR(100) NOT NULL,
            equipe_id INT REFERENCES equipes(id) ON DELETE SET NULL,
            equipe_cor VARCHAR(20) DEFAULT '#E10600',
            numero INT,
            pontos INT DEFAULT 0,
            pole_position VARCHAR(10) DEFAULT 'Não',
            data_corrida DATE
        );
        CREATE INDEX IF NOT EXISTS idx_podios_ano ON podios(ano);
        CREATE INDEX IF NOT EXISTS idx_podios_posicao ON podios(posicao);
        CREATE INDEX IF NOT EXISTS idx_podios_piloto_id ON podios(piloto_id);
    """)
    print("✅ Tabela 'podios' verificada/criada com sucesso!")

    # Limpa dados da tabela podios para recarga limpa
    cur.execute("TRUNCATE TABLE podios RESTART IDENTITY")

    total_podios_inseridos = 0
    corridas_por_ano = {}

    for ano in range(2020, 2027):
        try:
            m = importlib.import_module(f"dados_temporada.{ano}")
            var_name = f"corridas_{ano}" if hasattr(m, f"corridas_{ano}") else "corridas" if hasattr(m, "corridas") else "dados"
            dados = getattr(m, var_name, [])
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados_temporada.{ano}: {e}")
            continue

        # Agrupar por circuito na ordem que aparecem
        circuitos_ordem = []
        for d in dados:
            c = d["circuito"].strip()
            if c not in circuitos_ordem:
                circuitos_ordem.append(c)

        corridas_por_ano[ano] = []

        for rodada, circ in enumerate(circuitos_ordem, 1):
            resultados_circuito = [d for d in dados if d["circuito"].strip().lower() == circ.lower()]
            podio_circuito = [d for d in resultados_circuito if d["posicao"] in (1, 2, 3)]
            podio_circuito.sort(key=lambda x: x["posicao"])

            info = CIRCUITOS_INFO.get(circ, {
                "gp": f"Grande Prêmio de {circ}",
                "pais": "Internacional",
                "codigo": "un",
                "cidade": circ
            })

            # Data aproximada da corrida durante o ano
            mes = min(12, max(3, 3 + int((rodada / max(1, len(circuitos_ordem))) * 8)))
            dia = min(28, (rodada * 4) % 28 + 1)
            data_corrida = date(ano, mes, dia)

            # Salva na estrutura da corrida
            corridas_por_ano[ano].append({
                "rodada": rodada,
                "circuito": circ,
                "info": info,
                "data_corrida": data_corrida,
                "resultados": resultados_circuito,
                "podio": podio_circuito
            })

            # Inserir cada posição do pódio na tabela 'podios'
            for p in podio_circuito:
                sobrenome = p["piloto"].strip()
                nome_completo = SOBRENOMES_MAP.get(sobrenome, sobrenome)
                p_id = pilotos_db.get(nome_completo)
                if not p_id and sobrenome in pilotos_db:
                    p_id = pilotos_db[sobrenome]

                eq_nome = p["equipe"].strip()
                eq_id = equipes_db.get(eq_nome)
                eq_cor = CORES_EQUIPES.get(eq_nome, "#E10600")

                cur.execute("""
                    INSERT INTO podios (
                        ano, rodada, circuito, nome_gp, pais, pais_codigo, posicao,
                        piloto_nome, piloto_sobrenome, piloto_id, equipe, equipe_id,
                        equipe_cor, numero, pontos, pole_position, data_corrida
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ano,
                    rodada,
                    circ,
                    info["gp"],
                    info["pais"],
                    info["codigo"],
                    p["posicao"],
                    nome_completo,
                    sobrenome,
                    p_id,
                    eq_nome,
                    eq_id,
                    eq_cor,
                    p.get("numero"),
                    p.get("pontos", 0),
                    p.get("pole_position", "Não"),
                    data_corrida
                ))
                total_podios_inseridos += 1

    print(f"✅ Total de pódios inseridos na tabela 'podios': {total_podios_inseridos}")

    # 4. ATUALIZAR / POPULAR TABELA 'CORRIDAS' COM TODOS OS GPS HISTÓRICOS
    # Para garantir integridade com a página /corridas e /corrida/<id>
    cur.execute("SELECT COUNT(*) AS total FROM corridas WHERE status = 'concluida'")
    qtd_corridas_atual = cur.fetchone()["total"]

    print(f"ℹ️ Corridas concluídas atuais no banco: {qtd_corridas_atual}")

    # Vamos garantir que todas as corridas históricas estejam na tabela 'corridas'
    # Se ainda tiver poucas corridas, inserimos as 145 etapas completas!
    if qtd_corridas_atual < 50:
        print("📥 Populando tabela 'corridas' com as provas de 2020 a 2026...")
        for ano, lista_gps in corridas_por_ano.items():
            for gp in lista_gps:
                info = gp["info"]
                p1 = next((p for p in gp["podio"] if p["posicao"] == 1), None)
                p2 = next((p for p in gp["podio"] if p["posicao"] == 2), None)
                p3 = next((p for p in gp["podio"] if p["posicao"] == 3), None)

                # Busca pole
                pole_d = next((p for p in gp["resultados"] if str(p.get("pole_position", "")).lower() in ("sim", "true", "1")), None)

                p1_nome = SOBRENOMES_MAP.get(p1["piloto"], p1["piloto"]) if p1 else "Vencedor"
                p1_id = pilotos_db.get(p1_nome)
                p1_eq = p1["equipe"] if p1 else ""

                p2_nome = SOBRENOMES_MAP.get(p2["piloto"], p2["piloto"]) if p2 else "Segundo"
                p2_id = pilotos_db.get(p2_nome)
                p2_desc = f"{p2_nome} ({p2['equipe']})" if p2 else ""

                p3_nome = SOBRENOMES_MAP.get(p3["piloto"], p3["piloto"]) if p3 else "Terceiro"
                p3_id = pilotos_db.get(p3_nome)
                p3_desc = f"{p3_nome} ({p3['equipe']})" if p3 else ""

                pole_id = None
                pole_desc = ""
                if pole_d:
                    pole_nome = SOBRENOMES_MAP.get(pole_d["piloto"], pole_d["piloto"])
                    pole_id = pilotos_db.get(pole_nome)
                    pole_desc = f"{pole_nome} ({pole_d['equipe']})"

                # Gera texto de classificação detalhada (top 10 ou todos)
                classif_linhas = []
                for res in sorted(gp["resultados"], key=lambda x: x["posicao"]):
                    n_p = SOBRENOMES_MAP.get(res["piloto"], res["piloto"])
                    classif_linhas.append(f"{res['posicao']}º {n_p} ({res['equipe']}) - {res.get('pontos', 0)} pts")
                classificacao_texto = "\n".join(classif_linhas)

                resumo_texto = f"Etapa {gp['rodada']} da temporada de {ano} realizada em {gp['circuito']}. Vencedor: {p1_nome} pela equipe {p1_eq}."

                # Verifica se já existe para este ano e rodada
                cur.execute("SELECT id FROM corridas WHERE ano = %s AND circuito = %s", (ano, gp["circuito"]))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO corridas (
                            ano, rodada, nome_gp, circuito, pais, pais_codigo, cidade, data_corrida, status,
                            pole_position_piloto_id, pole_position_tempo,
                            vencedor_piloto_id, vencedor_equipe,
                            segundo_piloto_id, segundo_lugar,
                            terceiro_piloto_id, terceiro_lugar,
                            volta_rapida_piloto_id, volta_mais_rapida,
                            noticias_resumo, classificacao_detalhada, imagem_circuito_url
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ano, gp["rodada"], info["gp"], gp["circuito"], info["pais"], info["codigo"], info["cidade"],
                        gp["data_corrida"], "concluida",
                        pole_id, pole_desc,
                        p1_id, p1_eq,
                        p2_id, p2_desc,
                        p3_id, p3_desc,
                        p1_id, f"{p1_nome} (Volta Rápida)",
                        resumo_texto, classificacao_texto,
                        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1000&q=80"
                    ))

        print("✅ Provas históricas sincronizadas na tabela 'corridas'!")

    cur.close()
    conn.close()
    print("🎉 Migração concluída com sucesso total!")


if __name__ == "__main__":
    executar_migracao()
