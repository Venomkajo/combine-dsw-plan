from collections import defaultdict
from datetime import date, timedelta
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import asyncio
from bs4 import BeautifulSoup

PLAN_LINKS = {
    "INT-MWF-WykS": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20153", 
    "INT-MWF-1S": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20380", 
    "INT-MWF-2S": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/20381",
    "IAiSC-WykS": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18909",
    "IAiSC-1S": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18910",
    "IAiSC-2S": "https://harmonogramy.dsw.edu.pl/Plany/PlanyGrup/18911"}

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

async def get_plan_data(url: str, start_date: date, end_date: date) -> dict:
    async with httpx.AsyncClient() as client:
        # Use headers to look like a real browser
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Cookie": get_date_cookie(start_date, end_date)}
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
                        lesson_time = "0" + lesson_time

                row = "".join(str(td) for td in all_tds) # Convert the row to a string of its <td> elements
                date_dictionary[iterating_date].append((lesson_time, row))

        return date_dictionary

def get_date_cookie(start_date: date, end_date: date) -> str:
    today = start_date
    week = end_date
    return f"RadioList_TerminGr={today.year},{today.month},{today.day}%5C{week.year},{week.month},{week.day}%5C1"

@app.get("/", response_class=HTMLResponse)
async def my_combined_plan(
    request: Request,
    start_date: Optional[date] = date.today(), 
    end_date: Optional[date] = date.today() + timedelta(days=7), 
    plan1_name: Optional[str] = "INT-MWF-WykS", 
    plan2_name: Optional[str] = "IAiSC-WykS"
):
    # 1. Fetch data
    p1_data, p2_data = await asyncio.gather(
        get_plan_data(PLAN_LINKS[plan1_name], start_date=start_date, end_date=end_date),
        get_plan_data(PLAN_LINKS[plan2_name], start_date=start_date, end_date=end_date)
    )

    # 2. Process Data
    all_dates = sorted(set(p1_data.keys()) | set(p2_data.keys()))
    structured_plan = []

    for d in all_dates:
        entries1 = set(p1_data.get(d, []))
        entries2 = set(p2_data.get(d, []))
        
        day_entries = []
        
        # Identify overlaps and unique items
        for item in (entries1 & entries2):
            day_entries.append({"time": item[0], "content": item[1], "css": "plan-3"})
        for item in (entries1 - entries2):
            day_entries.append({"time": item[0], "content": item[1], "css": "plan-1"})
        for item in (entries2 - entries1):
            day_entries.append({"time": item[0], "content": item[1], "css": "plan-2"})
        
        # Sort day by time
        day_entries.sort(key=lambda x: x["time"])
        
        structured_plan.append({
            "date": d,
            "rows": day_entries
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "plan_data": structured_plan,
        "start_date": start_date,
        "end_date": end_date,
        "plan1_name": plan1_name,
        "plan2_name": plan2_name
    })