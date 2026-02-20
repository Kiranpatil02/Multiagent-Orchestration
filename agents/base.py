from services.retry import retries
from services.validatiors import validate_schema
import json

class Base:
    
    def __init__(self,schema:dict):
        self.schema=schema


    @retries
    def execute(self, system_prompt:str,user_prompt:str):
        
        response=([
           { "role":"system","content":system_prompt},
           {"role":"user","content":user_prompt}
        ])

        parsed_content=json.loads(response)

        validate_schema(parsed_content,self.schema)

        return parsed_content