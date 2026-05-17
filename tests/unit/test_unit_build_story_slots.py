from app.helpers import build_story_slots


class StoryStub:
    def __init__(self, title, description, image_path, display_order):
        self.title = title
        self.description = description
        self.image_path = image_path
        self.display_order = display_order


def test_build_story_slots_returns_three_empty_slots_when_no_stories(monkeypatch):
    monkeypatch.setattr("app.helpers.build_story_image_url", lambda image_path: "/static/default-story.jpg")

    slots = build_story_slots([])

    assert len(slots) == 3
    for index, slot in enumerate(slots, start=1):
        assert slot["display_order"] == index
        assert slot["is_empty"] is True
        assert slot["title"] == "Add Story"
        assert slot["description"] == "Share a moment from your life."
        assert slot["image_url"] == "/static/default-story.jpg"


def test_build_story_slots_places_named_story_in_correct_slot(monkeypatch):
    monkeypatch.setattr("app.helpers.build_story_image_url", lambda image_path: f"/static/{image_path}")

    stories = [
        StoryStub(
            title="Summer Hike",
            description="A great mountain walk.",
            image_path="uploads/story_images/hike.jpg",
            display_order=2,
        )
    ]

    slots = build_story_slots(stories)

    assert len(slots) == 3
    assert slots[0]["display_order"] == 1
    assert slots[0]["is_empty"] is True
    assert slots[1]["display_order"] == 2
    assert slots[1]["is_empty"] is False
    assert slots[1]["title"] == "Summer Hike"
    assert slots[1]["description"] == "A great mountain walk."
    assert slots[1]["image_url"] == "/static/uploads/story_images/hike.jpg"
    assert slots[2]["display_order"] == 3
    assert slots[2]["is_empty"] is True


def test_build_story_slots_ignores_stories_outside_slot_range(monkeypatch):
    monkeypatch.setattr("app.helpers.build_story_image_url", lambda image_path: "/static/default-story.jpg")

    stories = [
        StoryStub(
            title="Out of Bounds",
            description="Should not appear.",
            image_path="uploads/story_images/bad.jpg",
            display_order=5,
        ),
        StoryStub(
            title="Valid Story",
            description="Only this one should appear.",
            image_path="uploads/story_images/valid.jpg",
            display_order=1,
        ),
    ]

    slots = build_story_slots(stories)

    assert slots[0]["display_order"] == 1
    assert slots[0]["is_empty"] is False
    assert slots[0]["title"] == "Valid Story"
    assert slots[1]["is_empty"] is True
    assert slots[2]["is_empty"] is True
