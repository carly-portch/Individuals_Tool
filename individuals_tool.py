import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime

# Set the page config to wide mode
st.set_page_config(page_title="Get Aligned as a Couple", layout="wide")

# Function to calculate age from birthday
def calculate_age(birthday):
    today = date.today()
    birthdate = pd.to_datetime(birthday)
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Function to calculate future account value considering principal and monthly contributions
def calculate_future_value(principal, annual_rate, years, monthly_contribution):
    if annual_rate == 0:
        # Simple formula when the rate is 0 (no interest)
        future_value = principal + (monthly_contribution * years * 12)
    else:
        monthly_rate = annual_rate / 100 / 12
        months = years * 12
        try:
            future_value = principal * (1 + monthly_rate) ** months
            future_value += monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        except ZeroDivisionError:
            # Gracefully handle division by zero
            future_value = principal + (monthly_contribution * months)
    return future_value

# Function to calculate debt payback date based on fixed monthly payments
def calculate_payback_date(amount, interest_rate, monthly_payment):
    if monthly_payment <= 0:
        raise ValueError("Monthly payment must be greater than zero.")
    
    if interest_rate == 0:
        if monthly_payment < amount:
            raise ValueError("The monthly payment is not sufficient to pay off the debt.")
        months = amount / monthly_payment
    else:
        monthly_rate = interest_rate / 100 / 12
        if monthly_payment <= amount * monthly_rate:
            raise ValueError("The monthly payment is not sufficient to cover the interest on the debt.")
        months = np.log(monthly_payment / (monthly_payment - amount * monthly_rate)) / np.log(1 + monthly_rate)

    payback_date = date.today() + pd.DateOffset(months=int(months))
    return payback_date.date()

# Function to display progress toward goals
def display_goal_progress(goals, selected_year, account_balances):
    st.subheader(f"Goal Progress in {selected_year}:")
    if not goals:
        st.write("No goals have been added.")
        return

    for goal in goals:
        goal_name = goal["name"]
        goal_cost = goal["cost"]
        goal_year = goal["target_year"]
        account_name = goal["account"]

        if account_name not in account_balances:
            st.write(f"Account {account_name} not found.")
            continue

        # Calculate progress
        account_balance = account_balances[account_name]
        progress = min(account_balance / goal_cost, 1)  # Cap at 100%
        progress_percentage = progress * 100

        # Display progress bar and details
        st.write(f"**Goal: {goal_name}**")
        st.write(f"Cost: ${goal_cost:,.0f}, Target Year: {goal_year}")
        st.progress(progress)
        st.write(f"{progress_percentage:.0f}% of goal achieved.\n")

# Function to display the dashboard based on user responses
def show_dashboard(responses, selected_year):
    st.title("Your Personalized Financial Dashboard")

    current_year = date.today().year
    
    st.subheader("Your Monthly Overview:")
    # st.write(f"**Age**: {responses.get('age', 'N/A')}")
    st.write(f"**Monthly Take-Home Pay**: ${responses.get('paycheck', 0):,.0f}")
    st.write(f"**Monthly Expenses**: ${responses.get('total_expenses', 0):,.0f}")
    st.write(f"**Monthly Debt Payments**: ${responses.get('total_debt_payments', 0):,.0f}")
    
    remaining_funds = responses['paycheck'] - responses['total_expenses'] - responses['total_debt_payments']
    responses['remaining_funds'] = remaining_funds if remaining_funds > 0 else 0  # Ensure remaining funds don't go negative
    st.write(f"**Remaining Monthly Funds (After Expenses and Debt Payments)**: ${responses['remaining_funds']:,.0f}")

    st.subheader("Your Accounts Today:")
    if responses['accounts']:
        accounts_df = pd.DataFrame(responses['accounts'], columns=['Account Name', 'Type', 'Interest Rate (%)', 'Balance ($)'])
        st.write(accounts_df)
    else:
        st.write("No accounts added yet.")


    # Debt payback
    st.subheader("Debt Payback Dates:")
    st.write("These are the dates you will finish paying off your debts if you maintain your current monthly payments.")
    for debt in responses.get("debts", []):
        debt_name = debt['name']
        current_amount = debt['amount']
        interest_rate = debt['rate']
        monthly_payment = debt['monthly_payment']
        try:
            payback_date = calculate_payback_date(current_amount, interest_rate, monthly_payment)
            st.write(f"**{debt_name}** will be paid off by: {payback_date}")
        except Exception as e:
            st.error(f"Error calculating payback date for {debt_name}: {e}")

    st.session_state.dashboard_run = True

    st.subheader(f"Financial Snapshot in {selected_year}:")
    future_values = {}
    account_balances = {}  # To track balances for goal progress

    for account in responses['accounts']:
        account_name, _, interest_rate, balance = account
        allocation_percentage = responses['allocations'].get(account_name, 0)
        monthly_contribution = (responses['remaining_funds'] * (allocation_percentage / 100))
        years_to_project = selected_year - current_year

        try:
            future_value = calculate_future_value(balance, interest_rate, years_to_project, monthly_contribution)
            future_values[account_name] = future_value
            account_balances[account_name] = future_value
            st.write(f"Estimated balance in your **{account_name}** account in {selected_year}: ${future_value:,.0f}")
        except Exception as e:
            st.error(f"Error calculating future value for {account_name}: {e}")

    if future_values:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(future_values.keys(), future_values.values(), color='skyblue')
        ax.set_ylabel('Projected Value ($)')
        ax.set_title(f'Projected Account Values in {selected_year}')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Asset projections
    st.subheader(f"Asset Projections for {selected_year}:")
    for asset in responses.get("assets", []):
        asset_name = asset['name']
        current_value = asset['value']
        appreciation_rate = asset['rate']
        future_asset_value = calculate_future_value(current_value, appreciation_rate, selected_year - current_year, 0)
        st.write(f"The estimated value of **{asset_name}** in {selected_year} is: ${future_asset_value:,.0f}")
        
    # Display goal progress
    display_goal_progress(responses.get("goals", []), selected_year, account_balances)

# Main function to run the app
def main():
    if 'dashboard_run' not in st.session_state:
        st.session_state.dashboard_run = False
    
    if 'responses' not in st.session_state:
        st.session_state.responses = {
            'accounts': [],
            'allocations': {},
            'expenses': {},
            'total_expenses': 0,
            'remaining_funds': 0,
            'total_debt_payments': 0,
            'goals': [],
            'assets': [],
            'debts': []
        }

    responses = st.session_state.responses

    col1, col2 = st.columns([2, 5])

    with col1:
        with st.expander("Personal Information", expanded=not st.session_state.get('personal_info_complete', False)):
            birthday = st.date_input("When is your birthday?")
            if birthday:
                responses['age'] = calculate_age(birthday)
            st.session_state.personal_info_complete = True

        if st.session_state.get('personal_info_complete', False):
            with st.expander("Income", expanded=not st.session_state.get('income_info_complete', False)):
                paycheck = st.number_input("What is your monthly take-home pay after tax?", min_value=0.0)
                responses['paycheck'] = paycheck
                st.session_state.income_info_complete = True

        if st.session_state.get('income_info_complete', False):
            with st.expander("Expenses", expanded=not st.session_state.get('expenses_info_complete', False)):
                st.subheader("Enter Your Monthly Expenses:")
                expense_categories = st.text_input("Enter approximate total monthly expenses (if you would prefer to input by expense category, please write the categories in the text box below with commas between each category)", "Total expenses")
                expense_categories = [category.strip() for category in expense_categories.split(",")]
                total_expenses = 0.0
                for category in expense_categories:
                    amount = st.number_input(f"{category}:", min_value=0.0, key=category)
                    responses['expenses'][category] = amount
                    total_expenses += amount
                responses['total_expenses'] = total_expenses
                st.session_state.expenses_info_complete = True

        if st.session_state.get('expenses_info_complete', False):
            with st.expander("Debts", expanded=True):
                st.subheader("Enter Your Debts:")
                
                with st.form("add_debt_form"):
                    debt_name = st.text_input("Debt Name")
                    debt_amount = st.number_input("Current Amount ($)", min_value=0.0)
                    debt_rate = st.number_input("Interest Rate (%)", min_value=0.0)
                    monthly_payment = st.number_input("Monthly Payment Amount ($)", min_value=0.0)
                    if st.form_submit_button("Add Debt"):
                        debt_data = {
                            "name": debt_name,
                            "amount": debt_amount,
                            "rate": debt_rate,
                            "monthly_payment": monthly_payment
                        }
                        responses['debts'].append(debt_data)
                        responses['total_debt_payments'] += monthly_payment
                        st.success(f"Debt '{debt_name}' added.")
                        st.rerun()

                # Display current debts as cards with edit and delete options
                st.subheader("Current Debts:")
                if responses['debts']:
                    for idx, debt in enumerate(responses['debts']):
                        st.markdown(f"**{debt['name']}** - Amount: \${debt['amount']:,.0f}, Interest: {debt['rate']}%, Monthly Payment: \${debt['monthly_payment']:,.0f}")
                        
                        col_edit_debt, col_delete_debt = st.columns([1, 1])
                        with col_edit_debt:
                            if st.button(f"Edit {debt['name']}", key=f"edit_debt_{idx}"):
                                with st.form(f"edit_debt_form_{idx}"):
                                    debt_name = st.text_input("Debt Name", value=debt['name'])
                                    debt_amount = st.number_input("Current Amount ($)", min_value=0.0, value=debt['amount'])
                                    debt_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=debt['rate'])
                                    monthly_payment = st.number_input("Monthly Payment Amount ($)", min_value=0.0, value=debt['monthly_payment'])
                                    if st.form_submit_button("Update Debt"):
                                        debt_difference = monthly_payment - debt['monthly_payment']
                                        responses['debts'][idx] = {
                                            "name": debt_name,
                                            "amount": debt_amount,
                                            "rate": debt_rate,
                                            "monthly_payment": monthly_payment
                                        }
                                        responses['total_debt_payments'] += debt_difference
                                        st.success(f"Debt '{debt_name}' updated.")
                                        st.rerun()

                        with col_delete_debt:
                            if st.button(f"Delete {debt['name']}", key=f"delete_debt_{idx}"):
                                responses['total_debt_payments'] -= debt['monthly_payment']
                                del responses['debts'][idx]
                                st.success(f"Debt '{debt['name']}' deleted.")
                                st.rerun()

        if st.session_state.get('expenses_info_complete', False):
            with st.expander("Accounts", expanded=True):
                st.subheader("Tell us about your existing bank accounts:")

                with st.form("add_account_form"):
                    acc_name = st.text_input("Account Name (e.g., Chequing, HYSA, etc.)")
                    acc_type = st.selectbox("Account Type", ["Chequing", "Regular Savings", "HYSA", "Invested", "Registered"])
                    st.write("The interest rate represents the amount of interest gained based on the account it is in. If money in the account is invested, a good estimate is 7%, if the money is in a regular chequing/savings account, a good estimate is 0.05%.")
                    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
                    balance = st.number_input("Current Balance ($)", min_value=0.0)
                    if st.form_submit_button("Add Account"):
                        responses['accounts'].append((acc_name, acc_type, interest_rate, balance))
                        responses['allocations'][acc_name] = 0.0
                        st.success(f"Account {acc_name} added.")
                        st.rerun()

                # Display current accounts as cards with edit and delete options
                st.subheader("Current Accounts:")
                if responses['accounts']:
                    for idx, account in enumerate(responses['accounts']):
                        st.markdown(f"**{account[0]}** - Type: {account[1]}, Interest Rate: {account[2]}%, Balance: ${account[3]:,.0f}")
                        
                        col_edit, col_delete = st.columns([1, 1])
                        with col_edit:
                            if st.button(f"Edit {account[0]}", key=f"edit_{idx}"):
                                with st.form(f"edit_account_form_{idx}"):
                                    acc_name = st.text_input("Account Name", value=account[0])
                                    acc_type = st.selectbox("Account Type", ["HYSA", "Regular Savings", "Invested", "Registered"], index=["HYSA", "Regular Savings", "Invested", "Registered"].index(account[1]))
                                    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=account[2])
                                    balance = st.number_input("Current Balance ($)", min_value=0.0, value=account[3])
                                    if st.form_submit_button("Update Account"):
                                        responses['accounts'][idx] = (acc_name, acc_type, interest_rate, balance)
                                        st.success(f"Account {acc_name} updated.")
                                        st.rerun()

                        with col_delete:
                            if st.button(f"Delete {account[0]}", key=f"delete_{idx}"):
                                del responses['accounts'][idx]
                                st.success(f"Account {account[0]} deleted.")
                                st.rerun()

                # Allocation inputs for each account
                total_allocation = 0.0
                st.write("Please specify what percentage of your remaining monthly income will be deposited into each account. The percentages must total 100%.")
                for account in responses['accounts']:
                    account_name = account[0]
                    percentage = st.number_input(f"Percentage of remaining monthly income to contribute to {account_name} (%):", min_value=0.0, max_value=100.0, key=f"alloc_{account_name}")
                    responses['allocations'][account_name] = percentage
                    total_allocation += percentage

                if total_allocation != 100.0:
                    st.warning("The total allocation percentages must sum to 100%.")

        if st.session_state.get('expenses_info_complete', False):
            with st.expander("Assets", expanded=True):
                st.subheader("Enter Your Assets:")
                
                with st.form("add_asset_form"):
                    asset_name = st.text_input("Asset Name")
                    asset_value = st.number_input("Current Value ($)", min_value=0.0)
                    asset_rate = st.number_input("Expected Appreciation Rate (%)", min_value=0.0)
                    if st.form_submit_button("Add Asset"):
                        asset_data = {
                            "name": asset_name,
                            "value": asset_value,
                            "rate": asset_rate
                        }
                        responses['assets'].append(asset_data)
                        st.success(f"Asset '{asset_name}' added.")
                        st.rerun()

                # Display current assets as cards with edit and delete options
                st.subheader("Current Assets:")
                if responses['assets']:
                    for idx, asset in enumerate(responses['assets']):
                        st.markdown(f"**{asset['name']}** - Value: ${asset['value']:,.0f}, Appreciation Rate: {asset['rate']}%")
                        
                        col_edit_asset, col_delete_asset = st.columns([1, 1])
                        with col_edit_asset:
                            if st.button(f"Edit {asset['name']}", key=f"edit_asset_{idx}"):
                                with st.form(f"edit_asset_form_{idx}"):
                                    asset_name = st.text_input("Asset Name", value=asset['name'])
                                    asset_value = st.number_input("Current Value ($)", min_value=0.0, value=asset['value'])
                                    asset_rate = st.number_input("Expected Appreciation Rate (%)", min_value=0.0, value=asset['rate'])
                                    if st.form_submit_button("Update Asset"):
                                        responses['assets'][idx] = {
                                            "name": asset_name,
                                            "value": asset_value,
                                            "rate": asset_rate
                                        }
                                        st.success(f"Asset '{asset_name}' updated.")
                                        st.rerun()

                        with col_delete_asset:
                            if st.button(f"Delete {asset['name']}", key=f"delete_asset_{idx}"):
                                del responses['assets'][idx]
                                st.success(f"Asset '{asset['name']}' deleted.")
                                st.rerun()

        if st.session_state.get('expenses_info_complete', False):
            with st.expander("Goals", expanded=True):
                st.subheader("Set Your Financial Goals:")
                
                with st.form("add_goal_form"):
                    goal_name = st.text_input("Goal Name")
                    goal_cost = st.number_input("Cost of the Goal ($)", min_value=0.0)
                    goal_year = st.number_input("Target Year", min_value=date.today().year)
                    account_name = st.selectbox("Select Account to Fund the Goal", [acc[0] for acc in responses['accounts']])
                    if st.form_submit_button("Add Goal"):
                        goal_data = {
                            "name": goal_name,
                            "cost": goal_cost,
                            "target_year": goal_year,
                            "account": account_name
                        }
                        responses['goals'].append(goal_data)
                        st.success(f"Goal '{goal_name}' added.")
                        st.rerun()

                # Display current goals as cards with edit and delete options
                st.subheader("Current Goals:")
                if responses['goals']:
                    for idx, goal in enumerate(responses['goals']):
                        st.markdown(f"**{goal['name']}** - Cost: ${goal['cost']}, Target Year: {goal['target_year']}, Funded by: {goal['account']}")
                        
                        col_edit_goal, col_delete_goal = st.columns([1, 1])
                        with col_edit_goal:
                            if st.button(f"Edit {goal['name']}", key=f"edit_goal_{idx}"):
                                with st.form(f"edit_goal_form_{idx}"):
                                    goal_name = st.text_input("Goal Name", value=goal['name'])
                                    goal_cost = st.number_input("Cost of the Goal ($)", min_value=0.0, value=goal['cost'])
                                    goal_year = st.number_input("Target Year", min_value=date.today().year, value=goal['target_year'])
                                    account_name = st.selectbox("Select Account to Fund the Goal", [acc[0] for acc in responses['accounts']], index=[acc[0] for acc in responses['accounts']].index(goal['account']))
                                    if st.form_submit_button("Update Goal"):
                                        responses['goals'][idx] = {
                                            "name": goal_name,
                                            "cost": goal_cost,
                                            "target_year": goal_year,
                                            "account": account_name
                                        }
                                        st.success(f"Goal '{goal_name}' updated.")
                                        st.rerun()

                        with col_delete_goal:
                            if st.button(f"Delete {goal['name']}", key=f"delete_goal_{idx}"):
                                del responses['goals'][idx]
                                st.success(f"Goal '{goal['name']}' deleted.")
                                st.rerun()

    with col2:
        selected_year = st.number_input("Snapshot Year:", min_value=date.today().year, value=date.today().year + 5)

        if st.button("Show Dashboard"):
            show_dashboard(responses, selected_year)

if __name__ == "__main__":
    main()
