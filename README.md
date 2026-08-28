## Database Schema

<img src="docs/er-diagram.svg" width="750" height="750"/>

The schema is organized into four tables: `project`, `subject`, `sample`, and `cell_count`. This relational database is designed to be in Third Normal Form (3NF).

### Design rationale

The schema follows a natural hierarchy derived from the clinical trial data: a `project` has multiple `subject`s, each subject provides multiple `sample`s, and each sample has a `cell_count` row per immune cell population.

Separating `subject` from `sample` is a key design decision. A subject can appear multiple times across timepoints, so collapsing them into one table would duplicate subject-level attributes like `condition`, `treatment`, and `response` across every sample row, violating 3NF.

Cell counts are stored in a normalized `cell_count` table with one row per population per sample, rather than as columns on the sample table. This means adding new cell populations requires no schema changes, just new rows — which is important as cytometry panels evolve across projects.

### Scalability

At scale, with hundreds of projects, thousands of samples, and varied analytics, this schema holds up well:

- **Query performance**: adding indexes on `subject.project_id`, `sample.subject_id`, and `cell_count.sample_id` keeps joins fast as row counts grow
- **New populations**: the normalized `cell_count` table accommodates new cell types without `ALTER TABLE`
- **New metadata**: additional subject or sample attributes can be added as columns without restructuring the core schema
- **Analytics**: aggregations like frequency calculations naturally group by `sample_id` across the `cell_count` table, and filtering by `condition`, `treatment`, or `response` joins cleanly through the hierarchy

If the dataset scaled to millions of rows, this schema could migrate to PostgreSQL with minimal changes. The same structure supports partitioning by project and parallel query execution.

## Instructions

### Requirements
- Python 3.8+
- Git

### Setup
Clone the repository and run:

```bash
make setup
```

This installs all necessary dependencies from `requirements.txt`.

### Running the pipeline
To initialize the database, load the data, and generate all output tables and plots, run:

```bash
make pipeline
```

### Running the dashboard
To start the local dashboard server, run:

```bash
make dashboard
```

Then open the link provided in the terminal.

### Reproducing outputs
Running `make pipeline` is all that is needed to reproduce all outputs. The pipeline runs sequentially from start to finish without any manual intervention.

## Code Structure

### Overview
```
teiko-clinical-analysis/
├── load_data.py     # Initializes SQLite database and loads cell-count.csv
├── analysis.py      # Runs all analysis (Parts 2-4)
├── dashboard.py     # Streamlit dashboard
├── cell-count.csv   # Input data
├── requirements.txt # Python dependencies
├── Makefile         # Setup, pipeline, and dashboard targets
├── docs/
│ └── er-diagram.svg # Entity relationship diagram
└── output/
├── frequency_table.csv # Part 2 output
├── stat_analysis.csv   # Part 3 output
├── boxplot.png         # Part 3 boxplot
├── subset_samples_per_project.csv # Part 4 output
├── subset_response_counts.csv     # Part 4 output
└── subset_sex_counts.csv          # Part 4 output
```


### Design decisions

The pipeline is split into two scripts: `load_data.py` handles database initialization and data loading, while `analysis.py` handles all analytical tasks. This separation keeps data ingestion and analysis concerns independent, so if the data changes, only `load_data.py` needs to be updated.

All three analysis parts live in `analysis.py` as separate functions to keep the code organized without cluttering the repo with multiple files. 

The dashboard in `dashboard.py` reads directly from the output CSVs and PNG rather than rerunning the analysis, keeping it lightweight and fast.

## Dashboard

[View the dashboard](https://teiko-clinical-analysis-6cgjwnj57nq2bmbwczt9kr.streamlit.app/#teiko-assessment-clinical-trial-cell-population-analysis)