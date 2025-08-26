from flask import Flask, render_template, request, redirect, url_for, session, flash
from .database import get_db, init_db
from .models import User, Permission, DataTable
from .auth import authenticate_user, hash_password, get_user_permissions

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize database and create admin user
init_db()
db = get_db()
if not db.query(User).filter(User.username == 'admin').first():
    admin = User(username='admin', password_hash=hash_password('admin'), role='admin')
    db.add(admin)
    db.commit()

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = authenticate_user(db, username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    data = db.query(DataTable).all()
    
    return render_template('admin_dashboard.html', data=data)

@app.route('/admin/data/add', methods=['GET', 'POST'])
def admin_add_data():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        db = get_db()
        new_data = DataTable(
            city=request.form['city'],
            data_field1=request.form['data_field1'],
            data_field2=request.form['data_field2']
        )
        db.add(new_data)
        db.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_form_data.html', action='Add', data=None)

@app.route('/admin/data/edit/<int:data_id>', methods=['GET', 'POST'])
def admin_edit_data(data_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    data = db.query(DataTable).filter(DataTable.id == data_id).first()
    
    if request.method == 'POST':
        data.city = request.form['city']
        data.data_field1 = request.form['data_field1']
        data.data_field2 = request.form['data_field2']
        db.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_form_data.html', action='Edit', data=data)

@app.route('/admin/data/delete/<int:data_id>')
def admin_delete_data(data_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    db.query(DataTable).filter(DataTable.id == data_id).delete()
    db.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    users = db.query(User).filter(User.role == 'user').all()
    
    return render_template('admin_form_user.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
def admin_add_user():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    username = request.form['username']
    password = request.form['password']
    cities = request.form.getlist('cities')
    
    db = get_db()
    new_user = User(username=username, password_hash=hash_password(password), role='user')
    db.add(new_user)
    db.flush()
    
    # Handle ALL cities selection
    if 'ALL' in cities:
        all_cities = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Yogyakarta']
        for city in all_cities:
            permission = Permission(user_id=new_user.id, city=city)
            db.add(permission)
    else:
        for city in cities:
            permission = Permission(user_id=new_user.id, city=city)
            db.add(permission)
    
    db.commit()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    # Delete permissions first
    db.query(Permission).filter(Permission.user_id == user_id).delete()
    # Delete user
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reset/<int:user_id>', methods=['POST'])
def admin_reset_password(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password_hash = hash_password('password123')  # Default password
        db.commit()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user_cities(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    
    if request.method == 'POST':
        cities = request.form.getlist('cities')
        
        # Delete existing permissions
        db.query(Permission).filter(Permission.user_id == user_id).delete()
        
        # Add new permissions
        if 'ALL' in cities:
            all_cities = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Yogyakarta']
            for city in all_cities:
                permission = Permission(user_id=user_id, city=city)
                db.add(permission)
        else:
            for city in cities:
                permission = Permission(user_id=user_id, city=city)
                db.add(permission)
        
        db.commit()
        return redirect(url_for('admin_users'))
    
    # Get current user cities
    permissions = db.query(Permission).filter(Permission.user_id == user_id).all()
    user_cities = [p.city for p in permissions]
    
    return render_template('admin_edit_user_cities.html', user=user, user_cities=user_cities)

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    
    db = get_db()
    permissions = get_user_permissions(db, session['user_id'])
    allowed_cities = [p.city for p in permissions]
    
    if allowed_cities:
        data = db.query(DataTable).filter(DataTable.city.in_(allowed_cities)).all()
    else:
        data = []
    
    return render_template('user_dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)