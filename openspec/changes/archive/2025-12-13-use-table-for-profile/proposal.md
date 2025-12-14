
# Proposal: Visualize Comprehensive Profile with Tables

## Goal
Replace the raw JSON data display in the "Comprehensive Profile" modal with user-friendly HTML tables. This will make it easier for medical staff to read patient history, lab results, and medication records.

## Changes
### Frontend
#### [MODIFY] [index.html](file:///Users/xiaoyubin/Desktop/mcpserversvip/rag-study/src/templates/index.html)
- Update `showComprehensive()` function to:
  - Parse the JSON response.
  - Generate HTML tables for:
    - Patient Information (Key-Value table)
    - Medical Records (List table)
    - Lab Results (List table)
    - Medications (List table)
    - Diagnoses (List table)
    - Risk Assessments (List table)
  - Apply styling to tables for better readability.

## Verification
### Manual Verification
1. Open the application.
2. Select a patient (e.g., input ID `1001_0_20210730`).
3. Click "查看综合档案" (View Comprehensive Profile).
4. Verify that the modal displays structured tables instead of a JSON code block.
