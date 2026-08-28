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
    ...

def main():
    conn = get_connection()
    df = get_frequency_table(conn)
    run_statistical_analysis(df)
    run_subset_analysis(conn)
    conn.close()

if __name__ == "__main__":
    main()