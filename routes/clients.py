from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Client, db
from datetime import datetime

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients')
@login_required
def index():
    clients = Client.query.order_by(Client.name).all()
    return render_template('clients/index.html', clients=clients)

@clients_bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
def new_client():
    if request.method == 'POST':
        client = Client(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            notes=request.form['notes']
        )
        db.session.add(client)
        db.session.commit()
        flash('Client created successfully!')
        return redirect(url_for('clients.index'))
    return render_template('clients/new.html')

@clients_bp.route('/clients/<int:client_id>')
@login_required
def view_client(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template('clients/view.html', client=client)

@clients_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        client.address = request.form['address']
        client.notes = request.form['notes']
        db.session.commit()
        flash('Client updated successfully!')
        return redirect(url_for('clients.view_client', client_id=client.id))
    return render_template('clients/edit.html', client=client)

@clients_bp.route('/clients/search')
@login_required
def search_clients():
    query = request.args.get('q', '')
    if query:
        clients = Client.query.filter(
            db.or_(
                Client.name.ilike(f'%{query}%'),
                Client.email.ilike(f'%{query}%'),
                Client.phone.ilike(f'%{query}%')
            )
        ).all()
    else:
        clients = []
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address
        } for client in clients])
    
    # Otherwise render the template
    return render_template('clients/search.html', clients=clients, query=query) 