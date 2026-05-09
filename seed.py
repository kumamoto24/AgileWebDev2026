from app import app, db
from app.models import User, Profile, Interest, Story


INTEREST_OPTIONS = [
    "Sports",
    "Music",
    "Movies",
    "Travel",
    "Gaming",
    "Reading",
    "Cooking",
    "Fitness",
    "Art",
    "Technology"
]


DEMO_PROFILES = [
    {
        "email": "alice.demo@test.com",
        "password": "password123",
        "display_name": "Alice",
        "bio": "Computer Science student who enjoys music and travelling.",
        "age": 21,
        "gender": "female",
        "orientation": "straight",
        "location_text": "Perth WA, Australia",
        "latitude": -31.9523,
        "longitude": 115.8613,
        "place_id": "demo_place_perth_1",
        "profile_image_path": "uploads/demo/alice-profile.jpg",
        "interests": ["Music", "Travel", "Cooking"],
        "stories": [
            {
                "title": "Weekend Cafe",
                "description": "Trying a new cafe in Perth.",
                "image_path": "uploads/demo/alice-story-1.jpg",
                "display_order": 1
            },
            {
                "title": "Beach Walk",
                "description": "Enjoying the sunset near Cottesloe.",
                "image_path": "uploads/demo/alice-story-2.jpg",
                "display_order": 2
            }
        ]
    },
    {
        "email": "ben.demo@test.com",
        "password": "password123",
        "display_name": "Ben",
        "bio": "I like fitness, movies, and meeting new people.",
        "age": 23,
        "gender": "male",
        "orientation": "straight",
        "location_text": "UWA, Crawley WA, Australia",
        "latitude": -31.9812,
        "longitude": 115.8199,
        "place_id": "demo_place_uwa_1",
        "profile_image_path": "uploads/demo/ben-profile.jpg",
        "interests": ["Fitness", "Movies", "Sports"],
        "stories": [
            {
                "title": "Gym Day",
                "description": "Morning workout before class.",
                "image_path": "uploads/demo/ben-story-1.jpg",
                "display_order": 1
            },
            {
                "title": "Movie Night",
                "description": "Watching a new film with friends.",
                "image_path": "uploads/demo/ben-story-2.jpg",
                "display_order": 2
            }
        ]
    },
    {
        "email": "chloe.demo@test.com",
        "password": "password123",
        "display_name": "Chloe",
        "bio": "Art lover, gamer, and weekend explorer.",
        "age": 22,
        "gender": "female",
        "orientation": "other",
        "location_text": "Fremantle WA, Australia",
        "latitude": -32.0569,
        "longitude": 115.7439,
        "place_id": "demo_place_fremantle_1",
        "profile_image_path": "uploads/demo/chloe-profile.jpg",
        "interests": ["Art", "Gaming", "Technology"],
        "stories": [
            {
                "title": "Art Gallery",
                "description": "Visited a local art exhibition.",
                "image_path": "uploads/demo/chloe-story-1.jpg",
                "display_order": 1
            }
        ]
    },
        {
        "email": "mia.demo@test.com",
        "password": "password123",
        "display_name": "Mia",
        "bio": "Enjoys reading, cooking, and quiet weekends around Perth.",
        "age": 20,
        "gender": "female",
        "orientation": "straight",
        "location_text": "Subiaco WA, Australia",
        "latitude": -31.9485,
        "longitude": 115.8265,
        "place_id": "demo_place_subiaco_1",
        "profile_image_path": None,
        "interests": ["Reading", "Cooking", "Music"],
        "stories": [
            {
                "title": "Bookstore Visit",
                "description": "Spent the afternoon browsing new books.",
                "image_path": "uploads/demo/mia-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "ethan.demo@test.com",
        "password": "password123",
        "display_name": "Ethan",
        "bio": "Fitness, sports, and weekend beach walks.",
        "age": 24,
        "gender": "male",
        "orientation": "straight",
        "location_text": "Joondalup WA, Australia",
        "latitude": -31.7445,
        "longitude": 115.7662,
        "place_id": "demo_place_joondalup_1",
        "profile_image_path": None,
        "interests": ["Fitness", "Sports", "Travel"],
        "stories": [
            {
                "title": "Morning Run",
                "description": "Running near the lake before work.",
                "image_path": "uploads/demo/ethan-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "olivia.demo@test.com",
        "password": "password123",
        "display_name": "Olivia",
        "bio": "Movie fan, technology enthusiast, and occasional gamer.",
        "age": 22,
        "gender": "female",
        "orientation": "straight",
        "location_text": "Sydney NSW, Australia",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "place_id": "demo_place_sydney_1",
        "profile_image_path": None,
        "interests": ["Movies", "Technology", "Gaming"],
        "stories": [
            {
                "title": "Cinema Night",
                "description": "Watched a new film in the city.",
                "image_path": "uploads/demo/olivia-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "noah.demo@test.com",
        "password": "password123",
        "display_name": "Noah",
        "bio": "I like art galleries, music, and discovering new places.",
        "age": 25,
        "gender": "male",
        "orientation": "straight",
        "location_text": "Melbourne VIC, Australia",
        "latitude": -37.8136,
        "longitude": 144.9631,
        "place_id": "demo_place_melbourne_1",
        "profile_image_path": None,
        "interests": ["Art", "Music", "Travel"],
        "stories": [
            {
                "title": "Gallery Weekend",
                "description": "Visited a small art gallery in Melbourne.",
                "image_path": "uploads/demo/noah-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "sophie.demo@test.com",
        "password": "password123",
        "display_name": "Sophie",
        "bio": "Loves cooking, fitness, and reading after work.",
        "age": 23,
        "gender": "female",
        "orientation": "other",
        "location_text": "Brisbane QLD, Australia",
        "latitude": -27.4698,
        "longitude": 153.0251,
        "place_id": "demo_place_brisbane_1",
        "profile_image_path": None,
        "interests": ["Cooking", "Fitness", "Reading"],
        "stories": [
            {
                "title": "Home Cooking",
                "description": "Trying a new recipe on Sunday.",
                "image_path": "uploads/demo/sophie-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "liam.demo@test.com",
        "password": "password123",
        "display_name": "Liam",
        "bio": "Technology student who also enjoys gaming and movies.",
        "age": 21,
        "gender": "male",
        "orientation": "gay",
        "location_text": "Adelaide SA, Australia",
        "latitude": -34.9285,
        "longitude": 138.6007,
        "place_id": "demo_place_adelaide_1",
        "profile_image_path": None,
        "interests": ["Technology", "Gaming", "Movies"],
        "stories": [
            {
                "title": "Game Night",
                "description": "Playing games with friends online.",
                "image_path": "uploads/demo/liam-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "grace.demo@test.com",
        "password": "password123",
        "display_name": "Grace",
        "bio": "Enjoys travel, art, and relaxing music.",
        "age": 26,
        "gender": "female",
        "orientation": "lesbian",
        "location_text": "Hobart TAS, Australia",
        "latitude": -42.8821,
        "longitude": 147.3272,
        "place_id": "demo_place_hobart_1",
        "profile_image_path": None,
        "interests": ["Travel", "Art", "Music"],
        "stories": [
            {
                "title": "Harbour Walk",
                "description": "A quiet walk near the waterfront.",
                "image_path": "uploads/demo/grace-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "jack.demo@test.com",
        "password": "password123",
        "display_name": "Jack",
        "bio": "Sports, fitness, and outdoor activities.",
        "age": 27,
        "gender": "male",
        "orientation": "straight",
        "location_text": "Darwin NT, Australia",
        "latitude": -12.4634,
        "longitude": 130.8456,
        "place_id": "demo_place_darwin_1",
        "profile_image_path": None,
        "interests": ["Sports", "Fitness", "Travel"],
        "stories": [
            {
                "title": "Outdoor Training",
                "description": "Training outside before sunset.",
                "image_path": "uploads/demo/jack-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "ava.demo@test.com",
        "password": "password123",
        "display_name": "Ava",
        "bio": "Interested in technology, reading, and music.",
        "age": 24,
        "gender": "female",
        "orientation": "straight",
        "location_text": "Canberra ACT, Australia",
        "latitude": -35.2809,
        "longitude": 149.1300,
        "place_id": "demo_place_canberra_1",
        "profile_image_path": None,
        "interests": ["Technology", "Reading", "Music"],
        "stories": [
            {
                "title": "Study Session",
                "description": "Reading and coding at a local library.",
                "image_path": "uploads/demo/ava-story-1.jpg",
                "display_order": 1
            }
        ]
    },
    {
        "email": "lucas.demo@test.com",
        "password": "password123",
        "display_name": "Lucas",
        "bio": "Likes travelling, cooking, and watching movies.",
        "age": 22,
        "gender": "male",
        "orientation": "gay",
        "location_text": "Gold Coast QLD, Australia",
        "latitude": -28.0167,
        "longitude": 153.4000,
        "place_id": "demo_place_gold_coast_1",
        "profile_image_path": None,
        "interests": ["Travel", "Cooking", "Movies"],
        "stories": [
            {
                "title": "Beach Day",
                "description": "Spending the afternoon near the beach.",
                "image_path": "uploads/demo/lucas-story-1.jpg",
                "display_order": 1
            }
        ]
    }
]


def get_or_create_interest(name):
    interest = Interest.query.filter_by(name=name).first()

    if interest is None:
        interest = Interest(name=name)
        db.session.add(interest)

    return interest


def seed_interests():
    for name in INTEREST_OPTIONS:
        get_or_create_interest(name)

    db.session.commit()


def seed_demo_profiles():
    seed_interests()

    for data in DEMO_PROFILES:
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
            profile_image_path=data["profile_image_path"]
        )

        for interest_name in data["interests"]:
            interest = get_or_create_interest(interest_name)
            profile.interests.append(interest)

        for story_data in data["stories"]:
            story = Story(
                title=story_data["title"],
                description=story_data["description"],
                image_path=story_data["image_path"],
                display_order=story_data["display_order"]
            )
            profile.stories.append(story)

        db.session.add(user)

    db.session.commit()
    print("Demo profiles seeded successfully.")


if __name__ == "__main__":
    with app.app_context():
        seed_demo_profiles()