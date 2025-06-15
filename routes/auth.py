from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import db, User, Tag

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

        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('register.html', tags=Tag.query.all())

        # 只有当邮箱不为空时才检查重复
        if email and User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return render_template('register.html', tags=Tag.query.all())

        # 创建用户，如果邮箱为空则设为None
        user = User(
            username=username,
            email=email if email else None,  # 空字符串转为None
            gender=gender,
            contact_type=contact_type,
            contact_account=contact_account
        )
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