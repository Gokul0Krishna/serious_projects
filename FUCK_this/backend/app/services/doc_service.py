from typing import Dict

class Doc_service():
    def __init__(self,llm_service):
        self.llm = llm_service

    def generate_docstring(self, function_code: str, style: str = "google"):
        prompt = f"""Generate a {style}-style docstring for this function:
            ```python
            {function_code}
            ```
            Requirements:
            - Brief description (one line)
            - Args with types
            - Returns with type
            - Example usage

            Format as Python docstring (triple quotes)."""
            
        docstring = self.llm._generate(prompt)
           
        docstring = docstring.strip()
        if '```' in docstring:
            # Extract content between ```
            start = docstring.find('"""')
            end = docstring.rfind('"""') + 3
            docstring = docstring[start:end]
        
        return docstring
    
    def generate_readme(self, project_structure: Dict):
        pass