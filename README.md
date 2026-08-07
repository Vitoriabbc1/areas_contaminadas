# 🍃 Análise Espacial de Pressão Ambiental em Áreas Protegidas 

## Visão Geral
Este projeto realiza uma análise espacial de sobreposição e proximidade entre **Áreas Protegidas (Unidades de Conservação e APAs)** e **Focos de Áreas Contaminadas** no município do Rio de Janeiro. 

O objetivo é ranquear e quantificar as áreas protegidas em situação de vulnerabilidade crítica a até 500m de pontos de contaminação ambiental.

---

## Tecnologias e Ferramentas
* **PostgreSQL / PostGIS**: Banco de dados geoespacial e consultas de proximidade (`ST_DWithin`, `ST_Transform`).
* **QGIS**: Visualização cartográfica, simbologia temática e validação espacial.
* **Docker**: Containerização da instância do banco de dados geoespacial.
