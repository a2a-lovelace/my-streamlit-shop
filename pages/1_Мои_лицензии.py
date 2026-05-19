import streamlit as st
import datetime

# --- Должно быть первым ---
st.set_page_config(page_title="Мои лицензии", page_icon="🔑", layout="wide")

st.title("🔑 Мои лицензии")
st.markdown("---")

# Инициализация хранилища лицензий
if 'issued_licenses' not in st.session_state:
    st.session_state.issued_licenses = []

# --- Отображение всех лицензий ---
if st.session_state.issued_licenses:
    st.subheader("📋 Ваши активные лицензии")
    
    for idx, lic in enumerate(reversed(st.session_state.issued_licenses)):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{lic['product_name']}**")
                st.code(lic['key'], language="text")
            with col2:
                st.caption(f"Приобретена: {lic['date']}")
            
            # Кнопка проверки валидации (имитация API)
            if st.button("🔍 Проверить статус", key=f"check_{idx}"):
                st.success(f"✅ Лицензия {lic['key'][:8]}... активна и действительна")
else:
    st.info("📭 У вас пока нет лицензий. Совершите покупку в магазине!")
    # ИСПРАВЛЕНО: вместо st.page_link используем кнопку
    if st.button("🛒 Перейти в магазин", key="go_to_shop"):
        st.switch_page("app.py")

st.markdown("---")

# --- Проверка произвольного ключа (API-валидация) ---
st.subheader("🔍 Проверка лицензионного ключа")
st.caption("Имитация API-запроса к серверу для валидации ключа")

key_to_check = st.text_input("Введите лицензионный ключ для проверки", 
                              placeholder="Например: PRO-ABCD1234")

if st.button("Проверить ключ", key="validate_btn"):
    if key_to_check:
        # Ищем ключ в выданных
        found = False
        for lic in st.session_state.issued_licenses:
            if lic['key'] == key_to_check:
                found = True
                st.success(f"✅ Ключ действителен!\n\n"
                          f"**Товар:** {lic['product_name']}\n"
                          f"**Дата покупки:** {lic['date']}\n"
                          f"**Статус:** Активен")
                break
        
        if not found:
            st.error("❌ Ключ не найден в системе или истёк срок действия")
    else:
        st.warning("Введите ключ для проверки")

st.markdown("---")
st.caption("💡 Это демонстрационная версия. В реальном проекте ключи проверяются через API вашего ПО.")

# Кнопка возврата (ИСПРАВЛЕНО)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("← Вернуться в магазин", key="back_to_shop", use_container_width=True):
        st.switch_page("app.py")
