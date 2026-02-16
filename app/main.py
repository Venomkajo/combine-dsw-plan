from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

async def get_plan_data(url: str):
    async with httpx.AsyncClient() as client:
        # Use headers to look like a real browser
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Cookie": get_date_cookie()}
        response = await client.get(url, headers=headers)
        
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tr[id*='gridViewPlanyGrup_DX']") # Select rows with IDs containing 'gridViewPlanyGrup_DX'

        date_dictionary = defaultdict(list)
        iterating_date = "ERROR"
        
        for row in rows:
            for garbage in row.find_all(['script', 'img', 'input']): # Remove unwanted tags like <script>, <img>, and <input>
                garbage.decompose()

            for tag in row.find_all(True): # True finds all tags, remove them
                tag.attrs = {} 

            row_id = row.get("id", "")
            if "gridViewPlanyGrup_DXGroupRowExp" in row_id:
                # Extract the date from the row's inner text
                date_text = row.get_text(strip=True)
                iterating_date = date_text
            elif "gridViewPlanyGrup_DXDataRow" in row_id:
                all_tds = row.find_all("td")
                if len(all_tds) > 1:
                    lesson_time = all_tds[1].get_text(strip=True)


                date_dictionary[iterating_date].append(str(row))

        return date_dictionary

def get_date_cookie():
    return "RadioList_TerminGr=2026,2,16%5C2026,2,22%5C1"

@app.get("/", response_class=HTMLResponse)
async def my_combined_plan():
    plan1 = await get_plan_data("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20153")
    plan2 = await get_plan_data("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18909")

    combined_plan = defaultdict(list)
    
    for date, courses in plan1.items():
        combined_plan[date].extend(courses)
    
    for date, courses in plan2.items():
        combined_plan[date].extend(courses)

    print(combined_plan)

    html_content = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            .date-header { background-color: #f2f2f2; font-weight: bold; padding: 10px; border: 1px solid #ccc; margin-top: 10px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            td { border: 1px solid #ddd; padding: 8px; }
            tr:nth-child(even) { background-color: #fafafa; }
        </style>
    </head>
    <body>
        <h1>Połączony Plan Zajęć</h1>
    """

    for date in sorted(combined_plan.keys()):
        html_content += f"<div class='date-header'>{date}</div>"
        html_content += "<table>"
        html_content += "".join(combined_plan[date])
        html_content += "</table>"

    html_content += "</body></html>"
    return html_content