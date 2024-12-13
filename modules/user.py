import streamlit as st
import bcrypt
from db import get_db, close_db

def hash_password(password):
    """Хеширует пароль с использованием bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Проверяет, совпадает ли пароль с хешем."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

class UserManager:
    def __init__(self):
        self.conn, self.cursor = get_db()

    def __del__(self):
        close_db(self.conn, self.cursor)

    def register(self):
        st.subheader("Регистрация")
        name = st.text_input("Имя", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Пароль", type="password", key="signup_password")
        role = st.selectbox("Выберите вашу роль", ["Участник хора", "Дирижер"], key="signup_role")

        if st.button("Зарегистрироваться"):
            try:
                role_value = "participant" if role == "Участник хора" else "conductor"
                password_hash = hash_password(password)

                query = """
                    INSERT INTO users (name, email, password_hash, role)
                    VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(query, (name, email, password_hash, role_value))
                self.conn.commit()
                st.success(f"Аккаунт для {name} создан успешно как {role}!")
            except Exception as e:
                st.error(f"Ошибка при регистрации: {e}")

    def login(self):
        st.subheader("Вход")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Пароль", type="password", key="login_password")

        if st.button("Войти"):
            try:
                query = """
                    SELECT id, name, role, password_hash
                    FROM users
                    WHERE email = %s
                """
                self.cursor.execute(query, (email,))
                user = self.cursor.fetchone()

                if user and verify_password(password, user['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.user_name = user['name']
                    st.session_state.user_id = user['id']
                    st.session_state.role = user['role']
                    st.success(f"Добро пожаловать, {user['name']}!")
                else:
                    st.error("Неверные учетные данные.")
            except Exception as e:
                st.error(f"Ошибка при входе: {e}")