from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Set page layout
st.set_page_config(page_title="Zomato EDA", layout="wide")

st.title("🍽 Zomato Dataset - EDA Dashboard")

# --- Load Data ---
@st.cache_data
def get_datasets():
    try:
        df = pd.read_csv("zomato.csv", encoding="latin-1")
        country_df = pd.read_excel("Country-Code.xlsx")
        final_df = pd.merge(df, country_df, on="Country Code", how="left")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None
    return df, country_df, final_df

df, df_country, final_df = get_datasets()

# Sidebar Menu
with st.sidebar:
    selected = option_menu(
        "Zomato Explorer",
        ["Overview", "Statistics", "Visualizations"],
        icons=["info-circle", "bar-chart", "graph-up"],
        menu_icon="🍴",
        default_index=0,
    )

# --- OVERVIEW TAB ---
if selected == "Overview":
    st.header("📋 Dataset Information")

    tab1, tab2, tab3 = st.tabs(["Preview", "Details", "Stats"])

    with tab1:
        st.write("### First Few Rows")
        st.dataframe(df.head(10))

        st.write("### Last Few Rows")
        st.dataframe(df.tail(5))

    with tab2:
        st.write("### Column Names")
        st.table(pd.DataFrame(df.columns, columns=["Columns"]))

        st.write("### Shape of Data")
        st.write(f"{df.shape[0]} rows × {df.shape[1]} columns")

        st.write("### Missing Values")
        nulls = df.isnull().sum()
        st.dataframe(nulls[nulls > 0])

        if nulls.sum() > 0:
            fig, ax = plt.subplots(figsize=(4, 3))
            nulls[nulls > 0].plot(kind="bar", ax=ax)
            st.pyplot(fig)
        else:
            st.success("No missing values 🎉")

    with tab3:
        st.write("### Unique Value Counts")
        st.dataframe(df.nunique())

        st.write("### Descriptive Stats")
        st.dataframe(df.describe())

# --- STATISTICS TAB ---
elif selected == "Statistics":
    st.header("📊 Dataset Statistics")

    st.sidebar.subheader("Filter Options")
    countries = ["All"] + sorted(final_df["Country"].unique().tolist())
    choice = st.sidebar.selectbox("Choose Country", countries)

    filtered_df = final_df if choice == "All" else final_df[final_df["Country"] == choice]

    st.write(f"Showing statistics for: **{choice}**")
    st.dataframe(filtered_df.describe(include="all"))

    st.write("**Number of Restaurants:**", len(filtered_df))
    st.write("**Unique Cities:**", filtered_df["City"].nunique())
    st.write("**Average Rating:**", round(filtered_df["Aggregate rating"].mean(), 2))

    if "Cuisines" in filtered_df:
        try:
            st.write("**Most Common Cuisine:**", filtered_df["Cuisines"].mode()[0])
        except:
            st.write("Cuisine data not available")

# --- VISUALIZATIONS TAB ---
elif selected == "Visualizations":
    st.header("📈 Visualizations")

    countries = ["All"] + sorted(final_df["Country"].unique().tolist())
    choice = st.sidebar.selectbox("Choose Country", countries)

    filtered_df = final_df if choice == "All" else final_df[final_df["Country"] == choice]

    # Top Cities
    st.subheader("Top 5 Cities by Restaurants")
    top_cities = filtered_df["City"].value_counts().head(5).reset_index()
    top_cities.columns = ["City", "Count"]
    fig_city = px.bar(top_cities, x="City", y="Count", color="City", text="Count")
    st.plotly_chart(fig_city)

    # Top Cuisines
    st.subheader("Top 5 Cuisines")
    top_cuisines = filtered_df["Cuisines"].value_counts().head(5).reset_index()
    top_cuisines.columns = ["Cuisine", "Count"]
    fig_cuisine = px.bar(top_cuisines, x="Cuisine", y="Count", color="Cuisine", text="Count")
    st.plotly_chart(fig_cuisine)

    # Price Distribution
    st.subheader("Price Range Distribution")
    price_counts = filtered_df["Price range"].value_counts().reset_index()
    price_counts.columns = ["Price Range", "Count"]
    fig_price = px.pie(price_counts, names="Price Range", values="Count", hole=0.4)
    st.plotly_chart(fig_price)

    # Ratings
    st.subheader("Rating Distribution")
    rating_counts = filtered_df["Rating text"].value_counts().reset_index()
    rating_counts.columns = ["Rating", "Count"]
    fig_rating = px.bar(rating_counts, x="Rating", y="Count", color="Rating", text="Count")
    st.plotly_chart(fig_rating)
