
## ADDED Requirements

### Requirement: Chat Context Construction

The system SHALL construct a rich context for the chat agent when a valid patient ID is provided.

#### Scenario: Comprehensive Data Inclusion
Given a user initiates a chat with a valid `patient_id`
When the system constructs the prompt context
Then it includes the patient's basic info, medical records, lab results, medications, diagnoses, assessments from the database
And it includes the patient's insulin usage data from the statistics Excel file
And the context is formatted clearly for the LLM to analyze.
