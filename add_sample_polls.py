from app import app, db
from models import Poll

def add_sample_polls():
    sample_polls = [
        {
            "question": "What's your favorite programming language?",
            "choices": ["Python", "JavaScript", "Java", "C++", "Ruby"]
        },
        {
            "question": "How often do you exercise?",
            "choices": ["Daily", "Few times a week", "Once a week", "Rarely", "Never"]
        },
        {
            "question": "What's your preferred work environment?",
            "choices": ["Office", "Remote", "Hybrid", "Co-working space", "Outdoors"]
        },
        {
            "question": "Which social media platform do you use most?",
            "choices": ["Facebook", "Twitter", "Instagram", "LinkedIn", "TikTok"]
        },
        {
            "question": "What's your favorite type of movie?",
            "choices": ["Action", "Comedy", "Drama", "Sci-Fi", "Horror"]
        },
        {
            "question": "How do you prefer to read books?",
            "choices": ["Physical books", "E-books", "Audiobooks", "Mix of formats", "I don't read books"]
        },
        {
            "question": "What's your primary mode of transportation?",
            "choices": ["Car", "Public transit", "Bicycle", "Walking", "Ride-sharing"]
        },
        {
            "question": "How many hours of sleep do you usually get?",
            "choices": ["Less than 6", "6-7", "7-8", "8-9", "More than 9"]
        },
        {
            "question": "What's your favorite cuisine?",
            "choices": ["Italian", "Chinese", "Mexican", "Indian", "Japanese"]
        },
        {
            "question": "How do you usually spend your weekends?",
            "choices": ["Relaxing at home", "Outdoor activities", "Socializing", "Working", "Pursuing hobbies"]
        }
    ]

    with app.app_context():
        for poll_data in sample_polls:
            poll = Poll()
            poll.question = poll_data["question"]
            poll.choices = poll_data["choices"]
            db.session.add(poll)
        db.session.commit()
        print("Sample polls added successfully.")

if __name__ == "__main__":
    add_sample_polls()
