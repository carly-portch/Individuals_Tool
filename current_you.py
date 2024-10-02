import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Custom CSS for cleaner aesthetics
def set_custom_styles():
    st.markdown(
        """
        <style>
        /* Background color */
        .stApp {
            background-color: #fafafa;
        }
        /* General styles */
        body {
            color: #333333;
            background-color: #f0f2f6;
        }
        
        /* Title and description */
        .title {
            color: #4B0082;  /* Indigo */
            text-align: center;
            margin-bottom: 20px;
        }
        
        .description {
            background-color: #e6e6fa;  /* Lavender */
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-family: 'Verdana', sans-serif;  /* Added font style */
        }
        
        /* Section headers */
        .section-header {
            color: #4B0082;  /* Indigo */
            margin-top: 30px;
            margin-bottom: 10px;
        }
        
        /* Section2 headers */
        .section2-header {
            color: black;  /* Black */
            margin-top: 10px;
            margin-bottom: 10px;
        }

        /* Text styling */
        .stApp p, .stApp div, .stApp span, .stApp label {
            color: #4f4f4f;
            font-family: 'Verdana', sans-serif;
        }
        /* Button styling */
        .stButton>button {
            color: #e6e6fa;
            background-color: #e6e6fa; /* Changed for better contrast */
            border-radius: 5px;
            padding: 0.6em 1.2em;
            font-weight: bold;
        }
        /* Input field styling */
        input {
            border: 2px solid #2e6ef7;
            border-radius: 6px;
        }
        /* Expense Calculation Results Styling */
        .stApp .stMarkdown h3 {
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            color: #2e6ef7;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to create pie chart
def create_pie_chart(data, title, colors=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 12})
    ax.set_title(title, fontweight="bold")
    plt.axis('equal')
    return fig

# Function to create bar chart
def create_bar_chart(data, title):
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(data.keys(), data.values(), color='#2e6ef7')
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel('Amount ($)', fontweight="bold")
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01 * max(data.values()),
                f'${height:.2f}', ha='center', va='bottom')
        
    plt.tight_layout()
    return fig

def main():
    # Apply custom styles
    set_custom_styles()

    st.markdown("<h1 class='title'>The Current You Tool</h1>", unsafe_allow_html=True)

    # Description in the correct style
    st.markdown(
        "<div class='description'><h5>This tool helps us understand your current financial habits. Use this tool in combination with the 'Future You' tool to balance your current and future desires!<br><br>"
        "When entering your current monthly expenses, aim for accuracy to get the best insights. Using the past three months of income and spending as a guide will help provide an average for a typical month. Reviewing your credit card and bank statements is a great way to start. Please feel free to use this to analyse your personal finances, joint finances with a partner, or family finances."
        "</h5></div>",
        unsafe_allow_html=True
    )

    st.markdown("<h2 class='section-header'>Step 1: Enter Your Monthly Expenses</h2>", unsafe_allow_html=True)

    # New Section: Enter Post-Tax Income
    st.markdown("<h4 class='section2-header'>Monthly Income</h4>", unsafe_allow_html=True)
    post_tax_income = st.number_input("Enter your monthly post-tax income:", min_value=0.0, step=100.0)

    # Initialize session state variables
    if 'fixed_expenses' not in st.session_state:
        st.session_state.fixed_expenses = {'Housing': 0.0, 'Utilities': 0.0, 'Insurance': 0.0, 'Transportation': 0.0, 'Debt Payments': 0.0, 'Groceries': 0.0}
    if 'variable_expenses' not in st.session_state:
        st.session_state.variable_expenses = {'Fun (trips, vacations etc.)': 0.0}

    st.markdown("<h4 class='section2-header'>Monthly Fixed Expenses</h4>", unsafe_allow_html=True)
    # Display fixed expenses inputs
    fixed_expenses_to_delete = []
    for category in st.session_state.fixed_expenses:
        col1, col2 = st.columns([3, 1])
        with col1:
            amount = st.number_input(f"{category}:", min_value=0.0, step=10.0, key=f"fixed_{category}")
            st.session_state.fixed_expenses[category] = amount
        with col2:
            if st.button("Delete", key=f"delete_fixed_{category}"):
                fixed_expenses_to_delete.append(category)
    # Remove deleted fixed expense categories
    for category in fixed_expenses_to_delete:
        del st.session_state.fixed_expenses[category]

    # Add new fixed expense category
    new_fixed_category = st.text_input("Add a new fixed expense category:")
    if st.button("Add Fixed Expense Category"):
        if new_fixed_category:
            if new_fixed_category not in st.session_state.fixed_expenses:
                st.session_state.fixed_expenses[new_fixed_category] = 0.0
            else:
                st.warning("Category already exists.")
        else:
            st.warning("Please enter a category name.")

    st.markdown("<h4 class='section2-header'>Monthly Variable Expenses</h4>", unsafe_allow_html=True)
    # Display variable expenses inputs
    variable_expenses_to_delete = []
    for category in st.session_state.variable_expenses:
        col1, col2 = st.columns([3, 1])
        with col1:
            amount = st.number_input(f"{category}:", min_value=0.0, step=10.0, key=f"variable_{category}")
            st.session_state.variable_expenses[category] = amount
        with col2:
            if st.button("Delete", key=f"delete_variable_{category}"):
                variable_expenses_to_delete.append(category)
    # Remove deleted variable expense categories
    for category in variable_expenses_to_delete:
        del st.session_state.variable_expenses[category]

    # Add new variable expense category
    new_variable_category = st.text_input("Add a new variable expense category:")
    if st.button("Add Variable Expense Category"):
        if new_variable_category:
            if new_variable_category not in st.session_state.variable_expenses:
                st.session_state.variable_expenses[new_variable_category] = 0.0
            else:
                st.warning("Category already exists.")
        else:
            st.warning("Please enter a category name.")

    # Input expense limit from Future You tool
    st.markdown("<h2 class='section-header'>Step 2: Enter Expense Limit from 'Future You' Tool</h2>", unsafe_allow_html=True)
    future_you_limit = st.number_input("Enter the monthly expense limit suggested by the Future You tool (the red number at the bottom of the Future You tool):", min_value=0.0, step=10.0)

    # Calculate total expenses
    if st.button("Calculate Expenses"):
        fixed_expenses_data = st.session_state.fixed_expenses
        variable_expenses_data = st.session_state.variable_expenses

        total_fixed_expenses = sum(fixed_expenses_data.values())
        total_variable_expenses = sum(variable_expenses_data.values())
        total_expenses = total_fixed_expenses + total_variable_expenses

        # Calculate expense ratios
        if total_expenses > 0:
            expense_ratio = (total_expenses / post_tax_income) * 100
            fixed_expense_ratio = (total_fixed_expenses / post_tax_income) * 100

            st.success(f"Total Expenses: ${total_expenses:.2f}")
            st.success(f"Expense Ratio: {expense_ratio:.2f}% of income")
            st.success(f"Fixed Expenses: ${total_fixed_expenses:.2f}")
            st.success(f"Fixed Expense Ratio: {fixed_expense_ratio:.2f}% of income")

            # Pie chart for expenses
            expense_data = {**fixed_expenses_data, **variable_expenses_data}
            expense_colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']
            pie_fig = create_pie_chart(expense_data, "Expense Distribution", colors=expense_colors)
            st.pyplot(pie_fig)

            # Bar chart for fixed and variable expenses
            bar_data = {'Fixed Expenses': total_fixed_expenses, 'Variable Expenses': total_variable_expenses}
            bar_fig = create_bar_chart(bar_data, "Fixed vs Variable Expenses")
            st.pyplot(bar_fig)
        else:
            st.warning("Total expenses must be greater than zero to calculate ratios.")

# Run the tool
if __name__ == "__main__":
    main()
