from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user
from models import db, User, Tag
from werkzeug.utils import secure_filename
import os
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email', '').strip()  # 使用strip()去除空白字符
        password = request.form['password']
        gender = request.form.get('gender')
        contact_type = request.form.get('contact_type')
        contact_account = request.form.get('contact_account')
        selected_tags = request.form.getlist('tags')
        avatar_type = request.form.get('avatar_type', 'default')

        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('register.html', tags=Tag.query.all())

        # 只有当邮箱不为空时才检查重复
        if email and User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return render_template('register.html', tags=Tag.query.all())

        # 处理头像选择
        avatar_url = '/static/default-avatar.svg'  # 默认头像
        
        if avatar_type == 'preset':
            preset_avatar = request.form.get('preset_avatar')
            if preset_avatar and preset_avatar.startswith('/static/avatars/presets/'):
                avatar_url = preset_avatar
                
        elif avatar_type == 'upload':
            # 处理文件上传
            if 'avatar_file' in request.files:
                file = request.files['avatar_file']
                if file and file.filename != '':
                    # 检查文件类型
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if file_ext in allowed_extensions:
                        # 生成唯一文件名
                        filename = secure_filename(file.filename)
                        unique_filename = str(uuid.uuid4()) + '.' + file_ext
                        
                        # 确保上传目录存在
                        upload_dir = 'static/avatars/uploads'
                        if not os.path.exists(upload_dir):
                            os.makedirs(upload_dir)
                        
                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)
                        
                        avatar_url = '/' + upload_dir + '/' + unique_filename
        
        elif avatar_type == 'url':
            # 使用URL链接
            avatar_url_input = request.form.get('avatar_url', '').strip()
            if avatar_url_input:
                avatar_url = avatar_url_input

        # 创建用户，如果邮箱为空则设为None
        user = User(
            username=username,
            email=email if email else None,  # 空字符串转为None
            gender=gender.capitalize(),  # 首字母大写，与profile页面匹配
            avatar_url=avatar_url
        )
        
        # 根据联系方式类型，设置相应的字段
        if contact_type == 'qq':
            user.qq = contact_account
        elif contact_type == 'wechat':
            user.wechat = contact_account
        user.set_password(password)

        # 添加选择的标签
        for tag_id in selected_tags:
            tag = Tag.query.get(int(tag_id))
            if tag:
                user.tags.append(tag)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('注册成功！')
        return redirect(url_for('index'))

    return render_template('register.html', tags=Tag.query.all())

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))