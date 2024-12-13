import streamlit as st
from db import get_db, close_db

class EventManager:
    def __init__(self):
        self.conn, self.cursor = get_db()

    def __del__(self):
        close_db(self.conn, self.cursor)

    def list_events(self):
        events_query = "SELECT id, name, date, location, description FROM events"
        self.cursor.execute(events_query)
        events = self.cursor.fetchall()

        if not st.session_state.selected_event:
            st.subheader("Список мероприятий")
            if events:
                for event in events:
                    with st.container():
                        st.markdown(f"### {event['name']}")
                        st.write(f"📅 Дата: {event['date']}")
                        st.write(f"📍 Местоположение: {event['location']}")
                        if st.button(f"Подробнее о {event['name']}", key=f"details_{event['id']}"):
                            st.session_state.selected_event = event
            else:
                st.write("Мероприятий пока нет.")
        else:
            event = st.session_state.selected_event
            st.subheader(f"Подробная информация о мероприятии: {event['name']}")
            st.write(f"📅 Дата: {event['date']}")
            st.write(f"📍 Местоположение: {event['location']}")
            st.write(f"📝 Описание: {event['description']}")
            if st.button("Назад"):
                st.session_state.selected_event = None
    
    