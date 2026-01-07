"""
Magic Prompt Templates for Medical AI Chatbot
Provides pre-built prompts for common ICU clinical scenarios
"""

from typing import Dict, List, Optional


class MagicPromptTemplates:
    """Collection of medical prompt templates organized by category"""

    CATEGORIES = {
        "sepsis": "🦠 Sepsis & Infection",
        "mortality": "💔 Mortality Risk Assessment",
        "labs": "🔬 Lab Results Interpretation",
        "medications": "💊 Medication & Treatment",
        "diagnosis": "🩺 Differential Diagnosis",
        "procedures": "⚕️ Clinical Procedures",
        "emergency": "🚨 Emergency Situations",
    }

    TEMPLATES = {
        # 🦠 SEPSIS & INFECTION
        "sepsis": {
            "sepsis_screening": {
                "name": "Sepsis Screening Assessment",
                "description": "Evaluate patient for sepsis using qSOFA and SIRS criteria",
                "template": """Please perform a comprehensive sepsis screening assessment:

Patient Status:
- Temperature: {temperature}°C
- Heart Rate: {heart_rate} bpm
- Respiratory Rate: {respiratory_rate} breaths/min
- Blood Pressure: {blood_pressure}
- Mental Status: {mental_status}
- WBC Count: {wbc}
- Lactate: {lactate}

Questions:
1. Calculate qSOFA score and interpret the result
2. Assess SIRS criteria fulfillment
3. What is the probability of sepsis?
4. What are the immediate next steps?
5. What diagnostic tests should be ordered urgently?
6. Recommend initial treatment protocol

Please provide evidence-based recommendations with references to Surviving Sepsis Campaign guidelines.""",
                "placeholders": [
                    "temperature",
                    "heart_rate",
                    "respiratory_rate",
                    "blood_pressure",
                    "mental_status",
                    "wbc",
                    "lactate",
                ],
            },
            "sepsis_source": {
                "name": "Sepsis Source Investigation",
                "description": "Identify potential infection source and guide targeted treatment",
                "template": """Help identify the source of sepsis and guide treatment:

Clinical Presentation:
- Primary Symptoms: {symptoms}
- Recent Procedures/Devices: {procedures}
- Imaging Findings: {imaging}
- Culture Results: {cultures}

Analysis Needed:
1. What are the most likely infection sources?
2. What additional diagnostic tests are recommended?
3. What empiric antibiotic regimen is appropriate?
4. Should any devices (catheters, tubes) be removed?
5. What source control measures are needed?

Provide evidence-based recommendations with antibiotic spectrum coverage.""",
                "placeholders": ["symptoms", "procedures", "imaging", "cultures"],
            },
            "antibiotic_selection": {
                "name": "Antibiotic Selection Guide",
                "description": "Choose optimal antibiotic regimen based on patient factors",
                "template": """Recommend appropriate antibiotic therapy:

Patient Factors:
- Suspected Infection Site: {infection_site}
- Patient Allergies: {allergies}
- Renal Function (CrCl): {renal_function}
- Previous Cultures/Resistance: {resistance_history}
- Recent Antibiotics: {recent_antibiotics}
- Immunosuppression: {immunosuppression}

Questions:
1. What is the recommended empiric antibiotic regimen?
2. What adjustments are needed for renal function?
3. What is the appropriate dosing?
4. What is the duration of therapy?
5. What monitoring is required?
6. When should therapy be de-escalated?

Include hospital antibiogram considerations and local resistance patterns.""",
                "placeholders": [
                    "infection_site",
                    "allergies",
                    "renal_function",
                    "resistance_history",
                    "recent_antibiotics",
                    "immunosuppression",
                ],
            },
        },
        # 💔 MORTALITY RISK ASSESSMENT
        "mortality": {
            "mortality_risk": {
                "name": "ICU Mortality Risk Assessment",
                "description": "Calculate mortality risk scores and prognosis",
                "template": """Assess mortality risk for ICU patient:

Patient Demographics:
- Age: {age} years
- Admission Source: {admission_source}
- Primary Diagnosis: {diagnosis}

Clinical Scores:
- SOFA Score: {sofa_score}
- APACHE II: {apache_score}
- GCS: {gcs}

Comorbidities:
{comorbidities}

Analysis Required:
1. Calculate predicted mortality risk
2. Identify major risk factors contributing to mortality
3. What interventions could reduce mortality risk?
4. What is the expected ICU length of stay?
5. Should goals of care be discussed with family?
6. Provide prognostic information for care planning

Use validated mortality prediction models (APACHE, SOFA, SAPS).""",
                "placeholders": [
                    "age",
                    "admission_source",
                    "diagnosis",
                    "sofa_score",
                    "apache_score",
                    "gcs",
                    "comorbidities",
                ],
            },
            "code_status": {
                "name": "Code Status & Goals of Care",
                "description": "Guide discussions about resuscitation and care goals",
                "template": """Provide guidance for goals of care discussion:

Patient Situation:
- Current Condition: {condition}
- Prognosis: {prognosis}
- Family Understanding: {family_understanding}
- Patient's Prior Wishes: {prior_wishes}

Discussion Points Needed:
1. How to explain current medical situation to family?
2. What are realistic outcome expectations?
3. What are the options for level of care?
4. How to discuss DNR/DNI considerations?
5. What palliative care resources are available?
6. How to support family decision-making?

Provide compassionate, clear communication strategies.""",
                "placeholders": [
                    "condition",
                    "prognosis",
                    "family_understanding",
                    "prior_wishes",
                ],
            },
        },
        # 🔬 LAB RESULTS INTERPRETATION
        "labs": {
            "critical_labs": {
                "name": "Critical Lab Values Interpretation",
                "description": "Analyze abnormal lab results and recommend actions",
                "template": """Interpret critical laboratory values:

Laboratory Results:
- Potassium: {potassium} mmol/L
- Sodium: {sodium} mmol/L
- pH: {ph}
- Lactate: {lactate} mmol/L
- Creatinine: {creatinine} mg/dL
- Hemoglobin: {hemoglobin} g/dL
- Platelets: {platelets} x10^9/L
- INR: {inr}

Other Relevant Labs:
{other_labs}

Analysis Needed:
1. Which values are critically abnormal?
2. What are the potential causes?
3. What is the clinical significance?
4. What immediate interventions are required?
5. What additional tests should be ordered?
6. What monitoring is needed?
7. When should labs be rechecked?

Prioritize by urgency and clinical impact.""",
                "placeholders": [
                    "potassium",
                    "sodium",
                    "ph",
                    "lactate",
                    "creatinine",
                    "hemoglobin",
                    "platelets",
                    "inr",
                    "other_labs",
                ],
            },
            "blood_gas": {
                "name": "Blood Gas Analysis",
                "description": "Interpret ABG/VBG and guide ventilator management",
                "template": """Analyze arterial blood gas results:

ABG Results:
- pH: {ph}
- PaCO2: {paco2} mmHg
- PaO2: {pao2} mmHg
- HCO3: {hco3} mEq/L
- Base Excess: {base_excess}
- Lactate: {lactate}
- SaO2: {sao2}%

Ventilator Settings (if applicable):
- FiO2: {fio2}%
- PEEP: {peep} cmH2O
- Tidal Volume: {tidal_volume} mL

Questions:
1. What is the primary acid-base disorder?
2. Is there appropriate compensation?
3. Calculate A-a gradient and interpret
4. What is the P/F ratio?
5. What ventilator adjustments are needed?
6. What is the underlying cause?
7. What treatment is required?

Use systematic ABG interpretation approach.""",
                "placeholders": [
                    "ph",
                    "paco2",
                    "pao2",
                    "hco3",
                    "base_excess",
                    "lactate",
                    "sao2",
                    "fio2",
                    "peep",
                    "tidal_volume",
                ],
            },
        },
        # 💊 MEDICATION & TREATMENT
        "medications": {
            "vasopressor": {
                "name": "Vasopressor/Inotrope Selection",
                "description": "Choose appropriate vasoactive medication",
                "template": """Guide vasopressor/inotrope selection:

Hemodynamic Status:
- Blood Pressure: {blood_pressure}
- MAP: {map} mmHg
- Heart Rate: {heart_rate} bpm
- Cardiac Index: {cardiac_index}
- SVR: {svr}
- CVP: {cvp}

Clinical Context:
- Primary Diagnosis: {diagnosis}
- Fluid Status: {fluid_status}
- Cardiac Function: {cardiac_function}

Questions:
1. What is the hemodynamic profile (distributive/cardiogenic/hypovolemic)?
2. Which vasopressor/inotrope is most appropriate?
3. What is the recommended starting dose?
4. What is the titration strategy?
5. What monitoring is required?
6. What are the potential complications?
7. When can the medication be weaned?

Include evidence-based protocols and hemodynamic targets.""",
                "placeholders": [
                    "blood_pressure",
                    "map",
                    "heart_rate",
                    "cardiac_index",
                    "svr",
                    "cvp",
                    "diagnosis",
                    "fluid_status",
                    "cardiac_function",
                ],
            },
            "sedation": {
                "name": "Sedation & Analgesia Protocol",
                "description": "Optimize sedation strategy for mechanically ventilated patients",
                "template": """Develop sedation and analgesia plan:

Patient Status:
- Ventilation Mode: {vent_mode}
- Sedation Goal (RASS): {rass_target}
- Pain Score: {pain_score}
- Delirium Screening (CAM-ICU): {cam_icu}
- Agitation Level: {agitation}

Considerations:
- Renal Function: {renal_function}
- Liver Function: {liver_function}
- Contraindications: {contraindications}

Questions:
1. What sedation regimen is recommended?
2. What analgesic strategy is appropriate?
3. How to implement daily sedation interruption?
4. When can patient be assessed for extubation?
5. How to prevent/treat delirium?
6. What is the weaning plan?

Follow ICU Liberation Bundle (ABCDEF Bundle) principles.""",
                "placeholders": [
                    "vent_mode",
                    "rass_target",
                    "pain_score",
                    "cam_icu",
                    "agitation",
                    "renal_function",
                    "liver_function",
                    "contraindications",
                ],
            },
        },
        # 🩺 DIFFERENTIAL DIAGNOSIS
        "diagnosis": {
            "fever_workup": {
                "name": "Fever in ICU - Differential Diagnosis",
                "description": "Systematic approach to fever evaluation",
                "template": """Evaluate fever in ICU patient:

Fever Characteristics:
- Temperature: {temperature}°C
- Onset: {onset}
- Pattern: {pattern}
- Days in ICU: {icu_days}

Clinical Context:
- Lines/Tubes: {devices}
- Recent Procedures: {procedures}
- Medications: {medications}
- Imaging: {imaging}

Diagnostic Approach Needed:
1. What are the most likely infectious causes?
2. What are non-infectious causes (drug fever, VTE, etc.)?
3. What diagnostic workup is indicated?
4. Which devices should be evaluated/replaced?
5. Is empiric antibiotic therapy indicated?
6. What infection control measures are needed?

Use systematic "5 Lines and 5 Devices" approach.""",
                "placeholders": [
                    "temperature",
                    "onset",
                    "pattern",
                    "icu_days",
                    "devices",
                    "procedures",
                    "medications",
                    "imaging",
                ],
            },
            "shock_differentiation": {
                "name": "Shock State Differentiation",
                "description": "Identify shock type and guide treatment",
                "template": """Classify shock state and guide management:

Hemodynamics:
- Blood Pressure: {blood_pressure}
- MAP: {map}
- Heart Rate: {heart_rate}
- CVP: {cvp}
- Cardiac Output: {cardiac_output}
- SVR: {svr}
- ScvO2: {scvo2}%

Clinical Signs:
- Skin: {skin_findings}
- Urine Output: {urine_output}
- Lactate: {lactate}
- Mental Status: {mental_status}

Analysis Required:
1. What type of shock is present (distributive/cardiogenic/hypovolemic/obstructive)?
2. What is the underlying etiology?
3. What are the immediate resuscitation priorities?
4. What hemodynamic monitoring is needed?
5. What specific treatments are indicated?
6. What is the prognosis?

Use systematic shock classification and treatment algorithms.""",
                "placeholders": [
                    "blood_pressure",
                    "map",
                    "heart_rate",
                    "cvp",
                    "cardiac_output",
                    "svr",
                    "scvo2",
                    "skin_findings",
                    "urine_output",
                    "lactate",
                    "mental_status",
                ],
            },
        },
        # ⚕️ CLINICAL PROCEDURES
        "procedures": {
            "central_line": {
                "name": "Central Line Insertion Guidance",
                "description": "Pre-procedure planning and technique review",
                "template": """Guide central venous catheter insertion:

Patient Factors:
- Indication: {indication}
- Site Selection: {site}
- Coagulation Status (INR/Platelets): {coagulation}
- Anatomy Considerations: {anatomy}
- Previous CVC History: {history}

Pre-Procedure Questions:
1. What is the optimal site selection and why?
2. What are the contraindications?
3. What ultrasound technique should be used?
4. What are the key steps of sterile insertion?
5. What complications should be anticipated?
6. What post-procedure confirmation is needed?
7. How to maintain line and prevent CLABSI?

Include evidence-based practices and infection prevention.""",
                "placeholders": [
                    "indication",
                    "site",
                    "coagulation",
                    "anatomy",
                    "history",
                ],
            },
            "intubation_prep": {
                "name": "Intubation Preparation Checklist",
                "description": "Pre-intubation planning and medication selection",
                "template": """Prepare for emergency intubation:

Patient Assessment:
- Airway Exam: {airway_exam}
- SpO2: {spo2}%
- Blood Pressure: {blood_pressure}
- Mental Status: {mental_status}
- Aspiration Risk: {aspiration_risk}

Indication:
{indication}

Pre-Intubation Planning:
1. What are the difficult airway predictors?
2. What induction agents are appropriate?
3. What is the paralytic selection?
4. What pre-oxygenation strategy?
5. What is the backup plan if intubation fails?
6. What post-intubation sedation?
7. What ventilator settings initially?

Use rapid sequence intubation (RSI) protocol.""",
                "placeholders": [
                    "airway_exam",
                    "spo2",
                    "blood_pressure",
                    "mental_status",
                    "aspiration_risk",
                    "indication",
                ],
            },
        },
        # 🚨 EMERGENCY SITUATIONS
        "emergency": {
            "cardiac_arrest": {
                "name": "Cardiac Arrest Management",
                "description": "ACLS protocol and post-arrest care",
                "template": """Guide cardiac arrest management:

Arrest Details:
- Initial Rhythm: {rhythm}
- Location: {location}
- Witnessed: {witnessed}
- Time to CPR: {time_to_cpr}
- Suspected Cause: {suspected_cause}

Current Status:
- Duration of Arrest: {duration} minutes
- CPR Quality: {cpr_quality}
- Medications Given: {medications_given}

Management Questions:
1. What ACLS algorithm applies?
2. What reversible causes (H's and T's) to consider?
3. What medications/interventions are indicated now?
4. When to consider ECMO/mechanical CPR?
5. What is the prognosis?
6. What post-ROSC care is needed?
7. When to consider termination of efforts?

Follow current AHA ACLS guidelines.""",
                "placeholders": [
                    "rhythm",
                    "location",
                    "witnessed",
                    "time_to_cpr",
                    "suspected_cause",
                    "duration",
                    "cpr_quality",
                    "medications_given",
                ],
            },
            "massive_transfusion": {
                "name": "Massive Transfusion Protocol",
                "description": "Guide massive hemorrhage management",
                "template": """Activate and manage massive transfusion:

Bleeding Details:
- Source: {bleeding_source}
- Estimated Blood Loss: {blood_loss} mL
- Vital Signs: {vital_signs}
- Hemoglobin: {hemoglobin}
- INR: {inr}
- Platelets: {platelets}
- Fibrinogen: {fibrinogen}

Resuscitation Status:
- Products Given: {products_given}
- Ongoing Bleeding: {ongoing_bleeding}

Protocol Questions:
1. Should massive transfusion protocol be activated?
2. What is the recommended blood product ratio (RBC:FFP:Platelets)?
3. What adjunct medications (TXA, calcium, etc.)?
4. How to monitor coagulation status?
5. What are the goals of resuscitation?
6. What definitive hemorrhage control is needed?
7. When to consider damage control strategy?

Use balanced resuscitation and damage control principles.""",
                "placeholders": [
                    "bleeding_source",
                    "blood_loss",
                    "vital_signs",
                    "hemoglobin",
                    "inr",
                    "platelets",
                    "fibrinogen",
                    "products_given",
                    "ongoing_bleeding",
                ],
            },
        },
    }

    @classmethod
    def get_categories(cls) -> Dict[str, str]:
        """Get all available prompt categories"""
        return cls.CATEGORIES

    @classmethod
    def get_templates_by_category(cls, category: str) -> Dict:
        """Get all templates for a specific category"""
        return cls.TEMPLATES.get(category, {})

    @classmethod
    def get_template(cls, category: str, template_key: str) -> Optional[Dict]:
        """Get a specific template"""
        category_templates = cls.TEMPLATES.get(category, {})
        return category_templates.get(template_key)

    @classmethod
    def get_all_template_keys(cls) -> List[tuple]:
        """Get all (category, key, name) combinations"""
        result = []
        for category, templates in cls.TEMPLATES.items():
            for key, template_data in templates.items():
                result.append((category, key, template_data["name"]))
        return result

    @classmethod
    def format_template(cls, category: str, template_key: str, **kwargs) -> str:
        """
        Format a template with provided values

        Args:
            category: Template category
            template_key: Specific template key
            **kwargs: Values to fill in placeholders

        Returns:
            Formatted prompt string
        """
        template_data = cls.get_template(category, template_key)
        if not template_data:
            return ""

        template = template_data["template"]

        # Fill in provided values, leave others as placeholders
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))

        return template
