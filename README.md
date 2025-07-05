# SYSU-SE-Project - 标签社交平台

## 项目概述

TagMatch 是一个基于 Flask 的现代化社交网络平台，专注于通过标签匹配连接志同道合的用户。平台采用标签相似度算法为用户推荐具有共同兴趣的朋友，并提供丰富的社交功能。本项目是中山大学软件工程课程的期末作业，完整展示了全栈开发、用户体验设计和数据库管理的综合技能。

## ✨ 核心功能

### 🔐 用户认证系统
- 安全的用户注册和登录
- 密码强度检验和安全策略
- 用户会话管理和权限控制

### 🏷️ 智能标签匹配
- **15种预设兴趣标签**：音乐爱好者、电影迷、读书达人、运动健将、美食家、旅行者、摄影师、程序员、设计师、学生、创业者、艺术家、宠物爱好者、游戏玩家、健身达人
- **多标签选择搜索**：支持同时选择多个标签进行精准匹配
- **智能推荐算法**：基于标签相似度为用户推荐志同道合的朋友
- **AJAX动态搜索**：实时搜索结果，无需刷新页面

### 💬 实时聊天系统
- 私信功能，支持与匹配用户进行即时沟通
- **表情选择器**：丰富的emoji表情支持，包含8大分类（笑脸、人物、动物、食物、活动、旅行、物品、符号）
- 历史消息加载和分页展示
- 消息状态管理和时间戳显示

### 📱 动态发布与互动
- 发布个人动态和想法
- **表情选择器集成**：发动态时可选择表情丰富内容表达
- 点赞和互动功能
- 动态搜索和筛选

### 👤 用户资料管理
- 个性化头像上传（支持预设头像和自定义上传）
- 详细资料编辑（姓名、性别、生日、联系方式等）
- 隐私设置控制（联系方式可见性配置）
- 关注/粉丝关系管理

### 🛡️ 管理员系统
- 用户管理和封禁功能
- 内容审核和举报处理
- 系统日志和统计数据

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask 3.1.1
- **数据库**: SQLAlchemy + SQLite
- **认证**: Flask-Login
- **密码安全**: Werkzeug (密码哈希)
- **时区处理**: pytz

### 前端技术栈
- **模板引擎**: Jinja2
- **样式**: CSS3 + Flexbox/Grid布局
- **交互**: 原生JavaScript (ES6+)
- **AJAX**: Fetch API
- **响应式设计**: 移动端适配

### 核心模块
- **models.py**: 数据模型定义(User, Post, Tag, Message, Conversation等)
- **routes/**: 模块化路由系统
  - `auth.py`: 用户认证
  - `user.py`: 用户管理和推荐
  - `post.py`: 动态发布
  - `message.py`: 聊天系统
  - `follow.py`: 关注关系
  - `admin.py`: 管理员功能
- **utils/**: 工具函数
  - `user_vector.py`: 用户画像算法
  - `password_validator.py`: 密码强度检验

## 📂 项目结构



```
SYSU-SE-Project/
├── app.py                     # Flask应用主入口文件
├── config.py                  # 应用配置文件
├── models.py                  # 数据模型定义(SQLAlchemy)
├── requirements.txt           # Python依赖包列表
├── create_admin.py           # 管理员账户创建脚本
├── migrate_db.py             # 数据库迁移脚本
├── FEATURES_STATUS.md        # 功能开发状态文档
├── __pycache__/              # Python字节码缓存
├── instance/                 # 实例特定配置
│   └── social_app.db         # SQLite数据库文件
├── routes/                   # 模块化路由系统
│   ├── __init__.py          # 路由包初始化
│   ├── auth.py              # 用户认证路由(登录/注册)
│   ├── user.py              # 用户管理路由(资料/推荐/搜索)
│   ├── post.py              # 动态发布路由(创建/点赞/删除)
│   ├── message.py           # 聊天系统路由(私信/会话)
│   ├── follow.py            # 关注关系路由(关注/取消关注)
│   ├── admin.py             # 管理员功能路由
│   └── __pycache__/         # 路由模块缓存
├── static/                  # 静态资源目录
│   ├── css/                 # 样式表文件
│   │   ├── style.css        # 主样式文件(统一设计风格)
│   │   └── password-strength.css  # 密码强度样式
│   ├── js/                  # JavaScript文件
│   │   ├── main.js          # 主JS文件(通用功能/表情选择器)
│   │   ├── register.js      # 注册页面专用脚本
│   │   └── password-strength.js   # 密码强度检验
│   ├── images/              # 图片资源
│   │   └── backgrounds/     # 背景图片
│   ├── avatars/             # 头像文件系统
│   │   ├── presets/         # 预设头像(8个SVG文件)
│   │   └── uploads/         # 用户上传头像
│   ├── default-avatar.svg   # 默认头像文件
│   └── default-avatar.png   # 默认头像PNG版本
├── templates/               # Jinja2模板文件
│   ├── base.html           # 基础模板(导航栏/样式引入)
│   ├── index.html          # 首页(动态展示/发布)
│   ├── login.html          # 登录页面
│   ├── register.html       # 注册页面
│   ├── discover.html       # 发现页面(刷新推荐)
│   ├── recommendations.html # 标签搜索页面(多标签匹配)
│   ├── profile.html        # 用户资料页面
│   ├── edit_profile.html   # 编辑资料页面
│   ├── followers.html      # 粉丝列表页面
│   ├── following.html      # 关注列表页面
│   ├── search_results.html # 搜索结果页面
│   ├── admin/              # 管理员页面模板
│   │   ├── base.html       # 管理员基础模板
│   │   ├── dashboard.html  # 管理员仪表板
│   │   ├── users.html      # 用户管理页面
│   │   ├── posts.html      # 内容管理页面
│   │   ├── logs.html       # 系统日志页面
│   │   └── reports.html    # 举报管理页面
│   ├── messages/           # 聊天系统模板
│   │   ├── inbox.html      # 消息收件箱
│   │   ├── conversation.html # 聊天对话页面
│   │   └── conversation_new.html # 新建对话
│   └── user/               # 用户相关页面
│       ├── security.html   # 安全设置页面
│       └── change_password.html # 修改密码页面
└── utils/                  # 工具函数模块
    ├── user_vector.py      # 用户画像和推荐算法
    ├── password_validator.py # 密码强度检验工具
    └── __pycache__/        # 工具模块缓存
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd SYSU-SE-Project
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python app.py
# 首次运行会自动创建数据库表和预设标签
```

5. **创建管理员账户**
```bash
python create_admin.py
```

6. **启动应用**
```bash
python app.py
# 访问 http://localhost:5000
```

## 💡 功能亮点

### 🎯 智能推荐系统
- **标签匹配算法**: 基于用户选择的兴趣标签计算相似度
- **双模式推荐**: 
  - `/discover` - 刷新推荐 (基于当前标签的随机推荐)
  - `/user/recommendations` - 标签搜索 (多标签精准匹配)
- **实时搜索**: AJAX无刷新搜索，即时显示匹配结果

### 😊 表情选择器系统
- **8大表情分类**: 笑脸、人物、动物、食物、活动、旅行、物品、符号
- **双重集成**: 
  - 发动态表情选择器 (index.html)
  - 聊天表情选择器 (conversation.html)
- **优化交互**: 表情按钮悬停效果、分类切换、一键插入

### 💬 聊天系统特色
- **分页消息加载**: 历史消息按需加载，提升性能
- **智能输入框**: 自动调整高度、回车发送、Shift+Enter换行
- **实时体验**: AJAX发送消息，无需页面刷新

### 🎨 现代化UI设计
- **统一视觉风格**: 注册页、推荐页、聊天页等保持一致的设计语言
- **响应式布局**: 支持桌面和移动端设备
- **卡片式设计**: 用户卡片、动态卡片、消息卡片统一风格
- **微交互动画**: 按钮悬停、加载状态、消息提示等

## 🔧 开发信息

### 数据库设计
- **用户表 (User)**: 基础信息、头像、联系方式、隐私设置
- **标签表 (Tag)**: 预设兴趣标签系统
- **用户标签关联表 (user_tags)**: 多对多关系
- **动态表 (Post)**: 用户发布的动态内容
- **消息表 (Message)**: 私信消息
- **会话表 (Conversation)**: 聊天会话管理
- **关注关系表 (follows)**: 用户关注关系

### API接口
- `POST /user/search_by_tags` - 多标签匹配搜索
- `POST /follow/follow/<user_id>` - 关注/取消关注
- `POST /post/like/<post_id>` - 点赞动态
- `POST /messages/conversation/<id>/send` - 发送消息
- `GET /user/api/refresh_recommendations` - 刷新推荐

### 技术特色
- **模块化架构**: 路由按功能模块分离，便于维护
- **安全设计**: 密码哈希、CSRF保护、权限验证
- **性能优化**: 分页加载、AJAX请求、静态资源优化
- **代码规范**: 清晰的文件结构、注释文档、错误处理

## 👥 项目团队

本项目为中山大学软件工程课程期末作业，展示了现代全栈Web开发的技术能力和工程实践。

## 📄 许可证

本项目仅用于学习和教育目的。