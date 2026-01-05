#!/usr/bin/env python3
"""
End-to-End API Test Script for MediAI
Tests all Phase 3-4 endpoints in sequence

Usage:
    python scripts/test_e2e.py

Requirements:
    - API server running at http://localhost:8000
    - Test user credentials: demo/demo123
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime
import sys

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_USER = "demo"
TEST_PASSWORD = "demo123"

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class E2ETestRunner:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.session_id = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Log with colors"""
        color = {
            "INFO": BLUE,
            "SUCCESS": GREEN,
            "ERROR": RED,
            "WARNING": YELLOW,
        }.get(level, RESET)
        print(f"{color}[{level}]{RESET} {message}")

    def test(self, name: str, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute a single test"""
        url = f"{API_BASE}{endpoint}"
        headers = kwargs.pop("headers", {})

        if self.access_token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {self.access_token}"

        self.log(f"\nTest: {name}", "INFO")
        self.log(f"  {method.upper()} {endpoint}", "INFO")

        try:
            response = requests.request(method, url, headers=headers, **kwargs)

            if 200 <= response.status_code < 300:
                self.tests_passed += 1
                self.log(f"  ✓ {response.status_code} - PASSED", "SUCCESS")
                return response.json() if response.content else {}
            else:
                self.tests_failed += 1
                self.log(f"  ✗ {response.status_code} - FAILED", "ERROR")
                if response.content:
                    self.log(f"  Response: {response.text[:200]}", "ERROR")
                return None

        except Exception as e:
            self.tests_failed += 1
            self.log(f"  ✗ Exception: {str(e)}", "ERROR")
            return None

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("=" * 60, "INFO")
        self.log("MediAI End-to-End API Tests", "INFO")
        self.log("=" * 60, "INFO")

        # ==================== PHASE 1: AUTHENTICATION ====================
        self.log("\n📋 PHASE 1: Authentication Tests", "WARNING")

        # Test 1: Login
        login_data = {
            "username": TEST_USER,
            "password": TEST_PASSWORD,
        }
        result = self.test(
            "User Login",
            "POST",
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if result:
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")
            self.log(f"  Token received: {self.access_token[:20]}...", "SUCCESS")
        else:
            self.log("  ⚠️  Login failed - subsequent tests will fail", "ERROR")
            return

        # Test 2: Get Current User
        user = self.test("Get Current User", "GET", "/auth/me")
        if user:
            self.log(f"  User: {user.get('username')} ({user.get('email')})", "SUCCESS")

        # Test 3: Refresh Token
        refresh_result = self.test(
            "Refresh Access Token",
            "POST",
            "/auth/refresh",
            json={"token": self.refresh_token},
        )
        if refresh_result:
            self.access_token = refresh_result.get("access_token")

        # ==================== PHASE 2: PREDICTIONS ====================
        self.log("\n📋 PHASE 2: Prediction Tests", "WARNING")

        # Test 4: Predict Sepsis
        sepsis_data = {
            "patient_id": "TEST-001",
            "age": 65,
            "gender": "M",
            "heart_rate": 110,
            "temperature": 38.5,
            "respiratory_rate": 24,
            "systolic_bp": 90,
            "diastolic_bp": 60,
            "spo2": 92,
            "wbc": 15.2,
            "lactate": 2.8,
            "creatinine": 1.5,
        }
        sepsis_result = self.test(
            "Sepsis Risk Prediction",
            "POST",
            "/predict/sepsis",
            json=sepsis_data,
        )
        if sepsis_result and "prediction" in sepsis_result:
            pred = sepsis_result["prediction"]
            self.log(f"  Risk Score: {pred.get('risk_score'):.2%}", "SUCCESS")
            self.log(f"  Risk Level: {pred.get('risk_level')}", "SUCCESS")

        # Test 5: Predict Mortality
        mortality_data = {
            "patient_id": "TEST-001",
            "age": 72,
            "gender": "F",
            "admission_type": "EMERGENCY",
            "los_hours": 48,
            "sofa_score": 8,
            "charlson_index": 4,
            "mechanical_ventilation": True,
            "vasopressor_use": True,
        }
        mortality_result = self.test(
            "Mortality Risk Prediction",
            "POST",
            "/predict/mortality",
            json=mortality_data,
        )
        if mortality_result and "prediction" in mortality_result:
            pred = mortality_result["prediction"]
            self.log(f"  Risk Score: {pred.get('risk_score'):.2%}", "SUCCESS")
            self.log(f"  Risk Level: {pred.get('risk_level')}", "SUCCESS")

        # ==================== PHASE 3: DOCTORS ====================
        self.log("\n📋 PHASE 3: Doctor Management Tests", "WARNING")

        # Test 6: List Doctors
        doctors = self.test(
            "List All Doctors",
            "GET",
            "/doctors?page=1&page_size=5",
        )
        if doctors and "doctors" in doctors:
            self.log(f"  Found {doctors.get('total')} doctors", "SUCCESS")
            if doctors["doctors"]:
                doc = doctors["doctors"][0]
                self.log(f"  First: {doc.get('name')} - {doc.get('specialty')}", "SUCCESS")

        # Test 7: Get Doctor by ID
        doctor = self.test("Get Doctor by ID", "GET", "/doctors/1")
        if doctor:
            self.log(f"  Doctor: {doctor.get('name')}", "SUCCESS")
            self.log(f"  Specialty: {doctor.get('specialty')}", "SUCCESS")

        # Test 8: Search Doctors
        search_result = self.test(
            "Search Doctors",
            "GET",
            "/doctors?search=Chen&available=true",
        )
        if search_result and "doctors" in search_result:
            self.log(f"  Found {len(search_result['doctors'])} matching doctors", "SUCCESS")

        # Test 9: Get Doctor Schedule
        schedule = self.test("Get Doctor Schedule", "GET", "/doctors/1/schedule")
        if schedule and "schedule" in schedule:
            self.log(f"  Schedule days: {len(schedule['schedule'])}", "SUCCESS")

        # ==================== PHASE 4: CHAT/RAG ====================
        self.log("\n📋 PHASE 4: Medical AI Chat Tests", "WARNING")

        # Test 10: Send Chat Message (Sepsis)
        chat_result = self.test(
            "Ask about Sepsis",
            "POST",
            "/chat",
            json={
                "message": "What are the early signs of sepsis?",
                "include_sources": True,
            },
        )
        if chat_result:
            self.session_id = chat_result.get("session_id")
            self.log(f"  Answer length: {len(chat_result.get('answer', ''))} chars", "SUCCESS")
            self.log(f"  Citations: {len(chat_result.get('citations', []))}", "SUCCESS")
            self.log(f"  Processing time: {chat_result.get('processing_time_ms')}ms", "SUCCESS")

        # Test 11: Send Follow-up Message
        if self.session_id:
            followup = self.test(
                "Ask Follow-up Question",
                "POST",
                "/chat",
                json={
                    "message": "How is it treated?",
                    "session_id": self.session_id,
                    "include_sources": True,
                },
            )
            if followup:
                self.log(f"  Answer length: {len(followup.get('answer', ''))} chars", "SUCCESS")

        # Test 12: Get Conversation History
        if self.session_id:
            history = self.test(
                "Get Conversation History",
                "GET",
                f"/chat/history/{self.session_id}",
            )
            if history and "messages" in history:
                self.log(f"  Messages in history: {len(history['messages'])}", "SUCCESS")

        # Test 13: List Chat Sessions
        sessions = self.test("List All Chat Sessions", "GET", "/chat/sessions")
        if sessions and "sessions" in sessions:
            self.log(f"  Active sessions: {sessions.get('total')}", "SUCCESS")

        # ==================== PHASE 5: HEALTH ====================
        self.log("\n📋 PHASE 5: Health Check", "WARNING")

        # Test 14: Health Check (no auth required)
        health = self.test(
            "API Health Check",
            "GET",
            "/health",
            headers={},  # No auth needed
        )
        if health:
            self.log(f"  Status: {health.get('status')}", "SUCCESS")
            if "components" in health:
                for comp, status in health["components"].items():
                    self.log(f"  {comp}: {status}", "SUCCESS")

        # ==================== SUMMARY ====================
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0

        self.log("\n" + "=" * 60, "INFO")
        self.log("Test Summary", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"Total Tests: {total}", "INFO")
        self.log(f"Passed: {self.tests_passed}", "SUCCESS")
        self.log(f"Failed: {self.tests_failed}", "ERROR" if self.tests_failed > 0 else "INFO")
        self.log(f"Pass Rate: {pass_rate:.1f}%", "SUCCESS" if pass_rate >= 90 else "WARNING")
        self.log(f"Duration: {duration:.2f}s", "INFO")
        self.log("=" * 60, "INFO")

        if self.tests_failed > 0:
            self.log("\n⚠️  Some tests failed. Check the logs above.", "ERROR")
            sys.exit(1)
        else:
            self.log("\n✅ All tests passed!", "SUCCESS")
            sys.exit(0)


if __name__ == "__main__":
    print(f"\n{BLUE}Starting MediAI E2E Tests...{RESET}\n")
    print(f"{YELLOW}Prerequisites:{RESET}")
    print(f"  • API server running at {API_BASE}")
    print(f"  • Test user: {TEST_USER}/{TEST_PASSWORD}")
    print(f"\n{YELLOW}Press Ctrl+C to cancel{RESET}\n")

    try:
        runner = E2ETestRunner()
        runner.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{RED}Tests cancelled by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
