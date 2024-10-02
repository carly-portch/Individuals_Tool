import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date



# Function to calculate age from birthday
def calculate_age(birthday):
    today = date.today()
    birthdate = pd.to_datetime(birthday)
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Function to calculate future value with monthly contributions
def calculate_future_value(principal, annual_rate, years, monthly_contribution):
    monthly_rate = annual_rate / 100 / 12
    future_value = principal * (1 + monthly_rate) ** (years * 12)
    future_value += monthly_contribution * (((1 + monthly_rate) ** (years * 12) - 1) / monthly_rate)
    return future_value

# Function to visualize income distribution into buckets
def visualize_buckets(responses):
    st.subheader("Income Distribution Visualization")
    if len(responses['accounts']) == 0:
        st.write("No accounts available to distribute income.")
        return

    num_accounts = len(responses['accounts'])
    paycheck = responses['paycheck']

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.arrow(-1.5, 0.5, 1.5, 0, head_width=0.05, head_length=0.1, fc='green', ec='green')
    ax.text(-1.8, 0.5, 'Income', fontsize=12, color='green', ha='center', va='center')

    bucket_names = [acc[0] for acc in responses['accounts']]
    allocations = [responses['allocations'].get(acc[0], 0) for acc in responses['accounts']]

    for i, account in enumerate(bucket_names):
        bucket_height = allocations[i] / paycheck if paycheck > 0 else 0
        bucket_color = 'lightblue' if bucket_height > 0 else 'lightgray'
        ax.add_patch(plt.Rectangle((i, 0.3), 0.5, bucket_height, fill=True, color=bucket_color, edgecolor='black'))
        ax.text(i + 0.25, 0.3 + bucket_height + 0.02, account, fontsize=10, ha='center')

        if allocations[i] > 0:
            ax.text(i + 0.25, 0.3 + bucket_height / 2, f"${allocations[i]:.2f}", fontsize=10, color='blue', ha='center')

    ax.set_xlim([-2, num_accounts + 1])
    ax.set_ylim([0, 1])
    ax.axis('off')
    st.pyplot(fig)

# Function to display the dashboard based on user responses
def show_dashboard(responses):
    st.title("Your Personalized Financial Dashboard")

    st.subheader("Your Financial Overview:")
    st.write(f"**Age**: {responses['age']}")
    st.write(f"**Occupation Status**: {responses['occupation_status']}")
    
    if responses['occupation_status'] == 'Employed':
        st.write(f"**Monthly Take-Home Pay**: ${responses['paycheck']}")
    
    st.subheader("Your Accounts:")
    accounts = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate (%)', 'Balance'])
    st.write(accounts)

    visualize_buckets(responses)

    st.subheader("Your Financial Goals:")
    for goal, goal_detail in responses['goals'].items():
        st.write(f"**{goal}**: {goal_detail}")

    st.subheader("Projected Account Values")
    current_year = date.today().year
    snapshot_year = responses['future_year']
    years_to_calculate = snapshot_year - current_year

    st.write("Projected Account Values:")
    future_values = {}
    for account in responses['accounts']:
        account_name, _, interest_rate, balance = account
        allocation = responses['allocations'].get(account_name, 0)
        future_value = calculate_future_value(balance, interest_rate, years_to_calculate, allocation)
        future_values[account_name] = future_value
        st.write(f"**{account_name}**: ${future_value:.2f}")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(future_values.keys(), future_values.values(), color='skyblue')
    ax.set_ylabel('Projected Value ($)')
    ax.set_title(f'Projected Account Values in {snapshot_year}')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Main function to run the app
def main():
    try:
        st.header("Welcome to the Financial Planning App")

        if 'responses' not in st.session_state:
            st.session_state.responses = {
                'accounts': [],
                'allocations': {},
                'goals': {}
            }

        responses = st.session_state.responses

        # Input for birthday
        birthday = st.date_input("When is your birthday?")
        if birthday:
            responses['age'] = calculate_age(birthday)

        # Occupation status
        responses['occupation_status'] = st.selectbox("Current occupation status:", 
                                                        ["Unemployed", "Student", "Employed", "Maternity/Paternity Leave"])

        # Input for monthly take-home pay
        if responses['occupation_status'] == "Employed":
            responses['paycheck'] = st.number_input("What is your monthly take-home pay after tax?", min_value=0.0)

        # Accounts input
        st.subheader("Tell us about your existing bank accounts:")
        
        # Create a form to add accounts
        with st.form("account_form"):
            acc_name = st.text_input("Account Name (e.g., Chequing, HYSA, etc.)")
            acc_type = st.selectbox("Account Type", ["HYSA", "Regular Savings", "Invested", "Registered"])
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
            balance = st.number_input("Current Balance ($)", min_value=0.0)
            
            # Submit button to add account
            if st.form_submit_button("Add Account"):
                responses['accounts'].append((acc_name, acc_type, interest_rate, balance))
                st.success(f"Added {acc_name} successfully!")

        # Show all added accounts
        st.write("### Current Accounts:")
        if responses['accounts']:
            accounts_df = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate (%)', 'Balance'])
            for i, account in enumerate(responses['accounts']):
                cols = st.columns([3, 1])  # Create two columns
                cols[0].write(account)  # Show account details
                if cols[1].button("Delete", key=f"delete_{i}"):  # Delete button
                    responses['accounts'].pop(i)
                    st.experimental_rerun()  # Refresh the app after deletion

        # Capture allocations after adding accounts
        if responses['accounts']:
            st.subheader("How much would you like to allocate from your monthly take-home pay into each account?")
            for account in responses['accounts']:
                account_name = account[0]
                allocation = st.number_input(f"Allocation for {account_name}:", min_value=0.0, key=account_name)
                responses['allocations'][account_name] = allocation

        # Capture goal details
        goal_types = st.multiselect("What type of goals do you want to focus on today?", 
                                    ["This Year", "Short-term (1-5 years)", "Long-term (5-15 years)", "Retirement", "Debt payments", "House deposits/mortgages"])
        
        for goal in goal_types:
            goal_detail = st.text_input(f"Describe your goal for: {goal}", key=goal)
            if goal_detail:
                responses['goals'][goal] = goal_detail

        # Input for future year before showing dashboard
        current_year = date.today().year
        responses['future_year'] = st.number_input("Enter a future year for projections:", min_value=current_year, step=1)

        # Show dashboard
        if st.button("Show Dashboard"):
            show_dashboard(responses)

        # Button to navigate to Current You tool
        if st.button("Go to Current You Tool"):
            run_current_you_tool()  # Call the Current You tool function

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

 # Button to open Current You Tool
    if st.button("Open Current You Tool"):
        # Use the 'st.markdown' to create a link that opens in a new window
        st.markdown(
            '<a href="https://current-you.streamlit.app/" target="_blank" rel="noopener noreferrer">Open Current You Tool</a>', 
            unsafe_allow_html=True
        )
     
# Run the app
if __name__ == "__main__":
    main()
