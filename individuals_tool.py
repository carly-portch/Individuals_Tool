import streamlit as st
from datetime import datetime

# Function to calculate age
def calculate_age(birthday):
    today = datetime.today()
    birthdate = datetime.strptime(birthday, "%Y-%m-%d")
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Function to calculate future value with compound interest
def calculate_future_value(principal, rate, time, frequency, contribution):
    if frequency == "Monthly":
        n = 12
    elif frequency == "Bi-weekly":
        n = 26
    elif frequency == "Weekly":
        n = 52
    else:
        n = 1  # Assume annual for any other input

    # Calculate the future value using the compound interest formula
    future_value = principal * (1 + rate / (n * 100)) ** (n * time)

    # Calculate future contributions
    total_contributions = contribution * n * time
    future_value += total_contributions

    return future_value

# Function to visualize buckets
def visualize_buckets(responses):
    st.header("Your Financial Dashboard")
    
    contributions = {}
    for account in responses['accounts']:
        account_name, account_type, interest_rate, principal, contribution = account
        contributions[account_name] = {
            "Principal": principal,
            "Interest Rate": interest_rate,
            "Monthly Contribution": contribution,
            "Future Value (2055)": calculate_future_value(principal, interest_rate, 32, "Monthly", contribution)  # 32 years to 2055
        }
        
    for account, data in contributions.items():
        st.subheader(account)
        st.write(f"**Account Type:** {account_type}")
        st.write(f"**Current Amount:** ${data['Principal']:.2f}")
        st.write(f"**Monthly Contribution:** ${data['Monthly Contribution']:.2f}")
        st.write(f"**Estimated Amount in 2055:** ${data['Future Value (2055)']:.2f}")
        st.markdown("---")

# Main function
def main():
    st.title("Financial Planning App")
    
    # Initialize session state for accounts
    if 'accounts' not in st.session_state:
        st.session_state.accounts = []
    
    # Collect user responses
    responses = {
        'birthday': st.date_input("When is your birthday?"),
        'occupation_status': st.selectbox("Current occupation status:", 
                                           ["Unemployed", "Student", "Employed", "Maternity/Paternity Leave"]),
        'accounts': st.session_state.accounts
    }
    
    # Calculate age
    if responses['birthday']:
        age = calculate_age(responses['birthday'].strftime("%Y-%m-%d"))
        st.write(f"You are {age} years old.")
    
    # Add accounts
    st.header("Add Your Bank Accounts")
    
    while True:
        account_name = st.text_input("Account Name (e.g., Chequing, HYSA, etc.)")
        account_type = st.selectbox("Account Type (e.g., HYSA, Regular Savings, etc.)", 
                                     ["HYSA", "Regular Savings", "Invested", "Registered"])
        interest_rate = st.number_input("Interest Rate (%)")
        principal = st.number_input("Current Amount in Account ($)")
        contribution = st.number_input("Monthly Contribution Amount ($)")

        if st.button("Add Account"):
            st.session_state.accounts.append((account_name, account_type, interest_rate, principal, contribution))
            st.experimental_rerun()
        
        if st.session_state.accounts:
            responses['accounts'] = st.session_state.accounts

    # Show dashboard after accounts are added
    if st.button("Show Dashboard"):
        show_dashboard(responses)

# Show the dashboard
def show_dashboard(responses):
    visualize_buckets(responses)

# Run the app
if __name__ == "__main__":
    main()
