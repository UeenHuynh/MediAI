"""
Medical Knowledge Base Loader
Loads medical documents from various sources (files, URLs, APIs)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class MedicalKnowledgeLoader:
    """
    Load medical knowledge from various sources
    """

    def __init__(self, data_dir: str = "./data/medical_knowledge"):
        """
        Initialize knowledge loader

        Args:
            data_dir: Directory containing medical documents
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_text_file(self, file_path: str) -> Dict:
        """
        Load a text/markdown file

        Args:
            file_path: Path to text file

        Returns:
            Document dictionary with content and metadata
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = {
                "file_name": Path(file_path).name,
                "file_type": Path(file_path).suffix,
                "file_path": str(file_path),
            }

            return {"content": content, "metadata": metadata, "source": str(file_path)}

        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return None

    def load_json_file(self, file_path: str) -> List[Dict]:
        """
        Load medical data from JSON file

        Args:
            file_path: Path to JSON file

        Returns:
            List of document dictionaries
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            documents = []

            # Handle different JSON structures
            if isinstance(data, list):
                for idx, item in enumerate(data):
                    if isinstance(item, dict):
                        content = item.get("content") or item.get("text") or str(item)
                        metadata = item.get("metadata", {})
                        metadata["source_file"] = Path(file_path).name
                        metadata["index"] = idx

                        documents.append(
                            {
                                "content": content,
                                "metadata": metadata,
                                "source": f"{file_path}#{idx}",
                            }
                        )

            elif isinstance(data, dict):
                content = data.get("content") or data.get("text") or json.dumps(data)
                metadata = data.get("metadata", {})
                metadata["source_file"] = Path(file_path).name

                documents.append(
                    {"content": content, "metadata": metadata, "source": str(file_path)}
                )

            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents

        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return []

    def load_directory(self, directory: str = None) -> List[Dict]:
        """
        Load all supported files from a directory

        Args:
            directory: Directory path (defaults to self.data_dir)

        Returns:
            List of document dictionaries
        """
        directory = Path(directory) if directory else self.data_dir

        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []

        documents = []
        supported_extensions = [".txt", ".md", ".json"]

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                if file_path.suffix == ".json":
                    docs = self.load_json_file(str(file_path))
                    documents.extend(docs)
                else:
                    doc = self.load_text_file(str(file_path))
                    if doc:
                        documents.append(doc)

        logger.info(f"Loaded {len(documents)} documents from {directory}")
        return documents

    def create_sample_knowledge_base(self):
        """
        Create sample medical knowledge base files for testing
        """
        # Sepsis guidelines
        sepsis_content = """# Sepsis Recognition and Management Guidelines

## Definition
Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection.

## Quick Sequential Organ Failure Assessment (qSOFA)
Criteria (≥2 indicates higher risk):
- Respiratory rate ≥ 22/min
- Altered mentation (GCS < 15)
- Systolic blood pressure ≤ 100 mmHg

## SOFA Score
Sequential Organ Failure Assessment score ≥ 2 points indicates sepsis.

### SOFA Components:
1. **Respiratory**: PaO2/FiO2 ratio
2. **Coagulation**: Platelet count
3. **Liver**: Bilirubin level
4. **Cardiovascular**: Mean arterial pressure, vasopressor requirement
5. **Central Nervous System**: Glasgow Coma Scale
6. **Renal**: Creatinine or urine output

## Surviving Sepsis Campaign Hour-1 Bundle

### Immediate Actions (within 1 hour):
1. **Measure lactate level**
   - Normal: < 2 mmol/L
   - Elevated: ≥ 2 mmol/L indicates tissue hypoperfusion
   - Remeasure if elevated (target: normalization)

2. **Obtain blood cultures before antibiotics**
   - At least 2 sets (aerobic and anaerobic)
   - From different sites if possible
   - Do not delay antibiotics > 45 minutes

3. **Administer broad-spectrum antibiotics**
   - Within 1 hour of recognition
   - Empiric coverage based on suspected source
   - Common regimens: Piperacillin-tazobactam + Vancomycin

4. **Begin rapid fluid resuscitation**
   - 30 mL/kg crystalloid for hypotension or lactate ≥ 4 mmol/L
   - Reassess hemodynamic status frequently
   - Balanced crystalloids (Ringer's lactate) or 0.9% saline

5. **Apply vasopressors if hypotensive**
   - Target MAP ≥ 65 mmHg
   - Norepinephrine first-line
   - Consider vasopressin or epinephrine as second-line

## Source Control
- Identify infection source
- Drain abscesses
- Remove infected devices
- Débride infected tissue
- Consider imaging (CT, ultrasound)

## Monitoring
- Serial lactate measurements (q2-4h until normalized)
- Vital signs (continuous if unstable)
- Urine output (target ≥ 0.5 mL/kg/hr)
- Fluid balance
- Organ function (labs q6-12h)

## Red Flags
⚠️ **Immediate ICU consultation needed:**
- Lactate > 4 mmol/L
- Systolic BP < 90 mmHg despite fluids
- Respiratory failure
- Altered mental status
- Multi-organ dysfunction

## Evidence Base
Based on Surviving Sepsis Campaign Guidelines 2021
Level of Evidence: High (Grade 1B recommendations)

## References
1. Evans L, et al. Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med. 2021;49(11):e1063-e1143.
2. Singer M, et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA. 2016;315(8):801-810.
"""

        # Mortality risk factors
        mortality_content = """# ICU Mortality Risk Assessment

## Overview
ICU mortality prediction helps guide clinical decision-making, resource allocation, and family communication.

## Major Risk Factors

### Patient Demographics
- **Age**: Mortality increases with age (especially > 65 years)
- **Comorbidities**:
  - Chronic heart failure
  - Chronic kidney disease
  - Chronic liver disease
  - Malignancy
  - Immunosuppression

### Severity of Illness Scores

#### APACHE II (Acute Physiology and Chronic Health Evaluation)
- Range: 0-71 points
- Mortality correlation:
  - 0-4: < 4%
  - 5-9: 8%
  - 10-14: 15%
  - 15-19: 25%
  - 20-24: 40%
  - 25-29: 55%
  - 30-34: 75%
  - ≥ 35: > 85%

#### SOFA Score
- Sequential Organ Failure Assessment
- Daily assessment of organ dysfunction
- Increasing SOFA score indicates worsening prognosis

### Organ Dysfunction

#### Respiratory
- Mechanical ventilation requirement
- PaO2/FiO2 ratio < 200 (moderate-severe ARDS)
- Prolonged ventilation (> 7 days)

#### Cardiovascular
- Vasopressor requirement
- High-dose vasopressors (norepinephrine > 0.2 mcg/kg/min)
- Cardiac arrest
- Cardiogenic shock

#### Renal
- Acute kidney injury (AKI)
- Need for renal replacement therapy (RRT)
- Oliguria (urine output < 0.5 mL/kg/hr)

#### Hepatic
- Bilirubin > 12 mg/dL
- Acute liver failure
- Hepatic encephalopathy

#### Hematologic
- Severe thrombocytopenia (< 50,000)
- Disseminated intravascular coagulation (DIC)
- Severe anemia requiring transfusion

#### Neurologic
- Decreased Glasgow Coma Scale (GCS < 8)
- Intracranial hypertension
- Stroke

### Laboratory Markers

#### Metabolic
- **Lactate elevation**:
  - 2-4 mmol/L: Increased risk
  - > 4 mmol/L: High risk
  - Lactate clearance < 10% in 6 hours: Poor prognosis
- **Severe acidosis** (pH < 7.2)
- **Base deficit** > 6 mEq/L

#### Inflammatory
- Procalcitonin > 10 ng/mL
- C-reactive protein > 150 mg/L
- Persistent leukocytosis or leukopenia

### Clinical Factors

#### Septic Shock
- Sepsis with persistent hypotension requiring vasopressors
- Lactate > 2 mmol/L despite adequate fluid resuscitation
- Mortality: 30-50%

#### Multi-Organ Dysfunction Syndrome (MODS)
- Failure of ≥ 2 organ systems
- Mortality increases with each additional organ failure

#### Refractory Status
- Shock refractory to vasopressors
- Hypoxemia refractory to high FiO2/PEEP
- Acidosis refractory to treatment

## Prognostic Models

### Risk Stratification
- **Low Risk** (< 10% mortality):
  - Single organ dysfunction
  - Responsive to initial therapy
  - Low APACHE II score (< 15)

- **Moderate Risk** (10-30% mortality):
  - Multiple organ dysfunction (2-3 organs)
  - Partial response to therapy
  - Moderate APACHE II score (15-24)

- **High Risk** (> 30% mortality):
  - Severe multi-organ failure (≥ 3 organs)
  - Refractory shock
  - High APACHE II score (≥ 25)

## Clinical Decision Making

### Goals of Care Discussion
Consider when:
- Mortality risk > 50%
- Progressive organ failure despite maximal therapy
- Poor quality of life anticipated
- Patient/family wishes

### Palliative Care Consultation
Appropriate for:
- High mortality risk with poor functional outcome
- Patient/family request
- Refractory symptoms
- Ethical dilemmas

## Limitations of Prediction
- Individual variability
- Response to therapy
- Comorbidities and baseline function
- Age and frailty
- Prediction models are probabilistic, not deterministic

## Communication
- Discuss prognosis with empathy
- Use ranges rather than exact percentages
- Acknowledge uncertainty
- Focus on quality of life and patient values
- Involve family in shared decision-making

## References
1. Knaus WA, et al. APACHE II: a severity of disease classification system. Crit Care Med. 1985;13(10):818-829.
2. Vincent JL, et al. Use of the SOFA score to assess the incidence of organ dysfunction/failure in intensive care units. Crit Care Med. 1998;26(11):1793-1800.
"""

        # Common ICU medications
        medications_content = """# Common ICU Medications Reference

## Vasopressors and Inotropes

### Norepinephrine (Levophed)
**Indication**: First-line vasopressor for septic shock
**Mechanism**: Alpha-1 (vasoconstriction) >> Beta-1 (inotropy)
**Dosing**:
- Start: 0.01-0.05 mcg/kg/min
- Usual: 0.1-0.3 mcg/kg/min
- Max: 3 mcg/kg/min (consider adding second agent)
**Target**: MAP ≥ 65 mmHg
**Monitoring**: Continuous BP, peripheral perfusion
**Adverse Effects**: Peripheral ischemia, arrhythmias

### Vasopressin (Pitressin)
**Indication**: Second-line vasopressor, catecholamine-sparing
**Mechanism**: V1 receptor agonist (vasoconstriction)
**Dosing**: Fixed dose 0.03-0.04 units/min (do not titrate)
**Use**: Add to norepinephrine, never as sole agent
**Adverse Effects**: Decreased cardiac output, splanchnic ischemia
**Note**: Beneficial in septic shock due to relative vasopressin deficiency

### Epinephrine (Adrenaline)
**Indication**: Refractory shock, cardiac arrest, anaphylaxis
**Mechanism**: Alpha and Beta agonist
**Dosing**:
- Shock: 0.01-0.5 mcg/kg/min
- Cardiac arrest: 1 mg IV push q3-5min
**Adverse Effects**: Tachycardia, arrhythmias, hyperglycemia, lactate elevation
**Caution**: Can increase lactate without tissue hypoperfusion

### Dobutamine
**Indication**: Cardiogenic shock, low cardiac output
**Mechanism**: Beta-1 agonist (inotropy and chronotropy)
**Dosing**: 2.5-20 mcg/kg/min
**Adverse Effects**: Tachycardia, arrhythmias, hypotension
**Contraindication**: Severe hypotension without vasopressor support

## Sedatives and Analgesics

### Propofol (Diprivan)
**Indication**: Sedation for mechanical ventilation
**Mechanism**: GABA agonist
**Dosing**: 5-50 mcg/kg/min
**Advantages**: Rapid on/off, anticonvulsant
**Adverse Effects**: Hypotension, hypertriglyceridemia, propofol infusion syndrome
**Monitoring**: Triglycerides if > 48 hours
**Caution**: Pancreatitis risk, avoid prolonged use at high doses

### Dexmedetomidine (Precedex)
**Indication**: Sedation, especially for extubation trials
**Mechanism**: Alpha-2 agonist
**Dosing**: 0.2-1.4 mcg/kg/hr (no bolus)
**Advantages**: No respiratory depression, less delirium
**Adverse Effects**: Bradycardia, hypotension
**Note**: Facilitates lighter sedation and spontaneous breathing

### Fentanyl
**Indication**: Analgesia, sedation adjunct
**Mechanism**: Mu opioid agonist
**Dosing**:
- Bolus: 25-100 mcg IV q5-15min PRN
- Infusion: 25-200 mcg/hr
**Advantages**: No histamine release, rapid onset
**Adverse Effects**: Respiratory depression, chest wall rigidity (high doses)

### Midazolam (Versed)
**Indication**: Short-term sedation (< 48 hours)
**Mechanism**: GABA agonist (benzodiazepine)
**Dosing**: 1-10 mg/hr IV infusion
**Adverse Effects**: Delirium, prolonged sedation, accumulation
**Caution**: Avoid prolonged use due to delirium risk

## Antibiotics (Empiric Sepsis Coverage)

### Piperacillin-Tazobactam (Zosyn)
**Coverage**: Broad-spectrum, including Pseudomonas
**Dosing**: 3.375-4.5 g IV q6h or 3.375 g IV q8h
**Use**: Intra-abdominal infections, healthcare-associated infections
**Adjust**: Renal dosing required

### Vancomycin
**Coverage**: MRSA, coagulase-negative Staphylococcus
**Dosing**: 15-20 mg/kg IV q8-12h (loading dose 25-30 mg/kg)
**Target**: Trough 15-20 mcg/mL (serious infections)
**Monitoring**: Trough levels, renal function
**Adverse Effects**: Nephrotoxicity (especially with other nephrotoxins)

### Meropenem
**Coverage**: Broad-spectrum carbapenem
**Dosing**: 1-2 g IV q8h
**Use**: Severe sepsis, resistant organisms, meningitis
**Adjust**: Renal dosing required

### Cefepime
**Coverage**: Broad gram-negative including Pseudomonas, good gram-positive
**Dosing**: 1-2 g IV q8-12h
**Use**: Febrile neutropenia, nosocomial pneumonia
**Caution**: Neurotoxicity in renal failure

## Anticoagulation

### Heparin (Unfractionated)
**Indication**: VTE prophylaxis/treatment, ECMO, CRRT
**Dosing**:
- Prophylaxis: 5,000 units SC q8-12h
- Treatment: 80 units/kg bolus, then 18 units/kg/hr infusion
**Monitoring**: aPTT (target 1.5-2.5x control for treatment)
**Reversal**: Protamine sulfate

### Enoxaparin (Lovenox)
**Indication**: VTE prophylaxis/treatment
**Dosing**:
- Prophylaxis: 40 mg SC daily or 30 mg SC q12h
- Treatment: 1 mg/kg SC q12h
**Advantages**: No monitoring required, less HIT
**Contraindication**: CrCl < 30 mL/min (use UFH)

## Important Drug Interactions
- Propofol + vasopressors: Increased hypotension risk
- Fentanyl + benzodiazepines: Synergistic respiratory depression
- Vancomycin + piperacillin-tazobactam: Increased nephrotoxicity risk
- Multiple nephrotoxins: Monitor renal function closely

## Renal Dosing Adjustments
Most medications require adjustment for:
- CrCl < 50 mL/min
- CRRT/hemodialysis
- Consult pharmacy for specific dosing
"""

        # Write files
        files_to_create = [
            (self.data_dir / "sepsis_guidelines.md", sepsis_content),
            (self.data_dir / "mortality_risk_assessment.md", mortality_content),
            (self.data_dir / "icu_medications.md", medications_content),
        ]

        for file_path, content in files_to_create:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Created sample knowledge base file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create {file_path}: {e}")

        logger.info(f"Sample knowledge base created in {self.data_dir}")

    def load_pubmed_abstracts(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Load PubMed abstracts (requires Bio.Entrez)

        Args:
            query: PubMed search query
            max_results: Maximum number of results

        Returns:
            List of document dictionaries
        """
        try:
            from Bio import Entrez

            # Set email for NCBI
            Entrez.email = "your.email@example.com"

            # Search PubMed
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()

            id_list = record["IdList"]

            if not id_list:
                logger.info(f"No PubMed results for query: {query}")
                return []

            # Fetch abstracts
            handle = Entrez.efetch(
                db="pubmed", id=id_list, rettype="abstract", retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            documents = []
            for article in records["PubmedArticle"]:
                try:
                    medline = article["MedlineCitation"]
                    article_data = medline["Article"]

                    title = article_data.get("ArticleTitle", "")
                    abstract = article_data.get("Abstract", {}).get(
                        "AbstractText", [""]
                    )[0]

                    if abstract:
                        content = f"# {title}\n\n{abstract}"
                        pmid = medline["PMID"]

                        metadata = {
                            "pmid": str(pmid),
                            "title": title,
                            "source_type": "pubmed",
                        }

                        documents.append(
                            {
                                "content": content,
                                "metadata": metadata,
                                "source": f"PMID:{pmid}",
                            }
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed article: {e}")
                    continue

            logger.info(f"Loaded {len(documents)} PubMed abstracts for query: {query}")
            return documents

        except ImportError:
            logger.error("Biopython not installed. Install with: pip install biopython")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch PubMed abstracts: {e}")
            return []
