"""Database migration script"""
import subprocess
import sys

def run_alembic_command(args):
    cmd = [sys.executable, "-m", "alembic"] + args
    subprocess.run(cmd, cwd=__file__.rsplit("\\", 1)[0], check=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [upgrade|downgrade|revision]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "upgrade":
        run_alembic_command(["upgrade", "head"])
        print("Database migrated to latest version.")
    elif action == "downgrade":
        run_alembic_command(["downgrade", "-1"])
        print("Database downgraded one version.")
    elif action == "revision":
        msg = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        run_alembic_command(["revision", "--autogenerate", "-m", msg])
        print(f"Migration revision created: {msg}")