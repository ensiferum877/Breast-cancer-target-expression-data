import streamlit as st
import plotly.express as px
import pandas as pd

# Set the page to wide layout
st.set_page_config(layout="wide")


# Change the font of the dashboard
font_css = """
<style>
    body {
        font-family: Arial, sans-serif !important;
    }
    .stButton>button {
        font-family: Arial, sans-serif !important;
    }
    .stTextInput>div>div>input {
        font-family: Arial, sans-serif !important;
    }
    .stSelectbox>div>div>select {
        font-family: Arial, sans-serif !important;
    }
    /* Add more Streamlit-specific selectors if needed */
</style>
"""

# Change the color of the sidebar
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #838b8b;
    }
</style>
""", unsafe_allow_html=True)

# Sample data loading function (replace this with your actual data loading logic)
def load_data():
    diffexp_path = 'diffexpdata.csv'
    location_path = 'TargetsLocations.csv'

    diff_df = pd.read_csv(diffexp_path)
    loc_df = pd.read_csv(location_path)

    return diff_df, loc_df

# 2 - Load your data
diff_df, loc_df = load_data()

# 3 - Sidebar - Filter selection
st.sidebar.header("Filter Options")


# Contrast filter with "All" option
contrast_options = ["All"] + sorted(diff_df['Contrast'].dropna().unique())
selected_contrast = st.sidebar.selectbox("Select Contrast", options=contrast_options, index=0)
regulation_threshold = st.sidebar.number_input("Threshold for Gene Regulation (log2foldchange)", value=0.0, step=0.1)
# Slider for rna_value_breast threshold
# Set min and max values as per your dataset's range or leave them open for user input
rna_threshold = st.sidebar.number_input("Minimum RNA Value Breast", value=float(diff_df['rna_value_breast'].min()))

# Study ID filter with "All" option
study_id_options = ["All"] + sorted(diff_df['study_id'].dropna().unique())
selected_study_id = st.sidebar.selectbox("Select Study ID", options=study_id_options, index=0)

# 4 - Apply filters dynamically

if selected_contrast != "All":
    diff_df = diff_df[diff_df['Contrast'] == selected_contrast]
if selected_study_id != "All":
    diff_df = diff_df[diff_df['study_id'] == selected_study_id]

# Apply filters based on the user-entered threshold
if regulation_threshold > 0:
    # If the threshold is positive, select up-regulated genes
    diff_df = diff_df[diff_df['Log2FoldChangeValue'] >= regulation_threshold]
elif regulation_threshold < 0:
    # If the threshold is negative, select down-regulated genes
    diff_df = diff_df[diff_df['Log2FoldChangeValue'] <= regulation_threshold]
else:
    # If the threshold is zero, show all data
    diff_df = diff_df

# Further filter for rna_value_breast
diff_df = diff_df[diff_df['rna_value_breast'] >= rna_threshold]

# Get unique gene IDs from the filtered DataFrame
selected_id = diff_df['id'].unique()

# 5 - Display important numbers

# STEP 3: CREATE THE FIRST ROW CONTAINING IMPORTANT NUMBERS ABOUT THE DATA COLLECTED

unique_counts = {
    "Targets" : diff_df['id'].nunique(),
    "Targets with DE data" : diff_df[diff_df['Log2FoldChangeValue'].notnull()]['id'].nunique(), # it will count the non-null entries
    "Studies": diff_df["study_id"].nunique(),
    "Contrasts": diff_df["Contrast"].nunique(),
}

def display_kpi_tile(title, value):
    """Display a KPI tile with a title and value."""
    st.markdown(f"""
    <div style="padding:20px; 
                border: 1px solid light grey; 
                border-radius: 10px; 
                height: 200px; 
                width: 210px; 
                display: flex; 
                flex-direction: column; 
                justify-content: space-between; 
                align-items: center;">
        <h3 style="color: grey;">{title}</h3>
        <h1 style="height: 70px; 
        display: flex;
        justify-content: space-between;
        align-items: center;">{value}</h1>
    </div>
    """, unsafe_allow_html=True)

def display_dashboard(unique_counts):
    # Display title
    st.title("Breast cancer-associated targets and their exression pattern in breast")

    st.markdown('''
    This dashboard is designed as an interactive tool for the exploration and analysis of breast cancer associated targets expression        data obtained from the Expression Atlas. Users can apply various filters, such as log2foldchange and  rna_value_breast to refine         their data view. The dashboard leverages Plotly for detailed and interactive scatter plot visualizations, allowing for a  deeper         understanding of gene expression correlations. Additional features include a search functionality for pinpointing specific data          points. Overall, this dashboard serves as a powerful resource for conducting thorough and customizable analysis of gene expression       patterns, facilitating insightful scientific discoveries and data-driven decisions in the field of breast cancer.
    '''
    )
    
    # Display all KPI tiles in a single row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_kpi_tile("Targets", unique_counts["Targets"])
    with col2:
        display_kpi_tile("Targets with DE data", unique_counts["Targets with DE data"])
    with col3:
        display_kpi_tile("Studies", unique_counts["Studies"])
    with col4:
        display_kpi_tile("Contrasts", unique_counts["Contrasts"])

display_dashboard(unique_counts)

# Separating line
st.markdown("<hr style='height:2px;border-width:0;color:gray;background-color:gray'>", unsafe_allow_html=True)

# 6 - Create the Plotly chart
col1, col2 = st.columns([1,1])

with col1:

    fig = px.scatter(diff_df, x='Log_RNA_Value_Breast', y='Log2FoldChangeValue',
                 hover_data=['id', 'rna_value_breast'],
                 title='Gene Expression Correlation')

    # Update the size of the plot
    fig.update_layout(
        height=500,  # or any other height in pixels
        width=500   # or any other width in pixels
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig)

with col2:

    st.markdown(
        """
        <style>
        .stTextInput > div > div > input {
            background-color: #838b8b;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Display the DataFrame in Streamlit
    # Filter loc_df using the gene_ids from diff_df
    filtered_loc_df = loc_df[loc_df['id'].isin(selected_id)]
    # Add a text input for search
    search_term = st.text_input("Enter search term:")

    # Specify the column name you want to search in
    search_column = 'locations_clean'

    # Filter based on text search if search_term is not empty
    if search_term:
    # Apply the search term to the specified column
        mask = filtered_loc_df[search_column].astype(str).str.lower().str.contains(search_term.lower())
        search_results_df = filtered_loc_df[mask]
    else:
        search_results_df = filtered_loc_df

    # Display the DataFrame after search filter
    st.write("Filtered DataFrame based on search in column '{}':".format(search_column))
    st.dataframe(search_results_df)
