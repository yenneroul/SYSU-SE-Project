
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

// 头像选择预览功能
function setupAvatarSelection() {
    const avatarOptions = document.querySelectorAll('input[name="avatar_choice"]');
    avatarOptions.forEach(option => {
        option.addEventListener('change', function() {
            // 移除所有选中状态的样式
            document.querySelectorAll('.avatar-preview').forEach(img => {
                img.style.transform = 'scale(1)';
                img.style.border = '2px solid transparent';
            });
            
            // 为选中的头像添加样式
            const selectedLabel = this.closest('.avatar-option').querySelector('.avatar-preview');
            if (selectedLabel) {
                selectedLabel.style.transform = 'scale(1.1)';
                selectedLabel.style.border = '2px solid #3498db';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', (event) => {
    toggleContactInput();
    setupAvatarSelection();
});