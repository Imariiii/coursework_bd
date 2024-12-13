import streamlit as st
from db import get_db, close_db

class ChoirManager:
    def __init__(self):
        self.conn, self.cursor = get_db()

    def __del__(self):
        close_db(self.conn, self.cursor)

    def create_choir(self):
        st.subheader("Создание хора")
        choir_name = st.text_input("Название хора")
        choir_country = st.text_input("Страна")

        if st.button("Создать хор"):
            try:
                self.cursor.execute(
                    "CALL create_choir(%s, %s, %s)",
                    (choir_name, choir_country, st.session_state.user_id)
                )
                self.conn.commit()
                st.success("Хор успешно создан и закреплен за вами!")
            except Exception as e:
                self.conn.rollback()
                st.error(f"Ошибка при создании хора: {e}")

    def delete_choir(self):
        st.subheader("Удаление хора")

        self.cursor.execute("SELECT * FROM conductor_choirs WHERE user_id = %s", (st.session_state.user_id,))
        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для удаления", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                st.write(f"Вы выбрали хор: {selected_choir['name']}")

                if st.button("Удалить выбранный хор"):
                    try:
                        self.cursor.execute("CALL delete_choir(%s)", (selected_choir['id'],))
                        self.conn.commit()
                        st.success(f"Хор {selected_choir['name']} успешно удален!")
                    except Exception as e:
                        self.conn.rollback()
                        st.error(f"Ошибка при удалении хора: {e}")
        else:
            st.write("У вас нет хоров для удаления.")

    def add_choir_members(self):
        st.subheader("Добавление участников в хор")

        self.cursor.execute("SELECT * FROM conductor_choirs WHERE user_id = %s", (st.session_state.user_id,))
        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для добавления участников", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                st.write(f"Вы управляете хором: {selected_choir['name']}")

                self.cursor.execute("SELECT id, name FROM users WHERE role = 'participant'")
                participants = self.cursor.fetchall()

                if participants:
                    participant_names = [participant['name'] for participant in participants]
                    selected_participant_name = st.selectbox("Выберите участника для добавления", participant_names)

                    selected_participant = next(
                        (p for p in participants if p['name'] == selected_participant_name),
                        None
                    )

                    if selected_participant:
                        if st.button("Добавить участника"):
                            try:
                                self.cursor.execute("CALL add_member_to_choir(%s, %s)", (selected_choir['id'], selected_participant['id']))
                                self.conn.commit()
                                st.success(f"Участник {selected_participant_name} успешно добавлен в хор!")
                            except Exception as e:
                                self.conn.rollback()
                                st.error(f"Ошибка при добавлении участника: {e}")
                    else:
                        st.error("Пользователь не найден.")
                else:
                    st.write("Нет доступных участников для добавления.")
            else:
                st.error("Хор не найден.")
        else:
            st.write("У вас нет хоров для управления.")

    def delete_choir_members(self):
        st.subheader("Удаление участников из хора")

        self.cursor.execute("SELECT * FROM conductor_choirs WHERE user_id = %s", (st.session_state.user_id,))
        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для удаления участников", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                st.write(f"Вы управляете хором: {selected_choir['name']}")

                self.cursor.execute("""
                    SELECT * FROM choir_members_view 
                    WHERE choir_id = %s AND role != 'conductor'
                """, (selected_choir['id'],))
                members = self.cursor.fetchall()

                if members:
                    member_names = [member['name'] for member in members]
                    selected_member_name = st.selectbox("Выберите участника для удаления", member_names)

                    selected_member = next(
                        (m for m in members if m['name'] == selected_member_name),
                        None
                    )

                    if selected_member:
                        if st.button("Удалить участника"):
                            try:
                                self.cursor.execute("CALL remove_member_from_choir(%s, %s)", (selected_choir['id'], selected_member['id']))
                                self.conn.commit()
                                st.success(f"Участник {selected_member_name} успешно удален из хора!")
                            except Exception as e:
                                self.conn.rollback()
                                st.error(f"Ошибка при удалении участника: {e}")
                    else:
                        st.error("Участник не найден.")
                else:
                    st.write("В хоре пока нет участников для удаления.")
            else:
                st.error("Хор не найден.")
        else:
            st.write("У вас нет хоров для управления.")

    def display_choir_info(self, role="conductor"):
        st.subheader("Информация о вашем хоре")

        if role == "conductor":
            self.cursor.callproc('get_conductor_choirs', (st.session_state.user_id,))
        elif role == "participant":
            self.cursor.callproc('get_participant_choirs', (st.session_state.user_id,))

        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для просмотра информации", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                self.cursor.execute("SELECT * FROM choir_info WHERE id = %s", (selected_choir['id'],))
                choir = self.cursor.fetchone()

                if choir:
                    st.write(f"Название хора: {choir['name']}")
                    st.write(f"Страна: {choir['country']}")

                    self.cursor.execute("SELECT * FROM choir_members_view WHERE choir_id = %s", (selected_choir['id'],))
                    members = self.cursor.fetchall()
                    if members:
                        st.write("Состав хора:")
                        for member in members:
                            if member['role'] == 'conductor':
                                st.write(f"- {member['name']} (Дирижер)")
                            else:
                                st.write(f"- {member['name']} (Участник)")
                    else:
                        st.write("В хоре пока нет участников.")
                else:
                    st.write("Информация о хоре не найдена.")
        else:
            st.write("У вас нет хоров для просмотра информации.")

    def register_choir_for_event(self):
        st.subheader("Регистрация хора на мероприятие")

        self.cursor.execute("SELECT * FROM conductor_choirs WHERE user_id = %s", (st.session_state.user_id,))
        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для регистрации на мероприятие", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                st.write(f"Ваш хор: {selected_choir['name']}")

                self.cursor.execute("SELECT * FROM events")
                events = self.cursor.fetchall()

                show_events = True

                if "selected_event" in st.session_state and st.session_state.selected_event:
                    show_events = False

                if show_events:
                    if events:
                        st.write("Выберите мероприятие для регистрации:")
                        for event in events:
                            with st.container():
                                st.markdown(f"### {event['name']}")
                                st.write(f"📅 Дата: {event['date']}")
                                st.write(f"📍 Местоположение: {event['location']}")

                                if st.button(f"Подробнее о {event['name']}", key=f"details_{event['id']}"):
                                    st.session_state.selected_event = event

                                self.cursor.execute("SELECT is_choir_registered_for_event(%s, %s)", (selected_choir['id'], event['id']))
                                result = self.cursor.fetchone()

                                '''if result is not None:
                                    #is_registered = result[0]  # Получаем значение из кортежа
                                    st.write(result)
                                else:
                                    is_registered = False  # Если результат пустой, считаем, что хор не зарегистрирован'''
                                
                                is_registered = result["is_choir_registered_for_event"]

                                if is_registered:
                                    st.write("Статус: Зарегистрирован")
                                    if st.button("Отменить регистрацию", key=f"unregister_{event['id']}"):
                                        try:
                                            self.cursor.execute("CALL unregister_choir_from_event(%s, %s)", (selected_choir['id'], event['id']))
                                            self.conn.commit()
                                            st.success(f"Регистрация хора на мероприятие {event['name']} успешно отменена!")
                                        except Exception as e:
                                            self.conn.rollback()
                                            st.error(f"Ошибка при отмене регистрации хора на мероприятие: {e}")
                                else:
                                    st.write("Статус: Не зарегистрирован")
                                    if st.button("Зарегистрировать хор на это мероприятие", key=f"register_{event['id']}"):
                                        try:
                                            self.cursor.execute("CALL register_choir_for_event(%s, %s)", (selected_choir['id'], event['id']))
                                            self.conn.commit()
                                            st.success(f"Хор успешно зарегистрирован на мероприятие: {event['name']}!")
                                        except Exception as e:
                                            self.conn.rollback()
                                            st.error(f"Ошибка при регистрации хора на мероприятие: {e}")
                    else:
                        st.write("Нет доступных мероприятий для регистрации.")
                else:
                    event = st.session_state.selected_event
                    st.subheader(f"Подробная информация о мероприятии: {event['name']}")
                    st.write(f"📅 Дата: {event['date']}")
                    st.write(f"📍 Местоположение: {event['location']}")
                    st.write(f"📝 Описание: {event['description']}")
                    st.write("Дополнительно: Здесь можно добавить дополнительную информацию о мероприятии.")
                    if st.button("Назад к списку мероприятий"):
                        st.session_state.selected_event = None
        else:
            st.write("У вас нет хоров для регистрации на мероприятия.")
    
    def display_registered_events(self, role="conductor"):
        st.subheader("Мероприятия, на которые зарегистрирован хор")

        if role == "conductor":
            self.cursor.callproc('get_conductor_choirs', (st.session_state.user_id,))
        elif role == "participant":
            self.cursor.callproc('get_participant_choirs', (st.session_state.user_id,))

        choirs = self.cursor.fetchall()

        if choirs:
            choir_names = [choir['name'] for choir in choirs]
            selected_choir_name = st.selectbox("Выберите хор для просмотра зарегистрированных мероприятий", choir_names)

            selected_choir = next((c for c in choirs if c['name'] == selected_choir_name), None)

            if selected_choir:
                st.write(f"Выбранный хор: {selected_choir['name']}")

                self.cursor.execute("SELECT * FROM choir_events WHERE choir_id = %s", (selected_choir['id'],))
                events = self.cursor.fetchall()

                if events:
                    st.write("Зарегистрированные мероприятия:")
                    for event in events:
                        st.write(f"- {event['name']} (Дата: {event['date']}, Место: {event['location']})")
                else:
                    st.write("Выбранный хор не зарегистрирован ни на одно мероприятие.")
            else:
                st.write("Выбранный хор не найден.")
        else:
            st.write("У вас нет связанных хоров.")