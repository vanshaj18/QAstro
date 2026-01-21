import pytest
import sys
from pathlib import Path
import urllib.parse
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.ned import ned_api, _ned_api_html

class TestNedApi:
    """Test suite for enhanced NED API functionality."""
    
    def test_ned_api_object_name_json(self):
        """Test NED API with object name in JSON format."""
        url = ned_api(object_name="M31", output_format='json')
        
        # Parse the URL to check parameters
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert parsed_url.netloc == "ned.ipac.caltech.edu"
        assert parsed_url.path == "/cgi-bin/nph-objsearch"
        assert params['objname'][0] == "M31"
        assert params['of'][0] == "pre_text"
        assert params['out_csys'][0] == "Equatorial"
        assert params['out_equinox'][0] == "J2000.0"
    
    def test_ned_api_coordinates_json(self):
        """Test NED API with RA/DEC coordinates in JSON format."""
        url = ned_api(ra=10.684, dec=41.269, radius_arcmin=5.0, output_format='json')
        
        # Parse the URL to check parameters
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert parsed_url.netloc == "ned.ipac.caltech.edu"
        assert params['lon'][0] == "10.684"
        assert params['lat'][0] == "41.269"
        assert params['radius'][0] == "5.0"
        assert params['in_csys'][0] == "Equatorial"
        assert params['in_equinox'][0] == "J2000.0"
        assert params['of'][0] == "pre_text"
    
    def test_ned_api_default_radius(self):
        """Test NED API uses default radius when not specified."""
        url = ned_api(ra=10.684, dec=41.269, output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert params['radius'][0] == "2.0"  # Default radius
    
    def test_ned_api_html_format(self):
        """Test NED API with HTML format (backward compatibility)."""
        url = ned_api(object_name="M31", output_format='html')
        
        # Should use legacy implementation
        expected_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?objname=M31"
        assert url == expected_url
    
    def test_ned_api_no_parameters_error(self):
        """Test NED API raises error when no search parameters provided."""
        with pytest.raises(ValueError, match="Either object_name or ra/dec coordinates must be provided"):
            ned_api(output_format='json')
    
    def test_ned_api_bibcode_error(self):
        """Test NED API raises error for bibcode search (not supported)."""
        with pytest.raises(ValueError, match="Bibcode search not supported"):
            ned_api(bibcode="2019ApJ...123..456A", output_format='json')
    
    def test_ned_api_missing_dec_error(self):
        """Test NED API raises error when RA provided without DEC."""
        with pytest.raises(ValueError, match="Either object_name or ra/dec coordinates must be provided"):
            ned_api(ra=10.684, output_format='json')
    
    def test_ned_api_missing_ra_error(self):
        """Test NED API raises error when DEC provided without RA."""
        with pytest.raises(ValueError, match="Either object_name or ra/dec coordinates must be provided"):
            ned_api(dec=41.269, output_format='json')
    
    def test_ned_api_parameter_encoding(self):
        """Test proper URL encoding of object names with special characters."""
        url = ned_api(object_name="NGC 1234", output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert params['objname'][0] == "NGC 1234"
    
    def test_ned_api_json_parameters_complete(self):
        """Test that all required JSON parameters are included."""
        url = ned_api(object_name="M31", output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check all required parameters are present
        required_params = [
            'extend', 'hconst', 'omegam', 'omegav', 'corr_z',
            'out_csys', 'out_equinox', 'obj_sort', 'of',
            'zv_breaker', 'list_limit', 'img_stamp', 'objname'
        ]
        
        for param in required_params:
            assert param in params, f"Required parameter '{param}' missing"
    
    def test_ned_api_coordinate_parameters_complete(self):
        """Test that all required coordinate search parameters are included."""
        url = ned_api(ra=10.684, dec=41.269, output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check coordinate-specific parameters
        coordinate_params = ['in_csys', 'in_equinox', 'lon', 'lat', 'radius']
        
        for param in coordinate_params:
            assert param in params, f"Required coordinate parameter '{param}' missing"


class TestNedApiHtml:
    """Test suite for legacy HTML NED API functionality."""
    
    def test_ned_api_html_object_name(self):
        """Test legacy HTML implementation with object name."""
        url = _ned_api_html(object_name="M31")
        
        expected_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?objname=M31"
        assert url == expected_url
    
    def test_ned_api_html_special_characters(self):
        """Test legacy HTML implementation with special characters in object name."""
        url = _ned_api_html(object_name="NGC 1234")
        
        expected_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?objname=NGC%201234"
        assert url == expected_url
    
    def test_ned_api_html_no_object_name_error(self):
        """Test legacy HTML implementation raises error without object name."""
        with pytest.raises(ValueError, match="Object name must be provided for HTML format"):
            _ned_api_html()
    
    def test_ned_api_html_ignores_other_parameters(self):
        """Test legacy HTML implementation ignores RA/DEC and bibcode parameters."""
        url = _ned_api_html(object_name="M31", ra=10.684, dec=41.269, bibcode="test")
        
        expected_url = "https://ned.ipac.caltech.edu/cgi-bin/nph-objsearch?objname=M31"
        assert url == expected_url


class TestNedApiIntegration:
    """Integration tests for NED API functionality."""
    
    def test_ned_api_default_format_is_json(self):
        """Test that default output format is JSON."""
        url_default = ned_api(object_name="M31")
        url_json = ned_api(object_name="M31", output_format='json')
        
        assert url_default == url_json
    
    def test_ned_api_coordinate_precision(self):
        """Test coordinate precision is maintained in URL."""
        ra = 10.68470833
        dec = 41.26916667
        
        url = ned_api(ra=ra, dec=dec, output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert params['lon'][0] == str(ra)
        assert params['lat'][0] == str(dec)
    
    def test_ned_api_radius_precision(self):
        """Test radius precision is maintained in URL."""
        radius = 1.5
        
        url = ned_api(ra=10.684, dec=41.269, radius_arcmin=radius, output_format='json')
        
        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        assert params['radius'][0] == str(radius)


if __name__ == '__main__':
    import subprocess

    # Run tests with pytest and capture output
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        __file__,
        '-v',
        '--tb=short',
        '--color=no'
    ], capture_output=True, text=True, cwd=Path(__file__).parent)

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Parse the output to extract test results
    lines = result.stdout.split('\n')
    total_tests = 0
    passed = 0
    failed = 0
    errors = 0
    passed_tests = []
    failed_tests = []
    error_tests = []

    for line in lines:
        if '::' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
            if 'PASSED' in line:
                passed += 1
                # Extract test name
                test_name = line.split('::')[-1].split(' PASSED')[0].strip()
                passed_tests.append(test_name)
            elif 'FAILED' in line:
                failed += 1
                test_name = line.split('::')[-1].split(' FAILED')[0].strip()
                failed_tests.append(test_name)
            elif 'ERROR' in line:
                errors += 1
                test_name = line.split('::')[-1].split(' ERROR')[0].strip()
                error_tests.append(test_name)

        # Try to extract total from summary line
        if 'passed' in line.lower() and 'failed' in line.lower():
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if part.endswith('passed'):
                    passed = int(part.split()[0])
                elif part.endswith('failed'):
                    failed = int(part.split()[0])
                elif part.endswith('error') or part.endswith('errors'):
                    errors = int(part.split()[0])

    total_tests = passed + failed + errors

    # Print dynamic test summary
    print("\n" + "="*60)
    print("📊 NED API TEST SUMMARY")
    print("="*60)
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"⚠️  ERRORS: {errors}")
    print(f"🔢 TOTAL:  {total_tests}")

    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
    print("="*60)

    # Show individual passed tests
    if passed_tests:
        print("\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"  • {test}")

    # Show individual failed tests
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"  • {test}")

    # Show individual error tests
    if error_tests:
        print("\n💥 ERROR TESTS:")
        for test in error_tests:
            print(f"  • {test}")

    print("="*60)

    if failed == 0 and errors == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("🚨 SOME TESTS FAILED OR ERRORED!")

    print("="*60 + "\n")

    # Exit with appropriate code
    sys.exit(1 if (failed > 0 or errors > 0) else 0)