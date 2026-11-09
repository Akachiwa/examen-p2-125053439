#!/bin/bash
# =====================================================================
#  Script que corre cada vez que arranca el contenedor "hadoop"
# =====================================================================
set -e

KEYS_DIR=/ssh-keys                 # volumen compartido con el contenedor api
KEY=$KEYS_DIR/id_ed25519           # llave privada
SSH_DIR=/home/hduser/.ssh          # carpeta .ssh del usuario hduser

# 1) Si no hay llaves, las generamos SIN frase (-N "") => acceso sin contrasena
mkdir -p "$KEYS_DIR"
if [ ! -f "$KEY" ]; then
    echo "[entrypoint] Generando llaves SSH con ssh-keygen..."
    ssh-keygen -t ed25519 -N "" -f "$KEY" -C "hduser@datamart"
fi
chmod 600 "$KEY"
chmod 644 "$KEY.pub"

# 2) Le damos la llave a hduser y registramos la publica en authorized_keys
mkdir -p "$SSH_DIR"
cp "$KEY" "$SSH_DIR/id_ed25519"
cp "$KEY.pub" "$SSH_DIR/id_ed25519.pub"
cat "$KEY.pub" > "$SSH_DIR/authorized_keys"

# 3) Para que "ssh localhost" no pregunte "Are you sure... (yes/no)?"
cat > "$SSH_DIR/config" <<EOF
Host localhost 127.0.0.1 hadoop
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
EOF

# 4) SSH es MUY estricto con los permisos; si son abiertos rechaza la llave
chown -R hduser:hduser "$SSH_DIR"
chmod 700 "$SSH_DIR"
chmod 600 "$SSH_DIR/authorized_keys" "$SSH_DIR/id_ed25519" "$SSH_DIR/config"

# 5) Carpeta de salida escribible para cualquier usuario
chmod 777 /data/output 2>/dev/null || true

echo "[entrypoint] Verificando Hadoop:"
hadoop version | head -1

# 6) Arrancamos el servidor SSH en primer plano (-D).
#    Mientras sshd siga vivo, el contenedor sigue encendido.
echo "[entrypoint] Iniciando sshd..."
exec /usr/sbin/sshd -D -e