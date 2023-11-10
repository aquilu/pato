import openai
from duckduckgo_search import DDGS
import streamlit as st
import os
import time

# Claves de API aquí o en una variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Imagen personalizada para el icono de la app y el avatar del asistente
company_logo = 'https://d1b4gd4m8561gs.cloudfront.net/sites/default/files/favicon.ico'
# Configurando la página de Streamlit
st.set_page_config(
    page_title="Muisca bot de búsqueda asistida virtual",
    page_icon=company_logo
)

# Función para buscar en DuckDuckGo
def buscar_en_duckduckgo(keywords, region="wt-wt", safesearch="off", timelimit=None, max_results=10):
    with DDGS() as ddgs:
        return list(ddgs.text(keywords, region=region, safesearch=safesearch, timelimit=timelimit, max_results=max_results))

# Inicializando el historial del chat
if 'messages' not in st.session_state:
    # Comenzando con el primer mensaje del asistente
    st.session_state['messages'] = [{"role": "assistant", 
                                  "content": "Hola humano! Soy Muisca, la IA que te asiste en términos de búsqueda. ¿Cómo puedo ayudarte hoy?"}]

# Mostrando mensajes del chat desde el historial en cada re-ejecución de la app
# Avatar personalizado para el asistente, avatar predeterminado para el usuario
for message in st.session_state.messages:
    if message["role"] == 'assistant':
        with st.chat_message(message["role"], avatar=company_logo):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Lógica del chat
domain = st.text_input("Por favor, introduce el dominio (por ejemplo: https://www.banrepcultural.org): ")
if query := st.chat_input("Escribe que quieres buscar en el dominio "):  # Texto de la caja del chat
    # Agregar mensaje del usuario al historial del chat
    st.session_state.messages.append({"role": "user", "content": query})

    # Concatenar el dominio y el término de búsqueda para formar el término de búsqueda
    search_term = f"{query} site:{domain}"

    # Usa la función buscar_en_duckduckgo para obtener los resultados
    results = buscar_en_duckduckgo(search_term)

    # Prepara un contexto basado en los resultados para enviar a GPT-3.5 Turbo
    context = "\n".join([f"Title: {result['title']}\nURL: {result['href']}" for result in results])
    question = f"¿Qué puedes decirme sobre los resultados relacionados con '{query}' en el dominio '{domain}'?"

    # Construye el contexto de la conversación
    conversation = [
        "Eres un asistente virtual del Banco de la República, experto en cultura colombiana. Eres muy respetuoso y atento a las preguntas de los usuarios. Debes entregar la URL completa del recurso buscado. Al terminar la búsqueda ofrecer otros servicios como visitar el Museo del Oro y la Red de Bibliotecas del Banco de la República",
        f"Usuario: {context}",
        f"Usuario: {question}"
    ]
    # Convierte la conversación en un prompt de texto
    prompt = "\n".join(conversation)

    # Realiza la llamada a la API de OpenAI con el prompt de conversación
    response_obj = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente virtual del Banco de la República, experto en cultura colombiana. Eres muy respetuoso y atento a las preguntas de los usuarios. Debes entregar la URL completa del recurso buscado. Al terminar la búsqueda ofrecer otros servicios como visitar el Museo del Oro y la Red de Bibliotecas del Banco de la República"},
            {"role": "user", "content": context},
            {"role": "user", "content": question}
        ]
    )
    response = response_obj['choices'][0]['message']['content']
    with st.chat_message("assistant", avatar=company_logo):
        message_placeholder = st.empty()
        full_response = ""

        # Simular flujo de respuesta con milisegundos de retraso
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Agregar un cursor parpadeante para simular la escritura
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Agregar mensaje del asistente al historial del chat
    st.session_state.messages.append({"role": "assistant", "content": response})
