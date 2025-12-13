# Proposal: Visualize Insulin Usage

## Goal
Implement a real-time visualization of insulin usage rates based on the `data/糖尿病病例统计.xlsx` file, grouping data by gender.

## Context
The user wants to analyze the proportion of patients using insulin. The data source is an existing Excel file. The visualization should be integrated into the existing web application's index page.

## Plan
1.  **Backend**: Add an API endpoint `GET /api/statistics/insulin` that parses `data/糖尿病病例统计.xlsx`.
    -   Logic: A patient uses insulin if either "Fasting Insulin" or "2h Post-Prandial Insulin" has a value. If both are empty/NaN, they do not use insulin.
    -   Grouping: Group by Gender (1=Female, 2=Male).
2.  **Frontend**:
    -   Add a chart (e.g., Pie or Bar chart) to display the usage rate by gender.
    -   Add a menu entry on the Index page to access this visualization.
    -   Ensure the UI matches the existing style.

## Why
-   Provides valuable clinical insight into the patient population.
-   Leverages existing data without requiring database schema changes (reading directly from file as requested).
