from pathlib import Path
import streamlit as st
from streamlit_chat import message
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests
import os
from dotenv import load_dotenv
from time import sleep
import uuid
import sys
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="AI Chatbot 100% Free", layout="wide")
st.write('完全开源免费的AI智能聊天助手 | Absolute Free & Opensouce AI Chatbot')

css_file = "main.css"
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_dotenv()
yourHFtoken = "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"
yourHFtoken = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id = "HuggingFaceH4/starchat-beta"
av_us = '🧑'
av_ass = '🤖'

# Set a default model
if "hf_model" not in st.session_state:
    st.session_state["hf_model"] = "HuggingFaceH4/starchat-beta"

if "file_name" not in st.session_state:
   st.session_state["file_name"] = str(uuid.uuid4()) + ".txt"
    
#file_name = str(uuid.uuid4()) + ".txt"

### INITIALIZING STARCHAT FUNCTION MODEL
def starchat(model, myprompt, your_template):
    from langchain import PromptTemplate, LLMChain
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = yourHFtoken
    llm = HuggingFaceHub(repo_id=repo_id,
                         model_kwargs={"min_length": 100,
                                       "max_new_tokens": 1024, "do_sample": True,
                                       "temperature": 0.1,
                                       "top_k": 50,
                                       "top_p": 0.95, "eos_token_id": 49155})
    template = your_template
    prompt = PromptTemplate(template=template, input_variables=["myprompt"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    add_notes_1 = "Beginning of chat history:\n"
    add_notes_2 = "End of chat history.\n"
    add_notes_3 = "Please consult the above chat history before responding to the user question below.\n"
    add_notes_4 = "User question: "
    myprompt_temp = myprompt
    myprompt = add_notes_1 + "\n" + contexts + "\n" + add_notes_2 + "\n" + add_notes_3 + "\n" + add_notes_4 + "\n" + myprompt
    st.write("---在def starchat(model,myprompt, your_template)内的信息打印输出开始")
    st.write("Current User Query: "+myprompt_temp)
    st.write("Combined User Input as Prompt/也就是整合了聊天记录的更新后输入（包含用户的最新输入）:")
    st.write(myprompt)
    st.write("---在def starchat(model,myprompt, your_template)内的信息打印输出结束")    
    llm_reply = llm_chain.run(myprompt)
    reply = llm_reply.partition('<|end|>')[0]
    return reply

def write_history(text):    
    #st.write("随机生成的文件名称：" + file_name)
    with open(st.session_state["file_name"], 'a+') as f:
        f.write(text)
        f.write('\n')
        f.seek(0)  # 将文件指针移动到文件开头
        contexts = f.read()
        st.write("contexts的内容：" + contexts)
    return contexts

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.write("这里是用户输入的历史信息显示")
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.write("这里是assistant回复的历史信息显示")
            st.markdown(message["content"])

# Accept user input
if myprompt := st.chat_input("Enter your question here."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": myprompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write("---用户的当前输入问题显示开始---")
        st.markdown(myprompt)
        st.write("---用户的当前输入问题显示结束---")
        usertext = f"user: {myprompt}"
        contexts = write_history(usertext)
        # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("AI Thinking..."):
            st.markdown("st.markdown方法显示：assistant的本次/当前回复结果显示位置从这里开始 - 输出开始...")
            message_placeholder = st.empty()
            full_response = ""
            res = starchat(
                st.session_state["hf_model"],
                myprompt, "<|system|>\n<|end|>\n<|user|>\n{myprompt}<|end|>\n<|assistant|>")
            response = res.split(" ")
            for r in response:
                full_response = full_response + r + " "
                message_placeholder.markdown(full_response + "▌")
                sleep(0.1)
            st.markdown("st.markdown方法显示：assistant的本次/当前回复结果显示位置到这里结束 - 输出结束...")
            # message_placeholder.markdown(full_response)
            asstext = f"assistant: {full_response}"
            contexts = write_history(asstext)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
