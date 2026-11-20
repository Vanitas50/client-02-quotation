"""HansePack Angebotsrechner Web-App (HP-V1) – Factory-Task HP-T7-B-WEBUI."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

# Import helper functions from quotation.py (assumed to exist in the project structure)
# from quotation import load_catalog, calculate_quote, build_export_payload, export_quote_json, QuotationError

app = FastAPI(title="HansePack Angebotsrechner (HP-V1)")

@app.get("/")
async def serve_ui(request: Request):
    """Serves the static HTML UI."""
    try:
        html_path = Path(__file__).resolve().parent / "static" / "index.html"
        if not html_path.exists():
            raise FileNotFoundError("Static file 'static/index.html' not found.")
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=500,
            content={"error": {"reason": "FileNotFound", "message": str(e)}}
        )

@app.get("/api/catalog")
async def get_catalog():
    """Returns the product catalog."""
    try:
        from quotation import load_catalog
        catalog = load_catalog()
        return JSONResponse(
            content={
                "currency": "EUR",
                "rule_version": "HP-V1",
                "products": list(catalog.values())
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": {"reason": "InternalError", "message": str(e)}}
        )

@app.post("/api/quote")
async def calculate_quote(request: Request):
    """Calculates a quote based on provided items."""
    try:
        # Parse raw JSON manually without Pydantic
        body_bytes = await request.body()
        data = json.loads(body_bytes.decode("utf-8"))
        
        if not isinstance(data, dict):
            return JSONResponse(
                status_code=400,
                content={"error": {"reason": "InvalidInput", "message": "Request body must be a JSON object."}}
            )
        
        if "items" not in data:
            return JSONResponse(
                status_code=400,
                content={"error": {"reason": "MissingField", "message": 'Field "items" is required.'}}
            )
        
        rule_version = data.get("rule_version", "HP-V1")
        items = data["items"]
        
        from quotation import calculate_quote, build_export_payload
        quote = calculate_quote(items, rule_version=rule_version)
        export_payload = build_export_payload(quote)
        
        return JSONResponse(content=export_payload)
    
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": {"reason": "InvalidJSON", "message": "Request body is not valid JSON."}}
        )
    except Exception as e:
        # Catch QuotationError or other exceptions
        error_reason = type(e).__name__ if hasattr(type(e), '__name__') else 'Unknown'
        return JSONResponse(
            status_code=400,
            content={"error": {"reason": error_reason, "message": str(e)}}
        )

@app.post("/api/quote/export")
async def export_quote(request: Request):
    """Exports the calculated quote as a JSON file."""
    try:
        # Parse raw JSON manually without Pydantic
        body_bytes = await request.body()
        data = json.loads(body_bytes.decode("utf-8"))
        
        if not isinstance(data, dict):
            return JSONResponse(
                status_code=400,
                content={"error": {"reason": "InvalidInput", "message": "Request body must be a JSON object."}}
            )
        
        if "items" not in data:
            return JSONResponse(
                status_code=400,
                content={"error": {"reason": "MissingField", "message": 'Field "items" is required.'}}
            )
        
        rule_version = data.get("rule_version", "HP-V1")
        items = data["items"]
        
        from quotation import calculate_quote, export_quote_json
        quote = calculate_quote(items, rule_version=rule_version)
        json_content = export_quote_json(quote)
        
        return Response(
            content=json_content,
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="hansepack-angebot-HP-V1.json"'}
        )
    
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": {"reason": "InvalidJSON", "message": "Request body is not valid JSON."}}
        )
    except Exception as e:
        error_reason = type(e).__name__ if hasattr(type(e), '__name__') else 'Unknown'
        return JSONResponse(
            status_code=400,
            content={"error": {"reason": error_reason, "message": str(e)}}
        )