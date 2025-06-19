
function toggleContactInput() {
    var contactType = document.getElementById("contact_type").value;
    var contactAccountInput = document.getElementById("contact_account");

    // 更新输入框的占位符
    if (contactType === "qq") {
        contactAccountInput.placeholder = "请输入QQ号";
    } else if (contactType === "wechat") {
        contactAccountInput.placeholder = "请输入微信号";
    }
    
    // 确保输入框始终显示
        contactAccountInput.style.display = "block";
        contactAccountInput.setAttribute("required", "required");
}

// 头像选择功能
function setupAvatarSelection() {
    // 处理头像类型选择
    const avatarTypeOptions = document.querySelectorAll('input[name="avatar_type"]');
    const presetAvatarsSection = document.getElementById('preset-avatars');
    const uploadSection = document.getElementById('upload-section');
    const urlSection = document.getElementById('url-section');
    
    // 为每个头像类型选项添加事件监听器
    avatarTypeOptions.forEach(option => {
        option.addEventListener('change', function() {
            // 隐藏所有区域
            presetAvatarsSection.style.display = 'none';
            uploadSection.style.display = 'none';
            urlSection.style.display = 'none';
            
            // 显示选中的区域
            if (this.value === 'preset') {
                presetAvatarsSection.style.display = 'grid';
            } else if (this.value === 'upload') {
                uploadSection.style.display = 'block';
            } else if (this.value === 'url') {
                urlSection.style.display = 'block';
            }
        });
    });
    
    // 处理预设头像选择
    const presetAvatarOptions = document.querySelectorAll('input[name="preset_avatar"]');
    presetAvatarOptions.forEach(option => {
        option.addEventListener('change', function() {
            // 移除所有预设头像的选中样式
            document.querySelectorAll('.preset-avatar').forEach(img => {
                img.style.border = '2px solid transparent';
                img.style.transform = 'scale(1)';
            });
            
            // 为选中的预设头像添加样式
            const selectedAvatar = this.nextElementSibling;
            if (selectedAvatar) {
                selectedAvatar.style.border = '2px solid #3498db';
                selectedAvatar.style.transform = 'scale(1.1)';
            }
        });
    });
    
    // 处理文件上传预览
    const avatarFileInput = document.getElementById('avatar_file');
    const uploadPreview = document.getElementById('upload-preview');
    
    if (avatarFileInput) {
        avatarFileInput.addEventListener('change', function() {
            uploadPreview.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = '头像预览';
                    uploadPreview.appendChild(img);
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    toggleContactInput();
    setupAvatarSelection();
});