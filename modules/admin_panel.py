import streamlit as st
import subprocess
import os
from db import get_db, close_db

class AdminPanel:
    def __init__(self):
        self.conn, self.cursor = get_db()

    def __del__(self):
        close_db(self.conn, self.cursor)

    def delete_user(self, user_id):
        try:
            query = "DELETE FROM users WHERE id = %s"
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
            st.success("Пользователь успешно удалён.")
        except Exception as e:
            st.error(f"Ошибка при удалении пользователя: {e}")

    def delete_choir(self, choir_id):
        try:
            query = "DELETE FROM choirs WHERE id = %s"
            self.cursor.execute(query, (choir_id,))
            self.conn.commit()
            st.success("Хор успешно удалён.")
        except Exception as e:
            st.error(f"Ошибка при удалении хора: {e}")

    def create_event(self):
        st.subheader("Создание мероприятия")
        event_name = st.text_input("Название мероприятия")
        event_date = st.date_input("Дата мероприятия")
        event_location = st.text_input("Местоположение")
        event_description = st.text_area("Описание мероприятия")

        if st.button("Создать мероприятие"):
            try:
                query = """
                    INSERT INTO events (name, date, location, description)
                    VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(query, (event_name, event_date, event_location, event_description))
                self.conn.commit()
                st.success("Мероприятие успешно создано!")
            except Exception as e:
                st.error(f"Ошибка при создании мероприятия: {e}")

    def delete_event(self, event_id):
        try:
            query = "DELETE FROM events WHERE id = %s"
            self.cursor.execute(query, (event_id,))
            self.conn.commit()
            st.success("Мероприятие успешно удалено.")
        except Exception as e:
            st.error(f"Ошибка при удалении мероприятия: {e}")

    def list_events(self):
        st.subheader("Список мероприятий")

        events_query = "SELECT id, name, date, location, description FROM events"
        self.cursor.execute(events_query)
        events = self.cursor.fetchall()

        if events:
            for event in events:
                st.write(f"### {event['name']} (ID: {event['id']}, Дата: {event['date']})")
                st.write(f"Место: {event['location']}")
                st.write(f"Описание: {event['description']}")
                if st.button(f"Удалить {event['name']}", key=f"delete_event_{event['id']}"):
                    self.delete_event(event['id'])
        else:
            st.write("Мероприятий пока нет.")

    def assign_points(self):
        st.subheader("Назначение баллов хорам")

        events_query = "SELECT id, name FROM events"
        self.cursor.execute(events_query)
        events = self.cursor.fetchall()

        if not events:
            st.write("Нет доступных мероприятий.")
            return

        selected_event_id = st.selectbox(
            "Выберите мероприятие",
            options=[event["id"] for event in events],
            format_func=lambda eid: next(event["name"] for event in events if event["id"] == eid)
        )

        registrations_query = """
            SELECT er.id, c.id AS choir_id, c.name AS choir_name, er.points
            FROM event_registrations er
            JOIN choirs c ON er.choir_id = c.id
            WHERE er.event_id = %s
        """
        self.cursor.execute(registrations_query, (selected_event_id,))
        registrations = self.cursor.fetchall()

        if not registrations:
            st.write("На это мероприятие не зарегистрировано ни одного хора.")
            return

        for reg in registrations:
            with st.container():
                st.markdown(f"### Хор: {reg['choir_name']}")
                points = st.number_input(
                    f"Баллы для хора {reg['choir_name']}",
                    min_value=0,
                    value=reg["points"] or 0,
                    key=f"points_{reg['id']}"
                )

                if st.button(f"Сохранить баллы для хора {reg['choir_name']}", key=f"save_{reg['id']}"):
                    try:
                        update_points_query = """
                            UPDATE event_registrations
                            SET points = %s
                            WHERE id = %s
                        """
                        self.cursor.execute(update_points_query, (points, reg["id"]))

                        insert_total_points_query = """
                            INSERT INTO choir_ranking (choir_id, total_points, rank)
                            VALUES (
                                %s,
                                (SELECT SUM(points) FROM event_registrations WHERE choir_id = %s),
                                1
                            )
                            ON CONFLICT (choir_id) DO UPDATE
                            SET total_points = EXCLUDED.total_points
                        """
                        self.cursor.execute(insert_total_points_query, (reg["choir_id"], reg["choir_id"]))

                        self.conn.commit()
                        st.success(f"Баллы для хора {reg['choir_name']} успешно обновлены!")
                    except Exception as e:
                        st.error(f"Ошибка при обновлении баллов: {e}")

    def displaying_admin_panel(self):
        section = st.sidebar.selectbox("Выберите раздел", [
            "Пользователи",
            "Хоры",
            "Мероприятия",
            "Резервное копирование"
        ])

        if section == "Пользователи":
            st.subheader("Список пользователей")
            users_query = "SELECT id, name, email, role FROM users"
            self.cursor.execute(users_query)
            users = self.cursor.fetchall()

            for user in users:
                st.write(f"- id: {user['id']}, name: {user['name']}, email: {user['email']}, role: {user['role']}")
                if st.button("Удалить", key=f"delete_user_{user['id']}"):
                    self.delete_user(user['id'])

        elif section == "Хоры":
            st.subheader("Список хоров")
            choirs_query = "SELECT id, name, country FROM choirs"
            self.cursor.execute(choirs_query)
            choirs = self.cursor.fetchall()

            for choir in choirs:
                st.write(f"- id: {choir['id']}, name: {choir['name']}, country: {choir['country']}")
                if st.button("Удалить", key=f"delete_choir_{choir['id']}"):
                    self.delete_choir(choir['id'])

        elif section == "Мероприятия":
            event_action = st.sidebar.selectbox("Выберите действие", [
                "Список мероприятий",
                "Создать мероприятие",
                "Назначить баллы"
            ])

            if event_action == "Список мероприятий":
                self.list_events()
            elif event_action == "Создать мероприятие":
                self.create_event()
            elif event_action == "Назначить баллы":
                self.assign_points()

        elif section == "Резервное копирование":
            st.subheader("Резервное копирование и восстановление базы данных")
            action = st.selectbox("Выберите действие", ["Создать резервную копию", "Восстановить базу данных"])
            if action == "Создать резервную копию":
                self.backup_database()
            elif action == "Восстановить базу данных":
                self.restore_database()
    
    def backup_database(self):
        st.subheader("Резервное копирование базы данных")

        db_name = "postgres"
        db_user = "postgres"
        db_password = "1234"
        db_host = "localhost"
        db_port = "5432"

        backup_path = st.text_input("Укажите путь для сохранения резервной копии", value="backup.dump")

        if st.button("Создать резервную копию"):
            try:
                command = f"pg_dump -U {db_user} -h {db_host} -p {db_port} -F c -b -v -f {backup_path} {db_name}"
                os.environ['PGPASSWORD'] = db_password
                subprocess.run(command, shell=True, check=True)
                st.success(f"Резервная копия успешно создана: {backup_path}")
            except Exception as e:
                st.error(f"Ошибка при создании резервной копии: {e}")
            finally:
                del os.environ['PGPASSWORD']
    
    def restore_database(self):
        st.subheader("Восстановление базы данных")

        db_name = "postgres"
        db_user = "postgres"
        db_password = "1234"
        db_host = "localhost"
        db_port = "5432"

        backup_path = st.text_input("Укажите путь к файлу резервной копии", value="backup.dump")

        if st.button("Восстановить базу данных"):
            try:
                command = f"pg_restore -U {db_user} -h {db_host} -p {db_port} -d {db_name} -v --clean {backup_path}"
                os.environ['PGPASSWORD'] = db_password
                subprocess.run(command, shell=True, check=True)
                st.success(f"База данных успешно восстановлена из: {backup_path}")
            except Exception as e:
                st.error(f"Ошибка при восстановлении базы данных: {e}")
            finally:
                del os.environ['PGPASSWORD']