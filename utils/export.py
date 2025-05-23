from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os
from models import Job

class JobPDF(FPDF):
    def header(self):
        # Logo (if you have one)
        # self.image('logo.png', 10, 8, 33)
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, 'Job Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def format_job_for_export(job):
    """Format job data for export"""
    return {
        'ID': job.id,
        'Title': job.title,
        'Status': job.status,
        'Client': job.client.name if job.client else 'N/A',
        'Created Date': job.created_at.strftime('%Y-%m-%d'),
        'Scheduled Date': job.scheduled_date.strftime('%Y-%m-%d') if job.scheduled_date else 'N/A',
        'Completed Date': job.completed_at.strftime('%Y-%m-%d') if job.completed_at else 'N/A',
        'Assigned To': job.assigned_to.name if job.assigned_to else 'Unassigned',
        'Priority': job.priority,
        'Estimated Cost': f"${job.estimated_cost:.2f}" if job.estimated_cost else 'N/A',
        'Actual Cost': f"${job.actual_cost:.2f}" if job.actual_cost else 'N/A',
        'Location': job.location,
        'Description': job.description
    }

def export_jobs_to_pdf(jobs, filename):
    """Export jobs to PDF"""
    pdf = JobPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 12)

    # Add report info
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
    pdf.cell(0, 10, f'Total Jobs: {len(jobs)}', 0, 1)
    pdf.ln(5)

    # Table headers
    headers = ['ID', 'Title', 'Status', 'Client', 'Scheduled Date', 'Assigned To', 'Cost']
    col_widths = [15, 40, 25, 35, 25, 35, 25]

    pdf.set_font('helvetica', 'B', 10)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1)
    pdf.ln()

    # Table data
    pdf.set_font('helvetica', '', 9)
    for job in jobs:
        if pdf.get_y() > 250:  # Start new page if near bottom
            pdf.add_page()
            pdf.set_font('helvetica', 'B', 10)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1)
            pdf.ln()
            pdf.set_font('helvetica', '', 9)

        data = [
            str(job.id),
            job.title[:30] + '...' if len(job.title) > 30 else job.title,
            job.status,
            job.client.name if job.client else 'N/A',
            job.scheduled_date.strftime('%Y-%m-%d') if job.scheduled_date else 'N/A',
            job.assigned_to.name if job.assigned_to else 'Unassigned',
            f"${job.actual_cost:.2f}" if job.actual_cost else f"${job.estimated_cost:.2f}" if job.estimated_cost else 'N/A'
        ]

        for i, value in enumerate(data):
            pdf.cell(col_widths[i], 10, str(value), 1)
        pdf.ln()

        # Add job details
        if pdf.get_y() > 250:
            pdf.add_page()
        pdf.ln(5)
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(0, 5, 'Details:', 0, 1)
        pdf.set_font('helvetica', '', 9)
        pdf.multi_cell(0, 5, job.description[:200] + '...' if len(job.description) > 200 else job.description)
        pdf.ln(5)

    return pdf.output(dest='F', name=filename)

def export_jobs_to_csv(jobs, filename):
    """Export jobs to CSV"""
    jobs_data = [format_job_for_export(job) for job in jobs]
    df = pd.DataFrame(jobs_data)
    df.to_csv(filename, index=False)

def get_filtered_jobs(status=None, start_date=None, end_date=None, assigned_to=None):
    """Get filtered jobs based on criteria"""
    query = Job.query

    if status:
        if isinstance(status, list):
            query = query.filter(Job.status.in_(status))
        else:
            query = query.filter_by(status=status)

    if start_date:
        query = query.filter(Job.created_at >= start_date)
    
    if end_date:
        query = query.filter(Job.created_at <= end_date)

    if assigned_to:
        query = query.filter_by(assigned_to_id=assigned_to)

    return query.order_by(Job.created_at.desc()).all() 