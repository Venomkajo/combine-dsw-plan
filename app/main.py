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
import os

PLAN_LINKS = {
    "INT-MWF-WykS": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/20153", 
    "INT-MWF-1S": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/20380", 
    "INT-MWF-2S": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/20381",
    "IAiSC-WykS": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/18909",
    "IAiSC-1S": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/18910",
    "IAiSC-2S": "https://harmonogramy.ideis.pl/Plany/PlanyGrup/18911"
}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

async def get_plan_data(url: str, start_date: date, end_date: date) -> dict:
    async with httpx.AsyncClient() as client:
        # Use headers to look like a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://harmonogramy.ideis.pl/",
            "Connection": "keep-alive",
            "Cookie": f"{get_date_cookie(start_date, end_date)}; wdlang=pl"
        }
        
        try:
            response = await client.get(url, headers=headers)
        except httpx.HTTPError as e:
            print(f"Error fetching {url}: {e}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        # Match any DevExpress GridView row (both group and teacher pages)
        rows = soup.select("tr[id*='_DX']")

        date_dictionary = defaultdict(list)
        iterating_date = "ERROR"
        
        for row in rows:
            for garbage in row.find_all(['script', 'img', 'input']): # Remove unwanted tags like <script>, <img>, and <input>
                garbage.decompose()

            for button in row.find_all('button'): # Remove <button> tags but keep their content field
                text = button.get("data-bs-content", "")
                button.replace_with(text)

            for links in row.find_all('a'): # Remove <a> tags but keep their text
                links.unwrap()

            for tag in row.find_all(True): # True finds all tags, remove them
                tag.attrs = {} 

            row_id = row.get("id", "")
            if "DXGroupRowExp" in row_id:
                # Extract the date from the row's inner text
                date_text = row.get_text(strip=True)
                iterating_date = date_text
            elif "DXDataRow" in row_id:
                all_tds = row.find_all("td")
                if len(all_tds) > 1:
                    lesson_time = all_tds[1].get_text(strip=True)
                    if len(lesson_time) == 4:
                        lesson_time = "0" + lesson_time
                else:
                    lesson_time = "ERROR"

                row = "".join(str(td) for td in all_tds) # Convert the row to a string of its <td> elements
                date_dictionary[iterating_date].append((lesson_time, row))

        return date_dictionary

def get_date_cookie(start_date: date, end_date: date) -> str:
    date_from = start_date
    date_to = end_date
    return f"RadioList_TerminGr={date_from.year},{date_from.month},{date_from.day}%5C{date_to.year},{date_to.month},{date_to.day}%5C1"

@app.get("/", response_class=HTMLResponse)
async def my_combined_plan(
    request: Request,
    start_date: Optional[date] = date.today(), 
    end_date: Optional[date] = date.today() + timedelta(days=7), 
    plan1: Optional[str] = "INT-MWF-WykS", 
    plan2: Optional[str] = "IAiSC-WykS",
    custom_plan1_name: Optional[str] = "",
    custom_plan2_name: Optional[str] = ""
):

    if plan1 == "custom" and (not custom_plan1_name or not validate_link(custom_plan1_name)) or plan2 == "custom" and (not custom_plan2_name or not validate_link(custom_plan2_name)):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "plan_data": [],
            "start_date": start_date,
            "end_date": end_date,
            "plan1": plan1,
            "plan2": plan2,
            "custom_plan1_name": custom_plan1_name,
            "custom_plan2_name": custom_plan2_name,
            "error_message": "Custom plans selected but no valid links provided. Please enter a valid link for all custom plans. Currently supported custom website: https://harmonogramy.ideis.pl/"
        })

    # 1. Fetch data
    plan1_link = PLAN_LINKS.get(plan1) if plan1 != "custom" else custom_plan1_name
    plan2_link = PLAN_LINKS.get(plan2) if plan2 != "custom" else custom_plan2_name
    p1_data, p2_data = {}, {}

    try:
        p1_data, p2_data = await asyncio.gather(
            get_plan_data(plan1_link, start_date=start_date, end_date=end_date),
            get_plan_data(plan2_link, start_date=start_date, end_date=end_date)
        )
    except Exception as e:
        print(f"Error fetching plan data: {e}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "plan_data": [],
            "start_date": start_date,
            "end_date": end_date,
            "plan1": plan1,
            "plan2": plan2,
            "custom_plan1_name": custom_plan1_name,
            "custom_plan2_name": custom_plan2_name,
            "error_message": "Error fetching plan data. Please try again later."
        })

    # 2. Process Data
    all_dates = sorted(set(p1_data.keys()) | set(p2_data.keys()))
    structured_plan = []

    for d in all_dates:
        entries1 = set(p1_data.get(d, []))
        entries2 = set(p2_data.get(d, []))
        
        day_entries = []
        
        # Identify overlaps and unique items
        for item in (entries1 & entries2):
            day_entries.append({"time": item[0], "content": item[1], "css": f"{get_css_class(item[1], 'plan-3')}"})
        for item in (entries1 - entries2):
            day_entries.append({"time": item[0], "content": item[1], "css": f"{get_css_class(item[1], 'plan-1')}"})
        for item in (entries2 - entries1):
            day_entries.append({"time": item[0], "content": item[1], "css": f"{get_css_class(item[1], 'plan-2')}"})
        
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
        "plan1": plan1,
        "plan2": plan2,
        "custom_plan1_name": custom_plan1_name,
        "custom_plan2_name": custom_plan2_name,
        "error_message": ""
    })

def get_css_class(content: str, original_class: str) -> str:

    BORDER_CLASSES = {
        "Zajęcia odwołane": "canceled-border",
        "Distance learning": "distance-learning-border",
        "Platforma Moodle": "moodle-border",
        "<td>Zaliczenie</td>": "exam-border"
    }

    for key, value in BORDER_CLASSES.items():
        if key in content:
            return f"{original_class} {value}"
        
    return f"{original_class} regular-border"

def validate_link(link: str) -> bool:
    if not type(link) == str:
        return False
    elif not link.startswith("https://harmonogramy.ideis.pl/Plany/"):
        return False
    else:
        return True
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)