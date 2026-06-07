import json
from functools import wraps

from flask import (
    Blueprint, g, flash, jsonify, redirect, render_template,
    request, session, url_for,
)
from markupsafe import Markup
from sqlalchemy import func

from . import db
from .models import Lesson, LessonStep, Module, User, UserProgress


bp = Blueprint("main", __name__)


# ── Helpers ──────────────────────────────────────────────────────────

def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if g.user is None:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.login"))
        return view(*a, **kw)
    return wrapped


@bp.before_app_request
def load_logged_in_user():
    uid = session.get("user_id")
    g.user = db.session.get(User, uid) if uid else None


def _module_progress(user_id):
    """Return {module_id: {pct, done, total}} for all modules."""
    modules = Module.query.order_by(Module.order_index).all()
    result = {}
    for mod in modules:
        step_ids = []
        for les in mod.lessons:
            for s in les.steps:
                step_ids.append(s.id)
        total = len(step_ids)
        if total == 0:
            result[mod.id] = {"pct": 0, "done": 0, "total": 0}
            continue
        done = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.step_id.in_(step_ids),
        ).count() if user_id else 0
        result[mod.id] = {"pct": round(done / total * 100, 1), "done": done, "total": total}
    return result


def _overall_pct(user_id):
    if not user_id:
        return 0
    total = LessonStep.query.count()
    if total == 0:
        return 0
    done = UserProgress.query.filter_by(user_id=user_id).count()
    return round(done / total * 100, 1)


def _course_stats():
    return {
        "module_count": Module.query.count(),
        "lesson_count": Lesson.query.count(),
        "activity_count": LessonStep.query.count(),
    }


def _parse_options(step):
    """Parse JSON options into template-ready format."""
    raw = json.loads(step.options) if isinstance(step.options, str) else step.options
    letters = "ABCDEFGHIJKLMNOP"
    out = []
    for i, opt in enumerate(raw):
        out.append({
            "id": opt.get("id", f"opt{i+1}"),
            "text": opt.get("text", ""),
            "label_letter": letters[i] if i < len(letters) else str(i+1),
        })
    return out


def _correct_answer(step):
    raw = step.correct_answer
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def _hints(step):
    try:
        return json.loads(step.hints)
    except (json.JSONDecodeError, TypeError):
        return []


def _build_table_html(raw_json):
    """Build an HTML table from JSON table data."""
    if not raw_json:
        return None
    try:
        data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
    except (json.JSONDecodeError, TypeError):
        return None
    if not data or "columns" not in data:
        return None

    cols = data["columns"]
    rows = data.get("rows", [])
    highlight = data.get("highlight_row", -1)

    html = '<table class="w-full text-left border-collapse whitespace-nowrap">'
    html += '<thead><tr class="bg-surface-container border-b border-outline-variant">'
    for col in cols:
        html += f'<th class="p-3 font-label-mono text-[12px] text-on-surface-variant uppercase tracking-wider border-r border-outline-variant/50 last:border-r-0">{col}</th>'
    html += '</tr></thead><tbody class="font-label-mono text-[13px]">'
    for i, row in enumerate(rows):
        cls = "border-b border-outline-variant/50 hover:bg-surface-container-low transition-colors"
        if i == highlight:
            cls = "border-b border-secondary/40 bg-secondary-container/20"
        html += f'<tr class="{cls}">'
        for j, val in enumerate(row):
            tcls = "p-3 border-r border-outline-variant/50 last:border-r-0"
            if j == 0:
                tcls += " text-secondary"
            html += f'<td class="{tcls}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return Markup(html)


def _build_code_html(code_raw, language="sql"):
    """Build syntax-highlighted HTML from raw code, with clickable lines for 'spot' activities."""
    if not code_raw:
        return None, None
    lines = code_raw.strip().split('\n')
    html_lines = []
    for i, line in enumerate(lines, 1):
        # Escape HTML entities first, then apply highlighting
        import html as html_mod
        safe_line = html_mod.escape(line)
        highlighted = _highlight_line(safe_line, language)
        html_lines.append(
            f'<div class="flex code-line px-2 rounded-r" data-line="{i}">'
            f'<span class="editor-line-num w-8 select-none text-right pr-4 flex-shrink-0">{i}</span>'
            f'<span class="whitespace-pre">{highlighted}</span></div>'
        )
    return Markup('\n'.join(html_lines)), code_raw


def _highlight_line(line, language):
    """Very basic syntax highlighting via span classes. Input is already HTML-escaped."""
    import re
    if language in ("python", "py"):
        # Comments first (uses # which is safe in escaped HTML)
        line = re.sub(r'(#.*)', r'<span class="syntax-comment">\1</span>', line)
        # Keywords
        keywords = r'\b(import|from|def|return|if|else|elif|for|class|try|except|with|as|and|or|not|in|is|None|True|False)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        # Strings — match f-strings and regular strings (HTML-escaped quotes: &quot; and &#x27;)
        line = re.sub(r'(f?&quot;.*?&quot;|f?&#x27;.*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        # Function calls
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*\(', r'<span class="syntax-function">\1</span>(', line)
    elif language in ("sql",):
        keywords = r'\b(SELECT|FROM|WHERE|AND|OR|INSERT|UPDATE|DELETE|DROP|CREATE|TABLE|INTO|VALUES|SET|LIKE|UNION|ORDER|BY|LIMIT|JOIN|ON|AS|NULL|NOT|IN|EXISTS|BETWEEN|HAVING|GROUP|DISTINCT|TOP|SLEEP|IF|CONCAT|SUBSTRING|CONVERT|LOAD_FILE|EXTRACTVALUE)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line, flags=re.IGNORECASE)
        # SQL strings use &#x27; (escaped single quotes)
        line = re.sub(r'(&#x27;[^&]*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        line = re.sub(r'(--.*)', r'<span class="syntax-comment">\1</span>', line)
    elif language in ("javascript", "js"):
        line = re.sub(r'(//.*)', r'<span class="syntax-comment">\1</span>', line)
        keywords = r'\b(const|let|var|function|return|if|else|for|while|class|new|this|async|await|import|export|from|require)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        line = re.sub(r'(`[^`]*`|&quot;.*?&quot;|&#x27;.*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*\(', r'<span class="syntax-function">\1</span>(', line)
    elif language in ("java",):
        keywords = r'\b(public|private|static|void|class|return|if|else|new|String|int|boolean|import)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        line = re.sub(r'(&quot;.*?&quot;)', r'<span class="syntax-string">\1</span>', line)
    return line


# ── Routes ───────────────────────────────────────────────────────────

@bp.route("/")
def index():
    modules = Module.query.order_by(Module.order_index).all()
    user_count = User.query.count()
    return render_template(
        "index.html",
        modules=modules,
        user_count=user_count,
        **_course_stats(),
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = None
        if not username or not email or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            error = "Username or email already registered."

        if error is None:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("main.login"))
        flash(error, "danger")

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            flash("Welcome back.", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def dashboard():
    modules = Module.query.order_by(Module.order_index).all()
    mod_progress = _module_progress(g.user.id)
    overall_pct = _overall_pct(g.user.id)

    # Build in-progress and completed lists
    in_progress = []
    completed_modules = []
    for mod in modules:
        mp = mod_progress[mod.id]
        if mp["pct"] >= 100:
            completed_modules.append({"module": mod, "pct": mp["pct"]})
        else:
            # Find next incomplete lesson
            next_lesson = None
            for les in mod.lessons:
                step_ids = [s.id for s in les.steps]
                if step_ids:
                    done = UserProgress.query.filter(
                        UserProgress.user_id == g.user.id,
                        UserProgress.step_id.in_(step_ids),
                    ).count()
                    if done < len(step_ids):
                        next_lesson = les
                        break
                else:
                    next_lesson = les
                    break
            if next_lesson is None and mod.lessons:
                next_lesson = mod.lessons[0]
            if mp["pct"] > 0 or not in_progress:
                in_progress.append({"module": mod, "pct": mp["pct"], "next_lesson": next_lesson})

    return render_template(
        "dashboard.html",
        modules=modules,
        in_progress=in_progress[:3],
        completed_modules=completed_modules,
        overall_pct=overall_pct,
        module_count=len(modules),
    )


@bp.route("/course")
@login_required
def course():
    modules = Module.query.order_by(Module.order_index).all()
    mod_progress = _module_progress(g.user.id)
    overall_pct = _overall_pct(g.user.id)
    first_lesson = Lesson.query.join(Module).order_by(Module.order_index, Lesson.order_index).first()

    return render_template(
        "course.html",
        modules=modules,
        mod_progress=mod_progress,
        overall_pct=overall_pct,
        first_lesson=first_lesson,
    )


@bp.route("/lesson/<int:lesson_id>")
@login_required
def lesson_view(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    all_modules = Module.query.order_by(Module.order_index).all()
    overall_pct = _overall_pct(g.user.id)
    activity_count = LessonStep.query.count()

    # Find first incomplete step in this lesson
    current_step = None
    step_number = 1
    total_steps = len(lesson.steps)
    for i, step in enumerate(lesson.steps, 1):
        done = UserProgress.query.filter_by(user_id=g.user.id, step_id=step.id).first()
        if not done:
            current_step = step
            step_number = i
            break
    # If all done, show last step
    if current_step is None and lesson.steps:
        current_step = lesson.steps[-1]
        step_number = total_steps

    # Prepare display data
    step_options = _parse_options(current_step) if current_step else []
    correct_answer_json = json.dumps(_correct_answer(current_step)) if current_step else "null"
    explanation_json = json.dumps(current_step.explanation if current_step else "")
    hints_json = json.dumps(_hints(current_step) if current_step else [])

    # Code to display (prefer step-specific, fallback to lesson-level)
    display_code = None
    display_code_raw = None
    display_code_filename = None
    code_src = current_step if (current_step and current_step.code_snippet) else lesson
    if code_src and getattr(code_src, 'code_snippet', None):
        lang = getattr(code_src, 'code_language', 'sql') or 'sql'
        display_code, display_code_raw = _build_code_html(code_src.code_snippet, lang)
        display_code_filename = getattr(code_src, 'code_filename', None) or f"snippet.{lang}"

    # Table data
    table_html = _build_table_html(lesson.table_data)

    # Navigation: next lesson with steps, or next lesson in sequence
    all_lessons = Lesson.query.join(Module).order_by(Module.order_index, Lesson.order_index).all()
    current_idx = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), 0)

    # Next step within same lesson
    next_lesson = None
    if current_step and step_number < total_steps:
        next_lesson = lesson  # Will reload showing next step

    next_step_lesson = None
    if current_idx + 1 < len(all_lessons):
        next_step_lesson = all_lessons[current_idx + 1]

    return render_template(
        "lesson.html",
        lesson=lesson,
        all_modules=all_modules,
        module_count=len(all_modules),
        activity_count=activity_count,
        overall_pct=overall_pct,
        current_step=current_step,
        step_number=step_number,
        total_steps=total_steps,
        step_options=step_options,
        correct_answer_json=correct_answer_json,
        explanation_json=explanation_json,
        hints_json=hints_json,
        display_code=display_code,
        display_code_raw=display_code_raw,
        display_code_filename=display_code_filename,
        table_html=table_html,
        next_lesson=next_lesson,
        next_step_lesson=next_step_lesson,
    )


@bp.route("/leaderboard")
def leaderboard():
    ranking = (
        db.session.query(
            User.username,
            func.count(UserProgress.id).label("completed_steps"),
            User.streak_days.label("streak"),
        )
        .outerjoin(UserProgress, UserProgress.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(UserProgress.id).desc(), User.username.asc())
        .all()
    )
    return render_template("leaderboard.html", ranking=ranking)


# ── API Endpoints ────────────────────────────────────────────────────

@bp.route("/api/complete-step", methods=["POST"])
@login_required
def api_complete_step():
    data = request.get_json(silent=True) or {}
    step_id = data.get("step_id")
    if not step_id:
        return jsonify({"ok": False, "error": "Missing step_id"}), 400

    step = db.session.get(LessonStep, step_id)
    if not step:
        return jsonify({"ok": False, "error": "Invalid step"}), 404

    existing = UserProgress.query.filter_by(user_id=g.user.id, step_id=step_id).first()
    if not existing:
        db.session.add(UserProgress(user_id=g.user.id, step_id=step_id))
        db.session.commit()

    return jsonify({"ok": True})


@bp.route("/api/set-theme", methods=["POST"])
def api_set_theme():
    data = request.get_json(silent=True) or {}
    theme = data.get("theme", "light")
    if theme not in ("light", "dark"):
        theme = "light"
    if g.user:
        g.user.theme = theme
        db.session.commit()
    return jsonify({"ok": True})
