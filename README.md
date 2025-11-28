# n8n Text-to-Workflow Hackathon Registration

A registration web app for the n8n Text-to-Workflow Hackathon ($5,000 in Prizes | December 5-22, 2025).

## Quick Start

### Prerequisites
- Python 3.8 or higher

### Setup & Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   - Registration form: http://localhost:5050
   - Admin dashboard: http://localhost:5050/admin

## Features

- Clean registration form with n8n branding
- Client-side and server-side validation
- Confetti animation on successful registration
- Admin dashboard to view all registrations
- CSV export functionality
- Duplicate email prevention
- Mobile responsive design
- SQLite database (auto-created on first run)

## Project Structure

```
n8n Hackathon/
├── app.py              # Flask application
├── templates/
│   ├── index.html      # Registration form
│   └── admin.html      # Admin dashboard
├── requirements.txt    # Python dependencies
├── hackathon.db        # SQLite database (auto-generated)
└── README.md           # This file
```

## Form Fields

1. Full Name (required)
2. Email (required, unique)
3. Participation Type (Solo / Team with members / Match me)
4. Team Member Names/Emails (if applicable)
5. Skill Level (Beginner / Intermediate / Advanced)
6. Project Idea (required)
7. n8n Subscription Status
8. Availability Confirmation (December 5-22, 2025)
9. LinkedIn/X Handle (optional)

## Admin Features

- View all registrations in a sortable table
- Export all data to CSV
- Color-coded badges for participation type and skill level
- Expandable project idea cells

---

Hosted by Early AI-dopters Community
