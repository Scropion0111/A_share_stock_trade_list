try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit.components.v1 as components
    import os
    from datetime import datetime
    STREAMLIT_AVAILABLE = True

    # 页面配置
    st.set_page_config(
        page_title="A股量化研究 | Academic Research",
        page_icon="📚",
        layout="centered"
    )
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("请安装必要库: pip install streamlit pandas plotly")
    exit(1)


# ==================== 合规工具函数 ====================

def format_stock_code(code):
    """补齐股票代码到6位数"""
    code_str = str(code).strip()
    return code_str.zfill(6)


def get_latest_signal_folder(base_path):
    """获取最新的研究数据文件夹"""
    if not os.path.exists(base_path):
        return None, None

    folders = [f for f in os.listdir(base_path) 
               if os.path.isdir(os.path.join(base_path, f))]
    
    if not folders:
        return None, None

    folders.sort(reverse=True)
    latest_folder = folders[0]
    
    if '_risk_on' in latest_folder:
        signal_type = 'risk_on'
    elif '_risk_off' in latest_folder:
        signal_type = 'risk_off'
    else:
        signal_type = 'unknown'
    
    return latest_folder, signal_type


def get_tradingview_symbol(stock_code):
    """生成TradingView股票代码"""
    stock_code = format_stock_code(stock_code)
    
    if stock_code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{stock_code}"
    elif stock_code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{stock_code}"
    else:
        return f"SSE:{stock_code}"


def display_chart(stock_code, stock_name):
    """显示K线图表"""
    symbol = get_tradingview_symbol(stock_code)

    tv_html = f"""
    <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
        <div id="tradingview_widget"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
        "width": "100%",
        "height": 480,
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
    
    st.markdown(f"**{stock_name}** (`{format_stock_code(stock_code)}`)")
    components.html(tv_html, height=530)


# ==================== 主程序 ====================

def main():
    # CSS样式 - 学术/研究风格
    st.markdown("""
    <style>
    /* 限制宽度 */
    .block-container {
        max-width: 850px !important;
        padding-top: 1.5rem !important;
    }
    
    /* 学术风格标题 */
    .main-title {
        font-size: 1.8em;
        font-weight: 600;
        text-align: center;
        margin-bottom: 5px;
        color: #2c3e50;
    }
    
    .subtitle {
        font-size: 14px;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* 信号卡片 - 中性表述 */
    .signal-card {
        padding: 18px 22px;
        border-radius: 12px;
        margin: 15px 0;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    
    .risk-on {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-color: #6c757d;
    }
    
    .risk-off {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-color: #6c757d;
    }
    
    .signal-card h3 {
        font-size: 16px;
        margin-bottom: 6px;
        color: #495057;
    }
    
    .signal-card p {
        font-size: 13px;
        color: #6c757d;
        margin: 0;
        line-height: 1.5;
    }
    
    /* 股票卡片 */
    .stock-item {
        background: #fafafa;
        padding: 14px 16px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #eee;
    }
    
    .stock-item:hover {
        background: #f5f5f5;
    }
    
    /* 研究数据表格 */
    .data-table {
        font-size: 13px;
    }
    
    /* 免责声明区域 */
    .disclaimer-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 15px 18px;
        margin: 20px 0;
        font-size: 12px;
        color: #6c757d;
        line-height: 1.7;
    }
    
    .disclaimer-box strong {
        color: #495057;
    }
    
    /* 订阅区域 - 克制风格 */
    .subscription-box {
        background: #fff;
        border: 2px dashed #dee2e6;
        border-radius: 12px;
        padding: 20px;
        margin: 25px 0;
        text-align: center;
    }
    
    .subscription-box h4 {
        color: #495057;
        margin-bottom: 10px;
        font-size: 15px;
    }
    
    .subscription-box p {
        color: #6c757d;
        font-size: 13px;
        margin: 0;
    }
    
    /* 二维码区域 */
    .qr-section {
        text-align: center;
        padding: 15px;
        background: #fafafa;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .qr-section h5 {
        font-size: 14px;
        color: #495057;
        margin-bottom: 10px;
    }
    
    /* 风险提示 */
    .risk-warning {
        background: #f8f9fa;
        border-left: 3px solid #6c757d;
        padding: 12px 15px;
        margin: 15px 0;
        font-size: 12px;
        color: #6c757d;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        padding: 0 16px;
        background: #f0f0f0;
        font-size: 13px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #e9ecef;
        color: #495057;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: #fafafa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    
    .metric-card .label {
        font-size: 12px;
        color: #6c757d;
        margin-bottom: 5px;
    }
    
    .metric-card .value {
        font-size: 18px;
        font-weight: 600;
        color: #495057;
    }
    </style>
    """, unsafe_allow_html=True)

    # 标题
    st.markdown('<h1 class="main-title">📚 A股量化研究数据</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Quantitative Research Data | 仅供学术研究参考</p>', unsafe_allow_html=True)

    # ==================== 免责声明（顶部） ====================
    st.markdown("""
    <div class="disclaimer-box">
        <strong>📌 研究说明</strong><br>
        本网站提供的数据和分析仅用于<strong>学术研究</strong>目的，不构成任何形式的投资建议、股票推荐或交易指导。
        历史数据不代表未来表现，请独立判断，理性研究。
    </div>
    """, unsafe_allow_html=True)

    # ==================== 读取数据 ====================
    base_path = r"C:\Users\Administrator\A_share_index\daily_signals"
    
    try:
        latest_folder, signal_type = get_latest_signal_folder(base_path)
        
        if latest_folder is None:
            st.error(f"未找到研究数据文件夹: {base_path}")
            return

        folder_path = os.path.join(base_path, latest_folder)
        
        try:
            date_str = latest_folder.split('_')[0]
            display_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y年%m月%d日')
        except:
            display_date = latest_folder

        csv_path = os.path.join(folder_path, 'trade_list_top10.csv')
        
        if not os.path.exists(csv_path):
            st.error(f"未找到数据文件: {csv_path}")
            return

        df = pd.read_csv(csv_path)
        
        if 'symbol' not in df.columns or 'score' not in df.columns:
            st.error("数据格式异常，缺少必要字段")
            return

        df_top10 = df.head(10).copy()
        df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)

        if 'name' in df_top10.columns:
            stock_names = df_top10['name'].tolist()
        else:
            stock_names = df_top10['symbol'].tolist()

        # ==================== 市场状态（中性描述） ====================
        
        st.markdown(f"**数据更新**: {display_date} | 研究样本周期: 近20日因子评分")
        
        if signal_type == 'risk_on':
            st.markdown("""
            <div class="signal-card risk-on">
                <h3>📊 近期市场特征：风险偏好评分偏高</h3>
                <p>模型因子显示市场波动率下降，动量因子表现相对强势。<br>此为统计观察结果，不预测未来走势。</p>
            </div>
            """, unsafe_allow_html=True)
        elif signal_type == 'risk_off':
            st.markdown("""
            <div class="signal-card risk-off">
                <h3>📊 近期市场特征：风险偏好评分偏低</h3>
                <p>模型因子显示市场波动率上升，防御因子相对占优。<br>此为统计观察结果，不预测未来走势。</p>
            </div>
            """, unsafe_allow_html=True)

        # ==================== 标签页布局 ====================
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 研究样本", "📈 数据可视化", "📊 策略回测", "📬 联系方式"])

        with tab1:
            st.markdown("### 研究样本列表 | Sample Stocks")
            st.caption("以下为基于因子模型的样本股票，仅供研究参考，不构成推荐")
            
            col_list1, col_list2 = st.columns([1.3, 1])
            
            with col_list1:
                # 突出显示 Top 1
                st.markdown("**样本#1**")
                if len(df_top10) > 0:
                    code = df_top10.iloc[0]['symbol']
                    name = stock_names[0] if len(stock_names) > 0 else code
                    score = df_top10.iloc[0]['score']
                    st.markdown(f"""
                    <div class="stock-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 16px;">{code}</strong>
                                <span style="color: #666; margin-left: 8px; font-size: 14px;">{name}</span>
                            </div>
                            <span style="color: #6c757d; font-size: 14px;">评分: {score:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # 样本 #2-3
                for i in range(1, min(3, len(df_top10))):
                    code = df_top10.iloc[i]['symbol']
                    name = stock_names[i] if len(stock_names) > i else code
                    score = df_top10.iloc[i]['score']
                    st.markdown(f"""
                    <div class="stock-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: #999; margin-right: 8px;">#{i+1}</span>
                                <strong>{code}</strong>
                                <span style="color: #666; margin-left: 8px;">{name}</span>
                            </div>
                            <span style="color: #6c757d;">{score:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_list2:
                # 完整列表
                st.markdown("**完整样本 (#1-10)**")
                display_df = df_top10[['symbol', 'score']].copy()
                display_df.insert(0, '编号', range(1, len(display_df) + 1))
                display_df.columns = ['编号', '代码', '评分']
                st.dataframe(display_df, use_container_width=True, hide_index=True, height=280)

        with tab2:
            st.markdown("### 数据可视化 | Data Visualization")
            st.caption("交互式K线图，数据来源: TradingView")
            
            stock_options = [f"{code} - {name}" for code, name in zip(df_top10['symbol'], stock_names)]
            selected = st.selectbox("选择查看", stock_options, index=0, label_visibility="collapsed")

            if selected:
                selected_code = selected.split(" - ")[0]
                selected_name = selected.split(" - ")[1]
                display_chart(selected_code, selected_name)

        with tab3:
            st.markdown("### 策略回测 | Backtest Results")
            st.caption("历史回测数据不代表未来收益，仅供学术研究")
            
            equity_path = 'equity.csv'
            if os.path.exists(equity_path):
                try:
                    equity_df = pd.read_csv(equity_path)
                    equity_df['date'] = pd.to_datetime(equity_df['date'])

                    initial_value = equity_df['equity'].iloc[0]
                    final_value = equity_df['equity'].iloc[-1]
                    total_return = (final_value - initial_value) / initial_value * 100

                    col_m1, col_m2, col_m3 = st.columns(3)
                    
                    with col_m1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">初始净值</div>
                            <div class="value">{initial_value:.4f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">当前净值</div>
                            <div class="value">{final_value:.4f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">历史收益率</div>
                            <div class="value">{total_return:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=equity_df['date'],
                        y=equity_df['equity'],
                        mode='lines+markers',
                        name='净值曲线',
                        line=dict(color='#6c757d', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(108, 117, 125, 0.08)'
                    ))

                    fig.update_layout(
                        title="策略净值曲线 (仅供研究)",
                        xaxis_title="日期",
                        yaxis_title="净值",
                        height=350,
                        template="plotly_white",
                        hovermode="x unified"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.info("暂无回测数据")
            else:
                st.info("暂无线性回测数据")

        with tab4:
            # 克制、筛选式的联系方式
            st.markdown("### 学术交流 | Academic Exchange")
            
            st.markdown("""
            <div class="subscription-box">
                <h4>📌 研究说明</h4>
                <p>本项目为个人量化研究项目，数据和模型仅供参考学习。<br>
                如需学术交流，请扫码添加微信（请备注：研究交流）。</p>
            </div>
            """, unsafe_allow_html=True)

            col_qr1, col_qr2 = st.columns(2)

            with col_qr1:
                st.markdown('<div class="qr-section">', unsafe_allow_html=True)
                st.markdown("**💬 微信**")
                try:
                    st.image("wechat_qr.png", width=160)
                except:
                    st.info("二维码待添加")
                st.markdown('<p style="font-size: 11px; color: #999;">扫码添加，备注"研究交流"</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_qr2:
                st.markdown('<div class="qr-section">', unsafe_allow_html=True)
                st.markdown("**💳 支付宝**")
                try:
                    st.image("alipay_qr.png", width=160)
                except:
                    st.info("二维码待添加")
                st.markdown('<p style="font-size: 11px; color: #999;">自愿打赏，支持研究</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="risk-warning">
                <strong>⚠️ 重要提示</strong><br>
                • 添加微信即视为同意仅进行学术交流<br>
                • 不提供任何投资建议或实盘指导<br>
                • 不承诺任何收益，不保证数据准确性<br>
                • 交流过程中如产生分歧，请直接停止联系
            </div>
            """, unsafe_allow_html=True)

        # ==================== 底部免责声明 ====================
        st.markdown("---")
        st.markdown("""
        <div class="disclaimer-box">
            <strong>🔒 法律声明</strong><br><br>
            1. 本网站所有内容仅供<strong>学术研究</strong>和<strong>量化学习</strong>使用，不构成任何投资建议。<br><br>
            2. 任何基于本研究数据产生的投资行为，风险自担，与本站无关。<br><br>
            3. 历史数据、因子模型、回测结果均<strong>不代表未来表现</strong>。<br><br>
            4. 如不同意上述声明，请立即离开本站。
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"加载出错: {str(e)}")
        st.write("请检查数据路径配置")


if __name__ == "__main__":
    main()
