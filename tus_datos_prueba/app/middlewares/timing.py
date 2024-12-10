from fastapi import Request, Response
import time

async def timing(request: Request, call_next):
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Route-Time"] = str(process_time)
    return response