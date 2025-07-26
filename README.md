# Interactive Property Sales Analysis Dashboard

This is a containerized web application designed to ingest, analyze, and visualize large property sales datasets from CSV files. It provides an interactive dashboard for users to filter and explore property data.

---

## Features

- **Large File Upload:** Supports uploading and processing large CSV files (tested up to 300MB) with progress indication.
- **Interactive Filtering:** Users can dynamically filter the dataset by:
  - Suburb (multi-select)
  - Price Range (min/max slider)
  - Contract Date Range
  - Properties sold more than once within the selected timeframe.
- **Data Visualization:** The dashboard presents key insights through:
  - **KPI Cards:** Total Properties, Total Sales Value, Average Price, Median Price.
  - **Bar Chart:** Top 15 suburbs by number of sales.
  - **Line Chart:** Average property price trend over time (monthly).
- **Paginated Data Table:** A clean, sortable table displays the filtered property data for detailed inspection.
- **Dockerized Environment:** The entire application is containerized with Docker and managed via `docker-compose` for easy setup and consistent deployment.

## Technology Stack

### Backend
- **Python 3.9**
- **Web Framework:** Flask
- **Data Manipulation:** Pandas
- **WSGI Server:** Gunicorn

### Frontend
- **Structure:** HTML5
- **Styling:** Tailwind CSS
- **Interactivity & Charting:** JavaScript (ES6+), Chart.js

### Containerization
- Docker
- Docker Compose

## Project Structure

The project is organized into the following file structure:

```
.
├── docker-compose.yml    # Defines and runs the multi-container Docker application
├── Dockerfile            # Instructions to build the application's Docker image
├── requirements.txt      # Lists the Python dependencies
├── app.py                # The core Flask application with all backend logic
└── templates
    └── index.html        # The single-page HTML file for the frontend UI
```

## Setup and Installation

To run this application locally, you will need to have Docker and Docker Compose installed on your machine.

### 1. Install Docker

If you don't have it, download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### 2. Increase Docker's Memory (Crucial for Large Files)

Processing large datasets is memory-intensive. It is highly recommended to allocate sufficient memory to Docker to prevent crashes.

1. Open Docker Desktop.
2. Go to **Settings > Resources > Advanced**.
3. Increase the **Memory** slider to at least **4GB**, or more if your system allows (e.g., 8GB).
4. Click **Apply & Restart**.

### 3. Clone or Create the Project Files

Place all the project files (`Dockerfile`, `docker-compose.yml`, `requirements.txt`, `app.py`, and the `templates/index.html` file) into a single project directory as shown in the structure above.

### 4. Build and Run the Application

Open a terminal or command prompt, navigate to the root of your project directory, and run the following command:

```bash
docker-compose up --build
```

This command will:
1. Build the Docker image for the application based on the `Dockerfile`.
2. Start the container.
3. The application will be accessible on port `8080`.

### 5. Access the Dashboard

Once the build is complete and the container is running, open your web browser and navigate to:

**http://localhost:8080**

## How to Use the Application

1. **Upload Data:** On the main screen, click the upload area to select a CSV file from your computer.
2. **Analyze:** Click the "Analyze Data" button. A progress bar will show the file upload and server-side analysis status.
3. **Explore:** Once the dashboard loads, use the filters in the left sidebar to explore your data. All charts and metrics will update automatically.
4. **Upload New:** To analyze a different file, click the "Upload New" button in the sidebar to return to the main screen.
