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

    # --- INÍCIO DO BLOCO DE FILTRO ---
    pais_selecionado = request.args.get("Pais", "ALL")
    # Lista de países para o dropdown
    paises_disponiveis = sorted(df['pais'].dropna().unique().tolist()) if 'pais' in df.columns else []
    
    # Aplica o filtro no DataFrame base que os gráficos usam
    df_filtrado = df if pais_selecionado == "ALL" else df[df["pais"] == pais_selecionado]
    # --- FIM DO BLOCO DE FILTRO ---

    # Ordenar pela contagem do dataframe filtrado
    ordem_paises = df_filtrado['pais'].value_counts().index.tolist()

    # =========================================================
    # GRÁFICO 2: Distribuição por Oferta de Bolsas (Usando df_filtrado)
    # =========================================================
    df_bolsas = df_filtrado.groupby(['pais', 'bolsas']).size().reset_index(name='quantidade')
    fig_bolsas = px.bar(
        df_bolsas, x='pais', y='quantidade', color='bolsas',
        title='<b>Distribuição de Programas por Oferta de Bolsas de Estudo</b>',
        labels={'pais': '', 'quantidade': 'Qtd. de Programas', 'bolsas': 'Bolsas de Estudo'},
        barmode='stack', 
        color_discrete_sequence=['#f97316', '#3b82f6', '#00e5ff', '#93c5fd'] 
    )
    fig_bolsas.update_layout(
        **LAYOUT_KWARGS, margin=dict(t=50, b=50, l=20, r=20), height=450,
        xaxis={'categoryorder': 'array', 'categoryarray': ordem_paises},
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
    )

    # =========================================================
    # GRÁFICO 3: Matriz de Excelência (Usando df_filtrado)
    # =========================================================
    def extrair_ranking(val):
        if pd.isna(val) or val == "Não classificada": return None
        nums = re.findall(r'\d+', str(val))
        return int(nums[0]) if nums else None

    df_qs = df_filtrado.copy()
    df_qs['qs_num'] = df_qs['qs_ranking'].apply(extrair_ranking)
    df_qs = df_qs.dropna(subset=['qs_num'])

    df_univ = df_qs.groupby(['pais', 'universidade']).agg({'qs_num': 'min', 'qs_ranking': 'first'}).reset_index()
    df_univ['Categoria'] = df_univ['qs_num'].apply(lambda x: 'Top 20' if x <= 20 else 'Demais')
    df_univ['tamanho_bolha'] = 200 - df_univ['qs_num']
    df_univ.loc[df_univ['tamanho_bolha'] < 10, 'tamanho_bolha'] = 10

    fig_matriz = px.scatter(
        df_univ, x='pais', y='qs_num', color='Categoria', size='tamanho_bolha',
        hover_name='universidade',
        color_discrete_map={'Top 20': '#f97316', 'Demais': '#3b82f6'},
        title='<b>Matriz de Excelência (QS World University Rankings)</b>'
    )
    
    fig_matriz.update_yaxes(autorange="reversed", title='Posição no Ranking QS')
    fig_matriz.update_xaxes(title='', categoryorder='array', categoryarray=ordem_paises)
    fig_matriz.update_layout(**LAYOUT_KWARGS, margin=dict(t=50, b=50, l=20, r=20), height=500)

    # Retorno com os dados do filtro para o HTML
    return render_template("page3.html",
                           paises=paises_disponiveis,
                           selecionado=pais_selecionado,
                           grafico_bolsas=fig_bolsas.to_html(full_html=False, include_plotlyjs='cdn'), 
                           grafico_matriz=fig_matriz.to_html(full_html=False, include_plotlyjs='cdn'))
                           
