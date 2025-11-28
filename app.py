from flask import Flask, render_template, request, jsonify, Response
import csv
import io
import re
import os

app = Flask(__name__)

# Database configuration
USE_POSTGRES = os.environ.get('POSTGRES_URL') is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_db():
        """Get PostgreSQL connection."""
        conn = psycopg2.connect(os.environ['POSTGRES_URL'], cursor_factory=RealDictCursor)
        return conn

    def init_db():
        """Create PostgreSQL table if not exists."""
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                participation_type TEXT NOT NULL,
                team_members TEXT,
                skill_level TEXT NOT NULL,
                project_idea TEXT NOT NULL,
                wants_free_license BOOLEAN NOT NULL,
                availability_confirmed BOOLEAN NOT NULL,
                share_recordings BOOLEAN NOT NULL,
                social_handle TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
else:
    import sqlite3

    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hackathon.db')

    def get_db():
        """Get SQLite connection with row factory."""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        """Create SQLite table if not exists."""
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                participation_type TEXT NOT NULL,
                team_members TEXT,
                skill_level TEXT NOT NULL,
                project_idea TEXT NOT NULL,
                wants_free_license INTEGER NOT NULL,
                availability_confirmed INTEGER NOT NULL,
                share_recordings INTEGER NOT NULL,
                social_handle TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()


# Initialize database on startup
init_db()


@app.route('/')
def index():
    """Serve the registration form."""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Handle registration form submission."""
    data = request.get_json()
    errors = []

    # Server-side validation
    full_name = data.get('full_name', '').strip()
    if not full_name:
        errors.append('Full name is required')

    email = data.get('email', '').strip().lower()
    if not email:
        errors.append('Email is required')
    elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        errors.append('Invalid email format')

    phone = data.get('phone', '').strip()

    participation_type = data.get('participation_type', '')
    if not participation_type:
        errors.append('Participation type is required')

    # Conditional: team members required if "team"
    team_members = data.get('team_members', '').strip()
    if participation_type == 'team' and not team_members:
        errors.append('Team member names/emails are required when participating as a team')

    skill_level = data.get('skill_level', '')
    if not skill_level:
        errors.append('Skill level is required')

    project_idea = data.get('project_idea', '').strip()
    if not project_idea:
        errors.append('Project idea is required')

    availability_confirmed = data.get('availability_confirmed', False)
    if not availability_confirmed:
        errors.append('You must confirm your availability and commitment to submit')

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Insert into database
    try:
        conn = get_db()
        c = conn.cursor()

        wants_license = data.get('wants_free_license', False)
        share_rec = data.get('share_recordings', False)

        if USE_POSTGRES:
            c.execute('''
                INSERT INTO registrations
                (full_name, email, phone, participation_type, team_members, skill_level,
                 project_idea, wants_free_license, availability_confirmed, share_recordings, social_handle)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                full_name,
                email,
                phone or None,
                participation_type,
                team_members or None,
                skill_level,
                project_idea,
                wants_license,
                True,
                share_rec,
                data.get('social_handle', '').strip() or None
            ))
        else:
            c.execute('''
                INSERT INTO registrations
                (full_name, email, phone, participation_type, team_members, skill_level,
                 project_idea, wants_free_license, availability_confirmed, share_recordings, social_handle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                full_name,
                email,
                phone or None,
                participation_type,
                team_members or None,
                skill_level,
                project_idea,
                1 if wants_license else 0,
                1,
                1 if share_rec else 0,
                data.get('social_handle', '').strip() or None
            ))

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({'success': False, 'errors': ['This email is already registered']}), 409
        raise e


@app.route('/admin')
def admin():
    """Admin dashboard showing all registrations."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM registrations ORDER BY created_at DESC')
    registrations = c.fetchall()
    conn.close()
    return render_template('admin.html', registrations=registrations)


@app.route('/export-csv')
def export_csv():
    """Export all registrations as CSV."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM registrations ORDER BY created_at DESC')
    registrations = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Full Name', 'Email', 'Phone', 'Participation Type', 'Team Members',
        'Skill Level', 'Project Idea', 'Wants Free License',
        'Availability Confirmed', 'Share Recordings', 'Social Handle', 'Registered At'
    ])

    participation_labels = {
        'solo': 'Solo',
        'team': 'Team'
    }

    skill_labels = {
        'beginner': 'Beginner (new to n8n)',
        'intermediate': 'Intermediate (built a few workflows)',
        'advanced': 'Advanced (use n8n regularly)'
    }

    for reg in registrations:
        writer.writerow([
            reg['id'],
            reg['full_name'],
            reg['email'],
            reg['phone'] or '',
            participation_labels.get(reg['participation_type'], reg['participation_type']),
            reg['team_members'] or '',
            skill_labels.get(reg['skill_level'], reg['skill_level']),
            reg['project_idea'] or '',
            'Yes' if reg['wants_free_license'] else 'No',
            'Yes' if reg['availability_confirmed'] else 'No',
            'Yes' if reg['share_recordings'] else 'No',
            reg['social_handle'] or '',
            reg['created_at']
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=hackathon_registrations.csv'}
    )


if __name__ == '__main__':
    app.run(debug=True, port=5050)
