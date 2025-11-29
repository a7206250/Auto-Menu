# 1. 安裝 Streamlit 和穿透工具
!pip install -q streamlit
!npm install -g localtunnel

# 2. 寫入你的點餐系統程式碼 (app.py)
# 注意：這裡就是剛剛那段 Menu Magician 的程式碼
code = """
import streamlit as st
import pandas as pd

st.set_page_config(page_title="點餐魔術師", page_icon="🍱")
# --- 模擬資料庫 ---
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
if 'orders' not in st.session_state:
    st.session_state['orders'] = []

st.sidebar.title("👤 點餐登入")
user_name = st.sidebar.text_input("請輸入你的暱稱", "小明")

st.title("🍱 點餐魔術師 (Menu Magician)")
tab1, tab2, tab3 = st.tabs(["👉 我要點餐", "📊 訂單總表", "📝 給店家小抄"])

with tab1:
    st.subheader("第一步：搜尋店家")
    shop_name = st.selectbox("輸入或選擇店家", ["請選擇...", "50嵐", "阿明雞腿飯"])

    if shop_name in MENU_DB:
        menu = MENU_DB[shop_name]
        st.success(f"已載入 {shop_name} 的菜單")
        col1, col2 = st.columns(2)
        with col1:
            selected_item = st.radio("請選擇品項：", menu['items'])
            price = menu['prices'][selected_item]
            st.info(f"💰 價格：${price}")
        with col2:
            item_spec = "標準"
            if menu['type'] == "drink":
                sugar = st.selectbox("甜度", ["正常糖", "半糖", "微糖", "無糖"])
                ice = st.selectbox("冰塊", ["正常冰", "少冰", "微冰", "去冰"])
                item_spec = f"{sugar}/{ice}"
            custom_note = st.text_input("特殊備註", "")
            final_note = f"{item_spec}, {custom_note}" if custom_note else item_spec

        if st.button("➕ 加入訂單", use_container_width=True):
            new_order = {"姓名": user_name, "店家": shop_name, "餐點": selected_item, "規格": final_note, "價格": price, "已付款": False}
            st.session_state['orders'].append(new_order)
            st.toast("點餐成功！")

with tab2:
    if st.session_state['orders']:
        df = pd.DataFrame(st.session_state['orders'])
        st.dataframe(df, column_config={"已付款": st.column_config.CheckboxColumn("已付款?")}, use_container_width=True)
        st.markdown(f"### 總金額：${df['價格'].sum()}")
    else:
        st.info("暫無訂單")

with tab3:
    if st.session_state['orders']:
        df = pd.DataFrame(st.session_state['orders'])
        if shop_name != "請選擇...":
            sub_df = df[df['店家'] == shop_name]
            if not sub_df.empty:
                txt = f"老闆你好，我要點餐 ({shop_name})：\\n"
                for idx, row in sub_df.iterrows():
                    txt += f"- {row['餐點']} ({row['規格']})\\n"
                st.text_area("複製給老闆", txt)
"""
with open("app.py", "w") as f:
    f.write(code)

# 3. 取得通關密碼 (IP)
import urllib
print("請複製這個密碼 (IP):", urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n"))

# 4. 啟動網頁
print("點擊下方的網址，並貼上剛剛的密碼：")
!streamlit run app.py & npx localtunnel --port 8501
