from app import create_app, db
from models import Job, Client, User
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def create_test_clients(num_clients=20):
    """Create fake clients"""
    clients = []
    for _ in range(num_clients):
        client = Client(
            name=fake.company(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            notes=fake.text(max_nb_chars=200)
        )
        db.session.add(client)
        clients.append(client)
    db.session.commit()
    return clients

def create_test_jobs(num_jobs=100):
    """Create fake jobs with various statuses and dates"""
    # Get existing users and clients
    technicians = User.query.join(User.roles).filter_by(name='technician').all()
    sales_reps = User.query.join(User.roles).filter_by(name='sales').all()
    clients = Client.query.all()

    if not technicians or not sales_reps or not clients:
        print("Error: Make sure you have technicians, sales reps, and clients in the database")
        return

    # Job status progression
    status_progression = [
        'new',
        'quote_needed',
        'scheduled',
        'in_progress',
        'completed',
        'to_be_billed'
    ]

    # Create jobs across the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    for _ in range(num_jobs):
        # Randomly select status and calculate dates
        status_index = random.randint(0, len(status_progression) - 1)
        status = status_progression[status_index]
        
        # Create job with progressive dates based on status
        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)
        
        # Calculate scheduled_date between created_at and now
        max_schedule_date = min(end_date, created_at + timedelta(days=30))
        scheduled_date = fake.date_time_between(start_date=created_at, end_date=max_schedule_date)
        
        # Calculate completed_at for completed jobs
        completed_at = None
        if status in ['completed', 'to_be_billed']:
            completed_at = fake.date_time_between(
                start_date=scheduled_date,
                end_date=scheduled_date + timedelta(days=7)
            )

        # Create the job
        job = Job(
            title=fake.sentence(nb_words=4),
            description=fake.paragraph(),
            status=status,
            created_at=created_at,
            scheduled_date=scheduled_date.date(),
            scheduled_time=scheduled_date.time(),
            estimated_duration=random.uniform(1.0, 8.0),
            client=random.choice(clients),
            location=fake.address(),
            priority=random.choice(['low', 'medium', 'high', 'urgent']),
            materials_needed=fake.text(max_nb_chars=100),
            estimated_cost=random.uniform(100.0, 5000.0),
            actual_cost=random.uniform(100.0, 5000.0) if status in ['completed', 'to_be_billed'] else None,
            assigned_to=random.choice(technicians),
            created_by=random.choice(sales_reps),
            notes=fake.text(max_nb_chars=200),
            completion_notes=fake.text(max_nb_chars=200) if status in ['completed', 'to_be_billed'] else None,
            completed_at=completed_at
        )
        db.session.add(job)

    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("Creating test clients...")
        create_test_clients()
        print("Creating test jobs...")
        create_test_jobs()
        print("Done! Test data has been generated.") 