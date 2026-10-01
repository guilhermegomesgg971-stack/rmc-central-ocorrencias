from datetime import datetime
import os
import sqlite3
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Central de Ocorrências | Grupo RMC Mariano",
    page_icon="🛡️️",
    layout="centered",
)

# Estilização personalizada com visual limpo, claro e profissional
st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }
        /* Cabeçalho elegante com tons claros e suaves */
        .rmc-header {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            border-left: 8px solid #5a8c71; /* Verde Boticário */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 25px;
            text-align: center;
        }
        .rmc-title {
            color: #1e293b;
            margin: 0;
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 1px;
            font-family: sans-serif;
        }
        .rmc-subtitle {
            color: #64748b;
            margin: 8px 0 0 0;
            font-size: 14px;
            font-family: sans-serif;
        }
        /* Badges de marcas no topo */
        .brand-bar {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        .brand-dot {
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

# Configuração do Banco de Dados SQLite (Persistente na nuvem)
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
  conn.commit()
  conn.close()


init_db()


# Função para carregar os dados do banco SQLite
def carregar_ocorrencias():
  conn = sqlite3.connect(DB_PATH)
  df = pd.read_sql_query("SELECT * FROM ocorrencias", conn)
  conn.close()

  colunas = [
      "ID_Ocorrencia",
      "Data_Envio",
      "Nome_Supervisor",
      "Numero_Pedido",
      "Nome_Revendedora",
      "Codigo_Revendedor",
      "Data_Faturamento",
      "Relato_Problema",
      "Caminho_Anexo",
      "Solucao",
      "Status",
  ]
  if df.empty:
    return pd.DataFrame(columns=colunas, dtype=str)
  for col in colunas:
    if col not in df.columns:
      df[col] = ""
    else:
      df[col] = df[col].fillna("")
  return df


# Função para salvar uma nova ocorrência ou atualizar no banco
def salvar_nova_ocorrencia(dados):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT OR REPLACE INTO ocorrencias VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


# Inicializa o estado da sessão
if "df_ocorrencias" not in st.session_state:
  st.session_state.df_ocorrencias = carregar_ocorrencias()

# Abas principais (mantidas exatamente as suas)
aba_supervisor, aba_consulta, aba_gestor = st.tabs([
    "📝 Registrar Ocorrência",
    "🔍 Consultar Meu Pedido",
    "🕵️‍♂️ Caixa de Análise (Gestor)",
])

# ==========================================
# ABA 1: REGISTRO PELO SUPERVISOR
# ==========================================
with aba_supervisor:
  st.subheader("📋 Novo Registro de Ocorrência")
  st.markdown(
      "Preencha as informações abaixo para formalizar o problema do pedido perante"
      " a gestão."
  )

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
        placeholder=(
            "Descreva detalhadamente o ocorrido (ex: item faltando, produto"
            " avariado, caixa trocada)..."
        ),
        height=130,
    )

    arquivo_enviado = st.file_uploader(
        "Anexar Foto ou Vídeo Comprobatório (Opcional):",
        type=["png", "jpg", "jpeg", "mp4", "mov", "avi"],
    )

    st.markdown("<br>", unsafe_allow_html=True)
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
            "⚠️ Preencha os campos obrigatórios: **Nome do Supervisor**, **Número"
            " do Pedido** e o **Relato do Problema**!"
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

        # Salva diretamente no banco de dados SQLite persistente
        salvar_nova_ocorrencia(nova_linha)
        st.session_state.df_ocorrencias = carregar_ocorrencias()

        st.success(
            "✅ Ocorrência enviada com sucesso! A gestão foi notificada em"
            " tempo real."
        )

# ==========================================
# ABA 2: CONSULTA DE PEDIDOS (PARA OS SUPERVISORES)
# ==========================================
with aba_consulta:
  st.subheader("🔍 Consultar Status do Pedido")
  st.markdown(
      "Digite o **Número do Pedido** ou o **Nome do Supervisor** para verificar"
      " o andamento e a solução."
  )

  termo_busca = st.text_input(
      "Pesquisar por Pedido ou Supervisor:",
      placeholder="Ex: 123456 ou Carlos...",
  )

  # Atualiza os dados do banco para garantir consulta em tempo real
  st.session_state.df_ocorrencias = carregar_ocorrencias()
  df_oc = st.session_state.df_ocorrencias

  if termo_busca.strip():
    filtro_resultado = df_oc[
        df_oc["Numero_Pedido"]
        .str.contains(termo_busca.strip(), case=False, na=False)
        | df_oc["Nome_Supervisor"]
        .str.contains(termo_busca.strip(), case=False, na=False)
    ]

    if not filtro_resultado.empty:
      st.markdown(
          f"Encontrado(s) **{len(filtro_resultado)}** registro(s) para sua"
          f" busca:"
      )
      st.markdown("---")

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

          status_atual = row["Status"]
          st.markdown(f"📌 **Status Atual:** **{status_atual}**")

          solucao_resp = row["Solucao"] if pd.notna(row["Solucao"]) else ""
          if solucao_resp:
            st.success(f"🛠️ **Solução Registrada pela Gestão:** {solucao_resp}")
          else:
            st.info(
                "⏳ Este pedido aguarda análise ou verificação da equipe"
                " gestora."
            )
    else:
      st.warning(
          "⚠️ Nenhum pedido encontrado com esse termo. Verifique o número"
          " digitado e tente novamente."
      )
  else:
    st.info("ℹ️ Digite algo no campo acima para iniciar a pesquisa.")

# ==========================================
# ABA 3: SUA CAIXA DE ANÁLISE (GESTOR)
# ==========================================
with aba_gestor:
  st.subheader("🕵️‍♂️ Painel Gerencial de Ocorrências")
  st.markdown(
      "Acompanhe o fluxo de chamados, analise as evidências e registre as"
      " soluções aplicadas."
  )

  st.session_state.df_ocorrencias = carregar_ocorrencias()
  df_oc = st.session_state.df_ocorrencias

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

    if filtro_st != "Todos":
      df_exibir = df_oc[df_oc["Status"] == filtro_st]
    else:
      df_exibir = df_oc

    st.markdown(
        f"Exibindo **{len(df_exibir)}** registro(s) encontrado(s) no sistema."
    )
    st.markdown("---")

    for index, row in df_exibir.iterrows():
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
          st.markdown(f"📅 **Data Faturamento:** `{row['Data_Faturamento']}`")
          st.markdown(f"💬 **Relato do Supervisor:** *{row['Relato_Problema']}*")

          caminho_anexo = row["Caminho_Anexo"]
          if caminho_anexo and os.path.exists(caminho_anexo):
            st.markdown("📎 **Evidência Anexada:**")
            ext = caminho_anexo.lower().split(".")[-1]
            if ext in ["png", "jpg", "jpeg"]:
              st.image(
                  caminho_anexo,
                  caption=f"Evidência - Pedido {row['Numero_Pedido']}",
                  use_container_width=True,
              )
            elif ext in ["mp4", "mov", "avi"]:
              st.video(caminho_anexo)

          solucao_atual = (
              row["Solucao"] if pd.notna(row["Solucao"]) else ""
          )
          if solucao_atual:
            st.markdown(f"🛠️ **Como foi resolvido:** *{solucao_atual}*")

          st.markdown(f"📌 **Status Atual:** **{row['Status']}**")

        with col_c2:
          st.markdown("##### ⚙️ Ações e Solução")

          nova_solucao = st.text_area(
              "Registrar Solução:",
              value=solucao_atual,
              key=f"sol_text_{row['ID_Ocorrencia']}",
              height=85,
          )

          if st.button(
              "💾 Salvar Solução", key=f"save_sol_{row['ID_Ocorrencia']}"
          ):
            atualizar_campo_ocorrencia(
                row["ID_Ocorrencia"], "Solucao", nova_solucao.strip()
            )
            st.toast("Solução salva com sucesso!", icon="💾")
            st.rerun()

          st.markdown("---")

          col_b1, col_b2 = st.columns(2)
          with col_b1:
            if st.button(
                "🔍 Em Verif.", key=f"verif_{row['ID_Ocorrencia']}"
            ):
              atualizar_campo_ocorrencia(
                  row["ID_Ocorrencia"], "Status", "🔍 Em Verificação"
              )
              st.rerun()

          with col_b2:
            if st.button(
                "✅ Finalizar", key=f"fin_{row['ID_Ocorrencia']}"
            ):
              atualizar_campo_ocorrencia(
                  row["ID_Ocorrencia"], "Status", "✅ Problema Finalizado"
              )
              st.rerun()

          if st.button(
              "🗑️ Excluir",
              key=f"del_{row['ID_Ocorrencia']}",
              use_container_width=True,
          ):
            excluir_ocorrencia(row["ID_Ocorrencia"])
            st.warning("Registro excluído!")
            st.rerun()
  else:
    st.info("🎉 Nenhuma ocorrência registrada no momento.")
