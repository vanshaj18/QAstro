import unittest
import sys
from pathlib import Path
import urllib.parse
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.viser import (
    viser_api,
    get_wavelength_catalogs,
    build_vizier_object_query,
    build_vizier_cone_query
)
class TestViserApi(unittest.TestCase):
    """Test suite for VizieR API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_object_name = "M31"
        self.test_ra = 10.684
        self.test_dec = 41.269
        self.test_radius = 5.0
        self.valid_wavelengths = ["Radio", "IR", "Optical", "UV", "EUV", "X-Ray", "Gamma"]
    
    def test_viser_api_object_name_search(self):
        """Test URL construction for object name search."""
        url = viser_api(object_name=self.test_object_name)
        
        # Parse the URL to check components
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check base URL
        self.assertEqual(parsed_url.scheme, "http")
        self.assertEqual(parsed_url.netloc, "tapvizier.u-strasbg.fr")
        self.assertEqual(parsed_url.path, "/TAPVizieR/tap/sync")
        
        # Check required parameters
        self.assertIn('REQUEST', query_params)
        self.assertEqual(query_params['REQUEST'][0], 'doQuery')
        
        self.assertIn('LANG', query_params)
        self.assertEqual(query_params['LANG'][0], 'ADQL')
        
        self.assertIn('FORMAT', query_params)
        self.assertEqual(query_params['FORMAT'][0], 'json')
        
        self.assertIn('QUERY', query_params)
        # Query should contain the object name
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        self.assertIn(self.test_object_name, decoded_query)
    
    def test_viser_api_coordinate_search(self):
        """Test URL construction for coordinate search."""
        url = viser_api(ra=self.test_ra, dec=self.test_dec, radius_arcmin=self.test_radius)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check that query contains coordinates
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        self.assertIn(str(self.test_ra), decoded_query)
        self.assertIn(str(self.test_dec), decoded_query)
    
    def test_viser_api_wavelength_filtering(self):
        """Test URL construction with wavelength filtering."""
        for wavelength in self.valid_wavelengths:
            url = viser_api(object_name=self.test_object_name, wavelength=wavelength)
            
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Query should contain wavelength-specific filtering
            decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
            self.assertIn("AND", decoded_query)  # Should have catalog filtering
    
    def test_viser_api_custom_output_format(self):
        """Test URL construction with custom output format."""
        formats = ['votable', 'csv', 'tsv']
        
        for fmt in formats:
            url = viser_api(object_name=self.test_object_name, output_format=fmt)
            
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            self.assertEqual(query_params['FORMAT'][0], fmt)
    
    def test_viser_api_no_parameters_error(self):
        """Test that ValueError is raised when no search parameters are provided."""
        with self.assertRaises(ValueError) as context:
            viser_api()
        
        self.assertIn("Either object_name or both ra and dec coordinates must be provided", 
                     str(context.exception))
    
    def test_viser_api_incomplete_coordinates_error(self):
        """Test that ValueError is raised when only one coordinate is provided."""
        with self.assertRaises(ValueError) as context:
            viser_api(ra=self.test_ra)
        
        self.assertIn("Both ra and dec must be provided for coordinate search", 
                     str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            viser_api(dec=self.test_dec)
        
        self.assertIn("Both ra and dec must be provided for coordinate search", 
                     str(context.exception))
    
    def test_viser_api_invalid_coordinates_error(self):
        """Test that ValueError is raised for non-numeric coordinates."""
        with self.assertRaises(ValueError) as context:
            viser_api(ra="invalid", dec=self.test_dec)
        
        self.assertIn("RA and DEC must be numeric values", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            viser_api(ra=self.test_ra, dec="invalid")
        
        self.assertIn("RA and DEC must be numeric values", str(context.exception))
    
    def test_viser_api_coordinate_conversion(self):
        """Test that string coordinates are properly converted to float."""
        url = viser_api(ra="10.684", dec="41.269")
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        self.assertIn("10.684", decoded_query)
        self.assertIn("41.269", decoded_query)
    
    def test_viser_api_radius_parameter(self):
        """Test that custom radius parameter is properly handled."""
        custom_radius = 10.0
        url = viser_api(ra=self.test_ra, dec=self.test_dec, radius_arcmin=custom_radius)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        # Radius should be converted to degrees (10.0 arcmin = 0.1667 degrees)
        expected_radius_deg = custom_radius / 60.0
        self.assertIn(str(expected_radius_deg), decoded_query)
class TestWavelengthCatalogs(unittest.TestCase):
    """Test suite for wavelength catalog filtering."""
    
    def test_get_wavelength_catalogs_radio(self):
        """Test Radio wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("Radio")
        self.assertIn("radio", filter_clause.lower())
        self.assertIn("AND", filter_clause)
    
    def test_get_wavelength_catalogs_ir(self):
        """Test IR wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("IR")
        self.assertIn("ir", filter_clause.lower())
        self.assertIn("2mass", filter_clause.lower())
        self.assertIn("wise", filter_clause.lower())
    
    def test_get_wavelength_catalogs_optical(self):
        """Test Optical wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("Optical")
        self.assertIn("optical", filter_clause.lower())
        self.assertIn("gsc", filter_clause.lower())
        self.assertIn("usno", filter_clause.lower())
    
    def test_get_wavelength_catalogs_uv(self):
        """Test UV wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("UV")
        self.assertIn("uv", filter_clause.lower())
        self.assertIn("galex", filter_clause.lower())
    
    def test_get_wavelength_catalogs_euv(self):
        """Test EUV wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("EUV")
        self.assertIn("euv", filter_clause.lower())
    
    def test_get_wavelength_catalogs_xray(self):
        """Test X-Ray wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("X-Ray")
        self.assertIn("xray", filter_clause.lower())
        self.assertIn("rosat", filter_clause.lower())
        self.assertIn("chandra", filter_clause.lower())
    
    def test_get_wavelength_catalogs_gamma(self):
        """Test Gamma wavelength catalog filtering."""
        filter_clause = get_wavelength_catalogs("Gamma")
        self.assertIn("gamma", filter_clause.lower())
        self.assertIn("fermi", filter_clause.lower())
    
    def test_get_wavelength_catalogs_invalid(self):
        """Test invalid wavelength returns empty string."""
        filter_clause = get_wavelength_catalogs("Invalid")
        self.assertEqual(filter_clause, "")
    
    def test_get_wavelength_catalogs_none(self):
        """Test None wavelength returns empty string."""
        filter_clause = get_wavelength_catalogs(None)
        self.assertEqual(filter_clause, "")

class TestVizierQueryBuilding(unittest.TestCase):
    """Test suite for VizieR ADQL query construction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_object_name = "M31"
        self.test_ra = 10.684
        self.test_dec = 41.269
        self.test_radius = 5.0
        self.test_catalog_filter = "AND (cat_name LIKE '%optical%')"
    
    def test_build_vizier_object_query_basic(self):
        """Test basic object query construction."""
        query = build_vizier_object_query(self.test_object_name)
        
        # Check query structure
        self.assertIn("SELECT", query.upper())
        self.assertIn("FROM", query.upper())
        self.assertIn("WHERE", query.upper())
        self.assertIn(self.test_object_name, query)
        self.assertIn("CONTAINS", query.upper())
        self.assertIn("CIRCLE", query.upper())
    
    def test_build_vizier_object_query_with_filter(self):
        """Test object query construction with catalog filter."""
        query = build_vizier_object_query(self.test_object_name, self.test_catalog_filter)
        
        self.assertIn(self.test_object_name, query)
        self.assertIn(self.test_catalog_filter, query)
    
    def test_build_vizier_cone_query_basic(self):
        """Test basic cone search query construction."""
        query = build_vizier_cone_query(self.test_ra, self.test_dec, self.test_radius)
        
        # Check query structure
        self.assertIn("SELECT", query.upper())
        self.assertIn("FROM", query.upper())
        self.assertIn("WHERE", query.upper())
        self.assertIn(str(self.test_ra), query)
        self.assertIn(str(self.test_dec), query)
        self.assertIn("CONTAINS", query.upper())
        self.assertIn("CIRCLE", query.upper())
        self.assertIn("ORDER BY", query.upper())
    
    def test_build_vizier_cone_query_with_filter(self):
        """Test cone search query construction with catalog filter."""
        query = build_vizier_cone_query(
            self.test_ra, self.test_dec, self.test_radius, self.test_catalog_filter
        )
        
        self.assertIn(str(self.test_ra), query)
        self.assertIn(str(self.test_dec), query)
        self.assertIn(self.test_catalog_filter, query)
    
    def test_build_vizier_cone_query_radius_conversion(self):
        """Test that radius is properly converted from arcminutes to degrees."""
        radius_arcmin = 6.0
        query = build_vizier_cone_query(self.test_ra, self.test_dec, radius_arcmin)
        
        # 6 arcminutes = 0.1 degrees
        expected_radius_deg = radius_arcmin / 60.0
        self.assertIn(str(expected_radius_deg), query)
    
    def test_build_vizier_queries_return_strings(self):
        """Test that query building functions return strings."""
        object_query = build_vizier_object_query(self.test_object_name)
        cone_query = build_vizier_cone_query(self.test_ra, self.test_dec)
        
        self.assertIsInstance(object_query, str)
        self.assertIsInstance(cone_query, str)
        self.assertTrue(len(object_query) > 0)
        self.assertTrue(len(cone_query) > 0)
    
    def test_build_vizier_queries_proper_formatting(self):
        """Test that queries are properly formatted (no leading/trailing whitespace)."""
        object_query = build_vizier_object_query(self.test_object_name)
        cone_query = build_vizier_cone_query(self.test_ra, self.test_dec)
        
        self.assertEqual(object_query, object_query.strip())
        self.assertEqual(cone_query, cone_query.strip())

class TestViserApiEdgeCases(unittest.TestCase):
    """Test suite for VizieR API edge cases and special scenarios."""
    
    def test_viser_api_wavelength_none_handling(self):
        """Test that 'NONE' and 'Select Wavelength' are handled properly."""
        url_none = viser_api(object_name="M31", wavelength="NONE")
        url_select = viser_api(object_name="M31", wavelength="Select Wavelength")
        url_no_wavelength = viser_api(object_name="M31")
        
        # All should produce similar queries without wavelength filtering
        parsed_none = urllib.parse.urlparse(url_none)
        parsed_select = urllib.parse.urlparse(url_select)
        parsed_no = urllib.parse.urlparse(url_no_wavelength)
        
        query_none = urllib.parse.unquote(urllib.parse.parse_qs(parsed_none.query)['QUERY'][0])
        query_select = urllib.parse.unquote(urllib.parse.parse_qs(parsed_select.query)['QUERY'][0])
        query_no = urllib.parse.unquote(urllib.parse.parse_qs(parsed_no.query)['QUERY'][0])
        
        # None of these should contain wavelength-specific filtering
        self.assertNotIn("cat_name LIKE", query_none)
        self.assertNotIn("cat_name LIKE", query_select)
        self.assertNotIn("cat_name LIKE", query_no)
    
    def test_viser_api_zero_coordinates(self):
        """Test that zero coordinates are handled properly."""
        url = viser_api(ra=0.0, dec=0.0)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        self.assertIn("0.0", decoded_query)
    
    def test_viser_api_negative_coordinates(self):
        """Test that negative coordinates are handled properly."""
        url = viser_api(ra=-10.5, dec=-30.25)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        self.assertIn("-10.5", decoded_query)
        self.assertIn("-30.25", decoded_query)
    
    def test_viser_api_large_radius(self):
        """Test that large radius values are handled properly."""
        large_radius = 60.0  # 1 degree
        url = viser_api(ra=10.0, dec=20.0, radius_arcmin=large_radius)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        expected_radius_deg = large_radius / 60.0
        self.assertIn(str(expected_radius_deg), decoded_query)
    
    def test_viser_api_small_radius(self):
        """Test that small radius values are handled properly."""
        small_radius = 0.1  # 6 arcseconds
        url = viser_api(ra=10.0, dec=20.0, radius_arcmin=small_radius)
        
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        decoded_query = urllib.parse.unquote(query_params['QUERY'][0])
        expected_radius_deg = small_radius / 60.0
        self.assertIn(str(expected_radius_deg), decoded_query)


if __name__ == '__main__':
    # Create a test suite and run it
    suite = unittest.TestLoader().loadTestsFromTestCase(TestViserApi)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWavelengthCatalogs))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVizierQueryBuilding))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestViserApiEdgeCases))

    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    # Calculate summary metrics
    total_tests = result.testsRun
    failed = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failed - errors

    # Print dynamic test summary
    print("\n" + "="*60)
    print("📊 VIZIER API TEST SUMMARY")
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
        for test_case in [TestViserApi, TestWavelengthCatalogs, TestVizierQueryBuilding, TestViserApiEdgeCases]:
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