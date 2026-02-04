try:
    import streamlit as st
    import json
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit.components.v1 as components
    STREAMLIT_AVAILABLE = True

    # 设置页面配置
    st.set_page_config(
        page_title="A股量化推荐",
        page_icon="📊",
        layout="wide"
    )
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("警告：Streamlit未安装，请运行以下命令安装：")
    print("pip install streamlit pandas plotly")
    print("然后运行：streamlit run app.py")
    exit(1)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        color: #1f77b4;
    }
    .stock-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .top-stock {
        background-color: #e8f4fd;
        border-left-color: #ff6b6b;
    }
    .subscription-section {
        background-color: #fff3cd;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def get_tradingview_symbol(stock_code):
    """根据股票代码生成TradingView符号"""
    if stock_code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{stock_code}"
    elif stock_code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{stock_code}"
    else:
        return f"SSE:{stock_code}"  # 默认SSE

def display_tradingview_chart(stock_code, stock_name):
    """显示TradingView图表"""
    symbol = get_tradingview_symbol(stock_code)

    # TradingView Widget代码
    tv_html = f"""
    <div class="tradingview-widget-container">
        <div id="tradingview_widget"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget(
        {{
        "width": "100%",
        "height": 600,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Asia/Shanghai",
        "theme": "light",
        "style": "1",
        "locale": "zh_CN",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_widget"
        }});
        </script>
    </div>
    """

    st.subheader(f"[图表] {stock_name} ({stock_code}) - TradingView图表")
    components.html(tv_html, height=650)

def main():
    # 标题
    st.markdown('<h1 class="main-header">[图表] A股量化推荐系统</h1>', unsafe_allow_html=True)

    try:
        # 读取今日推荐数据
        with open('today.json', 'r', encoding='utf-8') as f:
            today_data = json.load(f)

        today_date = today_data['date']

        # 显示更新日期
        st.info(f"[日历] 数据更新日期：{today_date}")

        # 创建三列布局
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.subheader("[冠军] Top 1 推荐")
            if today_data['top1']:
                code, name = today_data['top1'][0]
                st.markdown(f"""
                <div class="stock-card top-stock">
                    <h3 style="margin: 0; color: #ff6b6b;">{code}</h3>
                    <p style="margin: 5px 0; font-size: 16px;">{name}</p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("[亚军][季军] Top 3 推荐")
            for i, (code, name) in enumerate(today_data['top3'], 1):
                medal = "[金牌]" if i == 1 else "[银牌]" if i == 2 else "[铜牌]"
                st.markdown(f"""
                <div class="stock-card">
                    <h4 style="margin: 0;">{medal} {code}</h4>
                    <p style="margin: 5px 0;">{name}</p>
                </div>
                """, unsafe_allow_html=True)

        with col3:
            st.subheader("[列表] Top 10 推荐")
            top10_df = pd.DataFrame(today_data['top10'], columns=['代码', '名称'])
            top10_df.index = range(1, len(top10_df) + 1)
            st.dataframe(top10_df, width='stretch')

        # 股票选择器
        st.markdown("---")
        st.subheader("[放大镜] 查看股票详情")

        # 创建所有推荐股票的选项
        all_stocks = {f"{code} - {name}": (code, name) for code, name in today_data['top10']}
        selected_stock_display = st.selectbox(
            "选择要查看的股票：",
            options=list(all_stocks.keys()),
            index=0
        )

        if selected_stock_display:
            selected_code, selected_name = all_stocks[selected_stock_display]
            display_tradingview_chart(selected_code, selected_name)

        # 历史表现 - 资金曲线
        st.markdown("---")
        st.subheader("[上涨] 历史表现 - 资金曲线")

        try:
            equity_df = pd.read_csv('equity.csv')
            equity_df['date'] = pd.to_datetime(equity_df['date'])

            # 计算收益
            initial_value = equity_df['equity'].iloc[0]
            final_value = equity_df['equity'].iloc[-1]
            total_return = (final_value - initial_value) / initial_value * 100

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("初始价值", "1.0000")
            with col2:
                st.metric("当前价值", ".4f")
            with col3:
                st.metric("总收益率", ".2f")

            # 绘制资金曲线
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=equity_df['date'],
                y=equity_df['equity'],
                mode='lines+markers',
                name='资金曲线',
                line=dict(color='#1f77b4', width=2),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)'
            ))

            fig.update_layout(
                title="等权持有策略资金曲线",
                xaxis_title="日期",
                yaxis_title="资金价值",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, width='stretch')

        except FileNotFoundError:
            st.warning("[警告] 资金曲线数据文件不存在")

        # 订阅区域
        st.markdown("---")
        st.markdown("""
        <div class="subscription-section">
            <h3 style="color: #856404; margin-top: 0;">[钻石] 支持我们持续运营</h3>
            <p>如需支持模型持续运行、解锁完整历史与长期表现，可选择订阅支持。</p>
            <p style="font-size: 14px; color: #6c757d;">
            您的支持将帮助我们改进算法，为您提供更优质的量化推荐服务。
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 二维码图片占位符
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("[人民币] 微信支付")
            st.image("https://via.placeholder.com/200x200.png?text=微信支付二维码",
                    caption="微信扫码支持", width=200)

        with col2:
            st.subheader("[信用卡] 支付宝")
            st.image("https://via.placeholder.com/200x200.png?text=支付宝二维码",
                    caption="支付宝扫码支持", width=200)

        # 风险提示
        st.markdown("---")
        st.warning("""
        [警告] **风险提示：**
        - 本推荐仅供参考，不构成投资建议
        - 股票投资有风险，入市需谨慎
        - 请根据自身风险承受能力投资
        - 过往表现不代表未来收益
        """)

    except FileNotFoundError:
        st.error("[错误] 找不到today.json文件，请确保数据文件存在")
    except json.JSONDecodeError:
        st.error("[错误] today.json文件格式错误")

if __name__ == "__main__":
    main()
