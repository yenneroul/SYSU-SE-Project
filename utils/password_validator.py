"""
密码强度检查工具
提供密码验证和强度评分功能
"""

import re
from typing import Dict, List, Tuple

class PasswordValidator:
    """密码强度验证器"""
    
    # 常见弱密码列表
    WEAK_PASSWORDS = {
        '123456', 'password', 'admin123', 'qwerty', 'asdf1234',
        '111111', 'aaaaaa', 'password123', 'admin', '123456789',
        'qwerty123', 'abc123', 'password1', '123123', 'welcome123'
    }
    
    # 键盘模式
    KEYBOARD_PATTERNS = [
        'qwerty', 'asdf', 'zxcv', 'qaz', 'wsx', 'edc',
        '123456', '654321', 'abcdef', 'fedcba'
    ]
    
    @staticmethod
    def validate_password(password: str, username: str = None, email: str = None) -> Dict:
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
            username: 用户名（可选，用于检查是否包含个人信息）
            email: 邮箱（可选，用于检查是否包含个人信息）
            
        Returns:
            Dict: 包含验证结果、强度等级、建议等信息
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'strength': 'weak',
            'score': 0,
            'checks': {
                'length': False,
                'has_letter': False,
                'has_number': False,
                'has_upper': False,
                'has_lower': False,
                'has_special': False,
                'no_common_pattern': True,
                'no_personal_info': True
            }
        }
        
        if not password:
            result['is_valid'] = False
            result['errors'].append('密码不能为空')
            return result
        
        # 1. 长度检查
        if len(password) >= 6:
            result['checks']['length'] = True
            result['score'] += 20
        else:
            result['is_valid'] = False
            result['errors'].append('密码至少需要6位字符')
        
        # 2. 字母检查
        if re.search(r'[a-zA-Z]', password):
            result['checks']['has_letter'] = True
            result['score'] += 15
        else:
            result['is_valid'] = False
            result['errors'].append('密码必须包含字母')
        
        # 3. 数字检查
        if re.search(r'[0-9]', password):
            result['checks']['has_number'] = True
            result['score'] += 15
        else:
            result['is_valid'] = False
            result['errors'].append('密码必须包含数字')
        
        # 4. 大写字母检查（加分项）
        if re.search(r'[A-Z]', password):
            result['checks']['has_upper'] = True
            result['score'] += 10
        else:
            result['suggestions'].append('建议添加大写字母以提高安全性')
        
        # 5. 小写字母检查（加分项）
        if re.search(r'[a-z]', password):
            result['checks']['has_lower'] = True
            result['score'] += 10
        else:
            result['suggestions'].append('建议添加小写字母')
        
        # 6. 特殊字符检查（加分项）
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            result['checks']['has_special'] = True
            result['score'] += 15
        else:
            result['suggestions'].append('建议添加特殊字符（如!@#$%）以增强安全性')
        
        # 7. 长度加分
        if len(password) >= 8:
            result['score'] += 10
        if len(password) >= 12:
            result['score'] += 10
        
        # 8. 常见弱密码检查
        if password.lower() in PasswordValidator.WEAK_PASSWORDS:
            result['warnings'].append('这是一个常见的弱密码，建议更换')
            result['score'] = max(0, result['score'] - 30)
            result['checks']['no_common_pattern'] = False
        
        # 9. 键盘模式检查
        password_lower = password.lower()
        for pattern in PasswordValidator.KEYBOARD_PATTERNS:
            if pattern in password_lower or pattern[::-1] in password_lower:
                result['warnings'].append('密码包含键盘序列，建议使用更复杂的组合')
                result['score'] = max(0, result['score'] - 15)
                result['checks']['no_common_pattern'] = False
                break
        
        # 10. 重复字符检查
        if PasswordValidator._has_repeated_chars(password):
            result['warnings'].append('密码包含过多重复字符')
            result['score'] = max(0, result['score'] - 10)
        
        # 11. 个人信息检查
        if username and username.lower() in password.lower():
            result['warnings'].append('密码不应包含用户名')
            result['score'] = max(0, result['score'] - 20)
            result['checks']['no_personal_info'] = False
        
        if email:
            email_prefix = email.split('@')[0].lower()
            if email_prefix in password.lower():
                result['warnings'].append('密码不应包含邮箱信息')
                result['score'] = max(0, result['score'] - 20)
                result['checks']['no_personal_info'] = False
        
        # 12. 计算强度等级
        result['strength'] = PasswordValidator._calculate_strength(result['score'])
        
        # 13. 生成改进建议
        if result['score'] < 70:
            if len(password) < 8:
                result['suggestions'].append('建议使用8位以上密码')
            if not result['checks']['has_upper']:
                result['suggestions'].append('添加大写字母可提高安全性')
            if not result['checks']['has_special']:
                result['suggestions'].append('添加特殊字符（!@#$%等）可大幅提升安全性')
        
        return result
    
    @staticmethod
    def _has_repeated_chars(password: str, max_repeat: int = 3) -> bool:
        """检查是否有过多重复字符"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count >= max_repeat:
                    return True
            else:
                count = 1
        return False
    
    @staticmethod
    def _calculate_strength(score: int) -> str:
        """根据分数计算强度等级"""
        if score < 30:
            return 'very_weak'
        elif score < 50:
            return 'weak'
        elif score < 70:
            return 'medium'
        elif score < 85:
            return 'strong'
        else:
            return 'very_strong'
    
    @staticmethod
    def get_strength_info(strength: str) -> Dict:
        """获取强度等级的详细信息"""
        strength_map = {
            'very_weak': {
                'text': '很弱',
                'color': '#dc3545',
                'progress': 20,
                'description': '密码强度很弱，容易被破解'
            },
            'weak': {
                'text': '弱',
                'color': '#fd7e14',
                'progress': 40,
                'description': '密码强度较弱，建议改进'
            },
            'medium': {
                'text': '中等',
                'color': '#ffc107',
                'progress': 60,
                'description': '密码强度中等，可以使用'
            },
            'strong': {
                'text': '强',
                'color': '#28a745',
                'progress': 80,
                'description': '密码强度良好'
            },
            'very_strong': {
                'text': '很强',
                'color': '#155724',
                'progress': 100,
                'description': '密码强度很强，安全性高'
            }
        }
        return strength_map.get(strength, strength_map['weak'])

# 便捷函数
def validate_password(password: str, username: str = None, email: str = None) -> Dict:
    """验证密码强度的便捷函数"""
    return PasswordValidator.validate_password(password, username, email)

def is_password_valid(password: str, username: str = None, email: str = None) -> bool:
    """检查密码是否满足最低要求"""
    result = PasswordValidator.validate_password(password, username, email)
    return result['is_valid']
