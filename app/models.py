from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin


profile_interests = db.Table(
    "profile_interests",
    db.Column("profile_id", db.Integer, db.ForeignKey("profile.id"), primary_key=True),
    db.Column("interest_id", db.Integer, db.ForeignKey("interest.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    display_name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    orientation = db.Column(db.String(30), nullable=False)
    location_text = db.Column(db.String(120), index=True,nullable=False)
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    place_id = db.Column(db.String(128), nullable=False)

    profile_image_path = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", back_populates="profile")

    interests = db.relationship(
        "Interest",
        secondary=profile_interests,
        back_populates="profiles"
    )

    stories = db.relationship(
        "Story",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Story.display_order"
    )


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False, index=True)

    profiles = db.relationship(
        "Profile",
        secondary=profile_interests,
        back_populates="interests"
    )


class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    image_path = db.Column(db.String(255), nullable=False)

    display_order = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    profile = db.relationship("Profile", back_populates="stories")

    __table_args__ = (
        db.UniqueConstraint(
            "profile_id",
            "display_order",
            name="uq_profile_story_order"
        ),
    )



class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)

    profile1_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    profile2_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "profile1_id",
            "profile2_id",
            name="uq_conversation_profiles"
        ),
    )


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversation.id"),
        nullable=False
    )

    sender_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    receiver_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    body = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )