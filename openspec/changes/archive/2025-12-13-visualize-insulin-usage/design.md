# Design: Insulin Visualization System

## Backend Design
### API Endpoint
`GET /api/statistics/insulin`

**Response Format:**
```json
{
  "total_patients": 125,
  "insulin_users": 60,
  "usage_rate": 0.48,
  "distribution": {
    "male": {
      "total": 60,
      "users": 30,
      "rate": 0.5
    },
    "female": {
      "total": 65,
      "users": 30,
      "rate": 0.46
    }
  }
}
```

### Parsing Logic
-   Load `data/糖尿病病例统计.xlsx` using `pandas`.
-   Columns:
    -   `空腹胰岛素 (pmol/L)`
    -   `餐后2小时胰岛素 (pmol/L)`
    -   `性别 (Female=1, Male=2)`
-   **Insulin Use Condition**:
    -   `NOT (isna(空腹) AND isna(餐后))`

## Frontend Design
-   **Library**: Use `Chart.js` (if available via CDN) or simple HTML/CSS bars to avoid heavy dependencies if not already present. *Correction*: Project uses Vanilla CSS/JS mostly. Will check if `Chart.js` is already used or if I should use a lightweight solution. Given "UI style matches", I will use `Chart.js` via CDN for good aesthetics or simple CSS bars if preferred.
-   **Location**: Add a "Statistics" or "Insulin Analysis" card/link on the main dashboard (`index.html`).
-   **Visual**:
    -   A modal or a dedicated section showing the chart.
    -   Use colors from `index.css` (likely medical blue/greens).
