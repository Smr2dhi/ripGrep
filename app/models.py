from pydantic import BaseModel

class SearchKeywords(BaseModel):
    keyword:list[str]