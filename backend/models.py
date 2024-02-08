from pydantic import BaseModel


class CrawlRequest(BaseModel):
    start_url: str
