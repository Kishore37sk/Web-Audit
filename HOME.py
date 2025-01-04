import streamlit as st

# Main page configuration
st.set_page_config(page_title="Audit Dashboard", page_icon="📋", layout="wide")

st.title("Audit Dashboard")
st.write("Welcome to the audit dashboard. Use the navigation menu to access different audits.")



# Custom Header with CSS
st.markdown("""
    <style>
        .header {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header .logo {
            font-size: 20px;
            font-weight: bold;
            color: #333333;
            display: flex;
            align-items: center;
        }
        .header .menu {
            display: flex;
            gap: 20px;
        }
        .header .menu a {
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 15px;
            color: #333333;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .header .menu a:hover {
            background-color: #4b87ff;
        }
        .header .menu .contact {
            background-color: #4b87ff;
            color: white;
        }
        .header .menu .contact:hover {
            background-color: #4b87ff;
        }
    </style>
    <div class="header">
        <div class="logo">
            🖥️ Main Menu
        </div>
        <div class="menu">
            <a href="/bau_audit" target="_self">🙋🏻‍♂️ BAU Audit</a>
            <a href="/ml_audit" target="_self">🤖 ML Audit</a>
            <a class="contact" href="mailto:kishorekumar.shanmugasundaram@nielseniq.com" target="_self">📧 Contact</a>
        </div>
    </div>
""", unsafe_allow_html=True)
