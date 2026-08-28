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
            ROUND(cc.count * 100.0 / SUM(cc.count) OVER (PARTITION BY s.sample_id), 2) AS percentage
        FROM cell_count cc
        JOIN sample s ON cc.sample_id = s.sample_id
        ORDER BY s.sample_name, cc.population
    """
    df = pd.read_sql_query(query, conn)
    df.to_csv("output/frequency_table.csv", index=False)
    return df
    
def run_statistical_analysis(df):   # Part 3: Statistical Analysis
    ...

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