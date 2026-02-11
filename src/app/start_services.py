import subprocess

def check_docker_perms():
    result = subprocess.run(["docker", "ps"], check=True)
    if result.returncode != 0:
        print("Docker failed:", result.stderr)
        return False
    return True

def start_containers()


docker run --name postgres-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -v ./pg_hba.conf:/var/lib/postgresql/data/pg_hba.conf \
  -v ./postgresql.conf:/var/lib/postgresql/data/postgresql.conf \
  -v postgres-data:/var/lib/postgresql/data \
  -d postgres