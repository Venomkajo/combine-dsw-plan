from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

async def get_plan_table(url: str):
    async with httpx.AsyncClient() as client:
        # Use headers to look like a real browser
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Cookie": get_date_cookie()}
        response = await client.get(url, headers=headers)
        
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tr[id*='gridViewPlanyGrup_DX']")

        clean_rows = []
        
        for row in rows:

            for garbage in row.find_all(['script', 'img', 'input']):
                garbage.decompose()

            for tag in row.find_all(True): # True finds all tags
                tag.attrs = {} 

            clean_rows.append(str(row))

        if clean_rows:
            # Wrap the cleaned rows in a standard table structure
            return f"<table class='clean-table'>{''.join(clean_rows)}</table>"

        return str(clean_rows) if clean_rows else "<p>No plan found</p>"
    
def get_date_cookie():
    return "RadioList_TerminGr=2026,2,16%5C2026,2,22%5C1"

@app.get("/", response_class=HTMLResponse)
async def my_combined_plan():
    # 1. Fetch both plans at once
    table1 = await get_plan_table("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20153")
    table2 = await get_plan_table("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18909")

    # 2. Combine the tables into one HTML response
    combined_html = f"<h1>Plan INT</h1>{table1}<h1>Plan CHMURY</h1>{table2}"
    
    return f"<html><body>{combined_html}</body></html>"