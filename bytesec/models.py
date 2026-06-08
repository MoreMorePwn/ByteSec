from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from . import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    streak_days = db.Column(db.Integer, default=0, nullable=False)
    last_active = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    theme = db.Column(db.String(10), default="light", nullable=False)

    progress = db.relationship("UserProgress", back_populates="user", cascade="all,delete")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_index = db.Column(db.Integer, nullable=False, default=1)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    icon = db.Column(db.String(40), nullable=False, default="database")
    difficulty = db.Column(db.String(20), nullable=False, default="beginner")
    estimated_minutes = db.Column(db.Integer, nullable=False, default=15)
    category = db.Column(db.String(20), nullable=False, default="web")

    lessons = db.relationship(
        "Lesson", back_populates="module", order_by="Lesson.order_index", cascade="all,delete"
    )


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=1)
    title = db.Column(db.String(200), nullable=False)
    narrative = db.Column(db.Text, nullable=False, default="")
    code_snippet = db.Column(db.Text, nullable=True)
    code_language = db.Column(db.String(20), nullable=True)
    code_filename = db.Column(db.String(60), nullable=True)
    table_data = db.Column(db.Text, nullable=True)  # JSON string for mock DB tables

    module = db.relationship("Module", back_populates="lessons")
    steps = db.relationship(
        "LessonStep", back_populates="lesson", order_by="LessonStep.order_index", cascade="all,delete"
    )


class LessonStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=1)
    kind = db.Column(db.String(20), nullable=False, default="mcq")
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False, default="[]")       # JSON array
    correct_answer = db.Column(db.Text, nullable=False, default="")  # JSON: id or array of ids
    explanation = db.Column(db.Text, nullable=False, default="")
    hints = db.Column(db.Text, nullable=False, default="[]")         # JSON array of strings
    code_snippet = db.Column(db.Text, nullable=True)
    code_language = db.Column(db.String(20), nullable=True)

    lesson = db.relationship("Lesson", back_populates="steps")
    progress = db.relationship("UserProgress", back_populates="step", cascade="all,delete")


class UserProgress(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "step_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey("lesson_step.id"), nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    user = db.relationship("User", back_populates="progress")
    step = db.relationship("LessonStep", back_populates="progress")


class CommunityChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    flag = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100)
    hint = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(255), nullable=True)     # Original uploaded filename
    file_size = db.Column(db.Integer, nullable=True)         # File size in bytes
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending / approved / rejected
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)

    author = db.relationship("User", foreign_keys=[author_id], backref="challenges")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])

    # Unique constraint: one solve per user per challenge
    solves = db.relationship("CommunityChallengeSolve", back_populates="challenge", cascade="all,delete")


class CommunityChallengeSolve(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("community_challenge.id"), nullable=False)
    solved_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    user = db.relationship("User")
    challenge = db.relationship("CommunityChallenge", back_populates="solves")


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="draft")  # draft / published
    cover_image = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)

    author = db.relationship("User", backref="articles")
