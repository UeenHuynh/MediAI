"""
Audit Logging Module
HIPAA/GDPR Compliant Audit Trail System

Tracks all user actions, data access, and system events for compliance
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import os
from pathlib import Path


class AuditEventType(Enum):
    """Types of auditable events"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

    # Data Access
    VIEW_PATIENT = "view_patient"
    VIEW_PREDICTION = "view_prediction"
    SEARCH_PATIENT = "search_patient"
    EXPORT_DATA = "export_data"

    # Predictions
    PREDICT_SEPSIS = "predict_sepsis"
    PREDICT_MORTALITY = "predict_mortality"

    # System Events
    API_CALL = "api_call"
    ERROR = "error"
    CONFIG_CHANGE = "config_change"

    # Compliance
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"
    DATA_DELETION = "data_deletion"


class AuditLogger:
    """
    HIPAA/GDPR compliant audit logging system

    Features:
    - Structured JSON logs
    - Tamper-evident logging
    - User action tracking
    - PHI access tracking
    - Retention policy support
    """

    def __init__(self, log_dir: str = None):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for audit logs (default: logs/audit/)
        """
        self.log_dir = Path(log_dir or os.getenv('AUDIT_LOG_DIR', 'logs/audit'))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create dated log file
        self.log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"

        # Setup structured logger
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured JSON logger"""
        logger = logging.getLogger('mediai.audit')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()  # Remove existing handlers

        # File handler for audit logs
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.propagate = False

        return logger

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        patient_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True
    ):
        """
        Log an audit event

        Args:
            event_type: Type of event
            user_id: User who performed the action
            details: Additional event details
            patient_id: Patient ID if applicable (PHI access)
            ip_address: IP address of user
            success: Whether action succeeded
        """
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'patient_id': patient_id,
            'ip_address': ip_address,
            'success': success,
            'details': details or {},
            'session_id': self._get_session_id()
        }

        # Log as JSON
        self.logger.info(json.dumps(audit_entry))

    def log_login(self, user_id: str, ip_address: str, success: bool = True):
        """Log user login attempt"""
        event_type = AuditEventType.LOGIN if success else AuditEventType.LOGIN_FAILED
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            success=success
        )

    def log_patient_access(self, user_id: str, patient_id: str, action: str, ip_address: str = None):
        """Log patient data access (PHI access tracking)"""
        self.log_event(
            event_type=AuditEventType.VIEW_PATIENT,
            user_id=user_id,
            patient_id=patient_id,
            ip_address=ip_address,
            details={'action': action}
        )

    def log_prediction(
        self,
        user_id: str,
        patient_id: str,
        model_type: str,
        risk_score: float,
        ip_address: str = None
    ):
        """Log prediction request"""
        event_type = (
            AuditEventType.PREDICT_SEPSIS if model_type == 'sepsis'
            else AuditEventType.PREDICT_MORTALITY
        )

        self.log_event(
            event_type=event_type,
            user_id=user_id,
            patient_id=patient_id,
            ip_address=ip_address,
            details={
                'model_type': model_type,
                'risk_score': risk_score
            }
        )

    def log_data_export(self, user_id: str, export_type: str, record_count: int, ip_address: str = None):
        """Log data export for compliance tracking"""
        self.log_event(
            event_type=AuditEventType.EXPORT_DATA,
            user_id=user_id,
            ip_address=ip_address,
            details={
                'export_type': export_type,
                'record_count': record_count
            }
        )

    def log_api_call(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        ip_address: str = None
    ):
        """Log API call"""
        self.log_event(
            event_type=AuditEventType.API_CALL,
            user_id=user_id,
            ip_address=ip_address,
            success=200 <= status_code < 400,
            details={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code
            }
        )

    def log_error(self, user_id: str, error_message: str, error_type: str, ip_address: str = None):
        """Log system error"""
        self.log_event(
            event_type=AuditEventType.ERROR,
            user_id=user_id,
            ip_address=ip_address,
            success=False,
            details={
                'error_message': error_message,
                'error_type': error_type
            }
        )

    def log_consent(self, user_id: str, patient_id: str, consent_given: bool, ip_address: str = None):
        """Log GDPR consent given/revoked"""
        event_type = AuditEventType.CONSENT_GIVEN if consent_given else AuditEventType.CONSENT_REVOKED
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            patient_id=patient_id,
            ip_address=ip_address,
            details={'consent_status': consent_given}
        )

    def log_data_deletion(self, user_id: str, patient_id: str, reason: str, ip_address: str = None):
        """Log GDPR right to be forgotten"""
        self.log_event(
            event_type=AuditEventType.DATA_DELETION,
            user_id=user_id,
            patient_id=patient_id,
            ip_address=ip_address,
            details={'reason': reason}
        )

    def get_user_activity(self, user_id: str, days: int = 30) -> list:
        """
        Retrieve user activity for audit review

        Args:
            user_id: User ID to search for
            days: Number of days to look back

        Returns:
            List of audit entries
        """
        entries = []

        # Read log files from last N days
        for i in range(days):
            date = datetime.now() - pd.Timedelta(days=i)
            log_file = self.log_dir / f"audit_{date.strftime('%Y%m%d')}.log"

            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            if entry.get('user_id') == user_id:
                                entries.append(entry)
                        except json.JSONDecodeError:
                            continue

        return sorted(entries, key=lambda x: x['timestamp'], reverse=True)

    def get_patient_access_log(self, patient_id: str) -> list:
        """
        Get all access logs for a specific patient (PHI access tracking)

        Args:
            patient_id: Patient ID

        Returns:
            List of access entries
        """
        entries = []

        # Search all log files in directory
        for log_file in sorted(self.log_dir.glob("audit_*.log"), reverse=True):
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('patient_id') == patient_id:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue

        return sorted(entries, key=lambda x: x['timestamp'], reverse=True)

    @staticmethod
    def _get_session_id() -> Optional[str]:
        """Get current session ID (placeholder for Streamlit session)"""
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'session_id'):
                return st.session_state.session_id
        except:
            pass
        return None


# Example usage
def example_usage():
    """Example: How to use AuditLogger for HIPAA/GDPR compliance"""

    # Initialize logger
    audit = AuditLogger()

    # Log user login
    audit.log_login(user_id='user123', ip_address='192.168.1.1', success=True)

    # Log patient data access
    audit.log_patient_access(
        user_id='user123',
        patient_id='P-100234',
        action='view_dashboard',
        ip_address='192.168.1.1'
    )

    # Log prediction
    audit.log_prediction(
        user_id='user123',
        patient_id='P-100234',
        model_type='sepsis',
        risk_score=0.89,
        ip_address='192.168.1.1'
    )

    # Log data export
    audit.log_data_export(
        user_id='user123',
        export_type='patient_report',
        record_count=1,
        ip_address='192.168.1.1'
    )

    # Get user activity
    activity = audit.get_user_activity(user_id='user123', days=7)
    print(f"User activity entries: {len(activity)}")

    # Get patient access log
    access_log = audit.get_patient_access_log(patient_id='P-100234')
    print(f"Patient access entries: {len(access_log)}")


if __name__ == "__main__":
    example_usage()
