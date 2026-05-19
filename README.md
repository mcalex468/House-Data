# 🏢 Proyecto Final de Máster: Analisis Histórico (Power BI) & IA Predictora del Índice de Precios de Vivienda (IPV)

Este repositorio contiene el Trabajo de Fin de Máster (TFM) desarrollado para el **Máster en Inteligencia Artificial y Big Data**. El proyecto aborda la problemática social del acceso a la vivienda y la emancipación mediante una solución tecnológica integral que fusiona la ingeniería de datos masivos, el análisis analítico clásico del pasado y la predicción prospectiva del futuro impulsada por Machine Learning.

---

## 📌 Índice de Contenidos
* [1. Descripción del Proyecto](#1-descripción-del-proyecto)
* [2. Arquitectura de Datos (Pipeline Medallion)](#2-arquitectura-de-datos-pipeline-medallion)
* [3. Análisis Histórico (Business Intelligence)](#3-análisis-historico-business-intelligence)
* [4. Motor de Inteligencia Artificial (Modelado)](#4-motor-de-inteligencia-artificial-modelado)
* [5. Conclusiones y Trabajo Futuro](#5-conclusiones-y-trabajo-futuro)
* [6. Tecnologías Utilizadas](#6-tecnologías-utilizadas)
* [7. Ejecución del Entorno](#7-ejecución-del-entorno)

---

## 1. Descripción del Proyecto
El objetivo principal de este sistema es democratizar el acceso al conocimiento inmobiliario y macroeconómico, poniendo la ciencia de datos al servicio del ciudadano. 

Frente a la desinformación actual —marcada por un entorno de alta volatilidad del IPC, leyes habitacionales complejas y un fuerte desacoplamiento entre los precios residenciales y los salarios reales— el ciudadano común carece de herramientas integradas. Las plataformas existentes suelen basarse en informes del pasado (estáticos y con meses de retraso) o en sofisticados modelos predictivos privados y costosos reservados para grandes fondos de inversión. 

Este proyecto rompe esa barrera unificando las fuentes oficiales del Instituto Nacional de Estadística (INE) sobre inflación, renta regional y demografía joven, estructurando toda la información para ofrecer dos experiencias complementarias: comprender con rigor técnico el comportamiento histórico del mercado y simular escenarios económicos interactivos en tiempo real a través de una Inteligencia Artificial accesible para cualquier usuario.

---

## 2. Arquitectura de Datos (Pipeline Medallion)
Para garantizar la integridad, consistencia y correcto tipado de fuentes de datos heterogéneas que venían en formatos dispersos (CSV y XLSX), se diseñó un pipeline robusto de ingeniería de datos estructurado bajo el patrón de arquitectura Medallion.

```text
       [ 🥉 CAPA BRONZE - Ingesta Raw ]
       ├── 1. IPC_Medias_Anuales_2002-2025.csv
       ├── 2. IPV_2007-2024.csv
       ├── 3. Poblacion_CCAA_Edades_2003-2022.csv
       ├── 4. Renta_Media_CCAA_2008-2023.csv
       └── 5. Renta_España-UE.csv
                    │
                    ▼ (Estandarización y Filtrado Técnico)
       [ 🥈 CAPA SILVER - Limpieza y Modelado ]
       ├── Normalización de encodado (Latin-1) y renombrado de cabeceras.
       ├── Pivoteo de tablas temporales y extracción de años (2008-2022).
       ├── Limpieza de strings (stripping) y normalización regional de CC.AA.
       └── Casteo de tipos: Limpieza de separadores de miles/decimales y cast a Float/Int.
                    │
                    ▼ (Unificación y Feature Engineering)
       [ 🥇 CAPA GOLD - Dataset Maestro Negocio ]
       ├── Unión por campos clave (Año, CCAA) formando el Dataset Maestro.
       ├── Creación de Variables Sintéticas (Métricas de Negocio e Inercia).
       └── Archivo optimizado de consumo: `house_data_gold.csv`
```

El resultado de esta arquitectura es una tabla maestra de negocio optimizada que alimenta de manera directa tanto los cuadros de mando como las fases de entrenamiento del modelo:

El resultado de esta arquitectura es una tabla maestra de negocio optimizada que alimenta de manera directa tanto los cuadros de mando como las fases de entrenamiento del modelo:

| Variable | Tipo de Dato | Descripción | Origen / Método de Cálculo |
| :--- | :--- | :--- | :--- |
| **CCAA** | Categórica | Comunidad Autónoma analizada (17 regiones de España). | Registro Original (INE) |
| **Año** | Temporal / Int | Año correspondiente a la serie histórica (2008-2022). | Registro Original (INE) |
| **Indice_IPC** | Numérica (Float) | Índice de Precios al Consumo. Mide la inflación general. | Registro Original (INE) |
| **Precio_Vivienda_IPV** | Numérica (Float) | Índice de Precios de la Vivienda. Variable objetivo del modelo. | Registro Original (INE) |
| **Renta_Media** | Numérica (Int) | Capacidad salarial media anual por hogar en la región. | Registro Original (INE) |
| **Pob_Adulta** | Numérica (Float) | Volumen de población en edad laboral y senior combinada. | Registro Original (INE) |
| **Pob_Joven** | Numérica (Float) | Volumen de población joven (rango de emancipación). | Registro Original (INE) |
| **Pob_Senior** | Numérica (Float) | Volumen de población en edad de jubilación. | Registro Original (INE) |
| **Ratio_Esfuerzo** | Numérica (Float) | Relación de accesibilidad inmobiliaria (Precio Vivienda / Renta). | Procesado (Capa Gold) |
| **Renta_Ajustada_IPC** | Numérica (Float) | Capacidad de compra real descontando el impacto de la inflación. | Feature Engineering ((Renta_Media * 100) / Indice_IPC) |
| **Pct_Pob_Joven** | Numérica (Float) | Porcentaje que representa la población joven sobre el total regional. | Feature Engineering (Pob_Joven / Población Total) |
| **IPV_Anterior** | Numérica (Float) | Histórico de inercia del precio del suelo del año previo (Lag 1). | Feature Engineering (groupby(CCAA).shift(1)) |

---

## 3. Análisis Histórico (Business Intelligence)
Una vez consolidados los datos limpios en la Capa Gold, se desarrolló un cuadro de mandos analítico e interactivo utilizando **Power BI Desktop**. Esta fase del proyecto se enfoca en el estudio descriptivo del pasado:

* **Gestión del Esfuerzo Financiero:** Transformación de microdatos planos en mapas coropléticos y gráficos de dispersión que identifican visualmente qué regiones sufren el mayor estrés inmobiliario.
* **Consolidación de Tendencias:** Permite al analista contextualizar el comportamiento de los mercados locales frente a las crisis de la última década, detectando cómo las variaciones del IPC y el estancamiento de la renta impactan de forma directa en el esfuerzo familiar necesario para acceder a una vivienda.

---

## 4. Motor de Inteligencia Artificial (Modelado)
Para la fase prospectiva y simulación de escenarios futuros en la aplicación web, se entrenó un algoritmo avanzado de aprendizaje supervisado.

### Justificación del Algoritmo
Se seleccionó **`HistGradientBoostingRegressor`** (un modelo basado en conjuntos de árboles de decisión optimizados mediante histogramas) por tres motivos estratégicos:
1. **Eficiencia Categórica:** Manejo nativo y brillante de las regiones geográficas (CC.AA.) sin generar explosiones de dimensionalidad (*One-Hot Encoding* masivos).
2. **Robustez ante Anomalías:** Capacidad de tolerar valores extremos u outliers moderados derivados de fluctuaciones de la economía real sin que el modelo se desestabilise.
3. **Relaciones No Lineales:** La relación entre las variables macroeconómicas y el precio de la vivienda no es una línea recta. Al construir árboles de decisión secuenciales basados en corregir los errores del árbol anterior (*Boosting*), el modelo captura saltos bruscos y patrones económicos complejos con una altísima precisión.

### Estrategia de Validación y Serialización
* **Validación Cruzada Temporal (`TimeSeriesSplit` de 5 Folds):** Evita el error crítico de mezclar datos aleatoriamente (*Data Leakage*). El modelo entrena estrictamente con ventanas del pasado y se examina evaluando el año cronológico posterior, simulando con rigor científico el comportamiento del sistema ante el futuro real.
* **Métricas de Rendimiento:** Evaluado mediante el Coeficiente de Determinación ($R^2$) para certificar la varianza explicada del modelo y el Error Absoluto Medio (MAE) para cuantificar la desviación física media de las predicciones de la IA.
* **Serialización:** Almacenamiento del cerebro entrenado mediante la librería `Joblib` en el archivo persistente `modelo_ipv_v2.pkl`, permitiendo lecturas e inferencias en milisegundos en la aplicación web.

---

## 5. Conclusiones y Trabajo Futuro

### Conclusiones
* **Garantía de la Arquitectura de Datos:** La unificación y el correcto tipado de fuentes heterogéneas mediante el pipeline Medallion demostró ser la infraestructura esencial para garantizar la fiabilidad analítica y el éxito de los modelos de Machine Learning.
* **Evolución del Motor Predictivo:** La selección de modelos basados en Boosting frente a regresiones lineales tradicionales resolvió con éxito el equilibrio entre la inercia histórica del mercado inmobiliario y los giros macroeconómicos imprevistos.
* **Democratización de la Información:** Se consiguió unificar la visión descriptiva del pasado (Power BI) con la simulación interactiva del futuro (Streamlit), cumpliendo el objetivo de poner la ciencia de datos al servicio del ciudadano.

### Líneas de Desarrollo Futuro
1. **Incremento de la Granularidad (Escala Micro):** Evolucionar el alcance actual a nivel de Comunidad Autónoma hacia una estratificación por provincias y municipios, permitiendo mapear "micro-burbujas" locales.
2. **Enriquecimiento Multifuente mediante APIs:** Conectar el sistema de forma automatizada con APIs de portales inmobiliarios para contrastar las predicciones teóricas de la IA con los precios de oferta reales del mercado activo.
3. **Despliegue y Enfoque Nativo Móvil:** Migrar la aplicación a una arquitectura Cloud automatizada (MLOps) y rediseñar la interfaz en formato de App Móvil, adaptando las consultas y alertas al perfil del usuario joven.

---

## 6. Tecnologías Utilizadas
* **Ingeniería de Datos y Modelado:** Python 3.x (`pandas`, `numpy`, `scikit-learn`, `joblib`).
* **Visualización de Datos:** Plotly, Seaborn, Matplotlib (Gráficos interactivos y dinámicos embebidos en el simulador).
* **Entorno Analítico BI:** Power BI Desktop.
* **Interfaz de Usuario Web:** Streamlit (Desarrollo del dashboard reactivo e interactivo para el usuario final).

---
## 7. Ejecución del Entorno

## 7.1 Manual de Instalación

El despliegue de la solución se compone de tres bloques secuenciales que cubren desde el procesamiento de los datos científicos hasta la visualización y la simulación interactiva.

### 1. Requisitos Previos e Ingesta Histórica (Jupyter Notebook)
El entorno base se apoya en la distribución **Anaconda**. Para visualizar y ejecutar el pipeline científico completo, el analista debe seguir estos pasos:
1. Iniciar **Anaconda Navigator**.
2. Lanzar **Jupyter Notebook**.
3. Abrir el cuaderno de trabajo `HouseData.ipynb`.
4. Ejecutar secuencialmente todas sus celdas seleccionando **Cell > Run All** (o *Run All* desde la barra de herramientas).

Al hacer esto, el script realiza de manera automática:
* La limpieza exhaustiva de los datos crudos.
* El cálculo de variables e indicadores clave de la **Capa Oro**, guardando el archivo resultante `house_data_gold.csv`.
* El entrenamiento del modelo de Inteligencia Artificial, exportando inmediatamente después el archivo binario serializado `modelo_ipv_v2.pkl`.

### 2. Explotación del Dashboard (Power BI)
La capa analítica descriptiva se encuentra totalmente consolidada en el archivo `DashboardHouseData.pbix`. 
* **Requisito previo:** El usuario debe contar con la aplicación **Power BI Desktop** (disponible de forma 100% gratuita en la *Microsoft Store* o en la web oficial de Microsoft).
* **Ejecución:** Una vez instalada la aplicación, basta con realizar doble clic sobre el archivo `DashboardHouseData.pbix` para que el cuadro de mandos interactivo se despliegue localmente, quedando listo para su exploración mediante los segmentadores y filtros regionales.

### 3. Despliegue del Servidor Predictivo (Streamlit)
Al ser una solución web interactiva en tiempo real, esta es la única herramienta que requiere el uso de la interfaz de comandos o consola. 
1. Abra **Anaconda Prompt** (o la Terminal del sistema).
2. Navegue hasta el directorio raíz del proyecto e instale las dependencias ejecutando los siguientes comandos:

## 7.2 Manual de Usuario (Guía de Explotación y Análisis)

La arquitectura de análisis está estructurada en 3 niveles de profundidad incremental para permitir una explotación analítica completa:

### Nivel 1: El Origen (Jupyter Notebooks)
* **Qué es:** El laboratorio científico donde se "cocinan" los datos.
* **Para quién:** Usuarios técnicos o auditores que quieran ver cómo se pasó de los datos sucios del INE a la Capa Oro.
* **Cómo se usa:** Se ejecutan las celdas de código para observar el *Storytelling*, pasando rigurosamente por las 5 fases:
  1. Ingesta
  2. Limpieza
  3. Consolidación
  4. EDA (Visualizaciones y Análisis Exploratorio de Datos)
  5. Modelo

### Nivel 2: El Diagnóstico (Dashboard Power BI)
* **Qué es:** La herramienta de análisis histórico encargada de evaluar el pasado y el presente.
* **Objetivo:** Entender "qué ha pasado" hasta ahora en el mercado inmobiliario.
* **Cómo se usa:**
  * **Filtros:** Selecciona tu Comunidad Autónoma y el año en los menús desplegables.
  * **Mapa de Burbujas:** Mira el tamaño de la burbuja para entender la presión del precio en cada zona.
  * **Gráfico de Dispersión:** Busca puntos "fuera de la línea" para detectar de forma ágil dónde la vivienda es demasiado cara respecto a la renta (detección de zonas tensionadas).

### Nivel 3: El Oráculo (App Streamlit)
* **Qué es:** La herramienta de simulación interactiva orientada al futuro.
* **Objetivo:** Ver "qué pasaría si..." cambian las condiciones económicas del entorno.
* **Cómo se usa:**
  * **Entrada de datos:** Mueve los deslizadores (*sliders*) para cambiar los valores del IPC o la Renta.
  * **Predicción:** Pulsa el botón para que la IA calcule instantáneamente el nuevo precio estimado de la vivienda.
  * **Semáforo de Riesgo:** El sistema categoriza el escenario mediante códigos de color visuales:
    * 🟢 **Verde:** Mercado respira, estabilización del IPV.
    * 🔴 **Rojo:** Riesgo de exclusión financiera, aumento crítico del IPV.
