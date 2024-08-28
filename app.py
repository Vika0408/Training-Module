from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)


# Model for Videos
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    filepath = db.Column(db.String(120), nullable=False)


# Model for Progress
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_watched = db.Column(db.Float, nullable=False, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    video = db.relationship('Video', backref='progress', lazy=True)


# Model for Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    progress = db.relationship('Progress', backref='user', lazy=True)


# Create database and tables
with app.app_context():
    db.create_all()

    # Add initial videos if none exist
    if not Video.query.first():
        video1 = Video(title="Introduction", filepath="static/videos/Video1.mp4")
        video2 = Video(title="Module 1", filepath="static/videos/Video2.mp4")
        video3 = Video(title="Module 2", filepath="static/videos/Video3.mp4")
        db.session.add_all([video1, video2, video3])
        db.session.commit()


# Home route
@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


@app.route('/play/<int:video_id>')
def play_video(video_id):
    video = Video.query.get_or_404(video_id)
    videos = Video.query.all()
    return render_template('index.html', videos=videos, current_video=video)


# API to get user progress
@app.route('/progress', methods=['POST'])
def get_progress():
    user_id = request.json.get('user_id')
    video_id = request.json.get('video_id')
    progress = Progress.query.filter_by(user_id=user_id, video_id=video_id).first()
    if progress:
        return jsonify({"last_watched": progress.last_watched})
    else:
        return jsonify({"last_watched": 0.0})


# API to save progress
@app.route('/save_progress', methods=['POST'])
def save_progress():
    user_id = request.json.get('user_id')
    video_id = request.json.get('video_id')
    last_watched = request.json.get('last_watched')

    progress = Progress.query.filter_by(user_id=user_id, video_id=video_id).first()
    if progress:
        progress.last_watched = last_watched
        db.session.commit()
    else:
        new_progress = Progress(user_id=user_id, video_id=video_id, last_watched=last_watched)
        db.session.add(new_progress)
        db.session.commit()

    return jsonify({"message": "Progress saved!"})


if __name__ == '__main__':
    app.run(debug=True)
