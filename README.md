# Job Tracking System

A modern web application for tracking jobs and managing employee assignments. Built with Flask, SQLAlchemy, and a modern UI using Tailwind CSS.

## Features

### User Management
- Role-based access control (Admin, Sales, Bookkeeper, Technician, Project Manager, Front Office)
- User-specific dashboards
- Secure authentication

### Job Management
- Comprehensive job tracking
- Real-time status updates
- Client database with auto-fill functionality
- Image attachments for jobs
- Detailed job information tracking

### Analytics & Reporting
- Monthly job completion statistics
- Revenue tracking
- Performance metrics
- Export functionality (PDF/CSV)
- Custom filtering options

### Client Management
- Client database
- Job history per client
- Contact information management

## Technology Stack

- Python 3.13
- Flask 3.0.2
- SQLAlchemy 2.0.41
- Flask-SQLAlchemy 3.1.1
- Flask-Login for authentication
- Flask-Migrate for database migrations
- Tailwind CSS for styling
- FPDF2 for PDF generation
- Pandas for CSV exports

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   flask --app app.py db upgrade
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application at `http://localhost:5000`

## Default Users

The system comes with the following pre-configured users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| sales | sales123 | Sales Representative |
| bookkeeper | book123 | Bookkeeper |
| tech1 | tech123 | Technician |
| tech2 | tech123 | Technician |
| tech3 | tech123 | Technician |
| project | project123 | Project Manager |
| office | office123 | Front Office |

## Job Status Workflow

1. New: Initial job status
2. Quote Needed: Requires attention from sales/project manager
3. Scheduled: Assigned to technicians
4. In Progress: Currently being worked on
5. Completed: Work finished
6. To be Billed: Ready for bookkeeping

## Export Features

- PDF exports with detailed job information
- CSV exports for data analysis
- Filtering by:
  - Job status
  - Date range
  - Assignment

## Development

To modify the application:

1. Database models are in `models.py`
2. Routes are organized in the `routes` directory
3. Templates are in the `templates` directory
4. Utility functions in `utils` directory

## Security Notes

- Change default passwords after first login
- Keep the SECRET_KEY secure in production
- Use environment variables for sensitive data
- Images are stored securely with unique filenames
- Role-based access control for sensitive operations

## Testing

Generate test data using:
```bash
python generate_test_data.py
```

This will create:
- 20 sample clients
- 100 sample jobs with various statuses
- Realistic data distribution 