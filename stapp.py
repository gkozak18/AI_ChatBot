import streamlit as st
import asyncio
import requests
import json


st.title('AI ChatBot')



async def call_chat_api(user_id, user_input, history):
    url = "http://127.0.0.1:8000/send_message/"  
    payload = {
        "user_id": user_id,
        "user_input": user_input,
        "history": history
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json()}
    except Exception as e:
        return {"error": str(e)}



if 'messages' not in st.session_state:
    st.session_state.messages = []
    # st.session_state.messages.append({"role": "assistant", "content": 'Hi!'})


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Write your message"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
        
    response = asyncio.run(call_chat_api('1498c77f-81f7-43f4-bcf3-2795bc00803b', prompt, st.session_state.messages))
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({'role' : 'assistant', 'content' : response})
