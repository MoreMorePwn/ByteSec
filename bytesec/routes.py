import base64
import io
import json
import hashlib
import html
import os
import re
import subprocess
import zipfile
from functools import wraps
from pathlib import Path

from flask import (
    Blueprint, g, flash, jsonify, redirect, render_template,
    request, send_file, session, url_for,
)
from markupsafe import Markup
from sqlalchemy import func

from . import db
from .models import Lesson, LessonStep, Module, User, UserProgress


bp = Blueprint("main", __name__)
ROOT_DIR = Path(__file__).resolve().parents[1]
CTF_DIR = ROOT_DIR / "ctf_chall" / "ezsqli"
XOR_CTF_DIR = ROOT_DIR / "ctf_chall" / "re_asm_xor_checker"

COURSE_TRACKS = [
    {
        "key": "web",
        "label": "[WEB]",
        "title": "Web Exploitation: SQL Injection",
        "short_title": "Web Exploitation",
        "description": "SQL fundamentals, injection mechanics, exploitation techniques, defensive patterns, real-world cases, and the EzSQLi lab.",
        "icon": "language",
        "order_start": 1,
        "order_end": 8,
    },
    {
        "key": "reverse",
        "label": "[REV]",
        "title": "Reverse Engineering: x86-64 Assembly",
        "short_title": "Reverse Engineering",
        "description": "Registers, stack frames, calls, branch logic, memory operands, XOR encoding, static triage, and the XOR flag-checker lab.",
        "icon": "memory",
        "order_start": 9,
        "order_end": 13,
    },
    {
        "key": "crypto",
        "label": "[CRYPTO]",
        "title": "Cryptography: CryptoBook Core",
        "short_title": "Cryptography",
        "description": "Fundamentals, number theory, asymmetric cryptography, and symmetric cryptography adapted into guided ByteSec lessons.",
        "icon": "vpn_key",
        "order_start": 14,
        "order_end": 18,
    },
]

RSA_CHALLENGE_N = 1050042634739472048527415083734141614623526794604292789934035929043944753840232886771262298879903328617034311167949696362901721533840465932367411227174743302792364017856573114095054665590548643385179579641709628757228698065267663737
RSA_CHALLENGE_E = 3
RSA_CHALLENGE_C = 72240295003014461054855741550584414831200556784223014880653253099947072198594653539608891757481870490299217523710665832953564908965164440080453331341426135368723683931085590986597


# ── Helpers ──────────────────────────────────────────────────────────

def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if g.user is None:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.login"))
        return view(*a, **kw)
    return wrapped


def _is_admin_user():
    if g.user is None:
        return False
    admins = {
        username.strip()
        for username in os.environ.get("BYTESEC_ADMIN_USERS", "demo").split(",")
        if username.strip()
    }
    return g.user.username in admins


def admin_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if g.user is None:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.login"))
        if not _is_admin_user():
            flash("Admin access is required.", "danger")
            return redirect(url_for("main.dashboard"))
        return view(*a, **kw)
    return wrapped


@bp.app_context_processor
def inject_admin_helpers():
    return {"is_admin_user": _is_admin_user}


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


def _first_lesson(modules):
    for mod in modules:
        if mod.lessons:
            return mod.lessons[0]
    return None


def _next_lesson(modules, user_id):
    if not user_id:
        return _first_lesson(modules)
    for mod in modules:
        for les in mod.lessons:
            step_ids = [step.id for step in les.steps]
            if not step_ids:
                return les
            done = UserProgress.query.filter(
                UserProgress.user_id == user_id,
                UserProgress.step_id.in_(step_ids),
            ).count()
            if done < len(step_ids):
                return les
    return _first_lesson(modules)


def _course_tracks(modules, mod_progress=None, user_id=None):
    tracks = []
    for definition in COURSE_TRACKS:
        course_modules = [
            module for module in modules
            if definition["order_start"] <= module.order_index <= definition["order_end"]
        ]
        done = 0
        total = 0
        if mod_progress:
            for module in course_modules:
                progress = mod_progress.get(module.id, {"done": 0, "total": 0})
                done += progress["done"]
                total += progress["total"]
        pct = round(done / total * 100, 1) if total else 0
        track = {
            **definition,
            "modules": course_modules,
            "lesson_count": sum(len(module.lessons) for module in course_modules),
            "activity_count": total or sum(len(lesson.steps) for module in course_modules for lesson in module.lessons),
            "progress_done": done,
            "progress_total": total,
            "progress_pct": pct,
            "first_lesson": _first_lesson(course_modules),
            "next_lesson": _next_lesson(course_modules, user_id),
        }
        if course_modules:
            tracks.append(track)
    return tracks


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


def _learning_tracks():
    return [
        {
            "title": "Web Exploitation",
            "description": "Browser, HTTP, database, and access-control flaws taught from concept to controlled lab practice.",
            "icon": "language",
            "status": "Live",
            "status_class": "bg-secondary-container text-on-secondary-container",
        },
        {
            "title": "Reverse Engineering",
            "description": "Static and dynamic analysis workflows for understanding compiled programs and hidden logic.",
            "icon": "memory",
            "status": "Live",
            "status_class": "bg-secondary-container text-on-secondary-container",
        },
        {
            "title": "Pwn",
            "description": "Binary exploitation fundamentals, process memory, stack behavior, and dockerized practice targets.",
            "icon": "terminal",
            "status": "Planned",
            "status_class": "bg-surface-container text-on-surface-variant",
        },
        {
            "title": "Forensics",
            "description": "Evidence-driven investigation across files, logs, packets, images, and challenge artifacts.",
            "icon": "travel_explore",
            "status": "Planned",
            "status_class": "bg-surface-container text-on-surface-variant",
        },
        {
            "title": "Cryptography",
            "description": "Encoding, classical crypto, implementation mistakes, and practical reasoning through guided puzzles.",
            "icon": "vpn_key",
            "status": "Live",
            "status_class": "bg-secondary-container text-on-secondary-container",
        },
    ]


def _parse_options(step):
    """Parse JSON options into template-ready format."""
    raw = json.loads(step.options) if isinstance(step.options, str) else step.options
    letters = "ABCDEFGHIJKLMNOP"
    out = []
    for i, opt in enumerate(raw):
        text = opt.get("text", "")
        out.append({
            "id": opt.get("id", f"opt{i+1}"),
            "text": text,
            "html": _render_material(text),
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


def _normalize_material(value):
    if not value:
        return ""
    return str(value).replace("\\r\\n", "\n").replace("\\n", "\n")


def _render_inline(text):
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\(((?:https?://|/)[^)]+)\)",
        r'<a class="text-secondary hover:underline" href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _render_table(lines):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)

    header = rows[0]
    body = rows[2:] if len(rows) > 2 else rows[1:]
    table = ['<table class="w-full text-left border-collapse my-4 text-[14px]">']
    table.append('<thead><tr class="border-b border-outline-variant">')
    for cell in header:
        table.append(f'<th class="py-2 pr-4 font-semibold text-on-surface">{_render_inline(cell)}</th>')
    table.append("</tr></thead><tbody>")
    for row in body:
        table.append('<tr class="border-b border-outline-variant/50">')
        for cell in row:
            table.append(f'<td class="py-2 pr-4 text-on-surface-variant">{_render_inline(cell)}</td>')
        table.append("</tr>")
    table.append("</tbody></table>")
    return "".join(table)


def _looks_like_diagram(code):
    markers = ("╔", "║", "╚", "╱", "╲", "│", "├", "└", "→", "↓")
    return any(marker in code for marker in markers)


def _render_diagram_image(code, label="Diagram"):
    lines = code.splitlines() or [""]
    char_width = 9
    line_height = 20
    padding_x = 20
    padding_y = 18
    width = max(360, min(1200, max(len(line) for line in lines) * char_width + padding_x * 2))
    height = len(lines) * line_height + padding_y * 2
    text_rows = []
    for index, line in enumerate(lines):
        y = padding_y + 14 + index * line_height
        text_rows.append(f'<text x="{padding_x}" y="{y}">{html.escape(line)}</text>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label)}">'
        '<rect width="100%" height="100%" rx="12" fill="#0d1117"/>'
        '<style>text{font-family:"JetBrains Mono","Consolas",monospace;font-size:14px;fill:#d4d4d4;white-space:pre}</style>'
        + "".join(text_rows)
        + "</svg>"
    )
    encoded = base64.b64encode(svg.encode()).decode()
    return (
        '<figure class="my-4 overflow-x-auto">'
        f'<img class="max-w-none rounded-lg border border-outline-variant shadow-sm" '
        f'src="data:image/svg+xml;base64,{encoded}" alt="{html.escape(label)}">'
        "</figure>"
    )


def _render_material(value):
    """Render the small markdown subset used by seeded lesson material."""
    text = _normalize_material(value).strip()
    if not text:
        return Markup("")

    blocks = []
    paragraph = []
    code_lines = []
    table_lines = []
    unordered_items = []
    ordered_items = []
    in_code = False
    code_lang = ""

    def flush_paragraph():
        if paragraph:
            joined = " ".join(line.strip() for line in paragraph if line.strip())
            if joined:
                blocks.append(f'<p class="mb-3 last:mb-0">{_render_inline(joined)}</p>')
            paragraph.clear()

    def flush_table():
        if table_lines:
            blocks.append(_render_table(table_lines))
            table_lines.clear()

    def flush_lists():
        if unordered_items:
            items = "".join(f"<li>{_render_inline(item)}</li>" for item in unordered_items)
            blocks.append(f'<ul class="list-disc pl-5 my-3 space-y-1">{items}</ul>')
            unordered_items.clear()
        if ordered_items:
            items = "".join(f"<li>{_render_inline(item)}</li>" for item in ordered_items)
            blocks.append(f'<ol class="list-decimal pl-5 my-3 space-y-1">{items}</ol>')
            ordered_items.clear()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_table()
            flush_lists()
            if in_code:
                raw_code = "\n".join(code_lines)
                if _looks_like_diagram(raw_code):
                    blocks.append(_render_diagram_image(raw_code))
                else:
                    code = html.escape(raw_code)
                    lang_class = f" language-{html.escape(code_lang)}" if code_lang else ""
                    blocks.append(
                        f'<pre class="editor-bg rounded-lg p-4 overflow-x-auto my-4 font-label-mono text-[13px] leading-[16px]">'
                        f'<code class="{lang_class}">{code}</code></pre>'
                    )
                code_lines.clear()
                code_lang = ""
                in_code = False
            else:
                in_code = True
                code_lang = stripped[3:].strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_table()
            flush_lists()
            continue

        if stripped == "---":
            flush_paragraph()
            flush_table()
            flush_lists()
            blocks.append('<hr class="my-4 border-outline-variant">')
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_lists()
            table_lines.append(stripped)
            continue
        flush_table()

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_lists()
            level = min(len(heading.group(1)) + 2, 6)
            blocks.append(
                f'<h{level} class="font-headline-sm text-[18px] font-semibold text-on-surface mt-5 mb-2">'
                f'{_render_inline(heading.group(2))}</h{level}>'
            )
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_lists()
            blocks.append(
                f'<blockquote class="border-l-4 border-secondary pl-4 my-3 text-on-surface-variant italic">'
                f'{_render_inline(stripped.lstrip("> ").strip())}</blockquote>'
            )
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            ordered_items.clear()
            unordered_items.append(re.sub(r"^[-*]\s+", "", stripped))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            unordered_items.clear()
            ordered_items.append(re.sub(r"^\d+\.\s+", "", stripped))
            continue

        flush_lists()
        paragraph.append(line)

    flush_paragraph()
    flush_table()
    flush_lists()
    if in_code and code_lines:
        raw_code = "\n".join(code_lines)
        if _looks_like_diagram(raw_code):
            blocks.append(_render_diagram_image(raw_code))
        else:
            code = html.escape(raw_code)
            blocks.append(
                f'<pre class="editor-bg rounded-lg p-4 overflow-x-auto my-4 font-label-mono text-[13px] leading-[16px]">'
                f'<code>{code}</code></pre>'
            )

    return Markup("\n".join(blocks))


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
    html = '<table class="w-full text-left border-collapse whitespace-nowrap">'
    html += '<thead><tr class="bg-surface-container border-b border-outline-variant">'
    for col in cols:
        html += f'<th class="p-3 font-label-mono text-[12px] text-on-surface-variant uppercase tracking-wider border-r border-outline-variant/50 last:border-r-0">{col}</th>'
    html += '</tr></thead><tbody class="font-label-mono text-[13px]">'
    for i, row in enumerate(rows):
        cls = "border-b border-outline-variant/50 hover:bg-surface-container-low transition-colors"
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
    code_raw = _normalize_material(code_raw)
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
        if line.lstrip().startswith("#"):
            return f'<span class="syntax-comment">{line}</span>'
        # Comments first (uses # which is safe in escaped HTML)
        # Keywords
        keywords = r'\b(import|from|def|return|if|else|elif|for|class|try|except|with|as|and|or|not|in|is|None|True|False)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        # Strings — match f-strings and regular strings (HTML-escaped quotes: &quot; and &#x27;)
        line = re.sub(r'(f?&quot;.*?&quot;|f?&#x27;.*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        # Function calls
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*\(', r'<span class="syntax-function">\1</span>(', line)
    elif language in ("sql",):
        if line.lstrip().startswith("--"):
            return f'<span class="syntax-comment">{line}</span>'
        keywords = r'\b(SELECT|FROM|WHERE|AND|OR|INSERT|UPDATE|DELETE|DROP|CREATE|TABLE|INTO|VALUES|SET|LIKE|UNION|ORDER|BY|LIMIT|JOIN|ON|AS|NULL|NOT|IN|EXISTS|BETWEEN|HAVING|GROUP|DISTINCT|TOP|SLEEP|IF|CONCAT|SUBSTRING|CONVERT|LOAD_FILE|EXTRACTVALUE)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line, flags=re.IGNORECASE)
        # SQL strings use &#x27; (escaped single quotes)
        line = re.sub(r'(&#x27;[^&]*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        line = re.sub(r'(--.*)', r'<span class="syntax-comment">\1</span>', line)
    elif language in ("javascript", "js"):
        if line.lstrip().startswith("//"):
            return f'<span class="syntax-comment">{line}</span>'
        keywords = r'\b(const|let|var|function|return|if|else|for|while|class|new|this|async|await|import|export|from|require)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        line = re.sub(r'(`[^`]*`|&quot;.*?&quot;|&#x27;.*?&#x27;)', r'<span class="syntax-string">\1</span>', line)
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*\(', r'<span class="syntax-function">\1</span>(', line)
    elif language in ("java",):
        keywords = r'\b(public|private|static|void|class|return|if|else|new|String|int|boolean|import)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        line = re.sub(r'(&quot;.*?&quot;)', r'<span class="syntax-string">\1</span>', line)
    elif language in ("c", "h"):
        if line.lstrip().startswith("//"):
            return f'<span class="syntax-comment">{line}</span>'
        keywords = r'\b(static|const|unsigned|char|int|size_t|return|if|else|for|while|void|include|define)\b'
        line = re.sub(keywords, r'<span class="syntax-keyword">\1</span>', line)
        line = re.sub(r'(&quot;.*?&quot;)', r'<span class="syntax-string">\1</span>', line)
        line = re.sub(r'\b([a-zA-Z_]\w*)\s*\(', r'<span class="syntax-function">\1</span>(', line)
    elif language in ("asm", "nasm", "x86asm"):
        stripped = line.lstrip()
        if stripped.startswith(";") or stripped.startswith("#"):
            return f'<span class="syntax-comment">{line}</span>'
        mnemonics = r'\b(mov|movzx|lea|xor|add|sub|cmp|test|je|jne|jmp|call|ret|push|pop|inc|dec|sete)\b'
        registers = r'\b(rax|eax|ax|al|rbx|ebx|rcx|ecx|rdx|edx|rsi|esi|rdi|edi|rsp|esp|rbp|ebp|rip|r8|r9|r10|r11|r12|r13|r14|r15|dil)\b'
        line = re.sub(mnemonics, r'<span class="syntax-keyword">\1</span>', line, flags=re.IGNORECASE)
        line = re.sub(registers, r'<span class="syntax-function">\1</span>', line, flags=re.IGNORECASE)
    return line


# ── Routes ───────────────────────────────────────────────────────────

@bp.route("/")
def index():
    modules = Module.query.order_by(Module.order_index).all()
    mod_progress = _module_progress(g.user.id if g.user else None)
    course_tracks = _course_tracks(modules, mod_progress, g.user.id if g.user else None)
    user_count = User.query.count()
    tracks = _learning_tracks()
    return render_template(
        "index.html",
        modules=modules,
        course_tracks=course_tracks,
        tracks=tracks,
        track_count=len(tracks),
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
    course_tracks = _course_tracks(modules, mod_progress, g.user.id)

    return render_template(
        "dashboard.html",
        course_tracks=course_tracks,
        mod_progress=mod_progress,
        overall_pct=overall_pct,
        module_count=len(modules),
    )


@bp.route("/course")
@bp.route("/course/<track_key>")
@login_required
def course(track_key=None):
    modules = Module.query.order_by(Module.order_index).all()
    mod_progress = _module_progress(g.user.id)
    overall_pct = _overall_pct(g.user.id)
    course_tracks = _course_tracks(modules, mod_progress, g.user.id)
    selected_course = None
    if track_key:
        selected_course = next((track for track in course_tracks if track["key"] == track_key), None)
        if selected_course is None:
            flash("Unknown course.", "warning")
            return redirect(url_for("main.course"))
    visible_courses = [selected_course] if selected_course else course_tracks

    return render_template(
        "course.html",
        course_tracks=course_tracks,
        visible_courses=visible_courses,
        selected_course=selected_course,
        mod_progress=mod_progress,
        overall_pct=overall_pct,
    )


def _docker_compose(args, timeout=45):
    try:
        result = subprocess.run(
            ["docker", "compose", *args],
            cwd=CTF_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {"ok": False, "output": "Docker is not installed or not on PATH."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Docker command timed out."}

    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return {"ok": result.returncode == 0, "output": output or "Command completed."}


@bp.route("/admin/docker", methods=["GET", "POST"])
@admin_required
def admin_docker():
    action_result = None
    if request.method == "POST":
        action = request.form.get("action", "")
        commands = {
            "start": ["up", "-d", "--build"],
            "stop": ["down"],
            "restart": ["restart"],
        }
        if action in commands:
            action_result = _docker_compose(commands[action], timeout=90)
            flash(
                f"Docker {action} {'completed' if action_result['ok'] else 'failed'}.",
                "success" if action_result["ok"] else "danger",
            )
        else:
            flash("Unknown Docker action.", "danger")

    status = _docker_compose(["ps"], timeout=20)
    logs = _docker_compose(["logs", "--tail=80"], timeout=20)
    return render_template(
        "admin_docker.html",
        ctf_url=os.environ.get("BYTESEC_CTF_URL", "http://127.0.0.1:8004"),
        status=status,
        logs=logs,
        action_result=action_result,
    )


@bp.route("/downloads/re-asm-xor-checker")
@login_required
def download_re_asm_xor_checker():
    binary_path = XOR_CTF_DIR / "xor_checker"
    if not binary_path.exists():
        build = subprocess.run(
            ["make"],
            cwd=XOR_CTF_DIR,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if build.returncode != 0 or not binary_path.exists():
            return (
                "The XOR checker artifact is not available yet. "
                "Ask the instructor to rebuild the challenge artifact."
            ), 503

    readme = (
        "ByteSec Reverse Engineering: XOR Flag Checker\n"
        "\n"
        "Target: recover a flag in the format BYTESEC{16_hex_characters}.\n"
        "\n"
        "Suggested workflow:\n"
        "  file ./xor_checker\n"
        "  strings -a ./xor_checker\n"
        "  objdump -d -M intel ./xor_checker | less\n"
        "  ./xor_checker BYTESEC{0000000000000000}\n"
        "\n"
        "Submit the recovered flag in the ByteSec lesson page.\n"
    )

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("xor_checker")
        info.external_attr = 0o755 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, binary_path.read_bytes())
        zf.writestr("README.txt", readme)
    archive.seek(0)

    return send_file(
        archive,
        mimetype="application/zip",
        as_attachment=True,
        download_name="bytesec-re-asm-xor-checker.zip",
    )


@bp.route("/downloads/crypto-rsa-starter")
@login_required
def download_crypto_rsa_starter():
    challenge = (
        "ByteSec RSA Starter\n"
        "\n"
        "A message was encrypted with textbook RSA. Recover the plaintext flag.\n"
        "\n"
        f"n = {RSA_CHALLENGE_N}\n"
        f"e = {RSA_CHALLENGE_E}\n"
        f"c = {RSA_CHALLENGE_C}\n"
    )
    readme = (
        "ByteSec Cryptography: RSA Starter\n"
        "\n"
        "Goal: recover the flag from challenge.txt and submit it in ByteSec.\n"
        "\n"
        "This is textbook RSA with a very small public exponent. Check whether the\n"
        "encrypted message actually wrapped around the modulus. If it did not, the\n"
        "ciphertext is just a small integer power of the plaintext.\n"
        "\n"
        "Suggested commands:\n"
        "  python3 solve_helper.py\n"
        "\n"
        "You may edit the helper script or solve it another way.\n"
    )
    helper = (
        "n = " + str(RSA_CHALLENGE_N) + "\n"
        "e = " + str(RSA_CHALLENGE_E) + "\n"
        "c = " + str(RSA_CHALLENGE_C) + "\n"
        "\n"
        "def iroot3(value):\n"
        "    lo, hi = 0, 1\n"
        "    while hi ** 3 <= value:\n"
        "        hi *= 2\n"
        "    while lo + 1 < hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if mid ** 3 <= value:\n"
        "            lo = mid\n"
        "        else:\n"
        "            hi = mid\n"
        "    return lo\n"
        "\n"
        "m = iroot3(c)\n"
        "print('exact cube:', m ** 3 == c)\n"
        "length = (m.bit_length() + 7) // 8\n"
        "print(m.to_bytes(length, 'big'))\n"
    )

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("challenge.txt", challenge)
        zf.writestr("README.txt", readme)
        zf.writestr("solve_helper.py", helper)
    archive.seek(0)

    return send_file(
        archive,
        mimetype="application/zip",
        as_attachment=True,
        download_name="bytesec-crypto-rsa-starter.zip",
    )


@bp.route("/lesson/<int:lesson_id>")
@login_required
def lesson_view(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    all_modules = Module.query.order_by(Module.order_index).all()
    course_tracks = _course_tracks(all_modules, _module_progress(g.user.id), g.user.id)
    current_course = next(
        (
            track for track in course_tracks
            if track["order_start"] <= lesson.module.order_index <= track["order_end"]
        ),
        None,
    )
    current_course_module_index = None
    if current_course:
        for index, module in enumerate(current_course["modules"], 1):
            if module.id == lesson.module_id:
                current_course_module_index = index
                break
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
    correct_answer_json = (
        "null"
        if not current_step or current_step.kind == "flag"
        else json.dumps(_correct_answer(current_step))
    )
    explanation_html_json = json.dumps(str(_render_material(current_step.explanation if current_step else "")))
    hints_html_json = json.dumps([str(_render_material(hint)) for hint in (_hints(current_step) if current_step else [])])
    lesson_narrative_html = _render_material(lesson.narrative)
    step_prompt_html = _render_material(current_step.prompt if current_step else "")

    # Code to display (prefer step-specific, fallback to lesson-level)
    display_code = None
    display_code_raw = None
    display_code_filename = None
    code_src = current_step if (current_step and current_step.code_snippet) else lesson
    if code_src and getattr(code_src, 'code_snippet', None):
        lang = getattr(code_src, 'code_language', None) or 'text'
        display_code, display_code_raw = _build_code_html(code_src.code_snippet, lang)
        display_code_filename = getattr(code_src, 'code_filename', None) or "code"

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
        course_tracks=course_tracks,
        current_course=current_course,
        current_course_module_index=current_course_module_index,
        module_count=len(all_modules),
        activity_count=activity_count,
        overall_pct=overall_pct,
        current_step=current_step,
        step_number=step_number,
        total_steps=total_steps,
        step_options=step_options,
        lesson_narrative_html=lesson_narrative_html,
        step_prompt_html=step_prompt_html,
        correct_answer_json=correct_answer_json,
        explanation_html_json=explanation_html_json,
        hints_html_json=hints_html_json,
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


@bp.route("/api/check-flag-step", methods=["POST"])
@login_required
def api_check_flag_step():
    data = request.get_json(silent=True) or {}
    step_id = data.get("step_id")
    answer = data.get("answer", "")
    if not step_id:
        return jsonify({"ok": False, "error": "Missing step_id"}), 400

    step = db.session.get(LessonStep, step_id)
    if not step or step.kind != "flag":
        return jsonify({"ok": False, "error": "Invalid flag step"}), 404

    submitted_hash = hashlib.sha256(str(answer).strip().lower().encode()).hexdigest()
    is_correct = submitted_hash == step.correct_answer
    if is_correct:
        existing = UserProgress.query.filter_by(user_id=g.user.id, step_id=step.id).first()
        if not existing:
            db.session.add(UserProgress(user_id=g.user.id, step_id=step.id))
            db.session.commit()

    message = step.explanation if is_correct else "The flag is not correct yet. Re-check the challenge output and submit the exact BYTESEC{...} value."
    return jsonify({
        "ok": True,
        "correct": is_correct,
        "message_html": str(_render_material(message)),
    })


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
