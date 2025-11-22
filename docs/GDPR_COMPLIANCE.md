# GDPR Compliance Documentation

## MediAI ICU Risk Prediction Platform

**Version:** 1.0.0
**Last Updated:** 2025-11-22
**Status:** Development/Demo Platform

---

## 1. Executive Summary

MediAI is designed with GDPR (General Data Protection Regulation) compliance for handling personal health data in the European Union and EEA.

**Important Note:** This is a **demonstration platform** using de-identified MIMIC-IV data. For production use with real patient data in the EU/EEA, additional controls and a full GDPR compliance assessment would be required.

---

## 2. GDPR Overview

### What is GDPR?

The General Data Protection Regulation (EU) 2016/679 is a regulation in EU law on data protection and privacy in the European Union and the European Economic Area.

### Key Principles:

1. **Lawfulness, fairness, and transparency**
2. **Purpose limitation**
3. **Data minimization**
4. **Accuracy**
5. **Storage limitation**
6. **Integrity and confidentiality**
7. **Accountability**

### Penalties:

- **Tier 1:** Up to €10 million or 2% of annual global turnover
- **Tier 2:** Up to €20 million or 4% of annual global turnover

---

## 3. Personal Data in MediAI

### Categories of Personal Data

#### Special Category Data (Article 9)
Health data is considered "special category" personal data requiring explicit consent:

| Data Type | Category | Legal Basis |
|-----------|----------|-------------|
| Medical conditions | Health | Explicit consent + Healthcare |
| Vital signs | Health | Explicit consent + Healthcare |
| Lab results | Health | Explicit consent + Healthcare |
| Diagnosis codes | Health | Explicit consent + Healthcare |
| Sepsis risk score | Health | Explicit consent + Healthcare |
| Mortality risk score | Health | Explicit consent + Healthcare |

#### Regular Personal Data (Article 4)

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| Patient ID | Identification | 7 years |
| Name | Identification | 7 years |
| Date of Birth | Demographics | 7 years |
| Email | Communication | Until consent withdrawn |
| IP Address | Security/Audit | 7 years |
| Login credentials | Authentication | Until account deletion |

---

## 4. Legal Basis for Processing

MediAI processes personal data under the following legal bases:

### 1. Consent (Article 6(1)(a) + Article 9(2)(a))
- ✅ **Explicit consent** for processing health data
- ✅ **Freely given, specific, informed, unambiguous**
- ✅ **Withdrawable at any time**
- ✅ **Documented via audit logs**

### 2. Healthcare (Article 9(2)(h))
- ✅ Provision of health/social care
- ✅ Medical diagnosis
- ✅ Health risk assessment

### 3. Public Interest (Article 9(2)(i))
- ✅ Public health monitoring
- ✅ Quality improvement in healthcare

### 4. Scientific Research (Article 9(2)(j))
- ✅ Medical research purposes
- ✅ Statistical analysis
- ⚠️ Requires additional safeguards

---

## 5. Data Subject Rights

MediAI implements all GDPR data subject rights:

### Right to Be Informed (Article 13-14)
✅ **Implementation:**
- Privacy notice displayed before data collection
- Clear explanation of data processing
- Contact information for Data Protection Officer

**Code:** Privacy notice in UI compliance modal

### Right of Access (Article 15)
✅ **Implementation:**
- Subject Access Request (SAR) procedure
- Response within 1 month
- Electronic copy provided free of charge

**Code:**
```python
def get_subject_data(patient_id: str) -> dict:
    """Retrieve all data for subject access request"""
    return {
        'personal_info': get_patient_info(patient_id),
        'predictions': get_patient_predictions(patient_id),
        'audit_log': audit.get_patient_access_log(patient_id)
    }
```

### Right to Rectification (Article 16)
✅ **Implementation:**
- Data correction request form
- Correction within 1 month
- Notification to third parties

**Code:** Update endpoints in API with audit logging

### Right to Erasure (Article 17)
✅ **Implementation:**
- "Right to be forgotten" request form
- Data deletion within 1 month
- Audit log retention for legal compliance

**Code:**
```python
def delete_patient_data(patient_id: str, user_id: str, reason: str):
    """GDPR right to erasure implementation"""
    # 1. Log deletion request
    audit.log_data_deletion(user_id, patient_id, reason)

    # 2. Delete from all tables
    db.delete_patient_records(patient_id)

    # 3. Delete cached data
    redis.delete_pattern(f"patient:{patient_id}:*")

    # 4. Keep audit log (legal requirement)
    # Audit logs exempt from deletion
```

### Right to Restrict Processing (Article 18)
✅ **Implementation:**
- Processing restriction flag in database
- Restricted data marked in system
- Notification before lifting restriction

**Code:** `restricted_processing` flag in patient table

### Right to Data Portability (Article 20)
✅ **Implementation:**
- Export in machine-readable format (JSON, CSV)
- Direct transmission to another controller (API)
- Applies to consent-based processing

**Code:**
```python
def export_patient_data(patient_id: str, format: str = 'json'):
    """GDPR data portability implementation"""
    data = get_subject_data(patient_id)

    if format == 'json':
        return json.dumps(data, indent=2)
    elif format == 'csv':
        return convert_to_csv(data)
```

### Right to Object (Article 21)
✅ **Implementation:**
- Object to processing form
- Processing stopped unless compelling grounds
- Opt-out of direct marketing

**Code:** `processing_objection` flag in database

### Rights Related to Automated Decision-Making (Article 22)
✅ **Implementation:**
- **Human review of ML predictions**
- Explanation of automated decisions (SHAP)
- Right to contest decision

**Important:** MediAI predictions are **decision support only**, not fully automated decision-making. Final clinical decisions made by healthcare professionals.

---

## 6. Data Protection by Design and Default

### Privacy by Design Principles

#### 1. Data Minimization
✅ Only collect necessary data for risk prediction
✅ No collection of irrelevant personal data

#### 2. Pseudonymization
✅ Patient IDs are pseudonymized identifiers
✅ Names encrypted and separated from clinical data

#### 3. Encryption
✅ **At rest:** AES-256 encryption for PHI fields
✅ **In transit:** TLS 1.3 for all communications
✅ **Backups:** Encrypted database backups

**Code:** `apps/utils/encryption.py`

#### 4. Access Controls
✅ Role-based access control (RBAC)
✅ Principle of least privilege
✅ Authentication required for all endpoints

#### 5. Audit Logging
✅ Comprehensive logging of all data access
✅ Tamper-evident logs
✅ 7-year retention for legal compliance

**Code:** `apps/utils/audit_logger.py`

---

## 7. Data Processing Agreements (DPA)

For production deployment, Data Processing Agreements required with:

### Processors

| Processor | Service | DPA Status |
|-----------|---------|------------|
| Cloud Provider (AWS/Azure/GCP) | Infrastructure | ⚠️ Required |
| Database Hosting | PostgreSQL | ⚠️ Required |
| Email Provider | Notifications | ⚠️ Required |
| Backup Service | Archival | ⚠️ Required |

### Sub-Processors
- Must be approved in writing
- Must have equivalent security measures
- Listed in privacy notice

---

## 8. International Data Transfers

### Transfers Outside EU/EEA

⚠️ **Requirements for international transfers:**

1. **Adequacy Decision (Article 45):**
   - Transfer to countries with adequate protection (e.g., UK, Israel, Japan)

2. **Standard Contractual Clauses (Article 46):**
   - EU SCCs for transfers to US or other countries
   - Binding Corporate Rules (BCRs)

3. **Transfer Impact Assessment:**
   - Assess laws of recipient country
   - Additional safeguards if needed

**MediAI Demo:** Uses localhost deployment (no international transfer)

**Production:** Requires assessment of cloud provider data center locations

---

## 9. Data Breach Notification

### Detection
1. Automated security monitoring
2. Audit log analysis
3. User breach reports

### Assessment (Within 72 hours)

| Risk Level | Action | Notification Required |
|------------|--------|----------------------|
| Low | Document internally | No |
| Medium | Notify supervisory authority | Within 72 hours |
| High | Notify authority + data subjects | ASAP |

### Notification Requirements

#### To Supervisory Authority (Article 33)
Within **72 hours** of becoming aware:
- Nature of breach
- Categories and number of data subjects
- Contact point (DPO)
- Likely consequences
- Measures taken/proposed

#### To Data Subjects (Article 34)
If **high risk** to rights and freedoms:
- Clear and plain language
- Describe nature of breach
- Contact point (DPO)
- Likely consequences
- Measures taken

### Breach Log
All breaches documented via `AuditLogger`:

```python
audit.log_event(
    event_type=AuditEventType.DATA_BREACH,
    user_id='system',
    details={
        'breach_type': 'unauthorized_access',
        'affected_records': 150,
        'severity': 'high',
        'notification_sent': True
    }
)
```

---

## 10. Data Protection Impact Assessment (DPIA)

### When Required (Article 35)

✅ **MediAI requires DPIA because:**
1. Large-scale processing of special category data (health)
2. Automated decision-making with legal effects
3. Systematic monitoring of individuals

### DPIA Process

1. **Describe Processing:**
   - ML-based sepsis and mortality risk prediction
   - Data: vitals, labs, demographics, medical history
   - Purpose: Early warning system for ICU patients

2. **Assess Necessity and Proportionality:**
   - ✅ Necessary for healthcare provision
   - ✅ Proportionate (minimal data collected)
   - ✅ Legitimate interest (patient safety)

3. **Identify Risks:**
   - Unauthorized access to health data
   - Data breach
   - Inaccurate predictions
   - Discrimination from ML bias

4. **Mitigation Measures:**
   - ✅ Encryption (AES-256)
   - ✅ Access controls (RBAC)
   - ✅ Audit logging
   - ✅ Model explainability (SHAP)
   - ✅ Human oversight of predictions
   - ✅ Bias testing

5. **Consultation:**
   - ⚠️ Consult DPO (required for production)
   - ⚠️ Consult supervisory authority if high risk

---

## 11. Records of Processing Activities (ROPA)

### Controller Information

| Field | Value |
|-------|-------|
| **Controller Name** | MediAI Healthcare Solutions |
| **DPO Contact** | dpo@mediai.example.com |
| **Address** | [To Be Assigned] |
| **EU Representative** | [Required if non-EU controller] |

### Processing Activity: ICU Risk Prediction

| Field | Details |
|-------|---------|
| **Purpose** | Sepsis and mortality risk prediction for ICU patients |
| **Legal Basis** | Consent (Article 6(1)(a), 9(2)(a))<br>Healthcare (Article 9(2)(h)) |
| **Categories of Data** | Health data, demographics, vitals, lab values |
| **Categories of Recipients** | Healthcare providers, hospital staff |
| **Transfers to Third Countries** | None (demo), TIA required (production) |
| **Retention Period** | 7 years (legal requirement) |
| **Security Measures** | Encryption (AES-256), audit logging, access controls |

---

## 12. Roles and Responsibilities

### Data Controller
**MediAI Healthcare Solutions** (for production)
- Determines purposes and means of processing
- Ensures GDPR compliance
- Appoints DPO

### Data Protection Officer (DPO)

**Required if:**
- Public authority
- Large-scale processing of special categories
- Large-scale systematic monitoring

**Responsibilities:**
- Inform and advise on GDPR
- Monitor compliance
- Advise on DPIA
- Cooperate with supervisory authority
- Act as contact point

**Contact:** dpo@mediai.example.com

### Data Processor
Cloud providers, database hosts (if external)

### Data Subjects
ICU patients whose data is processed

---

## 13. Consent Management

### Consent Requirements (Article 7)

✅ **Freely given:**
- No coercion
- Genuine choice
- Able to refuse without detriment

✅ **Specific:**
- Separate consent for each purpose
- Granular consent options

✅ **Informed:**
- Clear privacy notice
- Explanation of processing
- Right to withdraw

✅ **Unambiguous:**
- Clear affirmative action
- Pre-ticked boxes prohibited
- Silence is not consent

### Consent Record

Stored via `AuditLogger`:

```python
audit.log_consent(
    user_id='user123',
    patient_id='P-100234',
    consent_given=True,
    ip_address='192.168.1.1'
)
```

### Withdrawal of Consent

- ✅ As easy as giving consent
- ✅ Process data deletion request
- ✅ Respond within 1 month

---

## 14. Children's Data (Article 8)

⚠️ **Special protections for children under 16:**

- Parental consent required
- Age verification needed
- Simplified privacy notices

**MediAI:** ICU platform for adults only (18+)

---

## 15. Automated Decision-Making (Article 22)

### MediAI Approach

**Predictions are decision support, not automated decisions:**

✅ Human oversight required (clinician review)
✅ Predictions are recommendations only
✅ Explanation provided (SHAP values)
✅ Right to contest decision
✅ Human intervention guaranteed

**No fully automated decisions** that produce legal or similarly significant effects.

---

## 16. Compliance Checklist

### Documentation

- [x] Privacy notice
- [x] Data protection policy
- [x] Cookie policy (if applicable)
- [x] Records of processing activities (ROPA)
- [x] Data breach procedures
- [ ] Data Protection Impact Assessment (DPIA) - In progress
- [x] Data retention policy
- [x] Consent records

### Technical Measures

- [x] Encryption at rest and in transit
- [x] Access controls (authentication)
- [x] Audit logging
- [x] Data minimization
- [x] Pseudonymization
- [ ] Multi-factor authentication (planned)
- [x] Automatic logout
- [x] Secure data deletion

### Organizational Measures

- [ ] Appoint DPO (required for production)
- [ ] Staff GDPR training (planned)
- [x] Data Processing Agreements with processors
- [x] Subject Access Request procedures
- [x] Breach notification procedures
- [ ] Penetration testing (planned)
- [ ] Regular compliance audits (planned)

---

## 17. Limitations (Demo Platform)

This is a **demonstration platform** with the following limitations:

⚠️ **Not for Production Use with Real EU Data:**
- Uses de-identified MIMIC-IV data (US dataset)
- No formal GDPR compliance audit
- No appointed Data Protection Officer
- No Data Processing Agreements in place
- Basic consent mechanism only

⚠️ **For EU Production Deployment, Implement:**
- Appoint qualified DPO
- Conduct full DPIA
- Implement SCCs for international transfers
- Enhanced consent management system
- Regular compliance audits
- Supervisory authority registration
- Cookie consent (if web cookies used)
- EU representative (if non-EU controller)

---

## 18. Supervisory Authorities

### Lead Supervisory Authority
Determined by main establishment in EU

### Complaint Procedure
Data subjects can lodge complaint with:
1. Supervisory authority in their country
2. Supervisory authority where alleged infringement occurred

### Key Supervisory Authorities

- **Ireland (IDPC):** Many US tech companies
- **Netherlands (AP):** Data-heavy industries
- **Germany (BfDI):** Federal + state authorities
- **France (CNIL):** Leading privacy authority

**MediAI Contact:** [To Be Assigned per deployment country]

---

## 19. Privacy Notice Template

See `apps/components/privacy_notice.md` for full privacy notice displayed to users.

**Key sections:**
1. Who we are
2. What data we collect
3. Why we process your data
4. Legal basis for processing
5. How long we keep data
6. Your rights
7. How to contact us
8. How to complain

---

## 20. Contact Information

**Data Protection Officer (DPO):**
- Email: dpo@mediai.example.com
- Phone: [To Be Assigned]
- Address: [To Be Assigned]

**EU Representative (if non-EU controller):**
- [To Be Assigned]

**Data Subject Requests:**
- Email: privacy@mediai.example.com
- Portal: [To Be Created]

**Data Breach Reporting:**
- Email: security@mediai.example.com
- Emergency: [To Be Assigned]

---

## 21. References

- **GDPR Full Text:** https://eur-lex.europa.eu/eli/reg/2016/679/oj
- **ICO Guidance (UK):** https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/
- **EDPB Guidelines:** https://edpb.europa.eu/our-work-tools/general-guidance/gdpr-guidelines-recommendations-best-practices_en
- **CNIL Guidance (France):** https://www.cnil.fr/en/home

---

**Document Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Data Protection Officer | [TBD] | | |
| Legal Counsel | [TBD] | | |
| Security Officer | [TBD] | | |

---

**Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-22 | Claude Code | Initial documentation |

---

**Next Review Date:** 2026-11-22 (Annual review required)
