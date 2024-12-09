import os
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from openai import OpenAI, AssistantEventHandler

# Carregar as variáveis de ambiente
load_dotenv(find_dotenv())

# Inicializar o cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Cache para inicializar o assistente
@st.cache_resource
def get_or_create_assistant():
    assistants = list(client.beta.assistants.list())
    assistant_name = "Atendente Excelencia Saneamento"

    for assistant in assistants:
        if assistant.name == assistant_name:
            return assistant


# Cache para criar uma nova thread
@st.cache_resource
def create_thread():
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Você usa de boa educação para entender a necessidade do cliente quanto a serviços de detetização. "
                           "Sempre consulte sua base de conhecimento interna para responder as perguntas. Seja educado, breve e direto. "
                           "Não entre em qualquer outro assunto fora desse escopo mesmo que o usuário peça."
            }
        ]
    )
    return thread


# Classe para manipular eventos do assistente
class EventHandler(AssistantEventHandler):
    def on_message_done(self, message) -> None:
        # Atualiza a resposta no histórico de conversas
        for content in message.content:
            if content.type == 'text':
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": content.text.value.strip()}
                )
        # Rola automaticamente para a barra de texto
        scroll_to_bottom()


# Inicialização da página
st.set_page_config(page_title="Atendente Excelência Saneamento", layout="centered")

# Estilo CSS personalizado para fundo branco
st.markdown(
    """
    <style>
        .stApp {
            background-color: white;
            color: black;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Função para rolar até o final da página
def scroll_to_bottom():
    st.components.v1.html(
        """
        <script>
            var textBox = window.document.getElementById('scroll-to-bottom');
            if (textBox) {
                textBox.scrollIntoView({ behavior: 'smooth' });
            }
        </script>
        """,
        height=0,
    )


# Exibição do logo
st.image("Logo.jpg", width=200)  # Substitua "Logo.jpg" pelo caminho do logo do cliente

st.title("Atendente Excelência Saneamento - Versão de Testes")
st.markdown(
    """
    Bem-vindo ao Atendente Excelência Saneamento!  
    Este sistema foi projetado para atender suas dúvidas e necessidades relacionadas a serviços de saneamento e detetização.  
    **Para começar, digite algo como: Olá, pode me ajudar?**  
    O agente guarda o contexto da conversa durante toda a sessão.
    """
)

st.divider()

# Inicializar assistente e thread
assistant = get_or_create_assistant()
thread = create_thread()

# Inicialize o estado para armazenar o histórico
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # Lista para armazenar perguntas e respostas

# Exibição do histórico de mensagens
st.header("Histórico de Conversa")
for message in st.session_state["chat_history"]:
    if message["role"] == "user":
        st.write(f"**Você:** {message['content']}")
    elif message["role"] == "assistant":
        st.write(f"**Assistente:** {message['content']}")


# Função para enviar mensagens e atualizar o histórico
def enviar_mensagem():
    if st.session_state["user_input"]:  # Verifica se há texto na entrada
        user_message = st.session_state["user_input"]
        # Adiciona a mensagem do usuário ao histórico
        st.session_state["chat_history"].append({"role": "user", "content": user_message})

        # Processa a mensagem com o cliente
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler()
        ) as stream:
            stream.until_done()

        # Limpa o texto do campo de entrada
        st.session_state["user_input"] = ""


# Exibição do histórico e campo de entrada de texto
st.divider()

# Insere o elemento ancorado para rolagem
st.markdown('<div id="scroll-to-bottom"></div>', unsafe_allow_html=True)

# Caixa de texto para entrada de mensagens
st.text_input("Digite sua pergunta:", key="user_input", on_change=enviar_mensagem)

# Rodapé
st.divider()
st.markdown(
    """
    <footer style="text-align: center;">
        <p style="color: black;">
            © 2024 - Desenvolvido por 3LACKD SERVIÇOS DE TECNOLOGIA LTDA. |
            <a href="https://www.linkedin.com/in/tsnoronha/" target="_blank" style="color: black; text-decoration: none;">
                Meu LinkedIn
            </a>
        </p>
    </footer>
    """,
    unsafe_allow_html=True
)
