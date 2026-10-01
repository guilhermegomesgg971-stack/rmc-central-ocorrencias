from datetime import datetime
import os
import sqlite3
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Central de Ocorrências | Grupo RMC Mariano",
    page_icon="🛡️",
    layout="centered",
)

# Estilização personalizada
st.markdown(
    """
    <style>
        .main { background-color: #f8fafc; }
        .rmc-header {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            border-left: 8px solid #5a8c71;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 25px;
            text-align: center;
        }
        .rmc-title {
            color: #1e293b; margin: 0; font-size: 26px; font-weight: 700;
        }
        .rmc-subtitle {
            color: #64748b; margin: 8px 0 0 0; font-size: 14px;
        }
        .brand-bar {
            display: flex; justify-content: center; gap: 15px; margin-top: 15px;
        }
        .brand-dot {
            font-size: 12px; padding: 4px 12px; border-radius: 12px;
            color: white; font-weight: 600;
        }
    </style>
    <div class="rmc-header">
        <h2 class="rmc-title">GRUPO RMC MARIANO</h2>
        <p class="rmc-subtitle">Central de Ocorrências e Suporte Operacional</p>
        <div class="brand-bar">
            <span class="brand-dot" style="background-color: #5a8c71;">Boticário</span>
            <span class="brand-dot" style="background-color: #e6007e;">QDB</span>
            <span class="brand-dot" style="background-color: #8b2f3f;">O.U.i</span>
            <span class="brand-dot" style="background-color: #5b3256;">Eudora</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Configuração do Banco de Dados SQLite (Persistente)
PASTA_ATUAL = (
    os.path.dirname(os.path.abspath(__file__))
    if "__file__" in locals()
    else os.getcwd()
)
DB_PATH = os.path.join(PASTA_ATUAL, "rmc_ocorrencias.db")
PASTA_UPLOADS = os.path.join(PASTA_ATUAL, "uploads_ocorrencias")

if not os.path.exists(PASTA_UPLOADS):
  os.makedirs(PASTA_UPLOADS, exist_ok=True)


def init_db():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            ID_Ocorrencia TEXT PRIMARY KEY,
            Data_Envio TEXT,
            Nome_Supervisor TEXT,
            Numero_Pedido TEXT,
            Nome_Revendedora TEXT,
            Codigo_Revendedor TEXT,
            Data_Faturamento TEXT,
            Relato_Problema TEXT,
            Caminho_Anexo TEXT,
            Solucao TEXT,
            Status TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            Data TEXT,
            Nome TEXT,
            Estrelas TEXT,
            Sugestao TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


def carregar_ocorrencias():
  conn = sqlite3.connect(DB_PATH)
  df = pd.read_sql_query("SELECT * FROM ocorrencias", conn)
  conn.close()

  if df.empty:
    # Insere um registro de exemplo inicial se estiver vazio
    df_exemplo = pd.DataFrame([
        {
            "ID_Ocorrencia": "RMC-EXEMPLO01",
            "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome_Supervisor": "SUPERVISOR TESTE",
            "Numero_Pedido": "999888",
            "Nome_Revendedora": "MARIA CONSULTORA",
            "Codigo_Revendedor": "C001",
            "Data_Faturamento": datetime.now().strftime("%d/%m/%Y"),
            "Relato_Problema": (
                "Registro de exemplo para validação do painel."
            ),
            "Caminho_Anexo": "",
            "Solucao": "Exemplo de devolutiva da gestão.",
            "Status": "🟡 Pendente de Análise",
        }
    ])
    conn = sqlite3.connect(DB_PATH)
    df_exemplo.to_sql("ocorrencias", conn, if_exists="append", index=False)
    conn.close()
    return df_exemplo
  return df


def salvar_nova_ocorrencia(dados):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      """
        OR REPLACE INTO ocorrencias VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
      (
          dados["ID_Ocorrencia"],
          dados["Data_Envio"],
          dados["Nome_Supervisor"],
          dados["Numero_Pedido"],
          dados["Nome_Revendedora"],
          dados["Codigo_Revendedor"],
          dados["Data_Faturamento"],
          dados["Relato_Problema"],
          dados["Caminho_Anexo"],
          dados["Solucao"],
          dados["Status"],
      ),
  )
  conn.commit()
  conn.close()


def atualizar_campo_ocorrencia(id_ocorrencia, coluna, valor):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      f"UPDATE ocorrencias SET {coluna} = ? WHERE ID_Ocorrencia = ?",
      (valor, id_ocorrencia),
  )
  conn.commit()
  conn.close()


def excluir_ocorrencia(id_ocorrencia):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM ocorrencias WHERE ID_Ocorrencia = ?", (id_ocorrencia,))
  conn.commit()
  conn.close()


def carregar_avaliacoes():
  conn = sqlite3.connect(DB_PATH)
  df = pd.read_sql_query("SELECT * FROM avaliacoes", conn)
  conn.close()
  return df


def salvar_avaliacao(dados):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO avaliacoes VALUES (?, ?, ?, ?)
    """,
      (dados["Data"], dados["Nome"], dados["Estrelas"], dados["Sugestao"]),
  )
  conn.commit()
  conn.close()


# Abas principais
aba_supervisor, aba_consulta, aba_gestor, aba_avaliacao, aba_admin = st.tabs([
    "📝 Registrar Ocorrência",
    "🔍 Consultar Meu Pedido",
    "🕵️‍♂️ Caixa de Análise (Gestor)",
    "⭐ Avaliação e Feedback",
    "⚙️ Sincronização & Dados",
])

# ==========================================
# ABA 1: REGISTRO PELO SUPERVISOR
# ==========================================
with aba_supervisor:
  st.subheader("📋 Novo Registro de Ocorrência")
  st.markdown("Preencha as informações abaixo para formalizar o problema.")

  with st.form("form_reg_ocorrencia", clear_on_submit=True):
    st.markdown("#### 🔹 1. Dados do Pedido")
    col1, col2 = st.columns(2)
    with col1:
      nome_supervisor = st.text_input(
          "Nome do Supervisor *:", placeholder="Ex: Carlos Silva"
      )
      numero_pedido = st.text_input("Número do Pedido *:", placeholder="Ex: 123456")
      nome_revendedora = st.text_input("Nome da Revendedora:")
    with col2:
      codigo_revendedor = st.text_input("Código do Revendedor:")
      data_faturamento = st.text_input(
          "Data do Faturamento:",
          placeholder="Ex: 18/09/2026",
          value=datetime.now().strftime("%d/%m/%Y"),
      )

    st.markdown("---")
    st.markdown("#### 🔹 2. Relato do Problema e Evidência")
    relato_problema = st.text_area(
        "Relato do Problema *:",
        placeholder="Descreva detalhadamente o ocorrido...",
        height=130,
    )
    arquivo_enviado = st.file_uploader(
        "Anexar Foto ou Vídeo Comprobatório (Opcional):",
        type=["png", "jpg", "jpeg", "mp4", "mov", "avi"],
    )

    enviar = st.form_submit_button(
        "🚀 Enviar Ocorrência para a Gestão", use_container_width=True
    )

    if enviar:
      if (
          not nome_supervisor.strip()
          or not numero_pedido.strip()
          or not relato_problema.strip()
      ):
        st.error(
            "⚠️ Preencha os campos obrigatórios: **Nome do Supervisor**, "
            "**Número do Pedido** e o **Relato do Problema**!"
        )
      else:
        novo_id = f"RMC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        caminho_arquivo_salvo = ""
        if arquivo_enviado is not None:
          extensao = arquivo_enviado.name.split(".")[-1].lower()
          nome_arquivo = f"{novo_id}.{extensao}"
          caminho_arquivo_salvo = os.path.join(PASTA_UPLOADS, nome_arquivo)
          with open(caminho_arquivo_salvo, "wb") as f:
            f.write(arquivo_enviado.getbuffer())

        nova_linha = {
            "ID_Ocorrencia": novo_id,
            "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome_Supervisor": str(nome_supervisor).strip().upper(),
            "Numero_Pedido": str(numero_pedido).strip(),
            "Nome_Revendedora": str(nome_revendedora).strip().upper(),
            "Codigo_Revendedor": str(codigo_revendedor).strip(),
            "Data_Faturamento": str(data_faturamento).strip(),
            "Relato_Problema": str(relato_problema).strip(),
            "Caminho_Anexo": str(caminho_arquivo_salvo),
            "Solucao": "",
            "Status": "🟡 Pendente de Análise",
        }
        salvar_nova_ocorrencia(nova_linha)
        st.success(
            "✅ Ocorrência enviada com sucesso e salva permanentemente!"
        )

# ==========================================
# ABA 2: CONSULTA DE PEDIDOS
# ==========================================
with aba_consulta:
  st.subheader("🔍 Consultar Status do Pedido")
  termo_busca = st.text_input(
      "Pesquisar por Pedido ou Supervisor:",
      placeholder="Ex: 123456 ou Carlos...",
  )
  df_oc = carregar_ocorrencias()

  if termo_busca.strip():
    filtro_resultado = df_oc[
        df_oc["Numero_Pedido"]
        .str.contains(termo_busca.strip(), case=False, na=False)
        | df_oc["Nome_Supervisor"]
        .str.contains(termo_busca.strip(), case=False, na=False)
    ]
    if not filtro_resultado.empty:
      for _, row in filtro_resultado.iterrows():
        with st.container(border=True):
          st.markdown(
              f"**ID:** `{row['ID_Ocorrencia']}` | **Enviado em:**"
              f" `{row['Data_Envio']}`"
          )
          st.markdown(
              f"👤 **Supervisor:** `{row['Nome_Supervisor']}` | 📦 **Pedido:**"
              f" `{row['Numero_Pedido']}`"
          )
          st.markdown(
              f"👩‍💼 **Revendedora:** {row['Nome_Revendedora']} (Cód:"
              f" `{row['Codigo_Revendedor']}`)"
          )
          st.markdown(f"💬 **Seu Relato:** *{row['Relato_Problema']}*")
          st.markdown(f"📌 **Status Atual:** **{row['Status']}**")
          if row["Solucao"]:
            st.success(f"🛠️ **Devolutiva da Gestão:** {row['Solucao']}")
          else:
            st.info("⏳ Este pedido aguarda análise da equipe gestora.")
    else:
      st.warning("⚠️ Nenhum pedido encontrado com esse termo.")
  else:
    st.info("ℹ️ Digite algo no campo acima para iniciar a pesquisa.")

# ==========================================
# ABA 3: CAIXA DE ANÁLISE (GESTOR)
# ==========================================
with aba_gestor:
  st.subheader("🕵️‍♂️ Painel Gerencial de Ocorrências")
  df_oc = carregar_ocorrencias()

  if not df_oc.empty:
    filtro_st = st.selectbox(
        "🔍 Filtrar por Status do Processo:",
        [
            "Todos",
            "🟡 Pendente de Análise",
            "🔍 Em Verificação",
            "✅ Problema Finalizado",
        ],
    )
    df_exibir = (
        df_oc if filtro_st == "Todos" else df_oc[df_oc["Status"] == filtro_st]
    )
    st.markdown(f"Exibindo **{len(df_exibir)}** registro(s) no sistema.")
    st.markdown("---")

    for index, row in df_exibir.iterrows():
      id_unico = f"{row['ID_Ocorrencia']}_{index}"
      with st.container(border=True):
        col_c1, col_c2 = st.columns([2.3, 1.7])
        with col_c1:
          st.markdown(
              f"**ID:** `{row['ID_Ocorrencia']}` | **Enviado em:**"
              f" `{row['Data_Envio']}`"
          )
          st.markdown(
              f"👤 **Supervisor:** `{row['Nome_Supervisor']}` | 📦 **Pedido:**"
              f" `{row['Numero_Pedido']}`"
          )
          st.markdown(
              f"👩‍💼 **Revendedora:** {row['Nome_Revendedora']} (Cód:"
              f" `{row['Codigo_Revendedor']}`)"
          )
          st.markdown(f"💬 **Relato:** *{row['Relato_Problema']}*")
          if row["Caminho_Anexo"] and os.path.exists(row["Caminho_Anexo"]):
            st.image(row["Caminho_Anexo"], use_container_width=True)
          if row["Solucao"]:
            st.markdown(f"🛠️ **Devolutiva:** *{row['Solucao']}*")
          st.markdown(f"📌 **Status:** **{row['Status']}**")

        with col_c2:
          st.markdown("##### ⚙️ Ações")
          nova_solucao = st.text_area(
              "Devolutiva:",
              value=row["Solucao"],
              key=f"sol_text_{id_unico}",
              height=80,
          )
          if st.button("💾 Salvar Devolutiva", key=f"save_sol_{id_unico}"):
            atualizar_campo_ocorrencia(
                row["ID_Ocorrencia"], "Solucao", nova_solucao.strip()
            )
            st.toast("Devolutiva salva!", icon="💾")
            st.rerun()

          col_b1, col_b2 = st.columns(2)
          with col_b1:
            if st.button("🔍 Em Verif.", key=f"verif_{id_unico}"):
              atualizar_campo_ocorrencia(
                  row["ID_Ocorrencia"], "Status", "🔍 Em Verificação"
              )
              st.rerun()
          with col_b2:
            if st.button("✅ Finalizar", key=f"fin_{id_unico}"):
              atualizar_campo_ocorrencia(
                  row["ID_Ocorrencia"], "Status", "✅ Problema Finalizado"
              )
              st.rerun()

          if st.button(
              "🗑️ Excluir", key=f"del_{id_unico}", use_container_width=True
          ):
            excluir_ocorrencia(row["ID_Ocorrencia"])
            st.warning("Registro excluído!")
            st.rerun()
  else:
    st.info("🎉 Nenhuma ocorrência registrada.")

# ==========================================
# ABA 4: AVALIAÇÃO E SATISFAÇÃO
# ==========================================
with aba_avaliacao:
  st.subheader("⭐ Pesquisa de Satisfação")
  with st.form("form_avaliacao", clear_on_submit=True):
    mapa_estrelas = {
        "⭐ (1 - Muito Ruim)": "1",
        "⭐⭐ (2 - Ruim)": "2",
        "⭐⭐⭐ (3 - Regular)": "3",
        "⭐⭐⭐⭐ (4 - Bom)": "4",
        "⭐⭐⭐⭐⭐ (5 - Excelente)": "5",
    }
    escolha_estrela = st.selectbox("Avaliação:", options=list(mapa_estrelas.keys()))
    nome_avaliador = st.text_input("Seu Nome:")
    sugestao_melhoria = st.text_area("Sugestões:")
    if st.form_submit_button("📥 Enviar Avaliação", use_container_width=True):
      if nome_avaliador.strip():
        salvar_avaliacao({
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome": nome_avaliador.strip().upper(),
            "Estrelas": mapa_estrelas[escolha_estrela],
            "Sugestao": sugestao_melhoria.strip(),
        })
        st.success("🎉 Avaliação enviada!")
      else:
        st.error("Preencha seu nome.")

# ==========================================
# ABA 5: BACKUP E DADOS
# ==========================================
with aba_admin:
  st.subheader("⚙️ Central de Backup")
  df_admin = carregar_ocorrencias()
  st.markdown(f"📊 Registros salvos no banco: **{len(df_admin)}**")

  if not df_admin.empty:
    csv_dados = df_admin.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Backup Geral (.csv)",
        data=csv_dados,
        file_name="backup_ocorrencias.csv",
        mime="text/csv",
    )
