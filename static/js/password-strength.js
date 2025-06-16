/**
 * 密码强度检测器
 * 提供实时密码强度验证和视觉反馈
 */

class PasswordStrengthChecker {
    constructor(options = {}) {
        this.options = {
            passwordInput: '#password',
            strengthContainer: '.password-strength',
            strengthBar: '.strength-bar',
            strengthText: '.strength-text',
            checksContainer: '.password-checks',
            suggestionsContainer: '.password-suggestions',
            realTimeCheck: true,
            showSuggestions: true,
            ...options
        };
        
        this.init();
    }
    
    init() {
        this.passwordInput = document.querySelector(this.options.passwordInput);
        if (!this.passwordInput) return;
        
        this.createStrengthIndicator();
        this.bindEvents();
    }
    
    createStrengthIndicator() {
        // 如果已存在强度指示器，则不重复创建
        if (document.querySelector(this.options.strengthContainer)) return;
        
        const strengthHTML = `
            <div class="password-strength">
                <div class="strength-progress">
                    <div class="strength-bar"></div>
                </div>
                <div class="strength-info">
                    <span class="strength-text">请输入密码</span>
                </div>
                <div class="password-checks"></div>
                <div class="password-suggestions"></div>
            </div>
        `;
        
        // 在密码输入框后插入强度指示器
        this.passwordInput.insertAdjacentHTML('afterend', strengthHTML);
    }
    
    bindEvents() {
        if (!this.options.realTimeCheck) return;
        
        this.passwordInput.addEventListener('input', (e) => {
            this.checkPassword(e.target.value);
        });
        
        this.passwordInput.addEventListener('focus', () => {
            this.showStrengthIndicator();
        });
    }
    
    async checkPassword(password) {
        if (!password) {
            this.updateDisplay({
                strength: 'empty',
                strength_info: { text: '请输入密码', color: '#666', progress: 0 },
                checks: {},
                suggestions: []
            });
            return;
        }
        
        try {
            // 获取用户名和邮箱（如果有的话）
            const username = document.querySelector('#username')?.value || '';
            const email = document.querySelector('#email')?.value || '';
            
            const response = await fetch('/auth/api/validate-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password: password,
                    username: username,
                    email: email
                })
            });
            
            const result = await response.json();
            this.updateDisplay(result);
            
        } catch (error) {
            console.error('密码验证请求失败:', error);
            // 降级到前端验证
            this.fallbackValidation(password);
        }
    }
    
    fallbackValidation(password) {
        // 前端基础验证（作为后备）
        const result = {
            strength: 'weak',
            strength_info: { text: '弱', color: '#fd7e14', progress: 40 },
            checks: {
                length: password.length >= 6,
                has_letter: /[a-zA-Z]/.test(password),
                has_number: /[0-9]/.test(password),
                has_upper: /[A-Z]/.test(password),
                has_lower: /[a-z]/.test(password),
                has_special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
            },
            suggestions: []
        };
        
        // 简单的强度评估
        let score = 0;
        if (result.checks.length) score += 20;
        if (result.checks.has_letter) score += 15;
        if (result.checks.has_number) score += 15;
        if (result.checks.has_upper) score += 10;
        if (result.checks.has_special) score += 15;
        
        if (score < 30) {
            result.strength_info = { text: '很弱', color: '#dc3545', progress: 20 };
        } else if (score < 50) {
            result.strength_info = { text: '弱', color: '#fd7e14', progress: 40 };
        } else if (score < 70) {
            result.strength_info = { text: '中等', color: '#ffc107', progress: 60 };
        } else {
            result.strength_info = { text: '强', color: '#28a745', progress: 80 };
        }
        
        this.updateDisplay(result);
    }
    
    updateDisplay(result) {
        this.updateStrengthBar(result.strength_info);
        this.updateChecks(result.checks);
        this.updateSuggestions(result.suggestions || []);
    }
    
    updateStrengthBar(strengthInfo) {
        const strengthBar = document.querySelector('.strength-bar');
        const strengthText = document.querySelector('.strength-text');
        
        if (strengthBar) {
            strengthBar.style.width = `${strengthInfo.progress}%`;
            strengthBar.style.backgroundColor = strengthInfo.color;
        }
        
        if (strengthText) {
            strengthText.textContent = `强度：${strengthInfo.text}`;
            strengthText.style.color = strengthInfo.color;
        }
    }
    
    updateChecks(checks) {
        const checksContainer = document.querySelector('.password-checks');
        if (!checksContainer) return;
        
        const checkItems = [
            { key: 'length', label: '至少6位字符' },
            { key: 'has_letter', label: '包含字母' },
            { key: 'has_number', label: '包含数字' },
            { key: 'has_upper', label: '包含大写字母' },
            { key: 'has_special', label: '包含特殊字符' }
        ];
        
        const checksHTML = checkItems.map(item => {
            const isChecked = checks[item.key];
            const icon = isChecked ? '✅' : '❌';
            const className = isChecked ? 'check-pass' : 'check-fail';
            return `<div class="check-item ${className}">${icon} ${item.label}</div>`;
        }).join('');
        
        checksContainer.innerHTML = checksHTML;
    }
    
    updateSuggestions(suggestions) {
        if (!this.options.showSuggestions) return;
        
        const suggestionsContainer = document.querySelector('.password-suggestions');
        if (!suggestionsContainer) return;
        
        if (suggestions.length === 0) {
            suggestionsContainer.innerHTML = '';
            return;
        }
        
        const suggestionsHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item">💡 ${suggestion}</div>`
        ).join('');
        
        suggestionsContainer.innerHTML = `
            <div class="suggestions-title">改进建议：</div>
            ${suggestionsHTML}
        `;
    }
    
    showStrengthIndicator() {
        const strengthContainer = document.querySelector('.password-strength');
        if (strengthContainer) {
            strengthContainer.style.display = 'block';
        }
    }
    
    hideStrengthIndicator() {
        const strengthContainer = document.querySelector('.password-strength');
        if (strengthContainer) {
            strengthContainer.style.display = 'none';
        }
    }
    
    // 公共方法：手动验证密码
    async validatePassword(password) {
        return await this.checkPassword(password);
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查页面是否有密码输入框
    if (document.querySelector('#password')) {
        window.passwordChecker = new PasswordStrengthChecker();
    }
});

// 导出为全局变量
window.PasswordStrengthChecker = PasswordStrengthChecker;
