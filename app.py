import streamlit as st
import random
import string
import time
import json
from datetime import datetime
import os

st.set_page_config(page_title="Магазин лицензий", page_icon="🛒", layout="wide")

# --- Работа с "базой данных" (JSON-файл) ---
DB_FILE = "licenses_db.json"

def load_db():
    """Загрузка базы данных лицензий"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"licenses": []}

def save_db(data):
    """Сохранение базы данных лицензий"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_key_unique(key):
    """Проверка уникальности ключа"""
    db = load_db()
    for lic in db["licenses"]:
        if lic["key"] == key:
            return False
    return True

# --- Инициализация session_state ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'promo_applied' not in st.session_state:
    st.session_state.promo_applied = None
if 'show_licenses' not in st.session_state:
    st.session_state.show_licenses = False
if 'purchase_completed' not in st.session_state:
    st.session_state.purchase_completed = False

# --- Промокоды ---
PROMOCODES = {
    "DISCOUNT20": {"discount": 0.20, "name": "Скидка 20%"},
    "WELCOME10": {"discount": 0.10, "name": "Приветственная скидка 10%"},
    "TEAMUP": {"discount": 0.25, "name": "Командная скидка 25%"}
}

# --- Товары ---
PRODUCTS = {
    "pro": {
        "name": "💻 Лицензия PRO",
        "price": 1000,
        "description": "Расширенные возможности, приоритетная поддержка",
        "validity": "1 год"
    },
    "team": {
        "name": "👥 Лицензия TEAM",
        "price": 2500,
        "description": "До 10 пользователей, командная работа",
        "validity": "1 год"
    }
}

# --- Функции ---
def generate_license_key(product_type):
    """Генерация уникального лицензионного ключа"""
    while True:
        segments = [
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ]
        key = f"{product_type.upper()}-{segments[0]}-{segments[1]}-{segments[2]}"
        if is_key_unique(key):
            return key

def process_purchase(cart_items, discount_percent=0):
    """Обработка покупки и генерация лицензий"""
    db = load_db()
    new_licenses = []
    
    for item in cart_items:
        key = generate_license_key(item)
        license_data = {
            "id": len(db["licenses"]) + 1,
            "product_id": item,
            "product_name": PRODUCTS[item]["name"],
            "key": key,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "validity": PRODUCTS[item]["validity"],
            "status": "active",
            "discount_applied": discount_percent
        }
        db["licenses"].append(license_data)
        new_licenses.append(license_data)
    
    save_db(db)
    return new_licenses

def get_all_licenses():
    """Получение всех лицензий из БД"""
    return load_db()["licenses"]

# --- Боковое меню ---
with st.sidebar:
    st.title("📋 Навигация")
    
    if st.button("🛒 Магазин", use_container_width=True):
        st.session_state.show_licenses = False
        st.session_state.purchase_completed = False
        st.rerun()
    
    if st.button("🔑 Мои лицензии", use_container_width=True):
        st.session_state.show_licenses = True
        st.rerun()
    
    st.markdown("---")
    
    # Информация о корзине в сайдбаре
    cart_count = len(st.session_state.cart)
    if cart_count > 0:
        st.info(f"🛍️ Товаров в корзине: {cart_count}")
    
    # Статистика
    all_licenses = get_all_licenses()
    if all_licenses:
        st.metric("Всего выдано лицензий", len(all_licenses))

# --- СТРАНИЦА МАГАЗИНА ---
if not st.session_state.show_licenses:
    st.title("🛒 Магазин цифровых лицензий")
    
    # Показ товаров в карточках
    st.subheader("📦 Доступные товары")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown(f"### {PRODUCTS['pro']['name']}")
            st.write(f"*{PRODUCTS['pro']['description']}*")
            st.markdown(f"**Срок действия:** {PRODUCTS['pro']['validity']}")
            st.markdown(f"## {PRODUCTS['pro']['price']} ₽")
            
            if st.button("➕ Добавить в корзину", key="add_pro", use_container_width=True):
                st.session_state.cart.append("pro")
                st.toast(f"✅ {PRODUCTS['pro']['name']} добавлена в корзину!", icon="🛒")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown(f"### {PRODUCTS['team']['name']}")
            st.write(f"*{PRODUCTS['team']['description']}*")
            st.markdown(f"**Срок действия:** {PRODUCTS['team']['validity']}")
            st.markdown(f"## {PRODUCTS['team']['price']} ₽")
            
            if st.button("➕ Добавить в корзину", key="add_team", use_container_width=True):
                st.session_state.cart.append("team")
                st.toast(f"✅ {PRODUCTS['team']['name']} добавлена в корзину!", icon="🛒")
                time.sleep(0.5)
                st.rerun()
    
    st.markdown("---")
    
    # Корзина
    st.header("🛍️ Корзина")
    
    if not st.session_state.cart:
        st.info("🛒 Ваша корзина пуста. Добавьте товары для оформления заказа.")
    else:
        # Подсчет суммы
        total = sum(PRODUCTS[item]["price"] for item in st.session_state.cart)
        
        # Отображение товаров в корзине с возможностью удаления
        st.subheader("📋 Состав заказа:")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            for idx, item in enumerate(st.session_state.cart):
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.write(f"**{PRODUCTS[item]['name']}** — {PRODUCTS[item]['price']} ₽")
                    with cols[1]:
                        if st.button("❌", key=f"remove_{idx}", help="Удалить из корзины"):
                            st.session_state.cart.pop(idx)
                            st.rerun()
        
        st.markdown("---")
        
        # Промокод
        st.subheader("🎟️ Промокод")
        promo_code = st.text_input(
            "Введите промокод",
            placeholder="Например: WELCOME10, DISCOUNT20, TEAMUP",
            key="promo_input"
        )
        
        discount_percent = 0
        discount_amount = 0
        
        if promo_code:
            if promo_code in PROMOCODES:
                discount_percent = PROMOCODES[promo_code]["discount"]
                discount_amount = total * discount_percent
                st.success(f"✅ Промокод **{promo_code}** применён! ({PROMOCODES[promo_code]['name']})")
                st.session_state.promo_applied = promo_code
            else:
                st.error("❌ Недействительный промокод")
                st.session_state.promo_applied = None
        
        # Итоговая сумма
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Сумма заказа", f"{total} ₽")
        with col2:
            st.metric("Скидка", f"-{discount_amount:.0f} ₽" if discount_amount > 0 else "0 ₽")
        with col3:
            final_total = total - discount_amount
            st.metric("💰 Итого к оплате", f"{final_total:.0f} ₽", delta=None)
        
        st.markdown("---")
        
        # Кнопки действий
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Очистить корзину", use_container_width=True):
                st.session_state.cart = []
                st.session_state.promo_applied = None
                st.rerun()
        
        with col2:
            if st.button("💳 Оплатить и получить лицензии", use_container_width=True, type="primary"):
                with st.spinner("🔄 Обработка платежа..."):
                    time.sleep(1.5)
                
                # Генерация лицензий
                new_licenses = process_purchase(
                    st.session_state.cart,
                    discount_percent
                )
                
                st.session_state.purchase_completed = True
                
                # Показ результатов
                st.success("✅ Платёж успешно проведён!")
                st.balloons()
                
                st.markdown("---")
                st.subheader("🎉 Ваши лицензионные ключи")
                st.info("📧 Ключи также отправлены на вашу электронную почту")
                
                for lic in new_licenses:
                    with st.container(border=True):
                        st.markdown(f"**{lic['product_name']}**")
                        st.code(lic['key'], language="text")
                        
                        # Кнопка копирования
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("📋 Копировать", key=f"copy_{lic['id']}"):
                                st.write(f"```\n{lic['key']}\n```")
                                st.toast("✅ Ключ скопирован в буфер обмена!")
                
                # Очистка корзины после покупки
                st.session_state.cart = []
                st.session_state.promo_applied = None

# --- СТРАНИЦА МОИ ЛИЦЕНЗИИ ---
else:
    st.title("🔑 Мои лицензии")
    
    all_licenses = get_all_licenses()
    
    if not all_licenses:
        st.info("📭 У вас пока нет приобретённых лицензий.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🛒 Перейти в магазин", use_container_width=True, type="primary"):
                st.session_state.show_licenses = False
                st.rerun()
    else:
        # Статистика
        active_licenses = [l for l in all_licenses if l["status"] == "active"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего лицензий", len(all_licenses))
        with col2:
            st.metric("Активных", len(active_licenses))
        with col3:
            st.metric("Товаров в корзине", len(st.session_state.cart))
        
        st.markdown("---")
        
        # Список лицензий
        st.subheader("📋 Список приобретённых лицензий")
        
        for idx, lic in enumerate(reversed(all_licenses)):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    status_icon = "🟢" if lic["status"] == "active" else "🔴"
                    st.markdown(f"### {status_icon} {lic['product_name']}")
                    st.code(lic['key'], language="text")
                    
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.caption(f"📅 Приобретена: {lic['date']}")
                    with info_col2:
                        st.caption(f"⏱ Срок действия: {lic['validity']}")
                
                with col2:
                    with st.container(border=True):
                        st.markdown(f"**Статус:** {lic['status'].upper()}")
                        
                        if st.button("🔍 Проверить", key=f"check_{idx}", use_container_width=True):
                            if lic["status"] == "active":
                                st.success("✅ Лицензия действительна")
                            else:
                                st.error("❌ Лицензия недействительна")
                        
                        # Кнопка копирования
                        if st.button("📋 Копировать ключ", key=f"copy_lic_{idx}", use_container_width=True):
                            st.toast(f"✅ Ключ скопирован: {lic['key'][:20]}...")
        
        # Экспорт
        st.markdown("---")
        st.caption("💾 Для резервного копирования лицензии хранятся в файле `licenses_db.json`")

# --- Подвал ---
st.markdown("---")
st.caption("© 2026 Магазин цифровых лицензий | Демонстрационная версия | Все права защищены")
