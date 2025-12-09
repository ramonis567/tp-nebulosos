import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
from legacy.controle_ar_condicionado import calcular_ar_condicionado


def gerar_explicacao_gemini_com_contexto(temp_val, umid_val, velocidade, pergunta_usuario):
    """
    Gera uma resposta usando Google Gemini AI sobre o sistema fuzzy ou qualquer pergunta do usuário.
    
    Args:
        temp_val (float): Valor da temperatura
        umid_val (float): Valor da umidade
        velocidade (float): Velocidade calculada do ventilador
        pergunta_usuario (str): Pergunta feita pelo usuário
    
    Returns:
        str: Resposta gerada pela IA
    """
    try:
        # Configurar a API do Gemini
        genai.configure(api_key=st.secrets['GEMINI_API_KEY'])
        
        # Instanciar o modelo
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Criar o prompt para a IA
        prompt = f"""
        Você é um professor de Lógica Fuzzy especializado em sistemas de controle, mas também é amigável e educado.
        
        CONTEXTO DO SISTEMA ATUAL:
        - Temperatura: {temp_val}°C
        - Umidade: {umid_val}%
        - Velocidade do Ventilador: {velocidade:.2f}%
        
        REGRAS DO SISTEMA FUZZY:
        1. Temperatura Baixa (0-20°C) → Ventilador Desligado (0-30%)
        2. Temperatura Média (15-35°C) → Ventilador Baixo (20-80%)
        3. Temperatura Alta (30-40°C) + Umidade Alta (60-100%) → Ventilador Alto (70-100%)
        4. Temperatura Alta + Umidade Ideal (30-70%) → Ventilador Alto
        5. Temperatura Alta + Umidade Seca (0-40%) → Ventilador Baixo
        
        PERGUNTA DO USUÁRIO:
        {pergunta_usuario}
        
        INSTRUÇÕES:
        - Se a pergunta for sobre o sistema de climatização fuzzy atual, explique usando os dados acima
        - Se a pergunta for sobre Lógica Fuzzy em geral, explique os conceitos de forma educativa
        - Se a pergunta for sobre outro assunto, responda de forma educada e prestativa
        - Sempre use emojis e formatação markdown para tornar a resposta mais clara e amigável
        - Seja conversacional e amigável, não apenas técnico
        - Mantenha respostas concisas (máximo 250 palavras)
        
        Responda de forma natural e prestativa, independente do tipo de pergunta.
        """
        
        # Gerar resposta
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Fallback para uma explicação básica se a API falhar
        explicacao = f"⚠️ **Não foi possível conectar com a IA. Aqui está uma explicação básica:**\n\n"
        explicacao += f"📊 **Dados de Entrada:**\n"
        explicacao += f"- 🌡️ Temperatura: {temp_val}°C\n"
        explicacao += f"- 💧 Umidade: {umid_val}%\n\n"
        explicacao += f"⚙️ **Decisão do Sistema:**\n"
        explicacao += f"- 🌀 Velocidade do Ventilador: {velocidade:.2f}%\n\n"
        
        if velocidade <= 30:
            explicacao += "O sistema determinou que não é necessário refrigeração devido à temperatura baixa."
        elif velocidade <= 70:
            explicacao += "O sistema ativou ventilação moderada devido à temperatura média."
        else:
            explicacao += "O sistema ativou ventilação máxima devido à alta temperatura e/ou umidade elevada."
        
        explicacao += f"\n\n_Erro: {str(e)}_"
        return explicacao


def plotar_funcoes_pertinencia(temperatura, umidade, velocidade_fan, temp_val, umid_val):
    """
    Plota as funções de pertinência das variáveis de entrada.
    
    Args:
        temperatura: Variável fuzzy de temperatura
        umidade: Variável fuzzy de umidade
        velocidade_fan: Variável fuzzy de velocidade
        temp_val: Valor atual da temperatura
        umid_val: Valor atual da umidade
    
    Returns:
        matplotlib.figure.Figure: Figura com os gráficos
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    # Plotar temperatura
    axes[0].set_title('Funções de Pertinência - Temperatura', fontweight='bold')
    for label in temperatura.terms:
        axes[0].plot(temperatura.universe, temperatura[label].mf, label=label, linewidth=2)
    axes[0].axvline(x=temp_val, color='red', linestyle='--', linewidth=2, label=f'Valor atual: {temp_val}°C')
    axes[0].set_xlabel('Temperatura (°C)')
    axes[0].set_ylabel('Pertinência')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plotar umidade
    axes[1].set_title('Funções de Pertinência - Umidade', fontweight='bold')
    for label in umidade.terms:
        axes[1].plot(umidade.universe, umidade[label].mf, label=label, linewidth=2)
    axes[1].axvline(x=umid_val, color='red', linestyle='--', linewidth=2, label=f'Valor atual: {umid_val}%')
    axes[1].set_xlabel('Umidade (%)')
    axes[1].set_ylabel('Pertinência')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plotar velocidade do fan
    axes[2].set_title('Funções de Pertinência - Velocidade do Ventilador', fontweight='bold')
    for label in velocidade_fan.terms:
        axes[2].plot(velocidade_fan.universe, velocidade_fan[label].mf, label=label, linewidth=2)
    axes[2].set_xlabel('Velocidade (%)')
    axes[2].set_ylabel('Pertinência')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def main():
    """
    Função principal da aplicação Streamlit.
    """
    # Configuração da página
    st.set_page_config(
        page_title="Sistema Fuzzy - Ar Condicionado",
        page_icon="🤖",
        layout="wide"
    )
    
    # Título principal
    st.title("🤖 Sistema de Climatização Fuzzy Inteligente")
    
    # Barra lateral com controles
    st.sidebar.header("⚙️ Configurações")
    st.sidebar.markdown("Ajuste os parâmetros do ambiente:")
    
    temp_val = st.sidebar.slider(
        "🌡️ Temperatura (°C)",
        min_value=0,
        max_value=40,
        value=25,
        step=1,
        help="Temperatura atual do ambiente"
    )
    
    umid_val = st.sidebar.slider(
        "💧 Umidade (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=1,
        help="Umidade relativa do ar"
    )
    
    # Calcular resultado
    velocidade, simulacao, temperatura, umidade, velocidade_fan = calcular_ar_condicionado(temp_val, umid_val)
    
    # Criar abas
    tab1, tab2 = st.tabs(["📊 Painel de Controle", "🤖 Tutor IA"])
    
    # Aba 1 - Painel de Controle
    with tab1:
        st.header("Painel de Controle")
        
        # Exibir resultado em métrica
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🌡️ Temperatura",
                value=f"{temp_val}°C",
                delta=f"{temp_val - 25}°C" if temp_val != 25 else "Normal"
            )
        
        with col2:
            st.metric(
                label="💧 Umidade",
                value=f"{umid_val}%",
                delta=f"{umid_val - 50}%" if umid_val != 50 else "Ideal"
            )
        
        with col3:
            # Determinar status do ventilador
            if velocidade <= 30:
                status = "🔴 DESLIGADO"
                delta_color = "normal"
            elif velocidade <= 70:
                status = "🟡 BAIXO"
                delta_color = "off"
            else:
                status = "🟢 ALTO"
                delta_color = "off"
            
            st.metric(
                label="🌀 Velocidade do Ventilador",
                value=f"{velocidade:.2f}%",
                delta=status
            )
        
        st.divider()
        
        # Exibir gráficos
        st.subheader("📈 Funções de Pertinência")
        fig = plotar_funcoes_pertinencia(temperatura, umidade, velocidade_fan, temp_val, umid_val)
        st.pyplot(fig)
        plt.close()
    
    # Aba 2 - Tutor IA (Chatbot)
    with tab2:
        st.header("🤖 Tutor IA - Assistente Virtual")
        st.markdown("Faça perguntas sobre o sistema de climatização fuzzy!")
        
        # Inicializar histórico do chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Exibir histórico do chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input do usuário
        if user_prompt := st.chat_input("Digite sua pergunta aqui..."):
            # Adicionar mensagem do usuário ao histórico
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            
            # Exibir mensagem do usuário
            with st.chat_message("user"):
                st.markdown(user_prompt)
            
            # Gerar resposta usando Gemini AI (agora passa a pergunta do usuário)
            resposta = gerar_explicacao_gemini_com_contexto(temp_val, umid_val, velocidade, user_prompt)
            
            # Adicionar resposta do assistente ao histórico
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            
            # Exibir resposta do assistente
            with st.chat_message("assistant"):
                st.markdown(resposta)
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
