import jieba
import re

def preprocess_text(text):
    """预处理文本"""
    # 移除特殊字符
    text = re.sub(r'[^\w\s]', '', text)
    
    # 使用结巴分词
    words = jieba.lcut(text)
    
    # 移除停用词（可以根据需要添加更多停用词）
    stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '着'}
    words = [w for w in words if w not in stop_words and len(w) > 1]
    
    return words