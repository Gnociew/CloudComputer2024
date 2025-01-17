import json
import streamlit as st
from streamlit_echarts import st_pyecharts
from pyecharts import options as opts
from pyecharts.charts import Tree
import requests
import base64

# 设置API的URL
base_url = "http://###:5000" # 替换为你的服务器地址

# 设置页面布局为宽屏模式
st.set_page_config(
    page_title="思维导图",
    page_icon="",
    layout="wide"  # 使用宽屏模式
)

# 本地图片路径
local_image_path = "111.png"  # 替换为你的本地图片路径

# 动态设置背景图片
def set_background_image(image_path):
    """通过 CSS 设置页面背景图片"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;  # 使图片覆盖整个页面
            background-position: center;  # 图片居中
            background-repeat: no-repeat;  # 不重复
            background-attachment: fixed;  # 固定背景
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.title('思维导图')

# 应用本地背景图片
set_background_image(local_image_path)

def create_mindmap(data, key):
    """创建思维导图"""
    tree = (
        Tree()
        .add(
            series_name="",  # 系列名称
            data=[data],  # 数据
            orient="LR",  # 从左到右布局
            initial_tree_depth=3,  # 初始展开深度
            layout="orthogonal",  # 正交布局
            pos_left="3%",  # 左边距
            width="65%",  # 图表宽度
            height="86%",  # 图表高度
            edge_fork_position="10%",  # 分叉点位置
            symbol_size=10,  # 节点大小
            symbol="circle",  # 节点形状为圆形
            label_opts=opts.LabelOpts(
                position="right",
                horizontal_align="left",
                vertical_align="middle",
                font_size=20,
                font_weight="bold",  # 字体加粗
                color="black",  # 字体颜色
                padding=[0, 0, 0, 0],
            ),
            leaves_opts=opts.TreeLeavesOpts(  # 叶子节点样式
                label_opts=opts.LabelOpts(
                    position="right",
                    horizontal_align="left",
                    vertical_align="middle",
                    font_size=16,
                    color="darkgreen",  # 叶子节点字体颜色
                ),
            ),
            is_expand_and_collapse=True,  # 允许展开和折叠节点
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{key}知识点思维导图",
                pos_left="center",  # 标题居中
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=30,
                    font_weight="bold",
                    color="darkblue",
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                trigger_on="mousemove",
                formatter="{b}",  # 显示节点名称
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                pos_left="right",
                feature={
                    "zoom": {"is_show": True},
                    "restore": {"is_show": True},
                    "saveAsImage": {"is_show": True},  # 添加保存为图片功能
                },
            )
        )
    )
    return tree

# 生成思维导图
def generate_mind_map(key):
    """
    向API发送请求以生成思维导图。
    
    参数:
    key (str): 生成思维导图的键。
    mode (str): 生成模式，可选值为 'naive', 'local', 'global', 'hybrid'。
    
    返回:
    dict: 包含API响应的字典，通常包括以下字段：
        - message (str): 生成的思维导图结果或错误信息。
        - code (int): HTTP状态码，200表示成功，400表示请求错误，401表示模式无效。
    """
    url = f"{base_url}/generateMindMap"
    response = requests.post(url, json={'key': key})
    print(response.json())  # 打印API返回的响应
    return response.json()["message"]

def main(key, mind_map_data):
    tree = create_mindmap(mind_map_data, key)
    st_pyecharts(
        tree,
        height="900px",
        width="100%",
        key="mindmap"
    )

if __name__ == "__main__":
    # 添加查询输入框
    key = st.text_input("请输入知识点", "光合作用")
    mind_map = None

    if st.button("生成思维导图"):
        try:
            with st.spinner('思维导图生成中...'):
                mind_map = generate_mind_map(key=key)
                if mind_map:
                    main(key, mind_map)
                else:
                    st.warning("未获取到相关思维导图")
                
        except Exception as e:
            st.error(f"发生错误：{str(e)}")
            st.exception(e)