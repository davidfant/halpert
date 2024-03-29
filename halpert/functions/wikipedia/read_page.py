from elasticsearch import AsyncElasticsearch
from halpert.types import Function
from pydantic import BaseModel, Field

class Input(BaseModel):
  link: str

class Output(BaseModel):
  class Page(BaseModel):
    title: str
    content: str = Field(description='Markdown content')
  
  page: Page | None

async def read_page_call(
  input: Input,
  index_name: str = 'wikipedia',
  host: str = 'http://localhost:9200',
) -> Output:
  async with AsyncElasticsearch([host]) as es:
    slug = input.link.replace('/wiki/', '')
    # match document by slug
    response = await es.search(index=index_name, query={
      'match': { 'slug': slug },
    }, size=1)

    if len(response['hits']['hits']) == 0:
      return Output(page=None)
    hit = response['hits']['hits'][0]['_source']
    return Output(page=Output.Page(
      title=hit['title'],
      content=hit['markdown'],
    ))


read_page = Function(
  name='Read Wikipedia Page',
  description='Read a Wikipedia page by a link',
  Input=Input,
  Output=Output,
  call=lambda input: read_page_call(input),
)
