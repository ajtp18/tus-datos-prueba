from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from tus_datos_prueba.utils.elastic import get_elastic
from datetime import datetime
import uuid
import traceback

async def assertion_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=412,
        content={
            "deatil": f"Failed precondition: {str(exc)}"
        },
    )

async def on_error(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(exc.status_code, {"detail": exc.detail})

    error_id = str(uuid.uuid4())
    
    error_details = {
        "error_id": error_id,
        "timestamp": datetime.utcnow().isoformat(),
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "traceback": traceback.format_exc(),
        
        "request": {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_host": request.client.host,
            "client_port": request.client.port,
        },
        
        "server_info": {
            "server_time": datetime.utcnow().isoformat(),
        }
    }
    
    try:
        error_details["request"]["body"] = await request.body()
    except Exception:
        pass
    
    error_details["request"]["query_params"] = dict(request.query_params)
    
    elastic = await get_elastic()
    try:
        elastic.index(
            index="http_errors",
            body=error_details,
            id=error_id
        )
    except Exception as es_exc:
        print(f"Failed to log error to Elasticsearch: {es_exc}")
        print(f"Original error details: {error_details}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error_id": error_id,
            "message": "An unexpected error occurred",
            "detail": "Please contact support with the error ID"
        }
    )
