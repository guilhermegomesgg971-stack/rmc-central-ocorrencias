from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Central de Ocorrências | Grupo RMC Mariano",
    page_icon="🛡️",
    layout="centered",
)

# Estilização personalizada com visual limpo, claro e profissional
st.markdown(
    """
    <style>
        .main {
            background-color: #f8fafc;
        }
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

# Caminhos absolutos dos arquivos
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
DB_OCORRENCIAS = os.path.join(PASTA_ATUAL, "dados_ocorrencias.csv")
DB_AVALIACOES = os.path.join(PASTA_ATUAL, "dados_avaliacoes.csv")
PASTA_UPLOADS = os.path.join(PASTA_ATUAL, "uploads_ocorrencias")

if not os.path.exists(PASTA_UPLOADS):
  os.makedirs(PASTA_UPLOADS, exist_ok=True)

COLUNAS_OCORRENCIAS = [
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


def carregar_ocorrencias():
  if os.path.exists(DB_OCORRENCIAS):
    try:
      df = pd.read_csv(DB_OCORRENCIAS, dtype=str)
      for col in COLUNAS_OCORRENCIAS:
        if col not in df.columns:
          df[col] = ""
        else:
          df[col] = df[col].fillna("")
      
      if df.empty or len(df.dropna(how="all")) == 0:
        df_exemplo = pd.DataFrame([{
            "ID_Ocorrencia": "RMC-EXEMPLO01",
            "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome_Supervisor": "SUPERVISOR TESTE",
            "Numero_Pedido": "999888",
            "Nome_Revendedora": "MARIA CONSULTORA",
            "Codigo_Revendedor": "C001",
            "Data_Faturamento": datetime.now().strftime("%d/%m/%Y"),
            "Relato_Problema": "Este é um registro de exemplo automático para validação do painel.",
            "Caminho_Anexo": "",
            "Solucao": "Exemplo de devolutiva da gestão.",
            "Status": "🟡 Pendente de Análise"
        }])
        df_exemplo.to_csv(DB_OCORRENCIAS, index=False)
        return df_exemplo

      return df
    except Exception as e:
      st.error(f"Erro ao ler CSV de ocorrências: {e}")
      return pd.DataFrame(columns=COLUNAS_OCORRENCIAS, dtype=str)
  else:
    df_exemplo = pd.DataFrame([{
        "ID_Ocorrencia": "RMC-EXEMPLO01",
        "Data_Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Nome_Supervisor": "SUPERVISOR TESTE",
        "Numero_Pedido": "999888",
        "Nome_Revendedora": "MARIA CONSULTORA",
        "Codigo_Revendedor": "C001",
        "Data_Faturamento": datetime.now().strftime("%d/%m/%Y"),
        "Relato_Problema": "Este é um registro de exemplo automático para validação do painel.",
        "Caminho_Anexo": "",
        "Solucao": "Exemplo de devolutiva da gestão.",
        "Status": "🟡 Pendente de Análise"
    }])
    df_exemplo.to_csv(DB_OCORRENCIAS, index=False)
    return df_exemplo


def salvar_ocorrencias(df):
  try:
    df.to_csv(DB_OCORRENCIAS, index=False)
  except Exception as e:
    st.error(f"Erro ao salvar arquivo de ocorrências: {e}")


def carregar_avaliacoes():
  colunas = ["Data", "Nome", "Estrelas", "Sugestao"]
  if os.path.exists(DB_AVALIACOES):
    try:
      df = pd.read_csv(DB_AVALIACOES, dtype=str)
      for col in colunas:
        if col not in df.columns:
          df[col] = ""
        else:
          df[col] = df[col].fillna("")
      return df
    except Exception:
      return pd.DataFrame(columns=colunas, dtype=str)
  else:
    return pd.DataFrame(columns=colunas, dtype=str)


def salvar_avaliacoes(df):
  df.to_csv(DB_AVALIACOES, index=False)


# Inicializa a sessão
st.session_state.df_ocorrencias = carregar_ocorrencias()

if "df_avaliacoes" not in st.session_state:
  st.session_state.df_avaliacoes = carregar_avaliacoes()

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
  st.markdown("Preencha as informações abaixo para formalizar o problema do pedido perante a gestão.")

  with st.form("form_reg_ocorrencia", clear_on_submit=True):
    st.markdown("#### 🔹 1. Dados do Pedido")
    col1, col2 = st.columns(2)
    with col1:
      nome_supervisor = st.text_input("Nome do Supervisor *:", placeholder="Ex: Carlos Silva")
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

    st.markdown("<br>", unsafe_allow_html=True)
    enviar = st.form_submit_button("🚀 Enviar Ocorrência para a Gestão", use_container_width=True)

    if enviar:
      if not nome_supervisor.strip() or not numero_pedido.strip() or not relato_problema.strip():
        st.error("⚠️ Preencha os campos obrigatórios: **Nome do Supervisor**, **Número do Pedido** e o **Relato do Problema**!")
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

        df_atual = carregar_ocorrencias()
        df_atual = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
        salvar_ocorrencias(df_atual)
        st.session_state.df_ocorrencias = df_atual
        st.success("✅ Ocorrência enviada com sucesso! A gestão foi notificada em tempo real.")

# ==========================================
# ABA 2: CONSULTA DE PEDIDOS
# ==========================================
with aba_consulta:
  st.subheader("🔍 Consultar Status do Pedido")
  st.markdown("Digite o **Número do Pedido** ou o **Nome do Supervisor** para verificar o andamento.")

  termo_busca = st.text_input("Pesquisar por Pedido ou Supervisor:", placeholder="Ex: 123456 ou Carlos...", key="busca_consulta_ped")
  df_oc = carregar_ocorrencias()

  if termo_busca.strip():
    filtro_resultado = df_oc[
        df_oc["Numero_Pedido"].str.contains(termo_busca.strip(), case=False, na=False)
        | df_oc["Nome_Supervisor"].str.contains(termo_busca.strip(), case=False, na=False)
    ]

    if not filtro_resultado.empty:
      st.markdown(f"Encontrado(s) **{len(filtro_resultado)}** registro(s):")
      st.markdown("---")

      for _, row in filtro_resultado.iterrows():
        with st.container(border=True):
          st.markdown(f"**ID:** `{row['ID_Ocorrencia']}` | **Enviado em:** `{row['Data_Envio']}`")
          st.markdown(f"👤 **Supervisor:** `{row['Nome_Supervisor']}` | 📦 **Pedido:** `{row['Numero_Pedido']}`")
          st.markdown(f"👩‍💼 **Revendedora:** {row['Nome_Revendedora']} (Cód: `{row['Codigo_Revendedor']}`)")
          st.markdown(f"💬 **Seu Relato:** *{row['Relato_Problema']}*")
          st.markdown(f"📌 **Status Atual:** **{row['Status']}**")

          solucao_resp = row["Solucao"] if pd.notna(row["Solucao"]) else ""
          if solucao_resp:
            st.success(f"🛠️ **Devolutiva da Gestão:** {solucao_resp}")
          else:
            st.info("⏳ Este pedido aguarda análise ou verificação da equipe gestora.")
    else:
      st.warning("⚠️ Nenhum pedido encontrado com esse termo.")
  else:
    st.info("ℹ️ Digite algo no campo acima para iniciar a pesquisa.")

# ==========================================
# ABA 3: CAIXA DE ANÁLISE (GESTOR)
# ==========================================
with aba_gestor:
  st.subheader("🕵️‍♂️ Painel Gerencial de Ocorrências")
  st.markdown("Acompanhe o fluxo de chamados, analise as evidências e registre a devolutiva.")

  df_oc = carregar_ocorrencias()

  if not df_oc.empty:
    filtro_st = st.selectbox(
        "🔍 Filtrar por Status do Processo:",
        ["Todos", "🟡 Pendente de Análise", "🔍 Em Verificação", "✅ Problema Finalizado"],
        key="filtro_status_gestor"
    )

    if filtro_st != "Todos":
      df_exibir = df_oc[df_oc["Status"] == filtro_st]
    else:
      df_exibir = df_oc

    st.markdown(f"Exibindo **{len(df_exibir)}** registro(s) no sistema.")
    st.markdown("---")

    for index, row in df_exibir.iterrows():
      # Adicionamos o índice (index) na chave para garantir total unicidade e evitar o erro
      id_unico = f"{row['ID_Ocorrencia']}_{index}"

      with st.container(border=True):
        col_c1, col_c2 = st.columns([2.3, 1.7])

        with col_c1:
          st.markdown(f"**ID:** `{row['ID_Ocorrencia']}` | **Enviado em:** `{row['Data_Envio']}`")
          st.markdown(f"👤 **Supervisor:** `{row['Nome_Supervisor']}` | 📦 **Pedido:** `{row['Numero_Pedido']}`")
          st.markdown(f"👩‍💼 **Revendedora:** {row['Nome_Revendedora']} (Cód: `{row['Codigo_Revendedor']}`)")
          st.markdown(f"📅 **Data Faturamento:** `{row['Data_Faturamento']}`")
          st.markdown(f"💬 **Relato do Supervisor:** *{row['Relato_Problema']}*")

          caminho_anexo = row["Caminho_Anexo"]
          if caminho_anexo and os.path.exists(caminho_anexo):
            st.markdown("📎 **Evidência Anexada:**")
            ext = caminho_anexo.lower().split(".")[-1]
            if ext in ["png", "jpg", "jpeg"]:
              st.image(caminho_anexo, caption=f"Evidência - Pedido {row['Numero_Pedido']}", use_container_width=True)
            elif ext in ["mp4", "mov", "avi"]:
              st.video(caminho_anexo)

          solucao_atual = row["Solucao"] if pd.notna(row["Solucao"]) else ""
          if solucao_atual:
            st.markdown(f"🛠️ **Devolutiva Registrada:** *{solucao_atual}*")

          st.markdown(f"📌 **Status Atual:** **{row['Status']}**")

        with col_c2:
          st.markdown("##### ⚙️ Ações e Devolutiva")

          nova_solucao = st.text_area(
              "Digite ou cole a Devolutiva:",
              value=solucao_atual,
              key=f"sol_text_{id_unico}",
              placeholder="Escreva a resposta para o supervisor...",
              height=90,
          )

          if st.button("💾 Salvar Devolutiva", key=f"save_sol_{id_unico}"):
            df_atualizado = carregar_ocorrencias()
            idx_match = df_atualizado[df_atualizado["ID_Ocorrencia"] == row["ID_Ocorrencia"]].index
            if not idx_match.empty:
              df_atualizado.at[idx_match[0], "Solucao"] = nova_solucao.strip()
              salvar_ocorrencias(df_atualizado)
              st.toast("Devolutiva salva com sucesso!", icon="💾")
              st.rerun()

          st.markdown("---")
          col_b1, col_b2 = st.columns(2)
          with col_b1:
            if st.button("🔍 Em Verif.", key=f"verif_{id_unico}"):
              df_atualizado = carregar_ocorrencias()
              idx_match = df_atualizado[df_atualizado["ID_Ocorrencia"] == row["ID_Ocorrencia"]].index
              if not idx_match.empty:
                df_atualizado.at[idx_match[0], "Status"] = "🔍 Em Verificação"
                salvar_ocorrencias(df_atualizado)
                st.rerun()

          with col_b2:
            if st.button("✅ Finalizar", key=f"fin_{id_unico}"):
              df_atualizado = carregar_ocorrencias()
              idx_match = df_atualizado[df_atualizado["ID_Ocorrencia"] == row["ID_Ocorrencia"]].index
              if not idx_match.empty:
                df_atualizado.at[idx_match[0], "Status"] = "✅ Problema Finalizado"
                salvar_ocorrencias(df_atualizado)
                st.rerun()

          if st.button("🗑️ Excluir", key=f"del_{id_unico}", use_container_width=True):
            df_atualizado = carregar_ocorrencias()
            df_atualizado = df_atualizado[df_atualizado["ID_Ocorrencia"] != row["ID_Ocorrencia"]].reset_index(drop=True)
            salvar_ocorrencias(df_atualizado)
            st.warning("Registro excluído!")
            st.rerun()
  else:
    st.info("🎉 Nenhuma ocorrência registrada no momento.")

# ==========================================
# ABA 4: AVALIAÇÃO E SATISFAÇÃO
# ==========================================
with aba_avaliacao:
  st.subheader("⭐ Pesquisa de Satisfação e Melhorias")
  st.markdown("Sua opinião é fundamental para aprimorarmos nossa Central de Ocorrências.")

  with st.form("form_avaliacao", clear_on_submit=True):
    mapa_estrelas = {
        "⭐ (1 - Muito Ruim)": "1",
        "⭐⭐ (2 - Ruim)": "2",
        "⭐⭐⭐ (3 - Regular)": "3",
        "⭐⭐⭐⭐ (4 - Bom)": "4",
        "⭐⭐⭐⭐⭐ (5 - Excelente)": "5",
    }
    escolha_estrela = st.selectbox("Como você avalia o sistema?", options=list(mapa_estrelas.keys()), key="select_estrelas_av")
    nome_avaliador = st.text_input("Seu Nome:", placeholder="Ex: Maria Oliveira", key="input_nome_av")
    sugestao_melhoria = st.text_area("Sugestões de melhorias ou comentários:", height=120, key="txt_sugestao_av")

    btn_enviar_avaliacao = st.form_submit_button("📥 Enviar Avaliação", use_container_width=True)

    if btn_enviar_avaliacao:
      if not nome_avaliador.strip():
        st.error("⚠️ Preencha o campo **Seu Nome**!")
      else:
        nova_avaliacao = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome": str(nome_avaliador).strip().upper(),
            "Estrelas": mapa_estrelas[escolha_estrela],
            "Sugestao": str(sugestao_melhoria).strip(),
        }
        df_av = carregar_avaliacoes()
        df_av = pd.concat([df_av, pd.DataFrame([nova_avaliacao])], ignore_index=True)
        salvar_avaliacoes(df_av)
        st.success("🎉 Muito obrigado! Sua avaliação foi enviada com sucesso.")

# ==========================================
# ABA 5: SINCRONIZAÇÃO E BACKUP DE EMERGÊNCIA
# ==========================================
with aba_admin:
  st.subheader("⚙️ Central de Sincronização e Backup")
  st.markdown("Use esta aba para **baixar** ou **enviar** o arquivo de dados caso precise unificar registros de computadores diferentes.")

  df_atual_admin = carregar_ocorrencias()
  st.markdown(f"📊 Total de registros salvos no banco atual: **{len(df_atual_admin)}**")

  if not df_atual_admin.empty:
    csv_dados = df_atual_admin.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Backup de Ocorrências (.csv)",
        data=csv_dados,
        file_name="backup_dados_ocorrencias.csv",
        mime="text/csv",
        key="btn_download_csv_admin"
    )

  st.markdown("---")
  st.markdown("##### 📤 Importar / Restaurar Banco de Dados")
  arquivo_importado = st.file_uploader("Envie um arquivo `dados_ocorrencias.csv` para unificar os registros:", type=["csv"], key="uploader_csv_admin")
  
  if arquivo_importado is not None:
    try:
      df_importado = pd.read_csv(arquivo_importado, dtype=str)
      salvar_ocorrencias(df_importado)
      st.success("✅ Base de dados importada e sincronizada com sucesso! Recarregue a página.")
    except Exception as e:
      st.error(f"Erro ao importar arquivo: {e}")
