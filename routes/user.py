from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts.order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio', '')
        current_user.avatar_url = request.form.get('avatar_url', '')
        db.session.commit()
        return redirect(url_for('user.profile', user_id=current_user.id))

    return render_template('edit_profile.html')