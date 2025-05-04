# GSMArena Phone Scraper Web App (Redesigned)

This is a simple Flask web application that allows users to search for phone specifications on GSMArena.com. This version features a redesigned user interface using Tailwind CSS (via Play CDN) and vanilla JavaScript, incorporating features like dark mode, cards for results, and a modal for detailed views.

## Structure

- `src/main.py`: The main Flask application file. It defines routes and runs the app.
- `src/scraper.py`: Contains the Python script using Playwright to scrape GSMArena.
- `src/routes/gsmarena.py`: Defines the Flask blueprint and API endpoint (`/api/gsmarena/search`) that triggers the scraper.
- `src/static/index.html`: The frontend HTML page with the redesigned UI (Tailwind CSS via CDN), search form, card display, modal, dark mode toggle, and JavaScript to interact with the API.
- `requirements.txt`: Lists the Python dependencies required to run the application.
- `venv/`: Python virtual environment (not included in zip).

## How to Run Locally

1.  **Navigate to the project directory:**
    ```bash
    cd gsmarena_web_app
    ```
2.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
3.  **Install Python dependencies (if not already installed):**
    ```bash
    pip install -r requirements.txt
    # You might also need to install Playwright browsers if running for the first time:
    playwright install --with-deps chromium
    ```
4.  **Run the Flask application:**
    ```bash
    python src/main.py
    ```
5.  Open your web browser and go to `http://127.0.0.1:5002` (or the port specified in `main.py`).

**Note:**
- The frontend uses Tailwind CSS via the Play CDN, so an internet connection is required for the styles to load.
- The scraping process can take some time depending on the GSMArena website's response time.

