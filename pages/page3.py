from flask import Blueprint, render_template, request
import plotly.express as px
import pandas as pd
import re

# Importa os dados já carregados no data_loader
from data_loader import df, LAYOUT_KWARGS

page3_bp = Blueprint('page3', __name__)

@page3_bp.route("/page3")
def distribuicao():
    if df.empty:
        return "Erro ao carregar dados. Verifique o terminal."

    # Ordenar por quantidade total para que os países com mais programas fiquem à esquerda
    ordem_paises = df['pais'].value_counts().index.tolist()

    # =========================================================
    # GRÁFICO 1: Distribuição por País e Modalidade
    # =========================================================
    """df_mod = df.groupby(['pais', 'mod_ensino']).size().reset_index(name='quantidade')
    fig_mod = px.bar(
        df_mod, x='pais', y='quantidade', color='mod_ensino',
        title='<b>Distribuição de Programas por Modalidade de Ensino</b>',
        labels={'pais': '', 'quantidade': 'Qtd. de Programas', 'mod_ensino': 'Modalidade'},
        barmode='stack', color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_mod.update_layout(
        **LAYOUT_KWARGS, margin=dict(t=50, b=50, l=20, r=20), height=450,
        xaxis={'categoryorder': 'array', 'categoryarray': ordem_paises},
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )"""

    # =========================================================
    # GRÁFICO 2: Distribuição por Oferta de Bolsas (Becas)
    # =========================================================
    df_bolsas = df.groupby(['pais', 'bolsas']).size().reset_index(name='quantidade')
    fig_bolsas = px.bar(
        df_bolsas, x='pais', y='quantidade', color='bolsas',
        title='<b>Distribuição de Programas por Oferta de Bolsas de Estudo</b>',
        labels={'pais': '', 'quantidade': 'Qtd. de Programas', 'bolsas': 'Bolsas de Estudo'},
        barmode='stack', 
        # Mantendo as cores Laranja e Azul que você pediu
        color_discrete_sequence=['#f97316', '#3b82f6', '#00e5ff', '#93c5fd'] 
    )
    fig_bolsas.update_layout(
        **LAYOUT_KWARGS, margin=dict(t=50, b=50, l=20, r=20), height=450,
        xaxis={'categoryorder': 'array', 'categoryarray': ordem_paises},
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )

    # =========================================================
    # GRÁFICO 3: Matriz de Excelência (Bolhas Laranja e Azul)
    # =========================================================
    def extrair_ranking(val):
        if pd.isna(val) or val == "Não classificada": return None
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else None

    df_qs = df.copy()
    df_qs['qs_num'] = df_qs['qs_ranking'].apply(extrair_ranking)
    df_qs = df_qs.dropna(subset=['qs_num'])

    # Agrupar por universidade
    df_univ = df_qs.groupby(['pais', 'universidade']).agg({
        'qs_num': 'min', 'qs_ranking': 'first'
    }).reset_index()

    # Lógica de Cores: Top 20 (Laranja) vs Demais (Azul)
    df_univ['Categoria'] = df_univ['qs_num'].apply(lambda x: 'Top 20' if x <= 20 else 'Demais')
    
    # Tamanho da bolha (1º lugar = maior bolha)
    df_univ['tamanho_bolha'] = 200 - df_univ['qs_num']
    df_univ.loc[df_univ['tamanho_bolha'] < 10, 'tamanho_bolha'] = 10

    fig_matriz = px.scatter(
        df_univ, x='pais', y='qs_num', color='Categoria', size='tamanho_bolha',
        hover_name='universidade',
        hover_data={'qs_ranking': True, 'pais': False, 'qs_num': False, 'Categoria': False, 'tamanho_bolha': False},
        color_discrete_map={'Top 20': '#f97316', 'Demais': '#3b82f6'}, # Laranja e Azul
        title='<b>Matriz de Excelência (QS World University Rankings)</b>'
    )
    
    # Inverter Eixo Y (Posição 1 no topo)
    fig_matriz.update_yaxes(autorange="reversed", title='Posição no Ranking QS')
    fig_matriz.update_xaxes(title='', categoryorder='array', categoryarray=ordem_paises)
    fig_matriz.update_layout(
        **LAYOUT_KWARGS, margin=dict(t=50, b=50, l=20, r=20), height=500,
        legend=dict(title='Classificação')
    )

    return render_template("page3.html",
                           request=request,
                           #grafico_modalidade=fig_mod.to_html(full_html=False, include_plotlyjs='cdn'),
                           grafico_bolsas=fig_bolsas.to_html(full_html=False, include_plotlyjs='cdn'), 
                           grafico_matriz=fig_matriz.to_html(full_html=False, include_plotlyjs='cdn'))