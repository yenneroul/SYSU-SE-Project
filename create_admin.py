#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员账户创建脚本
运行此脚本来创建第一个管理员账户
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置Flask应用上下文
from flask import Flask
from models import db, User

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temp-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    db.init_app(app)
    
    return app

def create_admin_user():
    """创建管理员账户"""
    app = create_app()
    
    with app.app_context():
        try:
            # 确保所有表都存在
            db.create_all()
            print("✅ 数据库表检查完成")
            
            # 检查是否已有超级管理员
            existing_admin = User.query.filter_by(role='super_admin').first()
            if existing_admin:
                print(f"✅ 超级管理员账户已存在：{existing_admin.username}")
                print(f"📧 邮箱：{existing_admin.email or '未设置'}")
                return existing_admin
            
            # 检查用户名是否被占用
            existing_user = User.query.filter_by(username='admin').first()
            if existing_user:
                print("⚠️ 用户名 'admin' 已被占用，将其提升为管理员...")
                existing_user.role = 'super_admin'
                existing_user.is_active = True
                existing_user.bio = '系统管理员'
                db.session.commit()
                print(f"✅ 用户 '{existing_user.username}' 已提升为超级管理员")
                return existing_user
            
            # 创建新的管理员账户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='super_admin',
                is_active=True,
                bio='系统管理员',
                avatar_url='/static/default-avatar.svg',
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("🎉 管理员账户创建成功！")
            print("=" * 50)
            print("👤 用户名：admin")
            print("🔑 密码：admin123")
            print("📧 邮箱：admin@example.com")
            print("🔐 角色：超级管理员")
            print("=" * 50)
            print("⚠️ 安全提醒：")
            print("1. 请立即登录并修改默认密码")
            print("2. 建议修改默认邮箱地址")
            print("3. 妥善保管管理员账户信息")
            print("=" * 50)
            print("🚀 使用说明：")
            print("1. 启动应用：python app.py")
            print("2. 访问：http://localhost:5000")
            print("3. 使用 admin/admin123 登录")
            print("4. 点击导航栏的管理按钮进入管理面板")
            
            return admin_user
            
        except Exception as e:
            print(f"❌ 创建管理员账户失败：{e}")
            db.session.rollback()
            return None

def show_admin_info():
    """显示管理员账户信息"""
    app = create_app()
    
    with app.app_context():
        try:
            admin = User.query.filter_by(role='super_admin').first()
            if admin:
                print("\n📋 当前管理员账户信息：")
                print(f"👤 用户名：{admin.username}")
                print(f"📧 邮箱：{admin.email or '未设置'}")
                print(f"🔐 角色：{admin.role}")
                print(f"📅 创建时间：{admin.created_at}")
                print(f"✅ 状态：{'活跃' if admin.is_active else '已禁用'}")
            else:
                print("❌ 未找到管理员账户")
        except Exception as e:
            print(f"❌ 查询管理员信息失败：{e}")

if __name__ == '__main__':
    print("🔧 管理员账户管理工具")
    print("=" * 30)
    
    # 创建管理员账户
    admin = create_admin_user()
    
    if admin:
        show_admin_info()
    
    print("\n✅ 脚本执行完成")
