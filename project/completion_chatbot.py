import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 1. 初始化设置
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_PROJECT_API_KEY"))

# 2. 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 显示聊天界面标题
st.title("Chat with AI Assistant")

# 4. 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 用户输入处理
if prompt := st.chat_input("What's on your mind?"):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 显示助手正在输入的状态
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 调用 API 获取回复
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True
        )
        
        # 流式显示回复
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # 添加助手回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 6. 添加清除聊天按钮
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []