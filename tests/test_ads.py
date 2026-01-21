import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.parse
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ads import ads_api, get_ads_api_key, get_ads_headers, validate_ads_parameters


class DynamicTestResult(unittest.TestResult):
    """Custom test result class that tracks and displays test results dynamically."""

    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = defaultdict(list)
        self.current_test_class = None

    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)
        # Extract test class name
        test_class_name = test.__class__.__name__
        if test_class_name != self.current_test_class:
            self.current_test_class = test_class_name
            if self.stream:
                self.stream.write(f"\n🧪 Running tests for {test_class_name}:\n")
                self.stream.write("-" * 50 + "\n")

    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        test_name = test._testMethodName
        self.test_results['passed'].append(f"{self.current_test_class}.{test_name}")
        if self.stream:
            self.stream.write(f"✅ PASS: {test_name}\n")

    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        test_name = test._testMethodName
        self.test_results['failed'].append(f"{self.current_test_class}.{test_name}")
        if self.stream:
            self.stream.write(f"❌ FAIL: {test_name}\n")

    def addError(self, test, err):
        """Called when a test errors."""
        super().addError(test, err)
        test_name = test._testMethodName
        self.test_results['errors'].append(f"{self.current_test_class}.{test_name}")
        if self.stream:
            self.stream.write(f"💥 ERROR: {test_name}\n")

    def printSummary(self):
        """Print a comprehensive test summary."""
        if not self.stream:
            return

        total_tests = len(self.test_results['passed']) + len(self.test_results['failed']) + len(self.test_results.get('errors', []))
        passed_count = len(self.test_results['passed'])
        failed_count = len(self.test_results['failed'])
        error_count = len(self.test_results.get('errors', []))

        self.stream.write("\n" + "=" * 60 + "\n")
        self.stream.write("📊 TEST SUMMARY\n")
        self.stream.write("=" * 60 + "\n")

        self.stream.write(f"Total Tests: {total_tests}\n")
        self.stream.write(f"✅ Passed: {passed_count}\n")
        self.stream.write(f"❌ Failed: {failed_count}\n")
        if error_count > 0:
            self.stream.write(f"💥 Errors: {error_count}\n")

        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        self.stream.write(f"📈 Success Rate: {success_rate:.1f}%\n")

        if self.test_results['failed']:
            self.stream.write(f"\n❌ FAILED TESTS:\n")
            for failed_test in self.test_results['failed']:
                self.stream.write(f"  • {failed_test}\n")

        if self.test_results.get('errors'):
            self.stream.write(f"\n💥 ERROR TESTS:\n")
            for error_test in self.test_results['errors']:
                self.stream.write(f"  • {error_test}\n")

        if passed_count == total_tests:
            self.stream.write(f"\n🎉 ALL TESTS PASSED!\n")
        elif failed_count > 0 or error_count > 0:
            self.stream.write(f"\n⚠️  SOME TESTS FAILED OR ERRORED!\n")

        self.stream.write("=" * 60 + "\n")


def run_tests_with_summary():
    """Run tests with dynamic summary reporting."""
    # Load all tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    # Create custom result object
    result = DynamicTestResult(verbosity=2)
    result.stream = sys.stdout

    # Run the tests
    print("🚀 Starting NASA ADS API Test Suite...")
    print("=" * 60)

    suite.run(result)

    # Print final summary
    result.printSummary()

    # Return success/failure for exit code
    return len(result.test_results['failed']) + len(result.test_results.get('errors', [])) == 0

class TestAdsApi(unittest.TestCase):
    """Test suite for NASA ADS API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_bibcode = "2006ApJ...636L..85S"
        self.invalid_bibcode_short = "2006ApJ"
        self.invalid_bibcode_long = "2006ApJ...636L..85S123"
        self.test_object_name = "M31"
        self.test_author = "Smith, J."
        self.test_year_range = "2020-2023"
        self.test_single_year = "2022"
    
    def test_ads_api_object_name_search(self):
        """Test URL construction for object name search."""
        url = ads_api(object_name=self.test_object_name)
        
        # Parse the URL to check components
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check base URL
        self.assertEqual(parsed_url.scheme, "https")
        self.assertEqual(parsed_url.netloc, "api.adsabs.harvard.edu")
        self.assertEqual(parsed_url.path, "/v1/search/query")
        
        # Check query parameter
        self.assertIn('q', query_params)
        self.assertEqual(query_params['q'][0], f'object:"{self.test_object_name}"')
        
        # Check fields parameter
        self.assertIn('fl', query_params)
        expected_fields = ['bibcode', 'title', 'author', 'year', 'abstract', 'doi', 'pub', 'citation_count', 'read_count', 'keyword']
        actual_fields = query_params['fl'][0].split(',')
        self.assertEqual(set(actual_fields), set(expected_fields))
        
        # Check default parameters
        self.assertEqual(query_params['rows'][0], '50')
        self.assertEqual(query_params['sort'][0], 'citation_count desc')
    
    def test_ads_api_bibcode_search(self):
        """Test URL construction for bibcode search."""
        url = ads_api(bibcode=self.valid_bibcode)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.assertEqual(query_params['q'][0], f'bibcode:{self.valid_bibcode}')
    
    def test_ads_api_author_search(self):
        """Test URL construction for author search."""
        url = ads_api(author=self.test_author)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.assertEqual(query_params['q'][0], f'author:"{self.test_author}"')
    
    def test_ads_api_year_range_search(self):
        """Test URL construction for year range search."""
        url = ads_api(year_range=self.test_year_range)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.assertEqual(query_params['q'][0], 'year:2020-2023')
    
    def test_ads_api_single_year_search(self):
        """Test URL construction for single year search."""
        url = ads_api(year_range=self.test_single_year)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.assertEqual(query_params['q'][0], 'year:2022')
    
    def test_ads_api_combined_search(self):
        """Test URL construction for combined search parameters."""
        url = ads_api(
            object_name=self.test_object_name,
            author=self.test_author,
            year_range=self.test_year_range
        )
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        expected_query = f'object:"{self.test_object_name}" AND author:"{self.test_author}" AND year:2020-2023'
        self.assertEqual(query_params['q'][0], expected_query)
    
    def test_ads_api_custom_max_records(self):
        """Test URL construction with custom max_records parameter."""
        custom_max = 100
        url = ads_api(object_name=self.test_object_name, max_records=custom_max)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.assertEqual(query_params['rows'][0], str(custom_max))
    
    def test_ads_api_no_parameters_error(self):
        """Test that ValueError is raised when no search parameters are provided."""
        with self.assertRaises(ValueError) as context:
            ads_api()
        
        self.assertIn("At least one search parameter is required", str(context.exception))
    
    def test_ads_api_invalid_bibcode_short(self):
        """Test that ValueError is raised for short bibcode."""
        with self.assertRaises(ValueError) as context:
            ads_api(bibcode=self.invalid_bibcode_short)
        
        self.assertIn("Invalid bibcode format", str(context.exception))
    
    def test_ads_api_invalid_bibcode_long(self):
        """Test that ValueError is raised for long bibcode."""
        with self.assertRaises(ValueError) as context:
            ads_api(bibcode=self.invalid_bibcode_long)
        
        self.assertIn("Invalid bibcode format", str(context.exception))
    
    def test_ads_api_invalid_year_range_format(self):
        """Test that ValueError is raised for invalid year range format."""
        with self.assertRaises(ValueError) as context:
            ads_api(year_range="invalid-range")
        
        self.assertIn("Invalid year range format", str(context.exception))
    
    def test_ads_api_invalid_year_range_order(self):
        """Test that ValueError is raised when start year > end year."""
        with self.assertRaises(ValueError) as context:
            ads_api(year_range="2023-2020")
        
        self.assertIn("Start year cannot be greater than end year", str(context.exception))
    
    def test_ads_api_invalid_year_range_bounds(self):
        """Test that ValueError is raised for years outside valid range."""
        with self.assertRaises(ValueError) as context:
            ads_api(year_range="1700-1800")
        
        self.assertIn("Year range should be between 1800 and 2030", str(context.exception))
    
    def test_ads_api_invalid_single_year(self):
        """Test that ValueError is raised for invalid single year."""
        with self.assertRaises(ValueError) as context:
            ads_api(year_range="not_a_year")
        
        self.assertIn("Invalid year format", str(context.exception))
    
    def test_ads_api_invalid_max_records_low(self):
        """Test that ValueError is raised for max_records < 1."""
        with self.assertRaises(ValueError) as context:
            ads_api(object_name=self.test_object_name, max_records=0)
        
        self.assertIn("max_records must be between 1 and 2000", str(context.exception))
    
    def test_ads_api_invalid_max_records_high(self):
        """Test that ValueError is raised for max_records > 2000."""
        with self.assertRaises(ValueError) as context:
            ads_api(object_name=self.test_object_name, max_records=2001)
        
        self.assertIn("max_records must be between 1 and 2000", str(context.exception))
    
    def test_ads_api_whitespace_handling(self):
        """Test that whitespace in parameters is properly handled."""
        object_name_with_spaces = "  M 31  "
        url = ads_api(object_name=object_name_with_spaces)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Should strip whitespace
        self.assertEqual(query_params['q'][0], 'object:"M 31"')


class TestAdsApiKey(unittest.TestCase):
    """Test suite for NASA ADS API key handling."""
    
    @patch.dict(os.environ, {'ADS_API_KEY': 'test_api_key_123'})
    def test_get_ads_api_key_success(self):
        """Test successful API key retrieval from environment."""
        api_key = get_ads_api_key()
        self.assertEqual(api_key, 'test_api_key_123')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_ads_api_key_missing(self):
        """Test error when API key is missing from environment."""
        with self.assertRaises(ValueError) as context:
            get_ads_api_key()
        
        self.assertIn("NASA ADS API key not found", str(context.exception))
        self.assertIn("ADS_API_KEY", str(context.exception))
    
    @patch.dict(os.environ, {'ADS_API_KEY': 'test_api_key_456'})
    def test_get_ads_headers_success(self):
        """Test successful header construction."""
        headers = get_ads_headers()
        
        expected_headers = {
            'Authorization': 'Bearer test_api_key_456',
            'User-Agent': 'QAstro/1.0 (Astronomical Database Query Tool)'
        }
        
        self.assertEqual(headers, expected_headers)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_ads_headers_missing_key(self):
        """Test error when API key is missing during header construction."""
        with self.assertRaises(ValueError) as context:
            get_ads_headers()
        
        self.assertIn("NASA ADS API key not found", str(context.exception))


class TestAdsParameterValidation(unittest.TestCase):
    """Test suite for NASA ADS parameter validation."""
    
    def test_validate_ads_parameters_success(self):
        """Test successful parameter validation."""
        # Should not raise any exception
        self.assertTrue(validate_ads_parameters(object_name="M31"))
        self.assertTrue(validate_ads_parameters(bibcode="2006ApJ...636L..85S"))
        self.assertTrue(validate_ads_parameters(author="Smith"))
        self.assertTrue(validate_ads_parameters(year_range="2020-2023"))
    
    def test_validate_ads_parameters_no_params(self):
        """Test validation error when no parameters provided."""
        with self.assertRaises(ValueError) as context:
            validate_ads_parameters()
        
        self.assertIn("At least one search parameter must be provided", str(context.exception))
    
    def test_validate_ads_parameters_invalid_bibcode(self):
        """Test validation error for invalid bibcode."""
        with self.assertRaises(ValueError) as context:
            validate_ads_parameters(bibcode="invalid")
        
        self.assertIn("Invalid bibcode format", str(context.exception))
    
    def test_validate_ads_parameters_invalid_year_range(self):
        """Test validation error for invalid year range."""
        with self.assertRaises(ValueError) as context:
            validate_ads_parameters(year_range="2023-2020")
        
        self.assertIn("Start year cannot be greater than end year", str(context.exception))


if __name__ == '__main__':
    # Create a test suite and run it
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAdsApi)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAdsApiKey))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAdsParameterValidation))

    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    # Calculate summary metrics
    total_tests = result.testsRun
    failed = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failed - errors

    # Print dynamic test summary
    print("\n" + "="*60)
    print("📊 NASA ADS API TEST SUMMARY")
    print("="*60)
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"⚠️  ERRORS: {errors}")
    print(f"🔢 TOTAL:  {total_tests}")

    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
    print("="*60)

    # Show individual passed tests
    if passed > 0:
        print("\n✅ PASSED TESTS:")
        for test_case in [TestAdsApi, TestAdsApiKey, TestAdsParameterValidation]:
            test_names = [method for method in dir(test_case) if method.startswith('test_')]
            for test_name in test_names:
                full_test_name = f"{test_case.__name__}.{test_name}"
                # Check if this test is not in failures or errors
                if not any(full_test_name in failure[0] for failure in result.failures) and \
                   not any(full_test_name in error[0] for error in result.errors):
                    print(f"  • {full_test_name}")

    # Show individual failed tests with details
    if result.failures:
        print(f"\n❌ FAILED TESTS:")
        for test, traceback in result.failures:
            print(f"  • {test}")

    # Show individual error tests with details
    if result.errors:
        print(f"\n💥 ERROR TESTS:")
        for test, traceback in result.errors:
            print(f"  • {test}")

    print("="*60)

    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
    else:
        print("🚨 SOME TESTS FAILED OR ERRORED!")

    print("="*60 + "\n")

    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())