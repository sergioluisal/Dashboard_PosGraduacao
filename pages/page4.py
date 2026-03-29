from flask import Blueprint, render_template, request
from data_loader import df, LAYOUT_KWARGS
import plotly.express as px
import pandas as pd
import re
import os

page4_bp = Blueprint('page4', __name__)

# ===============================
# ROTA
# ===============================
@page4_bp.route("/page4")
def estrutura():

    if df.empty:
        return "Erro ao carregar dados. Verifique o arquivo."

    # ===============================
    # FUNÇÃO: ITENS SEPARADOS
    # ===============================
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

    # ===============================
    # FUNÇÃO: PADRÕES
    # ===============================
    def contar_por_padroes(coluna):

        textos = df[coluna].dropna().astype(str).str.lower()

        padroes = {
            "Tese": [r"\btese\b"],
            "Créditos em disciplinas": [r"\bcréditos\b", r"\bdisciplinas\b"],
            "Outras atividades": [r"\boutras atividades\b"],
            "Artigo publicado/submetido": [r"\bartigo\b", r"\bpublicado\b", r"\bsubmetido\b"]
        }

        resultado = {}

        for categoria, regex_list in padroes.items():
            count = 0
            for texto in textos:
                if any(re.search(regex, texto) for regex in regex_list):
                    count += 1
            resultado[categoria] = count

        return pd.DataFrame(list(resultado.items()), columns=["Item", "Quantidade"])

    # ===============================
    # FUNÇÃO: GRÁFICO
    # ===============================
    def criar_grafico_barras(df_dados, titulo, cor):

        df_dados['ItemCurto'] = df_dados['Item'].apply(
            lambda x: str(x)[:45] + '...' if len(str(x)) > 45 else str(x)
        )

        fig = px.bar(
            df_dados,
            x='Quantidade',
            y='ItemCurto',
            orientation='h',
            title=f'<b>{titulo}</b>',
            color_discrete_sequence=[cor],
            text='Quantidade',
            hover_name='Item'
        )

        fig.update_layout(
            **LAYOUT_KWARGS,
            margin=dict(l=200, r=40, t=50, b=10),
            height=320,
            xaxis=dict(visible=False),
            yaxis=dict(title='', automargin=True)
        )

        fig.update_traces(
            textposition='auto',
            hovertemplate='<b>%{hovertext}</b><br>Quantidade: %{x}<extra></extra>'
        )

        return fig

    # ===============================
    # GRÁFICOS
    # ===============================
    fig_ingresso = criar_grafico_barras(
        contar_itens_separados("req_ingresso").head(10).sort_values(by='Quantidade'),
        'Requisitos de Ingresso',
        '#2563eb'
    )

    fig_selecao = criar_grafico_barras(
        contar_itens_separados("etapas_selecao").head(10).sort_values(by='Quantidade'),
        'Etapas do Processo Seletivo',
        '#3b82f6'
    )

    fig_titulo = criar_grafico_barras(
        contar_por_padroes("req_titulo").sort_values(by='Quantidade'),
        'Requisitos para Obtenção do Título',
        '#f97316'
    )

    fig_vis = criar_grafico_barras(
        contar_itens_separados("visibilidade").head(10).sort_values(by='Quantidade'),
        'Canais de Visibilidade Utilizados',
        '#fb923c'
    )

    fig_int = criar_grafico_barras(
        contar_itens_separados("internacionalizacao").head(10).sort_values(by='Quantidade'),
        'Estratégia de Internacionalização',
        '#c084fc'
    )

    fig_parcerias = criar_grafico_barras(
        contar_itens_separados("parcerias").head(15).sort_values(by='Quantidade'),
        'Ranking de Países Parceiros',
        '#9333ea'
    )

    resp_config = {'responsive': True, 'displayModeBar': False}

    return render_template(
        "page4.html",
        request=request,
        grafico_ingresso=fig_ingresso.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
        grafico_selecao=fig_selecao.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
        grafico_titulo=fig_titulo.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
        grafico_visibilidade=fig_vis.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
        grafico_int=fig_int.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
        grafico_parcerias=fig_parcerias.to_html(full_html=False, include_plotlyjs=False, config=resp_config)
    )
