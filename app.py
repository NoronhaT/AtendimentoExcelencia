import os
import re
import mimetypes
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


# Cache para configurar e retornar o Vector Store
@st.cache_resource
def setup_vector_store_and_files():
    # Implemente a lógica da função de setup como no seu código original
    pass

# Cache para criar uma nova thread
@st.cache_resource
def create_thread():
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Você usa de boa eduação para entender a necessidade do cliente quanto a serviços de detetização."
                           "Sempre consulte sua base de conhecimento interna para responder as perguntas. Seja educado, breve e direto."
                           "Não entre em qualquer outro assunto fora desse escopo mesmo que o usuário peça."
            }
        ]
    )
    return thread

# Classe para manipular eventos do assistente
class EventHandler(AssistantEventHandler):


    def on_message_done(self, message) -> None:
        # Extrai apenas o texto das respostas do assistente
        for content in message.content:
            if content.type == 'text':
                # Exibe apenas o valor do texto, omitindo outras informações
                st.write(content.text.value.strip())


# Inicialização da página
st.set_page_config(page_title="Atendente Excelência Saneamento", layout="centered")

# Estilo CSS personalizado para fundo branco, caixa de texto e botão
st.markdown(
    """
    <style>
        /* Fundo branco da aplicação */
        .stApp {
            background-color: white;
            color: black; /* Certifique-se de que o texto fique legível */
        }
        /* Estilização da caixa de texto */
        input[type="text"] {
            background-color: white;
            color: black;
            border: 1px solid #ccc;
            padding: 8px;
            border-radius: 5px;
        }
        /* Estilização do botão */
        button {
            background-color: white !important; /* Fundo branco */
            color: black !important; /* Texto preto */
            border: 1px solid #ccc;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #f0f0f0 !important; /* Fundo levemente cinza ao passar o mouse */
            color: black !important; /* Texto permanece preto */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibição do logo
st.image("Logo.jpg", width=200)  # Substitua "Logo.jpg" pelo caminho do logo do cliente

st.title("Atendente Excelência Saneamento - Versão de Testes")
st.markdown(
    """
    Bem-vindo ao Atendente Excelência Saneamento!  
    Este sistema foi projetado para atender suas dúvidas e necessidades relacionadas a serviços de saneamento e detetização.
    PARA INICIAR COMECE COM ALGO COMO: OLÁ PODE ME AJUDAR?
    O AGENTE GUARDA A CONVERSA DURANTE TODA A SESSÃO, GERANDO CONTEXTO PARA AS PRÓXIMAS PERGUNTAS ATÉ QUE VOCÊ FECHE A JANELA.
    """
)

st.divider()

assistant = get_or_create_assistant()
vector_store = setup_vector_store_and_files()
thread = create_thread()

# Interface com o usuário
st.header("Converse com o assistente")
user_input = st.text_input("Digite sua pergunta:", "")

if st.button("Enviar"):
    if user_input:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                event_handler=EventHandler()
        ) as stream:
            stream.until_done()

# Rodapé
st.divider()
st.caption("© 2024 - Desenvolvido por 3LACKD SERVIÇOS DE TECNOLOGIA LTDA.")
