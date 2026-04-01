from flask import Blueprint, render_template, request
from data_loader import df, LAYOUT_KWARGS
import plotly.express as px
import pandas as pd
import re
import os

page4_bp = Blueprint('page4', __name__)

def load_data():
    caminho_arquivo = "Analise.xlsx"
    if not os.path.exists(caminho_arquivo):
        caminho_arquivo = os.path.join("..", "Analise.xlsx")
    
    try:
        temp_df = pd.read_excel(caminho_arquivo)
        temp_df.columns = [str(c).strip() for c in temp_df.columns]
        return temp_df
    except:
        return None

df = load_data()

# 2. Lógica de Análise - CERTIFIQUE-SE QUE RECEBE df_fonte
def contar_itens(df_fonte, nome_coluna):
    if df_fonte is None or nome_coluna not in df_fonte.columns:
        return pd.DataFrame()
    
    # O restante do código usa df_fonte agora, não o df global
    series = df_fonte[nome_coluna].dropna().astype(str)
    ignorar = ['nan', 'não informado', 'nao informado', 'n/a', '-----', 'nd']
    
    todos_itens = [item.strip() for linha in series for item in linha.split(',') 
                   if item.strip() != '' and item.strip().lower() not in ignorar]
    
    if not todos_itens:
        return pd.DataFrame()

    df_res = pd.Series(todos_itens).value_counts().reset_index()
    df_res.columns = ['Item', 'Quantidade']
    return df_res

# 3. Transformando o Gráfico em HTML
def gerar_grafico_html(df_filtrado, col_nome, titulo, cor):
    dados = contar_itens(df_filtrado, col_nome)
    if dados.empty:
        return f"<p>Sem dados para {titulo}</p>"
        
    dados = dados.head(10).sort_values(by='Quantidade')
    fig = px.bar(dados, x='Quantidade', y='Item', orientation='h',
                 title=f"<b>{titulo}</b>", color_discrete_sequence=[cor], text='Quantidade')
    
    fig.update_layout(template="plotly_white", margin=dict(l=200, r=20, t=50, b=20), height=350)
    fig.update_traces(textposition='inside', textangle=0, insidetextfont=dict(color='#1e293b', size=12), cliponaxis=False)
    
    # A MÁGICA DO FLASK: Converte a figura para código HTML
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

@page4_bp.route("/page4")
def estrutura():
    if df is None:
        return "Erro: Arquivo Analise.xlsx não encontrado."

    # --- LÓGICA DO FILTRO ---
    # Captura o país (certifique-se que o nome no HTML é 'pais')
    pais_selecionado = request.args.get("Pais", "ALL")
    
    # Gera a lista de países para o dropdown
    paises_disponiveis = sorted(df['Pais'].dropna().unique().tolist()) if 'Pais' in df.columns else []

    # Aplica o filtro no DataFrame
    df_filter = df if pais_selecionado == "ALL" else df[df["Pais"] == pais_selecionado]
    
    # Gera os gráficos usando o df_filter
    contexto = {
        'paises': paises_disponiveis,
        'selecionado': pais_selecionado,
        'g_ingresso': gerar_grafico_html(df_filter, 'Requisitos para ingresso no programa', 'Requisitos de Ingresso', '#2563eb'),
        'g_selecao': gerar_grafico_html(df_filter, 'Etapas processo seletivo', 'Etapas de Seleção', '#3b82f6'),
        'g_titulo': gerar_grafico_html(df_filter, 'Requisitos para obtenção do título de doutor', 'Requisitos para o Título', '#f97316'),
        'g_vis': gerar_grafico_html(df_filter, 'Quais?', 'Canais de Visibilidade', '#fb923c'),
        'g_int': gerar_grafico_html(df_filter, 'Internacionalização', 'Estratégia de Internacionalização', '#c084fc'),
        'g_parcerias': gerar_grafico_html(df_filter, 'Quais países', 'Ranking de Países Parceiros', '#9333ea')
    }

    # O return deve ser a última linha e deve usar o nome correto do seu arquivo HTML
    return render_template('page4.html', **contexto)
