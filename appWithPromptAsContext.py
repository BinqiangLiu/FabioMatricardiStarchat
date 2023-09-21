#Memory in prompt.将过往的对话历史文本内容提取出来并追加累积，然后放入myprompt中作为用户输入的问题（还有一些小的处理，增加一些固定的文字说明）
#/home/adminuser/venv/lib/python3.10/site-packages/huggingface_hub/utils/_deprecation.py:127: FutureWarning: '__init__' (from 'huggingface_hub.inference_api')
#is deprecated and will be removed from version '0.19.0'. `InferenceApi` client is deprecated in favor of the more feature-complete `InferenceClient`.
#Check out this guide to learn how to convert your script to use it: https://huggingface.co/docs/huggingface_hub/guides/inference#legacy-inferenceapi-client.
from pathlib import Path
import streamlit as st
from streamlit_chat import message
from huggingface_hub import InferenceClient
from langchain import HuggingFaceHub
import requests# Internal usage
import os
from dotenv import load_dotenv
from time import sleep
#from hugchat import hugchat
#from hugchat.login import Login
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="AI Chatbot 100% Free", layout="wide")
st.write('完全开源免费的AI智能聊天助手 | Absolute Free & Opensouce AI Chatbot')

# --- PATH SETTINGS ---
css_file = "main.css"
# --- LOAD CSS, PDF & PROFIL PIC ---
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

load_dotenv()
yourHFtoken = "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"
yourHFtoken = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id="HuggingFaceH4/starchat-beta"
myprompt_temp=""
myprompt=""
#AVATARS
#av_us = './man.png' #"🦖" #A single emoji, e.g. "🧑 💻", "🤖", "🦖". Shortco
#av_ass = './robot.png'
av_us = '🧑'
av_ass = '🤖'
# Set a default model
if "hf_model" not in st.session_state:
    st.session_state["hf_model"] = "HuggingFaceH4/starchat-beta"

### INITIALIZING STARCHAT FUNCTION MODEL
def starchat(model,myprompt, your_template):
    from langchain import PromptTemplate, LLMChain
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = yourHFtoken
    llm = HuggingFaceHub(repo_id=repo_id,
                         model_kwargs={"min_length":100,
                                       "max_new_tokens":1024, "do_sample":True,
                                       "temperature":0.1,
                                       "top_k":50,
                                       "top_p":0.95, "eos_token_id":49155})
#以下是新增内容
#    my_prompt_template = """You are a very smart and helpful AI assistant. You are provided {contexts} as chat history between the user and you.
#    For any following question, you MUST consider the chat history and response to {myprompt} as the user question. 
#    However, you SHOULD NOT limit your reponse to the chat history.
#    You should take any actions you would take when you response to a user question normally.
#    DO NOT OUTPUT the chat history or the user question or ANY other unrelated information!
#    AI Response:
#    """
#以上是新增内容    
#    template = my_prompt_template
    template = your_template
#    prompt = PromptTemplate(template=template, input_variables=["contexts", "myprompt"])
    prompt = PromptTemplate(template=template, input_variables=["myprompt"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    add_notes_1="Beginning of chat history:\n"
    add_notes_2="End of chat history.\n"
    add_notes_3="Please consult the above chat history before responding to the user question below.\n"
    add_notes_4="User question: "
    myprompt_temp=myprompt
    #myprompt=add_notes_1+contexts+add_notes_2+add_notes_3+myprompt
    myprompt = add_notes_1 + "\n" + contexts + "\n" + add_notes_2 + "\n" + add_notes_3 + "\n"+ add_notes_4 + "\n" + myprompt
#似乎能够运行不出错，但是运行速度很慢？！更重要的是，好像还是不能够将以前的对话历史纳入！
    #st.write("---在def starchat(model,myprompt, your_template)内的信息打印输出开始")
    #st.write("Current User Query: "+myprompt_temp)
    #st.write("---")
    #st.write("Combined User Input as Prompt:")
    #st.write(myprompt)
    #st.write("---在def starchat(model,myprompt, your_template)内的信息打印输出结束")
    llm_reply = llm_chain.run(myprompt)
    #llm_reply = llm_chain.run({'contexts': contexts, 'myprompt': myprompt})    
    reply = llm_reply.partition('<|end|>')[0]
    return reply

# FUNCTION TO LOG ALL CHAT MESSAGES INTO chathistory.txt
#def writehistory(text):
#    with open('chathistory.txt', 'a') as f:
#        f.write(text)
#        f.write('\n')
#增加下面一行代码，读取对话记录text并存储到contexts
#        contexts = f.read()
#    f.close()

def writehistory(text):
    with open('chathistory.txt', 'a+') as f:
        f.write(text)
        f.write('\n')
        f.seek(0)  # 将文件指针移动到文件开头
        contexts = f.read()
    return contexts

### START STREAMLIT UI
#st.title("🤗 HuggingFace Free ChatBot")
#st.subheader("using Starchat-beta")

# Initialize chat history
if "messages" not in st.session_state:
   st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
   if message["role"] == "user":
#      with st.chat_message(message["role"],avatar=av_us):
      with st.chat_message(message["role"]):
           st.write("用户输入问题的显示开始")
           st.markdown(message["content"])
           st.write("用户输入问题的显示结束")
   else:
#       with st.chat_message(message["role"],avatar=av_ass):
       with st.chat_message(message["role"]):
           st.write("assistant回复内容的显示开始")
           st.markdown(message["content"])
           st.write("assistant回复内容的显示结束")

# Accept user input
if myprompt := st.chat_input("Enter your question here."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": myprompt})
    # Display user message in chat message container
#    with st.chat_message("user", avatar=av_us):
    with st.chat_message("user"):
        st.markdown(myprompt)
        usertext = f"user: {myprompt}"
#        writehistory(usertext)
#新增如下一行        
        contexts = writehistory(usertext)
        st.write("st.chat_message的user之contexts: "+contexts)
        # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("AI Thinking..."):
            message_placeholder = st.empty()
            full_response = ""
            st.write("---assistant的回复结果输出开始---")
            res = starchat(
                  st.session_state["hf_model"],
                  myprompt, "<|system|>\n<|end|>\n<|user|>\n{myprompt}<|end|>\n<|assistant|>")
            response = res.split(" ")
            st.write("---assistant的回复结果输出结束---")
            for r in response:
                full_response = full_response + r + " "
                message_placeholder.markdown(full_response + "▌")
                sleep(0.1)            
            st.write("用st.write方法打印输出assistant的回复结果开始")
            st.write("assistant的回复结果: "+full_response)
            st.write("用st.write方法打印输出assistant的回复结果结束")
            st.write("---")
            #message_placeholder.markdown(full_response)   这个是不是用来显示assistant的方法？？？
            #st.write("---在with st.chat_message( - assistant - )内的信息打印输出开始")
            #st.write("Current User Query: "+myprompt_temp)
            #st.write("---")
            #st.write("Combined User Input as Prompt:")
            #st.write(myprompt)
            #在这里，变量myprompt_temp、myprompt都会被重置为空置
            #st.write("---在with st.chat_message( - assistant - )内的信息打印输出结束") - 位置不对
            asstext = f"assistant: {full_response}"            
#            writehistory(asstext)
#新增如下一行        
            contexts = writehistory(asstext)
            st.write("st.chat_message的assistant之contexts: "+contexts)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
