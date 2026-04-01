from flask import Blueprint, render_template, request
import plotly.graph_objects as go
import pandas as pd
import io
import base64
from wordcloud import WordCloud
from data_loader import df, LAYOUT_KWARGS

page6_bp = Blueprint('page6', __name__)

def gerar_nuvem(coluna_df):
    if coluna_df is None or coluna_df.empty:
        return ""
    
    # Filtro de palavras irrelevantes
    ignorar = {'e', 'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'que', 'em', 'para', 'com', 
               'não', 'uma', 'um', 'no', 'na', 'os', 'as', 'ao', 'aos', 'ou', 'se', 'por', 'sobre'}
    
    texto = " ".join(coluna_df.dropna().astype(str).tolist())
    if not texto.strip() or len(texto) < 5:
        return ""

    try:
        wc = WordCloud(width=600, height=300, background_color='white', 
                       colormap='Greens', stopwords=ignorar, max_words=80).generate(texto)
        img = io.BytesIO()
        wc.to_image().save(img, format='PNG')
        return base64.b64encode(img.getvalue()).decode('utf-8')
    except:
        return ""

@page6_bp.route("/page6")
def analise_qualitativa():
    if df.empty:
        return "Erro ao carregar dados."

    # --- LÓGICA DO FILTRO ---
    pais_selecionado = request.args.get("Pais", "ALL")
    col_p = 'pais' if 'pais' in df.columns else ('Pais' if 'Pais' in df.columns else None)
    
    if col_p:
        paises_disponiveis = sorted(df[col_p].dropna().unique().tolist())
        df_filtrado = df if pais_selecionado == "ALL" else df[df[col_p] == pais_selecionado]
    else:
        paises_disponiveis = []
        df_filtrado = df

    # --- BUSCA DINÂMICA DE COLUNAS (Evita o erro "Sem Dados") ---
    def localizar_coluna(termos):
        for col in df_filtrado.columns:
            if any(t in col.lower() for t in termos):
                return col
        return None

    # Mapeando as colunas conforme o que costuma vir no Excel
    col_missao = localizar_coluna(['missao', 'perfil', 'objetivo'])
    col_cat_missao = localizar_coluna(['cat_missao', 'categoria_missao'])
    col_area = localizar_coluna(['area_pesquisa', 'concentracao', 'linha'])
    col_cat_area = localizar_coluna(['cat_area', 'categoria_area'])
    col_conceito = localizar_coluna(['conceito', 'nota', 'classificacao'])
   
    # 1. Gerando as Nuvens
    nuvem_missao = gerar_nuvem(df_filtrado[col_missao]) if col_missao else ""
    nuvem_cat_missao = gerar_nuvem(df_filtrado[col_cat_missao]) if col_cat_missao else ""
    nuvem_area = gerar_nuvem(df_filtrado[col_area]) if col_area else ""
    nuvem_cat_area = gerar_nuvem(df_filtrado[col_cat_area]) if col_cat_area else ""

    # 2. Dados para Tabela e Cartões
    total_programas = len(df_filtrado)
    
    # Lógica de Destaque (Conceitos altos)
    notas_altas = ['5', '6', '7', 'alto', 'a', 'excelente', 'sim']
    if col_conceito:
        total_destaque = len(df_filtrado[df_filtrado[col_conceito].astype(str).str.strip().str.lower().isin(notas_altas)])
    else:
        total_destaque = 0

    top_pais = df_filtrado[col_p].value_counts().index[0] if col_p and not df_filtrado.empty else "N/A"

    # 3. Tabela com Farol de Cores
    df_tabela = df_filtrado.copy()
    conceitos_lista = df_tabela[col_conceito].fillna('N/A').astype(str) if col_conceito else pd.Series(['N/A']*len(df_tabela))
    
    cores_farol = []
    for v in conceitos_lista.str.lower():
        if any(n in v for n in notas_altas): cores_farol.append('#10b981') # Verde
        elif any(n in v for n in ['3', '4', 'bom', 'médio', 'b']): cores_farol.append('#fbbf24') # Amarelo
        else: cores_farol.append('#f3f4f6') # Cinza

    fig_table = go.Figure(data=[go.Table(
        header=dict(values=['<b>Universidade</b>', '<b>País</b>', '<b>Programa</b>', '<b>Conceito</b>'],
                    fill_color='#1f2937', font=dict(color='white')),
        cells=dict(values=[df_tabela.get('universidade', []), df_tabela.get(col_p, []), 
                           df_tabela.get('nome_programa', []), conceitos_lista],
                   fill_color=['white', 'white', 'white', cores_farol], align='left')
    )])
    fig_table.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=450)

    return render_template("page6.html",
                           request=request,
                           paises=paises_disponiveis,
                           selecionado=pais_selecionado,
                           nuvem_missao=nuvem_missao,
                           nuvem_cat_missao=nuvem_cat_missao,
                           nuvem_area=nuvem_area,
                           nuvem_cat_area=nuvem_cat_area,
                           total_programas=total_programas,
                           total_destaque=total_destaque,
                           top_pais=top_pais,
                           tabela_ranking=fig_table.to_html(full_html=False, include_plotlyjs=False))
