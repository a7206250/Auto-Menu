import streamlit as st
import pandas as pd
import urllib.parse # 用來處理網址編碼
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (即時同步版)")

# ==========================================
# 👇 設定區 (已幫你填入正確連結) 👇

# 1. 菜單資料庫
MENU_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXUPPZds_lPc5m7p6yXXPr5LZ8ISmrpvHGiTY8iz3cFaPfJmWeo3UDCAbd1IIX3ZMEc7yGcAs3BsFY/pub?output=csv"

# 2. 訂單資料庫
ORDER_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR7J3Q0wm7tSdmRdxjRJHFIYs6tRQELYbORio8Ug0ZNGfzOrRa8o9xN9U32z8HtVi1dShR5U6qeHlb/pub?output=csv"

# 3. Google 表單預填連結
FORM_URL_TEMPLATE = "https://docs.google.com/forms/d/e/1FAIpQLSdOAUZ6PBos8xj0J_dAe8stM5aI7yrfBOaXvcAocIAsLEkPfA/viewform?usp=pp_url&entry.1045899805=name&entry.1617860867=area&entry.131804259=shop&entry.2028542611=item&entry.1686582624=price"

# ==========================================

# --- 2. 讀取資料函數 ---
@st.cache_data(ttl=30)
def load_menu(url):
    try:
        df = pd.read_csv(url)
        if '區域' not in df.columns: df['區域'] = '未分類'
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=5) 
def load_orders(url):
    try:
        df = pd.read_csv(url)
        # 取得今天的日期字串 (修正為台灣時間 UTC+8)
        today_str = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
        
        if not df.empty:
            time_col = df.columns[0]
            # 確保是字串再比對
            today_df = df[df[time_col].astype(str).str.contains(today_str, na=False)]
            return today_df
        else:
            return df
    except Exception as e:
        return pd.read_csv(url)

menu_df = load_menu(MENU_CSV_URL)

# --- 3. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 ===
with tab1:
    # --- 團主專用：連結產生器 ---
    with st.expander("👑 團主專用：產生指定店家連結 (點此展開)"):
        st.caption("選好店家後，複製下方的連結傳給家人，他們打開就會直接是這家店！")
        if not menu_df.empty:
            # 假設這是你的 App 網址
            base_url = "https://auto-menu-c8coaalkxp2nyahawe4wxs.streamlit.app/"
            
            gen_areas = ["請選擇..."] + list(menu_df['區域'].dropna().unique())
            gen_area = st.selectbox("1. 選擇區域", gen_areas, key="gen_area")
            
            gen_shops = ["請選擇..."]
            if gen_area != "請選擇...":
                gen_shops = ["請選擇..."] + list(menu_df[menu_df['區域'] == gen_area]['店家'].unique())
            gen_shop = st.selectbox("2. 選擇店家", gen_shops, key="gen_shop")
            
            if gen_shop != "請選擇...":
                safe_area_param = urllib.parse.quote(gen_area)
                safe_shop_param = urllib.parse.quote(gen_shop)
                final_link = f"{base_url}?area={safe_area_param}&shop={safe_shop_param}"
                st.code(final_link, language="text")
                st.caption("👆 點右上角複製按鈕，傳到 Line 群組")

    st.markdown("---")
    
    # --- 一般使用者點餐區 ---
    st.markdown("### 步驟 1：你是誰？")
    user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason", key="user_name")
    
    st.markdown("### 步驟 2：選擇店家")
    
    if not menu_df.empty:
        # 0. 抓取網址參數
        query_params = st.query_params
        target_area = query_params.get("area", None)
        target_shop = query_params.get("shop", None)

        # 1. 準備區域選單
        all_areas = ["請選擇區域..."] + list(menu_df['區域'].dropna().unique())
        area_index = 0
        if target_area and target_area in all_areas:
            area_index = all_areas.index(target_area)
            
        selected_area = st.selectbox("📍 請問你在哪一區？", all_areas, index=area_index)
        
        # 2. 準備店家選單
        shop_list = ["請選擇店家..."]
        if selected_area != "請選擇區域...":
            filtered_df = menu_df[menu_df['區域'] == selected_area]
            shop_list = ["請選擇店家..."] + list(filtered_df['店家'].unique())
            
        shop_index = 0
        if target_shop and target_shop in shop_list:
            shop_index = shop_list.index(target_shop)
            
        shop_name = st.selectbox("🏪 選擇店家", shop_list, index=shop_index)

        # 3. 顯示菜單
        if shop_name != "請選擇店家..." and shop_name != "請先選擇區域...":
            shop_menu = menu_df[menu_df['店家'] == shop_name]
            shop_type = shop_menu.iloc[0]['類別'] 
            
            st.success(f"已載入：{shop_name}")
            
            shop_menu['顯示名稱'] = shop_menu['品項'] + " ($" + shop_menu['價格'].astype(str) + ")"
            selected_display = st.radio("請選擇品項：", shop_menu['顯示名稱'])
            
            selected_row = shop_menu[shop_menu['顯示名稱'] == selected_display].iloc[0]
            selected_item_name = selected_row['品項']
            price = int(selected_row['價格'])
            
            st.write("---")
            st.write("**客製化**")
            if shop_type == "drink":
                col1, col2 = st.columns(2)
                sugar = col1.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                ice = col2.selectbox("冰塊/溫度", ["正常冰", "少冰", "微冰", "去冰", "溫", "熱"])
                spec = f"({sugar}/{ice})"
            else:
                spec = ""
            
            note = st.text_input("備註", "")
            final_item_str = f"{selected_item_name} {spec} {note}".strip()

            st.markdown("### 步驟 3：確認送出")
            if user_name and selected_area != "請選擇區域...":
                safe_name = urllib.parse.quote(user_name)
                safe_area = urllib.parse.quote(selected_area)
                safe_shop = urllib.parse.quote(shop_name)
                safe_item = urllib.parse.quote(final_item_str)
                safe_price = str(price)

                form_link = FORM_URL_TEMPLATE.replace("name", safe_name)\
                                             .replace("area", safe_area)\
                                             .replace("shop", safe_shop)\
                                             .replace("item", safe_item)\
                                             .replace("price", safe_price)

                st.info(f"確認餐點：**{final_item_str}** (${price})")
                st.link_button("🚀 按這裡送出訂單 (將開啟 Google 表單)", form_link)
                st.caption("點擊後會開啟新視窗，請按下「提交」即可完成點餐。")
            
            elif not user_name:
                st.error("⚠️ 請先輸入名字才能送出！")

# === Tab 2: 訂單總表 ===
with tab2:
    st.subheader("目前訂單狀態 (自動同步)")
    if st.button("🔄 重新整理訂單", key="refresh_tab2"):
        st.cache_data.clear()
    
    orders_df = load_orders(ORDER_CSV_URL)
    
    if not orders_df.empty:
        try:
            display_cols = ["姓名", "店家", "訂單內容", "價格", "區域"]
            st.dataframe(orders_df[display_cols], use_container_width=True, hide_index=True)
            total = orders_df["價格"].sum()
            count = len(orders_df)
            st.markdown(f"### 💰 總金額：${total} (共 {count} 筆)")
        except:
            st.dataframe(orders_df)
    else:
        st.info("目前還沒有訂單資料...")

# === Tab 3: 給店家小抄 ===
with tab3:
    st.subheader("店家訂單彙整")
    
    if st.button("🔄 刷新資料 (產生最新小抄)", key="refresh_tab3"):
        st.cache_data.clear()
    
    orders_df = load_orders(ORDER_CSV_URL)
    
    if not orders_df.empty and shop_name != "請選擇店家..." and shop_name != "請先選擇區域...":
        current_shop_orders = orders_df[orders_df["店家"] == shop_name]
        
        if not current_shop_orders.empty:
            summary = current_shop_orders.groupby(["訂單內容"]).size().reset_index(name='數量')
            
            # --- 修正處：將原本很長的一行拆成兩行寫，避免複製錯誤 ---
            txt = f"老闆你好，我要點餐 ({shop_name})：\n"
            txt += "------------------\n"
            
            for _, row in summary.iterrows():
                txt += f"● {row['訂單內容']} x {row['數量']}\n"
            txt += f"------------------\n總共 {len(current_shop_orders)} 份。"
            
            st.text_area("複製文字", txt, height=200)
        else:
            st.warning(f"目前還沒有 {shop_name} 的訂單。")
    elif shop_name == "請選擇店家...":
        st.info("👈 請先在第一頁「選擇店家」，這裡才會顯示該店的統計喔！")
    else:
        st.warning("目前還沒有資料。")
