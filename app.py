import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import jieba
import re
from itertools import combinations
from semantic_network import preprocess_text

# 设置页面配置
st.set_page_config(page_title="电影评论语义网络分析", layout="wide")

# 标题
st.title("电影评论语义网络可视化")

def create_semantic_network(comments, min_weight, top_n, weight_multiplier):
    """创建语义网络"""
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
        words = set(preprocess_text(comment)) & top_words
        for w1, w2 in combinations(words, 2):
            if word_freq[w1] >= min_weight and word_freq[w2] >= min_weight:
                pair = tuple(sorted([w1, w2]))
                word_pairs[pair] = word_pairs.get(pair, 0) + 1
    
    # 添加边到网络
    for (w1, w2), weight in word_pairs.items():
        if weight >= min_weight:
            G.add_edge(w1, w2, weight=weight * weight_multiplier)
    
    return G

def draw_network(G, edge_color='#f681c6', font_color='#2c3e50'):
    """绘制网络图"""
    plt.figure(figsize=(15, 15))
    
    # 使用最基础的字体设置
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # DejaVu Sans 是 Linux 系统常见的支持中文的字体
    plt.rcParams['axes.unicode_minus'] = False
    
    # 获取节点位置
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, edge_color=edge_color, width=2, alpha=0.5)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='white', 
                          edgecolors='black', linewidths=2)
    
    # 绘制标签时不指定特定字体
    nx.draw_networkx_labels(G, pos, 
                          font_size=25,
                          font_weight='bold',
                          font_color=font_color)
    
    plt.axis('off')
    return plt.gcf()

# 加载数据
@st.cache_data
def load_data():
    return pd.read_csv('douban_comments_20241226_1600.csv')

# 主程序
def main():
    # 设置页面标题和说明
    st.title("电影评论语义网络可视化")
    st.markdown("""
    ### 使用说明：
    1. 在左侧选择要分析的电影
    2. 调整参数以获得不同的可视化效果：
        - min_weight：控制词语间最小共现次数
        - top_n：控制保留的高频词数量
        - weight_multiplier：控制连线的粗细
        - 颜色设置：可以自定义连线和文字的颜色
    """)
    
    # 加载数据
    df = load_data()
    
    # 创建侧边栏
    st.sidebar.header("参数设置")
    
    # 电影选择
    movies = df['movie'].unique()
    selected_movie = st.sidebar.selectbox(
        "选择电影",
        movies
    )
    
    # 参数调节
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        min_weight = st.number_input(
            "最小共现次数",
            min_value=1,
            max_value=20,
            value=3
        )
        
        weight_multiplier = st.slider(
            "连线粗细倍数",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1
        )
    
    with col2:
        top_n = st.number_input(
            "高频词数量",
            min_value=10,
            max_value=100,
            value=25
        )
    
    # 颜色选择
    st.sidebar.markdown("### 颜色设置")
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        # 预设的颜色选项
        edge_colors = {
            '粉色': '#f681c6',
            '蓝色': '#1f77b4',
            '绿色': '#2ecc71',
            '紫色': '#9b59b6',
            '橙色': '#e67e22',
            '红色': '#e74c3c'
        }
        selected_edge_color = st.selectbox(
            "连线颜色",
            list(edge_colors.keys())
        )
        edge_color = edge_colors[selected_edge_color]
        
    with col4:
        font_colors = {
            '深灰蓝': '#2c3e50',
            '黑色': '#000000',
            '深蓝': '#34495e',
            '深紫': '#8e44ad',
            '深绿': '#27ae60',
            '深红': '#c0392b'
        }
        selected_font_color = st.selectbox(
            "文字颜色",
            list(font_colors.keys())
        )
        font_color = font_colors[selected_font_color]
    
    # 获取选中电影的评论
    movie_comments = df[df['movie'] == selected_movie]['content'].tolist()
    
    # 创建并显示网络图
    G = create_semantic_network(movie_comments, min_weight, top_n, weight_multiplier)
    fig = draw_network(G, edge_color, font_color)
    
    # 显示图形
    st.pyplot(fig)
    
    # 显示网络统计信息
    st.sidebar.markdown("### 网络统计")
    st.sidebar.markdown(f"节点数量: {G.number_of_nodes()}")
    st.sidebar.markdown(f"边的数量: {G.number_of_edges()}")

if __name__ == "__main__":
    main() 