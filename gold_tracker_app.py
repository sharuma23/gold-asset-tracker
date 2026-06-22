# Gold Jewelry Break-Even Calculator
# Purpose:
# Compare a jewelry purchase price against:
# 1. the gold value on the purchase date,
# 2. the current gold value,
# 3. the jeweler premium/making fee,
# 4. and the inflation-adjusted break-even price.

# datasets
# https://fred.stlouisfed.org/series/CPIAUCSL
# https://datahub.io/core/gold-prices

import os
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


TROY_OUNCE_TO_GRAMS = 31.1034768


# Streamlit runs this script from top to bottom whenever the user changes an input.
# st.* commands create UI messages that Streamlit sends to the browser frontend.


def karat_to_purity(karat):
    """
    Convert a karat value into a gold purity decimal.

    Args:
        karat (int): Gold purity measured in karats. Example: 24, 22, 18, or 14.

    Returns:
        (float): Gold purity as a decimal. Example: 22K returns 0.9167.

    Raises:
        ValueError: If karat is not an integer or is outside the valid 1-24 range.
    """
    if type(karat) != int:
        raise ValueError("Karat must be an integer.")

    if karat <= 0 or karat > 24:
        raise ValueError("Karat must be between 1 and 24.")

    return karat / 24.0


def weight_to_grams(weight, unit):
    """
    Convert the user's selected weight unit into grams.

    Args:
        weight (int | float): Numeric weight entered by the user.
        unit (str): Weight unit selected by the user.

    Returns:
        (float): Weight converted into grams.

    Raises:
        ValueError: If weight is invalid or unit is unsupported.
    """
    if not isinstance(weight, (int, float)):
        raise ValueError("Weight must be a number.")

    if weight <= 0:
        raise ValueError("Weight must be greater than zero.")

    if type(unit) != str:
        raise ValueError("Weight unit must be text.")

    if unit == "grams":
        return weight

    if unit == "troy ounces":
        return weight * TROY_OUNCE_TO_GRAMS

    if unit == "regular ounces":
        return weight * 28.349523125

    raise ValueError("Unsupported weight unit.")


def get_value_on_or_before(df, selected_date, value_col):
    """
    Find the closest available value on or before a selected date.

    Args:
        df (DataFrame): Pandas DataFrame that contains a date column.
        selected_date (date): Date selected by the user.
        value_col (str): Name of the column we want to return.

    Returns:
        (float): The selected column value from the closest previous available date.

    Raises:
        ValueError: If the DataFrame has no earlier data.
    """
    selected_timestamp = pd.to_datetime(selected_date)

    # Keep only rows where the dataset date is less than or equal to the selected date.
    filtered = df[df["date"] <= selected_timestamp]

    if filtered.empty:
        raise ValueError("No data exists on or before the selected date.")

    # iloc[-1] means "give me the last row."
    # Since the DataFrame is sorted oldest to newest, this is the latest valid date.
    return float(filtered.iloc[-1][value_col])


def build_chart_data(gold_df, purchase_date, pure_gold_weight_grams):
    """
    Build a time-series DataFrame for charting.

    Args:
        gold_df (DataFrame): DataFrame containing gold prices over time.
        purchase_date (date): Date the jewelry was purchased.
        pure_gold_weight_grams (float): Pure gold weight in grams.

    Returns:
        (DataFrame): DataFrame with dates and calculated asset values.
    """
    start_date = pd.to_datetime(purchase_date)

    # Copy prevents Pandas warnings when we add a new calculated column.
    chart_df = gold_df[gold_df["date"] >= start_date].copy()

    # Calculate the asset's gold value on each date.
    chart_df["asset_gold_value"] = chart_df["gold_price_per_gram"] * pure_gold_weight_grams

    return chart_df


def plot_value_chart(chart_df, price_paid, inflation_adjusted_price_paid):
    """
    Draw a Matplotlib chart showing the asset value over time.

    Args:
        chart_df (DataFrame): DataFrame with date and asset_gold_value columns.
        price_paid (float): Original purchase price, used as the nominal break-even line.
        inflation_adjusted_price_paid (float): Inflation-adjusted cost, used as the real break-even line.

    Returns:
        (Figure): Matplotlib figure object that Streamlit can display.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(chart_df["date"], chart_df["asset_gold_value"], label="Gold value of asset")
    ax.axhline(price_paid, linestyle="--", label="Nominal break-even")
    ax.axhline(inflation_adjusted_price_paid, linestyle=":", label="Inflation-adjusted break-even")

    ax.set_title("Gold Asset Value Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value in dollars")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def show_intro():
    """
    Display the app title, motivation, and data-source explanation.

    Args:
        None.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.title("🟡 Gold Jewelry Break-Even Calculator")

    st.write(
        "This app started from a simple question: my friend bought gold earrings a few months ago, "
        "and we wanted to know whether the gold inside the earrings is now worth enough to break even."
    )

    st.info(
        "The included sample datasets are based on real historical gold and CPI data, not random demo values. "
        "Gold prices are expected in dollars per troy ounce and are converted to dollars per gram inside the app."
    )

    with st.expander("Project motivation"):
        st.write(
            "Gold jewelry is not priced only by the value of the gold. A jeweler may also charge for design, "
            "labor, store profit, brand value, taxes, and other costs. This means the buyer usually pays more "
            "than the melt value of the gold."
        )

        st.write("The goal of this app is to separate those ideas:")
        st.write("- How much was the actual gold worth on the purchase date?")
        st.write("- How much extra was paid above the raw gold value?")
        st.write("- What is the gold worth now?")
        st.write("- How much does gold need to rise for the buyer to break even?")
        st.write("- Did the gold beat inflation, or only rise in nominal dollars?")

    with st.expander("Data accuracy and sources"):
        st.write(
            "The included datasets are intended to be accurate historical datasets prepared for this app. "
            "The gold dataset should contain historical gold prices in dollars per troy ounce. "
            "The CPI dataset should contain Consumer Price Index values."
        )

        st.write(
            "Gold prices are commonly quoted per troy ounce, while jewelry weight is usually entered in grams."
        )

        st.code("gold_price_per_gram = gold_price_per_troy_ounce / 31.1034768")

        st.write(
            "CPI is used to estimate how much the original purchase price is worth in today's dollars."
        )

        st.code("inflation_adjusted_price = price_paid × current_CPI / purchase_CPI")

        st.link_button(
            "Open CPI source: FRED CPIAUCSL",
            "https://fred.stlouisfed.org/series/CPIAUCSL",
        )

        st.link_button(
            "Open gold source: DataHub",
            "https://datahub.io/core/gold-prices",
        )

def load_gold_and_cpi_data():
    """
    Load the included gold price data and CPI inflation data.

    Args:
        None.

    Returns:
        (tuple): Two sorted Pandas DataFrames: gold_df and cpi_df.

    Raises:
        ValueError: If required columns are missing or numeric data is invalid.
    """
    st.sidebar.header("CSV Data")

    app_folder = os.path.dirname(os.path.abspath(__file__))

    gold_path = os.path.join(app_folder, "sample_gold_prices.csv")
    cpi_path = os.path.join(app_folder, "sample_cpi.csv")

    st.sidebar.write("Using included sample datasets.")

    with st.sidebar.expander("Included CSV format"):
        st.write("Gold CSV format:")
        st.code(
            "Date,Price\n"
            "1833-01,18.93\n"
            "1833-02,18.93"
        )

        st.write("CPI CSV format:")
        st.code(
            "date,cpi\n"
            "1/1/47,21.48\n"
            "2/1/47,21.62"
        )

        st.write("Gold price is in dollars per troy ounce.")
        st.code("gold_price_per_gram = Price / 31.1034768")

    if not os.path.exists(gold_path):
        raise ValueError("sample_gold_prices.csv was not found in the app folder.")

    if not os.path.exists(cpi_path):
        raise ValueError("sample_cpi.csv was not found in the app folder.")

    with st.sidebar.expander("Open included CSV files"):
        with open(gold_path, "rb") as file:
            st.download_button(
                "Download / open gold CSV",
                data=file,
                file_name="sample_gold_prices.csv",
                mime="text/csv",
            )

        with open(cpi_path, "rb") as file:
            st.download_button(
                "Download / open CPI CSV",
                data=file,
                file_name="sample_cpi.csv",
                mime="text/csv",
            )

    gold_raw_df = pd.read_csv(gold_path)
    cpi_df = pd.read_csv(cpi_path)

    required_gold_columns = ["Date", "Price"]
    required_cpi_columns = ["date", "cpi"]

    for column in required_gold_columns:
        if column not in gold_raw_df.columns:
            raise ValueError("Gold CSV must contain Date and Price columns.")

    for column in required_cpi_columns:
        if column not in cpi_df.columns:
            raise ValueError("CPI CSV must contain date and cpi columns.")

    gold_df = pd.DataFrame()

    gold_df["date"] = pd.to_datetime(
        gold_raw_df["Date"],
        format="%Y-%m",
        errors="coerce",
    )

    gold_df["gold_price_per_troy_ounce"] = pd.to_numeric(
        gold_raw_df["Price"],
        errors="coerce",
    )

    gold_df["gold_price_per_gram"] = (
        gold_df["gold_price_per_troy_ounce"] / TROY_OUNCE_TO_GRAMS
    )

    cpi_df["date"] = pd.to_datetime(
        cpi_df["date"],
        format="%m/%d/%y",
        errors="coerce",
    )

    future_dates = cpi_df["date"].dt.year > date.today().year

    cpi_df.loc[future_dates, "date"] = cpi_df.loc[future_dates, "date"] - pd.DateOffset(years=100)

    cpi_df["cpi"] = pd.to_numeric(
        cpi_df["cpi"],
        errors="coerce",
    )

    gold_df = gold_df.dropna(subset=["date", "gold_price_per_troy_ounce"])
    cpi_df = cpi_df.dropna(subset=["date", "cpi"])

    if gold_df.empty:
        raise ValueError("No valid gold rows were found.")

    if cpi_df.empty:
        raise ValueError("No valid CPI rows were found.")

    if (gold_df["gold_price_per_troy_ounce"] <= 0).any():
        raise ValueError("Gold prices must be greater than zero.")

    if (cpi_df["cpi"] <= 0).any():
        raise ValueError("CPI values must be greater than zero.")

    gold_df = gold_df.sort_values("date", ascending=True)
    cpi_df = cpi_df.sort_values("date", ascending=True)

    return gold_df, cpi_df
        
def get_sidebar_inputs(gold_df, cpi_df):
    """
    Display sidebar inputs and collect user-entered asset details.

    Args:
        gold_df (DataFrame): Gold price DataFrame.
        cpi_df (DataFrame): CPI DataFrame.

    Returns:
        (dict): User input values from the sidebar.
    """
    min_date = max(gold_df["date"].min().date(), cpi_df["date"].min().date())
    max_date = min(gold_df["date"].max().date(), cpi_df["date"].max().date())

    st.sidebar.header("Asset Details")

    asset_name = st.sidebar.text_input("Asset name", value="Gold Earrings")

    default_purchase_date = min(max(date(2024, 1, 1), min_date), max_date)

    purchase_date = st.sidebar.date_input(
        "Purchase date",
        value=default_purchase_date,
        min_value=min_date,
        max_value=max_date,
    )

    price_paid = st.sidebar.number_input(
        "Total price paid ($)",
        min_value=0.01,
        value=1000.00,
        step=25.00,
    )

    weight_input = st.sidebar.number_input(
        "Weight",
        min_value=0.01,
        value=10.00,
        step=0.25,
    )

    weight_unit = st.sidebar.selectbox(
        "Weight unit",
        ["grams", "troy ounces", "regular ounces"],
    )

    karat = st.sidebar.selectbox(
        "Gold purity / karat",
        [24, 22, 21, 18, 14, 10],
    )

    uploaded_image = st.sidebar.file_uploader(
        "Optional asset image",
        type=["png", "jpg", "jpeg"],
    )

    return {
        "asset_name": asset_name,
        "purchase_date": purchase_date,
        "price_paid": price_paid,
        "weight_input": weight_input,
        "weight_unit": weight_unit,
        "karat": karat,
        "uploaded_image": uploaded_image,
    }


def calculate_results(gold_df, cpi_df, inputs):
    """
    Calculate all financial values used by the app.

    Args:
        gold_df (DataFrame): Gold price DataFrame.
        cpi_df (DataFrame): CPI DataFrame.
        inputs (dict): User input values from the sidebar.

    Returns:
        (dict): Calculated values used by the display functions.

    Raises:
        ValueError: If required data is missing or invalid.
    """
    purchase_date = inputs["purchase_date"]
    price_paid = inputs["price_paid"]
    weight_input = inputs["weight_input"]
    weight_unit = inputs["weight_unit"]
    karat = inputs["karat"]

    purchase_gold_price = get_value_on_or_before(
        gold_df,
        purchase_date,
        "gold_price_per_gram",
    )

    purchase_gold_price_troy_ounce = get_value_on_or_before(
        gold_df,
        purchase_date,
        "gold_price_per_troy_ounce",
    )

    current_gold_price = float(gold_df.iloc[-1]["gold_price_per_gram"])
    current_gold_price_troy_ounce = float(gold_df.iloc[-1]["gold_price_per_troy_ounce"])
    current_gold_date = gold_df.iloc[-1]["date"].date()

    purchase_cpi = get_value_on_or_before(
        cpi_df,
        purchase_date,
        "cpi",
    )

    current_cpi = float(cpi_df.iloc[-1]["cpi"])
    current_cpi_date = cpi_df.iloc[-1]["date"].date()

    purity = karat_to_purity(karat)
    gross_weight_grams = weight_to_grams(weight_input, weight_unit)
    pure_gold_weight_grams = gross_weight_grams * purity

    gold_value_at_purchase = pure_gold_weight_grams * purchase_gold_price
    jeweler_premium = price_paid - gold_value_at_purchase
    jeweler_premium_percent = (jeweler_premium / inputs['price_paid']) * 100

    current_gold_value = pure_gold_weight_grams * current_gold_price

    nominal_profit_loss = current_gold_value - price_paid
    nominal_profit_loss_percent = (nominal_profit_loss / price_paid) * 100

    inflation_adjusted_price_paid = price_paid * (current_cpi / purchase_cpi)

    real_profit_loss = current_gold_value - inflation_adjusted_price_paid
    real_profit_loss_percent = (real_profit_loss / inflation_adjusted_price_paid) * 100

    required_gold_price_nominal = price_paid / pure_gold_weight_grams
    required_gold_price_real = inflation_adjusted_price_paid / pure_gold_weight_grams

    gold_increase_needed_nominal_percent = (
        (required_gold_price_nominal - current_gold_price) / current_gold_price
    ) * 100

    gold_increase_needed_real_percent = (
        (required_gold_price_real - current_gold_price) / current_gold_price
    ) * 100

    return {
        "purchase_gold_price": purchase_gold_price,
        "purchase_gold_price_troy_ounce": purchase_gold_price_troy_ounce,
        "current_gold_price": current_gold_price,
        "current_gold_price_troy_ounce": current_gold_price_troy_ounce,
        "current_gold_date": current_gold_date,
        "purchase_cpi": purchase_cpi,
        "current_cpi": current_cpi,
        "current_cpi_date": current_cpi_date,
        "purity": purity,
        "gross_weight_grams": gross_weight_grams,
        "pure_gold_weight_grams": pure_gold_weight_grams,
        "gold_value_at_purchase": gold_value_at_purchase,
        "jeweler_premium": jeweler_premium,
        "jeweler_premium_percent": jeweler_premium_percent,
        "current_gold_value": current_gold_value,
        "nominal_profit_loss": nominal_profit_loss,
        "nominal_profit_loss_percent": nominal_profit_loss_percent,
        "inflation_adjusted_price_paid": inflation_adjusted_price_paid,
        "real_profit_loss": real_profit_loss,
        "real_profit_loss_percent": real_profit_loss_percent,
        "required_gold_price_nominal": required_gold_price_nominal,
        "required_gold_price_real": required_gold_price_real,
        "gold_increase_needed_nominal_percent": gold_increase_needed_nominal_percent,
        "gold_increase_needed_real_percent": gold_increase_needed_real_percent,
    }


def show_asset_summary(inputs, results):
    """
    Display the asset summary section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    overview_left, overview_right = st.columns([4, 1])

    with overview_left:
        st.header(inputs["asset_name"])

        st.subheader("Asset Summary")

        summary_cols = st.columns(4)

        summary_cols[0].metric(
            "Gross jewelry weight",
            f"{results['gross_weight_grams']:.2f} g",
            help="This is the total jewelry weight converted into grams.",
        )

        summary_cols[1].metric(
            "Gold purity",
            f"{inputs['karat']}K",
            f"{results['purity'] * 100:.2f}% pure",
            help="Karat measures how much of the jewelry is pure gold. 24K is treated as 100% pure gold.",
        )

        summary_cols[2].metric(
            "Pure gold weight",
            f"{results['pure_gold_weight_grams']:.2f} g",
            help="This is the estimated amount of actual pure gold inside the jewelry.",
        )

        summary_cols[3].metric(
            "Price paid",
            f"${inputs['price_paid']:,.2f}",
            help="This is how much you paid the jeweler for this gold."
        )

        with st.expander("How pure gold weight is calculated"):
            st.write(
                "Jewelry weight is not always the same as pure gold weight. "
                "For example, 22K gold is about 91.67% pure gold."
            )

            st.code(
                f"purity = karat / 24\n"
                f"purity = {inputs['karat']} / 24\n"
                f"purity = {results['purity']:.4f}"
            )

            st.code(
                f"pure_gold_weight = gross_weight × purity\n"
                f"pure_gold_weight = {results['gross_weight_grams']:.2f} × {results['purity']:.4f}\n"
                f"pure_gold_weight = {results['pure_gold_weight_grams']:.2f} grams"
            )

        with overview_right:
            app_folder = os.path.dirname(os.path.abspath(__file__))
            default_image_path = os.path.join(app_folder, "default_img.png")

            if inputs["uploaded_image"] is not None:
                st.image(
                    inputs["uploaded_image"],
                    caption=inputs["asset_name"],
                    use_container_width=True,
                )
            elif os.path.exists(default_image_path):
                st.image(
                    default_image_path,
                    caption="Default gold jewelry image",
                    use_container_width=True,
                )
            else:
                st.info("No asset image uploaded and default_img.png was not found.")


def show_value_breakdown(inputs, results):
    """
    Display the value breakdown section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header(f"Value Breakdown of ${inputs['price_paid']:,.2f}")

    metric_cols = st.columns(4)

    metric_cols[0].metric(
        "Gold value at purchase",
        f"${results['gold_value_at_purchase']:,.2f}",
        f"{(results['gold_value_at_purchase']/inputs['price_paid'])*100:.2f}% of price paid",
        help="Estimated melt value of the gold inside the jewelry on the purchase date.",
    )

    metric_cols[1].metric(
        "Jeweler premium",
        f"${results['jeweler_premium']:,.2f}",
        f"{results['jeweler_premium_percent']:.2f}% of price paid",
        help="The amount paid above the raw gold value on the purchase date.",
        delta_color="inverse",
    )

    metric_cols[2].metric(
        "Gold value today",
        f"${results['current_gold_value']:,.2f}",
        help="Estimated melt value of the same pure gold weight using the latest gold price in the CSV.",
    )

    metric_cols[3].metric(
        "Inflation-adjusted cost",
        f"${results['inflation_adjusted_price_paid']:.2f}",
        help="Your original purchase price converted into today's purchasing-power equivalent using CPI.",
    )

    with st.expander("Explain these value numbers"):
        st.subheader("Gold value at purchase")
        st.write(
            "This estimates what the gold inside the jewelry was worth on the purchase date. "
            "The source gold price starts as dollars per troy ounce, then the app converts it to dollars per gram."
        )

        st.code(
            f"purchase_gold_price_per_gram = purchase_gold_price_per_troy_ounce / 31.1034768\n"
            f"purchase_gold_price_per_gram = ${results['purchase_gold_price_troy_ounce']:,.2f} / 31.1034768\n"
            f"purchase_gold_price_per_gram = ${results['purchase_gold_price']:,.2f}/gram"
        )

        st.code(
            f"gold_value_at_purchase = pure_gold_weight × purchase_gold_price_per_gram\n"
            f"gold_value_at_purchase = {results['pure_gold_weight_grams']:.2f} × ${results['purchase_gold_price']:,.2f}\n"
            f"gold_value_at_purchase = ${results['gold_value_at_purchase']:,.2f}"
        )

        st.subheader("Jeweler premium")
        st.write(
            "This is the amount paid above the raw gold value. It can represent making charges, "
            "design markup, store profit, labor, and other non-gold costs."
        )

        st.code(
            f"jeweler_premium = price_paid - gold_value_at_purchase\n"
            f"jeweler_premium = ${inputs['price_paid']:,.2f} - ${results['gold_value_at_purchase']:,.2f}\n"
            f"jeweler_premium = ${results['jeweler_premium']:,.2f}"
        )

        st.subheader("Gold value today")
        st.write(
            "This estimates what the same amount of pure gold is worth using the latest gold price in the CSV."
        )

        st.code(
            f"current_gold_price_per_gram = current_gold_price_per_troy_ounce / 31.1034768\n"
            f"current_gold_price_per_gram = ${results['current_gold_price_troy_ounce']:,.2f} / 31.1034768\n"
            f"current_gold_price_per_gram = ${results['current_gold_price']:,.2f}/gram"
        )

        st.code(
            f"current_gold_value = pure_gold_weight × current_gold_price_per_gram\n"
            f"current_gold_value = {results['pure_gold_weight_grams']:.2f} × ${results['current_gold_price']:,.2f}\n"
            f"current_gold_value = ${results['current_gold_value']:,.2f}"
        )

        st.subheader("Inflation-adjusted cost")
        st.write(
            "This converts the original purchase price into today's dollars using CPI. "
            "It gives a purchasing-power baseline."
        )

        st.code(
            f"inflation_adjusted_cost = price_paid × current_CPI / purchase_CPI\n"
            f"inflation_adjusted_cost = ${inputs['price_paid']:,.2f} × {results['current_cpi']:.2f} / {results['purchase_cpi']:.2f}\n"
            f"inflation_adjusted_cost = ${results['inflation_adjusted_price_paid']:,.2f}"
        )


def show_cpi_explanation(inputs, results):
    """
    Display the CPI and inflation explanation section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Understanding CPI and Inflation Adjustment")

    st.write(
        "CPI stands for Consumer Price Index. It is an index that tracks how the general price level "
        "of common goods and services changes over time."
    )

    st.write(
        "CPI is not a dollar amount. It is an index number. If CPI rises, that means the general price level "
        "has increased, so each dollar usually buys less than before."
    )

    cpi_cols = st.columns(3)

    cpi_cols[0].metric(
        "Purchase-date CPI",
        f"{results['purchase_cpi']:.2f}",
        help="CPI value on or before the purchase date.",
    )

    cpi_cols[1].metric(
        "Latest CPI",
        f"{results['current_cpi']:.2f}",
        help="Latest CPI value available in the CSV.",
    )

    cpi_cols[2].metric(
        "Inflation multiplier",
        f"{results['current_cpi'] / results['purchase_cpi']:.4f}x",
        help="Current CPI divided by purchase-date CPI.",
    )

    with st.expander("Detailed CPI explanation"):
        st.write(
            "Imagine CPI as a rough measurement of the general cost of living. If CPI was 250 when you bought "
            "the earrings and CPI is 320 today, prices are generally higher today."
        )

        st.write("To compare old dollars to current dollars, the app uses this formula:")

        st.code("inflation_adjusted_price = price_paid × current_CPI / purchase_CPI")

        st.write("Using your current inputs:")

        st.code(
            f"inflation_adjusted_price = ${inputs['price_paid']:,.2f} × {results['current_cpi']:.2f} / {results['purchase_cpi']:.2f}\n"
            f"inflation_adjusted_price = ${results['inflation_adjusted_price_paid']:,.2f}"
        )

        st.write(
            f"This means paying \\${inputs['price_paid']:,.2f} on the purchase date is roughly like paying "
            f"\\${results['inflation_adjusted_price_paid']:,.2f} today, based on CPI."
        )

        st.write(
            "That is why the app shows two profit/loss numbers. The nominal result compares against the exact "
            "dollars paid. The inflation-adjusted result compares against the purchasing-power equivalent."
        )


def show_profit_loss(inputs, results):
    """
    Display the profit and loss section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Profit / Loss")

    profit_cols = st.columns(2)

    with profit_cols[0]:
        st.subheader("Nominal Result")

        if results["nominal_profit_loss"] >= 0:
            st.success(
                f"You are up ${results['nominal_profit_loss']:,.2f} "
                f"({results['nominal_profit_loss_percent']:.2f}%) before inflation."
            )
        else:
            st.error(
                f"You are down ${abs(results['nominal_profit_loss']):,.2f} "
                f"({results['nominal_profit_loss_percent']:.2f}%) before inflation."
            )

        st.write(
            "Nominal profit/loss answers this question: "
            "is the gold worth more dollars today than the exact amount paid?"
        )

        st.code(
            f"nominal_profit_loss = current_gold_value - price_paid\n"
            f"nominal_profit_loss = ${results['current_gold_value']:,.2f} - ${inputs['price_paid']:,.2f}\n"
            f"nominal_profit_loss = ${results['nominal_profit_loss']:,.2f}"
        )

    with profit_cols[1]:
        st.subheader("Inflation-Adjusted Result")

        if results["real_profit_loss"] >= 0:
            st.success(
                f"You are up ${results['real_profit_loss']:,.2f} "
                f"({results['real_profit_loss_percent']:.2f}%) after inflation adjustment."
            )
        else:
            st.error(
                f"You are down ${abs(results['real_profit_loss']):,.2f} "
                f"({results['real_profit_loss_percent']:.2f}%) after inflation adjustment."
            )

        st.write(
            "Inflation-adjusted profit/loss answers this question: "
            "did the gold beat the loss of purchasing power over time?"
        )

        st.code(
            f"real_profit_loss = current_gold_value - inflation_adjusted_cost\n"
            f"real_profit_loss = ${results['current_gold_value']:,.2f} - ${results['inflation_adjusted_price_paid']:,.2f}\n"
            f"real_profit_loss = ${results['real_profit_loss']:,.2f}"
        )

    with st.expander("Why show both nominal and inflation-adjusted results?"):
        st.write("Both results are useful, but they answer different questions.")

        st.write(
            "Nominal result checks whether the gold value today is greater than the exact number of dollars paid."
        )

        st.write(
            "Inflation-adjusted result checks whether the gold value today is greater than what the purchase price "
            "would be worth in today's dollars."
        )

        st.write(
            "Example: if someone paid \\$1,000 years ago, that \\$1,000 may be equivalent to "
            "\\$1,200 today after inflation. If the gold is worth \\$1,100 today, the buyer "
            "is up nominally but still down after inflation."
        )


def show_break_even(inputs, results):
    """
    Display the break-even analysis section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Break-Even Analysis")

    breakeven_cols = st.columns(2)

    breakeven_cols[0].metric(
        f"Nominal break-even gold price for \\${inputs['price_paid']:,.2f}",
        f"${results['required_gold_price_nominal']:,.2f}/gram",
        f"{results['gold_increase_needed_nominal_percent']:.2f}% from today",
        delta_color="inverse",
        help="Gold price per gram needed for the asset's melt value to equal what was paid.",
    )

    breakeven_cols[1].metric(
        f"Inflation-adjusted break-even gold price for \\${results['inflation_adjusted_price_paid']:,.2f}",
        f"${results['required_gold_price_real']:,.2f}/gram",
        f"{results['gold_increase_needed_real_percent']:.2f}% from today",
        delta_color="inverse",
        help="Gold price per gram needed for the asset's melt value to equal the inflation-adjusted cost.",
    )

    if results["gold_increase_needed_nominal_percent"] <= 0:
        st.success("You have already reached nominal break-even based on the latest gold price in the CSV.")
    else:
        st.warning(
            f"Gold needs to rise by about {results['gold_increase_needed_nominal_percent']:.2f}% "
            "from the latest CSV price to reach nominal break-even."
        )

    if results["gold_increase_needed_real_percent"] <= 0:
        st.success("You have already reached inflation-adjusted break-even.")
    else:
        st.warning(
            f"Gold needs to rise by about {results['gold_increase_needed_real_percent']:.2f}% "
            "from the latest CSV price to reach inflation-adjusted break-even."
        )

    with st.expander("What does break-even mean?"):
        st.write("Break-even means the estimated gold value equals the cost.")

        st.subheader("Nominal break-even")
        st.write(
            "This ignores inflation. It asks: what gold price would make the gold worth exactly what was paid?"
        )

        st.code(
            f"required_gold_price_nominal = price_paid / pure_gold_weight\n"
            f"required_gold_price_nominal = ${inputs['price_paid']:,.2f} / {results['pure_gold_weight_grams']:.2f}g\n"
            f"required_gold_price_nominal = ${results['required_gold_price_nominal']:,.2f}/g"
        )

        st.subheader("Inflation-adjusted break-even")
        st.write(
            "This includes inflation. It asks: what gold price would make the gold worth the purchasing-power "
            "equivalent of what was paid?"
        )

        st.code(
            f"required_gold_price_real = inflation_adjusted_cost / pure_gold_weight\n"
            f"required_gold_price_real = ${results['inflation_adjusted_price_paid']:,.2f} / {results['pure_gold_weight_grams']:.2f}g\n"
            f"required_gold_price_real = ${results['required_gold_price_real']:,.2f}/g"
        )

        st.subheader("Percent increase needed")
        st.write(
            "This tells you how much the latest gold price would need to rise to hit the break-even price."
        )

        st.code(
            "percent_needed = (required_gold_price - current_gold_price) / current_gold_price × 100"
        )


def show_scenarios(inputs, results):
    """
    Display the scenario analysis section.

    Args:
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Scenario Analysis")

    st.info(
        "This table shows what the gold value would look like if the latest gold price moved up or down. "
        "It is not a prediction. It is only a simple what-if analysis."
    )

    scenario_changes = np.array([-20, -10, -5, 0, 5, 10, 20, 30, 50])
    scenario_prices = results["current_gold_price"] * (1 + scenario_changes / 100)
    scenario_values = scenario_prices * results["pure_gold_weight_grams"]
    scenario_profit = scenario_values - inputs["price_paid"]
    scenario_real_profit = scenario_values - results["inflation_adjusted_price_paid"]

    scenario_df = pd.DataFrame(
        {
            "Gold price change": [f"{change:+.0f}%" for change in scenario_changes],
            "Gold price per gram": scenario_prices,
            "Asset gold value": scenario_values,
            "Nominal profit/loss": scenario_profit,
            "Real profit/loss": scenario_real_profit,
        }
    )

    st.dataframe(
        scenario_df.style.format(
            {
                "Gold price per gram": "${:,.2f}",
                "Asset gold value": "${:,.2f}",
                "Nominal profit/loss": "${:,.2f}",
                "Real profit/loss": "${:,.2f}"
            }
        ),
        use_container_width=True,
    )

    with st.expander("How the scenario table is calculated"):
        st.write(
            "The app takes the latest gold price in the CSV and applies simple percentage changes."
        )

        st.code(
            "scenario_gold_price = current_gold_price × (1 + percent_change / 100)\n"
            "scenario_asset_value = scenario_gold_price × pure_gold_weight"
        )


def show_chart(gold_df, inputs, results):
    """
    Display the gold value over time chart.

    Args:
        gold_df (DataFrame): Gold price DataFrame.
        inputs (dict): User input values from the sidebar.
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Gold Value Over Time")

    st.write(
        "The chart tracks the estimated melt value of the gold from the purchase date forward. "
        "The dashed line is the original purchase price. The dotted line is the inflation-adjusted break-even level."
    )

    chart_df = build_chart_data(
        gold_df,
        inputs["purchase_date"],
        results["pure_gold_weight_grams"],
    )

    if chart_df.empty:
        st.info("Not enough gold price data after the purchase date to draw a chart.")
    else:
        fig = plot_value_chart(
            chart_df,
            inputs["price_paid"],
            results["inflation_adjusted_price_paid"],
        )

        st.pyplot(fig)
        plt.close(fig)


def show_dataset_values(results):
    """
    Display the dataset values used in the calculation.

    Args:
        results (dict): Calculated values used by the app.

    Returns:
        (None): This function writes directly to the Streamlit page.
    """
    st.divider()

    st.header("Dataset Values Used")

    data_cols = st.columns(2)

    with data_cols[0]:
        st.subheader("Gold Prices")
        st.write(f"Purchase-date gold price: **${results['purchase_gold_price_troy_ounce']:,.2f}/troy oz**")
        st.write(f"Purchase-date gold price converted: **${results['purchase_gold_price']:,.2f}/gram**")
        st.write(f"Latest gold price: **${results['current_gold_price_troy_ounce']:,.2f}/troy oz**")
        st.write(f"Latest gold price converted: **${results['current_gold_price']:,.2f}/gram**")
        st.write(f"Latest gold date: **{results['current_gold_date']}**")

    with data_cols[1]:
        st.subheader("CPI Values")
        st.write(f"Purchase-date CPI: **{results['purchase_cpi']:.2f}**")
        st.write(f"Latest CPI: **{results['current_cpi']:.2f}**")
        st.write(f"Latest CPI date: **{results['current_cpi_date']}**")


def main():
    """
    Run the Streamlit app.

    Args:
        None.

    Returns:
        (None): This function builds and displays the Streamlit app.
    """
    st.set_page_config(
        page_title="Gold Asset Value Calculator",
        page_icon="🟡",
        layout="wide",
    )

    show_intro()

    try:
        gold_df, cpi_df = load_gold_and_cpi_data()
    except Exception as error:
        st.error(f"Could not load data: {error}")
        st.stop()

    inputs = get_sidebar_inputs(gold_df, cpi_df)

    try:
        results = calculate_results(gold_df, cpi_df, inputs)
    except Exception as error:
        st.error(f"Could not calculate metrics: {error}")
        st.stop()

    show_asset_summary(inputs, results)
    show_value_breakdown(inputs, results)
    show_cpi_explanation(inputs, results)
    show_profit_loss(inputs, results)
    show_break_even(inputs, results)
    show_scenarios(inputs, results)
    show_chart(gold_df, inputs, results)
    show_dataset_values(results)

    st.caption(
        "Note: This app estimates gold melt value only. It does not include resale discounts, "
        "brand value, gemstones, taxes, or transaction fees."
    )


if __name__ == "__main__":
    main()
