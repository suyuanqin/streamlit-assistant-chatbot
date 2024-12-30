from weatherapicall import get_current_temperature
from sendemail import send_email
import datetime as dt
from datetime import datetime
import streamlit as st
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
import time

# load_dotenv()


#init available_tools
if 'available_tools' not in st.session_state:
    st.session_state['available_tools'] = {}
st.session_state['available_tools'] = {
    'get_current_temperature':get_current_temperature,
    'send_email':send_email
}
#init api key
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = None

st.session_state['api_key'] = st.text_input("Enter API Key", key="api_key_input", value=st.session_state['api_key'])
client = OpenAI(api_key=st.session_state['api_key'])
# 1. 正确加载 JSON 文件
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_description_path = os.path.join(current_dir, 'tools_description.json')
with open(tools_description_path, 'r') as f:
    tools_description = json.load(f)
tool_lists = ['get_current_temperature','send_email']
tool_selected = st.multiselect("Select Tools", tool_lists,key="tool_list_selected")
#init tool_selected
if 'tool_selected' not in st.session_state:
    st.session_state['tool_selected'] = []

# 2. 每次选择更新时，直接用新的选择替换旧的
st.session_state['tool_selected'] = [
    tools_description['tool_description'][tool] 
    for tool in tool_selected
]
# ##移除了 for 循环追加的方式
# 直接用列表推导式创建新的工具列表
# 这样每次选择变化时，都会完全替换 tool_selected 的内容，而不是追加
# 这样就不会出现重复添加的问题了。每次用户改变选择时，tool_selected 都会准确反映当前选中的工具。
#初始化assistant
if 'assistant' not in st.session_state:
    st.session_state['assistant'] = None
# st.write(st.session_state['tool_selected'])
if st.button("Create Assistant",key="create_assistant"):
    assistant = client.beta.assistants.create(
        name="My Assistant",
        instructions="You are a helpful assistant.",
        model="gpt-4",
        tools=st.session_state['tool_selected']
    )
    st.session_state['assistant'] = assistant

#初始化messages
if "messages" not in st.session_state:
    st.session_state.messages = []
#初始化thread
# 如果没有现有的 thread_id，则创建新的线程
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id

# 显示聊天界面标题
st.title("Chat with AI Assistant")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
def get_name_arguments_from_run(run):
    function_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
    arguments = run.required_action.submit_tool_outputs.tool_calls[0].function.arguments
    function_id = run.required_action.submit_tool_outputs.tool_calls[0].id
    return function_name,arguments,function_id

def get_function_response(function_name,arguments):
    if function_name in st.session_state['available_tools']:
        function=st.session_state['available_tools'][function_name]
        arguments=json.loads(arguments)
        if 'specific_time' in arguments:
            dt_obj =  datetime.fromisoformat(arguments['specific_time'].replace('Z', '+00:00'))
            dt_str= dt_obj.strftime('%Y-%m-%d %H:%M:%S%z')
            dt_dt=dt.datetime.fromisoformat(dt_str)
            arguments['specific_time']=dt_dt
        results = function(**arguments)
         # 如果结果是 DataFrame，转换为字符串或字典
        if isinstance(results, pd.DataFrame):
            results = results.to_json(orient='records')
            
        # 确保结果是 JSON 可序列化的
        return json.dumps(results)
    else:
        results = f"Error: function {function_name} does not exist"
    return results
    
# 用户输入处理
#模型目前只能依次调用函数，并根据上下文决定调用顺序(2024-12-27,gpt3.5的回答)
if prompt := st.chat_input("How do you like the weather today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # thread = client.beta.threads.create()
    #这里每输入一次prompt，thread_id会不会变啊？如果会变的话，thread就没有意义了呀
    #是的，所以也有init thread
    message = client.beta.threads.messages.create(
        thread_id=st.session_state['thread_id'],
        role="user",
        content=prompt
    )
    #第一次发送要求给assistant
    run=client.beta.threads.runs.create(
        thread_id=st.session_state['thread_id'],
        assistant_id=st.session_state['assistant'].id,
    )
    st.write("第一次发送要求给assistant",run.status)
    #等待assistant处理
    
    # 通用的处理循环
    while True:
    # 等待 Assistant 的运行状态更新
        while run.status in ['queued', 'in_progress']:
            time.sleep(0.1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state['thread_id'],
                run_id=run.id,
            )
            st.write(run.status)

        # 如果需要函数调用，提交函数输出
        if run.status == 'requires_action':
            # 处理所有需要的函数调用
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                print(tool_call)
                function_name = tool_call.function.name
                arguments = tool_call.function.arguments
                function_id = tool_call.id

                # 执行函数并获取返回值
                function_response = get_function_response(function_name, arguments)
                st.write(f"Function: {function_name}, Arguments: {arguments}, Response: {function_response}")

                # 提交工具输出
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=st.session_state['thread_id'],
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": function_id,
                        "output": function_response,
                    }]
                )
                st.write(run.status)

        # 如果运行完成，获取最终的回复
        if run.status == 'completed':
            assistant_response = client.beta.threads.messages.list(
                thread_id=st.session_state['thread_id']
            )
            break

        # 如果运行进入未知状态，则终止循环
        if run.status not in ['requires_action', 'queued', 'in_progress']:
            st.write(f"Unexpected status: {run.status}")
            break

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
           
        # st.write(assistant_response.model_dump())
    # 流式显示回复
        if assistant_response.data:
            latest_message=assistant_response.data[0]
            text=latest_message.content[0].text.value
            full_response = ""
            for char in text:
                if char is not None:
                    full_response += char
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    
        # 添加助手回复到历史
            st.session_state.messages.append({"role": "assistant", "content": full_response})

##小结：问题：如果一个run没有跑完并且遇到问题，再在对话框输入请求就会报错说无法在一个active的run里面添加新的message