# main.py (FastAPI backend)
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel
import csv
import os

app = FastAPI()

class Sector(BaseModel):
    sector: str
    percent: float

# Load CSV data into dictionary { year: [ {sector, percent}, ... ] }
def load_budget_data(filepath: str) -> Dict[str, List[Dict[str, float]]]:
    budget = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found.")

    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            year = row['year'].strip()
            sector = row['sector'].strip()
            try:
                percent = float(row['percent'])
            except ValueError:
                continue  # Skip invalid rows

            if year not in budget:
                budget[year] = []
            budget[year].append({"sector": sector, "percent": percent})
    return budget

# Load on startup
budget_data = load_budget_data("budget_data.csv")

@app.get("/api/budget/{year}", response_model=List[Sector])
def get_budget(year: str):
    year = year.strip()
    if year in budget_data:
        return budget_data[year]
    raise HTTPException(status_code=404, detail="Data for this year not found.")

@app.get("/api/years", response_model=List[str])
def get_available_years():
    return sorted(budget_data.keys())
