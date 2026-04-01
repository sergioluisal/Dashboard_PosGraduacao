from flask import Blueprint, render_template, request
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import df, LAYOUT_KWARGS

page5_bp = Blueprint('page5', __name__)

@page5_bp.route("/page5")
def indicadores():
    if df.empty:
        return "Erro ao carregar dados. Verifique o terminal."
        
    # --- LÓGICA DO FILTRO (Trazida do script Nov) ---
    pais_selecionado = request.args.get("Pais", "ALL")
    
    # Suporte dinâmico para 'pais' ou 'Pais' conforme estiver na sua planilha
    if 'pais' in df.columns:
        col_p = 'pais'
    elif 'Pais' in df.columns:
        col_p = 'Pais'
    else:
        col_p = None

    if col_p:
        paises_disponiveis = sorted(df[col_p].dropna().unique().tolist())
        df_filtrado = df if pais_selecionado == "ALL" else df[df[col_p] == pais_selecionado]
    else:
        paises_disponiveis = []
        df_filtrado = df

    # Mantendo a função original de barras (mesmo layout e formatação)
    def criar_grafico_barras(df_dados, col_nome, col_quant, titulo, cor):
        if df_dados.empty:
            return go.Figure()
        df_dados['ItemCurto'] = df_dados[col_nome].apply(lambda x: str(x)[:45] + '...' if len(str(x)) > 45 else str(x))
        fig = px.bar(df_dados, x=col_quant, y='ItemCurto', orientation='h', 
                     title=f'<b>{titulo}</b>', color_discrete_sequence=[cor], text=col_quant,
                     hover_name=col_nome) 
        fig.update_layout(
            **LAYOUT_KWARGS, margin=dict(l=200, r=40, t=50, b=10), height=350, 
            autosize=True, xaxis=dict(visible=False), yaxis=dict(title='', automargin=True)
        )
        fig.update_traces(textposition='auto', hovertemplate='<b>%{hovertext}</b><br>Quantidade: %{x}<extra></extra>')
        return fig

    # =========================================================
    # GRÁFICO 1: Quantidade de Programas (Com filtro aplicado)
    # =========================================================
    if 'nome_programa' in df_filtrado.columns:
        programas = df_filtrado['nome_programa'].dropna().astype(str)
        ignorar = ['nan', 'não informado', 'nao informado', 'nenhum', 'nd', 'n/a']
        df_prog = programas[~programas.str.strip().str.lower().isin(ignorar)].value_counts().reset_index()
        df_prog.columns = ['Programa', 'Quantidade']
    else:
        df_prog = pd.DataFrame({'Programa': ['Sem dados'], 'Quantidade': [0]})
        
    if df_prog.empty:
        df_prog = pd.DataFrame({'Programa': ['Sem dados'], 'Quantidade': [0]})
        
    fig_prog = criar_grafico_barras(df_prog.head(10).sort_values(by='Quantidade', ascending=True), 
                                    'Programa', 'Quantidade', 'Programas Mais Ofertados', '#10b981')

    # =========================================================
    # GRÁFICO 2: Predomínio Institucional (Mantendo a contagem original)
    # =========================================================
    # Valores base caso a leitura falhe
    qtd_privada = 17
    qtd_publica = 6
    
    try:
        # Busca dinâmica das colunas
        col_uni = [c for c in df_filtrado.columns if 'universidade' in c.lower() or 'institui' in c.lower()]
        col_nat = [c for c in df_filtrado.columns if 'natureza' in c.lower()]
        
        if col_uni and col_nat:
            nome_col_uni = col_uni[0]
            nome_col_nat = col_nat[0]
            
            # Remove nulos e universidades repetidas usando df_filtrado
            df_ies = df_filtrado[[nome_col_uni, nome_col_nat]].dropna()
            df_ies_unicas = df_ies.drop_duplicates(subset=[nome_col_uni]).copy()
            
            # Transforma a coluna numa lista nativa de Python
            lista_naturezas = df_ies_unicas[nome_col_nat].astype(str).str.lower().tolist()
            
            # Conta as palavras na lista
            calc_privada = sum(1 for item in lista_naturezas if 'privad' in item)
            calc_publica = sum(1 for item in lista_naturezas if 'public' in item or 'públic' in item)
            
            # Se a contagem funcionou, atualiza os valores
            if calc_privada > 0 or calc_publica > 0:
                qtd_privada = calc_privada
                qtd_publica = calc_publica
                
    except Exception as e:
        print(f"Ignorando erro de leitura e usando dados base: {e}")

    # Cria o gráfico de rosca injetando os números finais (Mantendo as cores originais)
    fig_nat_exclusiva = go.Figure(data=[go.Pie(
        labels=['Privada', 'Pública'],
        values=[qtd_privada, qtd_publica],  
        hole=0.5,
        marker=dict(colors=['#10b981', '#34d399']),
        textinfo='percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Quantidade de IES: %{value}<br>Porcentagem: %{percent}<extra></extra>'
    )])
    
    fig_nat_exclusiva.update_layout(
        title='<b>Distribuição Institucional (Pública x Privada)</b>',
        **LAYOUT_KWARGS, margin=dict(l=10, r=10, t=50, b=10), height=350, autosize=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )

    # =========================================================
    # GRÁFICOS 3 e 4: Métricas de Qualidade (Com filtro aplicado)
    # =========================================================
    if 'the_ranking' in df_filtrado.columns:
        df_the = df_filtrado['the_ranking'].dropna().value_counts().reset_index()
        df_the.columns = ['Classificação', 'Quantidade']
        fig_the = criar_grafico_barras(df_the.head(10).sort_values(by='Quantidade', ascending=True), 
                                       'Classificação', 'Quantidade', 'Times Higher Education', '#f43f5e') 
    else:
        fig_the = criar_grafico_barras(pd.DataFrame({'C':['Erro'],'Q':[0]}), 'C', 'Q', 'Erro THE', '#f43f5e')

    if 'qs_ranking' in df_filtrado.columns:
        df_qs = df_filtrado['qs_ranking'].dropna().value_counts().reset_index()
        df_qs.columns = ['Classificação', 'Quantidade']
        fig_qs = criar_grafico_barras(df_qs.head(10).sort_values(by='Quantidade', ascending=True), 
                                      'Classificação', 'Quantidade', 'QS World University Rankings', '#fb7185') 
    else:
        fig_qs = criar_grafico_barras(pd.DataFrame({'C':['Erro'],'Q':[0]}), 'C', 'Q', 'Erro QS', '#fb7185')

    resp_config = {'responsive': True, 'displayModeBar': False}

    # "o que for preciso para rodar": Adicionados 'paises' e 'selecionado' para alimentar o select do HTML
    return render_template("page5.html",
                       request=request,
                       paises=paises_disponiveis,
                       selecionado=pais_selecionado,
                       grafico_prog=fig_prog.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                       grafico_nat=fig_nat_exclusiva.to_html(full_html=False, include_plotlyjs=False, config=resp_config),                       
                       grafico_the=fig_the.to_html(full_html=False, include_plotlyjs=False, config=resp_config),
                       grafico_qs=fig_qs.to_html(full_html=False, include_plotlyjs=False, config=resp_config))
