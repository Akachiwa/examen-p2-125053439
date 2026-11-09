       # Examen Segundo Parcial - Pipeline de datos contenerizado

**Alumna:** Amayrani Guadalupe Perusquia Gutierrez
**Matricula:** 125053439
**Materia:** Manejo Masivo de Datos (Big Data) - Prof. Javier Moya

## Pregunta de negocio asignada

Mi matricula termina en 9, entonces me toco: **ingreso total por hora del dia (0-23) y categoria**.
El ingreso de cada venta es `cantidad x precio_unitario` y se agrupa por hora y categoria,
asi que salen 24 horas x 10 categorias = 240 resultados.

## Parte E. Teoria

**1. Modos de Hadoop**
En standalone todo corre en un solo proceso de Java y lee los archivos directo del disco, no usa HDFS; es el modo que use en este examen y sirve para probar. En pseudo-distribuido todos los servicios de Hadoop (NameNode, DataNode, etc.) corren por separado pero en la misma maquina, como si fuera un cluster chiquito, y por eso pide SSH sin contrasena a localhost. En totalmente distribuido los servicios estan repartidos en varias maquinas. HDFS se usa en el pseudo-distribuido y en el totalmente distribuido.

**2. Por que el dataset se monta como volumen y no con COPY**
Primero por el tamano: si copio los 400 MB a la imagen, la imagen queda muy pesada y tarda mucho en construirse. Segundo, si el CSV cambia no tengo que volver a construir la imagen, solo cambio el archivo en mi carpeta. Ademas lo monte como solo lectura (`:ro`), asi el contenedor no puede modificar los datos originales y el CSV no se sube al repositorio.

**3. Que pasa con los datos al hacer docker compose down y down -v**
Con `docker compose down` se borran los contenedores y la red, pero el volumen `pgdata` se queda, entonces cuando vuelvo a levantar todo los datos de la base siguen ahi (lo comprobe en el paso de persistencia). Con `docker compose down -v` tambien se borran los volumenes, asi que la base queda vacia y hay que volver a correr el job y cargar los resultados.

**4. Por que MapReduce no siempre es mas rapido**
Porque Hadoop tarda en arrancar Java, partir el archivo, ordenar todas las parejas clave-valor y escribir resultados intermedios en disco. Con 400 MB en una sola computadora y en modo standalone no hay nada que se reparta en paralelo, asi que todo ese trabajo extra hace que sea mas lento que un script normal de Python. Conviene cuando los datos son muy grandes (cientos de GB o TB) y hay un cluster con varias maquinas para dividir el trabajo.

**5. CMD vs ENTRYPOINT y COPY vs ADD**
ENTRYPOINT es lo que siempre se ejecuta cuando arranca el contenedor (en mi Dockerfile de Hadoop es el `entrypoint.sh`), y CMD es el comando por defecto, que se puede cambiar al hacer `docker run` (en mi API es `python app.py`). COPY solo copia archivos de mi carpeta a la imagen, y ADD hace lo mismo pero tambien puede descargar de una URL y descomprimir archivos .tar automaticamente. Por eso es mejor usar COPY, porque hace solo lo que le pides.


## Estructura del proyecto

    examen-p2-125053439/
    ├── README.md
    ├── .gitignore            (ignora *.csv, data/ y .env)
    ├── .env.example
    ├── docker-compose.yml
    ├── generar_dataset.py
    ├── hadoop/               Dockerfile y entrypoint.sh
    ├── mapreduce/            mapper.py, reducer.py, secuencial.py, ejecutar_job.sh
    ├── api/                  Dockerfile, requirements.txt, app.py
    ├── scripts/              cargar_resultados.py
    └── evidencias/

## Como reproducir

    cp .env.example .env
    cd data && python3 ../generar_dataset.py 125053439 && cd ..
    docker compose up --build -d
    docker compose exec hadoop hadoop version
    docker compose exec -u hduser hadoop ssh localhost "hostname; whoami"
    docker compose exec api ssh hduser@hadoop "hostname; whoami"
    docker compose exec hadoop bash /opt/mapreduce/ejecutar_job.sh
    docker compose exec api python scripts/cargar_resultados.py
    curl http://localhost:5000/resultados

## Endpoints de la API

| Metodo | Ruta | Que hace |
|---|---|---|
| GET | /resultados | Regresa los 240 registros |
| GET | /resultados/clave | Si la clave es numero filtra por hora, si es texto filtra por categoria |
| POST | /resultados | Crea un registro |
| PUT | /resultados/id | Actualiza un registro |
| DELETE | /resultados/id | Borra un registro |

## Comparativa de rendimiento

| Metodo | Tiempo real |
|---|---|
| Hadoop Streaming (standalone) | 9.789 s |
| Python secuencial (linea por linea) | 3.447 s |
| Resultados iguales (diff) | Si, las 240 lineas son iguales |

Datos del job de Hadoop: leyo 5,000,001 lineas (incluye el encabezado), el mapper produjo 5,000,000 parejas clave-valor, el archivo se dividio en 11 partes (splits) y el reducer genero 240 resultados. No hubo lineas mal formadas.

El script secuencial fue casi 3 veces mas rapido (3.4 s contra 9.8 s). En modo standalone Hadoop corre en una sola maquina, entonces no reparte el trabajo entre varias computadoras, pero si tiene que arrancar Java, dividir el archivo en 11 partes, pasarle cada linea a Python, ordenar los 5 millones de parejas clave-valor (unos 100 MB en el shuffle) y escribir todo eso en disco. El script secuencial solo lee el archivo una vez y va sumando en un diccionario de 240 claves, sin ordenar ni escribir datos intermedios. Con 400 MB todo ese trabajo extra de Hadoop pesa mas que lo que ayuda. Para que los resultados salieran iguales al centavo, los dos programas suman en centavos enteros en lugar de usar decimales.

## Evidencias

En la carpeta `evidencias/` estan los logs y capturas de: hadoop version, ssh localhost, ssh de api a hadoop, ejecucion del job, version secuencial, comparacion (diff), carga a la base, respuesta de la API y persistencia despues de docker compose down y up.