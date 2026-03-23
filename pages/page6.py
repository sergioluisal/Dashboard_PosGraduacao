from flask import Blueprint, render_template, request
import plotly.graph_objects as go
import pandas as pd
import io
import base64
from wordcloud import WordCloud
from data_loader import df, LAYOUT_KWARGS

page6_bp = Blueprint('page6', __name__)

# Função para gerar Nuvens de Palavras em tons de Verde
def gerar_nuvem(coluna_df):
    if coluna_df is None or coluna_df.empty:
        return ""
    texto_completo = " ".join(coluna_df.dropna().astype(str).tolist())
    ignorar = {'e', 'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'que', 'em', 'para', 'com', 
               'não', 'uma', 'um', 'no', 'na', 'os', 'as', 'ao', 'aos', 'ou', 'se', 'por'}
    try:
        wc = WordCloud(width=600, height=300, background_color='white', 
                       colormap='Greens', stopwords=ignorar, max_words=100).generate(texto_completo)
        img = io.BytesIO()
        wc.to_image().save(img, format='PNG')
        return base64.b64encode(img.getvalue()).decode('utf-8')
    except:
        return ""

@page6_bp.route("/page6")
def analise_qualitativa():
    if df.empty:
        return "Erro ao carregar dados."

    # =========================================================
    # 1. NUVENS DE PALAVRAS
    # =========================================================
    nuvem_missao = gerar_nuvem(df.get('missao_perfil'))
    nuvem_cat_missao = gerar_nuvem(df.get('cat_missao'))
    nuvem_area = gerar_nuvem(df.get('area_pesquisa'))
    nuvem_cat_area = gerar_nuvem(df.get('cat_area'))

    # =========================================================
    # 2. PREPARAÇÃO DOS DADOS (Para Cartões e Tabela)
    # =========================================================
    colunas_tabela = ['universidade', 'pais', 'nome_programa']
    df_dados = df[[c for c in colunas_tabela if c in df.columns]].copy()
    
    if 'conceito' in df.columns:
        df_dados['Conceito'] = df['conceito'].fillna('Sem nota')
    else:
        df_dados['Conceito'] = 'Sem nota' 

    df_dados = df_dados.dropna(subset=['universidade'])
    
    if 'pais' in df_dados.columns:
        df_dados['pais'] = df_dados['pais'].fillna('Não informado')
    if 'nome_programa' in df_dados.columns:
        df_dados['nome_programa'] = df_dados['nome_programa'].fillna('Programa não informado')

    # =========================================================
    # 3. CÁLCULOS DOS CARTÕES DE DESTAQUE (OPÇÃO 3)
    # =========================================================
    total_programas = len(df_dados)
    
    # Lista do que consideramos "Notas Altas" (as que ficam a verde)
    notas_altas = ['5', '6', '7', 'alto', 'a', 'excelente', 'sim']
    programas_destaque = df_dados[df_dados['Conceito'].astype(str).str.strip().str.lower().isin(notas_altas)]
    total_destaque = len(programas_destaque)
    
    if not df_dados.empty and 'pais' in df_dados.columns:
        top_pais = df_dados['pais'].value_counts().index[0]
    else:
        top_pais = "N/A"

    # =========================================================
    # 4. TABELA DE RANKING (DADOS BRUTOS COM FAROL)
    # =========================================================
    cores_fundo_conceito = []
    for val in df_dados['Conceito']:
        v = str(val).strip().lower()
        if v in notas_altas:
            cores_fundo_conceito.append('#10b981') # Verde Esmeralda
        elif v in ['3', '4', 'médio', 'b', 'bom']:
            cores_fundo_conceito.append('#fbbf24') # Amarelo
        else:
            cores_fundo_conceito.append('#f3f4f6') # Cinza

    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Universidade</b>', '<b>País</b>', '<b>Programa</b>', '<b>Conceito</b>'],
            fill_color='#1f2937', font=dict(color='white', size=14), align='left'
        ),
        cells=dict(
            values=[df_dados.get('universidade', []), df_dados.get('pais', []), df_dados.get('nome_programa', []), df_dados['Conceito']],
            fill_color=['white', 'white', 'white', cores_fundo_conceito],
            align='left', font=dict(color='black', size=12), height=30
        )
    )])
    
    fig_table.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=450, autosize=True)
    tabela_html = fig_table.to_html(full_html=False, include_plotlyjs=False)

    return render_template("page6.html",
                           request=request,
                           nuvem_missao=nuvem_missao,
                           nuvem_cat_missao=nuvem_cat_missao,
                           nuvem_area=nuvem_area,
                           nuvem_cat_area=nuvem_cat_area,
                           total_programas=total_programas,
                           total_destaque=total_destaque,
                           top_pais=top_pais,
                           tabela_ranking=tabela_html)