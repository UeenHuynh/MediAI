"""
Prediction History Service

Handles saving and retrieving prediction history from database.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.prediction import Prediction


class PredictionHistoryService:
    """Service for prediction history management"""

    @staticmethod
    def save_prediction(
        db: Session,
        prediction_type: str,
        input_features: dict,
        risk_score: float,
        risk_percentage: float,
        model_version: str = "v2",
        model_file: Optional[str] = None,
        shap_values: Optional[dict] = None,
        top_features: Optional[dict] = None,
        patient_id: Optional[int] = None,
        predicted_by: Optional[int] = None,
    ) -> Prediction:
        """
        Save a prediction to the database

        Args:
            db: Database session
            prediction_type: 'sepsis' or 'mortality'
            input_features: Dictionary of input features
            risk_score: Prediction score (0.0-1.0)
            risk_percentage: Risk as percentage (0.0-100.0)
            model_version: Model version used
            model_file: Path to model file used
            shap_values: SHAP values for explainability
            top_features: Top contributing features
            patient_id: Optional patient ID
            predicted_by: User ID who made the prediction

        Returns:
            Created Prediction object
        """
        # Calculate risk category
        if risk_percentage < 10:
            risk_category = "low"
        elif risk_percentage < 30:
            risk_category = "medium"
        elif risk_percentage < 70:
            risk_category = "high"
        else:
            risk_category = "critical"

        prediction = Prediction(
            patient_id=patient_id,
            prediction_type=prediction_type,
            model_version=model_version,
            model_file=model_file,
            input_features=input_features,
            risk_score=Decimal(str(risk_score)),
            risk_percentage=Decimal(str(risk_percentage)),
            risk_category=risk_category,
            shap_values=shap_values,
            top_features=top_features,
            predicted_by=predicted_by,
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def get_prediction(db: Session, prediction_id: int) -> Optional[Prediction]:
        """
        Get prediction by ID

        Args:
            db: Database session
            prediction_id: Prediction ID

        Returns:
            Prediction object or None if not found
        """
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    @staticmethod
    def list_predictions_for_patient(
        db: Session,
        patient_id: int,
        prediction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Prediction], int]:
        """
        List all predictions for a specific patient

        Args:
            db: Database session
            patient_id: Patient ID
            prediction_type: Optional filter by 'sepsis' or 'mortality'
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of predictions, total count)
        """
        query = db.query(Prediction).filter(Prediction.patient_id == patient_id)

        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)

        # Get total count
        total = query.count()

        # Get records ordered by most recent first
        predictions = (
            query.order_by(desc(Prediction.predicted_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return predictions, total

    @staticmethod
    def list_all_predictions(
        db: Session,
        prediction_type: Optional[str] = None,
        risk_category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Prediction], int]:
        """
        List all predictions with optional filters

        Args:
            db: Database session
            prediction_type: Optional filter by 'sepsis' or 'mortality'
            risk_category: Optional filter by risk category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of predictions, total count)
        """
        query = db.query(Prediction)

        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)

        if risk_category:
            query = query.filter(Prediction.risk_category == risk_category)

        # Get total count
        total = query.count()

        # Get records ordered by most recent first
        predictions = (
            query.order_by(desc(Prediction.predicted_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return predictions, total

    @staticmethod
    def get_latest_prediction_for_patient(
        db: Session, patient_id: int, prediction_type: str
    ) -> Optional[Prediction]:
        """
        Get the most recent prediction for a patient

        Args:
            db: Database session
            patient_id: Patient ID
            prediction_type: 'sepsis' or 'mortality'

        Returns:
            Most recent Prediction object or None
        """
        return (
            db.query(Prediction)
            .filter(
                Prediction.patient_id == patient_id,
                Prediction.prediction_type == prediction_type,
            )
            .order_by(desc(Prediction.predicted_at))
            .first()
        )

    @staticmethod
    def update_outcome(
        db: Session,
        prediction_id: int,
        actual_outcome: bool,
        outcome_notes: Optional[str] = None,
    ) -> Optional[Prediction]:
        """
        Update the actual outcome for a prediction (for model evaluation)

        Args:
            db: Database session
            prediction_id: Prediction ID
            actual_outcome: True/False - did the event occur?
            outcome_notes: Optional notes about the outcome

        Returns:
            Updated Prediction object or None if not found
        """
        prediction = PredictionHistoryService.get_prediction(db, prediction_id)
        if not prediction:
            return None

        prediction.actual_outcome = actual_outcome
        prediction.outcome_recorded_at = datetime.utcnow()
        prediction.outcome_notes = outcome_notes

        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def get_prediction_statistics(
        db: Session, prediction_type: Optional[str] = None
    ) -> dict:
        """
        Get statistics about predictions

        Args:
            db: Database session
            prediction_type: Optional filter by type

        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func

        query = db.query(Prediction)
        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)

        total_predictions = query.count()

        if total_predictions == 0:
            return {
                "total_predictions": 0,
                "by_risk_category": {},
                "by_type": {},
                "avg_risk_percentage": 0,
            }

        # Group by risk category
        risk_stats = db.query(
            Prediction.risk_category, func.count(Prediction.id)
        ).group_by(Prediction.risk_category)

        if prediction_type:
            risk_stats = risk_stats.filter(
                Prediction.prediction_type == prediction_type
            )

        by_risk = {category: count for category, count in risk_stats.all()}

        # Group by prediction type
        type_stats = (
            db.query(Prediction.prediction_type, func.count(Prediction.id))
            .group_by(Prediction.prediction_type)
            .all()
        )

        by_type = {ptype: count for ptype, count in type_stats}

        # Average risk percentage
        avg_risk = query.with_entities(func.avg(Prediction.risk_percentage)).scalar()

        return {
            "total_predictions": total_predictions,
            "by_risk_category": by_risk,
            "by_type": by_type,
            "avg_risk_percentage": float(avg_risk) if avg_risk else 0,
        }
