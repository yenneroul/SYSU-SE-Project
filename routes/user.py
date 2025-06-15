from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Post, Tag
import os
import uuid

user_bp = Blueprint('user', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template('profile.html', user=user, posts=posts)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # 查询所有标签，用于在前端显示
    all_tags = Tag.query.all()

    # 预设头像列表
    PRESET_AVATARS = [
        '/static/avatars/presets/avatar1.svg',
        '/static/avatars/presets/avatar2.svg',
        '/static/avatars/presets/avatar3.svg',
        '/static/avatars/presets/avatar4.svg',
        '/static/avatars/presets/avatar5.svg',
        '/static/avatars/presets/avatar6.svg',
        '/static/avatars/presets/avatar7.svg',
        '/static/avatars/presets/avatar8.svg',
    ]

    if request.method == 'POST':
        try:
            # 更新个人简介
            current_user.bio = request.form.get('bio', '')

            # 更新联系方式（电话、QQ、微信）和性别
            current_user.phone = request.form.get('phone', '').strip()
            current_user.qq = request.form.get('qq', '').strip()
            current_user.wechat = request.form.get('wechat', '').strip()
            current_user.gender = request.form.get('gender')

            # 更新标签
            selected_tag_ids = request.form.getlist('tags')
            current_user.tags.clear()
            for tag_id in selected_tag_ids:
                tag = Tag.query.get(int(tag_id))
                if tag:
                    current_user.tags.append(tag)

            # 处理头像选择
            avatar_type = request.form.get('avatar_type')

            if avatar_type == 'preset':
                # 使用预设头像
                preset_avatar = request.form.get('preset_avatar')
                if preset_avatar in PRESET_AVATARS:
                    current_user.avatar_url = preset_avatar

            elif avatar_type == 'upload':
                # 处理文件上传
                if 'avatar_file' in request.files:
                    file = request.files['avatar_file']
                    if file and file.filename != '' and allowed_file(file.filename):
                        # 生成唯一文件名
                        filename = secure_filename(file.filename)
                        file_ext = filename.rsplit('.', 1)[1].lower()
                        unique_filename = str(uuid.uuid4()) + '.' + file_ext

                        # 确保上传目录存在
                        upload_dir = os.path.join(current_app.root_path, 'static/avatars/uploads')
                        if not os.path.exists(upload_dir):
                            os.makedirs(upload_dir)

                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)

                        # 删除旧头像文件（如果是上传的）
                        if current_user.avatar_url and current_user.avatar_url.startswith('/static/avatars/uploads/'):
                            old_file_path = os.path.join(current_app.root_path, current_user.avatar_url[1:])
                            if os.path.exists(old_file_path):
                                try:
                                    os.remove(old_file_path)
                                except:
                                    pass  # 忽略删除失败

                        current_user.avatar_url = '/static/avatars/uploads/' + unique_filename
                    else:
                        flash('请选择有效的图片文件（PNG, JPG, JPEG, GIF）')
                        return render_template('edit_profile.html', preset_avatars=PRESET_AVATARS, all_tags=all_tags)

            elif avatar_type == 'url':
                # 使用URL链接
                avatar_url = request.form.get('avatar_url', '').strip()
                if avatar_url:
                    current_user.avatar_url = avatar_url

            db.session.commit()
            flash('资料更新成功！')
            return redirect(url_for('user.profile', user_id=current_user.id))

        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}')
            return render_template('edit_profile.html', preset_avatars=PRESET_AVATARS, all_tags=all_tags)

    return render_template('edit_profile.html', preset_avatars=PRESET_AVATARS, all_tags=all_tags)