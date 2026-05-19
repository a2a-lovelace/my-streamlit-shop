import streamlit as st
import random
import string
import time

st.set_page_config(page_title="Магазин лицензий", page_icon="🛒", layout="wide")

# Инициализация
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'promo_code_applied' not in st.session_state:
    st.session_state.promo_code_applied = None
if 'issued_licenses' not in st.session_state:
    st.session_state.issued_licenses = []
if 'show_licenses' not in st.session_state:
    st.session_state.show_licenses = False

# Промокоды
promocodes = {"DISCOUNT20": 0.20, "WELCOME10": 0.10, "TEAMUP": 0.25}

# Товары
products = {
    "pro": {"name": "💻 Лицензия PRO", "price": 1000},
    "team": {"name": "👥 Лицензия TEAM", "price": 2500}
}

# --- МЕНЮ НАВИГАЦИИ ---
st.sidebar.title("📋 Меню")
if st.sidebar.button("🛒 Магазин"):
    st.session_state.show_licenses = False
    st.rerun()
if st.sidebar.button("🔑 Мои лицензии"):
    st.session_state.show_licenses = True
    st.rerun()

# --- СТРАНИЦА МАГАЗИНА ---
if not st.session_state.show_licenses:
    st.title("🛒 Магазин цифровых товаров")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(products["pro"]["name"])
        st.write(f"Цена: {products['pro']['price']} ₽")
        if st.button("➕ В корзину", key="add_pro"):
            st.session_state.cart.append("pro")
            st.success("Добавлено!")
            st.rerun()
    
    with col2:
        st.subheader(products["team"]["name"])
        st.write(f"Цена: {products['team']['price']} ₽")
        if st.button("➕ В корзину", key="add_team"):
            st.session_state.cart.append("team")
            st.success("Добавлено!")
            st.rerun()
    
    st.markdown("---")
    st.header("🛍️ Корзина")
    
    if not st.session_state.cart:
        st.info("Корзина пуста")
    else:
        # Считаем сумму
        total = 0
        for item in st.session_state.cart:
            total += products[item]["price"]
        
        # Показываем содержимое корзины
        for item in st.session_state.cart:
            st.write(f"- {products[item]['name']}: {products[item]['price']} ₽")
        
        # Промокод
        promo = st.text_input("🎟️ Промокод", placeholder="DISCOUNT20, WELCOME10, TEAMUP")
        discount = 0
        if promo and promo in promocodes:
            discount = total * promocodes[promo]
            st.success(f"✅ Промокод {promo} применён! Скидка {promocodes[promo]*100:.0f}%")
        
        final_total = total - discount
        if discount > 0:
            st.write(f"**Скидка:** -{discount:.0f} ₽")
        st.markdown(f"### Итого к оплате: {final_total:.0f} ₽")
        
        # Кнопка очистки
        if st.button("🗑️ Очистить корзину"):
            st.session_state.cart = []
            st.rerun()
        
        # Кнопка оплаты
        if st.button("💳 Оплатить", key="checkout"):
            with st.spinner("Обработка платежа..."):
                time.sleep(1.5)
            
            # Сохраняем лицензии (каждый товар -> свой ключ)
            for item in st.session_state.cart:
                key = f"{item.upper()}-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                st.session_state.issued_licenses.append({
                    "product_name": products[item]["name"],
                    "key": key,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            st.success("✅ Платёж успешно проведён!")
            st.balloons()
            
            # Показываем новые ключи
            st.subheader("🔑 Ваши лицензионные ключи:")
            new_keys = st.session_state.issued_licenses[-len(st.session_state.cart):]
            for lic in new_keys:
                st.code(f"{lic['product_name']}: {lic['key']}", language="text")
            
            st.info("📧 Ключи также отправлены на вашу электронную почту.")
            
            # Очищаем корзину
            st.session_state.cart = []
            st.session_state.promo_code_applied = None

# --- СТРАНИЦА МОИ ЛИЦЕНЗИИ ---
else:
    st.title("🔑 Мои лицензии")
    
    if not st.session_state.issued_licenses:
        st.info("📭 У вас пока нет лицензий. Совершите покупку в магазине!")
    else:
        for idx, lic in enumerate(reversed(st.session_state.issued_licenses)):
            with st.container(border=True):
                st.markdown(f"**{lic['product_name']}**")
                st.code(lic['key'], language="text")
                st.caption(f"Приобретена: {lic['date']}")
                
                if st.button("🔍 Проверить статус", key=f"check_{idx}"):
                    st.success(f"✅ Лицензия {lic['key'][:8]}... активна и действительна")
        
        st.markdown("---")
        st.caption("💡 Это демонстрационная версия. В реальном проекте ключи проверяются через API.")
