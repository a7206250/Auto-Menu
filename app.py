import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (完美體驗版)")

# ==========================================
# 👇 CSS 視覺優化區 (提示詞修復版) 👇
st.markdown(
    """
    <style>
    /* 1. 下拉選單 (按鈕) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1976D2 !important;
        border: 2px solid #0D47A1 !important;
        border-radius: 10px;
        color: white !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }
    .stSelectbox svg { fill: white !important; }

    /* 2. 下拉選單 (列表) */
    div[data-baseweb="popover"] ul, ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    li[role="option"] {
        color: black !important;
        background-color: #ffffff !important;
        font-weight: bold;
        border-bottom: 1px solid #f0f0f0;
    }
    li[role="option"] div { color: black !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #BBDEFB !important;
    }
    
    /* 3. 輸入框 (名字) - 樣式優化 */
    .stTextInput input {
        background-color: #E3F2FD !important;
        color: #000000 !important; /* 輸入的字是黑色 */
        border: 2px solid #2196F3;
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* --- 🌟 修正重點：提示詞樣式 --- */
    .stTextInput input::placeholder {
        color: #666666 !important; /* 改為深灰色，區分度高 */
        font-weight: normal !important; /* 變細一點，像提示 */
        opacity: 0.7 !important;
    }
    
    /* 當點擊輸入框時，提示詞自動消失 */
    .stTextInput input:focus::placeholder {
        color: transparent !important;
    }
    
    /* 4. 多選框標籤 */
    span[data-baseweb="tag"] {
        background-color: #1976D2 !important;
        color: white !important;
    }

    /* 5. 數字輸入框 */
    div[data-baseweb="input"] {
        background-color: #1976D2 !important;
        border: 2px solid #0D47A1 !important;
        border-radius: 10px;
        color: white !important;
    }
    input[type="number"] {
        color: white !important;
        font-weight: bold !important;
        caret-color: white;
    }
    button[tabindex="-1"] {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ==========================================

# ==========================================
# 👇 設定區 👇
MENU_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXUPPZds_lPc5m7p6yXXPr5LZ8ISmrpvHGiTY8iz3cFaPfJmWeo3UDCAbd1IIX3ZMEc7yGcAs3BsFY/pub?output=csv"
ORDER_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTR7J3Q0wm7tSdmRdxjRJHFIYs6tRQELYbORio8Ug0ZNGfzOrRa8o9xN9U32z8HtVi1dShR5U6qeHlb/pub?output=csv"
FORM_URL_TEMPLATE = "https://docs.google.com/forms/d/e/1FAIpQLSdOAUZ6PBos8xj0J_dAe8stM5aI7yrfBOaXvcAocIAsLEkPfA/viewform?usp=pp_url&entry.1045899805=name&entry.1617860867=area&entry.131804259=shop&entry.2028542611=item&entry.1686582624=price"
# ==========================================

# --- 初始化購物車 ---
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

# --- 2. 讀取資料函數 ---
@st.cache_data(ttl=30)
def load_menu(url):
    try:
        df = pd.read_csv(url)
        if '區域' not in df.columns: df['區域'] = '未分類'
        if '加料設定' not in df.columns: df['加料設定'] = None
        if '店家分類' not in df.columns: df['店家分類'] = '其他'
        if '類別' in df.columns:
            df['類別'] = df['類別'].astype(str).str.strip()
        df['店家分類'] = df['店家分類'].fillna('其他')
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=5) 
def load_orders(url):
    try:
        df = pd.read_csv(url)
        if not df.empty:
            time_col = df.columns[0]
            df = df.sort_values(by=time_col, ascending=False)
            return df
        else: return df
    except: return pd.read_csv(url)

menu_df = load_menu(MENU_CSV_URL)

# --- 3. 分頁結構 ---
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

# === Tab 1: 點餐區 ===
with tab1:
    with st.expander("👑 團主專用：產生指定連結"):
        if not menu_df.empty:
            base_url = "https://auto-menu-c8coaalkxp2nyahawe4wxs.streamlit.app/"
            gen_areas = ["請選擇..."] + list(menu_df['區域'].dropna().unique())
            gen_area = st.selectbox("1. 選擇區域", gen_areas, key="g_area")
            gen_cats = ["請選擇..."]
            if gen_area != "請選擇...":
                area_df = menu_df[menu_df['區域'] == gen_area]
                gen_cats = ["請選擇..."] + list(area_df['店家分類'].unique())
            gen_cat = st.selectbox("2. 選擇分類", gen_cats, key="g_cat")
            gen_shops = ["請選擇..."]
            if gen_cat != "請選擇...":
                cat_df = menu_df[(menu_df['區域'] == gen_area) & (menu_df['店家分類'] == gen_cat)]
                gen_shops = ["請選擇..."] + list(cat_df['店家'].unique())
            gen_shop = st.selectbox("3. 選擇店家", gen_shops, key="g_shop")
            
            if gen_area != "請選擇...":
                p_area = urllib.parse.quote(gen_area)
                link = f"{base_url}?area={p_area}"
                link += "&openExternalBrowser=1"
                if gen_cat != "請選擇...": link += f"&cat={urllib.parse.quote(gen_cat)}"
                if gen_shop != "請選擇...": link += f"&shop={urllib.parse.quote(gen_shop)}"
                st.code(link, language="text")

    st.markdown("---")
    st.markdown("### 步驟 1：你是誰？")
    user_name = st.text_input("請輸入暱稱", placeholder="例如：Jason", key="user_name")
    
    st.markdown("### 步驟 2：選擇店家")
    if not menu_df.empty:
        qp = st.query_params
        t_area, t_cat, t_shop = qp.get("area", None), qp.get("cat", None), qp.get("shop", None)

        all_areas = ["請選擇區域..."] + list(menu_df['區域'].dropna().unique())
        idx_area = all_areas.index(t_area) if t_area in all_areas else 0
        selected_area = st.selectbox("📍 區域", all_areas, index=idx_area)
        
        cat_list = ["請選擇分類..."]
        if selected_area != "請選擇區域...":
            area_df = menu_df[menu_df['區域'] == selected_area]
            cat_list = ["請選擇分類..."] + list(area_df['店家分類'].unique())
        idx_cat = cat_list.index(t_cat) if t_cat in cat_list else 0
        selected_cat = st.selectbox("📂 分類", cat_list, index=idx_cat)

        shop_list = ["請選擇店家..."]
        if selected_cat != "請選擇分類...":
            shop_df = menu_df[(menu_df['區域'] == selected_area) & (menu_df['店家分類'] == selected_cat)]
            shop_list = ["請選擇店家..."] + list(shop_df['店家'].unique())
        idx_shop = shop_list.index(t_shop) if t_shop in shop_list else 0
        shop_name = st.selectbox("🏪 店家", shop_list, index=idx_shop)

        if shop_name not in ["請選擇店家...", "請先選擇區域...", "請選擇分類..."]:
            # --- 換店提醒 ---
            if st.session_state['cart'] and st.session_state['cart'][0]['shop'] != shop_name:
                st.warning(f"⚠️ 你之前選擇了 {st.session_state['cart'][0]['shop']} 的商品，換店將會清空購物車。")
                if st.button("🗑️ 清空購物車並換店"):
                    st.session_state['cart'] = []
                    st.rerun()

            shop_all_data = menu_df[menu_df['店家'] == shop_name]
            main_menu = shop_all_data[shop_all_data['類別'] != 'addon']
            shop_addons_df = shop_all_data[shop_all_data['類別'] == 'addon']
            
            st.success(f"已載入：{shop_name}")
            if main_menu.empty: st.warning("此店家無主餐品項")
            else:
                main_menu['顯示名稱'] = main_menu['品項'] + " ($" + main_menu['價格'].astype(str) + ")"
                selected_display = st.radio("請選擇品項：", main_menu['顯示名稱'])
                
                selected_row = main_menu[main_menu['顯示名稱'] == selected_display].iloc[0]
                base_item_name = selected_row['品項']
                base_price = int(selected_row['價格'])
                shop_type = selected_row['類別']
                
                st.write("---")
                st.write("**客製化與加料**")
                
                spec_str = ""
                if shop_type == "drink":
                    c1, c2 = st.columns(2)
                    sugar = c1.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                    ice = c2.selectbox("冰塊/溫度", ["正常冰", "少冰", "微冰", "去冰", "溫", "熱"])
                    spec_str = f"({sugar}/{ice})"
                
                addon_dict = {}
                if pd.notna(selected_row['加料設定']) and str(selected_row['加料設定']).strip() != "":
                    raw_addons = str(selected_row['加料設定']).replace("，", ",")
                    for item in raw_addons.split(","):
                        if "$" in item:
                            name, cost = item.split("$")
                            addon_dict[f"{name} (+${cost})"] = int(cost)
                if not shop_addons_df.empty:
                    for index, row in shop_addons_df.iterrows():
                        addon_key = f"{row['品項']} (+${row['價格']})"
                        addon_dict[addon_key] = int(row['價格'])

                addon_total_price = 0
                selected_addons_str = ""
                if addon_dict:
                    picked_addons = st.multiselect("👇 加點/加料 (可複選)", options=addon_dict.keys())
                    for picked in picked_addons:
                        addon_total_price += addon_dict[picked]
                        clean_name = picked.split(" (")[0]
                        selected_addons_str += f"+{clean_name} "
                
                note = st.text_input("其他備註", "")
                
                st.write("---")
                col_qty, col_empty = st.columns([1, 2])
                with col_qty:
                    quantity = st.number_input("🔢 數量", min_value=1, max_value=20, value=1, step=1)
                
                unit_price = base_price + addon_total_price
                subtotal = unit_price * quantity
                
                item_str = f"{base_item_name} {spec_str} {selected_addons_str} {note}".strip()
                if quantity > 1: display_item_str = f"{item_str} x{quantity}"
                else: display_item_str = item_str

                if st.button("🛒 加入購物車"):
                    if not user_name: st.error("⚠️ 請先輸入名字！")
                    else:
                        st.session_state['cart'].append({
                            "shop": shop_name,
                            "item": display_item_str,
                            "price": subtotal,
                            "area": selected_area
                        })
                        st.toast(f"已加入：{display_item_str}")

                st.markdown("### 步驟 3：確認與送出")
                if len(st.session_state['cart']) > 0:
                    st.write("📋 **目前清單：**")
                    cart_total = 0
                    cart_items_str_list = []
                    
                    for idx, item in enumerate(st.session_state['cart']):
                        st.text(f"{idx+1}. {item['item']} (${item['price']})")
                        cart_total += item['price']
                        cart_items_str_list.append(item['item'])
                    
                    st.markdown(f"#### 💰 總金額：${cart_total}")
                    final_items_str = " | ".join(cart_items_str_list)
                    
                    if st.button("🗑️ 清空重選"):
                        st.session_state['cart'] = []
                        st.rerun()

                    if user_name:
                        safe_name = urllib.parse.quote(user_name)
                        safe_area = urllib.parse.quote(st.session_state['cart'][0]['area'])
                        safe_shop = urllib.parse.quote(shop_name)
                        safe_item = urllib.parse.quote(final_items_str)
                        safe_price = str(cart_total)
                        
                        form_link = FORM_URL_TEMPLATE.replace("name", safe_name)\
                                                     .replace("area", safe_area)\
                                                     .replace("shop", safe_shop)\
                                                     .replace("item", safe_item)\
                                                     .replace("price", safe_price)
                        
                        html_button = f"""
                        <a href="{form_link}" target="_blank" style="
                            display: block; width: 100%;
                            background-color: #1976D2; color: white;
                            text-align: center; padding: 12px;
                            border-radius: 10px; text-decoration: none;
                            font-weight: bold; font-size: 18px;
                            margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        ">
                            🚀 確認送出訂單 (開啟 Google 表單)
                        </a>
                        """
                        st.markdown(html_button, unsafe_allow_html=True)
                        st.caption("☝️ 點擊上方按鈕即可完成點餐")
                else: st.info("🛒 購物車是空的，請上方選購後按「加入購物車」")

# === Tab 2 ===
with tab2:
    st.subheader("目前訂單狀態")
    today_taiwan = datetime.datetime.now() + datetime.timedelta(hours=8)
    filter_date = st.date_input("📅 選擇要查看的日期", value=today_taiwan)
    if st.button("🔄 重新整理訂單", key="ref2"): st.cache_data.clear()
    orders_df = load_orders(ORDER_CSV_URL)
    if not orders_df.empty:
        time_col = orders_df.columns[0]
        s1 = filter_date.strftime("%Y/%m/%d")
        s2 = f"{filter_date.year}/{filter_date.month}/{filter_date.day}"
        mask = orders_df[time_col].astype(str).str.contains(s1, na=False) | \
               orders_df[time_col].astype(str).str.contains(s2, na=False)
        filtered_orders = orders_df[mask]
        try:
            st.dataframe(filtered_orders[["時間戳記", "姓名", "店家", "訂單內容", "價格", "區域"]], use_container_width=True, hide_index=True)
            total_price = filtered_orders['價格'].sum()
            total_count = len(filtered_orders)
            st.markdown(f"### 💰 {filter_date.strftime('%m/%d')} 總金額：${total_price} (共 {total_count} 筆)")
            if total_count == 0: st.info("💡 今天目前沒有訂單喔！")
        except: st.dataframe(filtered_orders)
    else: st.info("無訂單資料...")

# === Tab 3 ===
with tab3:
    st.subheader("店家訂單彙整")
    if st.button("🔄 刷新資料", key="ref3"): st.cache_data.clear()
    orders_df = load_orders(ORDER_CSV_URL)
    
    try: current_date = filter_date
    except NameError: current_date = datetime.datetime.now() + datetime.timedelta(hours=8)

    time_col = orders_df.columns[0]
    s1 = current_date.strftime("%Y/%m/%d")
    s2 = f"{current_date.year}/{current_date.month}/{current_date.day}"
    mask = orders_df[time_col].astype(str).str.contains(s1, na=False) | \
           orders_df[time_col].astype(str).str.contains(s2, na=False)
    todays_orders = orders_df[mask]

    if not todays_orders.empty and shop_name not in ["請選擇店家...", "請先選擇區域...", "請選擇分類..."]:
        curr_orders = todays_orders[todays_orders["店家"] == shop_name]
        if not curr_orders.empty:
            item_counter = {}
            for order_content in curr_orders["訂單內容"]:
                items = str(order_content).split(" | ")
                for item in items:
                    item = item.strip()
                    name = item
                    qty = 1
                    if " x" in item:
                        parts = item.rsplit(" x", 1)
                        if len(parts) == 2 and parts[1].isdigit():
                            name = parts[0]
                            qty = int(parts[1])
                    if name in item_counter: item_counter[name] += qty
                    else: item_counter[name] = qty
            
            txt = f"老闆你好，我要點餐 ({shop_name})：\n------------------\n"
            total_cups = 0
            for name, quantity in item_counter.items():
                txt += f"● {name} x {quantity}\n"
                total_cups += quantity
            txt += f"------------------\n總共 {total_cups} 份餐點。\n日期：{current_date.strftime('%Y/%m/%d')}"
            st.text_area("複製文字", txt, height=300)
        else: st.warning(f"今天 ({current_date.strftime('%m/%d')}) 還沒有 {shop_name} 的訂單。")
    elif shop_name == "請選擇店家...": st.info("👈 請先選擇店家")
    else: st.warning("尚無資料")
