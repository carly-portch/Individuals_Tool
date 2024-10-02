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
    allocations = [acc[4] for acc in responses['accounts']]  # Change the index to 4 for User Allocation

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

        # Optionally, show a visualization for future values
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(future_values.keys(), future_values.values(), color='skyblue')
        ax.set_ylabel('Projected Value ($)')
        ax.set_title(f'Projected Account Values in {snapshot_year}')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.write("You can further personalize your dashboard or add more goals from the side panel.")
