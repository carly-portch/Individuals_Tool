# Main function to run the app
def main():
    st.header("Welcome to the Financial Planning App")

    # Store user responses in session state
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
        st.write(accounts_df)

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
    
    # Capture goals
    for goal in goal_types:
        goal_detail = st.text_input(f"Describe your goal for: {goal}", key=goal)
        if goal_detail:
            responses['goals'][goal] = goal_detail

    # Input for future year before showing dashboard
    current_year = date.today().year  # Ensure current_year is defined here
    responses['future_year'] = st.number_input("Enter a future year for projections:", min_value=current_year, step=1)

    # Show dashboard
    if st.button("Show Dashboard"):
        show_dashboard(responses)

# Run the app
if __name__ == "__main__":
    main()
