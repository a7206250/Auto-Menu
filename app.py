import streamlit as st
import pandas as pd
import urllib.parse # 用來處理網址編碼
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (永久保存版)")

# ==========================================
# 👇 設定區 (已保留你填好的連結) 👇

# 1. 菜單資料庫
MENU_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXUPPZds_lPc5m7p6yXXPr5LZ8ISmrpvHGiTY8iz3cFaPfJmWeo3UDCAbd1IIX3ZMEc7yGcAs3BsFY/pub?output=csv"

# 2. 訂單資料庫
ORDER_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR7J3Q0wm7tSdmRdxjRJHFIYs6tRQELYbORio8Ug0ZNGfzOrRa8o9xN9U32z8HtVi1dShR5U6qeHlb/pub?output=csv"

# 3. Google 表單預填連結
FORM_URL_TEMPLATE = "https://docs.google.com/forms/d/e/1FAIpQLSdOAUZ6PBos8xj0J_dAe8stM5aI7yrfBOaXvcAocIAsLEkPfA/viewform?usp=pp_url&entry.1045899805=name&entry.1617860867=area&entry.131804259=shop&entry.2028542611=item&entry.1686582624=price"

# ==========================================

# --- 2. 讀取資料函數 ---
@st.cache_data(ttl=30) # 菜單不用太常更新
def load_menu(url):
    try:
        df = pd.read_csv(url)
        if '區域' not in df.columns: df['區域'] = '未分類'
        return df
    except: return pd.DataFrame()

# 訂單要常常更新，所以 ttl 設短一點 (5秒)
@st.cache_data(ttl=5) 
def load_orders(url):
    try:
        df = pd.read_csv(url)
        
        # 1. 取得今天的日期字串 (修正為台灣時間 UTC+8)
        # 加上 timedelta(hours=8) 確保早上點餐也能正常顯示
        today_str = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
        
        # 2. 進行篩選：只保留「時間戳記」欄位裡包含「今天日期」的資料
        if not df.empty:
            time_col = df.columns[0] # 抓取第一欄 (通常就是時間)
            # 這裡的邏輯是：把該欄轉成文字，然後檢查有沒有包含今天的日期
            today_df = df[df[time_col].astype(str).str.contains(today_str, na=False)]
            return today_df
        else:
            return df
            
    except Exception as e:
        # 如果出錯 (例如日期格式不對)，為了保險起見，還是回傳全部資料
        return pd.read_csv(url) # 降級處理：回傳全部

menu_df = load_menu(MENU_CSV_URL)

# --- 3. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 ===
with tab1:
    st.markdown("### 步驟 1：你是誰？")
    user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason", key="user_name")
    st.markdown("---")

    # --- 區域與店家篩選 (同上次邏輯) ---
    if not menu_df.empty:
        all_areas = ["請選擇區域..."] + list(menu_df['區域'].dropna().unique())
        selected_area = st.selectbox("📍 請問你在哪一區？", all_areas)
        
        shop_list = ["請選擇店家..."]
        if selected_area != "請選擇區域...":
            filtered_df = menu_df[menu_df['區域'] == selected_area]
            shop_list = ["請選擇店家..."] + list(filtered_df['店家'].unique())
            
        shop_name = st.selectbox("🏪 選擇店家", shop_list)

        if shop_name != "請選擇店家..." and shop_name != "請先選擇區域...":
            shop_menu = menu_df[menu_df['店家'] == shop_name]
            shop_type = shop_menu.iloc[0]['類別'] 
            
            # 選餐邏輯
            shop_menu['顯示名稱'] = shop_menu['品項'] + " ($" + shop_menu['價格'].astype(str) + ")"
            selected_display = st.radio("請選擇品項：", shop_menu['顯示名稱'])
            
            selected_row = shop_menu[shop_menu['顯示名稱'] == selected_display].iloc[0]
            selected_item_name = selected_row['品項']
            price = int(selected_row['價格'])
            
            # 客製化
            st.write("---")
            if shop_type == "drink":
                col1, col2 = st.columns(2)
                sugar = col1.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                ice = col2.selectbox("冰塊/溫度", ["正常冰", "少冰", "微冰", "去冰", "溫", "熱"])
                spec = f"({sugar}/{ice})"
            else:
                spec = ""
            
            note = st.text_input("備註", "")
            final_item_str = f"{selected_item_name} {spec} {note}".strip()

            # --- 產生 Google 表單連結 (魔法區) ---
            st.markdown("### 步驟 3：確認送出")
            if user_name and selected_area != "請選擇區域...":
                # 把資料填入網址
                safe_name = urllib.parse.quote(user_name)
                safe_area = urllib.parse.quote(selected_area)
                safe_shop = urllib.parse.quote(shop_name)
                safe_item = urllib.parse.quote(final_item_str)
                safe_price = str(price)

                # 替換 Template 裡的關鍵字
                form_link = FORM_URL_TEMPLATE.replace("name", safe_name)\
                                             .replace("area", safe_area)\
                                             .replace("shop", safe_shop)\
                                             .replace("item", safe_item)\
                                             .replace("price", safe_price)

                st.info(f"確認餐點：**{final_item_str}** (${price})")
                
                # 顯示連結按鈕
                st.link_button("🚀 按這裡送出訂單 (將開啟 Google 表單)", form_link)
                st.caption("點擊後會開啟新視窗，請按下「提交」即可完成點餐。")
            
            elif not user_name:
                st.error("⚠️ 請先輸入名字才能送出！")

# === Tab 2: 訂單總表 (讀取 Google Sheet) ===
with tab2:
    st.subheader("目前訂單狀態 (自動同步)")
    
    # 這裡加一個重新整理按鈕
    if st.button("🔄 重新整理訂單"):
        st.cache_data.clear()
    
    orders_df = load_orders(ORDER_CSV_URL)
    
    if not orders_df.empty:
        # 顯示重點欄位
        try:
            display_cols = ["姓名", "店家", "訂單內容", "價格", "區域"]
            st.dataframe(orders_df[display_cols], use_container_width=True, hide_index=True)
            
            total = orders_df["價格"].sum()
            count = len(orders_df)
            st.markdown(f"### 💰 總金額：${total} (共 {count} 筆)")
        except:
            st.dataframe(orders_df) # 如果欄位對不上，就直接顯示全部
    else:
        st.info("目前還沒有訂單資料，或是讀取中...")

# === Tab 3: 給店家小抄 ===
with tab3:
    st.subheader("店家訂單彙整")
    orders_df = load_orders(ORDER_CSV_URL)
    
    if not orders_df.empty and shop_name != "請選擇店家...":
        # 篩選目前店家的單
        current_shop_orders = orders_df[orders_df["店家"] == shop_name]
        
        if not current_shop_orders.empty:
            summary = current_shop_orders.groupby(["訂單內容"]).size().reset_index(name='數量')
            
            txt = f"老闆你好，我要點餐 ({shop_name})：\n------------------\n"
            for _, row in summary.iterrows():
                txt += f"● {row['訂單內容']} x {row['數量']}\n"
            txt += f"------------------\n總共 {len(current_shop_orders)} 份。"
            
            st.text_area("複製文字", txt, height=200)
        else:
            st.warning(f"目前還沒有 {shop_name} 的訂單。")
