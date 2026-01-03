# Who Am I? - Identity Explorer

A fun, interactive web app for Sunday school classes to explore and rank their identities. Students anonymously add their identities (son, daughter, student, friend, child of God, etc.), rank them by importance, and submit. Teachers can view class-wide visualizations showing which identities the class values most.

## Features

- **Student Page**: Kids can add their own identities, drag to reorder by importance, and submit anonymously
- **Teacher Dashboard**: View charts showing most common identities and average rankings
- **Mobile-Friendly**: Works great on phones and tablets for classroom use
- **Persistent Storage**: SQLite database keeps submissions across restarts
- **Real-time Updates**: Dashboard auto-refreshes every 30 seconds

## URLs

| URL | Who Uses It |
|-----|-------------|
| `/` | Students - add and rank identities |
| `/teacher` | Teacher - view class results and visualizations |

## Quick Start on Replit

1. **Import from GitHub**: Go to Replit and click "Import from GitHub", paste your repo URL
2. **Run**: Click the Run button!
3. **Share URLs**: 
   - Give students the main Replit URL
   - Teacher goes to the same URL with `/teacher` at the end

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000` for the student page and `http://localhost:5000/teacher` for the teacher dashboard.

## How It Works

### For Students
1. Visit the main page
2. Add identities one at a time (suggestions provided!)
3. Drag to reorder - most important at top
4. Submit when done

### For Teachers
1. Go to `/teacher`
2. View statistics and charts
3. See how "Child of God" ranks compared to other identities
4. Clear data between class sessions with the reset button

## The Lesson

This app is designed to support a lesson about identity. After students submit their rankings, discuss as a class:

- What identities did we have in common?
- What was ranked most important overall?
- Why is being a "child of God" the most important identity we have?

The goal is to help children understand that while they have many wonderful identities (student, friend, sibling, athlete), their identity as a **child of God** is the most foundational and important.

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Tailwind CSS, Chart.js, SortableJS
- **Fonts**: Fredoka (headings), Quicksand (body)

## File Structure

```
primary-identity/
├── app.py              # Flask application
├── templates/
│   ├── base.html       # Base template
│   ├── student.html    # Student identity entry
│   ├── submitted.html  # Thank you page
│   └── teacher.html    # Teacher dashboard
├── requirements.txt
├── .replit             # Replit config
└── README.md
```

## License

Free to use for educational purposes.
