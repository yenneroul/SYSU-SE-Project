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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
        """基于标签匹配推荐用户"""
        if not self.tags:
            return []

        user_tag_ids = [tag.id for tag in self.tags]
        matching_users = User.query.join(user_tags).filter(
            user_tags.c.tag_id.in_(user_tag_ids),
            User.id != self.id
        ).distinct().limit(limit).all()

        return matching_users


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