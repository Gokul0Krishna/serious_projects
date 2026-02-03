from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, List, Any, Optional
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm_key = os.getenv('llm_key')

class GraphState(TypedDict):
    q:str
    customerid : str
    conv : Dict[str, Any]

