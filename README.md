# Crocodilian Conservation Analysis — MapReduce K-Means Pipeline

A big data pipeline that clusters crocodilian species by morphological and ecological traits to identify conservation priorities. Built with Python and Apache Hadoop using the MapReduce programming model.

## How It Works

The pipeline runs four sequential MapReduce jobs on a real wildlife observation dataset:

1. **Data Cleaning** — Imputes missing values using per-species statistics and infers age class from body length quartiles
2. **Species Aggregation** — Reduces individual observations into per-species feature vectors (body ratio, sexual dimorphism, habitat diversity, geographic range, etc.)
3. **Z-Score Normalization** — Computes global feature statistics via MapReduce and normalizes all features
4. **K-Means Clustering** — Iteratively assigns species to clusters and recomputes centroids over 10 MapReduce rounds

## Output

- Cluster assignments for all species with conservation priority scores
- Statistical analysis report with actionable conservation recommendations
- Visualizations: cluster heatmaps, habitat risk breakdown, geographic at-risk maps, morphological vulnerability patterns

## Results

Species are grouped into 4 clusters and scored by conservation urgency (Critically Endangered ×5, Endangered ×3, Vulnerable ×1), helping identify which habitats and regions need the most immediate protection.
