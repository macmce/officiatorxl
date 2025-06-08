# OfficatorXL - Swim Meet Officials Scheduler

OfficatorXL is a Django-based web application designed for efficient scheduling and management of officials at swim meets. It provides a comprehensive system to handle leagues, divisions, teams, officials, certifications, meet events, positions, and assignments, with a focus on usability and robust data management.

## Features

- **User Authentication**: Secure login, registration, and password management.
- **Role-Based Access Control**:
  - Users can be assigned to specific leagues, restricting their view and management capabilities to those leagues.
  - Admin users (staff) have full access to all data across all leagues, ensuring comprehensive oversight.
- **Comprehensive Entity Management**: Full CRUD (Create, Read, Update, Delete) operations for:
  - **Leagues**: Top-level organizational units, can be assigned to users for granular access control.
  - **Divisions**: Sub-units within leagues to further organize teams.
  - **Teams**: Groups of participants, belonging to divisions. Can have associated user accounts for team-specific management.
  - **Officials**: Individuals who officiate meets, can be associated with teams and hold various certifications.
  - **Certifications**: Qualifications held by officials (e.g., Starter, Stroke & Turn Judge).
  - **Events**: Specific competitions within a meet (e.g., "Men's 100m Freestyle"), categorized by meet type and gender.
  - **Positions**: Roles that officials can be assigned to during a meet (e.g., "Head Timer", "Referee"), linked to predefined strategies.
  - **Meets**: Scheduled occurrences where events take place, involving specific teams and officials.
  - **Assignments**: Linking specific officials to positions for particular meets.
- **Data Import Capabilities**:
  - **Event Import**: Import meet events from Excel (.xlsx) files with comprehensive validation against existing data, detailed error reporting, and a downloadable template to ensure correct formatting.
  - **Position Import**: Import position definitions from Excel (.xlsx) or CSV (.csv) files. Includes validation against existing strategies, options to update existing records, and a downloadable template.
- **Advanced Filtering & Search**: Robust filtering options on list views for entities like Events, Divisions, and Officials, allowing users to quickly find relevant information.
- **Modern & Consistent UI**:
  - Built with Bootstrap 5 for a responsive, mobile-first experience.
  - Standardized design for filter sections, buttons, pagination, and page layouts across the application for enhanced usability.
  - Clear and intuitive navigation structure.
- **RESTful API**:
  - Comprehensive REST API for all major entities (Leagues, Divisions, Teams, Officials, etc.)
  - API endpoints accessible at `/api/v1/officials/`
  - Enables integration with mobile applications, third-party systems, and automation scripts
- **Detailed Views and Forms**:
  - Informative detail views for all entities, showing relevant information and relationships.
  - User-friendly forms for creating and editing data, enhanced with `django-crispy-forms` for better layout and validation display.

## Architecture

### Architecture Overview
The application follows a services-oriented architecture for complex business logic, promoting separation of concerns and reusability, and includes a comprehensive API layer:

- **Import Services**: Dedicated services (e.g., `EventImporter`, `PositionImporter`) in the `officials/services/` module encapsulate the logic for parsing files, validating data, and interacting with the database during import operations.
- **Excel Error Handling**: A specialized module (`excel_errors.py`) provides consistent error tracking and reporting mechanisms for Excel-based imports.
- **Form Separation**: Form definitions and their validation logic are kept in `forms.py`, separate from view logic.
- **Reusable Templates**: Utilizes Django's template inheritance and includes (snippets) to maintain a DRY (Don't Repeat Yourself) template structure, ensuring consistency and easier maintenance.
- **API Layer**: Built using Django REST Framework to provide RESTful API endpoints for all major entities, enabling integration with external systems.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd officiatorxl
   ```
2. **Set up and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
6. **Set up environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=5432
   ```
   A template `.env.example` file is provided for reference.

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```
7. **Access the application**: Open a web browser and navigate to `http://127.0.0.1:8000/`.

## Running Tests

The project includes a suite of automated tests to ensure functionality and prevent regressions.

To run all tests:
1. Ensure your virtual environment is activated and dependencies are installed.
2. Navigate to the project root directory (`officiatorxl`).
3. Run the following command:
   ```bash
   python manage.py test
   ```

To run tests for a specific app (e.g., `officials`):
   ```bash
   python manage.py test officials
   ```

For more verbose output (e.g., to see individual test names, level 2 verbosity):
   ```bash
   python manage.py test -v 2
   ```

## Usage Workflow

A typical workflow for using OfficatorXL might involve:

1.  **Initial Setup (Admin)**:
    *   Log in with your admin account.
    *   Create `League` entities.
    *   Create user accounts and assign them to appropriate `Leagues` if non-admin users will manage specific leagues.
2.  **Structuring Competitions**:
    *   Create `Divisions` within each `League`.
    *   Add `Teams` to their respective `Divisions`.
    *   Optionally, associate user accounts with `Teams` if team managers need specific access (current model supports users being linked to leagues).
3.  **Managing Personnel & Roles**:
    *   Register `Officials` in the system, providing their details.
    *   Define `Certifications` (e.g., "Referee", "Starter") and assign them to `Officials`.
    *   Associate `Officials` with `Teams` they belong to or officiate for.
    *   Create or import `Positions` (e.g., "Lane Timer", "Chief Judge") and link them to relevant `Strategies`.
4.  **Defining Competition Events**:
    *   Manually create or import `Events` (e.g., "Boys 100m Backstroke", "Girls 50m Freestyle") for different meet types.
5.  **Scheduling & Assigning**:
    *   Schedule `Meets`, specifying details like date, time, location, and participating teams.
    *   Create `Assignments` by assigning registered `Officials` to specific `Positions` for each `Meet`.
6.  **Ongoing Management**:
    *   Update official availability, team rosters, and meet schedules as needed.
    *   Utilize filtering and search functionalities to manage and view data efficiently.

## Dependencies

The application relies on the following key Python packages:

- **Django**: Core web framework (version as specified in `requirements.txt`).
- **django-filter**: Enables flexible and declarative filtering of QuerySets on list views.
- **openpyxl**: For reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files. Used for Event and Position imports/exports.
- **pandas**: Powerful data analysis and manipulation library. Used for handling CSV and Excel data during Position imports.
- **django-crispy-forms**: Controls the rendering behavior of Django forms, allowing for clean, Bootstrap-styled forms.
- **crispy-bootstrap5**: Bootstrap 5 template pack for `django-crispy-forms`.
- **Django REST Framework**: Powerful toolkit for building Web APIs.
- **Pillow**: Python Imaging Library (Fork) used for image processing (e.g., team logos, official photos if implemented).

(See `requirements.txt` for a full list and specific versions.)

## Project Structure and Key Modules

-   **`/officiatorxl/`** (Project Root):
    -   `manage.py`: Django's command-line utility.
    -   `requirements.txt`: Project dependencies.
    -   `README.md`: This file.
    -   **`/officiatorxl/`** (Django Project Directory):
        -   `settings.py`: Django project settings.
        -   `urls.py`: Project-level URL routing.
        -   `wsgi.py`, `asgi.py`: Web server gateway interface configurations.
    -   **`/officials/`** (Core Application):
        -   `models.py`: Defines the database schema for all primary entities (League, Division, Team, Official, Event, etc.).
        -   `views.py` (and related `views_*.py` files like `views_leagues.py`, `views_events.py`): Handles HTTP request processing, business logic execution, and template rendering.
        -   `forms.py`: Contains Django form definitions, often integrated with `django-crispy-forms`.
        -   `filters.py`: Implements `django-filter` classes for providing filtering capabilities on list views.
        -   `urls.py`: Defines URL patterns specific to the `officials` app.
        -   `api_urls.py`: Defines URL patterns for the API endpoints.
        -   `api_views.py`: Contains ViewSet definitions for the API.
        -   `admin.py`: Configures how models are displayed and managed in the Django admin interface.
        -   `tests/`: Contains automated tests (unit and integration) for the app's functionality.
        -   **`services/`**: Houses complex business logic decoupled from views.
            -   `event_importer.py`: Logic for importing Event data from Excel files.
            -   `position_importer.py`: Logic for importing Position data from Excel/CSV files.
            -   `excel_errors.py`: Standardized error handling and reporting for Excel-based imports.
        -   `migrations/`: Database migration files generated by Django.
    -   **`/users/`** (User Management Application):
        -   Manages custom user model (if extended from Django's default), authentication views, and user profile functionalities.
    -   **`/templates/`**: Contains all HTML templates, organized by application.
        -   `/templates/base.html`: Base template for consistent layout.
        -   `/templates/officials/`: Templates specific to the `officials` app.
        -   `/templates/officials/snippets/`: Reusable template partials (e.g., forms, navigation elements).
    -   **`/static/`**: Stores static assets like CSS stylesheets, JavaScript files, and images.
    -   **`/media/`**: Default directory for user-uploaded files (e.g., team logos, official photos), if applicable.

## Virtual Environment

This project uses a virtual environment to isolate dependencies. Here's how to work with it:

-   **Create (if not existing)**: `python -m venv venv`
-   **Activate**: `source venv/bin/activate` (Unix/macOS) or `venv\Scripts\activate` (Windows)
-   **Deactivate**: Simply type `deactivate` in the terminal when you're done working on the project.
-   **Update requirements**: If you add new packages, update the `requirements.txt` file: `pip freeze > requirements.txt`

## Admin Access

If you create a superuser during installation (e.g., username `admin`), you can access the Django admin interface at `/admin/`.
Default credentials if created via a script or standard setup might be:
-   **Username**: `admin`
-   **Email**: `admin@example.com`
-   **Password**: `adminpassword123` (Change this immediately on a real deployment!)

## API Usage

OfficatorXL provides a RESTful API for programmatic access to all major entities in the system. The API follows RESTful principles and uses Django REST Framework.

### API Endpoints

All API endpoints are accessible under the `/api/v1/officials/` base URL:

- `/api/v1/officials/leagues/` - League management
- `/api/v1/officials/divisions/` - Division management
- `/api/v1/officials/teams/` - Team management
- `/api/v1/officials/officials/` - Officials management
- `/api/v1/officials/meets/` - Meet management
- `/api/v1/officials/events/` - Event management
- `/api/v1/officials/positions/` - Position management
- `/api/v1/officials/assignments/` - Assignment management
- `/api/v1/officials/certifications/` - Certification management
- `/api/v1/officials/strategies/` - Strategy management
- `/api/v1/officials/userleagueadmins/` - User-League administration

### API Authentication

The API uses token-based authentication. To access protected endpoints, include an Authentication header with your request:

```
Authentication: Token <your-token>
```

## Heroku Deployment

To deploy this application on Heroku, follow these steps:

1. **Create a Heroku account and install the Heroku CLI**:
   Follow the instructions at [Heroku CLI Installation](https://devcenter.heroku.com/articles/heroku-cli).

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create officiatorxl
   ```
   Or connect to an existing app:
   ```bash
   heroku git:remote -a officiatorxl
   ```

4. **Set Python version**:
   Create a `.python-version` file in the project root:
   ```
   3.11
   ```
   This ensures Heroku uses a compatible Python version.

5. **Set environment variables**:
   ```bash
   heroku config:set DB_NAME=your_database_name --app officiatorxl
   heroku config:set DB_USER=your_database_user --app officiatorxl
   heroku config:set DB_PASSWORD=your_database_password --app officiatorxl
   heroku config:set DB_HOST=your_database_host --app officiatorxl
   heroku config:set DB_PORT=5432 --app officiatorxl
   ```

6. **Deploy to Heroku**:
   ```bash
   git push heroku main
   ```
   If you're using a different branch:
   ```bash
   git push heroku your-branch:main
   ```

7. **Run migrations on Heroku**:
   ```bash
   heroku run python manage.py migrate --app officiatorxl
   ```

8. **Create a superuser on Heroku** (optional):
   ```bash
   heroku run python manage.py createsuperuser --app officiatorxl
   ```

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
