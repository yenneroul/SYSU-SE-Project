from flask import Blueprint, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Post, Like
from datetime import datetime
import pytz  # 引入 pytz 库

# 定义中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')

post_bp = Blueprint('post', __name__)

@post_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    content = request.form['content']

    # 创建帖子时设置中国时间
    post = Post(
        content=content,
        user_id=current_user.id,
        created_at=datetime.now(CHINA_TZ)  # 使用中国时间
    )
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


@post_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # 检查是否为动态作者或管理员
    if post.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': '无权删除此动态'}), 403
    
    # 删除相关的点赞记录
    Like.query.filter_by(post_id=post_id).delete()
    
    # 删除动态
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '动态已删除'})