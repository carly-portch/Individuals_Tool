import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
import pandas as pd

# Function to calculate user's age
def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthday.day))
    return age

# Function to visualize income distribution into buckets
def visualize_buckets(responses):
    st.subheader("Income Distribution Visualization")

    # Check if the user is employed
    if responses['occupation_status'] != "Employed":
        st.write("This visualization is only available for employed users.")
        return

    # Get the number of accounts and total paycheck
    num_accounts = len(responses['accounts'])
    paycheck = responses['paycheck']
    if num_accounts == 0:
        st.write("No accounts available to distribute income.")
        return

    # Set up figure
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw an arrow representing income
    ax.arrow(-1.5, 0.5, 1.5, 0, head_width=0.05, head_length=0.1, fc='green', ec='green')
    ax.text(-1.8, 0.5, 'Income', fontsize=12, color='green', ha='center', va='center')

    # Buckets (as rectangles) with user-defined allocations
    bucket_names = [acc[0] for acc in responses['accounts']]
    allocations = [acc[5] for acc in responses['accounts']]  # User-defined allocations

    for i, account in enumerate(bucket_names):
        bucket_height = allocations[i] / paycheck if paycheck > 0 else 0
        bucket_color = 'lightblue' if bucket_height > 0 else 'lightgray'  # Color for allocated vs unallocated

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
    accounts = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate', 'Balance', 'Automated Deposit', 'User Allocation'])
    st.write(accounts)

    # Visualize the income being distributed into accounts
    visualize_buckets(responses)

    # Goal-based dashboard elements
    st.subheader("Your Financial Goals:")
    for goal, goal_detail in responses['goals'].items():
        st.write(f"**{goal}**: {goal_detail}")

    st.write("You can further personalize your dashboard or add more goals from the side panel.")

# Streamlit app logic
def main():
    st.title("Financial Planning for 20-Somethings")

    # Store user responses
    responses = {}

    # Ask for birthday and calculate age
    birthday = st.date_input("When is your birthday?")
    age = calculate_age(birthday)
    responses['age'] = age

    # Ask for occupation status
    occupation_status = st.radio("What is your current occupation status?", 
                                 ["Unemployed", "Student", "Employed", "Maternity/Paternity Leave", "Other"])
    responses['occupation_status'] = occupation_status

    if occupation_status == "Employed":
        paycheck = st.number_input("What is your paycheck?", min_value=0, step=100)
        paycheck_frequency = st.selectbox("How frequently do you get paid?", ["Monthly", "Bi-weekly", "Weekly", "Other"])
        responses['paycheck'] = paycheck
        responses['paycheck_frequency'] = paycheck_frequency
    elif occupation_status == "Student":
        student_income = st.number_input("Do you have any part-time job income during the school year?", min_value=0, step=100)
        responses['student_income'] = student_income

    # Ask for relationship status
    relationship_status = st.radio("What is your current relationship status?", 
                                   ["Single", "In a relationship but not ready to plan finances together yet", 
                                    "In a relationship and ready to plan finances together"])
    responses['relationship_status'] = relationship_status

    # Ask about bank accounts
    st.subheader("Tell us about your existing or planned bank accounts:")
    account_names = []
    account_types = []
    interest_rates = []
    balances = []
    automated_deposits = []
    allocations = []
    
    add_account = True
    while add_account:
        st.write("Enter details for a new account:")
        account_name = st.text_input("Account Name (e.g., Chequing, HYSA, TFSA, etc.)", key=f"acc_name_{len(account_names)}")
        account_type = st.selectbox("Account Type", ["HYSA", "Regular Savings", "Invested", "Registered"], key=f"acc_type_{len(account_names)}")
        interest_rate = st.number_input("Interest Rate (optional)", value=0.0, step=0.1, key=f"int_rate_{len(account_names)}")
        balance = st.number_input(f"How much is currently in your {account_name} account?", min_value=0, step=100, key=f"balance_{len(account_names)}")
        auto_deposit = st.number_input(f"How much do you currently auto-deposit into your {account_name} account?", min_value=0, step=50, key=f"auto_deposit_{len(account_names)}")
        
        # User-defined allocation input using sliders
        max_allocation = responses['paycheck'] if 'paycheck' in responses else 0
        allocation = st.slider(f"How much of your paycheck do you want to allocate to {account_name}?", min_value=0, max_value=max_allocation, step=10, key=f"allocation_{len(account_names)}")

        account_names.append(account_name)
        account_types.append(account_type)
        interest_rates.append(interest_rate)
        balances.append(balance)
        automated_deposits.append(auto_deposit)
        allocations.append(allocation)

        add_account = st.checkbox("Add another account?", key=f"add_account_{len(account_names)}")

    responses['accounts'] = list(zip(account_names, account_types, interest_rates, balances, automated_deposits, allocations))

    # Validate total allocations do not exceed paycheck
    total_allocated = sum(allocations)
    if total_allocated > responses.get('paycheck', 0):
        st.error(f"Total allocations (${total_allocated:.2f}) exceed your paycheck (${responses.get('paycheck', 0):.2f}). Please adjust your allocations.")
        return

    # Ask for goals
    st.subheader("What type of goals do you want to focus on today?")
    goal_types = st.multiselect("Choose your financial goals", 
                                ["This year", "Short-term (1-5 years)", "Long-term (5-15 years)", 
                                 "Retirement", "Debt payments", "House deposit/mortgage"])

    responses['goals'] = {}
    for goal in goal_types:
        goal_detail = st.text_input(f"Tell us more about your {goal} goal", key=f"goal_{goal}")
        responses['goals'][goal] = goal_detail

    # Submit button to show dashboard
    if st.button("Submit"):
        show_dashboard(responses)

if __name__ == '__main__':
    main()
