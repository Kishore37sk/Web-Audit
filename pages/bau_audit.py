import streamlit as st
import pandas as pd
import math

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
                additional_samples = additional_entries.sample(
                    n=min(len(additional_entries), needed), random_state=42
                )
                df_sampled = pd.concat([df_sampled, additional_samples])
    return df_sampled.drop_duplicates(subset='External Code').reset_index(drop=True)

# Streamlit App
st.title("OMNI Audit Sampling Tool")

# Sidebar parameters
st.sidebar.header("Sampling Parameters")
priority_percentage = st.sidebar.text_input("Priority Module Percentage", value="40")
user_percentage = st.sidebar.text_input("User Profile Percentage", value="20")
min_samples = st.sidebar.text_input("Minimum Samples per User", value="50")

# User Profile Selection
set_option = st.sidebar.radio("Select User Profile Set", options=["Shopper", "SOS", "Both"])

if set_option == "Shopper":
    user_profiles = [
        "LAVANYA PALANISAMY - US CROSS/CHAR CODER","KIRUTHIGA M - US CROSS/CHAR CODER","HARIHARAN M - US CROSS/CHAR CODER","AKASH C - US CROSS/CHAR CODER","JAGAN S - US CROSS/CHAR CODER","RAMITHA PR - US CROSS/CHAR CODER & LDC","MADHU MATHI - US CROSS/CHAR CODER","SUSHMITHA S - US CROSS/CHAR CODER","POOJA U - US CROSS/CHAR CODER","KISHORERAJ S - US CROSS/CHAR CODER","SHAROMI J - US CROSS/CHAR CODER","THILAGAVATHI MANI - US CROSS/CHAR CODER","SAJITH S - US CROSS/CHAR CODER","SHARANIMANJU D - US CROSS/CHAR CODER","RESHMA SATHIAN - US CROSS/CHAR CODER","JEEVITHA P - US CROSS/CHAR CODER","KHAJA SAIFULLAH - US CROSS/CHAR CODER","AISHWARYA SRINIVASAN - US CROSS/CHAR CODER","ASHIKA V - US CROSS/CHAR CODER & LDC","SUSHMITHA THAMBURAJ - US CROSS/CHAR CODER","SANJAY B - US CROSS/CHAR CODER","ETHESH K - US CROSS/CHAR CODER","BALA KRISHNA - US CROSS/CHAR CODER","UDAYASREE K - US CROSS/CHAR CODER","MARINA JOSEPH - US CROSS/CHAR CODER","HELEN MARTINA - US CROSS/CHAR CODER","ANANDA KRISHNAN - US CROSS/CHAR CODER","KANDHAVEL NAGARAJAN - US CROSS/CHAR CODER","MARIA BAMBINA - US CROSS/CHAR CODER","KANNEPALLI HEMANTHKUMAR - US CROSS/CHAR CODER","MADHUMITHA S - US CROSS/CHAR CODER","SHAIKABDUL ABDULHAFEEZ - US CROSS/CHAR CODER","RISHI RISHI - US CROSS/CHAR CODER","SUSMITHA PETERRAJ - US CROSS/CHAR CODER","HARINI S - US CROSS/CHAR CODER","MANIGANDA RAJA - US CROSS/CHAR CODER","DIVYA B - US CROSS/CHAR CODER","LAVANYA MURALIDHARAN - US LDC & CROSS/CHAR CODER","AVANTHIKAA S - US CROSS/CHAR CODER","LAVANYA MUMMADISETTI - US CROSS/CHAR CODER","SUVETHA G - US CROSS/CHAR CODER","SANJAY S - US CROSS/CHAR CODER","ANGELINJOICE S - US CROSS/CHAR CODER","AMAL P - US CROSS/CHAR CODER","NIKIL R - US CROSS/CHAR CODER","NITHILA G - US CROSS/CHAR CODER","SOWMIYA AG - US CROSS/CHAR CODER","AVINEESH RAJA - US CROSS/CHAR CODER","SYEDTHAQIURRAHMAN S - US CROSS/CHAR CODER","GOWRI N - US CROSS/CHAR CODER & LDC","MADHUVANTHI C - US CROSS/CHAR CODER & LDC","RAJALINGAM T - US CROSS/CHAR CODER","SOWMYA R - US CROSS/CHAR CODER","ADARSH M - US CROSS/CHAR CODER","KARTHIKEYAN H - US CROSS/CHAR CODER","HARIPRIYA NATARAJAN - US CROSS/CHAR CODER","PRAVEENKUMAR V - US CROSS/CHAR CODER","SUVEATHA J - US CROSS/CHAR CODER","SARASWATHY K - US CROSS/CHAR CODER","NANDHIKA P - US CROSS/CHAR CODER","JAYA PRAKASH - US CROSS/CHAR CODER","GURUPRASATH J - US CROSS/CHAR CODER","SUBRAMANIAN S - US CROSS/CHAR CODER","SATISH KUMAR - US LDC & CROSS/CHAR CODER","SUBIKSHA AYYAPPAN - US CROSS/CHAR CODER","DHEJASWINI PA - US CROSS/CHAR CODER","SARAN S - US CROSS/CHAR CODER & LDC","ARTHI R - US CROSS/CHAR CODER","NARMADHA RATHINASAMY - US CROSS/CHAR CODER","AKSHAYA SIVAKUMAR - US CROSS/CHAR CODER","MADHUMITHA RAMADOSS - US CROSS/CHAR CODER & LDC","KEERTHANA D - US CROSS/CHAR CODER","GUNTUR PAVAN RAM GANESH - US CROSS/CHAR CODER","AROKIA KAVITHA - US CROSS/CHAR CODER","KAARTHIC RAMASWAMI - US CROSS/CHAR CODER","KOWSALYA S - US CROSS/CHAR CODER","ANUSHYA G - US CROSS/CHAR CODER","RANJITH V - US CROSS/CHAR CODER","MRUDUL CU - US CROSS/CHAR CODER","RASMITHA GURRAM - US CROSS/CHAR CODER & LDC","HEMANADAN R - US CROSS/CHAR CODER","DESIYAA SUJATHA - US CROSS/CHAR CODER","LAVANYA JOTHI - US CROSS/CHAR CODER","KISHOREKUMAR SHANMUGASUNDARAM - US CROSS/CHAR CODER","AKASH B - US CROSS/CHAR CODER","MUKESHRAMGANESH K - US CROSS/CHAR CODER","RAM PRASATP - US CROSS/CHAR CODER","ISWARYA BABU - US CROSS/CHAR CODER","VARUN PRASATHK - US CROSS/CHAR CODER","VISHNU PRADAPHG - US CROSS/CHAR CODER","LAVANYA KANNA - US CROSS/CHAR CODER","VINODHINI D - US CROSS/CHAR CODER","SABEER I - US CROSS/CHAR CODER","JAYANTH PANCHETI - US CROSS/CHAR CODER","LAKSHMI K - US CROSS/CHAR CODER","SARAVANAN PADMANABHAN - US CROSS/CHAR CODER","CONSTELLACELESTINE JOACHIM - US CROSS/CHAR CODER","KAUSHIK S - US CROSS/CHAR CODER","ANTONYALBERT J - US LDC & CROSS/CHAR CODER","JANANI CHELLAPPAN - US CROSS/CHAR CODER","AISHWINTH G - US CROSS/CHAR CODER","SIVARAJ TIRISHA - US CROSS/CHAR CODER","KANISHKA M - US CROSS/CHAR CODER","INDHUNITHI P - US LDC & CROSS/CHAR CODER","BRINDHA M - US CROSS/CHAR CODER","TAMIZH SELVAN - US CROSS/CHAR CODER","NIRUBA PARAMANANTHAM - US CROSS/CHAR CODER","BHUVANESHWARI K - US CROSS/CHAR CODER","MOHAMMED AASIMBG - US CROSS/CHAR CODER","ADNAN AATIF - US CROSS/CHAR CODER","ABIRAMI P - US CROSS/CHAR CODER","POORNAVALLI M - US CROSS/CHAR CODER","GOPINATH A - US CROSS/CHAR CODER","JAGADISH N - US CROSS/CHAR CODER & LDC","SHRIVARUN THIRUPPATHYRAJ - US CROSS/CHAR CODER & LDC","MANONMANI M - US CROSS/CHAR CODER & LDC","SALONI SHAH - US CROSS/CHAR CODER","SURENDER SURESHKUMAR - US CROSS/CHAR CODER","RACHANA SURESH - US CROSS/CHAR CODER","SOWNDARYA U - US CROSS/CHAR CODER","PRITHVI D - US CROSS/CHAR CODER","SRINIVASAN ANNAMALAI - US CROSS/CHAR CODER","MONIKA NATARAJAN - US CROSS/CHAR CODER","NIVETHITHA GB - US CROSS/CHAR CODER","VENKATRAMAKRISHNAN S - US CROSS/CHAR CODER","VISHAL VV - US CROSS/CHAR CODER","PRITHIKA M - US CROSS/CHAR CODER","MOHANASRI CHANDAR - US CROSS/CHAR CODER","PAVITHRA X N - US CROSS/CHAR CODER","PRASANNA BYALLA - US CROSS/CHAR CODER","DHARSINI R - US CROSS/CHAR CODER","KESAVAKAUSHIK N - US CROSS/CHAR CODER","POOJA DHANARAJ - US CROSS/CHAR CODER","SHRINIVASU D - US CROSS/CHAR CODER","SUMIT KUMARSHARMA - US CROSS/CHAR CODER","DINESH RAJ - US CROSS/CHAR CODER","SWETA CHOUDHARY - US CROSS/CHAR CODER","PRASHAMSCHANDRA PENDYALA - US CROSS/CHAR CODER","RAAJ DHANUSH - US CROSS/CHAR CODER","SARANYA MANIVANNAN - US CROSS/CHAR CODER","ROSHINITRISHABABU KS - US CROSS/CHAR CODER"
    ]
elif set_option == "SOS":
    user_profiles = [
        "BALAMURUGAN G - US CROSS/CHAR CODER","SHAKTHI SHREEM - US CROSS/CHAR CODER","YASHNI SHREE - US CROSS/CHAR CODER","SOWMIYA K - US CROSS/CHAR CODER","KEERTHANA RAJASEKAR - US CROSS/CHAR CODER","PRAVEEN KUMAR - US CROSS/CHAR CODER","VISHALI B - US CROSS/CHAR CODER","DHARSHINI V - US CROSS/CHAR CODER","KISHOREKUMAR S - US CROSS/CHAR CODER","PRAJESH V - US CROSS/CHAR CODER","RETHINAGIRI G - US CROSS/CHAR CODER","SYED SAMEER - US CROSS/CHAR CODER","BHAVADHARANI KUPPAN - US CROSS/CHAR CODER","KUMUDHA B - US CROSS/CHAR CODER","KAVYA R - US CROSS/CHAR CODER","NIRANJANA T - US CROSS/CHAR CODER","DEEPTHI S - US CROSS/CHAR CODER","PRAJODHAY J - US CROSS/CHAR CODER","AMARK PUNEET - US CROSS/CHAR CODER","RAJADURAI KANAKARAJ - US CROSS/CHAR CODER","NADIA SALIM - US LDC & CROSS/CHAR CODER","SARULATHA THAMARAIKANNAN - US CROSS/CHAR CODER","ABITHA P - US CROSS/CHAR CODER","KARISHNIKA T - US CROSS/CHAR CODER","SOWMIYA S - US CROSS/CHAR CODER","KARTHICK A - US CROSS/CHAR CODER","SASIDHARAN S - US CROSS/CHAR CODER","SHALINI M - US CROSS/CHAR CODER","PUNITHA T - US CROSS/CHAR CODER & LDC","MYTHILY S - US CROSS/CHAR CODER","YOGAPRIYA B - US CROSS/CHAR CODER","SHARMILADEVI S - US CROSS/CHAR CODER","SARANYA KL - US CROSS/CHAR CODER","BHUVANESHWARI V - US CROSS/CHAR CODER","LAKSHMI RADHAKRISHNAN - US CROSS/CHAR CODER","PARKAVI R - US CROSS/CHAR CODER","PRASHANTH K - US LDC & CROSS/CHAR CODER","HEMA DARSHINI - US CROSS/CHAR CODER","P SATHYAMURTHY - US CROSS/CHAR CODER","HAARDIK H - US CROSS/CHAR CODER","HARISMITHA K - US CROSS/CHAR CODER","AKASH X SINGH - US CROSS/CHAR CODER","BHARATH TP - US CROSS/CHAR CODER","DIVYABHARATHI B - US CROSS/CHAR CODER","BHARATHY G - US CROSS/CHAR CODER","RAMASWAMY IYER - US CROSS/CHAR CODER","NAVYA M - US CROSS/CHAR CODER","PRAVEEN S - US CROSS/CHAR CODER","ARUL THOMAS - US CROSS/CHAR CODER","BALAJE BABU - US CROSS/CHAR CODER","RAMYA S - US CROSS/CHAR CODER","SWATHI K - US CROSS/CHAR CODER & LDC","PRANAV SATHISH - US CROSS/CHAR CODER & LDC","LIKITH BODAGALA - US CROSS/CHAR CODER","SWETHA SEKAR - US CROSS/CHAR CODER","KARTHIK HARIHARAN - US CROSS/CHAR CODER","MOHAN SUNDARARAJ - US CROSS/CHAR CODER","RAWOOF SHAH - US CROSS/CHAR CODER","PANIGATLA SAIKUMAR - US CROSS/CHAR CODER","BHANU PRASAD - US CROSS/CHAR CODER","SNEHA M - US CROSS/CHAR CODER","AMIRTHA V - US CROSS/CHAR CODER","RAHULKRISHNA M - US CROSS/CHAR CODER","SRIMATHI PARIMELAZHAGAN - US CROSS/CHAR CODER","KARTHICK P - US CROSS/CHAR CODER","LIKHITHA PADMANABHAN - US CROSS/CHAR CODER","SATHISH.R - US CROSS/CHAR CODER","KRISHNAPRIYA.DAMODHARAN - US CROSS/CHAR CODER","ASUWATHI PONNIVALAVAN - US CROSS/CHAR CODER","PONRAJ J - US CROSS/CHAR CODER & LDC","DEBORAH CHRISTINA - US CROSS/CHAR CODER","PRABHU VENKAT - US CROSS/CHAR CODER","SOUNDARIYA DEVARAJ - US CROSS/CHAR CODER","LAKSHMI NANDAKUMAR - US CROSS/CHAR CODER","DEEPA D - US CROSS/CHAR CODER","KARTHIK RAMU - US CROSS/CHAR CODER","SNEHAPRIYA NANDAKUMAR - US CROSS/CHAR CODER","YUVASRI V - US CROSS/CHAR CODER","TARUNSEKARAN CS - US CROSS/CHAR CODER","SOWMIYA PRABHU - US CROSS/CHAR CODER","PRANEETHA K - US CROSS/CHAR CODER","SOWMYA B - US CROSS/CHAR CODER","JAMUNA KRISHNAMOORTHY - US CROSS/CHAR CODER","KAVYA SATHIAH - US CROSS/CHAR CODER","HARSHINI R - US CROSS/CHAR CODER","RUPA ALAN - US CROSS/CHAR CODER","HARIKRISHNAN SIVARAMAKRISHNAN - US CROSS/CHAR CODER","NITHYASRI RAMESH - US CROSS/CHAR CODER","HARITHA ISHWARYA - US CROSS/CHAR CODER","SUDHARSAN L - US CROSS/CHAR CODER","HARSHAVARDHAN EN - US CROSS/CHAR CODER","SHANKHARSHNA B - US CROSS/CHAR CODER","GAYATHRI KALIDHASAN - US CROSS/CHAR CODER","ARIHARAPERUMAL V - US CROSS/CHAR CODER & LDC","SHEIK IQBALZ - US CROSS/CHAR CODER & LDC","MANI C - US CROSS/CHAR CODER & LDC","AKSHAYA RAI - US CROSS/CHAR CODER & LDC","SUBHASHINI N - US CROSS/CHAR CODER & LDC","RUBESH K - US CROSS/CHAR CODER","B BAHEERADHAN - US CROSS/CHAR CODER","KOUSIKA VENKATESAN - US CROSS/CHAR CODER","BALADEEPIKA J - US CROSS/CHAR CODER","AARTHI R - US CROSS/CHAR CODER & LDC","JOY JENISHA - US CROSS/CHAR CODER","SANJAY JAYARAMAN - US CROSS/CHAR CODER","POOJA VARSSHINISK - US CROSS/CHAR CODER","JESSY JOVITHA - US CROSS/CHAR CODER","BHARATH P - US CROSS/CHAR CODER","NITHYASRI LAKSHMINARAYANAN - US CROSS/CHAR CODER","DEEPIKA ELANGOVAN - US CROSS/CHAR CODER","SANGEETHA S - US CROSS/CHAR CODER","SNEKA MUTHUKUMARASAMY - US CROSS/CHAR CODER","NITHISH N - US CROSS/CHAR CODER","CYRIL DOSS - US CROSS/CHAR CODER","PRAMOTH R - US CROSS/CHAR CODER","PAVITHRA X S - US CROSS/CHAR CODER","SARAVANAN JAYAVEL - US CROSS/CHAR CODER","KAREEMUNNISSA S - US CROSS/CHAR CODER","PADMASRI GANESAN - US CROSS/CHAR CODER","SARANYA SHANMUGAVEL - US CROSS/CHAR CODER","KRITHICK S - US CROSS/CHAR CODER","SARASWATHI A - US CROSS/CHAR CODER","RESHMA R - US CROSS/CHAR CODER","JEEVITHA RAJA - US CROSS/CHAR CODER","TEJASWINI V - US CROSS/CHAR CODER","KOUSALYA T - US CROSS/CHAR CODER","JAYASRI R - US CROSS/CHAR CODER","VASANTHARAJA M - US CROSS/CHAR CODER","PREM SEETHALCHAND - US CROSS/CHAR CODER","SHALINI L - US CROSS/CHAR CODER & LDC","DARSHAN HARIHARAN - US CROSS/CHAR CODER","KEERTHI MADDIREDDY - US CROSS/CHAR CODER","SHANTHINI PITCHAIAH - US CROSS/CHAR CODER","VISHWA E - US CROSS/CHAR CODER","HARIPRASAD RAMACHANDRAN - US CROSS/CHAR CODER","PREETHA JAYASANKARAN - US CROSS/CHAR CODER","SHARATH RAM - US CROSS/CHAR CODER","GANESHRAAM R - US CROSS/CHAR CODER","DEEPIKA MOHAN - US CROSS/CHAR CODER","SUGANYA SURENDRAN - US CROSS/CHAR CODER","MEGHANA M - US CROSS/CHAR CODER","SANTHA JOHN - US CROSS/CHAR CODER","SRIGOWRISANGAVI M - US CROSS/CHAR CODER","KAAVIYA U - US CROSS/CHAR CODER","SARANYA RAMANATHAN - US CROSS/CHAR CODER","SHESHADIRI PADMANABHAN - US CROSS/CHAR CODER","DEEPA X D - US CROSS/CHAR CODER","PRATHIMA TG - US CROSS/CHAR CODER","MEREEN JOANN BROWNE - US CROSS/CHAR CODER","GOPALAKRISHNAN RAMASAMY - US CROSS/CHAR CODER","SONIYA N - US CROSS/CHAR CODER","VIKRAM MANOHARAN - US CROSS/CHAR CODER","KAVIYA G - US CROSS/CHAR CODER","POOJA K - US CROSS/CHAR CODER","DIVYA BHARATHI - US CROSS/CHAR CODER","THULASI VARADHARAJAN - US CROSS/CHAR CODER","DHARSHINI R - US CROSS/CHAR CODER","AGASTHIYA D - US CROSS/CHAR CODER","CAROLINE RAJ - US CROSS/CHAR CODER","VAISHNAVI K - US CROSS/CHAR CODER","NIVEDHA R - US CROSS/CHAR CODER","MAHALAKSHMI SATHYANARAYANAN - US CROSS/CHAR CODER & LDC","MAHIMAVARSHNI S - US CROSS/CHAR CODER & LDC","MEENATCHI.SUNDARAM - US CROSS/CHAR CODER","SARATHKUMAR.P - US CROSS/CHAR CODER","SOUMIYA R - US CROSS/CHAR CODER"
    ]
elif set_option == "Both":
    user_profiles = [
        "LAVANYA PALANISAMY - US CROSS/CHAR CODER","KIRUTHIGA M - US CROSS/CHAR CODER","HARIHARAN M - US CROSS/CHAR CODER","AKASH C - US CROSS/CHAR CODER","JAGAN S - US CROSS/CHAR CODER","RAMITHA PR - US CROSS/CHAR CODER & LDC","MADHU MATHI - US CROSS/CHAR CODER","SUSHMITHA S - US CROSS/CHAR CODER","POOJA U - US CROSS/CHAR CODER","KISHORERAJ S - US CROSS/CHAR CODER","SHAROMI J - US CROSS/CHAR CODER","THILAGAVATHI MANI - US CROSS/CHAR CODER","SAJITH S - US CROSS/CHAR CODER","SHARANIMANJU D - US CROSS/CHAR CODER","RESHMA SATHIAN - US CROSS/CHAR CODER","JEEVITHA P - US CROSS/CHAR CODER","KHAJA SAIFULLAH - US CROSS/CHAR CODER","AISHWARYA SRINIVASAN - US CROSS/CHAR CODER","ASHIKA V - US CROSS/CHAR CODER & LDC","SUSHMITHA THAMBURAJ - US CROSS/CHAR CODER","SANJAY B - US CROSS/CHAR CODER","ETHESH K - US CROSS/CHAR CODER","BALA KRISHNA - US CROSS/CHAR CODER","UDAYASREE K - US CROSS/CHAR CODER","MARINA JOSEPH - US CROSS/CHAR CODER","HELEN MARTINA - US CROSS/CHAR CODER","ANANDA KRISHNAN - US CROSS/CHAR CODER","KANDHAVEL NAGARAJAN - US CROSS/CHAR CODER","MARIA BAMBINA - US CROSS/CHAR CODER","KANNEPALLI HEMANTHKUMAR - US CROSS/CHAR CODER","MADHUMITHA S - US CROSS/CHAR CODER","SHAIKABDUL ABDULHAFEEZ - US CROSS/CHAR CODER","RISHI RISHI - US CROSS/CHAR CODER","SUSMITHA PETERRAJ - US CROSS/CHAR CODER","HARINI S - US CROSS/CHAR CODER","MANIGANDA RAJA - US CROSS/CHAR CODER","DIVYA B - US CROSS/CHAR CODER","LAVANYA MURALIDHARAN - US LDC & CROSS/CHAR CODER","AVANTHIKAA S - US CROSS/CHAR CODER","LAVANYA MUMMADISETTI - US CROSS/CHAR CODER","SUVETHA G - US CROSS/CHAR CODER","SANJAY S - US CROSS/CHAR CODER","ANGELINJOICE S - US CROSS/CHAR CODER","AMAL P - US CROSS/CHAR CODER","NIKIL R - US CROSS/CHAR CODER","NITHILA G - US CROSS/CHAR CODER","SOWMIYA AG - US CROSS/CHAR CODER","AVINEESH RAJA - US CROSS/CHAR CODER","SYEDTHAQIURRAHMAN S - US CROSS/CHAR CODER","GOWRI N - US CROSS/CHAR CODER & LDC","MADHUVANTHI C - US CROSS/CHAR CODER & LDC","RAJALINGAM T - US CROSS/CHAR CODER","SOWMYA R - US CROSS/CHAR CODER","ADARSH M - US CROSS/CHAR CODER","KARTHIKEYAN H - US CROSS/CHAR CODER","HARIPRIYA NATARAJAN - US CROSS/CHAR CODER","PRAVEENKUMAR V - US CROSS/CHAR CODER","SUVEATHA J - US CROSS/CHAR CODER","SARASWATHY K - US CROSS/CHAR CODER","NANDHIKA P - US CROSS/CHAR CODER","JAYA PRAKASH - US CROSS/CHAR CODER","GURUPRASATH J - US CROSS/CHAR CODER","SUBRAMANIAN S - US CROSS/CHAR CODER","SATISH KUMAR - US LDC & CROSS/CHAR CODER","SUBIKSHA AYYAPPAN - US CROSS/CHAR CODER","DHEJASWINI PA - US CROSS/CHAR CODER","SARAN S - US CROSS/CHAR CODER & LDC","ARTHI R - US CROSS/CHAR CODER","NARMADHA RATHINASAMY - US CROSS/CHAR CODER","AKSHAYA SIVAKUMAR - US CROSS/CHAR CODER","MADHUMITHA RAMADOSS - US CROSS/CHAR CODER & LDC","KEERTHANA D - US CROSS/CHAR CODER","GUNTUR PAVAN RAM GANESH - US CROSS/CHAR CODER","AROKIA KAVITHA - US CROSS/CHAR CODER","KAARTHIC RAMASWAMI - US CROSS/CHAR CODER","KOWSALYA S - US CROSS/CHAR CODER","ANUSHYA G - US CROSS/CHAR CODER","RANJITH V - US CROSS/CHAR CODER","MRUDUL CU - US CROSS/CHAR CODER","RASMITHA GURRAM - US CROSS/CHAR CODER & LDC","HEMANADAN R - US CROSS/CHAR CODER","DESIYAA SUJATHA - US CROSS/CHAR CODER","LAVANYA JOTHI - US CROSS/CHAR CODER","KISHOREKUMAR SHANMUGASUNDARAM - US CROSS/CHAR CODER","AKASH B - US CROSS/CHAR CODER","MUKESHRAMGANESH K - US CROSS/CHAR CODER","RAM PRASATP - US CROSS/CHAR CODER","ISWARYA BABU - US CROSS/CHAR CODER","VARUN PRASATHK - US CROSS/CHAR CODER","VISHNU PRADAPHG - US CROSS/CHAR CODER","LAVANYA KANNA - US CROSS/CHAR CODER","VINODHINI D - US CROSS/CHAR CODER","SABEER I - US CROSS/CHAR CODER","JAYANTH PANCHETI - US CROSS/CHAR CODER","LAKSHMI K - US CROSS/CHAR CODER","SARAVANAN PADMANABHAN - US CROSS/CHAR CODER","CONSTELLACELESTINE JOACHIM - US CROSS/CHAR CODER","KAUSHIK S - US CROSS/CHAR CODER","ANTONYALBERT J - US LDC & CROSS/CHAR CODER","JANANI CHELLAPPAN - US CROSS/CHAR CODER","AISHWINTH G - US CROSS/CHAR CODER","SIVARAJ TIRISHA - US CROSS/CHAR CODER","KANISHKA M - US CROSS/CHAR CODER","INDHUNITHI P - US LDC & CROSS/CHAR CODER","BRINDHA M - US CROSS/CHAR CODER","TAMIZH SELVAN - US CROSS/CHAR CODER","NIRUBA PARAMANANTHAM - US CROSS/CHAR CODER","BHUVANESHWARI K - US CROSS/CHAR CODER","MOHAMMED AASIMBG - US CROSS/CHAR CODER","ADNAN AATIF - US CROSS/CHAR CODER","ABIRAMI P - US CROSS/CHAR CODER","POORNAVALLI M - US CROSS/CHAR CODER","GOPINATH A - US CROSS/CHAR CODER","JAGADISH N - US CROSS/CHAR CODER & LDC","SHRIVARUN THIRUPPATHYRAJ - US CROSS/CHAR CODER & LDC","MANONMANI M - US CROSS/CHAR CODER & LDC","SALONI SHAH - US CROSS/CHAR CODER","SURENDER SURESHKUMAR - US CROSS/CHAR CODER","RACHANA SURESH - US CROSS/CHAR CODER","SOWNDARYA U - US CROSS/CHAR CODER","PRITHVI D - US CROSS/CHAR CODER","SRINIVASAN ANNAMALAI - US CROSS/CHAR CODER","MONIKA NATARAJAN - US CROSS/CHAR CODER","NIVETHITHA GB - US CROSS/CHAR CODER","VENKATRAMAKRISHNAN S - US CROSS/CHAR CODER","VISHAL VV - US CROSS/CHAR CODER","PRITHIKA M - US CROSS/CHAR CODER","MOHANASRI CHANDAR - US CROSS/CHAR CODER","PAVITHRA X N - US CROSS/CHAR CODER","PRASANNA BYALLA - US CROSS/CHAR CODER","DHARSINI R - US CROSS/CHAR CODER","KESAVAKAUSHIK N - US CROSS/CHAR CODER","POOJA DHANARAJ - US CROSS/CHAR CODER","SHRINIVASU D - US CROSS/CHAR CODER","SUMIT KUMARSHARMA - US CROSS/CHAR CODER","DINESH RAJ - US CROSS/CHAR CODER","SWETA CHOUDHARY - US CROSS/CHAR CODER","PRASHAMSCHANDRA PENDYALA - US CROSS/CHAR CODER","RAAJ DHANUSH - US CROSS/CHAR CODER","SARANYA MANIVANNAN - US CROSS/CHAR CODER","ROSHINITRISHABABU KS - US CROSS/CHAR CODER", "BALAMURUGAN G - US CROSS/CHAR CODER","SHAKTHI SHREEM - US CROSS/CHAR CODER","YASHNI SHREE - US CROSS/CHAR CODER","SOWMIYA K - US CROSS/CHAR CODER","KEERTHANA RAJASEKAR - US CROSS/CHAR CODER","PRAVEEN KUMAR - US CROSS/CHAR CODER","VISHALI B - US CROSS/CHAR CODER","DHARSHINI V - US CROSS/CHAR CODER","KISHOREKUMAR S - US CROSS/CHAR CODER","PRAJESH V - US CROSS/CHAR CODER","RETHINAGIRI G - US CROSS/CHAR CODER","SYED SAMEER - US CROSS/CHAR CODER","BHAVADHARANI KUPPAN - US CROSS/CHAR CODER","KUMUDHA B - US CROSS/CHAR CODER","KAVYA R - US CROSS/CHAR CODER","NIRANJANA T - US CROSS/CHAR CODER","DEEPTHI S - US CROSS/CHAR CODER","PRAJODHAY J - US CROSS/CHAR CODER","AMARK PUNEET - US CROSS/CHAR CODER","RAJADURAI KANAKARAJ - US CROSS/CHAR CODER","NADIA SALIM - US LDC & CROSS/CHAR CODER","SARULATHA THAMARAIKANNAN - US CROSS/CHAR CODER","ABITHA P - US CROSS/CHAR CODER","KARISHNIKA T - US CROSS/CHAR CODER","SOWMIYA S - US CROSS/CHAR CODER","KARTHICK A - US CROSS/CHAR CODER","SASIDHARAN S - US CROSS/CHAR CODER","SHALINI M - US CROSS/CHAR CODER","PUNITHA T - US CROSS/CHAR CODER & LDC","MYTHILY S - US CROSS/CHAR CODER","YOGAPRIYA B - US CROSS/CHAR CODER","SHARMILADEVI S - US CROSS/CHAR CODER","SARANYA KL - US CROSS/CHAR CODER","BHUVANESHWARI V - US CROSS/CHAR CODER","LAKSHMI RADHAKRISHNAN - US CROSS/CHAR CODER","PARKAVI R - US CROSS/CHAR CODER","PRASHANTH K - US LDC & CROSS/CHAR CODER","HEMA DARSHINI - US CROSS/CHAR CODER","P SATHYAMURTHY - US CROSS/CHAR CODER","HAARDIK H - US CROSS/CHAR CODER","HARISMITHA K - US CROSS/CHAR CODER","AKASH X SINGH - US CROSS/CHAR CODER","BHARATH TP - US CROSS/CHAR CODER","DIVYABHARATHI B - US CROSS/CHAR CODER","BHARATHY G - US CROSS/CHAR CODER","RAMASWAMY IYER - US CROSS/CHAR CODER","NAVYA M - US CROSS/CHAR CODER","PRAVEEN S - US CROSS/CHAR CODER","ARUL THOMAS - US CROSS/CHAR CODER","BALAJE BABU - US CROSS/CHAR CODER","RAMYA S - US CROSS/CHAR CODER","SWATHI K - US CROSS/CHAR CODER & LDC","PRANAV SATHISH - US CROSS/CHAR CODER & LDC","LIKITH BODAGALA - US CROSS/CHAR CODER","SWETHA SEKAR - US CROSS/CHAR CODER","KARTHIK HARIHARAN - US CROSS/CHAR CODER","MOHAN SUNDARARAJ - US CROSS/CHAR CODER","RAWOOF SHAH - US CROSS/CHAR CODER","PANIGATLA SAIKUMAR - US CROSS/CHAR CODER","BHANU PRASAD - US CROSS/CHAR CODER","SNEHA M - US CROSS/CHAR CODER","AMIRTHA V - US CROSS/CHAR CODER","RAHULKRISHNA M - US CROSS/CHAR CODER","SRIMATHI PARIMELAZHAGAN - US CROSS/CHAR CODER","KARTHICK P - US CROSS/CHAR CODER","LIKHITHA PADMANABHAN - US CROSS/CHAR CODER","SATHISH.R - US CROSS/CHAR CODER","KRISHNAPRIYA.DAMODHARAN - US CROSS/CHAR CODER","ASUWATHI PONNIVALAVAN - US CROSS/CHAR CODER","PONRAJ J - US CROSS/CHAR CODER & LDC","DEBORAH CHRISTINA - US CROSS/CHAR CODER","PRABHU VENKAT - US CROSS/CHAR CODER","SOUNDARIYA DEVARAJ - US CROSS/CHAR CODER","LAKSHMI NANDAKUMAR - US CROSS/CHAR CODER","DEEPA D - US CROSS/CHAR CODER","KARTHIK RAMU - US CROSS/CHAR CODER","SNEHAPRIYA NANDAKUMAR - US CROSS/CHAR CODER","YUVASRI V - US CROSS/CHAR CODER","TARUNSEKARAN CS - US CROSS/CHAR CODER","SOWMIYA PRABHU - US CROSS/CHAR CODER","PRANEETHA K - US CROSS/CHAR CODER","SOWMYA B - US CROSS/CHAR CODER","JAMUNA KRISHNAMOORTHY - US CROSS/CHAR CODER","KAVYA SATHIAH - US CROSS/CHAR CODER","HARSHINI R - US CROSS/CHAR CODER","RUPA ALAN - US CROSS/CHAR CODER","HARIKRISHNAN SIVARAMAKRISHNAN - US CROSS/CHAR CODER","NITHYASRI RAMESH - US CROSS/CHAR CODER","HARITHA ISHWARYA - US CROSS/CHAR CODER","SUDHARSAN L - US CROSS/CHAR CODER","HARSHAVARDHAN EN - US CROSS/CHAR CODER","SHANKHARSHNA B - US CROSS/CHAR CODER","GAYATHRI KALIDHASAN - US CROSS/CHAR CODER","ARIHARAPERUMAL V - US CROSS/CHAR CODER & LDC","SHEIK IQBALZ - US CROSS/CHAR CODER & LDC","MANI C - US CROSS/CHAR CODER & LDC","AKSHAYA RAI - US CROSS/CHAR CODER & LDC","SUBHASHINI N - US CROSS/CHAR CODER & LDC","RUBESH K - US CROSS/CHAR CODER","B BAHEERADHAN - US CROSS/CHAR CODER","KOUSIKA VENKATESAN - US CROSS/CHAR CODER","BALADEEPIKA J - US CROSS/CHAR CODER","AARTHI R - US CROSS/CHAR CODER & LDC","JOY JENISHA - US CROSS/CHAR CODER","SANJAY JAYARAMAN - US CROSS/CHAR CODER","POOJA VARSSHINISK - US CROSS/CHAR CODER","JESSY JOVITHA - US CROSS/CHAR CODER","BHARATH P - US CROSS/CHAR CODER","NITHYASRI LAKSHMINARAYANAN - US CROSS/CHAR CODER","DEEPIKA ELANGOVAN - US CROSS/CHAR CODER","SANGEETHA S - US CROSS/CHAR CODER","SNEKA MUTHUKUMARASAMY - US CROSS/CHAR CODER","NITHISH N - US CROSS/CHAR CODER","CYRIL DOSS - US CROSS/CHAR CODER","PRAMOTH R - US CROSS/CHAR CODER","PAVITHRA X S - US CROSS/CHAR CODER","SARAVANAN JAYAVEL - US CROSS/CHAR CODER","KAREEMUNNISSA S - US CROSS/CHAR CODER","PADMASRI GANESAN - US CROSS/CHAR CODER","SARANYA SHANMUGAVEL - US CROSS/CHAR CODER","KRITHICK S - US CROSS/CHAR CODER","SARASWATHI A - US CROSS/CHAR CODER","RESHMA R - US CROSS/CHAR CODER","JEEVITHA RAJA - US CROSS/CHAR CODER","TEJASWINI V - US CROSS/CHAR CODER","KOUSALYA T - US CROSS/CHAR CODER","JAYASRI R - US CROSS/CHAR CODER","VASANTHARAJA M - US CROSS/CHAR CODER","PREM SEETHALCHAND - US CROSS/CHAR CODER","SHALINI L - US CROSS/CHAR CODER & LDC","DARSHAN HARIHARAN - US CROSS/CHAR CODER","KEERTHI MADDIREDDY - US CROSS/CHAR CODER","SHANTHINI PITCHAIAH - US CROSS/CHAR CODER","VISHWA E - US CROSS/CHAR CODER","HARIPRASAD RAMACHANDRAN - US CROSS/CHAR CODER","PREETHA JAYASANKARAN - US CROSS/CHAR CODER","SHARATH RAM - US CROSS/CHAR CODER","GANESHRAAM R - US CROSS/CHAR CODER","DEEPIKA MOHAN - US CROSS/CHAR CODER","SUGANYA SURENDRAN - US CROSS/CHAR CODER","MEGHANA M - US CROSS/CHAR CODER","SANTHA JOHN - US CROSS/CHAR CODER","SRIGOWRISANGAVI M - US CROSS/CHAR CODER","KAAVIYA U - US CROSS/CHAR CODER","SARANYA RAMANATHAN - US CROSS/CHAR CODER","SHESHADIRI PADMANABHAN - US CROSS/CHAR CODER","DEEPA X D - US CROSS/CHAR CODER","PRATHIMA TG - US CROSS/CHAR CODER","MEREEN JOANN BROWNE - US CROSS/CHAR CODER","GOPALAKRISHNAN RAMASAMY - US CROSS/CHAR CODER","SONIYA N - US CROSS/CHAR CODER","VIKRAM MANOHARAN - US CROSS/CHAR CODER","KAVIYA G - US CROSS/CHAR CODER","POOJA K - US CROSS/CHAR CODER","DIVYA BHARATHI - US CROSS/CHAR CODER","THULASI VARADHARAJAN - US CROSS/CHAR CODER","DHARSHINI R - US CROSS/CHAR CODER","AGASTHIYA D - US CROSS/CHAR CODER","CAROLINE RAJ - US CROSS/CHAR CODER","VAISHNAVI K - US CROSS/CHAR CODER","NIVEDHA R - US CROSS/CHAR CODER","MAHALAKSHMI SATHYANARAYANAN - US CROSS/CHAR CODER & LDC","MAHIMAVARSHNI S - US CROSS/CHAR CODER & LDC","MEENATCHI.SUNDARAM - US CROSS/CHAR CODER","SARATHKUMAR.P - US CROSS/CHAR CODER","SOUMIYA R - US CROSS/CHAR CODER"
    ]


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
    df = pd.read_csv(uploaded_file)

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
