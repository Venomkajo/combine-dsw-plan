from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from bs4 import BeautifulSoup


templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

async def get_plan_data(url: str) -> dict:
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

            for links in row.find_all('a'): # Remove <a> tags but keep their text
                links.unwrap()

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

                row = "".join(str(td) for td in all_tds) # Convert the row to a string of its <td> elements
                date_dictionary[iterating_date].append((lesson_time, row))

        return date_dictionary

def get_date_cookie():
    today = datetime.now()
    week = datetime.now() + timedelta(days=7)
    return f"RadioList_TerminGr={today.year},{today.month},{today.day}%5C{week.year},{week.month},{week.day}%5C1"

@app.get("/", response_class=HTMLResponse)
async def my_combined_plan(request: Request):

    # Fetch data
    plan1 = await get_plan_data("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20153")
    plan2 = await get_plan_data("https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18909")

    # Combine keys (dates)
    all_dates = sorted(set(plan1.keys()) | set(plan2.keys()))
    
    html_content = ""

    for date in all_dates:
        html_content += f"<div class='date-header'>{date}</div><table>"
        
        # Create sets of (time, content) for comparison
        entries1 = plan1.get(date, [])
        entries2 = plan2.get(date, [])
        
        set1 = set(entries1)
        set2 = set(entries2)
        
        # Identify overlaps and unique items
        overlap = set1 & set2
        only_plan1 = set1 - set2
        only_plan2 = set2 - set1
        
        # Combine and sort all by time
        combined_rows = []
        for item in overlap: combined_rows.append((item[0], item[1], "plan-3"))
        for item in only_plan1: combined_rows.append((item[0], item[1], "plan-1"))
        for item in only_plan2: combined_rows.append((item[0], item[1], "plan-2"))
        
        combined_rows.sort(key=lambda x: x[0]) # Sort by time

        for time, content, css_class in combined_rows:
            html_content += f"<tr class='{css_class}'>{content}</tr>"
            
        html_content += "</table>"

    return templates.TemplateResponse("index.html", {"request": request, "content": html_content})