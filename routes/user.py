from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Post, Tag
import os
import uuid

from utils.user_vector import build_vocab, update_user_vector
from utils.password_validator import validate_password
from werkzeug.security import check_password_hash

user_bp = Blueprint('user', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/api/refresh_recommendations')
@login_required
def refresh_recommendations():
    """刷新推荐用户 - 返回JSON数据"""
    matching_users = current_user.get_matching_users()
    
    users_data = []
    for user in matching_users:        # 计算共同标签
        common_tags = []
        for tag in user.tags:
            if tag in current_user.tags:
                common_tags.append({'name': tag.name, 'matched': True})
            else:
                common_tags.append({'name': tag.name, 'matched': False})
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url or '/static/default-avatar.svg',
            'posts_count': user.posts_count,
            'followed_count': user.followed_count,
            'followers_count': user.followers_count,
            'tags': common_tags,
            'is_following': current_user.is_following(user)
        })
    
    return jsonify({'users': users_data})

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
            
            # 更新联系方式（电话、QQ、微信、邮箱）和性别
            current_user.phone = request.form.get('phone', '').strip()
            current_user.qq = request.form.get('qq', '').strip()
            current_user.wechat = request.form.get('wechat', '').strip()
            current_user.email = request.form.get('email', '').strip() or None  # 空字符串转为None
            current_user.gender = request.form.get('gender') # 单选按钮，直接获取值
            
            # 更新联系方式显示设置
            current_user.show_phone = 'show_phone' in request.form
            current_user.show_qq = 'show_qq' in request.form
            current_user.show_wechat = 'show_wechat' in request.form
            current_user.show_email = 'show_email' in request.form

            # 新增：更新标签
            selected_tag_ids = request.form.getlist('tags') # 获取所有选中的标签ID列表
            current_user.tags.clear() # 清除当前用户所有标签
            for tag_id in selected_tag_ids:
                tag = Tag.query.get(tag_id)
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
                        upload_dir = 'static/avatars/uploads'
                        if not os.path.exists(upload_dir):
                            os.makedirs(upload_dir)
                        
                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)
                        
                        # 删除旧头像文件（如果是上传的）
                        if current_user.avatar_url and current_user.avatar_url.startswith('/static/avatars/uploads/'):
                            old_file_path = current_user.avatar_url[1:]  # 去掉开头的 '/'
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
                    
            # 自动更新用户画像向量（词袋模型）
            all_users = User.query.all()
            vocab = build_vocab(all_users)
            update_user_vector(current_user, vocab)

            db.session.commit()
            flash('资料更新成功！')
            return redirect(url_for('user.profile', user_id=current_user.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}')
            return render_template('edit_profile.html', preset_avatars=PRESET_AVATARS, all_tags=all_tags)

    return render_template('edit_profile.html', preset_avatars=PRESET_AVATARS, all_tags=all_tags)


@user_bp.route('/recommendations')
@login_required
def recommend_users():
    from utils.user_vector import build_vocab, profile_to_vector, cosine_similarity

    # 获取当前用户已关注的用户ID列表
    # 假设你有一个Follow模型来处理关注关系
    followed_user_ids = set()
    if hasattr(current_user, 'following'):
        followed_user_ids = {user.id for user in current_user.following}
    # 或者如果你有其他的关注关系表，比如：
    # followed_user_ids = {f.followed_id for f in Follow.query.filter_by(follower_id=current_user.id).all()}

    users = User.query.all()

    # 缓存词汇表以提高性能
    if not hasattr(current_app, 'user_vocab'):
        current_app.user_vocab = build_vocab(users)
    vocab = current_app.user_vocab

    # 生成当前用户的向量
    target_vector = profile_to_vector(current_user, vocab)

    scored_users = []
    for user in users:
        # 排除当前用户自己和已经关注的用户
        if (user.id == current_user.id or
                user.id in followed_user_ids or
                not user.vector):
            continue

        try:
            user_vec = list(map(int, user.vector.split(',')))
            # 确保向量长度匹配
            if len(user_vec) != len(target_vector):
                continue
            sim = cosine_similarity(target_vector, user_vec)
            scored_users.append((user, sim))
        except (ValueError, IndexError, AttributeError):
            # 处理向量格式错误或长度不匹配的情况
            continue

    # 按相似度排序并保留分数
    scored_users.sort(key=lambda x: x[1], reverse=True)
    users_with_similarity = scored_users[:10]

    return render_template('recommendations.html', users_with_similarity=users_with_similarity)
@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码页面"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证当前密码
        if not current_user.check_password(current_password):
            flash('当前密码错误', 'error')
            return render_template('user/change_password.html')
        
        # 验证新密码确认
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'error')
            return render_template('user/change_password.html')
        
        # 检查新密码是否与当前密码相同
        if current_user.check_password(new_password):
            flash('新密码不能与当前密码相同', 'error')
            return render_template('user/change_password.html')
        
        # 验证新密码强度
        password_result = validate_password(
            new_password, 
            current_user.username, 
            current_user.email
        )
        
        if not password_result['is_valid']:
            for error in password_result['errors']:
                flash(error, 'error')
            return render_template('user/change_password.html')
        
        # 显示警告信息（如果有）
        for warning in password_result['warnings']:
            flash(warning, 'warning')
        
        # 更新密码
        try:
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('密码修改成功！', 'success')
            
            # 可选：强制用户重新登录
            # logout_user()
            # flash('密码已修改，请重新登录', 'info')
            # return redirect(url_for('auth.login'))
            
            return redirect(url_for('user.profile', user_id=current_user.id))
            
        except Exception as e:
            db.session.rollback()
            flash('密码修改失败，请重试', 'error')
            return render_template('user/change_password.html')
    
    return render_template('user/change_password.html')

@user_bp.route('/security')
@login_required
def security_settings():
    """安全设置页面"""
    return render_template('user/security.html')
