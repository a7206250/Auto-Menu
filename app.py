import streamlit as st
import pandas as pd

# --- 1. 設定頁面基本資訊 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")

# ==========================================
# 👇 請把你的 Google Sheet CSV 連結貼在這裡 👇
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXUPPZds_lPc5m7p6yXXPr5LZ8ISmrpvHGiTY8iz3cFaPfJmWeo3UDCAbd1IIX3ZMEc7yGcAs3BsFY/pub?output=csv"
# (記得換成你自己的連結！)
# ==========================================

# --- 2. 讀取 Google Sheet 資料庫 ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # 確保必要的欄位存在，避免報錯
        if '區域' not in df.columns:
            df['區域'] = '未分類' # 如果表格忘了加區域欄位，就預設為未分類
        return df
    except Exception as e:
        st.error(f"無法讀取菜單資料，請檢查連結。\n錯誤訊息: {e}")
        return pd.DataFrame()

menu_df = load_data(sheet_url)

# --- 3. 初始化訂單 ---
if 'orders' not in st.session_state:
    st.session_state['orders'] = []

# --- 4. 主標題 ---
st.title("🍱 點餐魔術師")

# --- 5. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 ===
with tab1:
    st.markdown("### 步驟 1：你是誰？")
    user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason")
    st.markdown("---")

    st.markdown("### 步驟 2：選擇店家")
    
    if not menu_df.empty:
        # --- 新增功能：區域篩選 ---
        # 取得所有不重複的區域列表
        all_areas = ["請選擇區域..."] + list(menu_df['區域'].dropna().unique())
        
        # 1. 先選區域
        selected_area = st.selectbox("📍 請問你在哪一區？", all_areas)
        
        shop_list = ["請先選擇區域..."]
        
        # 2. 根據區域篩選店家
        if selected_area != "請選擇區域...":
            # 篩選出該區域的店家
            filtered_df = menu_df[menu_df['區域'] == selected_area]
            shop_list = ["請選擇店家..."] + list(filtered_df['店家'].unique())
            
        shop_name = st.selectbox("🏪 選擇店家", shop_list)

        # 3. 顯示菜單 (邏輯不變)
        if shop_name != "請先選擇區域..." and shop_name != "請選擇店家...":
            shop_menu = menu_df[menu_df['店家'] == shop_name]
            shop_type = shop_menu.iloc[0]['類別'] 
            
            st.success(f"已載入：{shop_name}")
            
            # 顯示菜單選項
            shop_menu['顯示名稱'] = shop_menu['品項'] + " ($" + shop_menu['價格'].astype(str) + ")"
            selected_display = st.radio("請選擇品項：", shop_menu['顯示名稱'])
            
            # 找回原本資料
            selected_row = shop_menu[shop_menu['顯示名稱'] == selected_display].iloc[0]
            selected_item = selected_row['品項']
            price = selected_row['價格']
            
            st.write("---")
            st.write("**客製化選項**")
            
            if shop_type == "drink":
                col_sugar, col_ice = st.columns(2)
                with col_sugar:
                    sugar = st.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                with col_ice:
                    ice = st.selectbox("冰塊/溫度", ["正常冰", "少冰", "微冰", "去冰", "完全去冰", "常溫", "溫", "熱"])
                item_spec = f"{sugar}/{ice}"
            else:
                item_spec = "標準"
            
            custom_note = st.text_input("特殊備註", "")
            final_note = f"{item_spec}, {custom_note}" if custom_note else item_spec

            if st.button("➕ 加入訂單", use_container_width=True):
                if user_name.strip() == "":
                    st.error("⚠️ 記得填寫你的名字喔！")
                else:
                    new_order = {
                        "姓名": user_name,
                        "區域": selected_area, # 多記一個區域方便辨識
                        "店家": shop_name,
                        "餐點": selected_item,
                        "規格/備註": final_note,
                        "價格": int(price),
                        "付款狀態": False
                    }
                    st.session_state['orders'].append(new_order)
                    st.balloons()
                    st.toast(f"✅ {user_name} 點餐成功！")

# === Tab 2: 訂單總表 ===
with tab2:
    st.subheader("目前訂單狀態")
    if len(st.session_state['orders']) > 0:
        df = pd.DataFrame(st.session_state['orders'])
        # 顯示時把不需要的欄位藏起來，比較乾淨
        display_df = df[["姓名", "店家", "餐點", "規格/備註", "價格", "付款狀態"]]
        
        st.dataframe(
            display_df, 
            column_config={
                "付款狀態": st.column_config.CheckboxColumn("已付款?", default=False)
            },
            use_container_width=True,
            hide_index=True
        )
        total_amount = df["價格"].sum()
        st.markdown(f"### 💰 總金額：**${total_amount}**")
        st.markdown(f"👥 總人數：{len(df)} 人")
    else:
        st.info("目前還沒有人點餐喔！")

# === Tab 3: 給店家小抄 ===
with tab3:
    st.subheader("給店家的文字")
    if len(st.session_state['orders']) > 0:
        df = pd.DataFrame(st.session_state['orders'])
        if shop_name != "請選擇店家..." and shop_name != "請先選擇區域...":
            current_shop_orders = df[df["店家"] == shop_name]
            if not current_shop_orders.empty:
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
