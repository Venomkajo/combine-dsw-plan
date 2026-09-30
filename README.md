# Combine DSW Plan

A FastAPI-based web utility designed to scrape, compare, and merge university schedules from the DSW/Ideis websites. This tool allows students to view two different group schedules in a single, color-coded timeline to identify overlaps and gaps.

**Live Demo:** [https://combine-dsw-plan.vercel.app/](https://combine-dsw-plan.vercel.app/) *(Subject to availability)*

---

## Features

* **Dual-Plan Merging:** Compare two different study tracks or group schedules side-by-side.
* **Custom Date Ranges:** Users can specify start and end dates via a simple web interface. Maximum of around one week, due to scraping limitations.
* **Color-Coded UI:** Distinct CSS classes differentiate between Plan A, Plan B, and overlapping sessions.

**Default plans are for INT-MWF 2026/2027 and IAiSC 2026/2027. Custom DSW/Ideis schedules can be selected.**

---

## Tech Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Asynchronous HTTP:** [httpx](https://www.python-httpx.org/)
* **Web Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
* **Templating:** [Jinja2](https://jinja.palletsprojects.com/)
* **Styling:** CSS3 & HTML5

---

## Getting Started

### Prerequisites

* Python
* pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/venomkajo/combine-dsw-plan
cd combine-dsw-plan
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the Application

Start the local development server:

```bash
uvicorn main:app --reload
```

or

```bash
fastapi main:app --reload
```

The application will be available at `http://127.0.0.1:8000` by default.