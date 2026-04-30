# ecommerce-ai-agent

Agente de IA para operaciones de e-commerce construido con **LangGraph + MCP Server propio**, usando datos reales del dataset público **Olist Brazilian E-Commerce** cargados en PostgreSQL.

El objetivo del proyecto es demostrar una arquitectura profesional de AI Engineering: agente orquestado con LangGraph, herramientas de negocio expuestas vía MCP, API con FastAPI, UI con Streamlit, observabilidad con LangSmith y ejecución reproducible con Docker Compose.

---

## Estado actual

**Semana 1 — Infraestructura y datos**

Completado:

- Estructura base del repositorio.
- Docker Compose con PostgreSQL, Ollama, FastAPI y Streamlit.
- Imagen reusable mediante `Dockerfile`.
- Configuración async de SQLAlchemy.
- Modelos ORM para las tablas principales de Olist.
- Migraciones Alembic iniciales.
- Script de carga CSV → PostgreSQL.
- Dataset Olist cargado en PostgreSQL.
- Notebook EDA básico.
- Comandos `make` para operación local.
- CI básico con GitHub Actions para lint y tests.

Siguiente fase:

**Semana 2 — MCP Server**

Implementar las herramientas MCP de ventas, inventario y reporting con queries reales a PostgreSQL, schemas Pydantic v2 y tests unitarios.

---

## Stack

| Capa | Tecnología |
|---|---|
| Orquestación agente | LangGraph |
| Tool protocol | MCP Server propio con Python `mcp` SDK |
| LLM principal | Ollama + LLaMA 3.1 8B |
| LLM fallback/demo | Groq API |
| API | FastAPI |
| UI | Streamlit |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy async |
| Migraciones | Alembic |
| Observabilidad | LangSmith |
| Infraestructura | Docker Compose |
| Testing | pytest |
| Lint/format | Ruff + Black |
| CI | GitHub Actions |

---

## Arquitectura resumida

```text
Streamlit UI
    ↓ HTTP
FastAPI
    ↓
LangGraph Agent
    ↓ MCP Protocol
MCP Server propio
    ↓
PostgreSQL + Dataset Olist
```

El agente tendrá un flujo basado en tres nodos principales:

```text
planner → tool_node → synthesizer
```

Con un condicional `should_continue` para permitir múltiples iteraciones de herramientas cuando una consulta de negocio lo requiera.

---

## Requisitos

- Docker Desktop
- Docker Compose v2
- Python 3.11+
- Make para Windows o equivalente disponible en PowerShell
- Git

En Windows, el proyecto se ha validado usando **PowerShell**.

---

## Configuración inicial

Clonar el repositorio:

```powershell
git clone <repository-url>
cd ecommerce-ai-agent
```

Crear entorno virtual local:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias de desarrollo:

```powershell
pip install -e ".[dev]"
```

Crear archivo `.env` desde el ejemplo:

```powershell
Copy-Item .env.example .env
```

El `.env` debe mantenerse orientado a Docker. La variable de base de datos debe usar el host `postgres`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/ecommerce_ai_agent
```

No cambiarlo a `localhost` para los servicios Docker.

---

## Levantar servicios

```powershell
docker compose up --build
```

Servicios esperados:

| Servicio | Puerto |
|---|---|
| FastAPI | 8000 |
| Streamlit | 8501 |
| PostgreSQL | 5432 |
| Ollama | 11434 |

Healthcheck básico de FastAPI:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

---

## Comandos principales

```powershell
make run
```

Levanta los servicios con Docker Compose.

```powershell
make migrate
```

Aplica migraciones Alembic dentro del contenedor `api`.

```powershell
make migration
```

Crea una nueva migración Alembic.

```powershell
make load-data
```

Carga el dataset Olist desde `data/raw/olist` hacia PostgreSQL.

```powershell
make lint
```

Ejecuta Ruff y Black en modo check.

```powershell
make format
```

Aplica autofix con Ruff y formatea con Black.

```powershell
make test
```

Ejecuta tests con pytest dentro del contenedor `api`.

```powershell
make shell
```

Abre una shell dentro del contenedor `api`.

```powershell
make db-shell
```

Abre una sesión `psql` contra PostgreSQL.

---

## Migraciones de base de datos

Aplicar migraciones:

```powershell
make migrate
```

Equivalente manual:

```powershell
docker compose run --rm api alembic upgrade head
```

Crear una nueva migración:

```powershell
docker compose run --rm api alembic revision --autogenerate -m "migration message"
```

---

## Dataset Olist

El proyecto usa el dataset público **Brazilian E-Commerce Public Dataset by Olist**.

Ubicación esperada local:

```text
data/raw/olist
```

La carpeta `data/` está ignorada por Git para evitar subir archivos pesados o datasets locales.

Estructura esperada:

```text
data/raw/olist/
├── olist_customers_dataset.csv
├── olist_geolocation_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_orders_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
└── product_category_name_translation.csv
```

Actualmente se cargan las tablas principales necesarias para el MVP:

- `customers`
- `sellers`
- `products`
- `orders`
- `order_items`
- `order_payments`
- `order_reviews`
- `product_category_name_translation`

Cargar datos:

```powershell
make load-data
```

Equivalente manual:

```powershell
docker compose run --rm api python -m scripts.load_olist_data --data-dir data/raw/olist
```

---

## Notebook EDA

Notebook inicial:

```text
notebooks/olist_exploration.ipynb
```

Incluye:

- Conteo de filas por tabla.
- Rango de fechas de órdenes.
- Revenue total aproximado.
- Top categorías por revenue.
- Top productos por ventas.
- Distribución básica de estados de órdenes.

Para correrlo desde VS Code/Jupyter en Windows, el notebook usa por defecto:

```text
postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_ai_agent
```

Esto es intencional para ejecución desde host. El `.env` del proyecto debe seguir usando `postgres` para Docker.

Opcionalmente puedes definir:

```powershell
$env:NOTEBOOK_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_ai_agent"
```

---

## Lint y tests

Ejecutar lint:

```powershell
make lint
```

Ejecutar tests:

```powershell
make test
```

Aplicar formato automático:

```powershell
make format
```

Antes de abrir un Pull Request o pushear a `main`, se recomienda correr:

```powershell
make format
make lint
make test
```

---

## CI

El proyecto incluye un workflow básico de GitHub Actions:

```text
.github/workflows/ci.yml
```

El pipeline ejecuta:

- Build de servicios Docker.
- Migraciones Alembic.
- Ruff.
- Black check.
- pytest.

Esto asegura que el código pase validaciones básicas en cada push o pull request.

---

## Roadmap resumido

| Semana | Foco | Estado |
|---|---|---|
| Semana 1 | Infraestructura y datos | Completada |
| Semana 2 | MCP Server | Pendiente |
| Semana 3 | Agente LangGraph | Pendiente |
| Semana 4 | API + Reporting tools | Pendiente |
| Semana 5 | UI + Pulido MVP | Pendiente |
| Semana 6 | Diferenciadores post-MVP | Pendiente |
| Semana 7 | Evaluación y lanzamiento | Pendiente |

---

## Herramientas MCP planeadas

### Sales

- `get_top_products`
- `get_revenue_trend`
- `get_sales_by_category`

### Inventory

- `get_low_stock_products`
- `get_no_movement_products`
- `get_stock_alerts`

### Reporting

- `generate_executive_report`
- `export_report_markdown`

Total: **8 herramientas MCP**.

---

## Decisiones técnicas clave

- **LangGraph sobre LangChain AgentExecutor** por mayor control del flujo, estado explícito y mejor trazabilidad.
- **MCP Server propio** como capa de herramientas para separar el razonamiento del agente de las queries SQL.
- **Ollama local + Groq fallback** para balancear costo cero, privacidad y mejor razonamiento en demos.
- **PostgreSQL + SQLAlchemy async** para una base relacional realista y queries production-grade.
- **Streamlit para el MVP** para priorizar el agente, MCP y evaluación antes que una UI compleja.

---

## Limitaciones conocidas

- El dataset Olist llega hasta 2018, por lo que los análisis no representan datos actuales.
- Olist no incluye inventario explícito; las herramientas de inventario del MVP inferirán señales a partir de ventas y movimiento de productos.
- El LLM local puede tener menor capacidad de razonamiento que modelos propietarios grandes.
- La memoria conversacional persistente queda fuera del MVP inicial.

---

## Convenciones de commits

El proyecto usa conventional commits:

```text
feat: add new feature
fix: correct a bug
docs: update documentation
test: add or update tests
ci: update CI configuration
build: update build or dependency configuration
refactor: improve code structure without changing behavior
```

Ejemplos usados en Semana 1:

```text
feat: add initial docker compose infrastructure
build: add reusable application docker image
feat: add sqlalchemy models for olist dataset
feat: add olist data loading script
docs: add initial olist exploration notebook
ci: add lint and test workflow
```

---

## Próximo paso

Continuar con **Semana 2 — MCP Server**:

1. Crear estructura `src/mcp_server/`.
2. Definir schemas Pydantic v2 para inputs/outputs.
3. Implementar herramientas Sales.
4. Implementar herramientas Inventory.
5. Agregar tests unitarios.
6. Documentar ADR del diseño MCP.
