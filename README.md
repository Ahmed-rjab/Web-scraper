# 🔍 Phishing Threat Intelligence Scraper

A Python-based automated system for collecting, analyzing, and classifying phishing URLs. Built as an academic project for IT360 - Information Assurance and Security.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-Academic-green.svg)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Team](#team)
- [License](#license)

---

## 📖 Overview

This project implements a **layered pipeline architecture** for phishing threat intelligence. The system:

1. **Collects** phishing URLs from public threat feeds (URLhaus, PhishTank)
2. **Scrapes** target web pages to retrieve HTML content
3. **Parses** HTML to detect phishing indicators
4. **Analyzes** indicators using rule-based scoring
5. **Stores** results in SQLite for historical analysis
6. **Presents** findings via a Flask web dashboard

---

## ✨ Features

- ✅ Automated URL collection from URLhaus and PhishTank
- ✅ HTTP scraping with rate limiting and timeout handling
- ✅ 7 threat detection rules:
  - Hidden iframes (+3 points)
  - External login forms (+3 points)
  - Password fields (+2 points)
  - Suspicious external scripts (+2 points)
  - Urgency keywords (+1 point)
  - No HTTPS links (+1 point)
  - Mismatched brand title (+2 points)
- ✅ Rule-based risk classification (LOW/MEDIUM/HIGH)
- ✅ SQLite database with normalized schema
- ✅ Flask web dashboard with filtering and export
- ✅ Comprehensive unit tests
- ✅ CSV export functionality

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  URL Feed   │────▶│   Scraper    │────▶│    Parser    │
│(url_collector)    │  (scraper)   │     │  (parser)    │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Dashboard  │◀────│  Database   │◀────│   Analyzer  │
│   (app)     │     │ (database)  │     │  (analyzer) │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Pipeline Flow

| Stage | Component | Description |
|-------|-----------|-------------|
| 1 | URL Feed | Fetches URLs from URLhaus/PhishTank |
| 2 | Scraper Engine | HTTP requests with rate limiting |
| 3 | HTML Parser | DOM analysis for threat indicators |
| 4 | Threat Analyzer | Rule-based scoring & classification |
| 5 | SQLite Database | Persistent storage |
| 6 | Flask Dashboard | Web interface |

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Steps

1. **Clone or download** the project

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Option 1: CLI Scanner

Run the scanner from command line:
```bash
python main.py -n 10
```

Options:
- `-n, --max-urls`: Number of URLs to process (default: 10)
- `-f, --file`: Path to local CSV file with URLs
- `--dashboard`: Start web dashboard after scanning

### Option 2: Web Dashboard

Start the Flask web interface:
```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

### Option 3: Run Tests

Execute all unit tests:
```bash
python -m pytest tests/
# or
python tests/run_tests.py
```

---

## 📂 Components

### Core Modules

| File | Description |
|------|-------------|
| `url_collector.py` | URL Feed - Fetches from URLhaus/PhishTank |
| `scraper.py` | Scraper Engine - HTTP fetching with rate limiting |
| `parser.py` | HTML Parser - DOM analysis for threat indicators |
| `analyzer.py` | Threat Analyzer - Rule-based scoring & classification |
| `database.py` | SQLite operations - Persistent storage |
| `app.py` | Flask Dashboard - Web interface |
| `main.py` | Pipeline orchestration - Entry point |

### Supporting Files

| File | Description |
|------|-------------|
| `requirements.txt` | Python dependencies |
| `templates/dashboard.html` | Jinja2 web template |
| `tests/` | Unit test suite |
| `LOG.md` | Project development log |

---

## 🧪 Testing

The project includes comprehensive unit tests covering:

- **URL Collector**: URL validation, feed fetching, file loading
- **Parser**: All 7 threat indicator detection rules
- **Analyzer**: Risk classification boundaries, error handling
- **Database**: CRUD operations, filtering, statistics, export
- **Scraper**: HTTP requests, timeout handling, error cases

Run tests:
```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m pytest tests/test_parser.py -v
```

---

## 📁 Project Structure

```
phishing-scraper/
├── requirements.txt          # Python dependencies
├── main.py                   # Entry point
├── app.py                    # Flask dashboard
├── url_collector.py          # Component 1: URL Feed
├── scraper.py                 # Component 2: Scraper Engine
├── parser.py                  # Component 3: HTML Parser
├── analyzer.py               # Component 4: Threat Analyzer
├── database.py                # Component 5: SQLite Database
├── templates/
│   └── dashboard.html        # Jinja2 template
├── tests/
│   ├── test_url_collector.py
│   ├── test_scraper.py
│   ├── test_parser.py
│   ├── test_analyzer.py
│   ├── test_database.py
│   └── run_tests.py
├── LOG.md                     # Development log
└── README.md                 # This file
```

---

## 👥 Team

| Name | Major |
|------|-------|
| Azza Jomni | FIN-IT |
| Tassnim Msallem | FIN-IT |
| Ahmed Rjeb | FIN-IT |
| Aziz Mdaini | FIN-IT |
| Taycir Sahnouni | MRK-IT |

**Course:** IT360 - Information Assurance and Security  
**Academic Year:** 2025-2026

---

## 📄 License

This project is developed for academic purposes as part of the IT360 course requirements.

---

## 🔗 References

- [URLhaus](https://urlhaus.abuse.ch/) - Malware URL exchange
- [PhishTank](https://www.phishtank.com/) - Community phishing database
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

*Last Updated: May 2026*