from pydantic import BaseModel

class TicketCreate(BaseModel):
    titulo:str
    descricao:str
    prioridade : str ="normal" 
    
