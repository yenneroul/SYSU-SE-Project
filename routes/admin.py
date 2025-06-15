from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, Post, AdminLog, Report, Message
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('需要管理员权限', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """超级管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            flash('需要超级管理员权限', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def log_admin_action(action, target_type=None, target_id=None, description=None):
    """记录管理员操作"""
    log = AdminLog(
        admin_id=current_user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        description=description,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """管理员控制台"""
    # 统计数据
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_messages = Message.query.count()
    pending_reports = Report.query.filter_by(status='pending').count()
    
    # 最近用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # 最近帖子
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # 最近举报
    recent_reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_posts=total_posts,
                         total_messages=total_messages,
                         pending_reports=pending_reports,
                         recent_users=recent_users,
                         recent_posts=recent_posts,
                         recent_reports=recent_reports)

@admin_bp.route('/users')
@admin_required
def users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search, role_filter=role_filter)

@admin_bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@super_admin_required
def toggle_user_active(user_id):
    """切换用户激活状态"""
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin():
        flash('不能禁用超级管理员账户', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    action = '激活用户' if user.is_active else '禁用用户'
    log_admin_action(action, 'user', user.id, f'{action}: {user.username}')
    
    flash(f'用户 {user.username} 已{action}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    """封禁用户"""
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin():
        flash('不能封禁超级管理员', 'error')
        return redirect(url_for('admin.users'))
    
    days = request.form.get('days', type=int, default=7)
    reason = request.form.get('reason', '')
    
    user.banned_until = datetime.utcnow() + timedelta(days=days)
    db.session.commit()
    
    log_admin_action('封禁用户', 'user', user.id, f'封禁 {days} 天: {reason}')
    
    flash(f'用户 {user.username} 已被封禁 {days} 天', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/posts')
@admin_required
def posts():
    """帖子管理"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Post.query
    
    if search:
        query = query.filter(Post.content.contains(search))
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/posts.html', posts=posts, search=search)

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    """删除帖子"""
    post = Post.query.get_or_404(post_id)
    reason = request.form.get('reason', '')
    
    db.session.delete(post)
    db.session.commit()
    
    log_admin_action('删除帖子', 'post', post_id, f'删除帖子: {reason}')
    
    flash('帖子已删除', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """举报管理"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')
    
    query = Report.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    reports = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/reports.html', reports=reports, status_filter=status_filter)

@admin_bp.route('/reports/<int:report_id>/handle', methods=['POST'])
@admin_required
def handle_report(report_id):
    """处理举报"""
    report = Report.query.get_or_404(report_id)
    action = request.form.get('action')  # resolve, dismiss
    
    report.status = 'resolved' if action == 'resolve' else 'dismissed'
    report.handled_by = current_user.id
    report.handled_at = datetime.utcnow()
    
    db.session.commit()
    
    log_admin_action('处理举报', 'report', report.id, f'举报状态: {report.status}')
    
    flash('举报已处理', 'success')
    return redirect(url_for('admin.reports'))

@admin_bp.route('/logs')
@admin_required
def logs():
    """操作日志"""
    page = request.args.get('page', 1, type=int)
    action_filter = request.args.get('action', '')
    
    query = AdminLog.query
    
    if action_filter:
        query = query.filter(AdminLog.action.contains(action_filter))
    
    logs = query.order_by(AdminLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/logs.html', logs=logs, action_filter=action_filter)

@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@super_admin_required
def promote_user(user_id):
    """提升用户权限"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['user', 'moderator', 'super_admin']:
        flash('无效的角色', 'error')
        return redirect(url_for('admin.users'))
    
    old_role = user.role
    user.role = new_role
    db.session.commit()
    
    log_admin_action('修改用户角色', 'user', user.id, f'{old_role} -> {new_role}')
    
    flash(f'用户 {user.username} 的角色已更新为 {new_role}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/test')
@login_required
def test():
    """测试页面 - 检查当前用户状态"""
    user_info = {
        'username': current_user.username,
        'role': getattr(current_user, 'role', 'None'),
        'is_admin': hasattr(current_user, 'is_admin') and current_user.is_admin(),
        'is_super_admin': hasattr(current_user, 'is_super_admin') and current_user.is_super_admin(),
        'is_authenticated': current_user.is_authenticated,
        'user_id': current_user.id
    }
    return f"<h1>用户状态测试</h1><pre>{user_info}</pre><a href='/'>返回首页</a>"
