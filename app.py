import streamlit as st
import random
import string

# --- Настройка страницы ---
st.set_page_config(page_title="Цифровой магазин", page_icon="🛒", layout="centered")

# --- Заголовок ---
st.title("🛒 Магазин цифровых товаров")

# --- Товар ---
with st.container(border=True):
    st.subheader("💻 Лицензия на ПО \"SuperPro\"")
    st.write("Бессрочная лицензия для вашего бизнеса.")
    price = 1000

    # Кнопка "Купить"
    if st.button("💳 Купить лицензию", key="buy_btn"):
        # Имитация успешной оплаты
        with st.spinner('Обработка платежа...'):
            # Здесь в реальном проекте был бы API-запрос к платежной системе
            import time
            time.sleep(1)

        # Генерация уникального лицензионного ключа
        license_key = 'SUPER-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # --- Вывод результата (автоматическая доставка) ---
        st.success("✅ Платёж успешно проведён!")
        st.balloons() # Маленький бонус для радости 🎈
        st.markdown(f"### Ваш лицензионный ключ:")
        st.code(license_key, language="text")
        st.info("📧 Ключ также отправлен на вашу электронную почту.")
