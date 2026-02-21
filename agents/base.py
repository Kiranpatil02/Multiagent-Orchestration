from services.llm import llm
from services.validatiors import validate_schema
import json

class Base:
    
    def __init__(self,schema:dict,system_prompt):
        self.schema=schema
        self.system_prompt=system_prompt

    def run(self,user_prompt:str):
        
        result=llm(self.system_prompt,str(user_prompt))
        # parsed_content=json.loads(response)

        validate_schema(result,self.schema)

        return result