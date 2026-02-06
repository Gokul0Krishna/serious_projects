from langchain_core.messages import HumanMessage,SystemMessage
from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

class Llm_services():
    def __init__(self):
        load_dotenv()
        llm_key = os.getenv('llm_key')
        self.model=ChatOpenAI(model="openai/gpt-oss-20b:free",
                        api_key=llm_key,
                        base_url="https://openrouter.ai/api/v1")
        self.cache = {}

    
    def _generate(self,prompt:str,system_prompt):
        cache_key = hash(prompt + (system_prompt or ""))
        if cache_key in self.cache:
            return self.cache[cache_key]
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.model.invoke(messages)
        result = response.content

        self.cache[cache_key] = result
        return result
    
    def review_code(self, code: str, language: str):
        system_prompt = SystemMessage(content="You are an expert code reviewer. Always respond with valid JSON.")
        
        prompt = HumanMessage(content=f"""Review this {language} code for issues:
                ```{language}
                {code}
                ```
                Return JSON array of issues:
                {{
                "issues": [
                    {{
                    "type": "bug|security|performance|style",
                    "severity": "high|medium|low",
                    "line": line_number,
                    "description": "what's wrong",
                    "suggestion": "how to fix"
                    }}
                ]
                }}""") 
          
        response = self._generate(prompt, system_prompt)

        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except:
            return {"issues": [], "error": "Failed to parse response"}
        

if __name__ == '__main__':
    obj = Llm_services()
    code = """
            def divide(a, b):
                return a / b
            """
    result = obj.review_code(code, "python")
    print(result)