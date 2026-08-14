# Databricks notebook source
dbutils.widgets.text("TABLE_TRANSFORM", "g6_catalog.silver.spark_sql_transform")
dbutils.widgets.text("TABLE_SUMMARY", "g6_catalog.gold.spark_sql_summary")

# COMMAND ----------

TABLE_TRANSFORM = dbutils.widgets.get("TABLE_TRANSFORM")
TABLE_SUMMARY = dbutils.widgets.get("TABLE_SUMMARY")

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {TABLE_SUMMARY}')

# COMMAND ----------

spark.sql(f"""
          CREATE OR REPLACE TABLE {TABLE_SUMMARY} AS
            WITH metricas_base_cliente AS (
              SELECT 
                cust_code,
                no_cli,
                -- Conteos y frecuencias
                COUNT(*) as total_despachos,
                COUNT(DISTINCT co_obr) as total_obras_atendidas,
                COUNT(DISTINCT plant_code) as plantas_utilizadas,
                COUNT(DISTINCT truck_code) as camiones_utilizados,
                COUNT(DISTINCT short_prod_descr) as productos_diferentes,
                COUNT(DISTINCT order_date) as dias_con_despachos,
                -- Métricas de tiempo
                AVG(tiempo_ciclo_total) as promedio_tiempo_ciclo,
                MIN(tiempo_ciclo_total) as mejor_tiempo_ciclo,
                MAX(tiempo_ciclo_total) as peor_tiempo_ciclo,
                STDDEV(tiempo_ciclo_total) as variabilidad_tiempo_ciclo,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tiempo_ciclo_total) as mediana_tiempo_ciclo,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY tiempo_ciclo_total) as p25_tiempo_ciclo,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY tiempo_ciclo_total) as p75_tiempo_ciclo,
                -- Métricas de componentes de tiempo
                AVG(tiempo_a_obra) as promedio_tiempo_a_obra,
                AVG(tiempo_espera) as promedio_tiempo_espera,
                AVG(tiempo_vaciado) as promedio_tiempo_vaciado,
                AVG(tiempo_salida) as promedio_tiempo_salida,
                AVG(tiempo_a_planta) as promedio_tiempo_a_planta,
                -- Métricas de volumen
                SUM(delv_qty) as volumen_total_entregado,
                AVG(delv_qty) as volumen_promedio_por_despacho,
                MIN(delv_qty) as volumen_minimo,
                MAX(delv_qty) as volumen_maximo,
                SUM(order_qty) as volumen_total_pedido,
                -- Métricas de eficiencia
                SUM(CASE WHEN clasificacion_eficiencia_cliente = 'Eficiente para Cliente' THEN 1 ELSE 0 END) as despachos_eficientes,
                SUM(CASE WHEN clasificacion_eficiencia_cliente = 'Normal para Cliente' THEN 1 ELSE 0 END) as despachos_normales,
                SUM(CASE WHEN clasificacion_eficiencia_cliente = 'Lento para Cliente' THEN 1 ELSE 0 END) as despachos_lentos,
                -- Fechas
                MIN(order_date) as primera_orden,
                MAX(order_date) as ultima_orden
              FROM {TABLE_TRANSFORM}
              GROUP BY cust_code, no_cli
            ),

            metricas_comparativas AS (
              SELECT 
                cust_code,
                no_cli,
                total_despachos,
                total_obras_atendidas,
                plantas_utilizadas,
                camiones_utilizados,
                productos_diferentes,
                dias_con_despachos,
                promedio_tiempo_ciclo,
                mejor_tiempo_ciclo,
                peor_tiempo_ciclo,
                variabilidad_tiempo_ciclo,
                mediana_tiempo_ciclo,
                p25_tiempo_ciclo,
                p75_tiempo_ciclo,
                promedio_tiempo_a_obra,
                promedio_tiempo_espera,
                promedio_tiempo_vaciado,
                promedio_tiempo_salida,
                promedio_tiempo_a_planta,
                volumen_total_entregado,
                volumen_promedio_por_despacho,
                volumen_minimo,
                volumen_maximo,
                volumen_total_pedido,
                despachos_eficientes,
                despachos_normales,
                despachos_lentos,
                primera_orden,
                ultima_orden,
                
                -- Cálculos de eficiencia
                ROUND((despachos_eficientes * 100.0 / total_despachos), 2) as porcentaje_eficiencia,
                ROUND((despachos_lentos * 100.0 / total_despachos), 2) as porcentaje_problematico,
                
                -- Métricas de cumplimiento
                ROUND((volumen_total_entregado * 100.0 / NULLIF(volumen_total_pedido, 0)), 2) as porcentaje_cumplimiento_volumen,
                
                -- Periodicidad
                DATEDIFF(ultima_orden, primera_orden) + 1 as dias_como_cliente
                
              FROM metricas_base_cliente
            ),

            metricas_con_frecuencia AS (
              SELECT 
                *,
                ROUND(total_despachos * 1.0 / GREATEST(dias_como_cliente, 1), 2) as frecuencia_despachos_por_dia
              FROM metricas_comparativas
            ),

            rankings AS (
              SELECT 
                *,
                -- Rankings comparativos usando las métricas ya calculadas
                DENSE_RANK() OVER (ORDER BY total_despachos DESC) as ranking_volumen_despachos,
                DENSE_RANK() OVER (ORDER BY volumen_total_entregado DESC) as ranking_volumen_entregado,
                DENSE_RANK() OVER (ORDER BY promedio_tiempo_ciclo ASC) as ranking_eficiencia_tiempo,
                DENSE_RANK() OVER (ORDER BY (despachos_eficientes * 100.0 / total_despachos) DESC) as ranking_eficiencia_general,
                
                -- Percentiles
                PERCENT_RANK() OVER (ORDER BY promedio_tiempo_ciclo) * 100 as percentil_tiempo_ciclo,
                PERCENT_RANK() OVER (ORDER BY volumen_total_entregado) * 100 as percentil_volumen
                
              FROM metricas_con_frecuencia
            ),

            conteos_globales AS (
              SELECT 
                COUNT(*) as total_clientes,
                COUNT(*) * 0.2 as top_20_count,
                COUNT(*) * 0.5 as top_50_count,
                COUNT(*) * 0.8 as top_80_count
              FROM rankings
            ),

            clasificacion_clientes AS (
              SELECT 
                r.*,
                -- Clasificación por volumen usando rankings ya calculados
                CASE 
                  WHEN r.ranking_volumen_entregado <= c.top_20_count THEN 'VIP - Top 20%'
                  WHEN r.ranking_volumen_entregado <= c.top_50_count THEN 'Premium - Top 50%'
                  WHEN r.ranking_volumen_entregado <= c.top_80_count THEN 'Estándar'
                  ELSE 'Ocasional'
                END as segmento_volumen,
                
                -- Clasificación por eficiencia usando porcentaje ya calculado
                CASE 
                  WHEN r.porcentaje_eficiencia >= 80 THEN 'Excelente'
                  WHEN r.porcentaje_eficiencia >= 60 THEN 'Bueno'
                  WHEN r.porcentaje_eficiencia >= 40 THEN 'Regular'
                  ELSE 'Problemático'
                END as segmento_eficiencia,
                
                -- Clasificación por frecuencia
                CASE 
                  WHEN r.frecuencia_despachos_por_dia >= 1 THEN 'Diario'
                  WHEN r.frecuencia_despachos_por_dia >= 0.5 THEN 'Frecuente'
                  WHEN r.frecuencia_despachos_por_dia >= 0.2 THEN 'Regular'
                  ELSE 'Esporádico'
                END as segmento_frecuencia
                
              FROM rankings r
              CROSS JOIN conteos_globales c
            ),

            scores_finales AS (
              SELECT 
                *,
                -- Score compuesto (0-100) calculado con métricas ya disponibles
                ROUND((
                  (100 - percentil_tiempo_ciclo) * 0.4 +  -- 40% peso a eficiencia de tiempo
                  percentil_volumen * 0.3 +               -- 30% peso a volumen
                  porcentaje_eficiencia * 0.3             -- 30% peso a eficiencia general
                ), 2) as score_cliente
              FROM clasificacion_clientes
            ),

            alertas_cliente AS (
              SELECT 
                *,
                -- Alertas automáticas usando métricas ya calculadas
                CASE 
                  WHEN porcentaje_problematico > 30 THEN 'CRÍTICO: >30% despachos lentos'
                  WHEN promedio_tiempo_ciclo > (SELECT AVG(promedio_tiempo_ciclo) * 1.5 FROM scores_finales) THEN 'ALERTA: Tiempo ciclo muy alto'
                  WHEN porcentaje_cumplimiento_volumen < 95 THEN 'ATENCIÓN: Bajo cumplimiento volumen'
                  WHEN dias_como_cliente > 30 AND frecuencia_despachos_por_dia < 0.1 THEN 'RIESGO: Cliente inactivo'
                  ELSE 'Normal'
                END as estado_alerta,
                
                -- Próximas acciones recomendadas
                CASE 
                  WHEN porcentaje_problematico > 30 THEN 'Revisar proceso de despacho con cliente'
                  WHEN ranking_volumen_entregado <= 10 AND porcentaje_eficiencia < 70 THEN 'Reunión estratégica de mejora'
                  WHEN segmento_volumen = 'VIP - Top 20%' AND porcentaje_eficiencia < 80 THEN 'Optimización prioritaria'
                  WHEN dias_como_cliente > 30 AND frecuencia_despachos_por_dia < 0.1 THEN 'Campaña de reactivación'
                  ELSE 'Monitoreo regular'
                END as accion_recomendada
                
              FROM scores_finales
            )

            -- Resultado final con todas las métricas
            SELECT 
              -- Identificación del cliente
              cust_code,
              no_cli,
              
              -- Métricas operacionales
              total_despachos,
              total_obras_atendidas,
              plantas_utilizadas,
              productos_diferentes,
              dias_con_despachos,
              
              -- Métricas de tiempo
              ROUND(promedio_tiempo_ciclo, 2) as promedio_tiempo_ciclo,
              ROUND(mejor_tiempo_ciclo, 2) as mejor_tiempo_ciclo,
              ROUND(peor_tiempo_ciclo, 2) as peor_tiempo_ciclo,
              ROUND(variabilidad_tiempo_ciclo, 2) as variabilidad_tiempo_ciclo,
              
              -- Métricas de volumen
              ROUND(volumen_total_entregado, 2) as volumen_total_entregado,
              ROUND(volumen_promedio_por_despacho, 2) as volumen_promedio_por_despacho,
              porcentaje_cumplimiento_volumen,
              
              -- Métricas de eficiencia
              porcentaje_eficiencia,
              porcentaje_problematico,
              despachos_eficientes,
              despachos_normales,
              despachos_lentos,
              
              -- Clasificaciones y rankings
              segmento_volumen,
              segmento_eficiencia,
              segmento_frecuencia,
              ranking_volumen_despachos,
              ranking_volumen_entregado,
              ranking_eficiencia_tiempo,
              score_cliente,
              
              -- Información temporal
              primera_orden,
              ultima_orden,
              dias_como_cliente,
              ROUND(frecuencia_despachos_por_dia, 3) as frecuencia_despachos_por_dia,
              
              -- Alertas y acciones
              estado_alerta,
              accion_recomendada,
              
              -- Metadatos
              CURRENT_TIMESTAMP() as fecha_calculo,
              CURRENT_TIMESTAMP() as ultima_actualizacion
              
            FROM alertas_cliente
            ORDER BY score_cliente DESC, volumen_total_entregado DESC;

          """)