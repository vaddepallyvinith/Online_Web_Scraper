# 🎓 University Alumni Data Scraper & Viewer

A full-stack web application built using **Node.js, Express, Puppeteer, and Vanilla JavaScript** that automates the extraction of alumni information from the University of Hyderabad Alumni Portal and presents it through an interactive web dashboard.

---

## 📌 Project Overview

This project performs the following tasks:

1. **Automated Login & Scraping**
   - Logs into the alumni portal using Puppeteer.
   - Navigates through batch-wise and course-wise alumni listings.
   - Extracts alumni details such as:
     - Name
     - Location
     - Class / Batch
     - Course

2. **Data Storage**
   - Stores scraped data in a date-wise text file.
   - Supports multiple scraping sessions with timestamped separators.

3. **Backend API**
   - Exposes a REST API to parse and serve alumni data in JSON format.

4. **Frontend Viewer**
   - Displays alumni data in a clean card-based UI.
   - Supports:
     - Name search
     - Class filtering
     - Dynamic data loading

---

## 🧱 Tech Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | Node.js, Express |
| Scraping   | Puppeteer |
| Frontend   | HTML, CSS, JavaScript |
| Storage    | Text Files (`.txt`) |
| Automation | Headless Browser Control |

---

## 📂 Project Structure
