from fastapi import Request, Response
from tus_datos_prueba.utils.elastic import get_elastic
import asyncio

async def log(request: Request, call_next):
    loop = asyncio.get_running_loop()
    response: Response = await call_next(request)

    try:
        response_length = len(response.body)
    except AttributeError:
        response_length = int(response.headers.get('content-length', 0))
    client_ip = request.client.host

    elastic = await get_elastic()

    loop.create_task(elastic.index(index="http_logs", document={
        "path": request.url.path,
        "method": request.method,
        "client_ip": client_ip,
        "request_headers": dict(request.headers),
        "user_agent": request.headers.get("user-agent"),
        "status_code": response.status_code,
        "response_length": response_length,
        "timestamp": loop.time(),
    }))

    return response


