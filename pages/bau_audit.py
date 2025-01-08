import streamlit as st
import pandas as pd
import math
import json


# Load user profiles from JSON file
with open('user_profiles.json') as f:
    user_profiles_data = json.load(f)


# Define helper functions
def filter_criteria(df):
    df = df[~df['User Profile'].str.contains('OGRDS SYSTEM', na=False)]
    df = df[~df['Changed Using'].str.contains('ITEM CODING|SURGERY', na=False, case=False)]
    df = df[df['Current Destination Item Specificity'] == 'CONSOLIDATED ITEM']
    df = df[df['Current Nielsen Item Description'].notna()]
    return df

def sample_priority_modules(df, module_col, priority_modules, percentage):
    sampled_modules = []
    for module in priority_modules:
        module_group = df[df[module_col] == module]
        if not module_group.empty:
            required_count = math.ceil(len(module_group) * (percentage / 100))
            sampled_modules.append(module_group.sample(n=required_count))
    sampled_df = pd.concat(sampled_modules).drop_duplicates(subset='External Code') if sampled_modules else pd.DataFrame(columns=df.columns)
    remaining_df = df[~df.index.isin(sampled_df.index)]
    return sampled_df, remaining_df

def ensure_min_samples_per_user(df, df_sampled, df_remaining, user_col, percentage):
    user_entries = df.groupby(user_col).size()
    min_required = user_entries * (percentage / 100)
    for user, group in df.groupby(user_col):
        sampled_user = df_sampled[df_sampled[user_col] == user]
        if len(sampled_user) < min_required[user]:
            additional_entries = df_remaining[df_remaining[user_col] == user]
            needed = math.ceil(min_required[user] - len(sampled_user))
            if not additional_entries.empty:
                additional_entries = additional_entries.drop_duplicates(subset='External Code')
                df_sampled = pd.concat([df_sampled, additional_entries.sample(n=min(len(additional_entries), needed))])
    return df_sampled.drop_duplicates(subset='External Code')

def ensure_final_samples(df, df_sampled, user_col, min_samples):
    for user, group in df.groupby(user_col):
        sampled_user = df_sampled[df_sampled[user_col] == user]
        if len(sampled_user) < min_samples:
            additional_entries = group[~group.index.isin(df_sampled.index)]
            needed = min_samples - len(sampled_user)
            if not additional_entries.empty:
                additional_entries = additional_entries.drop_duplicates(subset='External Code')
                df_sampled = pd.concat([df_sampled, additional_entries.sample(n=min(len(additional_entries), needed))])
    return df_sampled.drop_duplicates(subset='External Code')

# Streamlit App
st.title("OMNI Audit Sampling Tool")

# Sidebar parameters
st.sidebar.header("Sampling Parameters")
priority_percentage = st.sidebar.text_input("Priority Module Percentage", value="40")
user_percentage = st.sidebar.text_input("User Profile Percentage", value="20")
min_samples = st.sidebar.text_input("Minimum Samples per User", value="50")

# User Profile Selection

# User Profile Selection
set_option = st.sidebar.radio("Select User Profile Set", options=["Shopper", "SOS", "Both"])

user_profiles = user_profiles_data.get(set_option, [])

# Validate inputs
try:
    priority_percentage = int(priority_percentage)
    user_percentage = int(user_percentage)
    min_samples = int(min_samples)
except ValueError:
    st.sidebar.error("Please enter valid numerical values for all parameters.")

# Upload file
uploaded_file = st.file_uploader("Upload an csv File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, low_memory=False)

    # Filter criteria
    df = filter_criteria(df)
    df['Module'] = df['Current Nielsen Item Description'].str.split('|').str[0]

    priority_modules = [
        "BEER","HEALTH & PERFORMANCE POWDER","DOG FOOD WET","DOG FOOD DRY","LAXATIVES","SUPPLEMENTS","BATH TISSUE","PREPARED COCKTAILS","RX PRESCRIPTIONS TOTAL","SIDES","BABY WIPE","BEER/FMB/CIDER (DETAIL UNKNOWN)","DOG FOOD SUB CATEGORY DETAIL UNKNOWN","MAC & CHEESE","MEAT SNACK","SHAVING CREAM","SNACK COMBOS","TEA","WHISKEY","CORDIALS","FUEL TOTAL","HEALTH & PERFORMANCE SHAKES","ENERGY BEVERAGES","COCONUT WATER","DAIRY BASED DRINKS","FRUIT/VEG JUICE & DRINK","KOMBUCHA","LEMONADE","OTHER PROBIOTIC DRINK","SELTZER WATER/TONIC WATER/CLUB SODA","SMOOTHIES (BEVERAGES)","SOFT DRINKS","SPARKLING JUICE","SPORT DRINKS","VALUE ADD WATER","WATER","BEVERAGES (DETAIL UNKNOWN)","BEVERAGES COMBINATION PACK","REMAINING FOUNTAIN DRINK","ASIAN SAUCE","BARBECUE & WING SAUCE","CHEESE SAUCE (SAUCE/GRAVY/MARINADE)","CURRY PASTE","GRAVY (SAUCE/GRAVY/MARINADE)","LATINO SAUCE","MOLE PASTE","PASTA SAUCE (SAUCE/GRAVY/MARINADE)","VARIETY PACK (SAUCE/GRAVY/MARINADE)","ANCHOVY PASTE","COOKING SAUCE ADD MEAT","FRUIT SAUCE/GLAZE","GLAZE","MARINADE","PIZZA SAUCE","REMAINING PASTE","REMAINING SAUCE","SAUCE/GRAVY/MARINADE (DETAIL UNKNOWN)","SAUCE/GRAVY/MARINADE COMBINATION PACKS","SEAFOOD SAUCE","TOMATO PASTE","TOMATO SAUCE","APPETIZER","APPETIZER PARTY PLATTER","BAGELS & SPREADS","BREAKFAST MEALS & SANDWICHES","CALZONE/STROMBOLI","CANNED MEAT","COMPLETE MEAL & MAIN COURSE","COOKING GREENS (PREPARED FOODS)","DRY MIXES","FRENCH TOAST","HANDHELD ENTREES","LASAGNA","MAC & CHEESE","MEAL KIT","OTHER DELI BREAKFAST FOODS","PANCAKE","PASTA (PREPARED FOODS)","POT PIE","PREPARED FOODS VARIETY PACK","SALADS","SANDWICH PARTY PLATTER","SANDWICHES","SOUP/STEW/BROTH/BOUILLON","SUSHI","SUSHI PARTY PLATTER","VEGETABLE/SALAD STARTERS","WAFFLE","BLINTZES","BREAKFAST MEAT","FRITTATA","OMELETS","PREPARED FOODS (DETAIL UNKNOWN)","PREPARED FOODS COMBINATION PACK","QUICHE","RAMEN","REMAINING BREAKFAST FOODS","VEGETABLE NOODLES","CEREAL & GRANOLA BARS","HEALTH/NUTRITION BARS","PERFORMANCE NUTRITION BARS","SPECIALTY NUTRITION BARS","WEIGHT MANAGEMENT BARS","NUTRITION & CEREAL BARS (DETAIL UNKNOWN)","CAT FOOD DRY","CAT FOOD WET","CAT TREATS","CAT FOOD SUB CATEGORY DETAIL UNKNOWN","MINERALS","VITAMINS","VITAMINS & SUPPLEMENTS (DETAIL UNKNOWN)","VITAMINS & SUPPLEMENTS COMBINATION PACKS","COOKIES (COOKIES & CRACKERS)","CRACKERS","COOKIE & CRACKER VARIETY PACK","COOKIES & CRACKERS (DETAIL UNKNOWN)","COOKIES COMBINATION PACKS","DOG TREATS","ASSORTED CAT & DOG FOOD","BIRD FOOD","FISH FOOD","DOG FOOD SUB CATEGORY DETAIL UNKNOWN","PET FOOD (DETAIL UNKNOWN)","PET FOOD COMBINATION PACKS","REMAINING PET FOOD","UNCODEABLE","FOOD (DETAIL UNKNOWN)","NPD LOW SALES"
    ]

    # Filter based on selected User Profile Set
    df = df[df['User Profile'].isin(user_profiles)]

    # Sampling steps
    df_sampled, df_remaining = sample_priority_modules(df, 'Module', priority_modules, priority_percentage)
    df_sampled = ensure_min_samples_per_user(df, df_sampled, df_remaining, 'User Profile', user_percentage)
    df_sampled = ensure_final_samples(df, df_sampled, 'User Profile', min_samples)

    # Display summaries
    st.subheader("Final Sampled Data")
    st.dataframe(df_sampled)

    category_summary = df_sampled.groupby('Module').size().reset_index(name='Sample Count')
    total_volume_by_module = df.groupby('Module').size().reset_index(name='Total Volume')
    category_summary = category_summary.merge(total_volume_by_module, on='Module', how='left')
    category_summary['Percentage'] = (category_summary['Sample Count'] / category_summary['Total Volume']) * 100

    st.subheader("Category Summary")
    st.dataframe(category_summary)

    user_summary = df_sampled.groupby('User Profile').size().reset_index(name='Sample Count')
    total_volume_by_user = df.groupby('User Profile').size().reset_index(name='Total Volume')
    user_summary = user_summary.merge(total_volume_by_user, on='User Profile', how='left')
    user_summary['Percentage'] = (user_summary['Sample Count'] / user_summary['Total Volume']) * 100

    st.subheader("User Profile Summary")
    st.dataframe(user_summary)

    # Download sampled data
    st.download_button(
        label="Download Sampled Data",
        data=df_sampled.to_csv(index=False),
        file_name="sampled_data.csv",
        mime="text/csv"
    )
