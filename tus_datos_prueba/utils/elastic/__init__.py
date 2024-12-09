from typing import Annotated
from fastapi import Depends
from elasticsearch import AsyncElasticsearch as ElasticClient
from tus_datos_prueba.config import ELASTIC_HOSTS


async def get_elastic() -> ElasticClient:
    return ElasticClient(hosts=ELASTIC_HOSTS)


Elastic = Annotated[ElasticClient, Depends(get_elastic)]