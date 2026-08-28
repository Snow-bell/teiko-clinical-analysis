import streamlit as st
import pandas as pd
from PIL import Image

st.title("Teiko Assessment — Clinical Trial Cell Population Analysis")

tab1, tab2, tab3 = st.tabs(["Frequency Table", "Statistical Analysis", "Subset Analysis"])

with tab1:
    st.header("Cell Population Frequencies")
    df = pd.read_csv("output/frequency_table.csv")
    st.dataframe(df)

with tab2:
    st.header("Statistical Analysis: Responders vs Non-Responders")
    st.image("output/boxplot.png", use_column_width=True)
    st.subheader("Mann-Whitney U Test Results")
    stat_df = pd.read_csv("output/stat_analysis.csv")
    st.dataframe(stat_df)

with tab3:
    st.header("Subset Analysis: Melanoma PBMC Baseline Miraclib Samples")
    st.subheader("Samples per Project")
    st.dataframe(pd.read_csv("output/subset_samples_per_project.csv"))
    st.subheader("Responders vs Non-Responders")
    st.dataframe(pd.read_csv("output/subset_response_counts.csv"))
    st.subheader("Males vs Females")
    st.dataframe(pd.read_csv("output/subset_sex_counts.csv"))