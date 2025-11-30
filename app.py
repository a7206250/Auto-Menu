import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (視覺增強版)")

# ==========================================
# 👇 CSS 視覺優化區 (這是幫網頁化妝的魔法代碼) 👇
st.markdown(
    """
    <style>
    /* 1. 針對所有下拉選單 (Selectbox) 的外框做造型 */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #e3f2fd; /* 淺藍色底 (讓它跟背景分開) */
        border: 2px solid #2196f3; /* 亮藍色邊框 */
        border-radius: 10px;       /* 圓角 */
        color: black;              /* 強制黑色文字 */
    }
    
    /* 2. 針對選單裡面的文字 */
    .stSelectbox div[data-baseweb="select"] span {
        color: black !important;   /* 強制黑色，避免在深色模式看不見 */
        font-weight: bold;         /* 加粗 */
        font-size: 16px;           /* 字體加大 */
    }

    /* 3. 針對下拉後的選單列表 (Popup Menu) */
    ul[data-baseweb="menu"] {
        background-color: #ffffff !important; /* 選單背景全白 */
    }
    li[role="option"] {
        color: black !important;      /* 選項文字黑色 */
        font-weight: bold;
    }
    /* 滑鼠滑過選項時的顏色 */
    li[role="option"]:hover {
        background-color: #bbdefb !important; /* 淺藍色高亮 */
    }
    
    /* 4. 優化輸入框 (名字輸入) */
    .stTextInput input {
        background-color: #fff9c4; /* 淺黃色底，提示要輸入 */
        color: black !important;
        border: 2px solid #fbc02d;
        border-radius: 10px;
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
    with st.expander("👑 團主專用：產生指定連結 (含分類)"):
        st.caption("現在可以產生鎖定「分類」的連結囉！")
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
                if gen_cat != "請選擇...":
                    p_cat = urllib.parse.quote(gen_cat)
                    link += f"&cat={p_cat}"
                if gen_shop != "請選擇...":
                    p_shop = urllib.parse.quote(gen_shop)
                    link += f"&shop={p_shop}"
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
            shop_all_data = menu_df[menu_df['店家'] == shop_name]
            main_menu = shop_all_data[shop_all_data['類別'] != 'addon']
            shop_addons_df = shop_all_data[shop_all_data['類別'] == 'addon']
            
            st.success(f"已載入：{shop_name}")
            
            if main_menu.empty:
                st.warning("此店家無主餐品項")
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
                final_price = base_price + addon_total_price
                final_item_str = f"{base_item_name} {spec_str} {selected_addons_str} {note}".strip()

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
            st.markdown(f"### 💰 總金額：${orders_df['價格'].sum()} (共 {len
