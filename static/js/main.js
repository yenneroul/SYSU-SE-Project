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
    });    // 关注功能
    const followButtons = document.querySelectorAll('.follow-btn');
    followButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            const isDiscoverPage = window.location.pathname.includes('/discover');
            
            try {
                const response = await fetch(`/follow/follow/${userId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    if (isDiscoverPage && data.action === 'followed') {
                        // 发现页面：关注后移除用户卡片
                        const userCard = this.closest('.user-card');
                        userCard.style.opacity = '0.5';
                        userCard.style.transform = 'scale(0.95)';
                        
                        setTimeout(() => {
                            userCard.remove();
                            showMessage('已关注，用户已从推荐列表中移除', 'success');
                            
                            // 检查是否还有推荐用户
                            const remainingCards = document.querySelectorAll('.user-card');
                            if (remainingCards.length === 0) {
                                // 显示空推荐状态
                                const userCardsContainer = document.querySelector('.user-cards');
                                if (userCardsContainer) {
                                    userCardsContainer.parentNode.innerHTML = `
                                        <div class="empty-discover">
                                            <div class="empty-icon">🤝</div>
                                            <h3>暂无推荐用户</h3>
                                            <p>看起来没有和你有共同兴趣的用户，或者他们都已经被你关注了！</p>
                                            <div class="empty-actions">
                                                <a href="/user/edit_profile" class="btn btn-primary">添加更多标签</a>
                                                <a href="/" class="btn btn-secondary">返回首页</a>
                                            </div>
                                        </div>
                                    `;
                                }
                            }
                        }, 300);
                    } else {
                        // 其他页面：更新按钮状态
                        if (data.action === 'followed') {
                            this.textContent = '取消关注';
                            this.style.background = '#e74c3c';
                            if (!isDiscoverPage) {
                                showMessage('关注成功', 'success');
                            }
                        } else {
                            this.textContent = '关注';
                            this.style.background = '#3498db';
                            showMessage('已取消关注', 'info');
                        }
                    }
                }
            } catch (error) {
                console.error('关注操作失败:', error);
                showMessage('操作失败，请重试', 'error');
            }
        });
    });

    // 删除动态功能
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const postId = this.dataset.postId;
            
            // 确认删除
            if (!confirm('确定要删除这条动态吗？删除后无法恢复。')) {
                return;
            }
            
            try {
                const response = await fetch(`/post/delete/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        // 找到并移除动态卡片
                        const postCard = this.closest('.post-card');
                        postCard.style.opacity = '0.5';
                        postCard.style.transform = 'scale(0.95)';
                        
                        setTimeout(() => {
                            postCard.remove();
                            showMessage('动态已删除', 'success');
                        }, 300);
                    } else {
                        showMessage(data.message || '删除失败', 'error');
                    }
                } else {
                    const data = await response.json();
                    showMessage(data.error || '删除失败', 'error');
                }
            } catch (error) {
                console.error('删除动态失败:', error);
                showMessage('删除失败，请重试', 'error');
            }
        });
    });

    // 标签选择验证（注册页面）
    const tagCheckboxes = document.querySelectorAll('input[name="tags"]');
    const submitButton = document.querySelector('button[type="submit"]');
    
    // 检查当前是否在注册页面
    const isRegisterPage = window.location.pathname.includes('/auth/register');

    if (tagCheckboxes.length > 0 && submitButton && isRegisterPage) {
        tagCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedTags = document.querySelectorAll('input[name="tags"]:checked');
                if (checkedTags.length < 1) {
                    submitButton.disabled = true;
                    submitButton.textContent = `请至少选择1个标签 (已选${checkedTags.length}个)`;
                } else {
                    submitButton.disabled = false;
                    submitButton.textContent = '注册';
                }
            });
        });

        // 初始检查
        const initialChecked = document.querySelectorAll('input[name="tags"]:checked');
        if (initialChecked.length < 1) {
            submitButton.disabled = true;
            submitButton.textContent = `请至少选择1个标签 (已选${initialChecked.length}个)`;
        }
    } 
    // 编辑资料页面的标签处理
    else if (tagCheckboxes.length > 0 && submitButton && window.location.pathname.includes('/user/edit_profile')) {
        // 为编辑资料页面的标签添加事件监听器，但不改变按钮文本
        tagCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedTags = document.querySelectorAll('input[name="tags"]:checked');
                if (checkedTags.length < 1) {
                    submitButton.disabled = true;
                    submitButton.textContent = `请至少选择1个标签 (已选${checkedTags.length}个)`;
                } else {
                    submitButton.disabled = false;
                    submitButton.textContent = '保存更改';
                }
            });
        });
        
        // 初始检查
        const initialChecked = document.querySelectorAll('input[name="tags"]:checked');
        if (initialChecked.length < 1) {
            submitButton.disabled = true;
            submitButton.textContent = `请至少选择1个标签 (已选${initialChecked.length}个)`;
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

    // 密码显示/隐藏功能
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            // 切换密码输入框的类型
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            // 切换图标样式            this.classList.toggle('hidden');
        });
    }

    // 回车发送功能
    // 发送动态 - 回车发送
    const postTextarea = document.querySelector('.post-form textarea[name="content"]');
    if (postTextarea) {
        postTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = this.closest('form');
                if (this.value.trim()) {
                    form.submit();
                }
            }
        });
    }    // 发送消息 - 回车发送 (仅用于非聊天页面的消息输入框)
    const messageTextarea = document.querySelector('textarea[name="body"]:not(.chat-input)');
    if (messageTextarea) {
        messageTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = this.closest('form');
                if (this.value.trim()) {
                    form.submit();
                }
            }
        });
    }
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

// 发动态表情选择器功能
function initPostEmojiPicker() {
    // 表情数据
    const emojiData = {
        smileys: ['😀','😃','😄','😁','😆','😅','😂','🤣','😊','😇','🙂','🙃','😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨','🧐','🤓','😎','🤩','🥳','😏','😒','😞','😔','😟','😕','🙁','☹️','😣','😖','😫','😩','🥺'],
        people: ['👶','🧒','👦','👧','🧑','👱','👨','🧔','👩','🧓','👴','👵','🙍','🙎','🙅','🙆','💁','🙋','🧏','🙇','🤦','🤷','👮','🕵️','💂','👷','🤴','👸','👳','👲','🧕','🤵','👰','🤰','🤱','👼','🎅','🤶','🦸','🦹','🧙','🧚','🧛','🧜','🧝'],
        animals: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐽','🐸','🐵','🙈','🙉','🙊','🐒','🐔','🐧','🐦','🐤','🐣','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🐛','🦋','🐌','🐞','🐜','🦟','🦗','🕷️','🦂','🐢','🐍','🦎','🦖','🦕','🐙','🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🐘','🦛','🦏','🐪','🐫','🦒','🦘','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🦙','🐐','🦌','🐕','🐩','🦮','🐈','🐓','🦃','🦚','🦜','🦢','🦩','🕊️','🐇','🦝','🦨','🦡','🦦','🦥','🐁','🐀','🐿️','🦔'],
        food: ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🥭','🍍','🥥','🥝','🍅','🍆','🥑','🥦','🥬','🥒','🌶️','🫑','🌽','🥕','🫒','🧄','🧅','🥔','🍠','🥐','🥯','🍞','🥖','🥨','🧀','🥚','🍳','🧈','🥞','🧇','🥓','🥩','🍗','🍖','🦴','🌭','🍔','🍟','🍕','🫓','🥪','🥙','🧆','🌮','🌯','🫔','🥗','🥘','🫕','🥫','🍝','🍜','🍲','🍛','🍣','🍱','🥟','🦪','🍤','🍙','🍚','🍘','🍥','🥠','🥮','🍢','🍡','🍧','🍨','🍦','🥧','🧁','🍰','🎂','🍮','🍭','🍬','🍫','🍿','🍩','🍪','🌰','🥜','🍯'],
        activities: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🪀','🏓','🏸','🏒','🏑','🥍','🏏','🪃','🥅','⛳','🪁','🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛼','🛷','⛸️','🥌','🎿','⛷️','🏂','🪂','🏋️','🤼','🤸','⛹️','🤺','🤾','🏌️','🏇','🧘','🏄','🏊','🤽','🚣','🧗','🚵','🚴','🏆','🥇','🥈','🥉','🏅','🎖️','🏵️','🎗️','🎫','🎟️','🎪','🤹','🎭','🩰','🎨','🎬','🎤','🎧','🎼','🎵','🎶','🥽','🥼','🦺','👑','🎩','🎓','🧢','⛑️','📿','💄','💍','💎'],
        travel: ['🚗','🚕','🚙','🚌','🚎','🏎️','🚓','🚑','🚒','🚐','🛻','🚚','🚛','🚜','🏍️','🛵','🚲','🛴','🛹','🛼','🚁','✈️','🛩️','🛫','🛬','🪂','💺','🚀','🛸','🚉','🚊','🚝','🚞','🚋','🚃','🚋','🚞','🚝','🚄','🚅','🚈','🚂','🚆','🚇','🚊','🚉','✈️','🛫','🛬','🛩️','💺','🚁','🚟','🚠','🚡','🛰️','🚀','🛸','🛎️','🧳','⌛','⏳','⌚','⏰','⏱️','⏲️','🕰️','🕛','🕧','🕐','🕜','🕑','🕝','🕒','🕞','🕓','🕟','🕔','🕠','🕕','🕡','🕖','🕢','🕗','🕣','🕘','🕤','🕙','🕥','🕚','🕦'],
        objects: ['⌚','📱','📲','💻','⌨️','🖥️','🖨️','🖱️','🖲️','🕹️','🗜️','💽','💾','💿','📀','📼','📷','📸','📹','🎥','📽️','🎞️','📞','☎️','📟','📠','📺','📻','🎙️','🎚️','🎛️','🧭','⏱️','⏲️','⏰','🕰️','⌛','⏳','📡','🔋','🔌','💡','🔦','🕯️','🪔','🧯','🛢️','💸','💵','💴','💶','💷','💰','💳','💎','⚖️','🧰','🔧','🔨','⚒️','🛠️','⛏️','🔩','⚙️','🧱','⛓️','🧲','🔫','💣','🧨','🪓','🔪','🗡️','⚔️','🛡️','🚬','⚰️','⚱️','🏺','🔮','📿','🧿','💈','⚗️','🔭','🔬','🕳️','🩹','🩺','💊','💉','🧬','🦠','🧫','🧪','🌡️','🧹','🧺','🧻','🚽','🚰','🚿','🛁','🛀','🧼','🪒','🧽','🧴','🛎️','🔑','🗝️','🚪','🪑','🛋️','🛏️','🛌','🧸','🖼️','🛍️','🛒','🎁','🎈','🎏','🎀','🎊','🎉','🎎','🏮','🎐','🧧','✉️','📩','📨','📧','💌','📥','📤','📦','🏷️','📪','📫','📬','📭','📮','📯','📜','📃','📄','📑','📊','📈','📉','🗒️','🗓️','📅','📆','🗑️','📇','🗃️','🗳️','🗄️','📋','📁','📂','🗂️','🗞️','📰','📓','📔','📒','📕','📗','📘','📙','📚','📖','🔖','🧷','🔗','📎','🖇️','📐','📏','🧮','📌','📍','✂️','🖊️','🖋️','✒️','🖌️','🖍️','📝','✏️','🔍','🔎','🔏','🔐','🔒','🔓'],
        symbols: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕','💞','💓','💗','💖','💘','💝','💟','☮️','✝️','☪️','🕉️','☸️','✡️','🔯','🕎','☯️','☦️','🛐','⛎','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚛️','🉑','☢️','☣️','📴','📳','🈶','🈚','🈸','🈺','🈷️','✴️','🆚','💮','🉐','㊙️','㊗️','🈴','🈵','🈹','🈲','🅰️','🅱️','🆎','🆑','🅾️','🆘','❌','⭕','🛑','⛔','📛','🚫','💯','💢','♨️','🚷','🚯','🚳','🚱','🔞','📵','🚭','❗','❕','❓','❔','‼️','⁉️','🔅','🔆','〽️','⚠️','🚸','🔱','⚜️','🔰','♻️','✅','🈯','💹','❇️','✳️','❎','🌐','💠','Ⓜ️','🌀','💤','🏧','🚾','♿','🅿️','🈳','🈂️','🛂','🛃','🛄','🛅','🚹','🚺','🚼','🚻','🚮','🎦','📶','🈁','🔣','ℹ️','🔤','🔡','🔠','🆖','🆗','🆙','🆒','🆕','🆓','0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','🔢','#️⃣','*️⃣','⏏️','▶️','⏸️','⏯️','⏹️','⏺️','⏭️','⏮️','⏩','⏪','⏫','⏬','◀️','🔼','🔽','➡️','⬅️','⬆️','⬇️','↗️','↘️','↙️','↖️','↕️','↔️','↪️','↩️','⤴️','⤵️','🔀','🔁','🔂','🔄','🔃','🎵','🎶','➕','➖','➗','✖️','♾️','💲','💱','™️','©️','®️','〰️','➰','➿','🔚','🔙','🔛','🔝','🔜','✔️','☑️','🔘','⚪','⚫','🔴','🔵','🔺','🔻','🔸','🔹','🔶','🔷','🔳','🔲','▪️','▫️','◾','◽','◼️','◻️','⬛','⬜','🔈','🔇','🔉','🔊','🔔','🔕','📣','📢','👁️‍🗨️','💬','💭','🗯️','♠️','♣️','♥️','♦️','🃏','🎴','🀄','🕐','🕑','🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛','🕜','🕝','🕞','🕟','🕠','🕡','🕢','🕣','🕤','🕥','🕦','🕧']
    };

    const postContent = document.getElementById('postContent');
    const emojiBtnPost = document.getElementById('emojiBtnPost');
    const emojiPickerPost = document.getElementById('emojiPickerPost');
    const emojiGridPost = document.getElementById('emojiGridPost');

    if (!postContent || !emojiBtnPost || !emojiPickerPost || !emojiGridPost) {
        return; // 如果页面上没有这些元素，直接返回
    }

    // 绑定表情按钮点击事件
    emojiBtnPost.addEventListener('click', function(e) {
        e.stopPropagation();
        emojiPickerPost.style.display = emojiPickerPost.style.display === 'none' ? 'block' : 'none';
        if (emojiPickerPost.style.display === 'block') {
            loadPostEmojis('smileys');
        }
    });

    // 绑定分类按钮点击事件
    emojiPickerPost.querySelectorAll('.emoji-category-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            emojiPickerPost.querySelectorAll('.emoji-category-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadPostEmojis(this.dataset.category);
        });
    });

    // 点击页面其他地方关闭表情选择器
    document.addEventListener('click', function(e) {
        if (!emojiPickerPost.contains(e.target) && e.target !== emojiBtnPost) {
            emojiPickerPost.style.display = 'none';
        }
    });

    // 加载表情
    function loadPostEmojis(category) {
        const emojis = emojiData[category] || [];
        emojiGridPost.innerHTML = '';
        
        emojis.forEach(emoji => {
            const emojiElement = document.createElement('button');
            emojiElement.className = 'emoji-item';
            emojiElement.type = 'button';
            emojiElement.textContent = emoji;
            emojiElement.addEventListener('click', function() {
                insertPostEmoji(emoji);
            });
            emojiGridPost.appendChild(emojiElement);
        });
    }

    // 插入表情到输入框
    function insertPostEmoji(emoji) {
        const start = postContent.selectionStart;
        const end = postContent.selectionEnd;
        const text = postContent.value;
        
        postContent.value = text.substring(0, start) + emoji + text.substring(end);
        postContent.setSelectionRange(start + emoji.length, start + emoji.length);
        postContent.focus();
        
        // 关闭表情选择器
        emojiPickerPost.style.display = 'none';
    }
}

// 初始化发动态表情选择器
initPostEmojiPicker();