import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# Set the page config to wide mode
st.set_page_config(page_title="Financial Planning App", layout="wide")

# Function to calculate age from birthday
def calculate_age(birthday):
    today = date.today()
    birthdate = pd.to_datetime(birthday)
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Function to calculate future value with monthly contributions
def calculate_future_value(principal, annual_rate, years, monthly_contribution):
    # Convert annual rate to a monthly rate
    monthly_rate = annual_rate / 100 / 12

    # Future Value calculation
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

    # Set up figure
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw an arrow representing income
    ax.arrow(-1.5, 0.5, 1.5, 0, head_width=0.05, head_length=0.1, fc='green', ec='green')
    ax.text(-1.8, 0.5, 'Income', fontsize=12, color='green', ha='center', va='center')

    # Buckets (as rectangles)
    bucket_names = [acc[0] for acc in responses['accounts']]
    allocations = [responses['allocations'].get(acc[0], 0) for acc in responses['accounts']]  # User-defined allocations

    for i, account in enumerate(bucket_names):
        bucket_height = allocations[i] / paycheck if paycheck > 0 else 0
        bucket_color = 'lightblue' if bucket_height > 0 else 'lightgray'

        # Draw the bucket
        ax.add_patch(plt.Rectangle((i, 0.3), 0.5, bucket_height, fill=True, color=bucket_color, edgecolor='black'))
        ax.text(i + 0.25, 0.3 + bucket_height + 0.02, account, fontsize=10, ha='center')

        # Label the percentage and dollar amount that goes into each bucket
        percentage = responses['allocations'].get(account, 0)
        dollar_value = (responses['remaining_funds'] * (percentage / 100)) if responses['remaining_funds'] > 0 else 0
        ax.text(i + 0.25, 0.3 + bucket_height / 2, f"{percentage}% / ${dollar_value:.2f}", fontsize=10, color='blue', ha='center')

    # Hide axis
    ax.set_xlim([-2, num_accounts + 1])
    ax.set_ylim([0, 1])
    ax.axis('off')

    # Show the plot
    st.pyplot(fig)

# Function to display the dashboard based on user responses
def show_dashboard(responses):
    st.title("Your Personalized Financial Dashboard")

    st.subheader("Your Financial Overview:")
    st.write(f"**Age**: {responses['age']}")
    st.write(f"**Occupation Status**: {responses['occupation_status']}")

    if responses['occupation_status'] == 'Employed':
        st.write(f"**Monthly Take-Home Pay**: ${responses['paycheck']}")
        st.write(f"**Monthly Expenses**: ${responses['total_expenses']}")
        st.write(f"**Remaining Funds After Expenses**: ${responses['remaining_funds']}")

    st.subheader("Your Accounts:")
    accounts = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate (%)', 'Balance'])
    st.write(accounts)

    visualize_buckets(responses)

    st.subheader("Your Financial Goals:")
    for goal, goal_detail in responses['goals'].items():
        st.write(f"**{goal}**: {goal_detail}")

    # Projected account values in future year
    st.subheader("Projected Account Values")
    current_year = date.today().year
    snapshot_year = responses['future_year']
    years_to_calculate = snapshot_year - current_year

    st.write("Projected Account Values:")
    future_values = {}
    for account in responses['accounts']:
        account_name, _, interest_rate, balance = account
        allocation = responses['allocations'].get(account_name, 0)  # Get allocation for this account
        future_value = calculate_future_value(balance, interest_rate, years_to_calculate, allocation)
        future_values[account_name] = future_value
        st.write(f"**{account_name}**: ${future_value:.2f}")

    # Visualization for future values
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

        # Store user responses in session state
        if 'responses' not in st.session_state:
            st.session_state.responses = {
                'accounts': [],
                'allocations': {},
                'goals': {},
                'expenses': {},  # Store expenses here
                'total_expenses': 0,
                'remaining_funds': 0,
            }

        responses = st.session_state.responses

        # Create two columns with specified widths
        col1, col2 = st.columns([2, 5])  # 1 part for the left column (20%), 4 parts for the right column (80%)

        with col1:
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

            # Input for monthly expenses
            st.subheader("Enter Your Monthly Expenses:")
            expense_categories = st.text_input("Enter expense categories (comma-separated)", "Housing, Groceries, Transportation, Entertainment")
            expense_categories = [category.strip() for category in expense_categories.split(",")]
            for category in expense_categories:
                amount = st.number_input(f"{category}:", min_value=0.0, key=category)
                responses['expenses'][category] = amount

            # Calculate total expenses and remaining funds
            responses['total_expenses'] = sum(responses['expenses'].values())
            if responses.get('paycheck'):
                responses['remaining_funds'] = responses['paycheck'] - responses['total_expenses']

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
                    responses['allocations'][acc_name] = 0  # Initialize allocation for this account
                    st.success(f"Added {acc_name} successfully!")

            # Show all added accounts with percentage contribution and delete button
            st.write("### Current Accounts:")
            if responses['accounts']:
                for idx, account in enumerate(responses['accounts']):
                    account_name = account[0]
                    account_row = f"{account_name} - Type: {account[1]}, Interest: {account[2]}%, Balance: ${account[3]:.2f}"
                    
                    # Percentage input for the account
                    percentage = st.number_input(f"Percentage to contribute for {account_name} (%):", min_value=0.0, max_value=100.0, key=f"percentage_{idx}")
                    responses['allocations'][account_name] = percentage
                    
                    # Calculate and display dollar amount for contribution
                    dollar_value = (responses['remaining_funds'] * (percentage / 100)) if responses['remaining_funds'] > 0 else 0
                    st.write(f"You will contribute **${dollar_value:.2f}** to {account_name}.")

                    # Delete account option
                    col_delete, col_info = st.columns([1, 4])
                    with col_delete:
                        if st.button("Delete", key=f"delete_{idx}"):
                            responses['accounts'].pop(idx)
                            responses['allocations'].pop(account_name, None)  # Remove allocation as well
                            st.session_state.clear()  # Clear session state to refresh app
                            st.success(f"Deleted {account_name} successfully!")
                    with col_info:
                        st.write(account_row)

            # Capture goal details
            goal_types = st.multiselect("What type of goals do you want to focus on today?", 
                                        ["This Year", "Short-term (1-5 years)", "Long-term (5-15 years)", "Retirement", "Debt payments", "House deposits/mortgages"])
            
            # Capture goals
            for goal in goal_types:
                goal_detail = st.text_input(f"Describe your goal for: {goal}", key=goal)
                if goal_detail:
                    responses['goals'][goal] = goal_detail

            # Input for future year before showing dashboard
            current_year = date.today().year  # Ensure current_year is defined here
            responses['future_year'] = st.number_input("Enter a future year for projections:", min_value=current_year, step=1)

        with col2:
            # Show dashboard
            if st.button("Show Dashboard"):
                show_dashboard(responses)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Run the app
if __name__ == "__main__":
    main()
