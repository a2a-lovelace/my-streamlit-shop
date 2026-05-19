import streamlit as st
import random
import string
import time
import json
from datetime import datetime
import os
from collections import Counter

# --- Конфигурация страницы ---
st.set_page_config(
    page_title="Магазин лицензий",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Константы ---
DB_FILE = "licenses_db.json"
STUDENT_NAME = "⭐ Марина С.⭐"  # Замените на свои данные
STUDENT_GROUP = "122-МКо"  # Замените на свои данные
DISCIPLINE = "Современное Web-программирование"
UNIVERSITY = "СГУ им. Питирима Сорокина"  # Замените при необходимости

# --- CSS для футера ---
st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #f0f2f6;
    color: #262730;
    text-align: center;
    padding: 15px 10px;
    font-size: 14px;
    border-top: 2px solid #e0e0e0;
    z-index: 999;
}
.footer strong {
    color: #ff4b4b;
}
.footer .divider {
    margin: 0 10px;
    color: #999;
}
.main-content {
    margin-bottom: 80px;
}
</style>
""", unsafe_allow_html=True)

# --- Работа с "базой данных" ---
def load_db():
    """Загрузка базы данных лицензий"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "licenses" not in data:
                data["licenses"] = []
            return data
    return {"licenses": []}

def save_db(data):
    """Сохранение базы данных лицензий"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_key_unique(key):
    """Проверка уникальности ключа"""
    db = load_db()
    return not any(lic["key"] == key for lic in db["licenses"])

def get_licenses_count():
    """Безопасное получение количества лицензий"""
    try:
        db = load_db()
        return len(db.get("licenses", []))
    except:
        return 0

# --- Инициализация session_state ---
def init_session_state():
    """Инициализация всех переменных сессии"""
    defaults = {
        'cart': [],
        'promo_applied': None,
        'show_licenses': False,
        'purchase_completed': False,
        'last_purchase_licenses': [],
        'licenses_count': get_licenses_count(),
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Промокоды ---
PROMOCODES = {
    "DISCOUNT20": {"discount": 0.20, "name": "Скидка 20%", "min_purchase": 1500},
    "WELCOME10": {"discount": 0.10, "name": "Приветственная скидка 10%", "min_purchase": 0},
    "TEAMUP": {"discount": 0.25, "name": "Командная скидка 25%", "min_purchase": 3000}
}

# --- Товары ---
PRODUCTS = {
    "pro": {
        "id": "pro",
        "name": "💻 Лицензия PRO",
        "price": 1000,
        "description": "Расширенные возможности, приоритетная поддержка",
        "validity": "1 год",
        "features": ["Приоритетная поддержка", "Расширенные функции", "API доступ"]
    },
    "team": {
        "id": "team",
        "name": "👥 Лицензия TEAM",
        "price": 2500,
        "description": "До 10 пользователей, командная работа",
        "validity": "1 год",
        "features": ["До 10 пользователей", "Командная работа", "Админ-панель", "Всё из PRO"]
    }
}

# --- Функции генерации и покупки ---
def generate_license_key(product_type):
    """Генерация уникального лицензионного ключа"""
    max_attempts = 100
    for _ in range(max_attempts):
        segments = [
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ]
        key = f"{product_type.upper()}-{segments[0]}-{segments[1]}-{segments[2]}"
        if is_key_unique(key):
            return key
    raise Exception("Не удалось сгенерировать уникальный ключ")

def process_purchase(cart_items, discount_percent=0):
    """Обработка покупки и генерация лицензий"""
    db = load_db()
    new_licenses = []
    current_id = len(db["licenses"])
    
    for item in cart_items:
        current_id += 1
        key = generate_license_key(item)
        license_data = {
            "id": current_id,
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
    st.session_state.licenses_count = len(db["licenses"])
    return new_licenses

def get_all_licenses():
    """Получение всех лицензий из БД"""
    try:
        return load_db().get("licenses", [])
    except:
        return []

# --- Боковое меню ---
with st.sidebar:
    st.title("📋 Навигация")
    
    # Основная навигация
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 Магазин", use_container_width=True, 
                    type="primary" if not st.session_state.show_licenses else "secondary"):
            st.session_state.show_licenses = False
            st.session_state.purchase_completed = False
            st.rerun()
    
    with col2:
        if st.button("🔑 Лицензии", use_container_width=True,
                    type="primary" if st.session_state.show_licenses else "secondary"):
            st.session_state.show_licenses = True
            st.rerun()
    
    st.markdown("---")
    
    # Информационная панель
    st.subheader("📊 Информация")
    
    current_licenses_count = get_licenses_count()
    cart_count = len(st.session_state.cart)
    
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("🛍️ В корзине", cart_count)
    with metric_col2:
        st.metric("🔑 Лицензий", current_licenses_count)
    
    if cart_count > 0:
        total = sum(PRODUCTS[item]["price"] for item in st.session_state.cart)
        st.progress(min(cart_count / 5, 1.0), text=f"Сумма: {total} ₽")
    
    st.markdown("---")
    
    # Информация о проекте в сайдбаре
    with st.expander("ℹ️ О проекте"):
        st.markdown(f"""
        **Дисциплина:**  
        {DISCIPLINE}
        
        **Студент:**  
        {STUDENT_NAME}
        
        **Группа:**  
        {STUDENT_GROUP}
        
        **Университет:**  
        {UNIVERSITY}
        
        **Тема проекта:**  
        Разработка интернет-магазина цифровых товаров с системой электронных лицензий
        """)
    
    # Быстрые действия
    if cart_count > 0:
        st.caption("⚡ Быстрые действия:")
        if st.button("🗑️ Очистить корзину", use_container_width=True, key="sidebar_clear"):
            st.session_state.cart = []
            st.session_state.promo_applied = None
            st.rerun()

# --- Основной контент ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- СТРАНИЦА МАГАЗИНА ---
if not st.session_state.show_licenses:
    st.title("🛒 Магазин цифровых лицензий")
    st.caption("💻 Покупайте лицензии мгновенно • Автоматическая доставка • Поддержка 24/7")
    
    # Если только что совершили покупку - показываем ключи сверху
    if st.session_state.purchase_completed and st.session_state.last_purchase_licenses:
        st.success("✅ Платёж успешно проведён!")
        st.balloons()
        
        with st.container(border=True):
            st.subheader("🎉 Ваши новые лицензионные ключи")
            st.info("📧 Ключи также отправлены на вашу электронную почту")
            
            for lic in st.session_state.last_purchase_licenses:
                lic_col1, lic_col2 = st.columns([3, 1])
                with lic_col1:
                    st.markdown(f"**{lic['product_name']}**")
                    st.code(lic['key'], language="text")
                with lic_col2:
                    st.caption(f"ID: {lic['id']}")
                    st.caption(f"📅 {lic['date']}")
            
            if st.button("✅ Понятно, продолжить покупки", use_container_width=True):
                st.session_state.purchase_completed = False
                st.session_state.last_purchase_licenses = []
                st.rerun()
        
        st.markdown("---")
    
    # Показ товаров
    st.subheader("📦 Доступные товары")
    
    col1, col2 = st.columns(2)
    
    for col, (product_id, product) in zip([col1, col2], PRODUCTS.items()):
        with col:
            with st.container(border=True):
                st.markdown(f"### {product['name']}")
                st.write(f"*{product['description']}*")
                
                st.markdown("**Возможности:**")
                for feature in product['features']:
                    st.write(f"  ✓ {feature}")
                
                st.markdown(f"**Срок действия:** {product['validity']}")
                st.markdown(f"## {product['price']} ₽")
                
                if st.button("➕ Добавить в корзину", 
                           key=f"add_{product_id}", 
                           use_container_width=True,
                           type="secondary"):
                    st.session_state.cart.append(product_id)
                    st.toast(f"✅ {product['name']} добавлена!", icon="🛒")
                    st.session_state.licenses_count = get_licenses_count()
                    time.sleep(0.3)
                    st.rerun()
    
    st.markdown("---")
    
    # Корзина
    st.header("🛍️ Корзина")
    
    if not st.session_state.cart:
        st.info("🛒 Ваша корзина пуста. Добавьте товары для оформления заказа.")
    else:
        total = sum(PRODUCTS[item]["price"] for item in st.session_state.cart)
        cart_counter = Counter(st.session_state.cart)
        
        st.subheader("📋 Состав заказа:")
        
        for product_id, quantity in cart_counter.items():
            product = PRODUCTS[product_id]
            with st.container(border=True):
                cols = st.columns([4, 1, 1])
                with cols[0]:
                    st.write(f"**{product['name']}**")
                    st.caption(f"{product['price']} ₽ × {quantity} шт.")
                with cols[1]:
                    st.write(f"**{product['price'] * quantity} ₽**")
                with cols[2]:
                    if st.button("❌", key=f"remove_{product_id}", help=f"Удалить все {product['name']}"):
                        st.session_state.cart = [item for item in st.session_state.cart if item != product_id]
                        st.rerun()
        
        st.markdown("---")
        
        # Промокод
        st.subheader("🎟️ Промокод")
        promo_col1, promo_col2 = st.columns([2, 1])
        
        with promo_col1:
            promo_code = st.text_input(
                "Введите промокод",
                placeholder="WELCOME10, DISCOUNT20, TEAMUP",
                key="promo_input",
                label_visibility="collapsed"
            )
        
        discount_percent = 0
        discount_amount = 0
        
        if promo_code:
            if promo_code in PROMOCODES:
                promo_data = PROMOCODES[promo_code]
                if total >= promo_data.get("min_purchase", 0):
                    discount_percent = promo_data["discount"]
                    discount_amount = total * discount_percent
                    with promo_col2:
                        st.success(f"✅ {promo_data['name']}")
                    st.session_state.promo_applied = promo_code
                else:
                    with promo_col2:
                        st.error(f"Мин. сумма: {promo_data['min_purchase']} ₽")
            else:
                with promo_col2:
                    st.error("❌ Недействителен")
                st.session_state.promo_applied = None
        
        # Итоговая сумма
        st.markdown("---")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Сумма заказа", f"{total} ₽")
        with metric_col2:
            st.metric("Скидка", f"-{discount_amount:.0f} ₽" if discount_amount > 0 else "0 ₽",
                     delta=f"-{discount_percent*100:.0f}%" if discount_percent > 0 else None)
        with metric_col3:
            final_total = total - discount_amount
            st.metric("💰 Итого", f"{final_total:.0f} ₽")
        
        st.markdown("---")
        
        # Кнопки действий
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🗑️ Очистить", use_container_width=True, key="main_clear"):
                st.session_state.cart = []
                st.session_state.promo_applied = None
                st.rerun()
        
        with col3:
            if st.button("💳 Оплатить", use_container_width=True, type="primary", key="checkout"):
                with st.spinner("🔄 Обрабатываем платёж..."):
                    time.sleep(1.2)
                
                new_licenses = process_purchase(st.session_state.cart, discount_percent)
                st.session_state.last_purchase_licenses = new_licenses
                st.session_state.purchase_completed = True
                st.session_state.cart = []
                st.session_state.promo_applied = None
                st.rerun()

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
        pro_licenses = [l for l in all_licenses if l["product_id"] == "pro"]
        team_licenses = [l for l in all_licenses if l["product_id"] == "team"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Всего", len(all_licenses))
        with col2:
            st.metric("🟢 Активных", len(active_licenses))
        with col3:
            st.metric("💻 PRO", len(pro_licenses))
        with col4:
            st.metric("👥 TEAM", len(team_licenses))
        
        st.markdown("---")
        
        # Поиск и фильтрация
        st.subheader("📋 Список лицензий")
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search = st.text_input("🔍 Поиск по ключу или названию", placeholder="Введите часть ключа...")
        with search_col2:
            status_filter = st.selectbox("Статус", ["Все", "active", "inactive"])
        
        # Фильтрация
        filtered_licenses = all_licenses
        if search:
            search = search.lower()
            filtered_licenses = [l for l in filtered_licenses 
                               if search in l["key"].lower() or search in l["product_name"].lower()]
        if status_filter != "Все":
            filtered_licenses = [l for l in filtered_licenses if l["status"] == status_filter]
        
        # Отображение лицензий
        if not filtered_licenses:
            st.info("🔍 Лицензии не найдены. Попробуйте изменить параметры поиска.")
        else:
            for idx, lic in enumerate(reversed(filtered_licenses)):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        status_icon = "🟢" if lic["status"] == "active" else "🔴"
                        st.markdown(f"### {status_icon} {lic['product_name']}")
                        st.code(lic['key'], language="text")
                        
                        info_col1, info_col2, info_col3 = st.columns(3)
                        with info_col1:
                            st.caption(f"📅 Приобретена: {lic['date']}")
                        with info_col2:
                            st.caption(f"⏱ Срок: {lic['validity']}")
                        with info_col3:
                            st.caption(f"🆔 ID: {lic['id']}")
                    
                    with col2:
                        with st.container(border=True):
                            st.markdown(f"**Статус:** {lic['status'].upper()}")
                            
                            if st.button("🔍 Проверить", key=f"check_{lic['id']}", use_container_width=True):
                                if lic["status"] == "active":
                                    st.success("✅ Лицензия действительна")
                                    st.balloons()
                                else:
                                    st.error("❌ Лицензия неактивна")
                            
                            if st.button("📋 Копировать", key=f"copy_{lic['id']}", use_container_width=True):
                                st.toast(f"✅ Ключ скопирован!")
        
        # Экспорт
        st.markdown("---")
        with st.expander("💾 Управление данными"):
            st.caption("Лицензии хранятся локально в файле `licenses_db.json`")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Обновить список", use_container_width=True):
                    st.session_state.licenses_count = get_licenses_count()
                    st.rerun()
            with col2:
                st.download_button(
                    "📥 Экспорт в JSON",
                    json.dumps(all_licenses, ensure_ascii=False, indent=2),
                    "licenses_backup.json",
                    "application/json",
                    use_container_width=True
                )

st.markdown('</div>', unsafe_allow_html=True)

# --- ФУТЕР С ИНФОРМАЦИЕЙ О СТУДЕНТЕ ---
st.markdown(f"""
<div class="footer">
    <strong>{DISCIPLINE}</strong>
    <span class="divider">|</span>
    Студент: <strong>{STUDENT_NAME}</strong>
    <span class="divider">|</span>
    Группа: <strong>{STUDENT_GROUP}</strong>
    <span class="divider">|</span>
    {UNIVERSITY} © {datetime.now().year}
</div>
""", unsafe_allow_html=True)
