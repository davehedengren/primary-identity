import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'identities.db'

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
    identity_counts = {}  # How many times each identity appears
    identity_ranks = {}   # Sum of ranks for each identity (lower = more important)
    identity_rank_counts = {}  # How many times each identity was ranked
    
    for sub in submissions:
        for rank, identity in enumerate(sub['identities'], start=1):
            identity_lower = identity.lower().strip()
            
            # Count occurrences
            identity_counts[identity_lower] = identity_counts.get(identity_lower, 0) + 1
            
            # Track ranks
            if identity_lower not in identity_ranks:
                identity_ranks[identity_lower] = 0
                identity_rank_counts[identity_lower] = 0
            identity_ranks[identity_lower] += rank
            identity_rank_counts[identity_lower] += 1
    
    # Calculate average ranks
    avg_ranks = {}
    for identity, total_rank in identity_ranks.items():
        avg_ranks[identity] = total_rank / identity_rank_counts[identity]
    
    # Sort by average rank (lower is better/more important)
    sorted_by_importance = sorted(avg_ranks.items(), key=lambda x: x[1])
    
    # Sort by frequency
    sorted_by_frequency = sorted(identity_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Check for "child of god" variants
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
        'by_frequency': sorted_by_frequency[:15],  # Top 15 most common
        'by_importance': sorted_by_importance[:15],  # Top 15 most important
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

