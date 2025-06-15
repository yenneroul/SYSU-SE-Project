// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 点赞功能
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const postId = this.dataset.postId;
            try {
                const response = await fetch(`/post/like/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    const likesCount = this.querySelector('.likes-count');
                    likesCount.textContent = data.likes_count;

                    // 添加点赞动画效果
                    this.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 200);
                }
            } catch (error) {
                console.error('点赞失败:', error);
            }
        });
    });

    // 关注功能
    const followButtons = document.querySelectorAll('.follow-btn');
    followButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            try {
                const response = await fetch(`/follow/follow/${userId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.action === 'followed') {
                        this.textContent = '取消关注';
                        this.style.background = '#e74c3c';
                    } else {
                        this.textContent = '关注';
                        this.style.background = '#3498db';
                    }
                }
            } catch (error) {
                console.error('关注操作失败:', error);
            }
        });
    });

    // 标签选择验证（注册页面）
    const tagCheckboxes = document.querySelectorAll('input[name="tags"]');
    const submitButton = document.querySelector('button[type="submit"]');

    if (tagCheckboxes.length > 0 && submitButton) {
        tagCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedTags = document.querySelectorAll('input[name="tags"]:checked');
<<<<<<< HEAD
                if (checkedTags.length < 1) {
                    submitButton.disabled = true;
                    submitButton.textContent = `请至少选择1个标签 (已选${checkedTags.length}个)`;
=======
                if (checkedTags.length < 3) {
                    submitButton.disabled = true;
                    submitButton.textContent = `请至少选择3个标签 (已选${checkedTags.length}个)`;
>>>>>>> e5735be3d1486f5e01a659050e799227020cf2e0
                } else {
                    submitButton.disabled = false;
                    submitButton.textContent = '注册';
                }
            });
        });

        // 初始检查
        const initialChecked = document.querySelectorAll('input[name="tags"]:checked');
<<<<<<< HEAD
        if (initialChecked.length < 1) {
            submitButton.disabled = true;
            submitButton.textContent = `请至少选择1个标签 (已选${initialChecked.length}个)`;
=======
        if (initialChecked.length < 3) {
            submitButton.disabled = true;
            submitButton.textContent = `请至少选择3个标签 (已选${initialChecked.length}个)`;
>>>>>>> e5735be3d1486f5e01a659050e799227020cf2e0
        }
    }

    // 图片预览功能
    const imageInputs = document.querySelectorAll('input[type="url"]');
    imageInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                // 创建图片预览
                const preview = document.createElement('img');
                preview.src = this.value;
                preview.style.maxWidth = '200px';
                preview.style.marginTop = '10px';
                preview.style.borderRadius = '5px';

                // 移除之前的预览
                const existingPreview = this.parentNode.querySelector('.image-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }

                preview.className = 'image-preview';
                this.parentNode.appendChild(preview);

                // 处理加载失败
                preview.onerror = function() {
                    this.remove();
                };
            }
        });
    });

    // 自动调整文本域高度
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
<<<<<<< HEAD
=======

    // 密码显示/隐藏功能
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            // 切换密码输入框的类型
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            // 切换图标样式
            this.classList.toggle('hidden');
        });
    }
>>>>>>> e5735be3d1486f5e01a659050e799227020cf2e0
});

// 工具函数：显示提示消息
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message flash-${type}`;
    messageDiv.textContent = message;

    const container = document.querySelector('.main-content');
    container.insertBefore(messageDiv, container.firstChild);

    // 3秒后自动隐藏
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// 格式化时间显示
function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return '刚刚';
    } else if (diff < 3600000) {
        return Math.floor(diff / 60000) + '分钟前';
    } else if (diff < 86400000) {
        return Math.floor(diff / 3600000) + '小时前';
    } else {
        return Math.floor(diff / 86400000) + '天前';
    }
}