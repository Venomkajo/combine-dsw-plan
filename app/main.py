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
                    if len(lesson_time) == 4:
                        lesson_time = "0"+ lesson_time



                date_dictionary[iterating_date].append((lesson_time, str(row)))

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

    html_content = """
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; padding: 20px; }
            .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .date-header { background-color: #0056b3; color: white; padding: 12px; font-weight: bold; border-radius: 4px; margin-top: 25px; }
            table { width: 100%; border-collapse: collapse; margin-top: 5px; }
            td { border-bottom: 1px solid #eee; padding: 12px; font-size: 14px; }
            tr:hover { background-color: #f9f9f9; }
            .time-col { font-weight: bold; color: #333; width: 100px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mój Połączony Harmonogram</h1>
    """

    for date in sorted(combined_plan.keys()):
        html_content += f"<div class='date-header'>{date}</div>"
        html_content += "<table>"
        
        sorted_entries = sorted(combined_plan[date], key=lambda x: x[0])
        
        for _, row_html in sorted_entries:
            html_content += row_html
            
        html_content += "</table>"

    html_content += "</div></body></html>"
    return html_content