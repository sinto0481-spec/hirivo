import os
import random
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ================================================================
#                   CATEGORIZED QUESTIONS
# ================================================================

CATEGORIES = {
    "Python & Programming": {
        "icon": "🐍",
        "questions": {
            "Explain a Python project you built.": ["python", "project", "code", "library", "flask", "api", "application"],
            "What is the difference between a list and a tuple in Python?": ["list", "tuple", "mutable", "immutable", "python", "data"],
            "How does Flask work?": ["flask", "framework", "route", "request", "response", "api"],
            "How do you debug a program?": ["debug", "error", "testing", "logs", "fix", "code"],
            "What programming languages do you know?": ["programming", "python", "java", "c", "language", "coding"],
            "Explain the concept of Object-Oriented Programming.": ["oop", "class", "object", "inheritance", "encapsulation", "polymorphism"],
            "What is unit testing?": ["testing", "unit", "code", "function", "validation"],
            "What is debugging?": ["debugging", "error", "code", "fix", "testing"],
        }
    },
    "Web Development": {
        "icon": "🌐",
        "questions": {
            "Explain REST API in simple terms.": ["api", "rest", "http", "request", "response", "json"],
            "What is the difference between GET and POST requests?": ["get", "post", "http", "request", "data", "method"],
            "What is the difference between frontend and backend development?": ["frontend", "backend", "server", "client", "web"],
            "What is HTML used for?": ["html", "web", "structure", "tag", "page"],
            "What is CSS used for?": ["css", "style", "design", "layout", "web"],
            "Explain JavaScript in simple terms.": ["javascript", "web", "script", "browser", "interaction"],
            "What is DOM in web development?": ["dom", "document", "html", "javascript", "element"],
            "What is an API?": ["api", "interface", "request", "response", "service"],
            "What is JSON?": ["json", "data", "format", "api", "key"],
            "Explain the difference between HTTP and HTTPS.": ["http", "https", "security", "encryption", "protocol"],
        }
    },
    "Databases": {
        "icon": "🗄️",
        "questions": {
            "What is a database?": ["database", "data", "storage", "table", "record"],
            "Explain SQL and NoSQL databases.": ["sql", "nosql", "database", "query", "table", "document"],
            "What is normalization in databases?": ["normalization", "database", "redundancy", "table", "structure"],
            "What is a primary key?": ["primary key", "unique", "identifier", "database", "table"],
            "What is a foreign key?": ["foreign key", "relation", "table", "database", "reference"],
            "Explain the concept of indexing in databases.": ["index", "database", "search", "performance", "query"],
        }
    },
    "DevOps & Tools": {
        "icon": "⚙️",
        "questions": {
            "What is Git and why is it used?": ["git", "version", "control", "repository", "code"],
            "Explain the difference between Git and GitHub.": ["git", "github", "repository", "version", "hosting"],
            "What is version control?": ["version", "control", "code", "history", "repository"],
            "What is a merge conflict in Git?": ["merge", "conflict", "git", "branch", "code"],
            "Explain the software development lifecycle.": ["sdlc", "development", "design", "testing", "deployment"],
            "What is Agile methodology?": ["agile", "sprint", "iteration", "team", "development"],
            "What is cloud computing?": ["cloud", "server", "storage", "internet", "service"],
            "What is Docker?": ["docker", "container", "deployment", "environment", "application"],
            "What is continuous integration?": ["ci", "automation", "testing", "deployment", "code"],
        }
    },
    "AI & Data Science": {
        "icon": "🤖",
        "questions": {
            "Explain machine learning in simple terms.": ["machine learning", "model", "data", "training", "algorithm"],
            "What is artificial intelligence?": ["ai", "machine", "learning", "automation", "intelligence"],
            "What is data preprocessing?": ["data", "cleaning", "processing", "dataset", "analysis"],
            "Explain the concept of big data.": ["big data", "large", "dataset", "analysis", "processing"],
        }
    },
    "Cybersecurity": {
        "icon": "🔒",
        "questions": {
            "What is cybersecurity?": ["security", "cyber", "protection", "network", "data"],
            "What are common types of cyber attacks?": ["attack", "phishing", "malware", "security", "hack"],
            "What is encryption?": ["encryption", "security", "data", "protection", "key"],
            "Explain the concept of authentication and authorization.": ["authentication", "authorization", "access", "security", "user"],
        }
    },
    "HR & Behavioral": {
        "icon": "💼",
        "questions": {
            "Tell me about yourself.": ["background", "experience", "skills", "education", "developer", "career"],
            "Why do you want to work in this company?": ["company", "mission", "growth", "opportunity", "values", "career"],
            "What are your strengths and weaknesses?": ["strength", "weakness", "improve", "skill", "learning", "development"],
            "Describe a challenging project you worked on.": ["project", "challenge", "solution", "team", "result", "problem"],
            "Where do you see yourself in 5 years?": ["career", "growth", "skills", "experience", "leadership"],
            "Why should we hire you?": ["skills", "experience", "value", "team", "contribution"],
            "What motivates you to work?": ["motivation", "learning", "growth", "challenge", "success"],
            "Describe a time you solved a difficult problem.": ["problem", "solution", "analysis", "decision", "result"],
            "How do you handle pressure or deadlines?": ["deadline", "time", "management", "focus", "priority"],
            "How do you stay updated with technology?": ["learning", "technology", "courses", "reading", "practice"],
            "What are your career goals?": ["career", "goal", "growth", "future", "development"],
            "Tell me about a time you worked in a team.": ["team", "collaboration", "communication", "project", "support"],
            "Describe a situation where you showed leadership.": ["leadership", "team", "decision", "initiative", "responsibility"],
            "How do you manage your time effectively?": ["time", "management", "priority", "schedule", "task"],
            "What is your biggest achievement?": ["achievement", "success", "project", "result", "impact"],
            "Tell me about a failure and what you learned from it.": ["failure", "lesson", "learning", "improvement", "experience"],
            "Do you prefer working alone or in a team?": ["team", "independent", "collaboration", "communication"],
            "What do you know about our company?": ["company", "mission", "product", "service", "industry"],
            "Do you have any questions for us?": ["role", "team", "growth", "opportunity", "company"],
        }
    }
}

# Build flat lookup for backward compatibility
ALL_QUESTIONS = []
QUESTION_KEYWORDS = {}
QUESTION_CATEGORY = {}

for cat_name, cat_data in CATEGORIES.items():
    for q, kws in cat_data["questions"].items():
        ALL_QUESTIONS.append(q)
        QUESTION_KEYWORDS[q] = kws
        QUESTION_CATEGORY[q] = cat_name

QUESTION_TIME_LIMIT = 30  # seconds per question


# ================================================================
#                   IMPROVEMENT TIPS DATA
# ================================================================

KEYWORD_TIPS = {
    "low": [
        "Try to use specific technical terms related to the topic.",
        "Mention key concepts by name — don't just describe them vaguely.",
        "Review common terminology for this subject before your next attempt.",
        "Structure your answer around the main keywords the interviewer expects.",
    ],
    "medium": [
        "Good effort! Try to weave in a few more relevant terms.",
        "Consider giving brief definitions of the key concepts you mention.",
        "Use examples that naturally include domain-specific vocabulary.",
    ],
    "high": [
        "Excellent keyword usage! You clearly know the domain well.",
        "Keep connecting concepts together — it shows deep understanding.",
    ]
}

GRAMMAR_TIPS = {
    "low": [
        "Try to speak in complete sentences rather than fragments.",
        "Pause before answering to organize your thoughts.",
        "Practice the STAR method: Situation, Task, Action, Result.",
        "Aim for at least 3–4 well-formed sentences per answer.",
    ],
    "medium": [
        "Your structure is decent — try adding a clear opening and closing statement.",
        "Use transition phrases like 'Additionally', 'Furthermore', 'For example'.",
    ],
    "high": [
        "Great sentence structure! Your answers are well-organized.",
        "Consider adding a brief summary at the end to reinforce your point.",
    ]
}

CONFIDENCE_TIPS = {
    "low": [
        "Reduce filler words like 'um', 'uh', 'like', and 'you know'.",
        "Practice pausing briefly instead of using filler words.",
        "Speak slowly and deliberately — it projects confidence.",
        "Record yourself practicing and listen back to identify fillers.",
    ],
    "medium": [
        "You have a few filler words — try replacing them with short pauses.",
        "Your delivery is good overall. A bit more practice will help.",
    ],
    "high": [
        "You sound very confident! Minimal filler words detected.",
        "Great natural flow in your speech — keep it up!",
    ]
}


def get_tips(keyword_score, grammar_score, confidence_score):
    """Generate improvement tips based on score ranges."""
    tips = []

    # Keyword tips
    if keyword_score <= 40:
        tips.append(random.choice(KEYWORD_TIPS["low"]))
    elif keyword_score <= 70:
        tips.append(random.choice(KEYWORD_TIPS["medium"]))
    else:
        tips.append(random.choice(KEYWORD_TIPS["high"]))

    # Grammar tips
    if grammar_score <= 40:
        tips.append(random.choice(GRAMMAR_TIPS["low"]))
    elif grammar_score <= 70:
        tips.append(random.choice(GRAMMAR_TIPS["medium"]))
    else:
        tips.append(random.choice(GRAMMAR_TIPS["high"]))

    # Confidence tips
    if confidence_score <= 40:
        tips.append(random.choice(CONFIDENCE_TIPS["low"]))
    elif confidence_score <= 70:
        tips.append(random.choice(CONFIDENCE_TIPS["medium"]))
    else:
        tips.append(random.choice(CONFIDENCE_TIPS["high"]))

    return tips


# ================================================================
#                         MODELS
# ================================================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    attempts = db.relationship('Attempt', backref='author', lazy=True)
    profile = db.relationship('Profile', backref='user', uselist=False, lazy=True)
    sessions = db.relationship('InterviewSession', backref='user', lazy=True)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=True)
    college = db.Column(db.String(200), nullable=True)
    branch = db.Column(db.String(150), nullable=True)
    year_of_study = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    github = db.Column(db.String(200), nullable=True)
    career_goal = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)


class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_questions = db.Column(db.Integer, default=0)
    avg_score = db.Column(db.Float, default=0)
    is_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.relationship('Attempt', backref='interview_session', lazy=True)


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    keyword_score = db.Column(db.Integer, nullable=False)
    grammar_score = db.Column(db.Integer, nullable=False)
    confidence_score = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_session.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    # ================================================================
#                 CREATE DATABASE TABLES
# ================================================================
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ================================================================
#                       AUTH ROUTES
# ================================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password, method='scrypt')
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in and complete your profile.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            if not user.profile or not user.profile.full_name:
                return redirect(url_for('setup_profile'))
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ================================================================
#                     PROFILE SETUP
# ================================================================

@app.route('/profile/setup', methods=['GET', 'POST'])
@login_required
def setup_profile():
    profile = current_user.profile

    if request.method == 'POST':
        if profile is None:
            profile = Profile(user_id=current_user.id)
            db.session.add(profile)

        profile.full_name    = request.form.get('full_name', '').strip()
        profile.college      = request.form.get('college', '').strip()
        profile.branch       = request.form.get('branch', '').strip()
        profile.year_of_study = request.form.get('year_of_study', '').strip()
        profile.phone        = request.form.get('phone', '').strip()
        profile.linkedin     = request.form.get('linkedin', '').strip()
        profile.github       = request.form.get('github', '').strip()
        profile.career_goal  = request.form.get('career_goal', '').strip()

        db.session.commit()
        flash('Profile saved successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('profile_setup.html', profile=profile)


# ================================================================
#                        DASHBOARD
# ================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    attempts = Attempt.query.filter_by(user_id=current_user.id)\
        .order_by(Attempt.id.desc()).all()

    avg_score = round(sum(a.total_score for a in attempts) / len(attempts), 1) if attempts else 0
    best_score = max((a.total_score for a in attempts), default=0)
    total_interviews = len(attempts)

    score_history = [
        {"id": a.id, "score": a.total_score}
        for a in reversed(attempts[:10])
    ]

    # Recent sessions
    recent_sessions = InterviewSession.query.filter_by(user_id=current_user.id)\
        .order_by(InterviewSession.id.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        attempts=attempts,
        avg_score=avg_score,
        best_score=best_score,
        total_interviews=total_interviews,
        score_history=score_history,
        profile=current_user.profile,
        recent_sessions=recent_sessions
    )


# ================================================================
#              INTERVIEW SETUP & SESSION MANAGEMENT
# ================================================================

@app.route('/interview/setup')
@login_required
def interview_setup():
    """Show category selection and question count picker."""
    categories_info = {}
    for cat_name, cat_data in CATEGORIES.items():
        categories_info[cat_name] = {
            "icon": cat_data["icon"],
            "count": len(cat_data["questions"])
        }
    return render_template('interview_setup.html', categories=categories_info)


@app.route('/interview/start', methods=['POST'])
@login_required
def interview_start():
    """Create a new interview session and redirect to it."""
    category = request.form.get('category', '')
    num_questions = int(request.form.get('num_questions', 5))

    if category not in CATEGORIES:
        flash('Invalid category selected.', 'danger')
        return redirect(url_for('interview_setup'))

    available_questions = list(CATEGORIES[category]["questions"].keys())
    num_questions = min(num_questions, len(available_questions))

    # Pick random questions for session
    selected = random.sample(available_questions, num_questions)

    # Create session
    new_session = InterviewSession(
        user_id=current_user.id,
        category=category,
        total_questions=num_questions
    )
    db.session.add(new_session)
    db.session.commit()

    # Store question list in Flask session
    session[f'session_{new_session.id}_questions'] = selected
    session[f'session_{new_session.id}_current'] = 0

    return redirect(url_for('interview_session', session_id=new_session.id))


@app.route('/interview/session/<int:session_id>')
@login_required
def interview_session(session_id):
    """Show the interview page for a specific session."""
    interview_sess = db.session.get(InterviewSession, session_id)

    if not interview_sess or interview_sess.user_id != current_user.id:
        flash('Session not found.', 'danger')
        return redirect(url_for('interview_setup'))

    if interview_sess.is_complete:
        return redirect(url_for('session_summary', session_id=session_id))

    questions_key = f'session_{session_id}_questions'
    current_key = f'session_{session_id}_current'

    questions = session.get(questions_key, [])
    current_idx = session.get(current_key, 0)

    if not questions or current_idx >= len(questions):
        # Session data lost or completed — mark complete
        interview_sess.is_complete = True
        db.session.commit()
        return redirect(url_for('session_summary', session_id=session_id))

    question = questions[current_idx]

    return render_template(
        'interview.html',
        question=question,
        time_limit=QUESTION_TIME_LIMIT,
        session_id=session_id,
        current_num=current_idx + 1,
        total_questions=interview_sess.total_questions,
        category=interview_sess.category,
        category_icon=CATEGORIES[interview_sess.category]["icon"],
        is_last=(current_idx + 1 >= interview_sess.total_questions)
    )


@app.route('/api/session/<int:session_id>/next')
@login_required
def session_next_question(session_id):
    """Advance to the next question in the session."""
    interview_sess = db.session.get(InterviewSession, session_id)

    if not interview_sess or interview_sess.user_id != current_user.id:
        return jsonify({"error": "Session not found"}), 404

    current_key = f'session_{session_id}_current'
    questions_key = f'session_{session_id}_questions'

    current_idx = session.get(current_key, 0) + 1
    questions = session.get(questions_key, [])

    if current_idx >= len(questions):
        # Session complete
        interview_sess.is_complete = True
        # Calculate average score
        session_attempts = Attempt.query.filter_by(session_id=session_id).all()
        if session_attempts:
            interview_sess.avg_score = round(
                sum(a.total_score for a in session_attempts) / len(session_attempts), 1
            )
        interview_sess.completed_questions = len(session_attempts)
        db.session.commit()
        return jsonify({"complete": True, "redirect": url_for('session_summary', session_id=session_id)})

    session[current_key] = current_idx
    question = questions[current_idx]

    return jsonify({
        "complete": False,
        "question": question,
        "current_num": current_idx + 1,
        "total_questions": interview_sess.total_questions,
        "is_last": (current_idx + 1 >= interview_sess.total_questions)
    })


@app.route('/interview/session/<int:session_id>/summary')
@login_required
def session_summary(session_id):
    """Show the session summary page."""
    interview_sess = db.session.get(InterviewSession, session_id)

    if not interview_sess or interview_sess.user_id != current_user.id:
        flash('Session not found.', 'danger')
        return redirect(url_for('interview_setup'))

    # Mark complete if not already
    if not interview_sess.is_complete:
        interview_sess.is_complete = True
        session_attempts = Attempt.query.filter_by(session_id=session_id).all()
        if session_attempts:
            interview_sess.avg_score = round(
                sum(a.total_score for a in session_attempts) / len(session_attempts), 1
            )
        interview_sess.completed_questions = len(session_attempts)
        db.session.commit()

    attempts = Attempt.query.filter_by(session_id=session_id)\
        .order_by(Attempt.id.asc()).all()

    if attempts:
        avg_keyword = round(sum(a.keyword_score for a in attempts) / len(attempts), 1)
        avg_grammar = round(sum(a.grammar_score for a in attempts) / len(attempts), 1)
        avg_confidence = round(sum(a.confidence_score for a in attempts) / len(attempts), 1)
        avg_total = round(sum(a.total_score for a in attempts) / len(attempts), 1)
    else:
        avg_keyword = avg_grammar = avg_confidence = avg_total = 0

    return render_template(
        'session_summary.html',
        session=interview_sess,
        attempts=attempts,
        avg_keyword=avg_keyword,
        avg_grammar=avg_grammar,
        avg_confidence=avg_confidence,
        avg_total=avg_total,
        category_icon=CATEGORIES.get(interview_sess.category, {}).get("icon", "📋")
    )


# Keep the old single-question route as a quick-play fallback
@app.route('/interview')
@login_required
def interview():
    return redirect(url_for('interview_setup'))


# ================================================================
#                    ANSWER ANALYSIS
# ================================================================

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_answer():
    data = request.get_json()
    answer_text = data.get('answer', '')
    question_text = data.get('question', '')
    session_id = data.get('session_id')

    word_count = len(answer_text.split())

    if word_count == 0:
        return jsonify({
            "keyword_score": 0,
            "grammar_score": 0,
            "confidence_score": 0,
            "total_score": 0,
            "keyword_feedback": "No answer detected.",
            "grammar_feedback": "Please provide an answer.",
            "confidence_feedback": "Speak your response clearly.",
            "improvement_tips": ["Try speaking clearly into the microphone."],
            "expected_keywords": QUESTION_KEYWORDS.get(question_text, []),
            "matched_keywords": [],
            "missed_keywords": QUESTION_KEYWORDS.get(question_text, [])
        })

    # -------- Keyword Analysis --------
    expected_keywords = QUESTION_KEYWORDS.get(question_text, [])
    answer_lower = answer_text.lower()
    matched_keywords = [kw for kw in expected_keywords if kw in answer_lower]
    missed_keywords = [kw for kw in expected_keywords if kw not in answer_lower]
    keyword_score = min(100, len(matched_keywords) * 15)

    words = re.findall(r'\w+', answer_lower)
    if len(words) > 20 and keyword_score < 40:
        keyword_score = 40

    # -------- Grammar Analysis --------
    blob = TextBlob(answer_text)
    sentence_count = len(blob.sentences)
    grammar_score = min(100, max(20, sentence_count * 20 + 30))
    if len(words) < 5:
        grammar_score = 10

    # -------- Confidence Analysis --------
    filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'sort of']
    filler_count = sum(
        len(re.findall(r'\b' + re.escape(fw) + r'\b', answer_lower))
        for fw in filler_words
    )
    confidence_score = max(10, 100 - (filler_count * 15))
    if word_count < 5:
        confidence_score = max(confidence_score - 20, 10)

    # -------- Final Score --------
    total_score = int(
        (keyword_score * 0.4) +
        (grammar_score * 0.3) +
        (confidence_score * 0.3)
    )

    # -------- Improvement Tips --------
    tips = get_tips(keyword_score, grammar_score, confidence_score)

    # -------- Determine category --------
    category = QUESTION_CATEGORY.get(question_text, 'General')

    # -------- Save Attempt --------
    attempt = Attempt(
        question=question_text,
        answer=answer_text,
        keyword_score=keyword_score,
        grammar_score=grammar_score,
        confidence_score=confidence_score,
        total_score=total_score,
        category=category,
        session_id=session_id,
        user_id=current_user.id
    )
    db.session.add(attempt)

    # Update session progress
    if session_id:
        interview_sess = db.session.get(InterviewSession, session_id)
        if interview_sess:
            interview_sess.completed_questions = (interview_sess.completed_questions or 0) + 1
            # Update running average
            session_attempts = Attempt.query.filter_by(session_id=session_id).all()
            all_scores = [a.total_score for a in session_attempts] + [total_score]
            interview_sess.avg_score = round(sum(all_scores) / len(all_scores), 1)

    db.session.commit()

    return jsonify({
        'keyword_score': keyword_score,
        'grammar_score': grammar_score,
        'confidence_score': confidence_score,
        'total_score': total_score,
        'grammar_feedback': (
            "Good sentence structure."
            if grammar_score > 60
            else "Consider using clearer sentence structures."
        ),
        'confidence_feedback': (
            "You sounded very confident!"
            if confidence_score > 70
            else "Try to reduce filler words like 'um' and 'uh'."
        ),
        'keyword_feedback': (
            "Great use of relevant terms."
            if keyword_score > 60
            else "Try to use more specific keywords related to the question."
        ),
        'improvement_tips': tips,
        'expected_keywords': expected_keywords,
        'matched_keywords': matched_keywords,
        'missed_keywords': missed_keywords
    })


# ================================================================
#                       RUN APP
# ================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
