# Databricks notebook source
dbutils.widgets.text("TABLE_INPUT", "g6_catalog.bronze.spark_sql_input")
dbutils.widgets.text("TABLE_TRANSFORM", "g6_catalog.silver.spark_sql_transform")

# COMMAND ----------

TABLE_INPUT = dbutils.widgets.get("TABLE_INPUT")
TABLE_TRANSFORM = dbutils.widgets.get("TABLE_TRANSFORM")

# COMMAND ----------

spark.sql(f'DROP TABLE IF EXISTS {TABLE_TRANSFORM}')

# COMMAND ----------

spark.sql(f"""
            CREATE OR REPLACE TABLE {TABLE_TRANSFORM} AS
            WITH despachos_consolidados AS (
            SELECT DISTINCT
                -- Identificadores únicos del despacho
                proj_code,
                order_code,
                tkt_code,
                load_num,
                truck_code,
                
                -- Información del pedido
                order_date,
                order_code2,
                cust_code,
                no_cli,
                
                -- Información de la obra
                co_obr,
                de_obr,
                obra_latitud,
                obra_longitud,
                
                -- [resto de campos...]
                -- Información de plantas
                pivot_plant_code,
                pivot_plant_name,
                pivot_plant_latitud,
                pivot_plant_longitud,
                plant_code,
                plant_name,
                plant_latitud,
                plant_longitud,
                
                -- Información del producto y camión
                short_prod_descr,
                prod_code,
                truck_type,
                descr,
                
                -- Cantidades
                delv_qty,
                order_qty,
                
                
                -- Tiempo total del ciclo
                COALESCE(tiempo_a_obra, 0) + 
                COALESCE(tiempo_espera, 0) + 
                COALESCE(tiempo_vaciado, 0) + 
                COALESCE(tiempo_salida, 0) + 
                COALESCE(tiempo_a_planta, 0) AS tiempo_ciclo_total,
                
                tiempo_a_obra,
                tiempo_espera,
                tiempo_vaciado,
                tiempo_salida,
                tiempo_a_planta
                
            FROM {TABLE_INPUT}
            WHERE 
                tkt_code IS NOT NULL 
                AND truck_code IS NOT NULL
                AND order_code IS NOT NULL
            ),

            estadisticas_ciclo AS (
            SELECT
                plant_code,
                plant_name,
                truck_type,
                short_prod_descr,
                cust_code,
                no_cli,
                co_obr,
                de_obr,
                
                COUNT(*) as total_despachos,
                AVG(tiempo_ciclo_total) as promedio_ciclo_despacho,
                MIN(tiempo_ciclo_total) as tiempo_ciclo_minimo,
                MAX(tiempo_ciclo_total) as tiempo_ciclo_maximo
                
            FROM despachos_consolidados
            GROUP BY 
                plant_code, plant_name, truck_type, short_prod_descr,  cust_code, no_cli, co_obr, de_obr
            ),

            estadisticas_por_cliente AS (
            SELECT
                cust_code,
                no_cli,
                plant_code,
                COUNT(*) as total_despachos_cliente,
                AVG(tiempo_ciclo_total) as promedio_ciclo_cliente
            FROM despachos_consolidados
            GROUP BY cust_code, no_cli, plant_code
            ),

            estadisticas_por_obra AS (
            SELECT
                co_obr,
                de_obr,
                cust_code,
                plant_code,
                COUNT(*) as total_despachos_obra,
                AVG(tiempo_ciclo_total) as promedio_ciclo_obra
            FROM despachos_consolidados
            GROUP BY co_obr, de_obr, cust_code, plant_code
            )

            SELECT 
            dc.*,
            ec.promedio_ciclo_despacho,
            ec.total_despachos as despachos_similares,
            epc.total_despachos_cliente,
            epc.promedio_ciclo_cliente,
            epo.total_despachos_obra,
            epo.promedio_ciclo_obra,
            
            -- Clasificaciones
            CASE 
                WHEN dc.tiempo_ciclo_total <= ec.promedio_ciclo_despacho THEN 'Eficiente'
                WHEN dc.tiempo_ciclo_total <= ec.promedio_ciclo_despacho * 1.2 THEN 'Normal'
                ELSE 'Lento'
            END as clasificacion_eficiencia_general,
            
            CASE 
                WHEN dc.tiempo_ciclo_total <= epc.promedio_ciclo_cliente THEN 'Eficiente para Cliente'
                WHEN dc.tiempo_ciclo_total <= epc.promedio_ciclo_cliente * 1.2 THEN 'Normal para Cliente'
                ELSE 'Lento para Cliente'
            END as clasificacion_eficiencia_cliente,
            
            CASE 
                WHEN dc.tiempo_ciclo_total <= epo.promedio_ciclo_obra THEN 'Eficiente para Obra'
                WHEN dc.tiempo_ciclo_total <= epo.promedio_ciclo_obra * 1.2 THEN 'Normal para Obra'
                ELSE 'Lento para Obra'
            END as clasificacion_eficiencia_obra,
            
            -- Rankings
            ROW_NUMBER() OVER (PARTITION BY dc.cust_code ORDER BY dc.tiempo_ciclo_total) as ranking_eficiencia_cliente,
            ROW_NUMBER() OVER (PARTITION BY dc.co_obr ORDER BY dc.tiempo_ciclo_total) as ranking_eficiencia_obra

            FROM despachos_consolidados dc
            INNER JOIN estadisticas_ciclo ec 
            ON dc.plant_code = ec.plant_code
            AND dc.truck_type = ec.truck_type
            AND dc.short_prod_descr = ec.short_prod_descr
            AND dc.cust_code = ec.cust_code
            AND dc.co_obr = ec.co_obr
            LEFT JOIN estadisticas_por_cliente epc
            ON dc.cust_code = epc.cust_code
            AND dc.plant_code = epc.plant_code
            LEFT JOIN estadisticas_por_obra epo
            ON dc.co_obr = epo.co_obr
            AND dc.cust_code = epo.cust_code
            AND dc.plant_code = epo.plant_code
            ORDER BY dc.cust_code, dc.co_obr, dc.order_date
        """)