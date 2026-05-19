"""
CAG (Cache-Augmented Generation) - Layer 4
Static medical knowledge cache for instant retrieval (~50ms)
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class CAGCache:
    """
    Cache-Augmented Generation (CAG) System

    Stores curated medical knowledge as Python dict for instant lookup.
    No external DB needed - version controlled in code.

    Benefits:
    - Ultra-fast retrieval (~50ms vs 500ms for vector search)
    - No API calls needed
    - Guaranteed accurate content (manually curated)
    - Version controlled with code
    """

    # Reference URLs for each knowledge entry
    REFERENCE_URLS = {
        "sepsis_definition": "https://jamanetwork.com/journals/jama/fullarticle/2492881",
        "sepsis_management": "https://journals.lww.com/ccmjournal/fulltext/2021/11000/surviving_sepsis_campaign__international.21.aspx",
        "sofa_score": "https://jamanetwork.com/journals/jama/fullarticle/2492881",
        "aki_kdigo": "https://kdigo.org/guidelines/acute-kidney-injury/",
        "ards_management": "https://www.nejm.org/doi/full/10.1056/NEJMoa1214103",
        "norepinephrine": "https://journals.lww.com/ccmjournal/fulltext/2021/11000/surviving_sepsis_campaign__international.21.aspx",
        "vasopressin": "https://www.nejm.org/doi/full/10.1056/NEJMoa067373",
        "mortality_risk_factors": "https://pubmed.ncbi.nlm.nih.gov/15312219/",
        "shock_classification": "https://doi.org/10.1007/s00134-014-3525-z",
        "mechanical_ventilation": "https://www.nejm.org/doi/full/10.1056/NEJMoa1214103",
        "postop_complications": "https://www.east.org/education-resources/practice-management-guidelines",
        "copd_exacerbation": "https://goldcopd.org/2024-gold-report/",
        "heart_failure_icu": "https://doi.org/10.1093/eurheartj/ehad195",
        "end_of_life_icu": "https://www.ama-assn.org/delivering-care/ethics/code-medical-ethics-overview",
        "fluid_resuscitation": "https://journals.lww.com/ccmjournal/fulltext/2021/11000/surviving_sepsis_campaign__international.21.aspx",
        "acid_base": "https://pubmed.ncbi.nlm.nih.gov/10650234/",
        "sedation_analgesia": "https://journals.lww.com/ccmjournal/fulltext/2018/09000/clinical_practice_guidelines_for_the_prevention.29.aspx",
        "antibiotic_icu": "https://journals.lww.com/ccmjournal/fulltext/2021/11000/surviving_sepsis_campaign__international.21.aspx",
    }

    # Static medical knowledge cache
    MEDICAL_KNOWLEDGE = {
        # ==================== SEPSIS ====================
        "sepsis_definition": {
            "content": """**Sepsis (Sepsis-3 Definition)**

Sepsis is defined as life-threatening organ dysfunction caused by a dysregulated host response to infection.

**Diagnostic Criteria:**
- Suspected or confirmed infection
- Acute increase in SOFA score ≥2 points
- Baseline SOFA assumed to be 0 unless chronic organ dysfunction present

**Septic Shock:**
- Sepsis + persistent hypotension requiring vasopressors
- Serum lactate >2 mmol/L despite adequate fluid resuscitation
- Hospital mortality >40%

**Key Points:**
- SIRS criteria no longer required for sepsis diagnosis
- qSOFA can be used for rapid screening (≥2: RR≥22, GCS≤13, SBP≤100)
- Early recognition and treatment critical for survival""",
            "keywords": [
                "sepsis",
                "septic shock",
                "sepsis-3",
                "sofa",
                "infection",
                "organ dysfunction",
            ],
            "category": "disease",
            "source": "Sepsis-3 Consensus (JAMA 2016)",
            "priority": 10,
        },
        "sepsis_management": {
            "content": """**Sepsis Management Bundle (Surviving Sepsis Campaign)**

**Hour-1 Bundle (Critical):**
1. Measure lactate level
2. Obtain blood cultures before antibiotics
3. Administer broad-spectrum antibiotics
4. Begin rapid fluid resuscitation (30 mL/kg crystalloid)
5. Apply vasopressors if hypotensive during/after fluid resuscitation

**Initial Resuscitation (First 6 hours):**
- Target MAP ≥65 mmHg
- Target urine output ≥0.5 mL/kg/hr
- Consider CVP 8-12 mmHg (if available)

**Antimicrobial Therapy:**
- Broad-spectrum within 1 hour
- De-escalate based on culture results
- Duration: typically 7-10 days

**Source Control:**
- Identify and control infection source within 12 hours
- Remove infected devices
- Drain abscesses

**Vasopressor Choice:**
- First-line: Norepinephrine (target MAP ≥65)
- Second-line: Vasopressin or epinephrine
- Avoid dopamine (increased arrhythmia risk)

**Steroids:**
- Consider hydrocortisone 200mg/day if refractory shock
- Do NOT use for non-shock sepsis""",
            "keywords": [
                "sepsis management",
                "sepsis bundle",
                "surviving sepsis",
                "resuscitation",
                "antibiotics",
                "vasopressors",
            ],
            "category": "protocol",
            "source": "Surviving Sepsis Campaign Guidelines 2021",
            "priority": 10,
        },
        # ==================== SOFA SCORE ====================
        "sofa_score": {
            "content": """**SOFA Score (Sequential Organ Failure Assessment)**

Used to assess organ dysfunction in ICU patients. Score 0-4 for each system.

**1. Respiratory (PaO2/FiO2)**
- 0: ≥400 mmHg
- 1: <400 mmHg
- 2: <300 mmHg
- 3: <200 mmHg with respiratory support
- 4: <100 mmHg with respiratory support

**2. Coagulation (Platelets)**
- 0: ≥150,000/μL
- 1: <150,000/μL
- 2: <100,000/μL
- 3: <50,000/μL
- 4: <20,000/μL

**3. Liver (Bilirubin)**
- 0: <1.2 mg/dL
- 1: 1.2-1.9 mg/dL
- 2: 2.0-5.9 mg/dL
- 3: 6.0-11.9 mg/dL
- 4: ≥12.0 mg/dL

**4. Cardiovascular (MAP or vasopressors)**
- 0: MAP ≥70 mmHg
- 1: MAP <70 mmHg
- 2: Dopamine ≤5 or dobutamine (any dose)
- 3: Dopamine >5 or epi/norepi ≤0.1
- 4: Dopamine >15 or epi/norepi >0.1

**5. CNS (Glasgow Coma Scale)**
- 0: GCS 15
- 1: GCS 13-14
- 2: GCS 10-12
- 3: GCS 6-9
- 4: GCS <6

**6. Renal (Creatinine or urine output)**
- 0: <1.2 mg/dL
- 1: 1.2-1.9 mg/dL
- 2: 2.0-3.4 mg/dL
- 3: 3.5-4.9 mg/dL or UO <500 mL/day
- 4: ≥5.0 mg/dL or UO <200 mL/day

**Interpretation:**
- Total score: 0-24
- Score ≥2: Organ dysfunction (sepsis criterion)
- Higher scores associated with increased mortality""",
            "keywords": [
                "sofa score",
                "sofa",
                "organ dysfunction",
                "organ failure",
                "icu scoring",
            ],
            "category": "scoring",
            "source": "JAMA 1996;276:707-713",
            "priority": 10,
        },
        # ==================== ACUTE KIDNEY INJURY ====================
        "aki_kdigo": {
            "content": """**Acute Kidney Injury (KDIGO Criteria)**

**AKI Definition (any of the following):**
1. Serum creatinine increase ≥0.3 mg/dL within 48 hours
2. Serum creatinine increase ≥1.5x baseline within 7 days
3. Urine output <0.5 mL/kg/hr for 6 hours

**KDIGO Stages:**

**Stage 1:**
- SCr: 1.5-1.9x baseline OR ≥0.3 mg/dL increase
- UO: <0.5 mL/kg/hr for 6-12 hours

**Stage 2:**
- SCr: 2.0-2.9x baseline
- UO: <0.5 mL/kg/hr for ≥12 hours

**Stage 3:**
- SCr: ≥3.0x baseline OR ≥4.0 mg/dL OR RRT initiated
- UO: <0.3 mL/kg/hr for ≥24 hours OR anuria for ≥12 hours

**Management:**
- Identify and treat underlying cause
- Optimize hemodynamics (avoid hypotension)
- Avoid nephrotoxins (NSAIDs, aminoglycosides, contrast)
- Adjust medication doses
- Monitor electrolytes (K+, PO4)
- Consider RRT if: severe acidosis, hyperkalemia, uremia, volume overload

**Common Causes in ICU:**
- Pre-renal: Hypoperfusion, hypovolemia
- Intra-renal: ATN, sepsis, contrast, drugs
- Post-renal: Obstruction (rare in ICU)""",
            "keywords": [
                "aki",
                "acute kidney injury",
                "kdigo",
                "creatinine",
                "renal failure",
                "dialysis",
            ],
            "category": "guideline",
            "source": "KDIGO Clinical Practice Guideline 2012",
            "priority": 9,
        },
        # ==================== MECHANICAL VENTILATION ====================
        "ards_management": {
            "content": """**ARDS Management (Berlin Definition)**

**ARDS Criteria:**
- Timing: Within 1 week of known insult
- Imaging: Bilateral opacities on CXR/CT
- Origin: Not fully explained by cardiac failure/fluid overload
- Oxygenation (PaO2/FiO2 on PEEP ≥5):
  - Mild: 200-300 mmHg
  - Moderate: 100-200 mmHg
  - Severe: <100 mmHg

**Lung-Protective Ventilation:**
- Tidal volume: 6 mL/kg predicted body weight (PBW)
- Plateau pressure: ≤30 cm H2O
- PEEP: Use ARDSnet table (higher PEEP in moderate/severe)
- FiO2: Titrate to SpO2 88-95%
- Permissive hypercapnia acceptable (pH >7.25)

**Adjunct Therapies:**

**Prone Positioning (moderate-severe ARDS):**
- ≥16 hours/day
- PaO2/FiO2 <150 mmHg
- Significant mortality benefit

**Neuromuscular Blockade (early severe ARDS):**
- Consider if PaO2/FiO2 <150 mmHg in first 48 hours
- Cisatracurium 48-hour infusion
- Controversial (more recent data neutral)

**Recruitment Maneuvers:**
- May improve oxygenation temporarily
- Use cautiously (risk of barotrauma)

**ECMO:**
- Consider if severe ARDS refractory to above
- PaO2/FiO2 <80 mmHg or pH <7.25 despite optimization
- Requires specialized center""",
            "keywords": [
                "ards",
                "mechanical ventilation",
                "lung protective",
                "prone positioning",
                "peep",
            ],
            "category": "protocol",
            "source": "ARDS Network Protocol, PROSEVA Trial",
            "priority": 9,
        },
        # ==================== MEDICATIONS ====================
        "norepinephrine": {
            "content": """**Norepinephrine (Levophed)**

**Indications:**
- First-line vasopressor for septic shock
- Distributive shock (sepsis, anaphylaxis, neurogenic)
- Hypotension refractory to fluid resuscitation

**Mechanism:**
- Potent α1-adrenergic agonist (vasoconstriction)
- Mild β1-adrenergic effects (increased inotropy)

**Dosing:**
- Start: 0.05-0.1 mcg/kg/min (typically 5-10 mcg/min for 70kg adult)
- Titrate: Increase by 0.05-0.1 mcg/kg/min every 5-10 minutes
- Target: MAP ≥65 mmHg
- Maximum: Typically 0.5-3 mcg/kg/min (higher doses indicate refractory shock)

**Administration:**
- MUST use central line (tissue necrosis if extravasates)
- Never bolus - continuous infusion only
- Compatible with D5W, NS, LR

**Monitoring:**
- MAP continuously (arterial line preferred)
- Heart rate (reflex bradycardia possible)
- Urine output (renal perfusion)
- Lactate clearance
- Digital perfusion (risk of ischemia)

**Side Effects:**
- Arrhythmias
- Tissue ischemia (digits, bowel, kidneys)
- Increased myocardial oxygen demand
- Extravasation → tissue necrosis (treat with phentolamine)

**Drug Interactions:**
- MAOIs: Exaggerated hypertension
- TCAs: Enhanced pressor response
- Beta-blockers: Unopposed alpha effects

**When to Add Second Agent:**
- If requiring >0.5 mcg/kg/min and MAP still <65:
  - Add vasopressin 0.03-0.04 units/min, OR
  - Add epinephrine if cardiac output low""",
            "keywords": [
                "norepinephrine",
                "levophed",
                "vasopressor",
                "shock",
                "septic shock",
                "hypotension",
            ],
            "category": "drug",
            "source": "Surviving Sepsis Campaign, Clinical Pharmacology",
            "priority": 8,
        },
        "vasopressin": {
            "content": """**Vasopressin (ADH)**

**Indications:**
- Second-line vasopressor in septic shock
- Add to norepinephrine if MAP <65 despite moderate doses

**Mechanism:**
- V1 receptor: Vasoconstriction (vascular smooth muscle)
- V2 receptor: Antidiuretic (renal collecting duct)
- Works via different pathway than catecholamines

**Dosing:**
- Fixed dose: 0.03-0.04 units/min IV (do NOT titrate)
- Never used as sole agent (always with norepinephrine)
- NOT weight-based

**Administration:**
- Central or peripheral line acceptable
- Continuous infusion
- Do NOT titrate up (higher doses → ischemia)

**Benefits:**
- Catecholamine-sparing effect
- May reduce norepinephrine requirements
- Restores vasopressin deficiency in septic shock
- Preserves renal blood flow

**Monitoring:**
- MAP
- Norepinephrine dose reduction
- Signs of ischemia (ECG, digits, bowel)
- Sodium (can cause hyponatremia at high doses)

**Side Effects:**
- Coronary/peripheral ischemia
- Hyponatremia (water retention)
- Decreased cardiac output
- Bronchoconstriction (rare)

**Contraindications:**
- Use cautiously in coronary artery disease
- Avoid as sole agent (always with norepi)

**When to Use:**
- If norepinephrine >0.25-0.5 mcg/kg/min and MAP still <65
- Alternative to epinephrine as second agent""",
            "keywords": [
                "vasopressin",
                "adh",
                "vasopressor",
                "septic shock",
                "catecholamine sparing",
            ],
            "category": "drug",
            "source": "VASST Trial, Surviving Sepsis Campaign",
            "priority": 7,
        },
        # ==================== MORTALITY RISK ====================
        "mortality_risk_factors": {
            "content": """**ICU Mortality Risk Factors**

**Major Risk Factors (Strong Association):**

**1. Severity of Illness:**
- High SOFA score (≥10: mortality >50%)
- High APACHE II score (≥25: mortality >50%)
- Septic shock (mortality 30-40%)
- Multiple organ failure (mortality increases with each organ)

**2. Age:**
- >65 years: increased mortality
- >75 years: significantly increased mortality
- >85 years: very high mortality (>50% in sepsis)

**3. Comorbidities:**
- Chronic kidney disease (especially ESRD)
- Cirrhosis (especially Child-Pugh C)
- Advanced malignancy
- Chronic heart failure (EF <30%)
- Chronic lung disease (on home O2)
- Immunosuppression (HIV, chemotherapy, transplant)

**4. Acute Conditions:**
- Severe ARDS (PaO2/FiO2 <100)
- Refractory shock (high-dose pressors >24 hours)
- Acute liver failure
- Severe traumatic brain injury (GCS <8)

**5. Laboratory Markers:**
- Lactate >4 mmol/L (mortality ~30-40%)
- Lactate not clearing (<10% in 6 hours)
- Severe acidosis (pH <7.2)
- Severe coagulopathy (platelets <20k, INR >3)
- Severe hyperkalemia (K >7)

**6. Treatment Factors:**
- Delayed antibiotic administration (>1 hour in sepsis)
- Inadequate initial resuscitation
- Prolonged mechanical ventilation (>7 days)
- Need for renal replacement therapy
- Cardiac arrest with CPR

**Protective Factors:**
- Young age
- No comorbidities
- Early recognition and treatment
- Appropriate source control
- Good functional status pre-ICU

**Risk Stratification:**
- Low risk (<10%): SOFA <5, single organ, responsive to treatment
- Moderate risk (10-30%): SOFA 5-10, 2 organs, improving
- High risk (>30%): SOFA >10, ≥3 organs, refractory shock

**Communication:**
- Use objective data (scores, trends)
- Avoid "futility" language
- Focus on goals of care
- Involve palliative care when appropriate""",
            "keywords": [
                "mortality",
                "prognosis",
                "risk factors",
                "icu mortality",
                "apache",
                "sofa score",
            ],
            "category": "guideline",
            "source": "Multiple ICU Outcome Studies",
            "priority": 9,
        },
        # ==================== NORMAL VALUES ====================
        "normal_lab_values": {
            "content": """**Normal Laboratory Values (ICU Reference)**

**Complete Blood Count:**
- WBC: 4.5-11.0 × 10³/μL
- Hemoglobin: M 13.5-17.5, F 12.0-15.5 g/dL
- Hematocrit: M 40-52%, F 36-48%
- Platelets: 150-400 × 10³/μL

**Basic Metabolic Panel:**
- Sodium: 135-145 mEq/L
- Potassium: 3.5-5.0 mEq/L
- Chloride: 98-107 mEq/L
- Bicarbonate: 22-29 mEq/L
- BUN: 7-20 mg/dL
- Creatinine: 0.6-1.2 mg/dL
- Glucose: 70-100 mg/dL (fasting)

**Arterial Blood Gas:**
- pH: 7.35-7.45
- PaCO2: 35-45 mmHg
- PaO2: 75-100 mmHg
- HCO3: 22-26 mEq/L
- Base Excess: -2 to +2
- SaO2: >95%

**Liver Function:**
- ALT: 7-56 U/L
- AST: 10-40 U/L
- Alkaline Phosphatase: 30-120 U/L
- Total Bilirubin: 0.1-1.2 mg/dL
- Albumin: 3.5-5.5 g/dL
- INR: 0.8-1.2

**Cardiac:**
- Troponin I: <0.04 ng/mL
- BNP: <100 pg/mL
- NT-proBNP: <125 pg/mL

**Coagulation:**
- PT: 11-13.5 seconds
- PTT: 25-35 seconds
- INR: 0.8-1.2
- Fibrinogen: 200-400 mg/dL
- D-dimer: <500 ng/mL

**Other:**
- Lactate: 0.5-2.2 mmol/L (critical if >4)
- CRP: <10 mg/L
- Procalcitonin: <0.5 ng/mL
- Magnesium: 1.7-2.2 mg/dL
- Phosphate: 2.5-4.5 mg/dL
- Calcium: 8.5-10.5 mg/dL""",
            "keywords": [
                "normal values",
                "lab values",
                "reference ranges",
                "laboratory",
                "labs",
            ],
            "category": "reference",
            "source": "Clinical Laboratory Standards",
            "priority": 6,
        },
        # ==================== EMERGENCY RECOGNITION ====================
        "emergency_signs": {
            "content": """**Critical Emergency Signs Requiring IMMEDIATE Intervention**

**Airway/Breathing:**
- Respiratory rate >30 or <8
- SpO2 <90% on supplemental O2
- Severe stridor or upper airway obstruction
- Apnea or agonal breathing
- Inability to speak in full sentences

**Circulation:**
- SBP <90 mmHg or MAP <65 mmHg
- HR >130 or <40 bpm
- New chest pain with ECG changes (STEMI)
- Uncontrolled bleeding

**Neurologic:**
- GCS <8 or decrease ≥2 points
- New focal deficits (stroke code)
- Seizure >5 minutes or status epilepticus
- Sudden severe headache (possible SAH)

**Metabolic:**
- Glucose <50 or >400 mg/dL
- Severe acidosis (pH <7.2)
- Severe hyperkalemia (K >6.5 with ECG changes)

**Actions:**
1. Call for help immediately
2. Assess ABCs
3. Apply supplemental oxygen
4. Establish IV access
5. Call rapid response/code team if indicated
6. Notify attending physician stat""",
            "keywords": [
                "emergency",
                "critical",
                "urgent",
                "code",
                "rapid response",
                "life threatening",
            ],
            "category": "protocol",
            "source": "Emergency Medicine Guidelines",
            "priority": 10,
        },
        # ==================== SHOCK ====================
        "shock_classification": {
            "content": """Shock Classification & ICU Management

Types of Shock:
1. Distributive (septic, anaphylactic, neurogenic) - low SVR, high/normal CO
2. Cardiogenic - low CO, high SVR, high filling pressures
3. Hypovolemic (hemorrhagic, dehydration) - low CO, low filling pressures
4. Obstructive (PE, tamponade, tension pneumothorax) - low CO, mechanical obstruction

Mixed Shock: Common in ICU. Example: septic + cardiogenic in patient with pre-existing HF.

Key Hemodynamic Parameters:
- MAP target ≥65 mmHg (higher in chronic hypertension)
- CVP: low in hypovolemic, high in cardiogenic/obstructive
- ScvO2: <70% suggests inadequate DO2 (low CO or high extraction)
- Lactate: >2 mmol/L indicates tissue hypoperfusion
- Cardiac index: <2.2 L/min/m2 = cardiogenic

POCUS Assessment (5-point):
1. Heart: LV/RV function, pericardial effusion
2. IVC: collapsibility (volume status)
3. Lungs: B-lines (pulmonary edema), pleural effusion
4. Abdomen: free fluid
5. DVT: femoral/popliteal veins

Vasopressor Selection:
- Norepinephrine: first-line for most shock
- Vasopressin: add if NE >0.25-0.5 mcg/kg/min
- Epinephrine: anaphylaxis, or add for low CO
- Dobutamine/Milrinone: cardiogenic shock (inotrope)
- Phenylephrine: pure vasoconstriction (avoid in low CO)""",
            "keywords": [
                "shock", "sốc", "cardiogenic", "distributive", "hypovolemic",
                "obstructive", "mixed shock", "sốc hỗn hợp", "hemodynamic",
                "huyết động", "vasopressor", "MAP", "CVP", "ScvO2", "POCUS",
                "cardiac output", "tamponade", "PE",
            ],
            "category": "critical_care",
            "source": "Surviving Sepsis Campaign 2021; ESICM Consensus on Circulatory Shock 2014",
            "priority": 9,
        },
        # ==================== MECHANICAL VENTILATION ====================
        "mechanical_ventilation": {
            "content": """Mechanical Ventilation in ICU

Indications for Intubation:
- Failure to protect airway (GCS ≤8)
- Refractory hypoxemia (PaO2/FiO2 <150 despite NIV/HFNC)
- Severe respiratory acidosis (pH <7.20, PaCO2 rising)
- Respiratory fatigue, accessory muscle use
- Hemodynamic instability requiring airway control

Lung-Protective Ventilation (ARDS Network):
- Tidal volume: 6 mL/kg predicted body weight
- Plateau pressure: <30 cmH2O
- Driving pressure: <15 cmH2O
- PEEP: titrate per FiO2/PEEP table or best compliance
- Target: pH 7.25-7.45, PaO2 55-80, SpO2 88-95%

HFNC vs NIV vs Intubation:
- HFNC: hypoxemic failure, post-extubation, comfort. Does NOT reduce PaCO2.
- NIV (BiPAP): COPD exacerbation (reduces PaCO2), cardiogenic pulmonary edema, immunocompromised.
- Intubation: failure of above, GCS drop, hemodynamic instability, unable to protect airway.

NIV Failure Criteria (consider intubation):
- No improvement in pH/PaCO2 within 1-2 hours
- Worsening mental status
- Inability to clear secretions
- Hemodynamic instability
- PaO2/FiO2 <150 despite FiO2 >60%

Ventilator-Associated Complications:
- VILI (barotrauma, volutrauma, atelectrauma)
- VAP (ventilator-associated pneumonia)
- Auto-PEEP (air trapping in COPD/asthma)
- Hemodynamic compromise (reduced venous return with high PEEP)""",
            "keywords": [
                "ventilation", "thở máy", "intubation", "NKQ", "nội khí quản",
                "HFNC", "NIV", "BiPAP", "ARDS", "PEEP", "tidal volume",
                "lung protective", "extubation", "FiO2", "PaO2", "respiratory failure",
                "suy hô hấp", "khó thở", "COPD", "auto-PEEP",
            ],
            "category": "critical_care",
            "source": "ARDS Network Protocol; BTS/ICS Guidelines for NIV 2016",
            "priority": 9,
        },
        # ==================== POST-OPERATIVE COMPLICATIONS ====================
        "postop_complications": {
            "content": """Post-Operative ICU Complications

Life-Threatening Complications (first 72h):
1. Hemorrhage: tachycardia, hypotension, dropping Hb, drain output >200mL/h
2. Anastomotic leak: fever, tachycardia, peritonitis, drain output change (day 3-7)
3. Pulmonary embolism: sudden dyspnea, hypoxia, tachycardia, RV strain on echo
4. Cardiac event (MI/arrhythmia): chest pain, ECG changes, troponin rise
5. Abdominal compartment syndrome: tense abdomen, oliguria, high airway pressures

Post-Colectomy Specific:
- Anastomotic leak rate: 3-6% (higher in low anterior resection)
- Presents day 3-7: fever, tachycardia, peritonitis, feculent drain
- CT with oral contrast for diagnosis
- Management: NPO, antibiotics, percutaneous drainage vs reoperation

Massive Transfusion Protocol (MTP):
- Trigger: anticipated need for >10 units RBC in 24h, or >4 units in 1h
- Ratio: 1:1:1 (RBC:FFP:Platelets)
- Targets: Hb >7, platelets >50K, fibrinogen >1.5, INR <1.5
- Calcium replacement (citrate toxicity)
- Permissive hypotension (MAP 50-60) until surgical control

Sepsis Post-Op:
- Source control is priority (drain abscess, reoperate if needed)
- Broad-spectrum antibiotics covering anaerobes
- Common sources: wound, intra-abdominal, UTI, line infection, pneumonia""",
            "keywords": [
                "post-op", "hậu phẫu", "surgery", "phẫu thuật", "colectomy",
                "anastomotic leak", "hemorrhage", "chảy máu", "bleeding",
                "PE", "pulmonary embolism", "thuyên tắc phổi",
                "abdominal compartment", "MTP", "massive transfusion",
                "drain", "peritonitis",
            ],
            "category": "critical_care",
            "source": "ERAS Society Guidelines; Eastern Association for Surgery of Trauma (EAST)",
            "priority": 8,
        },
        # ==================== COPD EXACERBATION ====================
        "copd_exacerbation": {
            "content": """COPD Acute Exacerbation in ICU

Severity Assessment:
- Mild: increased dyspnea, no respiratory failure
- Moderate: pH 7.25-7.35, PaCO2 45-70
- Severe: pH <7.25, PaCO2 >70, altered mental status

Management Stepwise:
1. Bronchodilators: salbutamol + ipratropium nebulized q20min x3, then q4-6h
2. Systemic corticosteroids: methylprednisolone 40mg IV or prednisone 40mg PO x5 days
3. Antibiotics: if purulent sputum or requiring ventilation (amoxicillin-clavulanate or azithromycin)
4. Oxygen: target SpO2 88-92% (avoid hyperoxia → CO2 retention)
5. NIV (BiPAP): FIRST-LINE for pH <7.35 with hypercapnia. IPAP 10-20, EPAP 4-8 cmH2O
6. Intubation: if NIV fails (no pH improvement in 1-2h), GCS drop, hemodynamic instability

Key Pitfalls:
- HFNC does NOT reduce PaCO2 — not a substitute for NIV in hypercapnic failure
- SpO2 97% with PaCO2 85 = oxygen-induced hypercapnia (Haldane effect)
- High FiO2 suppresses hypoxic drive → worsens CO2 retention
- Auto-PEEP: set extrinsic PEEP at 80% of measured auto-PEEP

ABG Interpretation in COPD:
- Acute on chronic: expected HCO3 rise = 1 mEq/L per 10 mmHg PaCO2 (acute) or 3.5 (chronic)
- pH <7.25 with high PaCO2 despite NIV → intubation threshold
- Mixed disorder: if HCO3 32 with pH 7.15 and PaCO2 85 → acute-on-chronic with inadequate compensation""",
            "keywords": [
                "COPD", "copd", "exacerbation", "đợt cấp", "hypercapnia",
                "CO2", "PaCO2", "BiPAP", "NIV", "bronchodilator",
                "respiratory acidosis", "toan hô hấp", "auto-PEEP",
                "oxygen therapy", "SpO2",
            ],
            "category": "critical_care",
            "source": "GOLD 2024 Guidelines; BTS/ICS Acute Hypercapnic Respiratory Failure Guidelines",
            "priority": 9,
        },
        # ==================== CARDIAC / HEART FAILURE ====================
        "heart_failure_icu": {
            "content": """Heart Failure in ICU - Acute Decompensation

Classification:
- HFrEF (EF <40%): systolic failure, reduced contractility
- HFpEF (EF ≥50%): diastolic failure, impaired relaxation
- Cardiogenic shock: CI <2.2, PCWP >18, SBP <90 despite volume

Acute Management:
1. Warm & Wet (most common): vasodilators (nitroglycerin, nitroprusside) + diuretics
2. Cold & Wet (cardiogenic shock): inotropes (dobutamine, milrinone) ± vasopressors
3. Cold & Dry: cautious fluid challenge, inotropes
4. Warm & Dry: optimize oral medications

Inotrope Selection:
- Dobutamine: β1 agonist, increases CO, may cause hypotension (β2 vasodilation)
- Milrinone: PDE3 inhibitor, increases CO + vasodilation, good for RV failure and pulmonary HTN
- Levosimendan: calcium sensitizer, no increase in O2 demand

Key Considerations in ICU:
- Fluid restriction: avoid bolus >250mL without reassessment
- PEEP interaction: positive pressure reduces preload (beneficial in pulmonary edema) but may worsen RV failure
- Beta-blockers: do NOT stop abruptly in chronic HF; hold if cardiogenic shock
- ACEi/ARB: hold if SBP <90 or AKI
- Target MAP 60-65 (not higher — reduces afterload)

Monitoring:
- Echocardiography: EF, RV function, valvular disease
- PA catheter (Swan-Ganz): if unclear hemodynamics
- Lactate, ScvO2, urine output as perfusion markers""",
            "keywords": [
                "heart failure", "suy tim", "EF", "cardiogenic shock",
                "sốc tim", "dobutamine", "milrinone", "inotrope",
                "pulmonary edema", "phù phổi", "PCWP", "cardiac index",
                "decompensation", "beta-blocker", "RV failure",
            ],
            "category": "critical_care",
            "source": "ESC Heart Failure Guidelines 2023; SCAI Cardiogenic Shock Classification",
            "priority": 9,
        },
        # ==================== END-OF-LIFE / PALLIATIVE ====================
        "end_of_life_icu": {
            "content": """End-of-Life & Palliative Care in ICU

Advance Directives:
- DNR (Do Not Resuscitate): no CPR/defibrillation if cardiac arrest
- DNI (Do Not Intubate): no endotracheal intubation
- DNR ≠ DNI: patient may accept intubation but not CPR, or vice versa
- AND (Allow Natural Death): comfort measures only

Patient Autonomy:
- Competent patient's wishes override family requests
- Capacity assessment: can patient understand, appreciate, reason, and communicate?
- If patient has capacity and refuses intervention → must respect even if family disagrees
- Document capacity assessment clearly in chart

Symptom Management (comfort):
- Dyspnea: morphine 2-4mg IV q2-4h (reduces air hunger without hastening death)
- Anxiety: midazolam 1-2mg IV, or lorazepam 0.5-1mg
- Secretions: glycopyrrolate 0.2mg IV q4h
- Oxygen: for comfort (nasal cannula, HFNC), not to target SpO2

Communication Framework (SPIKES):
1. Setting: private, sit down, family present
2. Perception: what does family understand?
3. Invitation: how much do they want to know?
4. Knowledge: deliver information clearly
5. Emotions: acknowledge and validate
6. Strategy/Summary: plan next steps

Conflict Resolution (patient vs family):
- Reaffirm patient's documented wishes
- Ethics consultation if unresolved
- Palliative care team involvement
- Family meeting with multidisciplinary team""",
            "keywords": [
                "DNR", "DNI", "palliative", "end of life", "comfort care",
                "withdrawal", "rút ống", "ngừng hồi sức", "gia đình",
                "autonomy", "capacity", "morphine", "dyspnea", "terminal",
                "ung thư", "cancer", "prognosis",
            ],
            "category": "ethics",
            "source": "AMA Code of Medical Ethics; AAHPM Palliative Care Guidelines",
            "priority": 8,
        },
        # ==================== FLUID RESUSCITATION ====================
        "fluid_resuscitation": {
            "content": """Fluid Resuscitation in ICU

Fluid Responsiveness Assessment:
- Passive Leg Raise (PLR): raise legs 45° for 1 min → if CO increases >10% = fluid responsive
- Pulse Pressure Variation (PPV): >13% on mechanical ventilation = fluid responsive
- IVC collapsibility: >50% (spontaneous breathing) or >18% distensibility (ventilated)
- Mini fluid challenge: 100mL over 1 min, assess stroke volume change

When NOT to Give Fluid:
- CVP >12-15 cmH2O with no improvement after prior bolus
- B-lines on lung ultrasound (pulmonary edema)
- IVC plethoric and non-collapsible
- Known EF <30% without evidence of hypovolemia
- Positive fluid balance >5L in first 72h (associated with worse outcomes)

Fluid Types:
- Balanced crystalloid (Ringer's Lactate, Plasmalyte): preferred over NS
- Normal saline: hyperchloremic acidosis risk, avoid in AKI
- Albumin 4-5%: consider in sepsis after 30mL/kg crystalloid
- Avoid: HES (renal injury), gelatin (anaphylaxis risk)

SSC 2021 Recommendation:
- Initial: 30 mL/kg crystalloid within first 3 hours for sepsis-induced hypoperfusion
- BUT: individualize in heart failure, ESRD, fluid overload
- Reassess after each 250-500mL bolus
- Dynamic measures preferred over static (CVP alone is poor predictor)""",
            "keywords": [
                "fluid", "dịch", "resuscitation", "hồi sức", "bolus",
                "crystalloid", "PLR", "passive leg raise", "IVC",
                "fluid responsive", "CVP", "overload", "quá tải",
                "albumin", "Ringer", "normal saline",
            ],
            "category": "critical_care",
            "source": "Surviving Sepsis Campaign 2021; ESICM FENICE Study",
            "priority": 8,
        },
        # ==================== ACID-BASE ====================
        "acid_base": {
            "content": """Acid-Base Disorders in ICU

Systematic Approach:
1. Look at pH: <7.35 = acidemia, >7.45 = alkalemia
2. Primary disorder: PaCO2 (respiratory) or HCO3 (metabolic)
3. Compensation: expected vs actual
4. Anion gap: Na - (Cl + HCO3), normal 8-12
5. Delta-delta: if AG elevated, (ΔAG)/(ΔHCO3) — detects hidden disorders

Common ICU Patterns:
- Lactic acidosis (AG metabolic acidosis): shock, sepsis, mesenteric ischemia
- Respiratory acidosis: COPD, sedation, neuromuscular disease, ARDS
- Mixed respiratory + metabolic acidosis: cardiac arrest, severe sepsis
- Metabolic alkalosis: vomiting, diuretics, contraction alkalosis

Life-Threatening Acid-Base:
- pH <7.10: cardiac arrest risk, consider bicarbonate if pH <7.10 with hemodynamic instability
- pH <7.20 with respiratory cause: intubation threshold
- Severe hyperkalemia + acidosis: calcium, insulin/glucose, bicarbonate, dialysis

Lactate Interpretation:
- Type A (hypoperfusion): shock, cardiac arrest, mesenteric ischemia
- Type B (non-hypoperfusion): liver failure, medications (metformin, epinephrine), seizures
- Clearance >10% in 2h = good prognostic sign
- Persistent lactate >4 despite resuscitation = high mortality""",
            "keywords": [
                "acid-base", "toan kiềm", "pH", "acidosis", "alkalosis",
                "lactate", "anion gap", "HCO3", "bicarbonate",
                "metabolic acidosis", "respiratory acidosis",
                "hyperkalemia", "tăng kali",
            ],
            "category": "critical_care",
            "source": "Stewart Approach to Acid-Base; Kellum JA Critical Care 2000",
            "priority": 8,
        },
        # ==================== SEDATION & ANALGESIA ====================
        "sedation_analgesia": {
            "content": """ICU Sedation & Analgesia (PADIS Guidelines 2018)

Pain First (Analgesia-First Approach):
- Assess pain before sedation (BPS or CPOT scale for intubated patients)
- Fentanyl: 25-100 mcg IV bolus, infusion 25-200 mcg/h
- Morphine: 2-4 mg IV q2-4h
- Ketamine: 0.1-0.5 mg/kg/h (opioid-sparing, bronchodilator)

Sedation:
- Target light sedation (RASS 0 to -2) unless specific indication for deep
- Propofol: 5-50 mcg/kg/min (short-acting, daily wake-up)
- Dexmedetomidine: 0.2-1.5 mcg/kg/h (no respiratory depression, delirium prevention)
- Midazolam: avoid if possible (delirium risk, accumulation)

Daily Sedation Interruption (DSI):
- Stop sedation daily, assess neurological status
- Paired with spontaneous breathing trial (SBT)
- Reduces ventilator days and ICU LOS

Delirium (CAM-ICU):
- Prevention: early mobilization, sleep hygiene, avoid benzodiazepines
- Treatment: address underlying cause, dexmedetomidine, avoid haloperidol in QTc >500ms
- Risk factors: age, pre-existing dementia, sepsis, benzodiazepines, immobility

Neuromuscular Blockade:
- Indication: severe ARDS (PaO2/FiO2 <150), refractory ICP, shivering in TTM
- Cisatracurium: 1-3 mcg/kg/min (organ-independent metabolism)
- Always ensure adequate sedation + analgesia before paralysis
- Train-of-four monitoring""",
            "keywords": [
                "sedation", "an thần", "analgesia", "giảm đau", "pain",
                "fentanyl", "propofol", "dexmedetomidine", "midazolam",
                "delirium", "RASS", "CAM-ICU", "paralysis",
                "neuromuscular blockade", "ketamine",
            ],
            "category": "critical_care",
            "source": "PADIS Guidelines 2018 (SCCM); ICU Liberation Bundle (A2F)",
            "priority": 7,
        },
        # ==================== ANTIBIOTIC THERAPY ====================
        "antibiotic_icu": {
            "content": """Empiric Antibiotic Therapy in ICU

Principles:
- Administer within 1 hour of sepsis recognition (each hour delay = 7% mortality increase)
- Broad-spectrum initially, de-escalate based on cultures at 48-72h
- Source control is equally important as antibiotics

Common ICU Infections & Empiric Coverage:
1. Community-acquired pneumonia (severe): ceftriaxone + azithromycin (or respiratory FQ)
2. Hospital-acquired/VAP: piperacillin-tazobactam or meropenem + vancomycin (if MRSA risk)
3. Intra-abdominal: piperacillin-tazobactam or meropenem (covers anaerobes)
4. Urosepsis: ceftriaxone or piperacillin-tazobactam
5. Skin/soft tissue (necrotizing): meropenem + vancomycin + clindamycin
6. Meningitis: ceftriaxone + vancomycin + ampicillin (if >50yo or immunocompromised)
7. Line infection: vancomycin + cefepime; remove line if possible

De-escalation:
- Narrow spectrum based on culture & sensitivity at 48-72h
- Procalcitonin-guided discontinuation (PCT <0.5 or >80% decrease)
- Duration: 7 days for most infections (shorter is better if responding)

Dosing in Critical Illness:
- Augmented renal clearance (ARC): may need higher doses of renally-cleared drugs
- Continuous/extended infusion beta-lactams: better PK/PD in sepsis
- Therapeutic drug monitoring: vancomycin (AUC/MIC), aminoglycosides""",
            "keywords": [
                "antibiotic", "kháng sinh", "empiric", "sepsis",
                "pneumonia", "viêm phổi", "VAP", "MRSA",
                "meropenem", "vancomycin", "piperacillin",
                "de-escalation", "procalcitonin", "infection", "nhiễm trùng",
            ],
            "category": "critical_care",
            "source": "Surviving Sepsis Campaign 2021; IDSA Guidelines",
            "priority": 9,
        },
    }

    def __init__(self):
        """Initialize CAG cache"""
        self.cache = self.MEDICAL_KNOWLEDGE
        logger.info(f"✅ CAG Cache initialized with {len(self.cache)} medical topics")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search cache for relevant medical knowledge

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching cache entries with scores
        """
        query_lower = query.lower()
        matches = []

        for key, data in self.cache.items():
            # Check if any keyword matches query
            keyword_matches = sum(
                1 for keyword in data["keywords"] if keyword in query_lower
            )

            if keyword_matches > 0:
                # Calculate relevance score
                score = keyword_matches / len(data["keywords"])
                score *= data["priority"] / 10  # Weight by priority

                matches.append(
                    {
                        "key": key,
                        "content": data["content"],
                        "category": data["category"],
                        "source": data["source"],
                        "keywords": data["keywords"],
                        "score": score,
                        "tier": "cag",
                        "metadata": {
                            "title": data["source"],
                            "url": self.REFERENCE_URLS.get(key),
                        },
                    }
                )

        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)

        logger.info(f"🔍 CAG search: '{query[:50]}...' → {len(matches)} matches")
        return matches[:top_k]

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all entries for a specific category"""
        return [
            {"key": key, **data}
            for key, data in self.cache.items()
            if data["category"] == category
        ]

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        categories = {}
        for data in self.cache.values():
            cat = data["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_entries": len(self.cache),
            "categories": categories,
            "avg_content_length": sum(len(d["content"]) for d in self.cache.values())
            // len(self.cache),
        }


# Example usage
if __name__ == "__main__":
    cache = CAGCache()

    # Test searches
    test_queries = [
        "What is sepsis?",
        "SOFA score calculation",
        "norepinephrine dosing",
        "acute kidney injury criteria",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("=" * 60)
        results = cache.search(query, top_k=2)

        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Key: {result['key']}")
            print(f"    Category: {result['category']}")
            print(f"    Score: {result['score']:.2f}")
            print(f"    Content preview: {result['content'][:150]}...")

    print(f"\n{'='*60}")
    print("Cache Statistics:")
    print("=" * 60)
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
