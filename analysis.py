import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from load_data import get_connection

def get_frequency_table(conn):      # Part 2: Initial Analysis
    query = """
    SELECT
        s.sample_name AS sample,
        SUM(cc.count) OVER (PARTITION BY s.sample_id) AS total_count,
        cc.population,
        cc.count,
        ROUND(cc.count * 100.0 / SUM(cc.count) OVER (PARTITION BY s.sample_id), 2) AS percentage,
        sub.condition,
        sub.treatment,
        sub.response,
        sub.sex,
        s.sample_type
    FROM cell_count cc
    JOIN sample s ON cc.sample_id = s.sample_id
    JOIN subject sub ON s.subject_id = sub.subject_id
    ORDER BY s.sample_name, cc.population
    """
    df = pd.read_sql_query(query, conn)
    df.to_csv("output/frequency_table.csv", index=False)
    return df
    
def run_statistical_analysis(df):   # Part 3: Statistical Analysis
    # Filter to melanoma PBMC samples treated with miraclib
    filtered = df[
        (df["condition"] == "melanoma") &
        (df["sample_type"] == "PBMC") &
        (df["treatment"] == "miraclib")
    ]

    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    results = []

    for pop in populations:
        pop_df = filtered[filtered["population"] == pop]
        responders = pop_df[pop_df["response"] == "yes"]["percentage"]
        non_responders = pop_df[pop_df["response"] == "no"]["percentage"]

        stat, p_value = stats.mannwhitneyu(responders, non_responders, alternative="two-sided")

        results.append({
            "population": pop,
            "p_value": round(p_value, 4),
            "significant": p_value < 0.05
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv("output/stat_analysis.csv", index=False)

    # Boxplot
    fig, axes = plt.subplots(1, 5, figsize=(20, 6))
    for i, pop in enumerate(populations):
        pop_df = filtered[filtered["population"] == pop]
        sns.boxplot(data=pop_df, x="response", y="percentage", ax=axes[i])
        axes[i].set_title(pop)
        axes[i].set_xlabel("Response")
        axes[i].set_ylabel("Frequency (%)")

    plt.suptitle("Cell Population Frequencies: Responders vs Non-Responders")
    plt.tight_layout()
    plt.savefig("output/boxplot.png")
    plt.close()

    return results_df

def run_subset_analysis(conn):      # Part 4: Data Subset Analysis
    query = """
        SELECT
            p.name AS project,
            sub.subject_name,
            sub.response,
            sub.sex,
            s.sample_name,
            s.sample_type,
            s.time_from_treatment_start
        FROM sample s
        JOIN subject sub ON s.subject_id = sub.subject_id
        JOIN project p ON sub.project_id = p.project_id
        WHERE sub.condition = 'melanoma'
        AND s.sample_type = 'PBMC'
        AND s.time_from_treatment_start = 0
        AND sub.treatment = 'miraclib'
    """
    df = pd.read_sql_query(query, conn)

    samples_per_project = df.groupby("project")["sample_name"].count().reset_index()
    samples_per_project.columns = ["project", "sample_count"]

    response_counts = df.drop_duplicates("subject_name").groupby("response")["subject_name"].count().reset_index()
    response_counts.columns = ["response", "subject_count"]

    sex_counts = df.drop_duplicates("subject_name").groupby("sex")["subject_name"].count().reset_index()
    sex_counts.columns = ["sex", "subject_count"]

    samples_per_project.to_csv("output/subset_samples_per_project.csv", index=False)
    response_counts.to_csv("output/subset_response_counts.csv", index=False)
    sex_counts.to_csv("output/subset_sex_counts.csv", index=False)
    
    avg_b_cells_query = """
        SELECT ROUND(AVG(cc.count), 2) AS avg_b_cells
        FROM cell_count cc
        JOIN sample s ON cc.sample_id = s.sample_id
        JOIN subject sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
        AND sub.sex = 'M'
        AND sub.response = 'yes'
        AND s.time_from_treatment_start = 0
        AND cc.population = 'b_cell'
    """
    avg_b_cells = conn.execute(avg_b_cells_query).fetchone()[0]
    print(f"Average B cells (melanoma male responders at time=0): {avg_b_cells:.2f}")

    return samples_per_project, response_counts, sex_counts

def main():
    conn = get_connection()
    df = get_frequency_table(conn)
    run_statistical_analysis(df)
    run_subset_analysis(conn)
    conn.close()

if __name__ == "__main__":
    main()