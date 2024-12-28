import streamlit as st
import pandas as pd
import networkx as nx
from streamlit_echarts import st_echarts
from collections import Counter
from semantic_network import preprocess_text

def create_semantic_network(comments, min_weight=2, top_n=50, weight_multiplier=1):
    """创建语义网络"""
    # 分词并统计词频
    all_words = []
    for comment in comments:
        words = preprocess_text(str(comment))
        all_words.extend(words)
    
    word_freq = Counter(all_words)
    top_words = dict(word_freq.most_common(top_n))
    
    # 创建网络
    G = nx.Graph()
    
    # 添加节点
    for word in top_words:
        G.add_node(word, size=word_freq[word])  # 添加词频作为节点大小
    
    # 添加边
    for i, comment in enumerate(comments):
        words = preprocess_text(str(comment))
        words = [w for w in words if w in top_words]
        for w1 in words:
            for w2 in words:
                if w1 < w2:
                    if G.has_edge(w1, w2):
                        G[w1][w2]['weight'] += weight_multiplier
                    else:
                        G.add_edge(w1, w2, weight=weight_multiplier)
    
    # 移除权重小于阈值的边
    edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < min_weight]
    G.remove_edges_from(edges_to_remove)
    
    return G

def draw_network(G, edge_color='#f681c6', font_color='#2c3e50', edge_scale=0.5):
    """使用 ECharts 绘制网络图"""
    # 获取最大词频作为节点大小的基准
    max_size = max(data['size'] for _, data in G.nodes(data=True))
    
    # 准备节点数据
    nodes = [{"name": node, 
             "symbolSize": 20 + (data['size'] / max_size) * 30} # 根据词频调整节点大小
             for node, data in G.nodes(data=True)]
    
    # 准备边数据，使用edge_scale来调整边的粗细
    edges = [{"source": source, 
             "target": target, 
             "lineStyle": {"color": edge_color, 
                          "width": G[source][target]['weight'] * edge_scale}} 
             for source, target in G.edges()]
    
    # 配置 ECharts 选项
    options = {
        "title": {"text": "电影评论语义网络"},
        "tooltip": {},
        "animationDurationUpdate": 1500,
        "animationEasingUpdate": "quinticInOut",
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": nodes,
            "links": edges,
            "roam": True,
            "label": {
                "show": True,
                "position": "right",
                "color": font_color,
                "fontSize": 14
            },
            "force": {
                "repulsion": 1000,
                "edgeLength": 200
            },
            "lineStyle": {
                "opacity": 0.5,
                "width": 2,
            }
        }]
    }
    
    # 显示图表
    st_echarts(options=options, height="800px")

def main():
    st.title("豆瓣电影评论语义网络分析")
    
    # 侧边栏参数设置
    st.sidebar.title("参数设置")
    min_weight = st.sidebar.slider("最小边权重", 1, 10, 2)
    top_n = st.sidebar.slider("Top N 关键词", 10, 100, 50)
    weight_multiplier = st.sidebar.slider("边权重乘数", 1, 5, 1)
    edge_scale = st.sidebar.slider("边的粗细缩放", 0.1, 1.0, 0.5, 0.1)  # 新增边的粗细调节
    edge_color = st.sidebar.color_picker("边的颜色", "#f681c6")
    font_color = st.sidebar.color_picker("字体颜色", "#2c3e50")
    
    try:
        # 读取数据
        df = pd.read_csv('douban_comments_20241226_1600.csv')
        
        # 电影选择
        movies = df['movie'].unique().tolist()
        selected_movie = st.sidebar.selectbox("选择电影", movies)
        
        # 过滤选中电影的评论
        movie_df = df[df['movie'] == selected_movie]
        movie_comments = movie_df['content'].tolist()
        
        # 创建网络
        G = create_semantic_network(movie_comments, min_weight, top_n, weight_multiplier)
        
        # 绘制网络
        draw_network(G, edge_color, font_color, edge_scale)
        
        # 显示网络统计信息
        st.sidebar.markdown("### 网络统计")
        st.sidebar.markdown(f"节点数量: {G.number_of_nodes()}")
        st.sidebar.markdown(f"边的数量: {G.number_of_edges()}")
        
    except Exception as e:
        st.error(f"读取文件时出错: {str(e)}")
        st.write("请确保文件 'douban_comments_20241226_1600.csv' 存在于仓库中，且包含所需列")

if __name__ == "__main__":
    main() 