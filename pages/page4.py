from flask import Blueprint, render_template, request
import plotly.express as px
import pandas as pd
from data_loader import df, LAYOUT_KWARGS

page4_bp = Blueprint('page4', __name__)

@page4_bp.route("/page4")
def estrutura():
    if df.empty:
        return "Erro ao carregar dados. Verifique o terminal."

    def contar_itens_separados(coluna):
        textos = df[coluna].dropna().astype(str)
        ignorar = ['nan', 'não informado', 'nao informado', 'nenhum', 'nenhuma', 'nd', 'n/a']
        
        itens = [
            item.strip() for sublist in textos.str.split(',') 
            for item in sublist 
            if item.strip() != '' and item.strip().lower() not in ignorar
        ]
        
        df_res = pd.Series(itens).value_counts().reset_index()
        df_res.columns = ['Item', 'Quantidade']
        return df_res

    # =========================================================
    # FUNÇÃO MESTRA PARA GRÁFICOS DE BARRAS RESPONSIVOS
    # =========================================================
    def criar_grafico_barras(df_dados, titulo, cor):
        # Aumentamos o limite para 45 letras para ler melhor a legenda
        df_dados['ItemCurto'] = df_dados['Item'].apply(lambda x: str(x)[:45] + '...' if len(str(x)) > 45 else str(x))
        
        fig = px.bar(df_dados, x='Quantidade', y='ItemCurto', orientation='h', 
                     title=f'<b>{titulo}</b>', color_discrete_sequence=[cor], text='Quantidade',
                     hover_name='Item') 
        
        fig.update_layout(
            **LAYOUT_KWARGS, 
            # AUMENTAMOS a margem esquerda (l=200) para o texto caber inteiro!
            margin=dict(l=200, r=40, t=50, b=10), 
            height=320, 
            autosize=True,
            xaxis=dict(visible=False), 
            yaxis=dict(title='', automargin=True)
        )
        
        fig.update_traces(
            textposition='auto', 
            hovertemplate='<b>%{hovertext}</b><br>Quantidade: %{x}<extra></extra>'
        )
        return fig

    # =========================================================
    # GERAR OS GRÁFICOS
    # =========================================================
    df_ing = contar_itens_separados("req_ingresso").head(10).sort_values(by='Quantidade', ascending=True)
    fig_ingresso = criar_grafico_barras(df_ing, 'Requisitos de Ingresso', '#2563eb')

    df_sel = contar_itens_separados("etapas_selecao").head(10).sort_values(by='Quantidade', ascending=True)
    fig_selecao = criar_grafico_barras(df_sel, 'Etapas do Processo Seletivo', '#3b82f6')

    df_tit = contar_itens_separados("req_titulo").head(10).sort_values(by='Quantidade', ascending=True)
    fig_titulo = criar_grafico_barras(df_tit, 'Requisitos para Obtenção do Título', '#f97316')

    df_vis = contar_itens_separados("visibilidade").head(10).sort_values(by='Quantidade', ascending=True)
    fig_vis = criar_grafico_barras(df_vis, 'Canais de Visibilidade Utilizados', '#fb923c')

    # =========================================================
    # ESTRATÉGIA DE INTERNACIONALIZAÇÃO (Agora em Barras!)
    # =========================================================
    df_int = contar_itens_separados("internacionalizacao").head(10).sort_values(by='Quantidade', ascending=True)
    fig_int = criar_grafico_barras(df_int, 'Estratégia de Internacionalização', '#c084fc')
    df_parcerias = contar_itens_separados("parcerias").head(15).sort_values(by='Quantidade', ascending=True)
    fig_parcerias = criar_grafico_barras(df_parcerias, 'Ranking de Países Parceiros', '#9333ea')

    resp_config = {'responsive': True, 'displayModeBar': False}

    return render_template("page4.html",
                           request=request,
                           grafico_ingresso=fig_ingresso.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                           grafico_selecao=fig_selecao.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                           grafico_titulo=fig_titulo.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                           grafico_visibilidade=fig_vis.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                           grafico_int=fig_int.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                           grafico_parcerias=fig_parcerias.to_html(full_html=False, include_plotlyjs=False, config=resp_config))