# 🏢 Proyecto Final de Máster: IA Predictora del Índice de Precios de Vivienda (IPV)

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
  [ FUENTES DE DATOS ]
  ↳ INE: Inflación (Índice de Precios de Consumo - IPC)
  ↳ INE: Renta Media Anual Regional por Hogar
  ↳ INE: Demografía de Población Joven (16-30 años)
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 🥉 CAPA BRONZE (Ingesta Raw)                           │
│    - Almacenamiento de archivos crudos sin procesar.   │
│    - Preservación del estado original de la extracción. │
└────────────────────────────────────────┬───────────────┘
                                         │ (Limpieza y Tipado)
                                         ▼
┌────────────────────────────────────────────────────────┐
│ 🥈 CAPA SILVER (Enriquecimiento y Limpieza)            │
│    - Tratamiento de strings y codificaciones nulas.     │
│    - Normalización de nombres de las CC.AA.            │
│    - Filtrado temporal y conversión a tipos float/int. │
└────────────────────────────────────────┬───────────────┘
                                         │ (Feature Engineering)
                                         ▼
┌────────────────────────────────────────────────────────┐
│ 🥇 CAPA GOLD (Dataset Maestro Negocio)                 │
│    - Unificación temporal por campos clave (Año, CCAA). │
│    - Feature Engineering: Renta Ajustada por IPC.      │
│    - Archivo optimizado de consumo: `house_data_gold.csv`│
└────────────────────────────────────────────────────────┘

El resultado de esta arquitectura es una tabla maestra de negocio optimizada que alimenta de manera directa tanto los cuadros de mando como las fases de entrenamiento del modelo:

| Variable | Tipo de Dato | Capa de Origen | Descripción Conceptual |
| :--- | :--- | :--- | :--- |
| **Año** | Integer (Index) | Silver | Clave temporal anual del registro |
| **CCAA** | String (Categórico) | Silver | Región geográfica (Comunidad Autónoma) de España |
| **Indice_IPC** | Float | Silver | Métrica de inflación oficial base 100 del INE |
| **Renta_Media** | Float | Silver | Ingresos medios anuales por hogar en la región |
| **Renta_Ajustada_IPC** | Float | Gold (Calculada) | Feature Engineering: Capacidad adquisitiva real deflactada |
| **Pct_Pob_Joven** | Float | Silver | Porcentaje demográfico de población en edad de emancipación |
| **Precio_Vivienda_IPV** | Float (Target) | Silver | Índice oficial (IPV) que mide la evolución de precios |

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
* **Visualización de Datos:** Plotly (Gráficos interactivos y dinámicos embebidos en el simulador).
* **Entorno Analítico BI:** Power BI Desktop.
* **Interfaz de Usuario Web:** Streamlit (Desarrollo del dashboard reactivo e interactivo para el usuario final).

---

   
