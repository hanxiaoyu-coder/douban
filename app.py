import streamlit as st
import pandas as pd
import networkx as nx
from streamlit_echarts import st_echarts
from semantic_network import preprocess_text
from collections import Counter

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
        G.add_node(word)
    
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

def draw_network(G, edge_color='#f681c6', font_color='#2c3e50'):
    """使用 ECharts 绘制网络图"""
    # 准备节点数据
    nodes = [{"name": node, "symbolSize": 50} for node in G.nodes()]
    
    # 准备边数据
    edges = [{"source": source, "target": target, 
              "lineStyle": {"color": edge_color, "width": G[source][target]['weight']}} 
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
                "fontSize": 16
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
    edge_color = st.sidebar.color_picker("边的颜色", "#f681c6")
    font_color = st.sidebar.color_picker("字体颜色", "#2c3e50")
    
    # 上传文件
    uploaded_file = st.file_uploader("上传豆瓣评论数据 (CSV)", type="csv")
    
    if uploaded_file is not None:
        # 读取数据
        df = pd.read_csv(uploaded_file)
        movie_comments = df['comment'].tolist()
        
        # 创建网络
        G = create_semantic_network(movie_comments, min_weight, top_n, weight_multiplier)
        
        # 绘制网络
        draw_network(G, edge_color, font_color)
        
        # 显示网络统计信息
        st.sidebar.markdown("### 网络统计")
        st.sidebar.markdown(f"节点数量: {G.number_of_nodes()}")
        st.sidebar.markdown(f"边的数量: {G.number_of_edges()}")

if __name__ == "__main__":
    main() 