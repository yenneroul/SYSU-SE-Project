from flask import Blueprint, redirect
from models import db, User
from flask import render_template, request, jsonify, url_for
from flask_login import login_required, current_user
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


@follow_bp.route('/followers/<int:user_id>')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    followers = user.followers.paginate(
        page=page, per_page=20, error_out=False)

    return render_template('followers.html',
                           user=user,
                           followers=followers)


@follow_bp.route('/following/<int:user_id>')
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    following = user.followed.paginate(
        page=page, per_page=20, error_out=False)

    return render_template('following.html',
                           user=user,
                           following=following)


# 移除粉丝的API
@follow_bp.route('/remove_follower/<int:user_id>', methods=['POST'])
@login_required
def remove_follower(user_id):
    follower = User.query.get_or_404(user_id)
    if follower.is_following(current_user):
        follower.unfollow(current_user)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': '该用户未关注你'}), 400