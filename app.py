from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User, Tag, Post
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 文件上传配置
    app.config['UPLOAD_FOLDER'] = 'static/avatars/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # 创建必要的目录
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    preset_dir = 'static/avatars/presets'
    if not os.path.exists(preset_dir):
        os.makedirs(preset_dir)

    # 初始化扩展
    db.init_app(app)    # 初始化登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # 注册蓝图

    from routes.auth import auth_bp
    from routes.user import user_bp
    # Change import to match the blueprint name
    from routes.post import bp as post_bp
    from routes.follow import follow_bp
    from routes.message import message_bp
    from routes.admin import admin_bp
    # 注册消息蓝图，并添加 URL 前缀
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    # In create_app()
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(follow_bp, url_prefix='/follow')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # 获取关注用户的动态
            followed_users = current_user.followed.all()
            followed_user_ids = [user.id for user in followed_users]
            followed_user_ids.append(current_user.id)  # 包含自己的动态

            followed_posts = Post.query.filter(
                Post.user_id.in_(followed_user_ids)
            ).order_by(Post.created_at.desc()).limit(20).all()

            return render_template('index.html', posts=followed_posts)
        return redirect(url_for('auth.login'))

    # 发现页面 - 标签匹配
    @app.route('/discover')
    def discover():
        if current_user.is_authenticated:
            matching_users = current_user.get_matching_users()
            return render_template('discover.html', users=matching_users)
        return redirect(url_for('auth.login'))    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化标签数据
        USER_TAGS = [
            '音乐爱好者', '电影迷', '读书达人', '运动健将', '美食家',
            '旅行者', '摄影师', '程序员', '设计师', '学生',
            '创业者', '艺术家', '宠物爱好者', '游戏玩家', '健身达人'
        ]
        if Tag.query.count() == 0:
            for tag_name in USER_TAGS:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)