from db import get_db
from sqlalchemy.sql import text

def assign_admin(email: str):
    db = next(get_db())
    try:
        query_find_user = text("SELECT id, name, role FROM users WHERE email = :email")
        user = db.execute(query_find_user, {"email": email}).mappings().fetchone()

        if user:
            query_update_role = text("UPDATE users SET role = 'admin' WHERE id = :user_id")
            db.execute(query_update_role, {"user_id": user["id"]})
            db.commit()
            print(f"Пользователь {user['name']} теперь администратор.")
        else:
            print("Пользователь с таким email не найден.")
    except Exception as e:
        print(f"Ошибка при назначении администратора: {e}")
    finally:
        db.close()

def main():
    assign_admin('a')

if __name__ == '__main__':
    main()
