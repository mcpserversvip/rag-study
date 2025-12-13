# Spec: Clinical Statistics Reporting

## ADDED Requirements

### Requirement: Insulin Usage Calculation
The system MUST calculate insulin usage rates from the patient statistics file in real-time.

#### Scenario: Determine Insulin Use
A patient is considered to be using insulin if they have a recorded value for either Fasting Insulin or 2h Post-Prandial Insulin. If both are missing, they are considered non-users.

### Requirement: Data Visualization
The system MUST visualize insulin usage statistics grouped by gender on the user interface.

#### Scenario: View Statistics
The user can access a statistics view from the main menu that displays the proportion of insulin users among male and female patients.
