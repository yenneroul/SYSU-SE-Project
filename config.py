import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///social_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 用户标签选项
    USER_TAGS = [
        '音乐爱好者', '电影迷', '读书达人', '运动健将', '美食家',
        '旅行者', '摄影师', '程序员', '设计师', '学生',
        '创业者', '艺术家', '宠物爱好者', '游戏玩家', '健身达人'
    ]