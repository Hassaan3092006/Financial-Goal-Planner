import streamlit as st


def format_money(value):
    return f"${value:,.2f}"


def months_to_goal(current, monthly, rate, target):
    balance = current
    monthly_rate = rate / 12
    months = 0
    while balance < target and months < 1200:
        balance = balance * (1 + monthly_rate) + monthly
        months += 1
    return months, balance


def required_monthly(current, rate, months, target):
    monthly_rate = rate / 12
    if months == 0:
        return 0.0
    if monthly_rate == 0:
        return max(0.0, (target - current) / months)
    factor = (1 + monthly_rate) ** months
    return max(0.0, (target - current * factor) * monthly_rate / (factor - 1))


def build_projection(current, monthly, rate, months):
    balance = current
    monthly_rate = rate / 12
    history = []
    for m in range(1, months + 1):
        balance = balance * (1 + monthly_rate) + monthly
        if m % 12 == 0 or m == months:
            history.append({"Period": f"Year {((m - 1) // 12) + 1}", "Balance": balance})
    return history


def main():
    st.set_page_config(page_title="Financial Goal Planner", layout="centered")
    st.title("Financial Goal Planner")
    st.write("Plan your savings goal with monthly contributions, target date, and expected return.")

    target = st.number_input("Goal amount", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
    current = st.number_input("Current savings", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
    annual_rate = st.number_input("Expected annual return rate (%)", min_value=0.0, value=5.0, step=0.1, format="%.2f") / 100
    mode = st.radio("Planner mode", ["Monthly savings", "Target date"], index=0)

    if mode == "Monthly savings":
        monthly = st.number_input("Monthly savings", min_value=0.0, value=300.0, step=10.0, format="%.2f")
    else:
        years = st.number_input("Goal horizon (years)", min_value=1, value=5, step=1)
        monthly = None

    if st.button("Plan goal"):
        if mode == "Monthly savings":
            months, projected = months_to_goal(current, monthly, annual_rate, target)
            years = months // 12
            extra_months = months % 12
            st.metric("Goal amount", format_money(target))
            st.metric("Projected balance", format_money(projected))

            if months >= 1200:
                st.warning("This goal may take too long. Increase your monthly savings or reduce the target.")
            else:
                st.write("### Goal plan")
                st.write(f"- Months to reach goal: {months}")
                st.write(f"- Which is: {years} years and {extra_months} months")
                st.write(f"- Total contributions: {format_money(current + monthly * months)}")

            horizon = min(months, 1200)
            projection = build_projection(current, monthly, annual_rate, horizon)
            st.line_chart({"Balance": [row["Balance"] for row in projection]})
            st.table(projection)
        else:
            months = years * 12
            monthly_needed = required_monthly(current, annual_rate, months, target)
            projected, projection = build_projection(current, monthly_needed, annual_rate, months)
            st.metric("Goal amount", format_money(target))
            st.metric("Required monthly savings", format_money(monthly_needed))
            st.metric("Projected balance", format_money(projected))

            st.write("### Goal plan")
            st.write(f"- Time horizon: {years} years")
            st.write(f"- Total contributions: {format_money(current + monthly_needed * months)}")
            st.write("- Monthly savings needed to meet the goal")
            st.line_chart({"Balance": [row["Balance"] for row in projection]})
            st.table(projection)

        st.write("### Notes")
        st.write(
            "This planner assumes fixed monthly savings and a constant annual return rate. "
            "Use this as an estimate and revisit it when your savings or goals change."
        )


if __name__ == "__main__":
    main()
