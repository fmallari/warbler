# warbler

Twitter (X) clone 

## Features

- User signup, login, and logout
- Create and delete messages
- Follow and unfollow users
- Like and unlike messages
- View liked posts on profile pages
- Edit user profile, bio, avatar, and header image
- Search users by username
- Server-rendered templates with Flask + Jinja
- Unit and view testing with Python unittest

## Tech Stack

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- WTForms
- Jinja2
- HTML/CSS
- Bootstrap
- unittest

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Create the PostgreSQL databases
5. Seed the development database
6. Run the Flask app

git clone https://github.com/fmallari/warbler.git
<p> cd warbler</p>

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

createdb warbler
createdb warbler-test

python seed.py
flask run

## Testing

Run all tests:

```bash
python -m unittest -v

python -m unittest test_user_model.py -v
python -m unittest test_message_model.py -v
python -m unittest test_user_views.py -v
python -m unittest test_message_views.py -v
python -m unittest test_likes_views.py -v

```

### Database / schema summary

```md
## Data Model

Core models include:

- User
- Message
- Follows
- Likes
