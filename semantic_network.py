import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import jieba
import re
from itertools import combinations

def load_data(file_path):
    """加载数据文件"""
    df = pd.read_csv(file_path)
    return df

def preprocess_text(text):
    """文本预处理"""
    # 移除标点符号和特殊字符
    text = re.sub(r'[^\w\s]', '', str(text))
    # 分词
    words = jieba.lcut(text)
    # 扩展停用词列表
    stopwords = set([
        # 基础停用词
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
        '上', '也', '很', '到', '说', '要', '这', '你', '会', '着', '没有', '看', '好', 
        
        # 连接词和语气词
        '这个', '但是', '因为', '所以', '那么', '只是', '还是', '真的', '可以', '觉得',
        '什么', '这样', '这种', '还有', '不过', '就是', '现在', '可能', '已经', '知道',
        '一样', '时候', '这些', '自己', '没有', '一直', '特别', '完全', '真是', '确实',
        '一点', '应该', '比较', '其实', '如果', '但', '吧', '啊', '呢', '嘛', '哦', 
        '喔', '呀', '啦', '么', '被', '给', '让', '从', '向', '才', '过', '对', '能',
        '想', '去', '来', '做', '太', '得', '着', '过', '为', '不是', '而是', '为了',
        '甚至', '一种', '除了', '他们', '不会', '那个', '只有', '需要', '那些', '虽然',
        
        # 电影相关词汇
        '电影', '剧情', '感觉', '片子', '这部', '评分', '评论', '豆瓣', '拍摄', '导演',
        '演员', '观众', '一部', '故事', '场景', '镜头', '演技', '角色', '台词', '情节',
        '看完', '看过', '片段', '银幕', '荧幕', '电影院', '影片', '拍得', '拍的', '看得',
        '看着', '看了', '看到', '电影里', '片中', '观影', '影视',
        
        # 程度词和形容词
        '非常', '十分', '如此', '相当', '格外', '分外', '更加', '很多', '许多', '极其',
        '越来越', '稍微', '略微', '比较', '超级', '蛮', '挺', '够', '老', '都', '简直',
        '实在', '真是', '确实', '的确', '太过', '多么', '好像', '似乎', '仿佛', '难道',
        
        # 代词和指示词
        '这里', '那里', '这儿', '那儿', '这次', '那次', '这样', '那样', '这么', '那么',
        '之前', '之后', '以前', '以后', '当时', '本来', '原来', '后来', '曾经', '一直',
        '最后', '出来', '那段', '有点', '怎么',
        # 数量词
        '一些', '有些', '几个', '好几', '好多', '许多', '很多', '大量', '一点', '一下',
        '整个', '全部', '所有', '每个', '每次', '一会', '一直', '一向', '从来', '一番' 
    ])
    words = [w for w in words if w not in stopwords and len(w) > 1]
    return words

def create_semantic_network(comments, min_weight=8, top_n=80, movie_name=None):
    """创建语义网络"""
    # 为不同电影调整参数
    if movie_name == "山花烂漫时":
        min_weight = 3  # 保持原有共现阈值
        top_n = 25     # 保持原有词语数量
        weight_multiplier = 5  # 为山花烂漫时特别增加权重倍数
    else:
        min_weight = 20  # 保持原有共现阈值
        top_n = 30     # 保持原有词语数量
        weight_multiplier = 0.5  # 其他电影保持原有权重
    
    # 统计词频
    all_words = []
    for comment in comments:
        words = preprocess_text(comment)
        all_words.extend(words)
    
    word_freq = Counter(all_words)
    
    # 只保留出现频率最高的 top_n 个词
    top_words = set(word for word, freq in word_freq.most_common(top_n))
    
    # 创建网络
    G = nx.Graph()
    
    # 添加边
    word_pairs = {}
    for comment in comments:
        words = set(preprocess_text(comment)) & top_words  # 只考虑高频词
        # 统计词对共现数
        for w1, w2 in combinations(words, 2):
            if word_freq[w1] >= min_weight and word_freq[w2] >= min_weight:
                pair = tuple(sorted([w1, w2]))
                word_pairs[pair] = word_pairs.get(pair, 0) + 1
    
    # 添加边到网络
    for (w1, w2), weight in word_pairs.items():
        if weight >= min_weight:
            G.add_edge(w1, w2, weight=weight * weight_multiplier)  # 使用权重倍数
    
    return G

def draw_network(G, title):
    """绘制网络图"""
    # 创建带有透明背景的图形
    plt.figure(figsize=(20, 20), facecolor='none')  # 设置图形背景透明
    
    # 设置轴的背景透明
    ax = plt.gca()
    ax.set_facecolor('none')  # 设置轴的背景透明
    
    # 计算节点大小(基于度中心性)
    degrees = dict(nx.degree(G))
    node_size = [1 for _ in degrees.values()]
    
    # 计算边的权重
    edge_weights = [G[u][v]['weight']/4 for u, v in G.edges()]  # 调整边的宽度系数
    
    # 设置布局
    pos = nx.spring_layout(G, k=3, iterations=60)  # 增大节点间距
    
    # 绘制节点（透明度设为0以隐藏圆背景）
    nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                          node_color='white', alpha=0)
    
    # 绘制边 - 修改边的颜色
    nx.draw_networkx_edges(G, pos, width=edge_weights, 
                          alpha=0.3,  # 增加透明度使其更清晰
                          edge_color='#f681c6')  
    
    # 添加标签 - 修改字体颜色和样式
    nx.draw_networkx_labels(G, pos, 
                          font_family='Microsoft YaHei',  # 使用微软雅黑字体
                          font_size=25,
                          font_weight='bold',  # 加粗字体
                          font_color='#2c3e50')  # 设置字体颜色
    
    plt.title(title, fontsize=20, fontfamily='Microsoft YaHei', color='#2c3e50')
    plt.axis('off')
    
    # 保存图片时设置透明背景
    plt.savefig(f'{title}_semantic_network.png', 
                dpi=300, 
                bbox_inches='tight',
                transparent=True)  # 设置保存时的背景透明
    plt.close()

def main():
    # 加载数据
    df = load_data('douban_comments_20241226_1600.csv')
    
    # 按电影名称分组
    movies = df['movie'].unique()
    
    for movie in movies:
        movie_comments = df[df['movie'] == movie]['content'].tolist()
        G = create_semantic_network(movie_comments, movie_name=movie)
        draw_network(G, movie)

if __name__ == "__main__":
    main() 