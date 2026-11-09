# =====================================================================
#  Imagen de Hadoop (modo standalone) + Python 3 + OpenSSH Server
#  Examen 2do Parcial - Big Data - Matricula 125053439
# =====================================================================

# 1) Imagen base Debian "slim" (Debian 12 bookworm, version ligera)
FROM debian:bookworm-slim

# 2) Version de Hadoop como argumento de construccion
ARG HADOOP_VERSION=3.3.6

# 3) Evita que apt haga preguntas interactivas durante la instalacion
ENV DEBIAN_FRONTEND=noninteractive

# 4) Paquetes del sistema:
#    - default-jdk-headless : Java (OpenJDK 17), Hadoop esta hecho en Java
#    - python3              : para el mapper/reducer de Hadoop Streaming
#    - openssh-server/client: SSH (Parte B del examen)
#    - wget, ca-certificates: para descargar Hadoop por HTTPS
#    - procps               : comandos como "ps" que usan los scripts de Hadoop
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-jdk-headless python3 openssh-server openssh-client \
        wget ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# 5) Enlace fijo /opt/java -> carpeta real de Java
RUN ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" /opt/java

# 6) Descargar Hadoop, descomprimirlo en /opt/hadoop y borrar lo que sobra
RUN wget -q https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop \
    && rm hadoop-${HADOOP_VERSION}.tar.gz \
    && rm -rf /opt/hadoop/share/doc

# 7) Variables de entorno que pide el examen
ENV JAVA_HOME=/opt/java
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# 8) Las ENV de Docker NO llegan a las sesiones SSH; las repetimos en
#    /etc/environment (lo lee SSH) y en hadoop-env.sh (lo lee Hadoop)
RUN echo "JAVA_HOME=/opt/java" >> /etc/environment \
    && echo "HADOOP_HOME=/opt/hadoop" >> /etc/environment \
    && echo "HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop" >> /etc/environment \
    && echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/java/bin:/opt/hadoop/bin:/opt/hadoop/sbin" >> /etc/environment \
    && echo "export JAVA_HOME=/opt/java" >> /opt/hadoop/etc/hadoop/hadoop-env.sh

# 9) Usuario "hduser" SIN contrasena valida (solo entra con llave SSH)
RUN useradd -m -s /bin/bash hduser && usermod -p '*' hduser

# 10) Configuracion del servidor SSH: solo llaves, sin contrasenas, sin root
RUN mkdir -p /run/sshd \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config \
    && ssh-keygen -A

# 11) Carpetas de trabajo (aqui se montan los volumenes)
RUN mkdir -p /data/input /data/output /opt/mapreduce && chmod 777 /data/output

# 12) Script de arranque
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# 13) Puerto de SSH (dentro de la red de Docker)
EXPOSE 22

WORKDIR /opt/mapreduce

# 14) Programa que SIEMPRE corre al iniciar el contenedor
ENTRYPOINT ["/entrypoint.sh"]