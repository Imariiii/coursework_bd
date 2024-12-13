import pandas as pd
import streamlit as st
from db import get_db, close_db

class RankingManager:
    def __init__(self):
        self.conn, self.cursor = get_db()

    def __del__(self):
        close_db(self.conn, self.cursor)

    def display_choir_ranking(self):
        st.subheader("Рейтинг хоров")

        try:
            update_ranking_query = """
                WITH RankedChoirs AS (
                    SELECT 
                        choir_id,
                        total_points,
                        RANK() OVER (ORDER BY total_points DESC) AS calculated_rank
                    FROM choir_ranking
                )
                INSERT INTO choir_ranking (choir_id, total_points, rank)
                SELECT choir_id, total_points, calculated_rank
                FROM RankedChoirs
                ON CONFLICT (choir_id) DO UPDATE
                SET rank = EXCLUDED.rank, total_points = EXCLUDED.total_points
            """
            self.cursor.execute(update_ranking_query)
            self.conn.commit()
        except Exception as e:
            st.error(f"Ошибка при обновлении рангов: {e}")
            return

        try:
            fetch_ranking_query = """
                SELECT cr.rank, c.name, c.country, cr.total_points
                FROM choir_ranking cr
                JOIN choirs c ON cr.choir_id = c.id
                ORDER BY cr.rank ASC
            """
            self.cursor.execute(fetch_ranking_query)
            rankings = self.cursor.fetchall()

            if not rankings:
                st.write("Рейтинг пока пуст.")
                return

            ranking_data = [
                {
                    "Ранг": rank["rank"],
                    "Название хора": rank["name"],
                    "Страна": rank["country"],
                    "Общее количество баллов": rank["total_points"]
                }
                for rank in rankings
            ]
            df = pd.DataFrame(ranking_data)
            st.table(df)
        except Exception as e:
            st.error(f"Ошибка при загрузке рейтинга: {e}")