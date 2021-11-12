from flask import current_app
from .models import User, Site


@current_app.route("/")
def index():
    user = User.query.get(2)
    site = Site.query.filter_by(user_id=user.id).first()
    return f"{site.id}) {site.title} ({site.url}) - {user.username} ({site.scrapping_time} ms)"
