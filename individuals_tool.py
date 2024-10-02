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
def calculate_future_value(principal, annual_rate, years, monthly_contribution, frequency):
    # Convert annual rate to a monthly rate
    monthly_rate = annual_rate / 100 / 12
    
    # Number of contributions based on frequency
    if frequency == 'Monthly':
        total_contributions = years * 12
    elif frequency == 'Bi-weekly':
        total_contributions = years * 26
    elif frequency == 'Weekly':
        total_contributions = years * 52
    else:
        total_contributions = 0  # Handle unexpected frequency

    # Future Value calculation
    future_value = principal * (1 + monthly_rate) ** total_contributions
    future_value += monthly_contribution * (((1 + monthly_rate) ** total_contributions - 1) / monthly_rate)
    return future_value

# Function to visualize income distribution into buckets
def visualize_buckets(responses):
    st.subheader("Income Distribution Visualization")

    # Check if the user has accounts
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

    # Buckets (as rectangles) with user-defined allocations
    bucket_names = [acc[0] for acc in responses['accounts']]
    allocations = [acc[4] for acc in responses['accounts']]  # User-defined allocations

    for i, account in enumerate(bucket_names):
        bucket_height = allocations[i] / paycheck if paycheck > 0 else 0
        bucket_color = 'lightblue' if bucket_height > 0 else 'lightgray'

        # Draw the bucket
        ax.add_patch(plt.Rectangle((i, 0.3), 0.5, bucket_height, fill=True, color=bucket_color, edgecolor='black'))
        ax.text(i + 0.25, 0.3 + bucket_height + 0.02, account, fontsize=10, ha='center')

        # Label the amount that goes into each bucket
        if allocations[i] > 0:
            ax.text(i + 0.25, 0.3 + bucket_height / 2, f"${allocations[i]:.2f}", fontsize=10, color='blue', ha='center')

    # Hide axis
    ax.set_xlim([-2, num_accounts + 1])
    ax.set_ylim([0, 1])
    ax.axis('off')

    # Show the plot
    st.pyplot(fig)

# Function to display the dashboard based on user responses
def show_dashboard(responses):
    st.title("Your Personalized Financial Dashboard")
    
    # Show basic info and accounts
    st.subheader("Your Financial Overview:")
    st.write(f"**Age**: {responses['age']}")
    st.write(f"**Occupation Status**: {responses['occupation_status']}")
    
    if responses['occupation_status'] == 'Employed':
        st.write(f"**Paycheck**: ${responses['paycheck']} at {responses['paycheck_frequency']} frequency")
    elif responses['occupation_status'] == 'Student' and responses.get('student_income'):
        st.write(f"**Part-time income during school**: ${responses['student_income']}")

    st.subheader("Your Accounts:")
    accounts = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate (%)', 'Balance', 'User Allocation'])
    st.write(accounts)

    # Visualize the income being distributed into accounts
    visualize_buckets(responses)

    # Goal-based dashboard elements
    st.subheader("Your Financial Goals:")
    for goal, goal_detail in responses['goals'].items():
        st.write(f"**{goal}**: {goal_detail}")

    # Snapshot feature for future account values
    st.subheader("Account Snapshot for a Future Year")
    year_input = st.number_input("Enter a future year:", min_value=date.today().year, step=1)
    
    if st.button("Calculate Snapshot"):
        snapshot_year = year_input
        current_year = date.today().year
        years_to_calculate = snapshot_year - current_year
        
        st.write("Projected Account Values:")
        future_values = {}
        for account in responses['accounts']:
            account_name, _, interest_rate, balance, allocation = account
            future_value = calculate_future_value(balance, interest_rate, years_to_calculate, allocation, responses['paycheck_frequency'])
            future_values[account_name] = future_value
            st.write(f"**{account_name}**: ${future_value:.2f}")

        # Visualization for future values
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(future_values.keys(), future_values.values(), color='skyblue')
        ax.set_ylabel('Projected Value ($)')
        ax.set_title(f'Projected Account Values in {snapshot_year}')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.write("You can further personalize your dashboard or add more goals from the side panel.")

# Main function to run the app
def main():
    st.header("Welcome to the Financial Planning App")

    # Store user responses
    responses = {}

    # Input for birthday
    birthday = st.date_input("When is your birthday?")
    if birthday:
        responses['age'] = calculate_age(birthday)

    # Occupation status
    responses['occupation_status'] = st.selectbox("Current occupation status:", 
                                                    ["Unemployed", "Student", "Employed", "Maternity/Paternity Leave"])

    # Input for paycheck if employed
    if responses['occupation_status'] == "Employed":
        responses['paycheck'] = st.number_input("What is your paycheck amount?", min_value=0)
        responses['paycheck_frequency'] = st.selectbox("How frequently do you get paid?", ["Monthly", "Bi-weekly", "Weekly"])

    # Accounts input
    st.subheader("Tell us about your existing bank accounts:")
    responses['accounts'] = []
    
    # Create a form to add accounts
    with st.form("account_form"):
        acc_name = st.text_input("Account Name (e.g., Chequing, HYSA, etc.)")
        acc_type = st.selectbox("Account Type", ["HYSA", "Regular Savings", "Invested", "Registered"])
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
        balance = st.number_input("Current Balance ($)", min_value=0.0)
        allocation = st.number_input("User Allocation ($)", min_value=0.0)
        
        # Submit button to add account
        if st.form_submit_button("Add Account"):
            responses['accounts'].append((acc_name, acc_type, interest_rate, balance, allocation))
            st.success(f"Added {acc_name} successfully!")

    # Finish adding accounts button
    if st.button("Finish Adding Accounts"):
        if not responses['accounts']:
            st.warning("Please add at least one account before finishing.")
        else:
            st.success("Finished adding accounts!")

    # Capture goal details
    goal_types = st.multiselect("What type of goals do you want to focus on today?", 
                                ["This Year", "Short-term (1-5 years)", "Long-term (5-15 years)", "Retirement", "Debt payments", "House deposits/mortgages"])
    
    # Capture goals
    responses['goals'] = {}
    for goal in goal_types:
        goal_detail = st.text_input(f"Please specify details for your goal: {goal}", key=f"goal_{goal}")
        responses['goals'][goal] = goal_detail

    # Show the dashboard based on the responses collected
    show_dashboard(responses)

if __name__ == "__main__":
    main()
