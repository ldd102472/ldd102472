#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Feedback and Suggestions System
Tests all implemented endpoints with realistic data scenarios
"""

import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE}")

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.created_feedback_ids = []
        self.created_suggestion_ids = []

    def log_result(self, test_name, success, message=""):
        if success:
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")

    def test_health_check(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                self.log_result("Health Check", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_create_feedback(self):
        """Test POST /api/feedback endpoint"""
        test_cases = [
            {
                "name": "User Interface Feedback",
                "data": {
                    "title": "Navigation Menu Improvement",
                    "description": "The main navigation menu could be more intuitive. Consider adding breadcrumbs and better visual hierarchy.",
                    "category": "user_interface",
                    "type": "feedback",
                    "rating": 4,
                    "is_anonymous": False,
                    "user_email": "sarah.johnson@email.com",
                    "user_name": "Sarah Johnson"
                }
            },
            {
                "name": "Anonymous Bug Report",
                "data": {
                    "title": "Login Page Loading Issue",
                    "description": "The login page takes too long to load on mobile devices, especially on slower connections.",
                    "category": "performance",
                    "type": "bug_report",
                    "rating": 2,
                    "is_anonymous": True
                }
            },
            {
                "name": "Security Concern",
                "data": {
                    "title": "Password Reset Security",
                    "description": "The password reset process should include additional verification steps for better security.",
                    "category": "security",
                    "type": "feedback",
                    "rating": 3,
                    "is_anonymous": False,
                    "user_email": "mike.chen@email.com",
                    "user_name": "Mike Chen"
                }
            }
        ]

        for test_case in test_cases:
            try:
                response = self.session.post(f"{API_BASE}/feedback", json=test_case["data"])
                if response.status_code == 200:
                    feedback_data = response.json()
                    self.created_feedback_ids.append(feedback_data['id'])
                    self.log_result(f"Create Feedback - {test_case['name']}", True, 
                                  f"ID: {feedback_data['id']}")
                else:
                    self.log_result(f"Create Feedback - {test_case['name']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result(f"Create Feedback - {test_case['name']}", False, str(e))

    def test_get_feedback(self):
        """Test GET /api/feedback endpoint with various filters"""
        test_cases = [
            {"name": "Get All Feedback", "params": {}},
            {"name": "Filter by Category", "params": {"category": "user_interface"}},
            {"name": "Filter by Status", "params": {"status": "pending"}},
            {"name": "Filter by Type", "params": {"feedback_type": "feedback"}},
            {"name": "Multiple Filters", "params": {"category": "performance", "status": "pending"}},
            {"name": "Pagination", "params": {"limit": 2, "skip": 0}}
        ]

        for test_case in test_cases:
            try:
                response = self.session.get(f"{API_BASE}/feedback", params=test_case["params"])
                if response.status_code == 200:
                    feedback_list = response.json()
                    self.log_result(f"Get Feedback - {test_case['name']}", True, 
                                  f"Count: {len(feedback_list)}")
                else:
                    self.log_result(f"Get Feedback - {test_case['name']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Get Feedback - {test_case['name']}", False, str(e))

    def test_get_feedback_by_id(self):
        """Test GET /api/feedback/{id} endpoint"""
        if not self.created_feedback_ids:
            self.log_result("Get Feedback by ID", False, "No feedback IDs available for testing")
            return

        feedback_id = self.created_feedback_ids[0]
        try:
            response = self.session.get(f"{API_BASE}/feedback/{feedback_id}")
            if response.status_code == 200:
                feedback_data = response.json()
                self.log_result("Get Feedback by ID", True, f"Retrieved feedback: {feedback_data['title']}")
            else:
                self.log_result("Get Feedback by ID", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Get Feedback by ID", False, str(e))

        # Test with invalid ID
        try:
            response = self.session.get(f"{API_BASE}/feedback/invalid-id")
            if response.status_code == 404:
                self.log_result("Get Feedback by Invalid ID", True, "Correctly returned 404")
            else:
                self.log_result("Get Feedback by Invalid ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Get Feedback by Invalid ID", False, str(e))

    def test_update_feedback(self):
        """Test PATCH /api/feedback/{id} endpoint"""
        if not self.created_feedback_ids:
            self.log_result("Update Feedback", False, "No feedback IDs available for testing")
            return

        feedback_id = self.created_feedback_ids[0]
        update_data = {
            "status": "reviewed",
            "priority": "high",
            "admin_notes": "This feedback has been reviewed and prioritized for the next sprint.",
            "admin_response": "Thank you for your valuable feedback. We will address this in our upcoming UI improvements."
        }

        try:
            response = self.session.patch(f"{API_BASE}/feedback/{feedback_id}", json=update_data)
            if response.status_code == 200:
                updated_feedback = response.json()
                self.log_result("Update Feedback", True, f"Status: {updated_feedback['status']}, Priority: {updated_feedback['priority']}")
            else:
                self.log_result("Update Feedback", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Update Feedback", False, str(e))

    def test_create_suggestions(self):
        """Test POST /api/suggestions endpoint"""
        test_cases = [
            {
                "name": "Community Feature Suggestion",
                "data": {
                    "title": "Community Events Calendar",
                    "description": "Add a shared calendar where residents can post and view community events, meetings, and activities.",
                    "category": "social_features",
                    "rating": 5,
                    "is_anonymous": False,
                    "user_email": "emma.davis@email.com",
                    "user_name": "Emma Davis",
                    "expected_benefit": "Better community engagement and participation in local events"
                }
            },
            {
                "name": "Mobile App Suggestion",
                "data": {
                    "title": "Mobile App Development",
                    "description": "Develop a dedicated mobile app for easier access to community features on smartphones.",
                    "category": "functionality",
                    "rating": 4,
                    "is_anonymous": False,
                    "user_email": "alex.rodriguez@email.com",
                    "user_name": "Alex Rodriguez",
                    "expected_benefit": "Increased accessibility and user engagement"
                }
            },
            {
                "name": "Anonymous Content Suggestion",
                "data": {
                    "title": "Local Business Directory",
                    "description": "Create a directory of local businesses with reviews and recommendations from community members.",
                    "category": "content",
                    "rating": 4,
                    "is_anonymous": True,
                    "expected_benefit": "Support local economy and provide valuable resource for residents"
                }
            }
        ]

        for test_case in test_cases:
            try:
                response = self.session.post(f"{API_BASE}/suggestions", json=test_case["data"])
                if response.status_code == 200:
                    suggestion_data = response.json()
                    self.created_suggestion_ids.append(suggestion_data['id'])
                    self.log_result(f"Create Suggestion - {test_case['name']}", True, 
                                  f"ID: {suggestion_data['id']}")
                else:
                    self.log_result(f"Create Suggestion - {test_case['name']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result(f"Create Suggestion - {test_case['name']}", False, str(e))

    def test_get_suggestions(self):
        """Test GET /api/suggestions endpoint"""
        test_cases = [
            {"name": "Get All Suggestions", "params": {}},
            {"name": "Filter by Category", "params": {"category": "social_features"}},
            {"name": "Filter by Status", "params": {"status": "pending"}},
            {"name": "Pagination", "params": {"limit": 2, "skip": 0}}
        ]

        for test_case in test_cases:
            try:
                response = self.session.get(f"{API_BASE}/suggestions", params=test_case["params"])
                if response.status_code == 200:
                    suggestions_list = response.json()
                    self.log_result(f"Get Suggestions - {test_case['name']}", True, 
                                  f"Count: {len(suggestions_list)}")
                else:
                    self.log_result(f"Get Suggestions - {test_case['name']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Get Suggestions - {test_case['name']}", False, str(e))

    def test_update_suggestion(self):
        """Test PATCH /api/suggestions/{id} endpoint"""
        if not self.created_suggestion_ids:
            self.log_result("Update Suggestion", False, "No suggestion IDs available for testing")
            return

        suggestion_id = self.created_suggestion_ids[0]
        update_data = {
            "status": "in_progress",
            "priority": "high",
            "admin_notes": "This suggestion has been approved and is being developed.",
            "admin_response": "Great suggestion! We're excited to implement this feature."
        }

        try:
            response = self.session.patch(f"{API_BASE}/suggestions/{suggestion_id}", json=update_data)
            if response.status_code == 200:
                updated_suggestion = response.json()
                self.log_result("Update Suggestion", True, f"Status: {updated_suggestion['status']}")
            else:
                self.log_result("Update Suggestion", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Update Suggestion", False, str(e))

    def test_vote_suggestion(self):
        """Test POST /api/suggestions/{id}/vote endpoint"""
        if not self.created_suggestion_ids:
            self.log_result("Vote for Suggestion", False, "No suggestion IDs available for testing")
            return

        suggestion_id = self.created_suggestion_ids[0]
        
        # Vote multiple times to test vote counting
        for i in range(3):
            try:
                response = self.session.post(f"{API_BASE}/suggestions/{suggestion_id}/vote")
                if response.status_code == 200:
                    self.log_result(f"Vote for Suggestion #{i+1}", True, "Vote recorded")
                else:
                    self.log_result(f"Vote for Suggestion #{i+1}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Vote for Suggestion #{i+1}", False, str(e))

    def test_analytics(self):
        """Test POST /api/analytics endpoint"""
        analytics_data = {
            "user_id": "user_123",
            "page_path": "/feedback",
            "action": "submit_feedback",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "session_id": "session_456"
        }

        try:
            response = self.session.post(f"{API_BASE}/analytics", json=analytics_data)
            if response.status_code == 200:
                self.log_result("Track Analytics", True, "Analytics data recorded")
            else:
                self.log_result("Track Analytics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Track Analytics", False, str(e))

    def test_category_stats(self):
        """Test GET /api/categories/stats endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/categories/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_result("Get Category Stats", True, f"Retrieved stats for {len(stats)} categories")
                
                # Verify stats structure
                if stats and isinstance(stats, list):
                    first_stat = stats[0]
                    required_fields = ['category', 'feedback_count', 'suggestion_count']
                    if all(field in first_stat for field in required_fields):
                        self.log_result("Category Stats Structure", True, "All required fields present")
                    else:
                        self.log_result("Category Stats Structure", False, "Missing required fields")
            else:
                self.log_result("Get Category Stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Get Category Stats", False, str(e))

    def test_admin_dashboard(self):
        """Test GET /api/admin/dashboard endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/admin/dashboard")
            if response.status_code == 200:
                dashboard_data = response.json()
                self.log_result("Get Admin Dashboard", True, "Dashboard data retrieved")
                
                # Verify dashboard structure
                required_sections = ['overview', 'recent_feedback', 'recent_suggestions']
                if all(section in dashboard_data for section in required_sections):
                    self.log_result("Dashboard Structure", True, "All required sections present")
                    
                    # Check overview data
                    overview = dashboard_data['overview']
                    overview_fields = ['total_feedback', 'total_suggestions', 'pending_feedback', 
                                     'pending_suggestions', 'high_priority_items']
                    if all(field in overview for field in overview_fields):
                        self.log_result("Dashboard Overview", True, f"Total feedback: {overview['total_feedback']}, Total suggestions: {overview['total_suggestions']}")
                    else:
                        self.log_result("Dashboard Overview", False, "Missing overview fields")
                else:
                    self.log_result("Dashboard Structure", False, "Missing required sections")
            else:
                self.log_result("Get Admin Dashboard", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Get Admin Dashboard", False, str(e))

    def test_data_validation(self):
        """Test data validation for various endpoints"""
        
        # Test invalid rating (should be 1-5)
        invalid_feedback = {
            "title": "Test Feedback",
            "description": "Test description",
            "category": "user_interface",
            "type": "feedback",
            "rating": 6,  # Invalid rating
            "is_anonymous": False
        }
        
        try:
            response = self.session.post(f"{API_BASE}/feedback", json=invalid_feedback)
            if response.status_code == 422:  # Validation error
                self.log_result("Rating Validation", True, "Correctly rejected invalid rating")
            else:
                self.log_result("Rating Validation", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Rating Validation", False, str(e))

        # Test missing required fields
        incomplete_feedback = {
            "title": "Test Feedback"
            # Missing required fields
        }
        
        try:
            response = self.session.post(f"{API_BASE}/feedback", json=incomplete_feedback)
            if response.status_code == 422:  # Validation error
                self.log_result("Required Fields Validation", True, "Correctly rejected incomplete data")
            else:
                self.log_result("Required Fields Validation", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Required Fields Validation", False, str(e))

        # Test invalid enum values
        invalid_category_feedback = {
            "title": "Test Feedback",
            "description": "Test description",
            "category": "invalid_category",  # Invalid category
            "type": "feedback",
            "rating": 3,
            "is_anonymous": False
        }
        
        try:
            response = self.session.post(f"{API_BASE}/feedback", json=invalid_category_feedback)
            if response.status_code == 422:  # Validation error
                self.log_result("Enum Validation", True, "Correctly rejected invalid category")
            else:
                self.log_result("Enum Validation", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Enum Validation", False, str(e))

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Backend API Testing...")
        print("=" * 60)
        
        # Basic connectivity test
        if not self.test_health_check():
            print("❌ Backend is not accessible. Stopping tests.")
            return
        
        print("\n📝 Testing Feedback API Endpoints...")
        self.test_create_feedback()
        time.sleep(1)  # Brief pause between test suites
        self.test_get_feedback()
        self.test_get_feedback_by_id()
        self.test_update_feedback()
        
        print("\n💡 Testing Suggestions API Endpoints...")
        self.test_create_suggestions()
        time.sleep(1)
        self.test_get_suggestions()
        self.test_update_suggestion()
        self.test_vote_suggestion()
        
        print("\n📊 Testing Analytics and Admin Endpoints...")
        self.test_analytics()
        self.test_category_stats()
        self.test_admin_dashboard()
        
        print("\n🔍 Testing Data Validation...")
        self.test_data_validation()
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print(f"\n🆔 Created Test Data:")
        print(f"   • Feedback IDs: {len(self.created_feedback_ids)}")
        print(f"   • Suggestion IDs: {len(self.created_suggestion_ids)}")
        
        return self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()