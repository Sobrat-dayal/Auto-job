# AUTONOM Role & Specialization Taxonomy

## Stage 25 of 50 — Technical Classification

---

### 11 Role Families

AUTONOM classifies all technical and product roles into standard role families to prevent semantic drift:

1. **`backend`**: Distributed systems, microservices, high-throughput APIs, server architectures, databases.
2. **`frontend`**: Web UI, React/Vue/Angular, browser performance, accessibility, responsive styling.
3. **`fullstack`**: End-to-end web applications, combined client and server implementations.
4. **`software_engineering`**: General core software engineering, algorithms, general systems.
5. **`cloud_devops`**: Cloud infrastructure (AWS/GCP/Azure), Kubernetes, CI/CD, Terraform, SRE, observability.
6. **`ai_ml_engineering`**: Machine learning infrastructure, MLOps, model deployment, inference optimization, vector DBs.
7. **`ai_research`**: Theoretical machine learning, algorithmic breakthroughs, model pre-training, novel architectures.
8. **`data_engineering`**: ETL/ELT pipelines, Spark, BigQuery, Kafka, data lakes, distributed data warehousing.
9. **`data_science`**: Statistical modeling, business analytics, experimentation, predictive metrics.
10. **`systems_embedded`**: Embedded systems, kernel development, C/C++, firmware, IoT.
11. **`cybersecurity`**: InfoSec, application security, penetration testing, compliance, cryptography.

---

### Non-Conflation Rules

The `RoleTaxonomyEngine` explicitly separates commonly conflated roles:
- **ML Researcher != MLOps Engineer**: Research focuses on publication and training dynamics; MLOps focuses on Kubernetes serving, GPU clusters, and monitoring.
- **Data Analyst != Data Scientist**: Analysis emphasizes SQL and BI dashboards; Science emphasizes statistical modeling and feature engineering.
- **Engineering Manager != Individual Contributor**: Management involves people and delivery; IC focuses on architectural design and code authoring.
