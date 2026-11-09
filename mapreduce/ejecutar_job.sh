#!/bin/bash
# Ejecuta el job de Hadoop Streaming midiendo el tiempo.
# Uso (dentro del contenedor hadoop):  bash /opt/mapreduce/ejecutar_job.sh
MATRICULA=${MATRICULA:-125053439}
ENTRADA=/data/input/ventas_${MATRICULA}.csv
SALIDA=/data/output/resultado

# Hadoop NO sobrescribe: si la carpeta de salida existe, falla
rm -rf "$SALIDA"

time hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files /opt/mapreduce/mapper.py,/opt/mapreduce/reducer.py \
  -input "$ENTRADA" \
  -output "$SALIDA" \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py"

echo "----- Primeras lineas del resultado -----"
head -5 "$SALIDA/part-00000"
echo "Total de lineas: $(wc -l < "$SALIDA/part-00000")  (esperado: 240)"