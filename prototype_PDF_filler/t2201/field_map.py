"""
T2201 Part B — Complete field map.
Each entry: (field_id, description, type, options)

Radio options: '/0' = Yes (first option), '/1' = No (second option)
  EXCEPT where noted. Always check the form text to confirm ordering.

Checkbox checked values: '/1', '/2', '/3' for mutually-exclusive sets
  (e.g. "Yes / No / Unsure" improvement questions use checkboxes not radios)

Choice fields: use the exact option text string as the value.
"""

# ── Shared pattern across most impairment sections ──────────────────────────
# Q5 radio: Yes=/0, No=/1
# Q6 radio (all or substantially all): Yes=/0, No=/1
# Q8 radio (lasted 12 months): Yes=/0, No=/1
# Q9 checkboxes (improved/likely to improve):
#   [0] checked=/1  → Yes (provide year)
#   [1] checked=/2  → No
#   [2] checked=/3  → Unsure

FIELD_MAP = {

    # ════════════════════════════════════════════════════════════
    # PAGE 4 — VISION
    # ════════════════════════════════════════════════════════════
    "vision_patient_name": {
        "field_id": "form1[0].Page4_Vision[0].PatientName[0]",
        "type": "text",
        "description": "Patient's full name (repeated on each page)"
    },
    "vision_doctor_initial": {
        "field_id": "form1[0].Page4_Vision[0].Initial_sf[0].Vision_Doctor[0]",
        "type": "text",
        "description": "Medical doctor's initials (if applicable)"
    },
    "vision_nurse_initial": {
        "field_id": "form1[0].Page4_Vision[0].Initial_sf[0].Vision_Nurse[0]",
        "type": "text",
        "description": "Nurse practitioner's initials (if applicable)"
    },
    "vision_optometrist_initial": {
        "field_id": "form1[0].Page4_Vision[0].Initial_sf[0].Vision_Opto[0]",
        "type": "text",
        "description": "Optometrist's initials (if applicable)"
    },
    "vision_q1_conditions": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q1_sf[0].Details_sf[0].Vision_Q1_details[0]",
        "type": "text",
        "description": "Q1: Medical conditions/diagnoses impairing vision, with year of diagnosis"
    },
    # Q2 — Left eye checkboxes (check ONE of these)
    "vision_q2_left_snellen": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Vision_Q2_Measure_LeftCheckBox1[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Left eye: Visual acuity measurable on Snellen chart"
    },
    "vision_q2_left_acuity_num1": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Acuity_sf[0].Vision_Q2_Left_Numeric1[0]",
        "type": "text",
        "description": "Q2 Left eye Snellen acuity numerator (e.g. 20)"
    },
    "vision_q2_left_acuity_num2": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Acuity_sf[0].Vision_Q2_Left_Numeric2[0]",
        "type": "text",
        "description": "Q2 Left eye Snellen acuity denominator (e.g. 200)"
    },
    "vision_q2_left_count_fingers": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Vision_Q2_Measure_LeftCheckBox2[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Left eye: Count fingers (CF)"
    },
    "vision_q2_left_no_light": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Vision_Q2_Measure_LeftCheckBox3[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Left eye: No light perception (NLP)"
    },
    "vision_q2_left_light_perception": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Vision_Q2_Measure_LeftCheckBox4[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Left eye: Light perception (LP)"
    },
    "vision_q2_left_hand_motion": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Measure_sf[0].Vision_Q2_Measure_LeftCheckBox5[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Left eye: Hand motion (HM)"
    },
    "vision_q2_left_field_degrees": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Left_sf[0].Vision_Q2_Left_Numeric3[0]",
        "type": "text",
        "description": "Q2 Left eye: Field of vision greatest diameter in degrees"
    },
    # Q2 — Right eye checkboxes (mirror of left)
    "vision_q2_right_snellen": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Vision_Q2_Measure_RightCheckBox1[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Right eye: Visual acuity measurable on Snellen chart"
    },
    "vision_q2_right_acuity_num1": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Acuity_sf[0].Vision_Q2_Right_Numeric1[0]",
        "type": "text",
        "description": "Q2 Right eye Snellen acuity numerator"
    },
    "vision_q2_right_acuity_num2": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Acuity_sf[0].Vision_Q2_Right_Numeric2[0]",
        "type": "text",
        "description": "Q2 Right eye Snellen acuity denominator"
    },
    "vision_q2_right_count_fingers": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Vision_Q2_Measure_RightCheckBox2[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Right eye: Count fingers (CF)"
    },
    "vision_q2_right_no_light": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Vision_Q2_Measure_RightCheckBox3[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Right eye: No light perception (NLP)"
    },
    "vision_q2_right_light_perception": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Vision_Q2_Measure_RightCheckBox4[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Right eye: Light perception (LP)"
    },
    "vision_q2_right_hand_motion": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Measure_sf[0].Vision_Q1_Measure_RightCheckBox5[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q2 Right eye: Hand motion (HM)"
    },
    "vision_q2_right_field_degrees": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q2_sf[0].Eyes_sf[0].Right_sf[0].Vision_Q2_Right_Numeric3[0]",
        "type": "text",
        "description": "Q2 Right eye: Field of vision greatest diameter in degrees"
    },
    "vision_q3_meets_criteria": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q3_sf[0].Vision_Q3_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - meets criteria (acuity 20/200 or less, or field 20 degrees or less) in both eyes", "/1": "No"},
        "description": "Q3: Does patient meet vision criteria in both eyes?"
    },
    "vision_q4_year_impaired": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q4_sf[0].Year_sf[0].Vision_Q4_Year1[0]",
        "type": "text",
        "description": "Q4: Year patient became impaired in vision (4-digit year)"
    },
    "vision_q5_lasted_12mo": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q5_sf[0].Vision_Q5_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - lasted or expected to last 12+ months", "/1": "No"},
        "description": "Q5: Has vision impairment lasted or expected to last 12+ months?"
    },
    "vision_q6_improved_yes": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q6_sf[0].VisionQ6_checkbox_sf[0].VisionQ6_check1[0]",
        "type": "checkbox", "checked_value": "/1",
        "description": "Q6: Yes - vision has improved or likely to improve (check this OR No OR Unsure)"
    },
    "vision_q6_improved_no": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q6_sf[0].VisionQ6_checkbox_sf[0].VisionQ6_check1[1]",
        "type": "checkbox", "checked_value": "/2",
        "description": "Q6: No - vision has not improved"
    },
    "vision_q6_improved_unsure": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q6_sf[0].VisionQ6_checkbox_sf[0].VisionQ6_check1[2]",
        "type": "checkbox", "checked_value": "/3",
        "description": "Q6: Unsure - whether vision will improve"
    },
    "vision_q6_year": {
        "field_id": "form1[0].Page4_Vision[0].Vision_sf[0].Vision_Q6_sf[0].VisionQ6_checkbox_sf[0].Year_sf[0].Vision_Q6_Year[0]",
        "type": "text",
        "description": "Q6: Year vision improvement expected (only if Q6=Yes)"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 5 — SPEAKING
    # ════════════════════════════════════════════════════════════
    "speaking_patient_name": {
        "field_id": "form1[0].Page5_Speaking[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 5)"
    },
    "speaking_doctor_initial": {
        "field_id": "form1[0].Page5_Speaking[0].Initial_sf[0].Speaking_Doctor[0]",
        "type": "text", "description": "Doctor initials for speaking section"
    },
    "speaking_nurse_initial": {
        "field_id": "form1[0].Page5_Speaking[0].Initial_sf[0].Speaking_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials for speaking section"
    },
    "speaking_pathologist_initial": {
        "field_id": "form1[0].Page5_Speaking[0].Initial_sf[0].Speaking_Patho[0]",
        "type": "text", "description": "Speech-language pathologist initials"
    },
    "speaking_q1_conditions": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q1_sf[0].Details_sf[0].SpeakingQ1[0].Speaking_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing speaking, with year of diagnosis"
    },
    "speaking_q2_takes_medication": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q2_sf[0].Speaking_Q2_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Does patient take medication for speaking impairment?"
    },
    "speaking_q3_devices_therapy": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q3_sf[0].Details_sf[0].SpeakingQ3[0].Speaking_Q3_details[0]",
        "type": "text", "description": "Q3: Devices or therapy used for speaking (e.g. voice amplifier)"
    },
    "speaking_q4_examples": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q4_sf[0].Q4Details_sf[0].Q4[0].Speaking_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of how speaking is impaired despite therapy/devices"
    },
    "speaking_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q5_sf[0].Speaking_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - unable or takes inordinate time (3x longer)", "/1": "No"},
        "description": "Q5: Is patient unable to speak or takes inordinate time?"
    },
    "speaking_q6_all_or_substantially": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q6_sf[0].Speaking_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: Is this the case all or substantially all of the time?"
    },
    "speaking_q7_year_impaired": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year patient became impaired in speaking"
    },
    "speaking_q8_lasted_12mo": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q8_sf[0].Speaking_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Has speaking impairment lasted or expected to last 12+ months?"
    },
    "speaking_q9_improved_yes": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q9_sf[0].Speaking_Q9_checkbox_sf[0].Speaking_Q9_check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - speaking likely to improve (provide year)"
    },
    "speaking_q9_improved_no": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q9_sf[0].Speaking_Q9_checkbox_sf[0].Speaking_Q9_check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No - speaking will not improve"
    },
    "speaking_q9_improved_unsure": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q9_sf[0].Speaking_Q9_checkbox_sf[0].Speaking_Q9_check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure - whether speaking will improve"
    },
    "speaking_q9_year": {
        "field_id": "form1[0].Page5_Speaking[0].Speaking_sf[0].Speaking_Q9_sf[0].Speaking_Q9_checkbox_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q9: Year speaking improvement expected (only if Q9=Yes)"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 6 — HEARING
    # ════════════════════════════════════════════════════════════
    "hearing_patient_name": {
        "field_id": "form1[0].Page6_Hearing[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 6)"
    },
    "hearing_doctor_initial": {
        "field_id": "form1[0].Page6_Hearing[0].Initial_sf[0].Hearing_Doctor[0]",
        "type": "text", "description": "Doctor initials for hearing section"
    },
    "hearing_nurse_initial": {
        "field_id": "form1[0].Page6_Hearing[0].Initial_sf[0].Hearing_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials for hearing section"
    },
    "hearing_audiologist_initial": {
        "field_id": "form1[0].Page6_Hearing[0].Initial_sf[0].Hearing_Audio[0]",
        "type": "text", "description": "Audiologist initials"
    },
    "hearing_q1_conditions": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q1_sf[0].Details_sf[0].HearingQ1[0].Hearing_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing hearing, with year"
    },
    "hearing_q2_left_ear": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q2_sf[0].Hearing_Q2_Left_Drop[0]",
        "type": "choice",
        "options": ["normal: 0-25dB", "mild: 26-40dB", "moderate: 41-55dB", "moderate-to-severe: 56-70dB", "severe: 71-90dB", "profound: 91dB+", "unknown"],
        "description": "Q2: Hearing loss level in left ear"
    },
    "hearing_q2_right_ear": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q2_sf[0].Hearing_Q2_Right_Drop[0]",
        "type": "choice",
        "options": ["normal: 0-25dB", "mild: 26-40dB", "moderate: 41-55dB", "moderate-to-severe: 56-70dB", "severe: 71-90dB", "profound: 91dB+", "unknown"],
        "description": "Q2: Hearing loss level in right ear"
    },
    "hearing_q3_devices_therapy": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q3_sf[0].Q3_Details_sf[0].Q3[0].Hearing_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy for hearing (e.g. cochlear implant, hearing aid)"
    },
    "hearing_q4_examples": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q4_sf[0].HearingQ4_Details_sf[0].Q4[0].Hearing_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of hearing impairment despite therapy/devices"
    },
    "hearing_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q5_sf[0].Hearing_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - unable or takes inordinate time", "/1": "No"},
        "description": "Q5: Unable to hear or takes inordinate time?"
    },
    "hearing_q6_all_or_substantially": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q6_sf[0].Hearing_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: All or substantially all of the time?"
    },
    "hearing_q7_year_impaired": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year hearing impairment began"
    },
    "hearing_q8_lasted_12mo": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q8_sf[0].Hearing_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Lasted or expected to last 12+ months?"
    },
    "hearing_q9_improved_yes": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q9_sf[0].Hearing_Q9_checkbox[0].HearingQ9_check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - hearing likely to improve"
    },
    "hearing_q9_improved_no": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q9_sf[0].Hearing_Q9_checkbox[0].HearingQ9_check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "hearing_q9_improved_unsure": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q9_sf[0].Hearing_Q9_checkbox[0].HearingQ9_check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "hearing_q9_year": {
        "field_id": "form1[0].Page6_Hearing[0].Hearing_sf[0].Hearing_Q9_sf[0].Hearing_Q9_checkbox[0].Year_sf[0].Hearing_Q9_Year[0]",
        "type": "text", "description": "Q9: Year hearing improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 7 — WALKING
    # ════════════════════════════════════════════════════════════
    "walking_patient_name": {
        "field_id": "form1[0].Page7_Walking[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 7)"
    },
    "walking_doctor_initial": {
        "field_id": "form1[0].Page7_Walking[0].Initial_sf[0].Walking_Doctor[0]",
        "type": "text", "description": "Doctor initials for walking section"
    },
    "walking_nurse_initial": {
        "field_id": "form1[0].Page7_Walking[0].Initial_sf[0].Walking_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "walking_therapist_initial": {
        "field_id": "form1[0].Page7_Walking[0].Initial_sf[0].Walking_Thera[0]",
        "type": "text", "description": "Occupational therapist initials"
    },
    "walking_physio_initial": {
        "field_id": "form1[0].Page7_Walking[0].Initial_sf[0].Walking_Physio[0]",
        "type": "text", "description": "Physiotherapist initials"
    },
    "walking_q1_conditions": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q1_sf[0].Q1_Details_sf[0].Q1[0].Walking_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing walking, with year"
    },
    "walking_q2_takes_medication": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q2_sf[0].Walking_Q2_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Takes medication for walking impairment?"
    },
    "walking_q3_devices_therapy": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q3_sf[0].Q3_Details_sf[0].Q3[0].Walking_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy used (e.g. cane, occupational therapy)"
    },
    "walking_q4_examples": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q4_sf[0].Q4_Details_sf[0].Q4[0].Walking_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of walking impairment despite therapy/devices"
    },
    "walking_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q5_sf[0].Walking_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - unable or takes inordinate time (3x longer for 100m)", "/1": "No"},
        "description": "Q5: Unable to walk or takes inordinate time?"
    },
    "walking_q6_all_or_substantially": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q6_sf[0].Walking_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: All or substantially all of the time?"
    },
    "walking_q7_year_impaired": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year walking impairment began"
    },
    "walking_q8_lasted_12mo": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q8_sf[0].Walking_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Lasted or expected to last 12+ months?"
    },
    "walking_q9_improved_yes": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q9_sf[0].Walking_Q9_checkbox_sf[0].WalkingQ9_check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - walking likely to improve"
    },
    "walking_q9_improved_no": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q9_sf[0].Walking_Q9_checkbox_sf[0].WalkingQ9_check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "walking_q9_improved_unsure": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q9_sf[0].Walking_Q9_checkbox_sf[0].WalkingQ9_check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "walking_q9_year": {
        "field_id": "form1[0].Page7_Walking[0].Walking_sf[0].Walking_Q9_sf[0].Walking_Q9_checkbox_sf[0].Year_sf[0].Walking_Q9_Year[0]",
        "type": "text", "description": "Q9: Year walking improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 8 — ELIMINATING
    # ════════════════════════════════════════════════════════════
    "eliminating_patient_name": {
        "field_id": "form1[0].Page8_Eliminating[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 8)"
    },
    "eliminating_doctor_initial": {
        "field_id": "form1[0].Page8_Eliminating[0].Initial_sf[0].Eliminating_Doctor[0]",
        "type": "text", "description": "Doctor initials for eliminating section"
    },
    "eliminating_nurse_initial": {
        "field_id": "form1[0].Page8_Eliminating[0].Initial_sf[0].Eliminating_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "eliminating_q1_conditions": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q1_sf[0].Q1_Details_sf[0].Q1[0].Eliminating_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing bowel/bladder functions, with year"
    },
    "eliminating_q2_takes_medication": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q2_sf[0].Eliminating_Q2_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Takes medication for bowel/bladder impairment?"
    },
    "eliminating_q3_devices_therapy": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q3_sf[0].Q3_Details_sf[0].Q3[0].Eliminating_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy used (e.g. ostomy, biological therapy)"
    },
    "eliminating_q4_examples": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q4_sf[0].Q4_Details_sf[0].Q4[0].Eliminating_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of eliminating impairment despite therapy/devices"
    },
    "eliminating_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q5_sf[0].Eliminating_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q5: Unable to manage bowel/bladder or takes inordinate time?"
    },
    "eliminating_q6_all_or_substantially": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q6_sf[0].Eliminating_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: All or substantially all of the time?"
    },
    "eliminating_q7_year_impaired": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].EliminatingQ7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year eliminating impairment began"
    },
    "eliminating_q8_lasted_12mo": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q8_sf[0].Eliminating_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Lasted or expected to last 12+ months?"
    },
    "eliminating_q9_improved_yes": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q9_sf[0].Eliminating_Q9_checkbox_sf[0].EliminatingQ9_check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - likely to improve"
    },
    "eliminating_q9_improved_no": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q9_sf[0].Eliminating_Q9_checkbox_sf[0].EliminatingQ9_check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "eliminating_q9_improved_unsure": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q9_sf[0].Eliminating_Q9_checkbox_sf[0].EliminatingQ9_check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "eliminating_q9_year": {
        "field_id": "form1[0].Page8_Eliminating[0].Eliminating_sf[0].Eliminating_Q9_sf[0].Eliminating_Q9_checkbox_sf[0].Year_sf[0].Eliminating_Q9_Year[0]",
        "type": "text", "description": "Q9: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 9 — FEEDING
    # ════════════════════════════════════════════════════════════
    "feeding_patient_name": {
        "field_id": "form1[0].Page9_Feeding[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 9)"
    },
    "feeding_doctor_initial": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_Doctor[0]",
        "type": "text", "description": "Doctor initials for feeding section"
    },
    "feeding_nurse_initial": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "feeding_therapist_initial": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_Thera[0]",
        "type": "text", "description": "Occupational therapist initials"
    },
    "feeding_q1_conditions": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q1_sf[0].Q1_Details_sf[0].Q1[0].Feeding_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing feeding, with year"
    },
    "feeding_q2_takes_medication": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q2_sf[0].Feeding_Q2_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Takes medication for feeding impairment?"
    },
    "feeding_q3_devices_therapy": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q3_sf[0].Q3_Details_sf[0].Q3[0].Feeding_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy used (e.g. assistive utensils)"
    },
    "feeding_q4_examples": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q4_sf[0].Q4_details_sf[0].Q4[0].Feeding_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of feeding impairment"
    },
    "feeding_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q5_sf[0].Feeding_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q5: Unable to feed or takes inordinate time?"
    },
    "feeding_q6_all_or_substantially": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q6_sf[0].Feeding_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: All or substantially all of the time?"
    },
    "feeding_q7_year_impaired": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year feeding impairment began"
    },
    "feeding_q8_lasted_12mo": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q8_sf[0].Feeding_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Lasted or expected to last 12+ months?"
    },
    "feeding_q9_improved_yes": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q9_sf[0].Feeding_Q9_checkbox_sf[0].FeedingQ9_check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - likely to improve"
    },
    "feeding_q9_improved_no": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q9_sf[0].Feeding_Q9_checkbox_sf[0].FeedingQ9_check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "feeding_q9_improved_unsure": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q9_sf[0].Feeding_Q9_checkbox_sf[0].FeedingQ9_check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "feeding_q9_year": {
        "field_id": "form1[0].Page9_Feeding[0].Feeding_sf[0].Feeding_Q9_sf[0].Feeding_Q9_checkbox_sf[0].Year_sf[0].Feeding_Q9_Year[0]",
        "type": "text", "description": "Q9: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 10 — DRESSING
    # ════════════════════════════════════════════════════════════
    "dressing_patient_name": {
        "field_id": "form1[0].Page10_Dressing[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 10)"
    },
    "dressing_doctor_initial": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_Doctor[0]",
        "type": "text", "description": "Doctor initials for dressing section"
    },
    "dressing_nurse_initial": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "dressing_therapist_initial": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_Thera[0]",
        "type": "text", "description": "Occupational therapist initials"
    },
    "dressing_q1_conditions": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q1_sf[0].Q1_Details_sf[0].Q1[0].Dressing_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing dressing, with year"
    },
    "dressing_q2_takes_medication": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q2_sf[0].Dressing_Q2_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Takes medication for dressing impairment?"
    },
    "dressing_q3_devices_therapy": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q3_sf[0].Q3_Details_sf[0].Q3[0].Dressing_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy used (e.g. button hook)"
    },
    "dressing_q4_examples": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q4_sf[0].Q4_details_sf[0].Q4[0].Dressing_Q4_details[0]",
        "type": "text", "description": "Q4 (mandatory): Examples of dressing impairment"
    },
    "dressing_q5_unable_or_inordinate": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q5_sf[0].Dressing_Q5_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q5: Unable to dress or takes inordinate time?"
    },
    "dressing_q6_all_or_substantially": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q6_sf[0].Dressing_Q6_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: All or substantially all of the time?"
    },
    "dressing_q7_year_impaired": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q7_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q7: Year dressing impairment began"
    },
    "dressing_q8_lasted_12mo": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q8_sf[0].Dressing_Q8_RadioButtonList[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Lasted or expected to last 12+ months?"
    },
    "dressing_q9_improved_yes": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q9_sf[0].Dressing_Q9_checkbox_sf[0].Dressing_Q9_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - likely to improve"
    },
    "dressing_q9_improved_no": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q9_sf[0].Dressing_Q9_checkbox_sf[0].Dressing_Q9_Check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "dressing_q9_improved_unsure": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q9_sf[0].Dressing_Q9_checkbox_sf[0].Dressing_Q9_Check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "dressing_q9_year": {
        "field_id": "form1[0].Page10_Dressing[0].Dressing_sf[0].Dressing_Q9_sf[0].Dressing_Q9_checkbox_sf[0].Year_sf[0].Dressing_Q9_Year[0]",
        "type": "text", "description": "Q9: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 11 — MENTAL FUNCTIONS (Part 1)
    # ════════════════════════════════════════════════════════════
    "mental_patient_name_p11": {
        "field_id": "form1[0].Page11_Mental1[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 11)"
    },
    "mental_doctor_initial": {
        "field_id": "form1[0].Page11_Mental1[0].Initial_sf[0].Mental1_Doctor[0]",
        "type": "text", "description": "Doctor initials for mental functions section"
    },
    "mental_nurse_initial": {
        "field_id": "form1[0].Page11_Mental1[0].Initial_sf[0].Mental1_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "mental_psychologist_initial": {
        "field_id": "form1[0].Page11_Mental1[0].Initial_sf[0].Mental1_Psycho[0]",
        "type": "text", "description": "Psychologist initials"
    },
    "mental_q1_conditions": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q1_sf[0].Q1_Details_sf[0].Q1[0].Mental1_Q1_details[0]",
        "type": "text", "description": "Q1: Conditions impairing mental functions, with year"
    },
    "mental_q2_takes_medication": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q2_sf[0].Mental1_Q2_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Takes medication for mental functions impairment?"
    },
    "mental_q2_needs_supervision_for_meds": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q2_sf[0].Mental1_Q2_RadioButtonList2[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No", "/2": "Unsure"},
        "description": "Q2: Requires supervision/reminders to take medication? (not applicable for children)"
    },
    "mental_q2_medication_effectiveness": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q2_sf[0].Mental1_Q2_RadioButtonList3[0]",
        "type": "radio_group",
        "options": {"/0": "Effective", "/1": "Moderately effective", "/2": "Mildly effective", "/3": "Ineffective", "/4": "Unsure"},
        "description": "Q2: How effectively does medication manage the impairment?"
    },
    "mental_q3_devices_therapy": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q3_sf[0].Designation_sf[0].Q3[0].Mental1_Q3_details[0]",
        "type": "text", "description": "Q3: Devices/therapy used (e.g. memory aids, assistive technology, CBT)"
    },
    "mental_q4_impaired_independence": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].Mental1_Q4_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No", "/1": "Yes - impaired capacity to live independently"},
        "description": "Q4: Does patient have impaired capacity to live independently without daily supervision?"
    },
    # Q4 support checkboxes — Adult
    "mental_q4_adult_assisted_living": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Adult_sf[0].Adult_Check_sf[0].M1_Q4_A_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Adult support: Assisted living or long-term facility"
    },
    "mental_q4_adult_community_services": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Adult_sf[0].Adult_Check_sf[0].M1_Q4_A_Check2[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Adult support: Community-based health services"
    },
    "mental_q4_adult_hospitalization": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Adult_sf[0].Adult_Check_sf[0].M1_Q4_A_Check3[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Adult support: Hospitalization"
    },
    "mental_q4_adult_family_support": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Adult_sf[0].Adult_Check_sf[0].M1_Q4_A_Check4[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Adult support: Support from family members"
    },
    # Q4 support checkboxes — Child
    "mental_q4_child_adult_supervision": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Child_sf[0].Child_Check_sf[0].M1_Q4_Child_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Child support: Adult supervision at home beyond age-appropriate level"
    },
    "mental_q4_child_school_support": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Child_sf[0].Child_Check_sf[0].M1_Q4_Child_Check2[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q4 Child support: Additional support from educational staff at school"
    },
    "mental_q4_support_details": {
        "field_id": "form1[0].Page11_Mental1[0].Mental1_sf[0].Mental1_Q4_sf[0].M1_Q4_Details_sf[0].Q4[0].Mental2_Q4_details[0]",
        "type": "text", "description": "Q4: Additional details about support received (optional)"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 12 — MENTAL FUNCTIONS TABLE (Q5 ratings)
    # Radio options: /0=No limitations, /1=Some limitations, /2=Severe limitations
    # ════════════════════════════════════════════════════════════
    "mental_patient_name_p12": {
        "field_id": "form1[0].Page12_Mental2[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 12)"
    },
    # Adaptive functioning
    "mental_q5_adaptive_adapt_to_change": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub1_sf[0].M2_Q5_C1_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Adapt to change"
    },
    "mental_q5_adaptive_express_needs": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub2_sf[0].M2_Q5_C1_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Express basic needs"
    },
    "mental_q5_adaptive_go_into_community": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub3_sf[0].M2_Q5_C1_S3_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Go out into the community"
    },
    "mental_q5_adaptive_transactions": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub4_sf[0].M2_Q5_C1_S4_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Initiate common, simple transactions"
    },
    "mental_q5_adaptive_hygiene": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub5_sf[0].M2_Q5_C1_S5_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Perform basic hygiene or self-care"
    },
    "mental_q5_adaptive_everyday_tasks": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie1_sf[0].Sub6_sf[0].M2_Q5_C1_S6_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Adaptive functioning: Perform necessary everyday tasks"
    },
    # Attention
    "mental_q5_attention_danger_awareness": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie2_sf[0].Sub1_sf[0].M2_Q5_C2_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Attention: Demonstrate awareness of danger and risks"
    },
    "mental_q5_attention_impulse_control": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie2_sf[0].Sub2_sf[0].M2_Q5_C2_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Attention: Demonstrate basic impulse control"
    },
    # Concentration
    "mental_q5_concentration_focus": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie3_sf[0].Sub1_sf[0].M2_Q5_C3_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Concentration: Focus on a simple task for any length of time"
    },
    "mental_q5_concentration_short_term_memory": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie3_sf[0].Sub2_sf[0].M2_Q5_C3_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Concentration: Absorb and retrieve information in the short-term"
    },
    # Goal-setting
    "mental_q5_goal_make_plans": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie4_sf[0].Sub1_sf[0].M2_Q5_C4_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Goal-setting: Make and carry out simple day-to-day plans"
    },
    "mental_q5_goal_self_direct": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie4_sf[0].Sub2_sf[0].M2_Q5_C4_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Goal-setting: Self-direct to begin everyday tasks"
    },
    # Judgment
    "mental_q5_judgment_clothing": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie5_sf[0].Sub1_sf[0].M2_Q5_C5_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Judgment: Choose weather-appropriate clothing"
    },
    "mental_q5_judgment_own_treatment": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie5_sf[0].Sub2_sf[0].M2_Q5_C5_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Judgment: Make decisions about own treatment and welfare"
    },
    "mental_q5_judgment_exploitation_risk": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie5_sf[0].Sub3_sf[0].M2_Q5_C5_S3_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Judgment: Recognize risk of being taken advantage of"
    },
    "mental_q5_judgment_consequences": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie5_sf[0].Sub4_sf[0].M2_Q5_C5_S4_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Judgment: Understand consequences of actions or decisions"
    },
    # Memory
    "mental_q5_memory_personal_info": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie6_sf[0].Sub1_sf[0].M2_Q5_C6_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Memory: Remember basic personal information (DOB, address)"
    },
    "mental_q5_memory_important_info": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie6_sf[0].Sub2_sf[0].M2_Q5_C6_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Memory: Remember material of importance and interest"
    },
    "mental_q5_memory_simple_instructions": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie6_sf[0].Sub3_sf[0].M2_Q5_C6_S3_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Memory: Remember simple instructions"
    },
    # Perception of reality
    "mental_q5_perception_reality": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie7_sf[0].Sub1_sf[0].M2_Q5_C7_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Perception of reality: Demonstrate accurate understanding of reality"
    },
    "mental_q5_perception_delusions": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie7_sf[0].Sub2_sf[0].M2_Q5_C7_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Perception of reality: Distinguish reality from delusions/hallucinations"
    },
    # Problem-solving
    "mental_q5_problem_identify": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie8_sf[0].Sub1_sf[0].M2_Q5_C8_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Problem-solving: Identify everyday problems"
    },
    "mental_q5_problem_implement": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie8_sf[0].Sub2_sf[0].M2_Q5_C8_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Problem-solving: Implement solutions to simple problems"
    },
    # Regulation of behaviour and emotions
    "mental_q5_regulation_behaviour": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie9_sf[0].Sub1_sf[0].M2_Q5_C9_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Regulation: Behave appropriately for the situation"
    },
    "mental_q5_regulation_emotions": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie9_sf[0].Sub2_sf[0].M2_Q5_C9_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Regulation: Demonstrate appropriate emotional responses"
    },
    "mental_q5_regulation_mood": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie9_sf[0].Sub3_sf[0].M2_Q5_C9_S3_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Regulation: Regulate mood to prevent risk of harm to self or others"
    },
    # Verbal and non-verbal comprehension
    "mental_q5_comprehension_nonverbal": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie10_sf[0].Sub1_sf[0].M2_Q5_C10_S1_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Comprehension: Understand and respond to non-verbal information"
    },
    "mental_q5_comprehension_verbal": {
        "field_id": "form1[0].Page12_Mental2[0].Mental2_sf[0].Table_sf[0].Categorie10_sf[0].Sub2_sf[0].M2_Q5_C10_S2_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "No limitations", "/1": "Some limitations", "/2": "Severe limitations"},
        "description": "Q5 Comprehension: Understand and respond to verbal information"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 13 — MENTAL FUNCTIONS (Part 3)
    # ════════════════════════════════════════════════════════════
    "mental_patient_name_p13": {
        "field_id": "form1[0].Page13_Mental3[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 13)"
    },
    "mental_q6_some_limitations_examples": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q6_sf[0].Q6_details_sf[0].Q6[0].Mental_Q6_details[0]",
        "type": "text",
        "description": "Q6: Examples of 'some limitations' from Q5 table, or additional examples of mental function impairment"
    },
    "mental_q7_unable_or_inordinate": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q7_sf[0].M3_Q7_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - unable or takes inordinate time (3x longer)", "/1": "No"},
        "description": "Q7: Unable to perform mental functions or takes inordinate time?"
    },
    "mental_q8_all_or_substantially": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q8_sf[0].M3_Q8_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: All or substantially all of the time?"
    },
    "mental_q9_year_impaired": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q9_sf[0].Year_sf[0].Year[0]",
        "type": "text", "description": "Q9: Year mental functions impairment began"
    },
    "mental_q10_lasted_12mo": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q10_sf[0].M3_Q10_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q10: Lasted or expected to last 12+ months?"
    },
    "mental_q11_improved_yes": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q11_sf[0].M3_Q11_Check_sf[0].M3_Q11_Check[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q11: Yes - mental functions likely to improve"
    },
    "mental_q11_improved_no": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q11_sf[0].M3_Q11_Check_sf[0].M3_Q11_Check[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q11: No"
    },
    "mental_q11_improved_unsure": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q11_sf[0].M3_Q11_Check_sf[0].M3_Q11_Check[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q11: Unsure"
    },
    "mental_q11_year": {
        "field_id": "form1[0].Page13_Mental3[0].Mental3_sf[0].Mental3_Q11_sf[0].M3_Q11_Check_sf[0].Year_sf[0].Mental3_Q11_Year[0]",
        "type": "text", "description": "Q11: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 14 — CUMULATIVE EFFECT
    # ════════════════════════════════════════════════════════════
    "cumulative_patient_name": {
        "field_id": "form1[0].Page14_Cumulative[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 14)"
    },
    "cumulative_doctor_initial": {
        "field_id": "form1[0].Page14_Cumulative[0].Initial_sf[0].Cumul_Doctor[0]",
        "type": "text", "description": "Doctor initials for cumulative section"
    },
    "cumulative_nurse_initial": {
        "field_id": "form1[0].Page14_Cumulative[0].Initial_sf[0].Cumul_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "cumulative_therapist_initial": {
        "field_id": "form1[0].Page14_Cumulative[0].Initial_sf[0].Cumul_Thera[0]",
        "type": "text", "description": "Occupational therapist initials"
    },
    # Q1 — Categories with significant limitations (check all that apply)
    "cumulative_q1_vision": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Vision - significant limitations"
    },
    "cumulative_q1_speaking": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check2[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Speaking - significant limitations"
    },
    "cumulative_q1_hearing": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check3[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Hearing - significant limitations"
    },
    "cumulative_q1_walking": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check4[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Walking - significant limitations"
    },
    "cumulative_q1_eliminating": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check5[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Eliminating - significant limitations"
    },
    "cumulative_q1_feeding": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check6[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Feeding - significant limitations"
    },
    "cumulative_q1_dressing": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check7[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Dressing - significant limitations"
    },
    "cumulative_q1_mental_functions": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q1_sf[0].Cumul_Q1_Check8[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q1: Mental functions - significant limitations"
    },
    "cumulative_q2_examples": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q2_sf[0].Q2_details_sf[0].Q2[0].Cumul_Q2_details[0]",
        "type": "text",
        "description": "Q2 (mandatory): Examples of significant limitations in selected categories"
    },
    "cumulative_q3_exist_together": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q3_sf[0].Cumul_Q3_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - limitations exist together all/substantially all of the time", "/1": "No"},
        "description": "Q3: Do limitations exist together all or substantially all of the time?"
    },
    "cumulative_q4_equivalent_to_marked": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q4_sf[0].Cumul_Q4_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - equivalent to marked restriction in single category", "/1": "No"},
        "description": "Q4: Is cumulative effect equivalent to being unable/inordinate time in one category?"
    },
    "cumulative_q5_year_began": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q5_sf[0].Year_sf[0].Cumul_Q5_Year[0]",
        "type": "text", "description": "Q5: Year cumulative effect of limitations began"
    },
    "cumulative_q6_lasted_12mo": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q6_sf[0].Cumul_Q6_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q6: Impairments lasted or expected to last 12+ months?"
    },
    "cumulative_q7_improved_yes": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q7_sf[0].Cumul_Q7_Check_sf[0].Cumul_Q7_Check[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q7: Yes - cumulative impairments likely to improve"
    },
    "cumulative_q7_improved_no": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q7_sf[0].Cumul_Q7_Check_sf[0].Cumul_Q7_Check[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q7: No"
    },
    "cumulative_q7_improved_unsure": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q7_sf[0].Cumul_Q7_Check_sf[0].Cumul_Q7_Check[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q7: Unsure"
    },
    "cumulative_q7_year": {
        "field_id": "form1[0].Page14_Cumulative[0].Cumulative_sf[0].Cumul_Q7_sf[0].Cumul_Q7_Check_sf[0].Year_sf[0].Cumul_Q7_Year[0]",
        "type": "text", "description": "Q7: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 15 — LIFE-SUSTAINING THERAPY
    # ════════════════════════════════════════════════════════════
    "lst_patient_name": {
        "field_id": "form1[0].Page15_LST[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 15)"
    },
    "lst_doctor_initial": {
        "field_id": "form1[0].Page15_LST[0].LST_Doctor[0]",
        "type": "text", "description": "Doctor initials for LST section"
    },
    "lst_nurse_initial": {
        "field_id": "form1[0].Page15_LST[0].LST_Nurse[0]",
        "type": "text", "description": "Nurse practitioner initials"
    },
    "lst_q1_type1_diabetes_timing": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].Info_sf[0].LST_Q1_sf[0].LST_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {"/0": "Prior to 2021 - continue to Q2", "/1": "2021 and later - skip to Certification"},
        "description": "Q1: When was patient diagnosed with type 1 diabetes? (Only for type 1 diabetes)"
    },
    "lst_q1_year_diagnosed": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].Info_sf[0].LST_Q1_sf[0].Year[0].Numeric_NoDecimal_BordersAll[0]",
        "type": "text", "description": "Q1: Year type 1 diabetes diagnosed (if 2021 and later)"
    },
    # Q2 — Therapy type checkboxes
    "lst_q2_therapy_insulin_injections": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Multiple daily insulin injections"
    },
    "lst_q2_therapy_insulin_pump": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check2[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Insulin pump"
    },
    "lst_q2_therapy_hemodialysis": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check3[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Hemodialysis"
    },
    "lst_q2_therapy_peritoneal_dialysis": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check4[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Peritoneal dialysis"
    },
    "lst_q2_therapy_intermittent_oxygen": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check5[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Intermittent oxygen therapy"
    },
    "lst_q2_therapy_24hr_oxygen": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check6[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: 24-hour oxygen therapy"
    },
    "lst_q2_therapy_tube_feeding": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check7[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Tube feeding"
    },
    "lst_q2_therapy_chest_physio": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check8[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Chest physiotherapy"
    },
    "lst_q2_therapy_other": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].LST_Q2_Check9[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Therapy: Other (specify in text field)"
    },
    "lst_q2_therapy_other_text": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].LST_list[0].Other_text_LST[0]",
        "type": "text", "description": "Q2 Therapy: Other therapy description"
    },
    # Q2 — Medical condition checkboxes
    "lst_q2_condition_type1_diabetes": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check10[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: Type 1 diabetes"
    },
    "lst_q2_condition_type2_diabetes": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check11[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: Type 2 diabetes"
    },
    "lst_q2_condition_renal_disease": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check12[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: End-stage renal disease"
    },
    "lst_q2_condition_pku": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check13[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: Phenylketonuria (PKU)"
    },
    "lst_q2_condition_cystic_fibrosis": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check14[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: Cystic fibrosis"
    },
    "lst_q2_condition_other": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].LST_Q2_Check15[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q2 Condition: Other (specify)"
    },
    "lst_q2_condition_other_text": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q2_sf[0].Med_Cond_list[0].Other_text_mc[0]",
        "type": "text", "description": "Q2 Condition: Other condition description"
    },
    "lst_q3_eligible_activities": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q3_sf[0].LST_Q3_Details_sf[0].Q3[0].LST_Q3_details[0]",
        "type": "text", "description": "Q3: List eligible activities patient dedicates time to for therapy administration"
    },
    "lst_q4_supports_vital_function": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q4_sf[0].LST_Q4_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes - therapy supports a vital function", "/1": "No"},
        "description": "Q4: Does therapy support a vital function?"
    },
    "lst_q5_times_per_week": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q5_sf[0].LST_Q5_Week[0]",
        "type": "text", "description": "Q5: Minimum number of times per week therapy is needed (numeric)"
    },
    "lst_q6_hours_per_week": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q6_sf[0].LST_Q6_Week[0]",
        "type": "text", "description": "Q6: Average hours per week dedicated to therapy administration (numeric)"
    },
    "lst_q7_year_began": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q7_sf[0].Year_sf[0].LST_Q7_Year[0]",
        "type": "text", "description": "Q7: Year patient began needing life-sustaining therapy"
    },
    "lst_q8_lasted_12mo": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q8_sf[0].LST_Q8_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q8: Impairment lasted or expected to last 12+ months?"
    },
    "lst_q9_improved_yes": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q9_sf[0].LST_Q9_Check_sf[0].LST_Q9_Check1[0]",
        "type": "checkbox", "checked_value": "/1", "description": "Q9: Yes - likely to improve"
    },
    "lst_q9_improved_no": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q9_sf[0].LST_Q9_Check_sf[0].LST_Q9_Check1[1]",
        "type": "checkbox", "checked_value": "/2", "description": "Q9: No"
    },
    "lst_q9_improved_unsure": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q9_sf[0].LST_Q9_Check_sf[0].LST_Q9_Check1[2]",
        "type": "checkbox", "checked_value": "/3", "description": "Q9: Unsure"
    },
    "lst_q9_year": {
        "field_id": "form1[0].Page15_LST[0].LST_sf[0].LST_Q9_sf[0].LST_Q9_Check_sf[0].Year_sf[0].LST_Q9_Year[0]",
        "type": "text", "description": "Q9: Year improvement expected"
    },

    # ════════════════════════════════════════════════════════════
    # PAGE 16 — CERTIFICATION (doctor's section)
    # ════════════════════════════════════════════════════════════
    "cert_patient_name": {
        "field_id": "form1[0].Page16_Certification[0].PatientName[0]",
        "type": "text", "description": "Patient name (page 16)"
    },
    "cert_year_from": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Q1_sf[0].Cert_Q1_Year1[0]",
        "type": "text", "description": "Q1: Year FROM which patient has been under your care"
    },
    "cert_year_to": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Q1_sf[0].Cert_Q1_Year2[0]",
        "type": "text", "description": "Q1: Year TO which patient has been under your care (or present year)"
    },
    "cert_q2_medical_info_on_file": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Q2_sf[0].Cert_Q2_RadioButtonList1[0]",
        "type": "radio_group",
        "options": {"/0": "Yes", "/1": "No"},
        "description": "Q2: Do you have medical information on file for all certified years?"
    },
    "cert_practitioner_type": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_type_sf[0].Cert_Med_RadioButtonGroup1[0]",
        "type": "radio_group",
        "options": {
            "/0": "Medical doctor",
            "/1": "Nurse practitioner",
            "/2": "Optometrist",
            "/3": "Occupational therapist",
            "/4": "Audiologist",
            "/5": "Physiotherapist",
            "/6": "Psychologist",
            "/7": "Speech-language pathologist"
        },
        "description": "Certification: Type of medical practitioner signing"
    },
    "cert_practitioner_name": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Sign_sf[0].PatientName[0]",
        "type": "text", "description": "Certification: Practitioner's printed name"
    },
    "cert_license_number": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Sign_sf[0].Cert_License[0]",
        "type": "text", "description": "Certification: Medical license/registration number (optional)"
    },
    "cert_telephone": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Sign_sf[0].Cert_TelephoneNumber[0]",
        "type": "text", "description": "Certification: Practitioner telephone number"
    },
    "cert_date": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Sign_sf[0].Date_Comb[0].Certification_Date_Fill[0]",
        "type": "text", "description": "Certification: Date signed (YYYYMMDD format)"
    },
    "cert_address": {
        "field_id": "form1[0].Page16_Certification[0].Certification_sf[0].Cert_Sign_sf[0].Cert_Address[0]",
        "type": "text", "description": "Certification: Practitioner's address"
    },
}


def build_llm_schema() -> str:
    """
    Build a JSON schema description for the LLM prompt.
    Only includes fields that make sense to extract from unstructured text.
    Skips patient_name fields (those are filled from a separate source)
    and footnote checkboxes.
    """
    lines = []
    for key, field in FIELD_MAP.items():
        if "patient_name" in key:
            continue
        desc = field["description"]
        ftype = field["type"]
        if ftype == "radio_group":
            opts = " | ".join(f'{v}="{label}"' for v, label in field["options"].items())
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "choice":
            opts = " | ".join(f'"{o}"' for o in field["options"])
            lines.append(f'  "{key}": ""  // {desc}. Options: {opts}')
        elif ftype == "checkbox":
            lines.append(f'  "{key}": false  // {desc}. Set true to check.')
        else:
            lines.append(f'  "{key}": ""  // {desc}')
    return "{\n" + "\n".join(lines) + "\n}"