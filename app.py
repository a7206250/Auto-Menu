import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (智慧加點版)")

# ==========================================
# 👇 設定區 👇
MENU_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXUPPZds_lPc5m7p6yXXPr5LZ8ISmrpvHGiTY8iz3cFaPfJmWeo3UDCAbd1IIX3ZMEc7yGcAs3BsFY/pub?output=csv"
ORDER_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR7J3Q0wm7tSdmRdxjRJHFIYs6tRQELYbORio8Ug0ZNGfzOrRa8o9xN9U32z8HtVi1dShR5U6qeHlb/pub?output=csv"
FORM_URL_TEMPLATE = "https://docs.google.com/forms/d/e/1FAIpQLSdOAUZ6PBos8xj0J_dAe8stM5aI7yrfBOaXvcAocIAsLEkPfA/viewform?usp=pp_url&entry.1045899805=name&entry.1617860867=area&entry.131804259=shop&entry.2028542611=item&entry.1686582624=price"
# ==========================================

# --- 2. 讀取資料函數 ---
@st.cache_data(ttl=30)
def load_menu(url):
    try:
        df = pd.read_csv(url)
        if '區域' not in df.columns: df['區域'] = '未分類'
        if '加料設定' not in df.columns: df['加料設定'] = None
        # 確保類別欄位存在，且去除空白
        if '類別' in df.columns:
            df['類別'] = df['類別'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=5) 
def load_orders(url):
    try:
        df = pd.read_csv(url)
        today_str = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
        if not df.empty:
            time_col = df.columns[0]
            today_df = df[df[time_col].astype(str).str.contains(today_str, na=False)]
            return today_df
        else: return df
    except: return pd.read_csv(url)

menu_df = load_menu(MENU_CSV_URL)

# --- 3. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 ===
with tab1:
    with st.expander("👑 團主專用：產生指定店家連結"):
        if not menu_df.empty:
            base_url = "https://auto-menu-c8coaalkxp2nyahawe4wxs.streamlit.app/"
            gen_areas = ["請選擇..."] + list(menu_df['區域'].dropna().unique())
            gen_area = st.selectbox("1. 選擇區域", gen_areas, key="gen_area")
            gen_shops = ["請選擇..."]
            if gen_area != "請選擇...":
                gen_shops = ["請選擇..."] + list(menu_df[menu_df['區域'] == gen_area]['店家'].unique())
            gen_shop = st.selectbox("2. 選擇店家", gen_shops, key="gen_shop")
            if gen_shop != "請選擇...":
                link = f"{base_url}?area={urllib.parse.quote(gen_area)}&shop={urllib.parse.quote(gen_shop)}"
                st.code(link, language="text")

    st.markdown("---")
    st.markdown("### 步驟 1：你是誰？")
    user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason", key="user_name")
    
    st.markdown("### 步驟 2：選擇店家")
    
    if not menu_df.empty:
        qp = st.query_params
        t_area, t_shop = qp.get("area", None), qp.get("shop", None)

        all_areas = ["請選擇區域..."] + list(menu_df['區域'].dropna().unique())
        idx_area = all_areas.index(t_area) if t_area in all_areas else 0
        selected_area = st.selectbox("📍 區域", all_areas, index=idx_area)
        
        shop_list = ["請選擇店家..."]
        if selected_area != "請選擇區域...":
            filtered_df = menu_df[menu_df['區域'] == selected_area]
            shop_list = ["請選擇店家..."] + list(filtered_df['店家'].unique())
            
        idx_shop = shop_list.index(t_shop) if t_shop in shop_list else 0
        shop_name = st.selectbox("🏪 店家", shop_list, index=idx_shop)

        # 3. 顯示菜單
        if shop_name not in ["請選擇店家...", "請先選擇區域..."]:
            # 抓出這家店的所有資料
            shop_all_data = menu_df[menu_df['店家'] == shop_name]
            
            # 分離「主餐」和「全店通用加點(addon)」
            # 主餐 = 類別不是 addon 的
            main_menu = shop_all_data[shop_all_data['類別'] != 'addon']
            # 通用加點 = 類別是 addon 的
            shop_addons_df = shop_all_data[shop_all_data['類別'] == 'addon']
            
            st.success(f"已載入：{shop_name}")
            
            if main_menu.empty:
                st.warning("這家店好像只有單點品項，沒有主餐喔！(請檢查 Google Sheet 類別設定)")
            else:
                main_menu['顯示名稱'] = main_menu['品項'] + " ($" + main_menu['價格'].astype(str) + ")"
                selected_display = st.radio("請選擇品項：", main_menu['顯示名稱'])
                
                selected_row = main_menu[main_menu['顯示名稱'] == selected_display].iloc[0]
                base_item_name = selected_row['品項']
                base_price = int(selected_row['價格'])
                shop_type = selected_row['類別']
                
                st.write("---")
                st.write("**客製化與加料**")
                
                # --- A. 飲料客製化 ---
                spec_str = ""
                if shop_type == "drink":
                    c1, c2 = st.columns(2)
                    sugar = c1.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                    ice = c2.selectbox("冰塊/溫度", ["正常冰", "少冰", "微冰", "去冰", "溫", "熱"])
                    spec_str = f"({sugar}/{ice})"
                
                # --- B. 智慧加料區 (合併兩種來源) ---
                addon_dict = {}

                # 來源 1: 該品項專屬的「加料設定」欄位 (給飲料珍椰用)
                if pd.notna(selected_row['加料設定']) and str(selected_row['加料設定']).strip() != "":
                    raw_addons = str(selected_row['加料設定']).replace("，", ",")
                    for item in raw_addons.split(","):
                        if "$" in item:
                            name, cost = item.split("$")
                            addon_dict[f"{name} (+${cost})"] = int(cost)

                # 來源 2: 全店通用的「addon」類別品項 (給火鍋料用)
                if not shop_addons_df.empty:
                    for index, row in shop_addons_df.iterrows():
                        addon_key = f"{row['品項']} (+${row['價格']})"
                        addon_dict[addon_key] = int(row['價格'])

                # 顯示多選選單
                addon_total_price = 0
                selected_addons_str = ""
                
                if addon_dict:
                    picked_addons = st.multiselect("👇 想要加點什麼料？(可複選)", options=addon_dict.keys())
                    for picked in picked_addons:
                        addon_total_price += addon_dict[picked]
                        clean_name = picked.split(" (")[0]
                        selected_addons_str += f"+{clean_name} "
                else:
                    st.caption("此品項無可加購項目")
                
                # --- C. 備註 ---
                note = st.text_input("其他備註", "")
                
                # --- 計算 ---
                final_price = base_price + addon_total_price
                final_item_str = f"{base_item_name} {spec_str} {selected_addons_str} {note}".strip()

                # --- 送出 ---
                st.markdown("### 步驟 3：確認送出")
                if user_name and selected_area != "請選擇區域...":
                    safe_name = urllib.parse.quote(user_name)
                    safe_area = urllib.parse.quote(selected_area)
                    safe_shop = urllib.parse.quote(shop_name)
                    safe_item = urllib.parse.quote(final_item_str)
                    safe_price = str(final_price)

                    form_link = FORM_URL_TEMPLATE.replace("name", safe_name)\
                                                 .replace("area", safe_area)\
                                                 .replace("shop", safe_shop)\
                                                 .replace("item", safe_item)\
                                                 .replace("price", safe_price)

                    st.info(f"餐點：**{base_item_name}** (${base_price})")
                    if addon_total_price > 0:
                        st.warning(f"加料：**{selected_addons_str}** (+${addon_total_price})")
                    st.success(f"💰 **總金額：${final_price}**")
                    
                    st.link_button("🚀 送出訂單 (開啟 Google 表單)", form_link)
                
                elif not user_name:
                    st.error("⚠️ 請先輸入名字！")

# === Tab 2 & 3 ===
with tab2:
    st.subheader("目前訂單狀態 (自動同步)")
    if st.button("🔄 重新整理訂單", key="ref2"): st.cache_data.clear()
    orders_df = load_orders(ORDER_CSV_URL)
    if not orders_df.empty:
        try:
            st.dataframe(orders_df[["姓名", "店家", "訂單內容", "價格", "區域"]], use_container_width=True, hide_index=True)
            st.markdown(f"### 💰 總金額：${orders_df['價格'].sum()} (共 {len(orders_df)} 筆)")
        except: st.dataframe(orders_df)
    else: st.info("無訂單資料...")

with tab3:
    st.subheader("店家訂單彙整")
    if st.button("🔄 刷新資料", key="ref3"): st.cache_data.clear()
    orders_df = load_orders(ORDER_CSV_URL)
    if not orders_df.empty and shop_name not in ["請選擇店家...", "請先選擇區域..."]:
        curr_orders = orders_df[orders_df["店家"] == shop_name]
        if not curr_orders.empty:
            summary = curr_orders.groupby(["訂單內容"]).size().reset_index(name='數量')
            txt = f"老闆你好，我要點餐 ({shop_name})：\n"
            txt += "------------------\n"
            for _, row in summary.iterrows(): txt += f"● {row['訂單內容']} x {row['數量']}\n"
            txt += f"------------------\n總共 {len(curr_orders)} 份。"
            st.text_area("複製文字", txt, height=200)
        else: st.warning("尚無訂單。")
    elif shop_name == "請選擇店家...": st.info("👈 請先選擇店家")
    else: st.warning("尚無資料")
