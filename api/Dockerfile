# Imagen de la API (Flask) + cliente SSH para conectarse a "hadoop"
FROM python:3.12-slim

# Cliente SSH (el servidor esta en el contenedor hadoop)
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/*

# "ssh hduser@hadoop" usara la llave del volumen compartido /ssh-keys
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh \
    && printf 'Host hadoop\n    User hduser\n    IdentityFile /ssh-keys/id_ed25519\n    StrictHostKeyChecking no\n    UserKnownHostsFile /dev/null\n    LogLevel ERROR\n' > /root/.ssh/config \
    && chmod 600 /root/.ssh/config

WORKDIR /app

# Primero solo requirements: si no cambia, Docker usa la cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# CMD = comando por defecto
CMD ["python", "app.py"]