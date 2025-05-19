# **DTEAM - Django Developer Practical Test**

Welcome! This test will help us see how you structure a Django project, work with various tools, and handle common tasks in web development. Follow the instructions step by step. Good luck!


## **Requirements**

* Follow PEP 8 and other style guidelines
* Use clear and concise commit messages and docstrings where needed
* Structure your project for readability and maintainability
* Optimize database access using Django’s built-in methods
* Provide enough details in your README


## **Version Control System**

1. Create a public GitHub repository for this practical test, for example: `DTEAM-django-practical-test`
2. Put the text of this test (all instructions) into `README.md`
3. For each task, create a separate branch (e.g., `tasks/task-1`, `tasks/task-2`, etc.)
4. When you finish each task, merge that branch back into `main` but **do not delete** the original task branch


## **Python Virtual Environment**

1. Use `pyenv` to manage the Python version
2. Create a `.python-version` file in your repository
3. Use **Poetry** to manage project dependencies → this will create a `pyproject.toml` file
4. Update your `README.md` with instructions for setting up `pyenv` and `Poetry`


## **Tasks**

### **Task 1: Django Fundamentals**

1. **Create a New Django Project**

   * Name it something like `CVProject`
   * Use the Python version set up in Task 2 and the latest stable Django release
   * Use SQLite as your database for now

2. **Create an App and Model**

   * Create a Django app (e.g., `main`)
   * Define a `CV` model with fields: `firstname`, `lastname`, `skills`, `projects`, `bio`, and `contacts`
   * Organize the data efficiently

3. **Load Initial Data with Fixtures**

   * Create a fixture with at least one sample CV
   * Include fixture loading instructions in `README.md`

4. **List Page View and Template**

   * Implement a view for the main page (`/`) displaying a list of CVs
   * Use any CSS library for styling
   * Ensure efficient data retrieval

5. **Detail Page View**

   * Implement a detail view (`/cv/<id>/`) to show all CV data
   * Style it and ensure DB efficiency

6. **Tests**

   * Add basic tests for list and detail views
   * Add test instructions to `README.md`


### **Task 2: PDF Generation Basics**

1. Install any HTML-to-PDF library or tool
2. Add a **"Download PDF"** button on the CV detail page


### **Task 3: REST API Fundamentals**

1. Install **Django REST Framework (DRF)**
2. Create full CRUD endpoints for the CV model
3. Add tests for each endpoint


### **Task 4: Middleware & Request Logging**

1. **Create a `RequestLog` model**

   * Place in the existing or new app (e.g., `audit`)
   * Fields: `timestamp`, `method`, `path`, and optionally query string, IP, user

2. **Implement Logging Middleware**

   * Write custom middleware to intercept requests
   * Log request data in `RequestLog` model
   * Keep it efficient

3. **Recent Requests Page**

   * Create `/logs/` view showing 10 most recent requests (sorted descending)
   * Include a template showing `timestamp`, `method`, `path`

4. **Test Logging**

   * Ensure tests cover logging


### **Task 5: Template Context Processors**

1. Create a `settings_context` processor to inject settings into templates
2. Create `/settings/` view to show values like `DEBUG`


### **Task 6: Docker Basics**

1. Use **Docker Compose** to containerize the project
2. Switch DB from SQLite to PostgreSQL in Docker
3. Use `.env` file for env variables


### **Task 7: Celery Basics**

1. Install and configure **Celery**, with Redis or RabbitMQ as broker
2. Add Celery worker to Docker Compose
3. On CV detail page, add email field and **"Send PDF to Email"** button → trigger Celery task to email PDF


### **Task 8: OpenAI Basics**

1. On CV detail page, add **"Translate"** button and language selector
2. Include these languages:
   *Cornish, Manx, Breton, Inuktitut, Kalaallisut, Romani, Occitan, Ladino, Northern Sami, Upper Sorbian, Kashubian, Zazaki, Chuvash, Livonian, Tsakonian, Saramaccan, Bislama*
3. Connect to OpenAI translation API (or other) to translate CV content


### **Task 9: Deployment**

* Deploy project to **DigitalOcean** or another VPS

## Installation

### Clone Git Repository

Clone the project by running the following command in your terminal:

```bash
git clone https://github.com/NazarChaban/DTEAM-django-prectical-test.git
```

After cloning, navigate to the newly created directory:

```bash
cd DTEAM-django-practical-test
```

## **Setting Up Poetry**

Poetry is used for dependency management and packaging. Follow these steps to install and configure Poetry for this project:

1. **Install Poetry**

   Follow the official instructions or run:
   ```bash
   pip install poetry
   ```
   Ensure that Poetry is added to your PATH as per the installation output.

2. **Running Shell in Poetry Environment**

   You can activate the virtual environment using:
   ```bash
   poetry env activate
   ```

3. **Install Dependencies**

   With Poetry initialized (using `poetry init` if needed), install the project dependencies:
   ```bash
   poetry install --no-root
   ```
   This creates a virtual environment and installs all required packages as specified in `pyproject.toml`.


## Loading Fixture Data

To load the sample data into your database, ensure you have run migrations first:

```bash
python manage.py makemigrations
python manage.py migrate
```

Then, use the `loaddata` command:

```bash
python manage.py loaddata sample_data.json
```

This will populate your database with the sample CV, skills, and projects defined in `CVProject/main/fixtures/sample_data.json`.


## Running Tests

This project uses `pytest` for running automated tests.

**Running all tests:**

To run all tests, navigate to the project root directory (where `manage.py` and `pytest.ini` are located) and run:

```bash
pytest
```

Or, more verbosely:
```bash
pytest -v
```

**Running tests for a specific app or file:**

You can specify the path to the tests:
```bash
pytest main/tests.py
```
