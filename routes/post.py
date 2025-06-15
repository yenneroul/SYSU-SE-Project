from flask import Blueprint, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Post, Like

post_bp = Blueprint('post', __name__)


@post_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    content = request.form['content']
    image_url = request.form.get('image_url', '')

    post = Post(content=content, image_url=image_url, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))


@post_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 检查是否已经点赞
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        post.likes_count -= 1
    else:
        # 添加点赞
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post.likes_count += 1

    db.session.commit()
    return jsonify({'likes_count': post.likes_count})