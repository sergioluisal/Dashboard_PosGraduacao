from flask import Blueprint, render_template, request
import pandas as pd
import json

from data_loader import df, paises_lista

page2_bp = Blueprint('page2', __name__)

@page2_bp.route("/page2")
def comparativo():
    if df.empty:
        return "Erro ao carregar dados. Verifique o terminal."

    pais1 = request.args.get("pais1", "Brasil")
    pais2 = request.args.get("pais2", "México")
    
    if pais1 not in paises_lista: pais1 = paises_lista[0] if paises_lista else ""
    if pais2 not in paises_lista: pais2 = paises_lista[1] if len(paises_lista) > 1 else pais1

    df1 = df[df["pais"] == pais1]
    df2 = df[df["pais"] == pais2]

    # 1. KPIs
    kpis = {
        "p1_nome": pais1,
        "p2_nome": pais2,
        "p1_prog": len(df1),
        "p2_prog": len(df2),
        "p1_inst": df1["universidade"].nunique(),
        "p2_inst": df2["universidade"].nunique(),
        "p1_dur": f'{df1["duracao"].mean():.0f}' if not df1["duracao"].isna().all() else "-",
        "p2_dur": f'{df2["duracao"].mean():.0f}' if not df2["duracao"].isna().all() else "-",
        "p1_presencial": len(df1[df1["mod_ensino"].str.contains("Presencial", case=False, na=False)]),
        "p2_presencial": len(df2[df2["mod_ensino"].str.contains("Presencial", case=False, na=False)])
    }

    # 2. Dados para os Gráficos de Rosca (Concéntricos)
    def obter_distribuicao(coluna):
        categorias = list(set(df1[coluna].unique()).union(set(df2[coluna].unique())))
        c1 = df1[coluna].value_counts().reindex(categorias, fill_value=0).tolist()
        c2 = df2[coluna].value_counts().reindex(categorias, fill_value=0).tolist()
        return {"labels": categorias, "d1": c1, "d2": c2}

    graficos_data = {
        "ensino": obter_distribuicao("mod_ensino"),
        "natureza": obter_distribuicao("natureza"),
        "programa": obter_distribuicao("mod_programa")
    }

    # 3. Dados para o Gráfico Histórico (Linha)
    df_anos1 = df1.groupby("ano_inicio").size().reset_index(name="qtd")
    df_anos2 = df2.groupby("ano_inicio").size().reset_index(name="qtd")
    
    todos_anos = sorted(list(set(df_anos1["ano_inicio"].dropna().unique()).union(set(df_anos2["ano_inicio"].dropna().unique()))))
    todos_anos = [int(ano) for ano in todos_anos if ano >= 1990] # Filtrar anos muito antigos
    
    hist_d1 = [int(df_anos1[df_anos1["ano_inicio"] == ano]["qtd"].sum()) for ano in todos_anos]
    hist_d2 = [int(df_anos2[df_anos2["ano_inicio"] == ano]["qtd"].sum()) for ano in todos_anos]
    
    graficos_data["historico"] = {"anos": todos_anos, "d1": hist_d1, "d2": hist_d2}

    return render_template("page2.html",
                           request=request,
                           paises=paises_lista,
                           kpis=kpis,
                           graficos_data=graficos_data)