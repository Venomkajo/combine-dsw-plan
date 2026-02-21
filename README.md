# 📅 Combine DSW Plan

A FastAPI-based web utility designed to scrape, compare, and merge university schedules from the DSW portal for this particular semester. This tool allows students to view two different group schedules in a single, color-coded timeline to identify overlaps and gaps.

**Live Demo:** [https://combine-dsw-plan.onrender.com/](https://combine-dsw-plan.onrender.com/) *(Subject to availability)*

---

## ✨ Features

* **Dual-Plan Merging:** Compare two different study tracks or group schedules side-by-side.
* **Smart Parsing:** Extracts and cleans HTML table data from the DSW schedule system, stripping unnecessary scripts and styles while maintaining readability.
* **Custom Date Ranges:** Users can specify start and end dates via a simple web interface. Maximum of around one week, due to scraping limitations.
* **Color-Coded UI:** Distinct CSS classes differentiate between Plan A, Plan B, and overlapping sessions.

---

## 🛠️ Tech Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Asynchronous HTTP:** [httpx](https://www.python-httpx.org/)
* **Web Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
* **Templating:** [Jinja2](https://jinja.palletsprojects.com/)
* **Styling:** CSS3 & HTML5

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9 or higher
* pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/venomkajo/combine-dsw-plan
cd combine-dsw-plan
```


2. **Create and activate a virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```



### Running the Application

Start the local development server:

```bash
uvicorn main:app --reload

```

The application will be available at `http://127.0.0.1:8000`.

---

## ⚙️ How it Works

The application performs the following steps:

1. **Cookie Generation:** It formats a specific `RadioList_TerminGr` cookie required by the DSW server to filter results by date.
2. **Concurrent Fetching:** It triggers two simultaneous requests to the DSW schedule links using `asyncio.gather`.
3. **Data Extraction:** BeautifulSoup parses the returned HTML, specifically targeting rows with the ID `gridViewPlanyGrup_DX`.
4. **Set Logic Comparison:**
* **Intersection:** Sessions appearing in both plans (Overlap).
* **Difference:** Sessions unique to Plan 1 or Plan 2.
5. **Rendering:** The sorted, merged data is injected into a template with CSS classes (`plan-1`, `plan-2`, `plan-3`) for visual differentiation.

---
