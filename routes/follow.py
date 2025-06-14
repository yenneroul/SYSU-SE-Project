from flask import Blueprint, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User

follow_bp = Blueprint('follow', __name__)


@follow_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'error': '不能关注自己'}), 400

    if current_user.is_following(user):
        current_user.unfollow(user)
        action = 'unfollowed'
    else:
        current_user.follow(user)
        action = 'followed'

    db.session.commit()
    return jsonify({'action': action})