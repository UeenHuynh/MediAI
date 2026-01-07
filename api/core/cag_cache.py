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
