# Harvard University: CS50 SQL (Databases with SQL)

![Build Status](https://github.com/Sais-gallego/harvard-cs50-sql/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Course](https://img.shields.io/badge/Harvard-CS50%20SQL-crimson.svg)

Implementaciones completas de arquitectura relacional, álgebra relacional, normalización (3NF), optimización con índices B-Tree, CTEs recursivas y transacciones ACID del programa oficial de **Harvard University: CS50's Introduction to Databases with SQL**, impartido por **Carter Zenke** y **David J. Malan**.

**Autor:** Sergio Andrés Ipuz Saavedra  
**GitHub:** [@Sais-gallego](https://github.com/Sais-gallego)  
**Institución:** Harvard University (CS50)

---

## 🏛️ Núcleos de Base de Datos y Arquitectura Relacional

### 1. Esquema Relacional en Tercera Forma Normal (3NF) (`src/relational_engine.py`)
- Entidades normalizadas (`students`, `courses`, tabla intermedia `enrollments`).
- Restricciones de integridad referencial: `FOREIGN KEY ... ON DELETE CASCADE`, `CHECK`, `UNIQUE` y tipos estrictos.

### 2. Consultas Complejas, Agregaciones y Vistas Virtuales
- Joins multi-tabla (`INNER JOIN`, `LEFT JOIN`), funciones de agregación (`COUNT`, `AVG`, `SUM`, `HAVING`).
- Creación de vistas virtuales dinámicas (`CREATE VIEW honors_students`) para abstracción de consultas analíticas frecuentes.

### 3. Expresiones de Tablas Comunes Recursivas (Recursive CTEs)
- Modelado de grafos de dependencias acíclicos mediante `WITH RECURSIVE` para resolución jerárquica de prerequisitos académicos.

### 4. Optimización de Consultas y Benchmarking con Índices B-Tree
- Análisis de planes de ejecución mediante `EXPLAIN QUERY PLAN`, demostrando la transición de `SCAN TABLE` (complejidad $O(N)$) a `SEARCH TABLE USING INDEX` (complejidad $O(\log N)$).

### 5. Transacciones ACID y Atomicidad
- Control de transacciones mediante `BEGIN TRANSACTION`, `COMMIT` y `ROLLBACK` ante excepciones, garantizando la consistencia y atomicidad de las operaciones de base de datos.

---

## 🧪 Pruebas Automatizadas

```bash
python -m unittest discover tests -v
```

### Resultados de la Suite (6/6 Passed ✅)
```text
test_acid_transaction_commit_and_rollback ... ok
test_b_tree_indexing_optimization ... ok
test_multi_table_joins_and_aggregations ... ok
test_recursive_cte_prerequisites ... ok
test_schema_and_integrity_constraints ... ok
test_virtual_view_honors_students ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.019s

OK
```
