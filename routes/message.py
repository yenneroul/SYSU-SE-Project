# In routes/message.py

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import desc

# 假设你的 db 和 User/Message/Conversation 模型在这些地方
# 请根据你的实际项目结构调整 from .app import db 这一行
from app import db
from models import User, Message, Conversation

# 1. 定义一个名为 'message' 的蓝图
# 我们用它来组织所有与消息相关的路由
message_bp = Blueprint('message', __name__)


@message_bp.route('/', methods=['GET'])
@login_required
def message_inbox():
    """
    收件箱页面，显示当前用户的所有会话列表。
    (此函数已更新，将复杂的逻辑处理移到了后端)
    """
    # 1. 查询当前用户参与的所有会话
    conversations = db.session.query(Conversation).filter(
        Conversation.participants.any(id=current_user.id)
    ).order_by(Conversation.last_message_at.desc()).all()

    # 2. 为模板准备一个包含更多详细信息的数据列表
    conversations_with_details = []
    for conv in conversations:
        # 找到会话中的另一位参与者
        other_user = next((p for p in conv.participants if p.id != current_user.id), None)

        # 获取此会话的最后一条消息用于预览
        last_message = conv.messages.order_by(Message.timestamp.desc()).first()

        # 将整理好的数据添加进列表
        conversations_with_details.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message
        })

    # 3. 将处理好的、干净的数据传递给模板
    return render_template(
        'messages/inbox.html',
        title='收件箱',
        conversations_with_details=conversations_with_details
    )


@message_bp.route('/conversation/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def view_conversation(conversation_id):
    """
    查看特定会话（聊天窗口）并处理回复。
    """
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation or current_user not in conversation.participants:
        # 如果会话不存在或用户不是参与者，则禁止访问
        abort(403)

    recipient = next((p for p in conversation.participants if p != current_user), None)

    if request.method == 'POST':
        # 处理回复消息的逻辑
        body = request.form.get('body')
        if body and recipient:
            message = Message(body=body, sender_id=current_user.id, conversation_id=conversation.id)
            # 更新会话的最后消息时间
            conversation.last_message_at = datetime.utcnow()
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('message.view_conversation', conversation_id=conversation.id))

    # 获取该会话的所有消息，按时间升序排列
    messages = conversation.messages.order_by(Message.timestamp.asc()).all()

    return render_template('messages/conversation.html',
                           title=f'与 {recipient.username} 的对话' if recipient else '对话',
                           conversation=conversation,
                           messages=messages,
                           recipient=recipient)


@message_bp.route('/send/<string:recipient_username>', methods=['POST'])
@login_required
def send_message(recipient_username):
    """
    从用户个人资料页等处发起新的对话。
    """
    recipient = User.query.filter_by(username=recipient_username).first_or_404()
    if recipient == current_user:
        flash('你不能给自己发送消息。')
        return redirect(url_for('user.profile', user_id=recipient.id))  # 假设用户个人页面的路由是 'user.profile'

    body = request.form.get('body', '').strip()

    # 检查是否已存在当前用户和接收者之间的会话
    conversation = db.session.query(Conversation).filter(
        Conversation.participants.any(id=current_user.id)    ).filter(
        Conversation.participants.any(id=recipient.id)
    ).filter(
        db.select(db.func.count(User.id)).where(User.conversations.any(id=Conversation.id)).scalar_subquery() == 2
    ).first()
    
    if not conversation:
        # 如果没有会话，则创建一个新会话
        conversation = Conversation()
        conversation.participants.append(current_user)
        conversation.participants.append(recipient)
        db.session.add(conversation)
        db.session.commit()  # 确保会话被保存并获得ID

    if not body:
        return redirect(url_for('message.view_conversation', conversation_id=conversation.id))

    # 创建新消息并关联到会话
    message = Message(body=body, sender_id=current_user.id, conversation_id=conversation.id)
    # 更新会话的最后消息时间
    conversation.last_message_at = datetime.utcnow()
    db.session.add(message)
    db.session.commit()

    return redirect(url_for('message.view_conversation', conversation_id=conversation.id))
