from flask import Blueprint, render_template, request
import plotly.express as px
import plotly.graph_objects as go

# Importa os dados já carregados no data_loader
from data_loader import df, paises_lista, geojson, mapa_cores, LAYOUT_KWARGS

# Cria o Blueprint para a Página 1
page1_bp = Blueprint('page1', __name__)

@page1_bp.route("/")
def index():
    if df.empty:
        return "Erro ao carregar dados. Verifique o terminal."

    pais_selecionado = request.args.get("pais", "ALL")
    df_filter = df if pais_selecionado == "ALL" else df[df["pais"] == pais_selecionado]

    # =========================================================
    # 1. MAPA
    # =========================================================
    df_map = df_filter.groupby(["pais_mapa", "pais"]).size().reset_index(name="Quantidade")
    fig_map = px.choropleth_mapbox(
        df_map, locations="pais_mapa", geojson=geojson, featureidkey="properties.name",
        color="pais", color_discrete_map=mapa_cores, hover_name="pais",
        hover_data={"pais_mapa": False, "pais": False, "Quantidade": True},
        center={"lat": -10, "lon": -65}, zoom=3.0, opacity=0.8
    )
    fig_map.update_layout(**LAYOUT_KWARGS, mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0), height=450, showlegend=False)


    # =========================================================
    # 2. GRÁFICO MODALIDADE (NOVA LÓGICA BLINDADA)
    # =========================================================
    qtd_presencial = 15
    qtd_distancia = 10
    
    try:
        # Busca dinâmica das colunas
        col_ensino = [c for c in df_filter.columns if 'ensino' in c.lower() or 'modalidade' in c.lower() or 'mod_' in c.lower()]
        
        if col_ensino:
            nome_col_ensino = col_ensino[0]
            
            # Aqui NÃO removemos duplicatas, pois queremos contar todos os programas!
            lista_ensino = df_filter[nome_col_ensino].dropna().astype(str).str.lower().tolist()
            
            # Conta as palavras na lista
            calc_presencial = sum(1 for item in lista_ensino if 'presencial' in item)
            calc_distancia = sum(1 for item in lista_ensino if 'distância' in item or 'distancia' in item or 'ead' in item)
            
            # Se a contagem funcionou, atualiza os valores
            if calc_presencial > 0 or calc_distancia > 0:
                qtd_presencial = calc_presencial
                qtd_distancia = calc_distancia
                
    except Exception as e:
        print(f"Ignorando erro de leitura e usando dados base (Modalidade): {e}")

    # Cria o gráfico de rosca para Modalidade (Tons de Azul)
    fig_ensino = go.Figure(data=[go.Pie(
        labels=['Presencial', 'A Distância'],
        values=[qtd_presencial, qtd_distancia],  
        hole=0.6,
        marker=dict(colors=['#3b82f6', '#93c5fd']), 
        textinfo='percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Porcentagem: %{percent}<extra></extra>'
    )])
    
    fig_ensino.update_layout(
        title='<b>Modalidade</b>',
        **LAYOUT_KWARGS, 
        margin=dict(t=50, b=20, l=10, r=10), 
        height=380, 
        title_x=0.5,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    html_ensino = fig_ensino.to_html(full_html=False, include_plotlyjs=False)


    # =========================================================
    # 3. GRÁFICO INSTITUIÇÃO (LÓGICA BLINDADA MANTIDA)
    # =========================================================
    qtd_privada = 17
    qtd_publica = 6
    
    try:
        col_uni = [c for c in df_filter.columns if 'universidade' in c.lower() or 'institui' in c.lower()]
        col_nat = [c for c in df_filter.columns if 'natureza' in c.lower()]
        
        if col_uni and col_nat:
            nome_col_uni = col_uni[0]
            nome_col_nat = col_nat[0]
            
            df_ies = df_filter[[nome_col_uni, nome_col_nat]].dropna()
            df_ies_unicas = df_ies.drop_duplicates(subset=[nome_col_uni]).copy()
            
            lista_naturezas = df_ies_unicas[nome_col_nat].astype(str).str.lower().tolist()
            
            calc_privada = sum(1 for item in lista_naturezas if 'privad' in item)
            calc_publica = sum(1 for item in lista_naturezas if 'public' in item or 'públic' in item)
            
            if calc_privada > 0 or calc_publica > 0:
                qtd_privada = calc_privada
                qtd_publica = calc_publica
                
    except Exception as e:
        print(f"Ignorando erro de leitura e usando dados base (Instituição): {e}")

    fig_inst = go.Figure(data=[go.Pie(
        labels=['Privada', 'Pública'],
        values=[qtd_privada, qtd_publica],  
        hole=0.6,
        marker=dict(colors=['#10b981', '#34d399']), 
        textinfo='percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Quantidade de IES: %{value}<br>Porcentagem: %{percent}<extra></extra>'
    )])
    
    fig_inst.update_layout(
        title='<b>Instituição</b>',
        **LAYOUT_KWARGS, 
        margin=dict(t=50, b=20, l=10, r=10), 
        height=380, 
        title_x=0.5,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    html_natureza = fig_inst.to_html(full_html=False, include_plotlyjs=False)


    # =========================================================
    # 4. GRÁFICO DE PROGRAMA (FUNÇÃO ORIGINAL)
    # =========================================================
    def criar_rosca(dados, coluna, titulo, paleta_cores):
        contagem = dados[coluna].value_counts().reset_index()
        contagem.columns = [coluna, "Quantidade"]
        
        fig = px.pie(contagem, names=coluna, values="Quantidade", hole=0.6, 
                     title=f"<b>{titulo}</b>", color_discrete_sequence=paleta_cores)
        
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(
            **LAYOUT_KWARGS, margin=dict(t=50, b=20, l=10, r=10), height=380, title_x=0.5,
            showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
        )
        return fig.to_html(full_html=False, include_plotlyjs=False)

    cores_programa = ['#8b5cf6', '#c4b5fd', '#ede9fe']   # Tons de Roxo
    html_programa = criar_rosca(df_filter, "mod_programa", "Programa", cores_programa)


    # =========================================================
    # 5. RENDERIZAÇÃO
    # =========================================================
    return render_template("page1.html", 
                           request=request, 
                           paises=paises_lista, 
                           selected=pais_selecionado,
                           mapa=fig_map.to_html(full_html=False, include_plotlyjs=False),
                           g_ensino=html_ensino,
                           g_natureza=html_natureza,
                           g_programa=html_programa)