
# Proposal: Enrich Patient Context

## Goal
Enrich the chat agent's context with comprehensive patient information when a `patient_id` is provided. This includes data from the MySQL database (medical records, lab results, etc.) and the Excel file (insulin usage statistics).

## Changes
### API
#### [MODIFY] [src/api/statistics.py](file:///Users/xiaoyubin/Desktop/mcpserversvip/rag-study/src/api/statistics.py)
- Add `get_patient_excel_data(patient_id)` function to retrieve a specific patient's row from `糖尿病病例统计.xlsx`.
- Ensure it handles missing data gracefully.

### App
#### [MODIFY] [src/app.py](file:///Users/xiaoyubin/Desktop/mcpserversvip/rag-study/src/app.py)
- Update `chat` endpoint:
  - When `patient_id` is present:
    - Call `medical_retriever.get_patient_comprehensive_data(patient_id)` to get DB data.
    - Call `statistics.get_patient_excel_data(patient_id)` to get Excel data.
    - Combine both into a structured JSON-like text block for the `patient_context`.

## Verification
### Manual Verification
1.  Start the application.
2.  Select a patient (e.g., `1001_0_20210730`).
3.  Ask a question that requires cross-referencing data (e.g., "这位患者目前的胰岛素使用情况如何？结合病历分析。").
4.  Verify the agent answers using details from both the DB (diagnoses) and Excel (insulin levels).
