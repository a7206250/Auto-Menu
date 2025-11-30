import streamlit as st
import pandas as pd

# --- 1. 設定頁面基本資訊 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")

# --- 2. 模擬資料庫 ---
MENU_DB = {
    "50嵐": {
        "items": ["珍珠奶茶", "四季春茶", "紅茶拿鐵", "1號 (珍波椰)"],
        "prices": {"珍珠奶茶": 50, "四季春茶": 35, "紅茶拿鐵": 60, "1號 (珍波椰)": 50},
        "type": "drink"
    },
    "阿明雞腿飯": {
        "items": ["招牌雞腿飯", "滷排骨飯", "鱈魚飯", "菜飯"],
        "prices": {"招牌雞腿飯": 120, "滷排骨飯": 100, "鱈魚飯": 130, "菜飯": 80},
        "type": "food"
    }
}

# --- 3. 初始化訂單儲存空間 ---
if 'orders' not in st.session_state:
    st.session_state['orders'] = []

# --- 4. 主標題 ---
st.title("🍱 點餐魔術師")

# --- 5. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 (修改重點：把暱稱輸入搬進來了) ===
with tab1:
    # --- 修改處：步驟一直接顯示在最上面 ---
    st.markdown("### 步驟 1：你是誰？")
    col_name, col_empty = st.columns([2, 1]) # 排版調整
    with col_name:
        # 這裡不放預設值，讓使用者自己輸入，避免變成一堆小明
        user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason")
    
    st.markdown("---") # 畫一條分隔線

    st.markdown("### 步驟 2：想吃什麼？")
    shop_name = st.selectbox("選擇店家", ["請選擇...", "50嵐", "阿明雞腿飯"])

    if shop_name in MENU_DB:
        menu = MENU_DB[shop_name]
        
        # 顯示菜單區塊
        st.success(f"已載入 {shop_name}")
        
        # 選餐區
        selected_item = st.radio("請選擇品項：", menu['items'])
        price = menu['prices'][selected_item]
        st.info(f"💰 價格：${price}")

        # 客製化區
        st.write("---")
        st.write("**客製化選項**")
        
        if menu['type'] == "drink":
            col_sugar, col_ice = st.columns(2)
            with col_sugar:
                sugar = st.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
            with col_ice:
                ice = st.selectbox("冰塊", ["正常冰", "少冰", "微冰", "去冰"])
            item_spec = f"{sugar}/{ice}"
        else:
            item_spec = "標準"
        
        custom_note = st.text_input("特殊備註 (例如：不要香菜)", "")
        final_note = f"{item_spec}, {custom_note}" if custom_note else item_spec

        # --- 送出按鈕 (加入防呆機制) ---
        if st.button("➕ 加入訂單", use_container_width=True):
            if user_name.strip() == "":
                st.error("⚠️ 等等！請先在最上面輸入你的名字喔！")
            else:
                new_order = {
                    "姓名": user_name,
                    "店家": shop_name,
                    "餐點": selected_item,
                    "規格/備註": final_note,
                    "價格": price,
                    "付款狀態": False
                }
                st.session_state['orders'].append(new_order)
                st.balloons() # 成功時放氣球慶祝
                st.toast(f"✅ {user_name} 點餐成功！")

# === Tab 2: 訂單總表 ===
with tab2:
    st.subheader("目前訂單狀態")
    if len(st.session_state['orders']) > 0:
        df = pd.DataFrame(st.session_state['orders'])
        st.dataframe(
            df, 
            column_config={
                "付款狀態": st.column_config.CheckboxColumn(
                    "已付款?",
                    default=False,
                )
            },
            use_container_width=True,
            hide_index=True
        )
        total_amount = df["價格"].sum()
        st.markdown(f"### 💰 總金額：**${total_amount}**")
        
        # 顯示簡單統計
        st.markdown(f"👥 總人數：{len(df)} 人")
    else:
        st.info("目前還沒有人點餐喔！")

# === Tab 3: 給店家小抄 ===
with tab3:
    st.subheader("給店家的文字")
    if len(st.session_state['orders']) > 0:
        df = pd.DataFrame(st.session_state['orders'])
        if shop_name != "請選擇...":
            current_shop_orders = df[df["店家"] == shop_name]
            if not current_shop_orders.empty:
                # 統計數量
                summary = current_shop_orders.groupby(["餐點", "規格/備註"]).size().reset_index(name='數量')
                
                text_output = f"老闆你好，我要點餐 ({shop_name})：\n"
                text_output += "------------------\n"
                for index, row in summary.iterrows():
                    text_output += f"● {row['餐點']} ({row['規格/備註']}) x {row['數量']}\n"
                text_output += "------------------\n"
                text_output += f"總共 {len(current_shop_orders)} 份餐點。"
                st.text_area("複製內容：", text_output, height=200)
            else:
                st.warning(f"目前還沒有人點 {shop_name}。")
        else:
            st.warning("請先選擇店家。")
    else:
        st.info("暫無訂單資料。")
