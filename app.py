import streamlit as st
import random
import string
import json

# --- ДОЛЖНО БЫТЬ САМЫМ ПЕРВЫМ ---
st.set_page_config(page_title="Магазин лицензий", page_icon="🛒", layout="wide")

# --- Инициализация session_state (ДО ВСЕГО ОСТАЛЬНОГО) ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'promo_code_applied' not in st.session_state:
    st.session_state.promo_code_applied = None  # храним название применённого промокода
if 'issued_licenses' not in st.session_state:
    st.session_state.issued_licenses = []  # список выданных ключей

# --- Загрузка корзины из localStorage (JavaScript) ---
st.markdown("""
    <script>
        // Загружаем корзину при старте
        let savedCart = localStorage.getItem('cart');
        if (savedCart) {
            // Передаём данные в Streamlit через скрытый элемент
            const input = document.createElement('input');
            input.id = 'cart_from_storage';
            input.value = savedCart;
            input.style.display = 'none';
            document.body.appendChild(input);
        }
    </script>
""", unsafe_allow_html=True)

# Пытаемся прочитать данные из скрытого поля (если есть)
import streamlit.components.v1 as components
# Простой способ: проверяем параметры URL
query_params = st.query_params
if 'load_cart' in query_params:
    try:
        loaded_cart = json.loads(query_params['load_cart'])
        if loaded_cart and not st.session_state.cart:
            st.session_state.cart = loaded_cart
            st.success("🔄 Корзина восстановлена!")
    except:
        pass

# --- Словарь промокодов ---
promocodes = {
    "DISCOUNT20": 0.20,   # 20% скидка
    "WELCOME10": 0.10,    # 10% скидка
    "TEAMUP": 0.25        # 25% скидка
}

# --- Товары ---
products = {
    "pro": {"name": "💻 Лицензия PRO", "price": 1000, "description": "Бессрочная лицензия. Поддержка 1 год."},
    "team": {"name": "👥 Лицензия TEAM (3 пользователя)", "price": 2500, "description": "Для малого бизнеса. Поддержка 2 года."}
}

# --- Заголовок ---
st.title("🛒 Магазин цифровых товаров")
st.markdown("---")

# --- Кнопка сохранения корзины (добавим для удобства) ---
col_save, _ = st.columns([1, 5])
with col_save:
    if st.button("💾 Сохранить корзину", key="save_cart"):
        cart_json = json.dumps(st.session_state.cart)
        # Сохраняем в localStorage через JS
        st.markdown(f"""
            <script>
                localStorage.setItem('cart', '{cart_json}');
                alert('Корзина сохранена!');
            </script>
        """, unsafe_allow_html=True)
        st.success("✅ Корзина сохранена! При следующем заходе она восстановится.")

# --- Отображение товаров ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(products["pro"]["name"])
    st.write(products["pro"]["description"])
    st.write(f"**Цена:** {products['pro']['price']} ₽")
    if st.button("➕ В корзину", key="add_pro"):
        st.session_state.cart.append("pro")
        st.success("✅ Добавлено в корзину!")
        st.rerun()

with col2:
    st.subheader(products["team"]["name"])
    st.write(products["team"]["description"])
    st.write(f"**Цена:** {products['team']['price']} ₽")
    if st.button("➕ В корзину", key="add_team"):
        st.session_state.cart.append("team")
        st.success("✅ Добавлено в корзину!")
        st.rerun()

st.markdown("---")

# --- Корзина ---
st.header("🛍️ Ваша корзина")

if not st.session_state.cart:
    st.info("Корзина пуста. Добавьте товары выше.")
else:
    # Считаем сумму
    total = 0
    cart_counts = {}
    for item in st.session_state.cart:
        cart_counts[item] = cart_counts.get(item, 0) + 1
        total += products[item]["price"]
    
    # Показываем корзину
    for item_id, qty in cart_counts.items():
        item_total = products[item_id]["price"] * qty
        st.write(f"- {products[item_id]['name']} x{qty} = {item_total} ₽")
    
    # Промокод (НОВАЯ ВЕРСИЯ)
    promo_input = st.text_input("🎟️ Промокод", key="promo_input", 
                                 placeholder="Введите DISCOUNT20, WELCOME10 или TEAMUP")
    
    discount_rate = 0
    if promo_input and promo_input in promocodes:
        discount_rate = promocodes[promo_input]
        if st.session_state.promo_code_applied != promo_input:
            st.session_state.promo_code_applied = promo_input
            st.success(f"✅ Промокод {promo_input} применён! Скидка {discount_rate*100:.0f}%")
            st.rerun()
    elif promo_input and promo_input not in promocodes:
        st.error("❌ Неверный промокод")
    
    # Применяем скидку
    if st.session_state.promo_code_applied in promocodes:
        discount_rate = promocodes[st.session_state.promo_code_applied]
    
    discount = total * discount_rate
    final_total = total - discount
    
    if discount > 0:
        st.write(f"**Скидка:** -{discount:.0f} ₽")
    st.markdown(f"### Итого к оплате: {final_total:.0f} ₽")
    
    # Очистка корзины
    if st.button("🗑️ Очистить корзину", key="clear_cart"):
        st.session_state.cart = []
        st.session_state.promo_code_applied = None
        st.rerun()
    
    # Кнопка оплаты
    if st.button("💳 Оформить заказ и оплатить", key="checkout"):
        with st.spinner("Обработка платежа..."):
            import time
            time.sleep(1.5)
        
        # Генерируем ключи для КАЖДОГО товара
        license_keys = []
        for item_id in st.session_state.cart:
            key = f"{item_id.upper()}-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            license_keys.append({
                "product_name": products[item_id]["name"],
                "key": key
            })
            # Сохраняем в историю лицензий
            st.session_state.issued_licenses.append({
                "product_name": products[item_id]["name"],
                "key": key,
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
               # Показываем результат
        st.success("✅ Платёж успешно проведён!")
        st.balloons()
        st.header("🔑 Ваши лицензионные ключи:")
        
        for license_item in license_keys:
            st.code(f"{license_item['product_name']}: {license_item['key']}", language="text")
        
        st.info("📧 Ключи также отправлены на вашу электронную почту.")
        
        # --- ИСПРАВЛЕННАЯ НАВИГАЦИЯ ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛒 Продолжить покупки", key="continue_shopping"):
                st.rerun()
        with col2:
            # Проверяем, существует ли страница с лицензиями
            try:
                st.switch_page("pages/1_Мои_лицензии.py")
            except:
                st.markdown("[🔑 Перейти к моим лицензиям](https://[ТВОЙ_АДРЕС].streamlit.app/?page=licenses)")
        
        # Очищаем корзину
        st.session_state.cart = []
        st.session_state.promo_code_applied = None
        st.stop()
