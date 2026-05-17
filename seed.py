from app import app, db
from app.models import User, Profile, Interest, Story, Likes


ALL_INTERESTS = [
    "Sports",
    "Music",
    "Movies",
    "Travel",
    "Gaming",
    "Reading",
    "Cooking",
    "Fitness",
    "Art",
    "Technology",
]


DEMO_PROFILES = [
    {
        "email": "alice.demo@test.com",
        "password": "password123",
        "display_name": "Alice",
        "bio": "Computer Science student who enjoys music, cafes, and weekend trips around Perth.",
        "age": 21,
        "gender": "Female",
        "orientation": "Straight",
        "location_text": "Perth WA, Australia",
        "latitude": -31.9523,
        "longitude": 115.8613,
        "place_id": "demo_place_perth_1",
        "profile_image_path": "uploads/profile_images/alice-profile.jpg",
        "interests": ["Music", "Travel", "Cooking"],
        "stories": [
            {
                "title": "Weekend Cafe",
                "description": "Trying a new cafe in Perth.",
                "image_path": "uploads/story_images/alice-story-cafe.jpg",
                "display_order": 1,
            },
            {
                "title": "Beach Walk",
                "description": "Enjoying the sunset near Cottesloe.",
                "image_path": "uploads/story_images/alice-story-beach.jpg",
                "display_order": 2,
            },
        ],
    },
    {
        "email": "ben.demo@test.com",
        "password": "password123",
        "display_name": "Ben",
        "bio": "I like fitness, movies, and meeting new people around campus.",
        "age": 23,
        "gender": "Male",
        "orientation": "Straight",
        "location_text": "UWA, Crawley WA, Australia",
        "latitude": -31.9812,
        "longitude": 115.8199,
        "place_id": "demo_place_uwa_1",
        "profile_image_path": "uploads/profile_images/ben-profile.jpg",
        "interests": ["Fitness", "Movies", "Sports"],
        "stories": [
            {
                "title": "Gym Day",
                "description": "Morning workout before class.",
                "image_path": "uploads/story_images/ben-story-gym.jpg",
                "display_order": 1,
            },
            {
                "title": "Movie Night",
                "description": "Watching a new film with friends.",
                "image_path": "uploads/story_images/ben-story-movie.jpg",
                "display_order": 2,
            },
        ],
    },
    {
        "email": "chloe.demo@test.com",
        "password": "password123",
        "display_name": "Chloe",
        "bio": "Art lover, gamer, and weekend explorer based near Fremantle.",
        "age": 22,
        "gender": "Female",
        "orientation": "Other",
        "location_text": "Fremantle WA, Australia",
        "latitude": -32.0569,
        "longitude": 115.7439,
        "place_id": "demo_place_fremantle_1",
        "profile_image_path": "uploads/profile_images/chloe-profile.jpg",
        "interests": ["Art", "Gaming", "Technology"],
        "stories": [
            {
                "title": "Art Gallery",
                "description": "Visited a local art exhibition.",
                "image_path": "uploads/story_images/chloe-story-gallery.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "mia.demo@test.com",
        "password": "password123",
        "display_name": "Mia",
        "bio": "Enjoys reading, cooking, and quiet weekends around Subiaco.",
        "age": 20,
        "gender": "Female",
        "orientation": "Straight",
        "location_text": "Subiaco WA, Australia",
        "latitude": -31.9485,
        "longitude": 115.8265,
        "place_id": "demo_place_subiaco_1",
        "profile_image_path": "uploads/profile_images/mia-profile.jpg",
        "interests": ["Reading", "Cooking", "Music"],
        "stories": [
            {
                "title": "Bookstore Visit",
                "description": "Spent the afternoon browsing new books.",
                "image_path": "uploads/story_images/mia-story-bookstore.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "ethan.demo@test.com",
        "password": "password123",
        "display_name": "Ethan",
        "bio": "Fitness, sports, and weekend beach walks.",
        "age": 24,
        "gender": "Male",
        "orientation": "Straight",
        "location_text": "Joondalup WA, Australia",
        "latitude": -31.7445,
        "longitude": 115.7662,
        "place_id": "demo_place_joondalup_1",
        "profile_image_path": "uploads/profile_images/ethan-profile.jpg",
        "interests": ["Fitness", "Sports", "Travel"],
        "stories": [
            {
                "title": "Morning Run",
                "description": "Running near the lake before work.",
                "image_path": "uploads/story_images/ethan-story-run.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "olivia.demo@test.com",
        "password": "password123",
        "display_name": "Olivia",
        "bio": "Movie fan, technology enthusiast, and occasional gamer.",
        "age": 22,
        "gender": "Female",
        "orientation": "Straight",
        "location_text": "Northbridge WA, Australia",
        "latitude": -31.9467,
        "longitude": 115.8586,
        "place_id": "demo_place_northbridge_1",
        "profile_image_path": "uploads/profile_images/olivia-profile.jpg",
        "interests": ["Movies", "Technology", "Gaming"],
        "stories": [
            {
                "title": "Cinema Night",
                "description": "Watched a new film in the city.",
                "image_path": "uploads/story_images/olivia-story-cinema.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "noah.demo@test.com",
        "password": "password123",
        "display_name": "Noah",
        "bio": "I like art galleries, live music, and discovering new places.",
        "age": 25,
        "gender": "Male",
        "orientation": "Straight",
        "location_text": "Leederville WA, Australia",
        "latitude": -31.9368,
        "longitude": 115.8414,
        "place_id": "demo_place_leederville_1",
        "profile_image_path": "uploads/profile_images/noah-profile.jpg",
        "interests": ["Art", "Music", "Travel"],
        "stories": [
            {
                "title": "Gallery Weekend",
                "description": "Visited a small art gallery with friends.",
                "image_path": "uploads/story_images/noah-story-gallery.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "sophie.demo@test.com",
        "password": "password123",
        "display_name": "Sophie",
        "bio": "Loves cooking, fitness, and reading after work.",
        "age": 23,
        "gender": "Female",
        "orientation": "Not Specified",
        "location_text": "Victoria Park WA, Australia",
        "latitude": -31.9766,
        "longitude": 115.8964,
        "place_id": "demo_place_victoria_park_1",
        "profile_image_path": "uploads/profile_images/sophie-profile.jpg",
        "interests": ["Cooking", "Fitness", "Reading"],
        "stories": [
            {
                "title": "Home Cooking",
                "description": "Trying a new recipe on Sunday.",
                "image_path": "uploads/story_images/sophie-story-cooking.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "liam.demo@test.com",
        "password": "password123",
        "display_name": "Liam",
        "bio": "Technology student who also enjoys gaming and movies.",
        "age": 21,
        "gender": "Male",
        "orientation": "Gay",
        "location_text": "East Perth WA, Australia",
        "latitude": -31.9587,
        "longitude": 115.8756,
        "place_id": "demo_place_east_perth_1",
        "profile_image_path": "uploads/profile_images/liam-profile.jpg",
        "interests": ["Technology", "Gaming", "Movies"],
        "stories": [
            {
                "title": "Game Night",
                "description": "Playing games with friends online.",
                "image_path": "uploads/story_images/liam-story-gaming.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "grace.demo@test.com",
        "password": "password123",
        "display_name": "Grace",
        "bio": "Enjoys travel, art, and relaxing music.",
        "age": 26,
        "gender": "Female",
        "orientation": "Lesbian",
        "location_text": "South Perth WA, Australia",
        "latitude": -31.9805,
        "longitude": 115.8639,
        "place_id": "demo_place_south_perth_1",
        "profile_image_path": "uploads/profile_images/grace-profile.jpg",
        "interests": ["Travel", "Art", "Music"],
        "stories": [
            {
                "title": "River Walk",
                "description": "A quiet walk near the Swan River.",
                "image_path": "uploads/story_images/grace-story-river.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "jack.demo@test.com",
        "password": "password123",
        "display_name": "Jack",
        "bio": "Sports, fitness, and outdoor activities.",
        "age": 27,
        "gender": "Male",
        "orientation": "Straight",
        "location_text": "Scarborough WA, Australia",
        "latitude": -31.8948,
        "longitude": 115.7577,
        "place_id": "demo_place_scarborough_1",
        "profile_image_path": "uploads/profile_images/jack-profile.jpg",
        "interests": ["Sports", "Fitness", "Travel"],
        "stories": [
            {
                "title": "Outdoor Training",
                "description": "Training outside before sunset.",
                "image_path": "uploads/story_images/jack-story-training.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "ava.demo@test.com",
        "password": "password123",
        "display_name": "Ava",
        "bio": "Interested in technology, reading, and music.",
        "age": 24,
        "gender": "Female",
        "orientation": "Straight",
        "location_text": "Claremont WA, Australia",
        "latitude": -31.9813,
        "longitude": 115.7795,
        "place_id": "demo_place_claremont_1",
        "profile_image_path": "uploads/profile_images/ava-profile.jpg",
        "interests": ["Technology", "Reading", "Music"],
        "stories": [
            {
                "title": "Study Session",
                "description": "Reading and coding at a local library.",
                "image_path": "uploads/story_images/ava-story-study.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "lucas.demo@test.com",
        "password": "password123",
        "display_name": "Lucas",
        "bio": "Likes travelling, cooking, and watching movies.",
        "age": 22,
        "gender": "Male",
        "orientation": "Gay",
        "location_text": "Mount Lawley WA, Australia",
        "latitude": -31.9344,
        "longitude": 115.8716,
        "place_id": "demo_place_mount_lawley_1",
        "profile_image_path": "uploads/profile_images/lucas-profile.jpg",
        "interests": ["Travel", "Cooking", "Movies"],
        "stories": [
            {
                "title": "Dinner Night",
                "description": "Trying a new restaurant with friends.",
                "image_path": "uploads/story_images/lucas-story-dinner.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "ruby.demo@test.com",
        "password": "password123",
        "display_name": "Ruby",
        "bio": "Design student who enjoys art, music, and weekend markets.",
        "age": 20,
        "gender": "Female",
        "orientation": "Lesbian",
        "location_text": "Cottesloe WA, Australia",
        "latitude": -31.9940,
        "longitude": 115.7515,
        "place_id": "demo_place_cottesloe_1",
        "profile_image_path": "uploads/profile_images/ruby-profile.jpg",
        "interests": ["Art", "Music", "Travel"],
        "stories": [
            {
                "title": "Beach Sketching",
                "description": "Drawing near the beach in the afternoon.",
                "image_path": "uploads/story_images/ruby-story-sketching.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "harry.demo@test.com",
        "password": "password123",
        "display_name": "Harry",
        "bio": "Enjoys sports, gaming, and casual weekend hangouts.",
        "age": 24,
        "gender": "Male",
        "orientation": "Not Specified",
        "location_text": "Nedlands WA, Australia",
        "latitude": -31.9796,
        "longitude": 115.8117,
        "place_id": "demo_place_nedlands_1",
        "profile_image_path": "uploads/profile_images/harry-profile.jpg",
        "interests": ["Sports", "Gaming", "Movies"],
        "stories": [
            {
                "title": "Match Day",
                "description": "Watching a football match with friends.",
                "image_path": "uploads/story_images/harry-story-match.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "emma.demo@test.com",
        "password": "password123",
        "display_name": "Emma",
        "bio": "Food lover, travel planner, and beginner photographer.",
        "age": 25,
        "gender": "Female",
        "orientation": "Straight",
        "location_text": "Applecross WA, Australia",
        "latitude": -32.0151,
        "longitude": 115.8356,
        "place_id": "demo_place_applecross_1",
        "profile_image_path": "uploads/profile_images/emma-profile.jpg",
        "interests": ["Cooking", "Travel", "Art"],
        "stories": [
            {
                "title": "Brunch Spot",
                "description": "Found a nice brunch place by the river.",
                "image_path": "uploads/story_images/emma-story-brunch.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "daniel.demo@test.com",
        "password": "password123",
        "display_name": "Daniel",
        "bio": "Interested in technology, fitness, and science fiction movies.",
        "age": 26,
        "gender": "Male",
        "orientation": "Straight",
        "location_text": "Burswood WA, Australia",
        "latitude": -31.9618,
        "longitude": 115.8948,
        "place_id": "demo_place_burswood_1",
        "profile_image_path": "uploads/profile_images/daniel-profile.jpg",
        "interests": ["Technology", "Fitness", "Movies"],
        "stories": [
            {
                "title": "Coding Afternoon",
                "description": "Working on a small side project.",
                "image_path": "uploads/story_images/daniel-story-coding.jpg",
                "display_order": 1,
            },
        ],
    },
    {
        "email": "nina.demo@test.com",
        "password": "password123",
        "display_name": "Nina",
        "bio": "Enjoys books, music, and small live performances.",
        "age": 23,
        "gender": "Other",
        "orientation": "Other",
        "location_text": "Maylands WA, Australia",
        "latitude": -31.9308,
        "longitude": 115.8940,
        "place_id": "demo_place_maylands_1",
        "profile_image_path": "uploads/profile_images/nina-profile.jpg",
        "interests": ["Reading", "Music", "Art"],
        "stories": [
            {
                "title": "Live Music",
                "description": "A relaxing night at a local music venue.",
                "image_path": "uploads/story_images/nina-story-music.jpg",
                "display_order": 1,
            },
        ],
    },
]


DEMO_LIKES = [
    ("ben.demo@test.com", "alice.demo@test.com"),
    ("chloe.demo@test.com", "alice.demo@test.com"),
    ("mia.demo@test.com", "alice.demo@test.com"),
    ("ethan.demo@test.com", "alice.demo@test.com"),
    ("olivia.demo@test.com", "alice.demo@test.com"),
    ("noah.demo@test.com", "alice.demo@test.com"),

    ("alice.demo@test.com", "ben.demo@test.com"),
    ("chloe.demo@test.com", "ben.demo@test.com"),
    ("jack.demo@test.com", "ben.demo@test.com"),

    ("alice.demo@test.com", "grace.demo@test.com"),
    ("ruby.demo@test.com", "grace.demo@test.com"),
    ("nina.demo@test.com", "grace.demo@test.com"),

    ("liam.demo@test.com", "lucas.demo@test.com"),
    ("lucas.demo@test.com", "liam.demo@test.com"),
]


def validate_demo_profile(data):
    valid_genders = {"Male", "Female", "Other"}
    valid_orientations = {"Straight", "Gay", "Lesbian", "Other", "Not Specified"}

    if data["gender"] not in valid_genders:
        raise ValueError(f"Invalid gender for {data['email']}: {data['gender']}")

    if data["orientation"] not in valid_orientations:
        raise ValueError(f"Invalid orientation for {data['email']}: {data['orientation']}")

    invalid_interests = [
        interest for interest in data["interests"]
        if interest not in ALL_INTERESTS
    ]

    if invalid_interests:
        raise ValueError(
            f"Invalid interests for {data['email']}: {invalid_interests}"
        )


def get_or_create_interest(name):
    interest = Interest.query.filter_by(name=name).first()

    if interest is None:
        interest = Interest(name=name)
        db.session.add(interest)

    return interest


def seed_interests():
    for name in ALL_INTERESTS:
        get_or_create_interest(name)

    db.session.commit()


def seed_demo_profiles():
    seed_interests()

    for data in DEMO_PROFILES:
        validate_demo_profile(data)

        existing_user = User.query.filter_by(email=data["email"]).first()

        if existing_user:
            print(f"Skipped existing demo user: {data['email']}")
            continue

        user = User(email=data["email"])
        user.set_password(data["password"])

        profile = Profile(
            user=user,
            display_name=data["display_name"],
            bio=data["bio"],
            age=data["age"],
            gender=data["gender"],
            orientation=data["orientation"],
            location_text=data["location_text"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            place_id=data["place_id"],
            profile_image_path=data["profile_image_path"],
        )

        for interest_name in data["interests"]:
            interest = get_or_create_interest(interest_name)
            profile.interests.append(interest)

        for story_data in data["stories"]:
            story = Story(
                title=story_data["title"],
                description=story_data["description"],
                image_path=story_data["image_path"],
                display_order=story_data["display_order"],
            )
            profile.stories.append(story)

        db.session.add(user)

    db.session.commit()
    print("Demo profiles seeded successfully.")


def seed_demo_likes():
    for liker_email, liked_email in DEMO_LIKES:
        liker_user = User.query.filter_by(email=liker_email).first()
        liked_user = User.query.filter_by(email=liked_email).first()

        if not liker_user or not liked_user:
            print(f"Skipped like: {liker_email} -> {liked_email}")
            continue

        liker_profile = liker_user.profile
        liked_profile = liked_user.profile

        if not liker_profile or not liked_profile:
            print(f"Skipped like because profile is missing: {liker_email} -> {liked_email}")
            continue

        if liker_profile.id == liked_profile.id:
            print(f"Skipped self-like: {liker_email}")
            continue

        existing_like = Likes.query.filter_by(
            liker_id=liker_profile.id,
            liked_id=liked_profile.id,
        ).first()

        if existing_like:
            continue

        like = Likes(
            liker_id=liker_profile.id,
            liked_id=liked_profile.id,
        )

        db.session.add(like)

    db.session.commit()
    print("Demo likes seeded successfully.")


def seed_database():
    seed_demo_profiles()
    seed_demo_likes()


if __name__ == "__main__":
    with app.app_context():
        seed_database()