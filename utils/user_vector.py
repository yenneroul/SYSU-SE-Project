import re
import math
from models import User, Tag

def tokenize(text):
    """简单分词并小写化"""
    return re.findall(r'\b\w+\b', text.lower())

def build_vocab(users):
    """构建所有用户简介和标签的词汇表"""
    vocab = set()
    for user in users:
        vocab.update(tokenize(user.bio or ''))
        for tag in user.tags:
            vocab.add(tag.name.lower())
    return sorted(list(vocab))

def text_to_vector(text, vocab):
    """将文本映射为词袋向量"""
    tokens = tokenize(text)
    vec = [0] * len(vocab)
    for i, word in enumerate(vocab):
        vec[i] = tokens.count(word)
    return vec

def profile_to_vector(user, vocab):
    """将用户的简介和标签转为统一向量"""
    bio_vec = text_to_vector(user.bio or '', vocab)
    tag_words = ' '.join([tag.name for tag in user.tags])
    tag_vec = text_to_vector(tag_words, vocab)
    return [b + t for b, t in zip(bio_vec, tag_vec)]

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

def update_user_vector(user, vocab):
    """生成并保存用户向量"""
    user.vector = ','.join(map(str, profile_to_vector(user, vocab)))
