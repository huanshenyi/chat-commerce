import os

# Pyhton外部モジュールのインポート
import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
from langchain.chains import LLMChain

# 外部 API 呼び出し関数を定義
import requests

def get_weather(city_name):
    api_key = os.getenv("API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&lang=ja&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"天気情報の取得中にエラーが発生しました: {e}"
    if response.status_code == 200:
        data = response.json()
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        return f"{city_name}の現在の天気は{weather_description}、気温は{temperature}℃です。"
    else:
        return f"{city_name}の天気情報を取得できませんでした。"

# ツールを定義
weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="指定された都市の現在の天気を取得します。"
)

# セッションIDを定義
if "session_id" not in st.session_state:
    st.session_state.session_id = "session_id"

# セッションに会話履歴を定義
if "history" not in st.session_state:
    st.session_state.history = DynamoDBChatMessageHistory(
        table_name="chat_commerce_db", session_id=st.session_state.session_id
    )

# セッションにLangChainの処理チェーンを定義
if "agent_executor" not in st.session_state:
    # プロンプトを定義
    prefix = """あなたは有能なアシスタントです。必要に応じて以下のツールを使うことができます。"""
    suffix = """始めましょう！

    {chat_history}
    質問: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools=[weather_tool],
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"]
    )

    # チャット用LLMを定義
    chat = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"max_tokens": 4000}, streaming=True,
        region_name="ap-northeast-1",
    )

    llm_chain = LLMChain(llm=chat, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=[weather_tool])
    # チェーンを定義
    st.session_state.agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=[weather_tool], verbose=True, handle_parsing_errors=True
    )

# タイトルを画面表示
st.title("Chat Commerceと話そう！")

st.sidebar.title("質問履歴")

# 履歴クリアボタンを画面表示
if st.button("履歴クリア"):
    st.session_state.history.clear()

if st.session_state.history.messages:
    for message in st.session_state.history.messages:
        if message.type == "user":  # ユーザーからのメッセージのみ表示
            st.sidebar.markdown(f"- {message.content}")

# メッセージを画面表示
for message in st.session_state.history.messages:
    with st.chat_message(message.type):
        st.markdown(message.content)

# チャット入力欄を定義
if prompt := st.chat_input("何でも話してね！"):
    # ユーザーの入力をメッセージに追加
    with st.chat_message("user"):
        st.markdown(prompt)

    # モデルの呼び出しと結果の画面表示
    with st.chat_message("assistant"):
        response = st.session_state.agent_executor.run(
            input=prompt,
            chat_history=st.session_state.history.messages,
            config={"configurable": {"session_id": st.session_state.session_id}},
        )
        # レスポンスが文字列かジェネレータかをチェックして適切に処理
        if isinstance(response, str):
            st.markdown(response)
        else:
            st.write_stream(response)

    # 会話を履歴に追加
    st.session_state.history.add_user_message(prompt)
    st.session_state.history.add_ai_message(response)
