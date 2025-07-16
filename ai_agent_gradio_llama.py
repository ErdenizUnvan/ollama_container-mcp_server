import asyncio
import gradio as gr
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from ollama import Client
from enum import Enum
from pydantic import BaseModel
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
import os
import ast

### === MODEL AYARLARI === ###

class Category(str, Enum):
    get_weather_temperature = 'The weather temperature of a city'
    capitalize_each_word = 'Capitalize each word'
    count_each_word = 'Count each word'
    other = 'Other'

class ResultModel(BaseModel):
    result: Category

system_prompt = (
    "You are a function-calling AI agent.\n"
    "The function you need to call will be selected according to the user's input for you and it will be informed to you\n"
    "Only provide the outcome of the function, do not make any additional comments or statements\n"
)

chat_model = ChatOllama(
    model="llama3.2",
    base_url="http://192.168.218.156:11434"
).with_config({
    "system_prompt": system_prompt
})

### === AGENT WORKFLOW === ###
async def agent_pipeline(user_input):
    categories = [c.value for c in Category]
    prompt = f"""
You are an intent classifier.
Your job is to return one of the following categories based on the user input.

Categories: {categories}

Respond only in this JSON format:
{{"result": "<one of the categories>"}}

User input: "{user_input}"
"""

    try:
        client = Client(host='http://192.168.218.156:11434')
        int_response = client.chat(
            model='llama3.2',
            messages=[{"role": "user", "content": prompt}]
        )
        raw_data = int_response['message']['content']

        # Uygun şekilde literal eval ile dict'e çevir
        dict_data = ast.literal_eval(raw_data)
        top_label = dict_data.get('result', '').strip()

    except Exception as e:
        return f"Intent classification error: {e}"

    if not top_label:
        return "Invalid response: missing result field"

    # Out of scope kontrolü
    if top_label.lower() == Category.other.value.lower():
        return "Out of scope as function!"

    # Fonksiyon eşlemesi
    label_map = {
        Category.count_each_word.value: 'count_words',
        Category.capitalize_each_word.value: 'capitalize_words',
        Category.get_weather_temperature.value: 'get_weather_temperature'
    }
    top_label_internal = label_map.get(top_label)

    if not top_label_internal:
        return f"Invalid category returned: {top_label}"

    try:
        server_params = StdioServerParameters(command="python", args=["test_tools_mcp_server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                selected_tools = [tool for tool in tools if tool.name == top_label_internal]
                if not selected_tools:
                    return f"No tool matched for: {top_label_internal}"

                agent = create_react_agent(chat_model, selected_tools)
                msg = {"messages": user_input}
                response = await agent.ainvoke(msg)

                for m in response["messages"]:
                    if m.type == "tool":
                        return m.content
                return "No function output returned."

    except Exception as e:
        return f"Agent error: {e}"

### === GRADIO ARAYÜZÜ === ###
with gr.Blocks(title="LDAP + AI Agent Chat") as demo:
    with gr.Column():
        gr.Markdown("## MCP AI Agent")
        user_query = gr.Textbox(label="Your Query")
        agent_response = gr.Textbox(label="Agent Output")
        query_btn = gr.Button("Run MCP Agent")

    async def handle_query_wrapper(query):
        return await agent_pipeline(query)

    query_btn.click(
        fn=handle_query_wrapper,
        inputs=[user_query],
        outputs=agent_response
    )

demo.launch()
