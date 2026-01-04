import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import sqlite3

app = Flask(__name__)

DATABASE = 'identities.db'
UPLOAD_FOLDER = 'uploads'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            identities TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            photo_filename TEXT,
            interesting_fact TEXT NOT NULL,
            goal TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ============ Student Routes ============

@app.route('/')
def student_page():
    """Render the student identity entry page."""
    return render_template('student.html')

@app.route('/api/submit', methods=['POST'])
def submit_identities():
    """Submit a student's ranked identities."""
    data = request.get_json()
    identities = data.get('identities', [])
    
    if not identities:
        return jsonify({'error': 'No identities provided'}), 400
    
    conn = get_db()
    conn.execute(
        'INSERT INTO submissions (identities) VALUES (?)',
        (json.dumps(identities),)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Thank you for sharing!'})

@app.route('/submitted')
def submitted():
    """Show thank you page after submission."""
    return render_template('submitted.html')

# ============ Goals Survey Routes ============

@app.route('/goals')
def goals_page():
    """Render the 2026 goals survey page."""
    return render_template('goals.html')

@app.route('/api/goals', methods=['POST'])
def submit_goals():
    """Submit a goals survey response."""
    name = request.form.get('name', '').strip()
    interesting_fact = request.form.get('interesting_fact', '').strip()
    goal = request.form.get('goal', '').strip()
    
    if not name or not interesting_fact or not goal:
        return jsonify({'error': 'Please fill in all fields'}), 400
    
    # Handle photo upload
    photo_filename = None
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename:
            # Generate unique filename
            ext = os.path.splitext(photo.filename)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                photo_filename = f"{uuid.uuid4()}{ext}"
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))
    
    conn = get_db()
    conn.execute(
        'INSERT INTO goals (name, photo_filename, interesting_fact, goal) VALUES (?, ?, ?, ?)',
        (name, photo_filename, interesting_fact, goal)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/goals/submitted')
def goals_submitted():
    """Show thank you page after goals submission."""
    return render_template('goals_submitted.html')

@app.route('/goals/view')
def goals_view():
    """View all goals submissions."""
    return render_template('goals_view.html')

@app.route('/api/goals/list')
def get_goals():
    """Get all goals submissions."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM goals ORDER BY created_at DESC').fetchall()
    conn.close()
    
    goals = []
    for row in rows:
        goals.append({
            'id': row['id'],
            'created_at': row['created_at'],
            'name': row['name'],
            'photo_filename': row['photo_filename'],
            'interesting_fact': row['interesting_fact'],
            'goal': row['goal']
        })
    
    return jsonify({'goals': goals, 'total': len(goals)})

@app.route('/api/goals/reset', methods=['POST'])
def reset_goals():
    """Clear all goals submissions."""
    conn = get_db()
    conn.execute('DELETE FROM goals')
    conn.commit()
    conn.close()
    
    # Clear uploaded photos
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))
    
    return jsonify({'success': True})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded photos."""
    return send_from_directory(UPLOAD_FOLDER, filename)

# ============ Teacher Routes ============

@app.route('/teacher')
def teacher_dashboard():
    """Teacher dashboard with visualizations."""
    return render_template('teacher.html')

@app.route('/api/results')
def get_results():
    """Get all submissions for visualization."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM submissions ORDER BY created_at DESC').fetchall()
    conn.close()
    
    submissions = []
    for row in rows:
        submissions.append({
            'id': row['id'],
            'created_at': row['created_at'],
            'identities': json.loads(row['identities'])
        })
    
    # Calculate statistics
    identity_counts = {}
    identity_ranks = {}
    identity_rank_counts = {}
    
    for sub in submissions:
        for rank, identity in enumerate(sub['identities'], start=1):
            identity_lower = identity.lower().strip()
            identity_counts[identity_lower] = identity_counts.get(identity_lower, 0) + 1
            
            if identity_lower not in identity_ranks:
                identity_ranks[identity_lower] = 0
                identity_rank_counts[identity_lower] = 0
            identity_ranks[identity_lower] += rank
            identity_rank_counts[identity_lower] += 1
    
    avg_ranks = {}
    for identity, total_rank in identity_ranks.items():
        avg_ranks[identity] = total_rank / identity_rank_counts[identity]
    
    sorted_by_importance = sorted(avg_ranks.items(), key=lambda x: x[1])
    sorted_by_frequency = sorted(identity_counts.items(), key=lambda x: x[1], reverse=True)
    
    child_of_god_rank = None
    for identity, avg_rank in avg_ranks.items():
        if 'child of god' in identity.lower() or 'god' in identity.lower():
            child_of_god_rank = {
                'identity': identity,
                'avg_rank': avg_rank,
                'count': identity_counts[identity]
            }
            break
    
    return jsonify({
        'submissions': submissions,
        'total_submissions': len(submissions),
        'by_frequency': sorted_by_frequency[:15],
        'by_importance': sorted_by_importance[:15],
        'child_of_god': child_of_god_rank
    })

@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Clear all submissions."""
    conn = get_db()
    conn.execute('DELETE FROM submissions')
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'All data has been cleared'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
