from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User, Tag, Post
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)

    # 初始化登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.post import post_bp
    from routes.follow import follow_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(follow_bp, url_prefix='/follow')

    # 主页路由
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
        return redirect(url_for('auth.login'))

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化标签数据
        if Tag.query.count() == 0:
            for tag_name in Config.USER_TAGS:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)