import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
st.title("🍱 點餐魔術師 (藍白科技版)")

# ==========================================
# 👇 CSS 視覺優化區 (深色模式修復) 👇
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

    /* 2. 下拉選單 (展開列表) */
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
    
    /* 3. 輸入框 */
    .stTextInput input {
        background-color: #E3F2FD !important;
        color: #000000 !important;
        border: 2px solid #2196F3;
        border-radius: 10px;
        font-weight: bold;
    }
    .stTextInput input::placeholder {
        color: #000000 !important;
        font-weight: 900 !important;
        opacity: 1 !important;
    }
    
    /* 4. 多選框標籤 */
    span[data-baseweb="tag"] {
        background-color: #1976D2 !important;
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
        st.caption("產生指定連結")
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
                    picked_addons = st.multise
