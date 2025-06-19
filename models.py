from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 用户标签关联表
user_tags = db.Table('user_tags',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                     )

# 关注关系表
follows = db.Table('follows',
                   db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                   db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                   )
# 用于建立 User 和 Conversation 之间的多对多关系
# 一个用户可以参与多个会话，一个会话可以有多个用户
conversation_participants = db.Table('conversation_participants',
                                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                     db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'),
                                               primary_key=True)
                                     )


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 记录最后一条消息的时间，用于收件箱排序
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立与 Message 的一对多关系
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade="all, delete-orphan")

    # 建立与 User 的多对多关系
    participants = db.relationship('User', secondary=conversation_participants,
                                   lazy='subquery',
                                   backref=db.backref('conversations', lazy=True))

    def __repr__(self):
        return f'<Conversation {self.id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 消息内容
    body = db.Column(db.Text, nullable=False)
    # 发送时间
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # 发送者 ID
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 所属会话 ID
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

    def __repr__(self):
        return f'<Message {self.id}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True, unique=True)  # nullable=True 允许为空
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(200), default='/static/default-avatar.svg')
    # 添加向量字段
    vector = db.Column(db.Text, default='')  # 存储词向量（逗号分隔字符串）

    # 关系字段：tags = relationship('Tag', secondary=user_tags, backref='users')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(10))  # New column for gender
    contact_type = db.Column(db.String(20))  # New column for contact type (qq/wechat)
    contact_account = db.Column(db.String(100))  # New column for contact account details
    phone = db.Column(db.String(20), nullable=True)
    qq = db.Column(db.String(20), nullable=True)
    wechat = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联系方式显示设置
    show_email = db.Column(db.Boolean, default=True)
    show_qq = db.Column(db.Boolean, default=True)
    show_wechat = db.Column(db.Boolean, default=True)
    show_phone = db.Column(db.Boolean, default=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    # 关系
    tags = db.relationship('Tag', secondary=user_tags, lazy='subquery',
                           backref=db.backref('users', lazy=True))
    posts = db.relationship('Post', backref='author', lazy=True)

    # 关注关系
    followed = db.relationship('User', secondary=follows,
                               primaryjoin=(follows.c.follower_id == id),
                               secondaryjoin=(follows.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    
    

    

    # 管理员相关字段
    role = db.Column(db.String(20), default='user')  # user, moderator, super_admin
    is_active = db.Column(db.Boolean, default=True)  # 账户是否激活
    banned_until = db.Column(db.DateTime, nullable=True)  # 封禁到期时间    created_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 由哪个管理员创建

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def posts_count(self):
        """获取用户发布的动态数量"""
        return len(self.posts)
    
    @property
    def followers_count(self):
        """获取粉丝数量"""
        return self.followers.count()
    
    @property
    def followed_count(self):
        """获取关注数量"""
        return self.followed.count()

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(follows.c.followed_id == user.id).count() > 0

    def is_mutual_following(self, user):
        """检查是否互相关注"""
        return self.is_following(user) and user.is_following(self)
    
    def get_matching_users(self, limit=10):
        """基于标签匹配推荐用户，排除已关注的用户，按匹配度排序"""
        if not self.tags:
            return []

        user_tag_ids = [tag.id for tag in self.tags]
        
        # 获取已关注用户的ID列表
        followed_user_ids = [user.id for user in self.followed.all()]
        followed_user_ids.append(self.id)  # 也排除自己
        
        # 查询有共同标签的用户
        potential_users = User.query.join(user_tags).filter(
            user_tags.c.tag_id.in_(user_tag_ids),
            ~User.id.in_(followed_user_ids)  # 排除已关注的用户和自己
        ).distinct().all()
        
        # 计算每个用户的匹配分数
        user_scores = []
        for user in potential_users:
            user_tag_ids_set = {tag.id for tag in user.tags}
            current_user_tag_ids_set = set(user_tag_ids)
            
            # 计算共同标签数量
            common_tags = len(user_tag_ids_set.intersection(current_user_tag_ids_set))
            
            # 计算匹配分数（共同标签数 / 总标签数的平均值）
            total_tags = len(user_tag_ids_set.union(current_user_tag_ids_set))
            match_score = common_tags / total_tags if total_tags > 0 else 0
            
            user_scores.append((user, match_score, common_tags))
        
        # 按匹配分数降序排序，然后按共同标签数降序排序
        user_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # 返回前limit个用户
        return [user for user, score, common_tags in user_scores[:limit]]

    # 管理员权限检查方法
    def is_admin(self):
        """检查是否为管理员（版主或超级管理员）"""
        return self.role in ['moderator', 'super_admin']
    
    def is_super_admin(self):
        """检查是否为超级管理员"""
        return self.role == 'super_admin'
    
    def can_manage_users(self):
        """检查是否可以管理用户"""
        return self.role == 'super_admin'
    
    def can_manage_posts(self):
        """检查是否可以管理帖子"""
        return self.role in ['moderator', 'super_admin']
    
    def is_banned(self):
        """检查用户是否被封禁"""
        if not self.is_active:
            return True
        if self.banned_until and self.banned_until > datetime.utcnow():
            return True
        return False


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 点赞数
    likes_count = db.Column(db.Integer, default=0)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)


class AdminLog(db.Model):
    """管理员操作日志"""
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 操作类型
    target_type = db.Column(db.String(50))  # 目标类型 (user, post, etc.)
    target_id = db.Column(db.Integer)  # 目标ID
    description = db.Column(db.Text)  # 操作描述
    ip_address = db.Column(db.String(45))  # IP地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联管理员
    admin = db.relationship('User', foreign_keys=[admin_id])

    def __repr__(self):
        return f'<AdminLog {self.id}: {self.action}>'


class Report(db.Model):
    """用户举报"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reported_post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    reported_message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    reason = db.Column(db.String(100), nullable=False)  # 举报原因
    description = db.Column(db.Text)  # 详细描述
    status = db.Column(db.String(20), default='pending')  # pending, resolved, dismissed
    handled_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    handled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
      # 关联用户
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    reported_post = db.relationship('Post', foreign_keys=[reported_post_id])
    reported_message = db.relationship('Message', foreign_keys=[reported_message_id])
    handler = db.relationship('User', foreign_keys=[handled_by])

    def __repr__(self):
        return f'<Report {self.id}: {self.reason}>'