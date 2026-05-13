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

    display_name = db.Column(db.String(80))
    bio = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(30))
    orientation = db.Column(db.String(30))
    location_text = db.Column(db.String(120), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    place_id = db.Column(db.String(128))

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

    @property
    def is_complete(self):
        required_fields = [
            self.display_name,
            self.age,
            self.gender,
            self.orientation,
            self.location_text,
            self.latitude,
            self.longitude,
            self.place_id,
        ]

        return all(field is not None and field != "" for field in required_fields) and len(self.interests) > 0

    @property
    def like_count(self):
        return Likes.query.filter_by(liked_id=self.id).count()

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

# Add Likes table to store like relationships between users
# In this project, user.id strictly equals to profile.id, and is a one-to-one relationship
class Likes(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)

    # The profile/user who sends the like
    liker_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    # The profile/user who receives the like
    liked_id = db.Column(
        db.Integer,
        db.ForeignKey("profile.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint(
            "liker_id",
            "liked_id",
            name="uq_like_pair"
        ),
        db.CheckConstraint(
            "liker_id != liked_id",
            name="ck_no_self_like"
        ),
        db.Index("ix_likes_liker_id", "liker_id"),
        db.Index("ix_likes_liked_id", "liked_id"),
    )