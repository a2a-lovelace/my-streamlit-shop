import streamlit as st
import random
import string

# --- Настройка страницы ---
st.set_page_config(page_title="Магазин лицензий", page_icon="🛒", layout="wide")

# --- Заголовок ---
st.title("🛒 Магазин цифровых товаров")
st.markdown("---")

# --- Инициализация корзины в session_state ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'promo_applied' not in st.session_state:
    st.session_state.promo_applied = False

# --- Товары (словарь) ---
products = {
    "pro": {"name": "💻 Лицензия PRO", "price": 1000, "description": "Бессрочная лицензия. Поддержка 1 год."},
    "team": {"name": "👥 Лицензия TEAM (3 пользователя)", "price": 2500, "description": "Для малого бизнеса. Поддержка 2 года."}
}

# --- Отображение товаров в две колонки ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(products["pro"]["name"])
    st.write(products["pro"]["description"])
    st.write(f"**Цена:** {products['pro']['price']} ₽")
    if st.button("➕ В корзину", key="add_pro"):
        st.session_state.cart.append("pro")
        st.success("Добавлено в корзину!")

with col2:
    st.subheader(products["team"]["name"])
    st.write(products["team"]["description"])
    st.write(f"**Цена:** {products['team']['price']} ₽")
    if st.button("➕ В корзину", key="add_team"):
        st.session_state.cart.append("team")
        st.success("Добавлено в корзину!")

st.markdown("---")

# --- Корзина и оформление ---
st.header("🛍️ Ваша корзина")

if not st.session_state.cart:
    st.info("Корзина пуста. Добавьте товары выше.")
else:
    # Считаем сумму и собираем список товаров с количеством
    total = 0
    cart_counts = {}
    for item in st.session_state.cart:
        cart_counts[item] = cart_counts.get(item, 0) + 1
        total += products[item]["price"]
    
    # Показываем корзину построчно
    for item_id, qty in cart_counts.items():
        item_total = products[item_id]["price"] * qty
        st.write(f"- {products[item_id]['name']} x{qty} = {item_total} ₽")
    
    # Промокод
    promo_code = st.text_input("🎟️ Промокод (ВВЕДИТЕ: DISCOUNT20)", key="promo_input")
    if promo_code == "DISCOUNT20" and not st.session_state.promo_applied:
        st.session_state.promo_applied = True
        st.success("✅ Промокод применён! Скидка 20%")
        st.rerun()
    
    if st.session_state.promo_applied:
        discount = total * 0.2
        final_total = total - discount
        st.write(f"**Скидка 20%:** -{discount:.0f} ₽")
        st.markdown(f"### Итого к оплате: {final_total:.0f} ₽")
    else:
        final_total = total
        st.markdown(f"### Итого к оплате: {final_total} ₽")
    
    # Кнопка оплаты
    if st.button("💳 Оформить заказ и оплатить", key="checkout"):
        with st.spinner("Обработка платежа..."):
            import time
            time.sleep(1.5)
        
        # --- ИСПРАВЛЕНО: генерируем ключ ДЛЯ КАЖДОГО экземпляра товара ---
        license_keys = []  # теперь это список, а не словарь
        for item_id in st.session_state.cart:
            key = f"{item_id.upper()}-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            license_keys.append({
                "product_name": products[item_id]["name"],
                "key": key
            })
        
        # Показываем результат
        st.success("✅ Платёж успешно проведён!")
        st.balloons()
        st.header("🔑 Ваши лицензионные ключи:")
        
        # Выводим каждый ключ отдельной строкой
        for license_item in license_keys:
            st.code(f"{license_item['product_name']}: {license_item['key']}", language="text")
        
        st.info("📧 Ключи также отправлены на вашу электронную почту.")
        
        # Очищаем корзину
        st.session_state.cart = []
        st.session_state.promo_applied = False
        st.stop()
