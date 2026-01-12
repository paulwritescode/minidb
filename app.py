from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from minidb import MiniDB
import uvicorn
import webbrowser
import threading
import time
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize database
db = MiniDB(persist_file="app_db.json")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Get list of tables
    tables = list(db.tables.keys())
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "tables": tables
    })

@app.post("/execute-sql", response_class=HTMLResponse)
async def execute_sql(request: Request, sql: str = Form(...)):
    try:
        result = db.execute(sql.strip())
        
        # Format result for template response
        if isinstance(result, list):
            return templates.TemplateResponse("sql_result.html", {
                "request": request,
                "success": True,
                "result": result,
                "message": f"Query executed successfully. {len(result)} row(s) returned.",
                "type": "select"
            })
        else:
            return templates.TemplateResponse("sql_result.html", {
                "request": request,
                "success": True,
                "result": [],
                "message": str(result),
                "type": "command"
            })
    except Exception as e:
        return templates.TemplateResponse("sql_result.html", {
            "request": request,
            "success": False,
            "result": [],
            "message": f"Error: {str(e)}",
            "type": "error"
        })

@app.get("/tables", response_class=HTMLResponse)
async def get_tables(request: Request):
    try:
        tables_info = {}
        for table_name, table_data in db.tables.items():
            tables_info[table_name] = {
                "columns": table_data["columns"],
                "row_count": len(table_data["data"]),
                "indexes": list(table_data["indexes"].keys())
            }
        return templates.TemplateResponse("tables_list.html", {
            "request": request,
            "success": True, 
            "tables": tables_info
        })
    except Exception as e:
        return templates.TemplateResponse("tables_list.html", {
            "request": request,
            "success": False, 
            "error": str(e)
        })

@app.get("/table/{table_name}", response_class=JSONResponse)
async def get_table_data(table_name: str):
    try:
        if table_name not in db.tables:
            return {"success": False, "error": f"Table {table_name} not found"}
        
        data = db.execute(f"SELECT * FROM {table_name}")
        table_info = db.tables[table_name]
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": table_info["columns"],
            "data": data,
            "indexes": list(table_info["indexes"].keys())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_browser():
    """Open browser after a short delay to ensure server is running"""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8001/")

if __name__ == "__main__":
    port = 8001  # Changed port to avoid conflicts
    print(f"Starting server on http://127.0.0.1:{port}/")
    print("Opening browser...")
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    uvicorn.run(app, host="127.0.0.1", port=port)