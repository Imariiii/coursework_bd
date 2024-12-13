import streamlit as st

from modules.events import EventManager
from modules.choirs import ChoirManager
from modules.user import UserManager
from modules.ranking import RankingManager
from modules.admin_panel import AdminPanel

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

def navigate_to(page):
    st.session_state.current_page = page

def main(): 
    st.title("SingSync")

    if st.session_state.logged_in:
        if st.session_state.role == "conductor":
            menu = ["Home", "Choir Management", "Choir Rankings", "Logout"]
        else:
            menu = ["Home", "Choir Rankings", "Logout"]
    else:
        menu = ["Home", "Login", "Sign Up"]

    choice = st.sidebar.selectbox("Menu", menu, key="menu_select")

    if choice == "Home":
        navigate_to("Home")
    elif choice == "Login":
        navigate_to("Login")
    elif choice == "Sign Up":
        navigate_to("Sign Up")
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.role = ""
        st.success("Вы успешно вышли из системы.")
        navigate_to("Home")
    elif choice == "Choir Rankings":
        navigate_to("Choir Rankings")
    elif choice == "Choir Management":
        navigate_to("Choir Management")

    event_manager = EventManager()
    choir_manager = ChoirManager()
    user_manager = UserManager()  
    ranking_manager = RankingManager()
    admin_panel = AdminPanel()

    if st.session_state.current_page == "Home":
        if st.session_state.logged_in:
            if st.session_state.role == "admin":
                st.subheader("Панель администратора")
                admin_panel.displaying_admin_panel()

            elif st.session_state.role == "conductor":
                choir_manager.display_choir_info(role="conductor")
                choir_manager.display_registered_events(role="conductor")

            elif st.session_state.role == "participant":
                choir_manager.display_choir_info(role="participant")
                choir_manager.display_registered_events(role="participant")
        else:
            st.subheader("Добро пожаловать!")
            st.write("Войдите или зарегистрируйтесь, чтобы продолжить.")

    elif st.session_state.current_page == "Sign Up":
        user_manager.register()

    elif st.session_state.current_page == "Login":
        user_manager.login()
        
    elif st.session_state.current_page == "Choir Rankings":
        ranking_manager.display_choir_ranking()
    
    elif st.session_state.current_page == "Choir Management":
        st.subheader("Управление вашим хором")
        section = st.sidebar.selectbox("Выберите раздел", [
            "Создание/удаление хоров",
            "Участники хора",
            "Регистрация на мероприятия"
        ])

        if section == "Создание/удаление хоров":
            choir_manager.create_choir()
            choir_manager.delete_choir()

        if section == "Участники хора":
            choir_manager.add_choir_members()
            choir_manager.delete_choir_members()

        elif section == "Регистрация на мероприятия":
            choir_manager.register_choir_for_event()

if __name__ == '__main__':
    main()