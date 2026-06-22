# Gold Jewelry Break-Even Calculator

## Team Member

Shivansh Sharma

## Project Overview

The **Gold Jewelry Break-Even Calculator** is an interactive Python application that estimates whether a gold jewelry purchase has reached its financial break-even point. The project was motivated by a real situation: a friend bought gold earrings a few months ago, and we wanted to know whether the gold inside the earrings had increased enough in value to offset the original purchase price.

Gold jewelry is not priced only by the value of the gold. A buyer may also pay for design, labor, store markup, brand value, and other non-gold costs. This app separates those pieces by estimating the raw gold value of the jewelry, the jeweler premium paid above melt value, the current gold value, and both nominal and inflation-adjusted profit or loss.

The app uses **Streamlit** as the interactive application framework, with instructor permission, and also integrates **Pandas**, **NumPy**, and **Matplotlib**.

## Application Functionality

The user enters details about one gold jewelry item:

- Asset name
- Purchase date
- Price paid
- Weight
- Weight unit
- Gold purity in karats
- Optional image of the jewelry

The app then calculates:

- Gross jewelry weight in grams
- Pure gold weight
- Gold value at the purchase date
- Jeweler premium
- Current gold value
- Nominal profit or loss
- Inflation-adjusted cost
- Inflation-adjusted profit or loss
- Nominal break-even gold price
- Inflation-adjusted break-even gold price
- Scenario analysis for possible gold price movements

The app also includes explanatory sections so the user can understand what each number means. This includes explanations of gold purity, troy-ounce conversion, CPI, inflation adjustment, nominal profit, real profit, and break-even analysis.

## Dataset Explanation

The app uses two included CSV datasets.

### Gold Price Dataset

The gold price dataset is stored in `sample_gold_prices.csv`.

Expected columns:

```csv
Date,Price
1833-01,18.93
1833-02,18.93
```

The `Date` column stores the month and year. The `Price` column stores the gold price in **U.S. dollars per troy ounce**. Since jewelry weight is usually entered in grams, the app converts the gold price from dollars per troy ounce into dollars per gram.

Formula:

```text
gold_price_per_gram = gold_price_per_troy_ounce / 31.1034768
```

The gold price dataset source used for this project is:

```text
https://datahub.io/core/gold-prices
```

### CPI Dataset

The CPI dataset is stored in `sample_cpi.csv`.

Expected columns:

```csv
date,cpi
1/1/47,21.48
2/1/47,21.62
```

The CPI dataset contains Consumer Price Index values. CPI is used to estimate how much the original purchase price is worth in today’s dollars. The app uses CPI to compare nominal profit against inflation-adjusted profit.

Formula:

```text
inflation_adjusted_price = price_paid × current_CPI / purchase_CPI
```

The CPI dataset source used for this project is:

```text
https://fred.stlouisfed.org/series/CPIAUCSL
```

## Main Calculations

The app first converts karat purity into a decimal.

```text
purity = karat / 24
```

For example, 22K gold is:

```text
22 / 24 = 0.9167
```

Then it estimates the amount of pure gold inside the jewelry.

```text
pure_gold_weight = gross_weight_grams × purity
```

The app then calculates the gold value at the purchase date.

```text
gold_value_at_purchase = pure_gold_weight × purchase_gold_price_per_gram
```

The jeweler premium is the difference between what the user paid and the estimated raw gold value on the purchase date.

```text
jeweler_premium = price_paid - gold_value_at_purchase
```

The current gold value is calculated using the latest gold price in the dataset.

```text
current_gold_value = pure_gold_weight × current_gold_price_per_gram
```

Nominal profit or loss compares today’s gold value to the exact number of dollars paid.

```text
nominal_profit_loss = current_gold_value - price_paid
```

Inflation-adjusted profit or loss compares today’s gold value to the original price adjusted into today’s purchasing power.

```text
real_profit_loss = current_gold_value - inflation_adjusted_price_paid
```

The app also calculates the gold price needed to break even.

```text
required_gold_price_nominal = price_paid / pure_gold_weight
required_gold_price_real = inflation_adjusted_price_paid / pure_gold_weight
```

## Use of Required Python Libraries

### Pandas

Pandas is used to load and clean the CSV datasets. The app uses Pandas to parse dates, convert price and CPI columns into numeric values, remove invalid rows, sort data by date, and look up the closest available value on or before the selected purchase date.

### NumPy

NumPy is used in the scenario analysis section. The app creates an array of possible gold price percentage changes, such as -20%, -10%, 0%, +10%, and +50%. It then calculates the possible asset values and profit/loss outcomes for each scenario.

### Matplotlib

Matplotlib is used to generate a line chart showing how the estimated gold value of the jewelry changes over time. The chart also includes break-even reference lines for the original purchase price and the inflation-adjusted purchase price.

### Streamlit

Streamlit is used to create the interactive application interface. It provides sidebar inputs, metric cards, expanders, tables, chart display, file download buttons, and interactive reruns whenever the user changes an input.

## Creative Mechanics and User Experience

The app is designed to be more than a simple calculator. It works like a small financial dashboard for a personal jewelry purchase. Its creative features include:

- A real-world motivation based on a friend’s gold earrings
- Personal asset inputs
- Optional jewelry image display
- Default image support
- Historical gold and CPI datasets
- Explanations for each financial number
- CPI and inflation education inside the app
- Nominal and inflation-adjusted profit comparison
- Break-even analysis
- Scenario analysis table
- Matplotlib chart of gold value over time

These features make the app interactive, educational, and practical.

## Challenges Faced and Solutions

One challenge was handling different date formats in the datasets. The gold dataset uses year-month dates such as `1833-01`, while the CPI dataset uses dates such as `1/1/47`. The app solves this by parsing the gold dates with the `%Y-%m` format and the CPI dates with the `%m/%d/%y` format.

Another challenge was the two-digit CPI year format. Pandas may interpret dates such as `1/1/47` as 2047 instead of 1947. To fix this, the app checks for CPI dates that are in the future and subtracts 100 years from those dates.

A third challenge was making the inflation adjustment understandable. The formula is mathematically simple, but users may not know what CPI means. The app solves this by including a full explanation of CPI and by showing the exact calculation used for the selected purchase.

Another challenge was keeping the code organized. The original `main()` function became too large because it contained both UI code and calculation logic. The final version was refactored into smaller functions such as `load_gold_and_cpi_data()`, `calculate_results()`, `show_value_breakdown()`, `show_cpi_explanation()`, and `show_scenarios()`. This makes the code easier to read, debug, and explain during the project interview.

## Team Member Contributions

### Shivansh Sharma

- Designed the project idea and real-world use case
- Created the Streamlit app interface
- Added sidebar inputs for jewelry details
- Integrated the gold and CPI datasets
- Implemented Pandas data loading, date parsing, and data cleaning
- Implemented gold purity, weight conversion, and melt-value calculations
- Implemented CPI-based inflation adjustment
- Added NumPy-based scenario analysis
- Added Matplotlib chart visualization
- Refactored the code into smaller functions
- Tested the app with sample gold jewelry inputs
- Prepared the final report and project explanation

## Generative AI Use

Generative AI was used as a helper for brainstorming, debugging, refactoring, and improving explanations. The final code was reviewed and edited to make sure the logic is understood. The project interview preparation focuses on being able to explain the code, the formulas, the dataset structure, and the purpose of each major function.

## Conclusion

The Gold Jewelry Break-Even Calculator is a practical Python application that combines real historical data, financial logic, and an interactive interface. It helps users understand whether a gold jewelry purchase has gained enough value to break even, both before and after inflation. The project demonstrates data loading with Pandas, numerical analysis with NumPy, visualization with Matplotlib, and a polished user interface with Streamlit.
