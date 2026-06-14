import os
import sys

script_dir = r"D:\aiphxt-app\ai-service"
os.chdir(script_dir)
sys.path.insert(0, script_dir)

output = []
output.append("=== TEST START ===")
output.append(f"Working dir: {os.getcwd()}")

try:
    from app.core.database_pool import get_db_manager, DATABASE_URL, _APP_DIR, _ABS_DB_PATH
    output.append(f"APP_DIR: {_APP_DIR}")
    output.append(f"ABS_DB_PATH: {_ABS_DB_PATH}")
    output.append(f"DATABASE_URL: {DATABASE_URL}")
    db_manager = get_db_manager()
    output.append(f"DB Manager created: {db_manager}")
    session = db_manager.get_session()
    output.append(f"Session created: {session}")
    session.close()
    output.append("DB: OK")
except Exception as e:
    output.append(f"DB ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

output.append("")
try:
    import bcrypt
    password = "test123456"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    output.append(f"bcrypt: OK (hash={hashed[:30]}...)")
except Exception as e:
    output.append(f"bcrypt ERROR: {type(e).__name__}: {e}")

output.append("")
try:
    from app.models.user import User
    output.append(f"User model: {User}")
    output.append(f"User.__tablename__: {User.__tablename__}")
    output.append("User model: OK")
except Exception as e:
    output.append(f"User model ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

output.append("")
try:
    from app.api.routes.auth import register, RegisterRequest, Role
    output.append(f"register function: {register}")
    output.append(f"RegisterRequest: {RegisterRequest}")
    output.append(f"Role: {[r.value for r in Role]}")
    output.append("Auth imports: OK")
except Exception as e:
    output.append(f"Auth imports ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

output.append("")
output.append("=== Creating test user directly ===")
try:
    import bcrypt
    from app.core.database_pool import get_db_manager
    from app.models.user import User
    import time

    username = f"direct_test_{int(time.time())}"
    phone = f"138{int(time.time()) % 100000000:08d}"

    db_manager = get_db_manager()
    session = db_manager.get_session()

    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(
        username=username,
        password_hash=password_hash,
        email=f"{username}@test.com",
        phone=phone,
        role="student"
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    output.append(f"Created user: id={new_user.id}, username={new_user.username}")
    session.close()
    output.append("Direct user creation: OK")
except Exception as e:
    output.append(f"Direct user creation ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

output.append("")
output.append("=== TEST END ===")

with open(os.path.join(script_dir, "test_results.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Test complete. Results written to test_results.txt")
