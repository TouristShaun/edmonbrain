from langchain.agents import Tool
from langchain.agents import AgentType

from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory

from langchain.tools.python.tool import PythonREPLTool

from httpx import ReadTimeout

import logging
import traceback

def activate_agent(question, chat_history, llm_chat):

    logging.info(f"Activating agent {question}, chat history {chat_history}")
    tools = [
        Tool(
            name="python-repl",
            description="useful for when you need to calculate something using programing. Use print() to see the answer.",
            func=PythonREPLTool().run
        )
    ]

    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    max_retries=1
    initial_delay = 5
    import time
    for retry in range(max_retries):
        try:
            agent_chain = initialize_agent(tools, llm=llm_chat, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
            result = agent_chain.run(input=question, chat_history=chat_history)
        except ReadTimeout as err:
            delay = initial_delay * (retry + 1)
            logging.warning(f"Read timeout while asking: {question} - trying again after {delay} seconds. Error: {str(err)}")
            time.sleep(delay)
            try:
                agent_chain = initialize_agent(tools, llm=llm_chat, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
                result = agent_chain.run(input=question, chat_history=chat_history)
            except ReadTimeout:
                if retry == max_retries - 1:
                    raise
        except Exception as err:
            delay = initial_delay * (retry + 1)
            logging.error(f"General error: {traceback.format_exc()}")
            time.sleep(delay)
            try:
                agent_chain = initialize_agent(tools, llm=llm_chat, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
                result = agent_chain.run(input=question, chat_history=chat_history)

            except Exception:
                if retry == max_retries - 1:
                    raise

        raise Exception(f"Max retries exceeded for question: {question}")

    logging.info("Agent answer: {result}")

    return {"answer": result}