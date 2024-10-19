from app import app, db
from models import Poll

def add_sample_polls():
    sample_polls = [
        {
            "question": "What's your favorite programming language?",
            "choices": ["Python", "JavaScript", "Java", "C++"]
        },
        {
            "question": "How often do you exercise?",
            "choices": ["Daily", "Few times a week", "Once a week", "Rarely"]
        },
        {
            "question": "What's your preferred work environment?",
            "choices": ["Office", "Remote", "Hybrid", "Co-working space"]
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
