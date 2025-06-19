from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import current_user, login_required
from datetime import datetime
import pytz  # 引入 pytz 库
from sqlalchemy import desc

# 假设你的 db 和 User/Message/Conversation 模型在这些地方
from app import db
from models import User, Message, Conversation

# 定义中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')

# 定义一个名为 'message' 的蓝图
message_bp = Blueprint('message', __name__)


def find_conversation_between_users(user1, user2):
    """
    查找两个用户之间的现有对话
    """
    # 查找所有用户1参与的对话
    user1_conversations = user1.conversations
    
    # 在这些对话中找到同时包含用户2的对话
    for conversation in user1_conversations:
        if user2 in conversation.participants and len(conversation.participants) == 2:
            return conversation
    
    return None

@message_bp.route('/', methods=['GET'])
@login_required
def message_inbox():
    """
    收件箱页面，显示当前用户的所有会话列表。
    """
    # 查询当前用户参与的所有会话
    conversations = db.session.query(Conversation).filter(
        Conversation.participants.any(id=current_user.id)
    ).order_by(Conversation.last_message_at.desc()).all()

    # 为模板准备一个包含更多详细信息的数据列表
    conversations_with_details = []
    for conv in conversations:
        # 找到会话中的另一位参与者
        other_user = next((p for p in conv.participants if p.id != current_user.id), None)

        # 获取此会话的最后一条消息用于预览
        last_message = conv.messages.order_by(Message.timestamp.desc()).first()

        conversations_with_details.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message
        })

    return render_template(
        'messages/inbox.html',
        title='收件箱',
        conversations_with_details=conversations_with_details
    )

@message_bp.route('/conversation/<int:conversation_id>', methods=['GET'])
@login_required
def view_conversation(conversation_id):
    """
    查看特定会话（聊天窗口）。
    """
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation or current_user not in conversation.participants:
        abort(403)

    recipient = next((p for p in conversation.participants if p != current_user), None)    # 获取页码参数，默认为第1页
    page = request.args.get('page', 1, type=int)
    per_page = 50  # 每页显示50条消息
    
    # 分页查询消息，按时间降序
    messages_pagination = conversation.messages.order_by(Message.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 重新按时间升序排列以正确显示
    messages = list(reversed(messages_pagination.items))
      # 判断是否还有更多历史消息
    has_more = messages_pagination.has_prev

    return render_template(
        'messages/conversation.html',
        title=f'与 {recipient.username} 的对话' if recipient else '对话',
        conversation=conversation,
        messages=messages,
        recipient=recipient,
        has_more=has_more,
        current_page=page
    )


@message_bp.route('/conversation/<int:conversation_id>/send', methods=['POST'])
@login_required
def send_message_ajax(conversation_id):
    """
    AJAX发送消息，不刷新页面。
    """
    conversation = db.session.get(Conversation, conversation_id)
    if not conversation or current_user not in conversation.participants:
        return jsonify({'error': '无权限访问此对话'}), 403

    body = request.form.get('body', '').strip()
    if not body:
        return jsonify({'error': '消息内容不能为空'}), 400

    # 创建新消息
    message = Message(
        body=body,
        sender_id=current_user.id,
        conversation_id=conversation.id,
        timestamp=datetime.now(CHINA_TZ)
    )
    
    # 更新会话的最后消息时间
    conversation.last_message_at = datetime.now(CHINA_TZ)
    db.session.add(message)
    db.session.commit()

    # 返回新消息的HTML
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'body': message.body,
            'sender_username': message.sender.username,
            'timestamp': message.timestamp.strftime('%m-%d %H:%M'),
            'is_current_user': message.sender_id == current_user.id
        }
    })

@message_bp.route('/send/<string:recipient_username>', methods=['POST'])
@login_required
def send_message(recipient_username):
    """
    从用户个人资料页等处发起新的对话。
    """
    recipient = User.query.filter_by(username=recipient_username).first_or_404()
    if recipient == current_user:
        flash('你不能给自己发送消息。')
        return redirect(url_for('user.profile', user_id=recipient.id))

    body = request.form.get('body', '').strip()

    # 使用辅助函数查找现有对话
    conversation = find_conversation_between_users(current_user, recipient)
    
    if not conversation:
        # 如果没有会话，则创建一个新会话
        conversation = Conversation(last_message_at=datetime.now(CHINA_TZ))
        conversation.participants.append(current_user)
        conversation.participants.append(recipient)
        db.session.add(conversation)
        db.session.commit()

    if not body:
        return redirect(url_for('message.view_conversation', conversation_id=conversation.id))

    # 创建新消息并关联到会话
    message = Message(
        body=body,
        sender_id=current_user.id,
        conversation_id=conversation.id,
        timestamp=datetime.now(CHINA_TZ)  # 使用中国时间
    )
    # 更新会话的最后消息时间
    conversation.last_message_at = datetime.now(CHINA_TZ)  # 使用中国时间
    db.session.add(message)
    db.session.commit()

    return redirect(url_for('message.view_conversation', conversation_id=conversation.id))