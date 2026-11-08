# field_map.py — ISP-2519 Medical Report for CPP Disability Benefits
#
# Structure differs significantly from T2201:
#  - Sections 1-2: Patient fills (we still map them for completeness)
#  - Sections 3-9: Doctor fills — this is our primary target
#  - Section 5 repeats 3 times (pages 6, 7, 8) for up to 3 medical conditions
#  - Key fields are large narrative text boxes, not discrete yes/no dropdowns
#
# Radio button option codes decoded from PDF inspection:
#   rb_howManyYears:      /0=1yr or less, /1=1-2yrs, /2=3-4yrs, /3=5yrs or more
#   rb_prognosis:         /0=improve, /1=deteriorate, /2=remain the same, /3=unknown
#   rb_expectedDuration:  /0=less than 1yr, /1=more than 1yr
#   rb_frequency:         /0=recurrent/episodic, /1=continuous, /2=unknown
#   rb_Q1 (stop working): /0=yes, /1=no, /2=not discussed
#   rb_Q2 (return work):  /0=yes, /1=no, /2=unknown
#   rb_Q3 (when return):  /0=6-12mo, /1=12-24mo, /2=more than 24mo, /3=unknown
#   rb_Q4 (type of work): /0=usual, /1=modified, /2=another type needing training, /3=other
#   rb_Section10 (role):  /0=GP/CCFP, /1=other specialist, /2=nurse practitioner, /3=registered nurse

FIELD_MAP = {

    # ── Section 3: Duration of relationship ─────────────────────────────────
    "s3_years_in_care": {
        "field_id": "SC_ISP2519_E[0].page4[0].sub_Section3_borders[0].rb_howManyYears[0]",
        "type": "radio_group",
        "description": "How many years has this patient been in your care",
        "options": {"/0": "1 year or less", "/1": "1 to 2 years", "/2": "3 to 4 years", "/3": "5 years or more"},
    },
    "s3_visit_count_12mo": {
        "field_id": "SC_ISP2519_E[0].page4[0].sub_Section3_borders[0].txtF_numberOfTimes[0]",
        "type": "text",
        "description": "Number of times patient visited office in past 12 months",
    },
    "s3_last_visit_date": {
        "field_id": "SC_ISP2519_E[0].page4[0].sub_Section3_borders[0].df_dateOfLastVisit[0]",
        "type": "text",
        "description": "Date of last office visit (YYYY-MM-DD)",
    },
    "s3_first_treatment_date": {
        "field_id": "SC_ISP2519_E[0].page4[0].sub_Section3_borders[0].df_dateYouFirstStarted[0]",
        "type": "text",
        "description": "Date doctor first started treating patient's primary medical condition (YYYY-MM-DD)",
    },

    # ── Section 4: Terminal / Grave condition ────────────────────────────────
    "s4_terminal": {
        "field_id": "SC_ISP2519_E[0].page5[0].#subform[0].Yes[0]",
        "type": "checkbox",
        "description": "Patient has a TERMINAL condition (expected death within 6 months)",
        "checked_value": "/Yes",
    },
    "s4_terminal_diagnosis": {
        "field_id": "SC_ISP2519_E[0].page5[0].#subform[0].Table1[0].Row1[0].txtF_row1[0]",
        "type": "text",
        "description": "Terminal diagnosis name (only if s4_terminal is checked)",
    },
    "s4_terminal_icd_code": {
        "field_id": "SC_ISP2519_E[0].page5[0].#subform[0].Table1[0].Row1[0].txtF_ICDcode[0]",
        "type": "text",
        "description": "ICD-9-CM code for terminal condition (format XXX.X)",
    },
    "s4_terminal_onset": {
        "field_id": "SC_ISP2519_E[0].page5[0].#subform[0].Table1[0].Row1[0].df_row1[0]",
        "type": "text",
        "description": "Date of symptom onset for terminal condition (YYYY-MM)",
    },
    "s4_grave": {
        "field_id": "SC_ISP2519_E[0].page5[0].#subform[0].Yes[1]",
        "type": "checkbox",
        "description": "Patient has a GRAVE condition (from Annex A list of severe/rapidly progressive conditions)",
        "checked_value": "/Yes",
    },

    # ── Section 5 — Medical Condition 1 (page 6) ────────────────────────────
    "s5a_patient_height": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_patient_height[0]",
        "type": "text",
        "description": "Patient height in centimeters",
    },
    "s5a_patient_weight": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_patient_weight[0]",
        "type": "text",
        "description": "Patient weight in kilograms",
    },
    "s5a_condition": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_medicalCondition[0]",
        "type": "text",
        "description": "Primary medical condition name/diagnosis (greatest functional impact)",
    },
    "s5a_icd_code": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_ICDcode[0]",
        "type": "text",
        "description": "ICD-9-CM code for primary condition (format XXX.X)",
    },
    "s5a_onset_date": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].df_dateOfSymptomOnset[0]",
        "type": "text",
        "description": "Date of symptom onset for primary condition (YYYY-MM)",
    },
    "s5a_impairments": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_impairment[0]",
        "type": "text",
        "description": "Impairments for primary condition — list any loss/abnormality of psychological or anatomical structure/function",
    },
    "s5a_functional_limitations": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].txtF_functionalLimitations[0]",
        "type": "text",
        "description": "Functional limitations for primary condition — describe how impairments restrict activities and prevent substantially gainful work. This is the most important field for CPP eligibility.",
    },
    "s5a_prognosis": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].rb_prognosis[0]",
        "type": "radio_group",
        "description": "Prognosis for primary condition",
        "options": {"/0": "improve", "/1": "deteriorate", "/2": "remain the same", "/3": "unknown"},
    },
    "s5a_expected_duration": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].rb_expectedDuration[0]",
        "type": "radio_group",
        "description": "Expected duration of primary condition",
        "options": {"/0": "less than 1 year", "/1": "more than 1 year"},
    },
    "s5a_frequency": {
        "field_id": "SC_ISP2519_E[0].page6[0].sub_medicalConditions_1[0].rb_frequency[0]",
        "type": "radio_group",
        "description": "Frequency of primary condition",
        "options": {"/0": "recurrent/episodic", "/1": "continuous", "/2": "unknown"},
    },
    "s5a_med1_name": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_1[0].TextField1[0]", "type": "text", "description": "Medication 1 name, dosage and frequency (condition 1)"},
    "s5a_med1_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_1[0].DateField1[0]", "type": "text", "description": "Medication 1 start date YYYY-MM (condition 1)"},
    "s5a_med1_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_1[0].DateField4[0]", "type": "text", "description": "Medication 1 end date YYYY-MM (condition 1)"},
    "s5a_med1_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_1[0].TextField10[0]", "type": "text", "description": "Medication 1 response/efficacy/side effects (condition 1)"},
    "s5a_med2_name": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_2[0].TextField1[0]", "type": "text", "description": "Medication 2 name, dosage and frequency (condition 1)"},
    "s5a_med2_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_2[0].DateField6[0]", "type": "text", "description": "Medication 2 start date YYYY-MM (condition 1)"},
    "s5a_med2_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_2[0].DateField3[0]", "type": "text", "description": "Medication 2 end date YYYY-MM (condition 1)"},
    "s5a_med2_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_2[0].TextField9[0]", "type": "text", "description": "Medication 2 response (condition 1)"},
    "s5a_med3_name": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_3[0].TextField1[0]", "type": "text", "description": "Medication 3 name, dosage and frequency (condition 1)"},
    "s5a_med3_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_3[0].DateField5[0]", "type": "text", "description": "Medication 3 start date YYYY-MM (condition 1)"},
    "s5a_med3_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_3[0].DateField2[0]", "type": "text", "description": "Medication 3 end date YYYY-MM (condition 1)"},
    "s5a_med3_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_Medication[0].BR_3[0].TextField8[0]", "type": "text", "description": "Medication 3 response (condition 1)"},
    "s5a_tx1_type": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_1[0].TextField22[0]", "type": "text", "description": "Other treatment 1 type and frequency (condition 1)"},
    "s5a_tx1_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_1[0].DateField12[0]", "type": "text", "description": "Other treatment 1 start date YYYY-MM (condition 1)"},
    "s5a_tx1_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_1[0].DateField11[0]", "type": "text", "description": "Other treatment 1 end date YYYY-MM (condition 1)"},
    "s5a_tx1_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_1[0].TextField19[0]", "type": "text", "description": "Other treatment 1 response (condition 1)"},
    "s5a_tx2_type": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_2[0].TextField18[0]", "type": "text", "description": "Other treatment 2 type and frequency (condition 1)"},
    "s5a_tx2_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_2[0].DateField10[0]", "type": "text", "description": "Other treatment 2 start date YYYY-MM (condition 1)"},
    "s5a_tx2_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_2[0].DateField9[0]", "type": "text", "description": "Other treatment 2 end date YYYY-MM (condition 1)"},
    "s5a_tx2_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_2[0].TextField15[0]", "type": "text", "description": "Other treatment 2 response (condition 1)"},
    "s5a_tx3_type": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_3[0].TextField14[0]", "type": "text", "description": "Other treatment 3 type and frequency (condition 1)"},
    "s5a_tx3_start": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_3[0].DateField8[0]", "type": "text", "description": "Other treatment 3 start date YYYY-MM (condition 1)"},
    "s5a_tx3_end": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_3[0].DateField7[0]", "type": "text", "description": "Other treatment 3 end date YYYY-MM (condition 1)"},
    "s5a_tx3_response": {"field_id": "SC_ISP2519_E[0].page6[0].Table_type_frequency[0].BR_3[0].TextField11[0]", "type": "text", "description": "Other treatment 3 response (condition 1)"},

    # ── Section 5 — Medical Condition 2 (page 7) ────────────────────────────
    "s5b_condition": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].txtF_medicalCondition[0]", "type": "text", "description": "Second medical condition name/diagnosis (if applicable)"},
    "s5b_icd_code": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].txtF_ICDcode[0]", "type": "text", "description": "ICD-9-CM code for second condition (format XXX.X)"},
    "s5b_onset_date": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].df_dateOfSymptomOnset[0]", "type": "text", "description": "Symptom onset date for second condition (YYYY-MM)"},
    "s5b_impairments": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].txtF_impairment[0]", "type": "text", "description": "Impairments for second condition"},
    "s5b_functional_limitations": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].txtF_functionalLimitations[0]", "type": "text", "description": "Functional limitations for second condition — how does this prevent substantially gainful work"},
    "s5b_prognosis": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].rb_prognosis[0]", "type": "radio_group", "description": "Prognosis for second condition", "options": {"/0": "improve", "/1": "deteriorate", "/2": "remain the same", "/3": "unknown"}},
    "s5b_expected_duration": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].rb_expectedDuration[0]", "type": "radio_group", "description": "Expected duration of second condition", "options": {"/0": "less than 1 year", "/1": "more than 1 year"}},
    "s5b_frequency": {"field_id": "SC_ISP2519_E[0].page7[0].sub_medicalConditions_1[0].rb_frequency[0]", "type": "radio_group", "description": "Frequency of second condition", "options": {"/0": "recurrent/episodic", "/1": "continuous", "/2": "unknown"}},
    "s5b_med1_name": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_1[0].TextField1[0]", "type": "text", "description": "Medication 1 name, dosage and frequency (condition 2)"},
    "s5b_med1_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_1[0].DateField18[0]", "type": "text", "description": "Medication 1 start date YYYY-MM (condition 2)"},
    "s5b_med1_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_1[0].DateField17[0]", "type": "text", "description": "Medication 1 end date YYYY-MM (condition 2)"},
    "s5b_med1_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_1[0].TextField10[0]", "type": "text", "description": "Medication 1 response (condition 2)"},
    "s5b_med2_name": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_2[0].TextField1[0]", "type": "text", "description": "Medication 2 name, dosage and frequency (condition 2)"},
    "s5b_med2_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_2[0].DateField16[0]", "type": "text", "description": "Medication 2 start date YYYY-MM (condition 2)"},
    "s5b_med2_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_2[0].DateField15[0]", "type": "text", "description": "Medication 2 end date YYYY-MM (condition 2)"},
    "s5b_med2_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_2[0].TextField9[0]", "type": "text", "description": "Medication 2 response (condition 2)"},
    "s5b_med3_name": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_3[0].TextField1[0]", "type": "text", "description": "Medication 3 name, dosage and frequency (condition 2)"},
    "s5b_med3_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_3[0].DateField14[0]", "type": "text", "description": "Medication 3 start date YYYY-MM (condition 2)"},
    "s5b_med3_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_3[0].DateField13[0]", "type": "text", "description": "Medication 3 end date YYYY-MM (condition 2)"},
    "s5b_med3_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_Medication[0].BR_3[0].TextField8[0]", "type": "text", "description": "Medication 3 response (condition 2)"},
    "s5b_tx1_type": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_1[0].TextField22[0]", "type": "text", "description": "Other treatment 1 type and frequency (condition 2)"},
    "s5b_tx1_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_1[0].DateField24[0]", "type": "text", "description": "Other treatment 1 start date YYYY-MM (condition 2)"},
    "s5b_tx1_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_1[0].DateField23[0]", "type": "text", "description": "Other treatment 1 end date YYYY-MM (condition 2)"},
    "s5b_tx1_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_1[0].TextField19[0]", "type": "text", "description": "Other treatment 1 response (condition 2)"},
    "s5b_tx2_type": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_2[0].TextField18[0]", "type": "text", "description": "Other treatment 2 type and frequency (condition 2)"},
    "s5b_tx2_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_2[0].DateField22[0]", "type": "text", "description": "Other treatment 2 start date YYYY-MM (condition 2)"},
    "s5b_tx2_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_2[0].DateField21[0]", "type": "text", "description": "Other treatment 2 end date YYYY-MM (condition 2)"},
    "s5b_tx2_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_2[0].TextField15[0]", "type": "text", "description": "Other treatment 2 response (condition 2)"},
    "s5b_tx3_type": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_3[0].TextField14[0]", "type": "text", "description": "Other treatment 3 type and frequency (condition 2)"},
    "s5b_tx3_start": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_3[0].DateField20[0]", "type": "text", "description": "Other treatment 3 start date YYYY-MM (condition 2)"},
    "s5b_tx3_end": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_3[0].DateField19[0]", "type": "text", "description": "Other treatment 3 end date YYYY-MM (condition 2)"},
    "s5b_tx3_response": {"field_id": "SC_ISP2519_E[0].page7[0].Table_type_frequency[0].BR_3[0].TextField11[0]", "type": "text", "description": "Other treatment 3 response (condition 2)"},

    # ── Section 5 — Medical Condition 3 (page 8) ────────────────────────────
    "s5c_condition": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].txtF_medicalCondition[0]", "type": "text", "description": "Third medical condition name/diagnosis (if applicable)"},
    "s5c_icd_code": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].txtF_ICDcode[0]", "type": "text", "description": "ICD-9-CM code for third condition (format XXX.X)"},
    "s5c_onset_date": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].df_dateOfSymptomOnset[0]", "type": "text", "description": "Symptom onset date for third condition (YYYY-MM)"},
    "s5c_impairments": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].txtF_impairment[0]", "type": "text", "description": "Impairments for third condition"},
    "s5c_functional_limitations": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].txtF_functionalLimitations[0]", "type": "text", "description": "Functional limitations for third condition"},
    "s5c_prognosis": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].rb_prognosis[0]", "type": "radio_group", "description": "Prognosis for third condition", "options": {"/0": "improve", "/1": "deteriorate", "/2": "remain the same", "/3": "unknown"}},
    "s5c_expected_duration": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].rb_expectedDuration[0]", "type": "radio_group", "description": "Expected duration of third condition", "options": {"/0": "less than 1 year", "/1": "more than 1 year"}},
    "s5c_frequency": {"field_id": "SC_ISP2519_E[0].page8[0].sub_medicalConditions_1[0].rb_frequency[0]", "type": "radio_group", "description": "Frequency of third condition", "options": {"/0": "recurrent/episodic", "/1": "continuous", "/2": "unknown"}},
    "s5c_med1_name": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_1[0].TextField1[0]", "type": "text", "description": "Medication 1 name, dosage and frequency (condition 3)"},
    "s5c_med1_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_1[0].DateField30[0]", "type": "text", "description": "Medication 1 start date YYYY-MM (condition 3)"},
    "s5c_med1_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_1[0].DateField29[0]", "type": "text", "description": "Medication 1 end date YYYY-MM (condition 3)"},
    "s5c_med1_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_1[0].TextField10[0]", "type": "text", "description": "Medication 1 response (condition 3)"},
    "s5c_med2_name": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_2[0].TextField1[0]", "type": "text", "description": "Medication 2 name, dosage and frequency (condition 3)"},
    "s5c_med2_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_2[0].DateField28[0]", "type": "text", "description": "Medication 2 start date YYYY-MM (condition 3)"},
    "s5c_med2_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_2[0].DateField27[0]", "type": "text", "description": "Medication 2 end date YYYY-MM (condition 3)"},
    "s5c_med2_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_2[0].TextField9[0]", "type": "text", "description": "Medication 2 response (condition 3)"},
    "s5c_med3_name": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_3[0].TextField1[0]", "type": "text", "description": "Medication 3 name, dosage and frequency (condition 3)"},
    "s5c_med3_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_3[0].DateField26[0]", "type": "text", "description": "Medication 3 start date YYYY-MM (condition 3)"},
    "s5c_med3_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_3[0].DateField25[0]", "type": "text", "description": "Medication 3 end date YYYY-MM (condition 3)"},
    "s5c_med3_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_Medication[0].BR_3[0].TextField8[0]", "type": "text", "description": "Medication 3 response (condition 3)"},
    "s5c_tx1_type": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_1[0].TextField22[0]", "type": "text", "description": "Other treatment 1 type and frequency (condition 3)"},
    "s5c_tx1_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_1[0].DateField36[0]", "type": "text", "description": "Other treatment 1 start date YYYY-MM (condition 3)"},
    "s5c_tx1_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_1[0].DateField35[0]", "type": "text", "description": "Other treatment 1 end date YYYY-MM (condition 3)"},
    "s5c_tx1_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_1[0].TextField19[0]", "type": "text", "description": "Other treatment 1 response (condition 3)"},
    "s5c_tx2_type": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_2[0].TextField18[0]", "type": "text", "description": "Other treatment 2 type and frequency (condition 3)"},
    "s5c_tx2_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_2[0].DateField34[0]", "type": "text", "description": "Other treatment 2 start date YYYY-MM (condition 3)"},
    "s5c_tx2_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_2[0].DateField33[0]", "type": "text", "description": "Other treatment 2 end date YYYY-MM (condition 3)"},
    "s5c_tx2_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_2[0].TextField15[0]", "type": "text", "description": "Other treatment 2 response (condition 3)"},
    "s5c_tx3_type": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_3[0].TextField14[0]", "type": "text", "description": "Other treatment 3 type and frequency (condition 3)"},
    "s5c_tx3_start": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_3[0].DateField32[0]", "type": "text", "description": "Other treatment 3 start date YYYY-MM (condition 3)"},
    "s5c_tx3_end": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_3[0].DateField31[0]", "type": "text", "description": "Other treatment 3 end date YYYY-MM (condition 3)"},
    "s5c_tx3_response": {"field_id": "SC_ISP2519_E[0].page8[0].Table_type_frequency[0].BR_3[0].TextField11[0]", "type": "text", "description": "Other treatment 3 response (condition 3)"},

    # ── Section 6: Employment situation ─────────────────────────────────────
    "s6_q1_stop_working": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].rb_Q1[0]",
        "type": "radio_group",
        "description": "Did you recommend patient stop working",
        "options": {"/0": "Yes (provide date)", "/1": "No", "/2": "Not discussed"},
    },
    "s6_q1_stop_date": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].df_DOB[0]",
        "type": "text",
        "description": "Date doctor recommended patient stop working (YYYY-MM-DD) — only if s6_q1 is Yes",
    },
    "s6_q2_return_to_work": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].rb_Q2[0]",
        "type": "radio_group",
        "description": "Do you expect patient to return to any type of work in the future",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unknown"},
    },
    "s6_q3_when_return": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].rb_Q3[0]",
        "type": "radio_group",
        "description": "When expected to return to work — only fill if s6_q2 is Yes",
        "options": {"/0": "In 6 to 12 months", "/1": "In 12 to 24 months", "/2": "In more than 24 months", "/3": "Unknown"},
    },
    "s6_q4_work_type": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].rb_Q4[0]",
        "type": "radio_group",
        "description": "Type of work expected to return to — only fill if s6_q2 is Yes",
        "options": {"/0": "Usual work", "/1": "Modified work", "/2": "Another type requiring training", "/3": "Other"},
    },
    "s6_q4_work_type_other": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section7[0].txtF_otherQ4[0]",
        "type": "text",
        "description": "Other work type description — only if s6_q4 is Other",
    },

    # ── Section 7: Other relevant information ───────────────────────────────
    "s7_other_info": {
        "field_id": "SC_ISP2519_E[0].page9[0].sub_Section8[0].txtF_otherRelevantInformation[0]",
        "type": "text",
        "description": "Other relevant information — planned investigations, specialist consultations, reason for unknown prognosis, additional context supporting disability claim",
    },

    # ── Section 8: Supporting documents ─────────────────────────────────────
    "s8_clinical_notes": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].#subform[0].medicalInvestigation[0]", "type": "checkbox", "description": "Including longitudinal clinical notes", "checked_value": "/Yes"},
    "s8_investigation_reports": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].#subform[0].medicalInvestigation[1]", "type": "checkbox", "description": "Including medical investigation reports", "checked_value": "/Yes"},
    "s8_specialist_reports": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].#subform[0].specialistsReports[0]", "type": "checkbox", "description": "Including specialist reports", "checked_value": "/Yes"},
    "s8_hospital_discharge": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].#subform[0].hospitalDischarge[0]", "type": "checkbox", "description": "Including hospital discharge reports", "checked_value": "/Yes"},
    "s8_other_docs": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].#subform[0].other[0]", "type": "checkbox", "description": "Including other supporting documents", "checked_value": "/Yes"},
    "s8_other_docs_description": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section9[0].txtF_other[0]", "type": "text", "description": "Description of other supporting documents"},

    # ── Section 9: Declaration ───────────────────────────────────────────────
    "s9_practitioner_role": {
        "field_id": "SC_ISP2519_E[0].page10[0].sub_Section10[0].rb_Section10[0]",
        "type": "radio_group",
        "description": "Practitioner role/designation",
        "options": {
            "/0": "General practice physician or physician certified in family medicine (CCFP)",
            "/1": "Other physician specialist",
            "/2": "Nurse practitioner",
            "/3": "Registered nurse in geographically isolated community",
        },
    },
    "s9_specialist_type": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section10[0].txtF_other[0]", "type": "text", "description": "Specialist type — only if s9_practitioner_role is other specialist"},
    "s9_practitioner_name": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section10_part2[0].txtF_name[0]", "type": "text", "description": "Practitioner name (print)"},
    "s9_practitioner_address": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section10_part2[0].sub_mailing_address[0].txtF_Signature[0]", "type": "text", "description": "Practitioner address and telephone number"},
    "s9_signature": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section10_part2[0].txtF_Signature[0]", "type": "text", "description": "Practitioner signature (typed name)"},
    "s9_date": {"field_id": "SC_ISP2519_E[0].page10[0].sub_Section10_part2[0].txtF_DOB[0]", "type": "text", "description": "Date of declaration (YYYY-MM-DD)"},
}

# ── Section groupings for extract.py ────────────────────────────────────────
SECTIONS = {
    "relationship":   {k: v for k, v in FIELD_MAP.items() if k.startswith("s3_")},
    "terminal_grave": {k: v for k, v in FIELD_MAP.items() if k.startswith("s4_")},
    "condition_1":    {k: v for k, v in FIELD_MAP.items() if k.startswith("s5a_")},
    "condition_2":    {k: v for k, v in FIELD_MAP.items() if k.startswith("s5b_")},
    "condition_3":    {k: v for k, v in FIELD_MAP.items() if k.startswith("s5c_")},
    "employment":     {k: v for k, v in FIELD_MAP.items() if k.startswith("s6_")},
    "other_info":     {k: v for k, v in FIELD_MAP.items() if k.startswith("s7_")},
    "documents":      {k: v for k, v in FIELD_MAP.items() if k.startswith("s8_")},
    "declaration":    {k: v for k, v in FIELD_MAP.items() if k.startswith("s9_")},
}

# ── Mandatory fields (Service Canada will reject without these) ──────────────
MANDATORY_FIELDS = {
    "s3_years_in_care",
    "s5a_condition",
    "s5a_icd_code",
    "s5a_onset_date",
    "s5a_impairments",
    "s5a_functional_limitations",
    "s5a_prognosis",
    "s5a_expected_duration",
    "s5a_frequency",
    "s6_q1_stop_working",
    "s6_q2_return_to_work",
    "s9_practitioner_role",
    "s9_practitioner_name",
    "s9_date",
}