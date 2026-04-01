import pandas as pd
import json
import plotly.express as px

def carregar_dados():
    try:
        df_raw = pd.read_excel("Analise.xlsx")
        df_raw.columns = df_raw.columns.str.strip()

        def obter_coluna(nome_coluna):
            if nome_coluna in df_raw.columns:
                col = df_raw[nome_coluna]
                if isinstance(col, pd.DataFrame):
                    return col.iloc[:, 0]
                return col
            return pd.Series(["Não informado"] * len(df_raw))

        # Adicionamos as colunas completas e com os nomes exatos
        df = pd.DataFrame({
            "pais": obter_coluna("Pais"),
            "universidade": obter_coluna("Universidade"),
            "duracao": obter_coluna("Duração do curso (em meses)"),
            "mod_ensino": obter_coluna("Modalidade de ensino"),
            "natureza": obter_coluna("Natureza da Instituição"),
            "mod_programa": obter_coluna("Modalidade do programa"),
            "ano_inicio": obter_coluna("Ano de início"),
            "qs_ranking": obter_coluna("QS World University Rankings: América Latina e Caribe 2026"),
            "bolsas": obter_coluna("Programa de bolsas de estudos (becas)"),
            "req_ingresso": obter_coluna("Requisitos para ingresso no programa"),
            "etapas_selecao": obter_coluna("Etapas processo seletivo"),            
            "req_titulo": obter_coluna("Requisitos para obtenção do título de doutor"),
            "visibilidade": obter_coluna("Quais?"),
            "internacionalizacao": obter_coluna("Internacionalização"),
            "parcerias": obter_coluna("Quais países"),
            # NOVAS COLUNAS PARA A PAGE 5:
            "nome_programa": obter_coluna("Nome de Programa"),
            "natureza": obter_coluna("Natureza da Instituição"), 
            "the_ranking": obter_coluna("Times Higher Education"),
            "qs_ranking": obter_coluna("QS World University Rankings: América Latina e Caribe 2026"),
            # Novas colunas para a Página 6 (Análise Qualitativa)
            "missao_perfil": obter_coluna("Missão/ Perfil do egresso"),
            "cat_missao": obter_coluna("Categorização missão/perfil do egresso"),
            "area_pesquisa": obter_coluna("Área de Concentração / Linhas de pesquisa"),
            "cat_area": obter_coluna("Categorização Área de Concentração"),
            "conceito": obter_coluna("Conceito"), # Caso tenha esta coluna, senão ele ignora sem dar erro
            
        })

        df = df.dropna(subset=["pais"])
        df["pais"] = df["pais"].astype(str).str.strip()
        
        df["duracao"] = pd.to_numeric(df["duracao"].astype(str).str.extract(r'(\d+)')[0], errors="coerce")
        df["ano_inicio"] = pd.to_numeric(df["ano_inicio"], errors="coerce")

        # Não se esqueça de adicionar "bolsas" nesta lista para limpar os dados:
        for col in ["mod_ensino", "natureza", "mod_programa", "bolsas"]:
            df[col] = df[col].astype(str).str.strip().replace("nan", "Não informado")

        df = df.dropna(subset=["pais"])
        df["pais"] = df["pais"].astype(str).str.strip()
        
        df["duracao"] = pd.to_numeric(df["duracao"].astype(str).str.extract(r'(\d+)')[0], errors="coerce")
        df["ano_inicio"] = pd.to_numeric(df["ano_inicio"], errors="coerce")

        for col in ["mod_ensino", "natureza", "mod_programa"]:
            df[col] = df[col].astype(str).str.strip().replace("nan", "Não informado")

        traducao = {
            "Brasil": "Brazil", "Colômbia": "Colombia", "Espanha": "Spain",
            "México": "Mexico", "Estados Unidos": "United States of America",
            "Chile": "Chile", "Argentina": "Argentina", "França": "France",
            "Portugal": "Portugal", "Canadá": "Canada", "Equador": "Ecuador",
            "Cuba": "Cuba", "Peru": "Peru"
        }
        df["pais_mapa"] = df["pais"].map(traducao).fillna(df["pais"])

        return df
    except Exception as e:
        print(f"ERRO CRÍTICO NO PROCESSAMENTO: {e}")
        return pd.DataFrame()

df = carregar_dados()
paises_lista = sorted(df["pais"].unique()) if not df.empty else []

try:
    with open("countries.geo.json", encoding="utf-8") as f:
        geojson = json.load(f)
except Exception as e:
    geojson = {}

paleta_cores = px.colors.qualitative.Prism
mapa_cores = {pais: paleta_cores[i % len(paleta_cores)] for i, pais in enumerate(paises_lista)}
LAYOUT_KWARGS = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b")
