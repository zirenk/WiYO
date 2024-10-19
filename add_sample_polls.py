from app import app, db
from models import Poll, Response

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
        existing_polls = Poll.query.order_by(Poll.number).all()
        
        for i, poll_data in enumerate(sample_polls, start=1):
            if i <= len(existing_polls):
                # Update existing poll
                poll = existing_polls[i-1]
                poll.question = poll_data["question"]
                poll.choices = poll_data["choices"]
            else:
                # Create new poll
                poll = Poll(number=i, question=poll_data["question"], choices=poll_data["choices"])
                db.session.add(poll)
        
        # If there are more existing polls than sample polls, remove the extra ones
        if len(existing_polls) > len(sample_polls):
            for poll in existing_polls[len(sample_polls):]:
                Response.query.filter_by(poll_id=poll.id).delete()
                db.session.delete(poll)
        
        db.session.commit()
        print(f"{len(sample_polls)} polls have been updated or added successfully.")

if __name__ == "__main__":
    add_sample_polls()
