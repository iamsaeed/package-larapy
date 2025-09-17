"""Testing helpers for response assertions."""

import json
from typing import Any, Dict, Optional, Union, List
from flask import Response as FlaskResponse, session


class ResponseAssertions:
    """Laravel-style response assertions for testing."""
    
    def __init__(self, response: FlaskResponse):
        """Initialize with Flask response."""
        self.response = response
        self._json_data = None
    
    def assert_status(self, status: int):
        """Assert response status code."""
        assert self.response.status_code == status, \
            f"Expected status {status}, got {self.response.status_code}"
        return self
    
    def assert_ok(self):
        """Assert response is OK (200)."""
        return self.assert_status(200)
    
    def assert_created(self):
        """Assert response is Created (201)."""
        return self.assert_status(201)
    
    def assert_no_content(self):
        """Assert response is No Content (204)."""
        return self.assert_status(204)
    
    def assert_redirect(self, url: Optional[str] = None):
        """Assert response is a redirect."""
        assert 300 <= self.response.status_code < 400, \
            f"Expected redirect status (3xx), got {self.response.status_code}"
        
        if url:
            location = self.response.headers.get('Location', '')
            assert url in location, \
                f"Expected redirect to '{url}', got '{location}'"
        
        return self
    
    def assert_unauthorized(self):
        """Assert response is Unauthorized (401)."""
        return self.assert_status(401)
    
    def assert_forbidden(self):
        """Assert response is Forbidden (403)."""
        return self.assert_status(403)
    
    def assert_not_found(self):
        """Assert response is Not Found (404)."""
        return self.assert_status(404)
    
    def assert_method_not_allowed(self):
        """Assert response is Method Not Allowed (405)."""
        return self.assert_status(405)
    
    def assert_unprocessable_entity(self):
        """Assert response is Unprocessable Entity (422)."""
        return self.assert_status(422)
    
    def assert_server_error(self):
        """Assert response is Server Error (500)."""
        return self.assert_status(500)
    
    def assert_header(self, header: str, value: Optional[str] = None):
        """Assert response has header."""
        assert header in self.response.headers, \
            f"Response does not have header '{header}'"
        
        if value is not None:
            actual_value = self.response.headers[header]
            assert actual_value == value, \
                f"Header '{header}' expected '{value}', got '{actual_value}'"
        
        return self
    
    def assert_header_missing(self, header: str):
        """Assert response does not have header."""
        assert header not in self.response.headers, \
            f"Response should not have header '{header}'"
        return self
    
    def assert_content_type(self, content_type: str):
        """Assert response content type."""
        actual_content_type = self.response.headers.get('Content-Type', '')
        assert content_type in actual_content_type, \
            f"Expected content type '{content_type}', got '{actual_content_type}'"
        return self
    
    def assert_json(self):
        """Assert response is JSON."""
        self.assert_content_type('application/json')
        return self
    
    def assert_html(self):
        """Assert response is HTML."""
        self.assert_content_type('text/html')
        return self
    
    def get_json(self) -> Dict:
        """Get JSON data from response."""
        if self._json_data is None:
            try:
                self._json_data = json.loads(self.response.get_data(as_text=True))
            except json.JSONDecodeError:
                raise AssertionError("Response is not valid JSON")
        return self._json_data
    
    def assert_json_structure(self, structure: Union[Dict, List]):
        """Assert JSON response has expected structure."""
        data = self.get_json()
        self._assert_structure_matches(data, structure)
        return self
    
    def assert_json_path(self, path: str, value: Any = None):
        """Assert JSON path exists and optionally has value."""
        data = self.get_json()
        current = data
        
        # Navigate through path
        for key in path.split('.'):
            if isinstance(current, dict):
                assert key in current, f"JSON path '{path}' not found"
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key)
                    assert 0 <= index < len(current), f"JSON array index '{index}' out of range"
                    current = current[index]
                except ValueError:
                    raise AssertionError(f"Invalid array index '{key}' in path '{path}'")
            else:
                raise AssertionError(f"Cannot navigate path '{path}' - not a dict or list")
        
        if value is not None:
            assert current == value, \
                f"JSON path '{path}' expected '{value}', got '{current}'"
        
        return self
    
    def assert_json_count(self, count: int, path: Optional[str] = None):
        """Assert JSON array has expected count."""
        data = self.get_json()
        
        if path:
            current = data
            for key in path.split('.'):
                current = current[key]
        else:
            current = data
        
        assert isinstance(current, list), "JSON data is not an array"
        assert len(current) == count, \
            f"Expected {count} items, got {len(current)}"
        
        return self
    
    def assert_json_missing(self, path: str):
        """Assert JSON path does not exist."""
        data = self.get_json()
        current = data
        
        try:
            for key in path.split('.'):
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return self  # Path doesn't exist, assertion passes
            
            # If we get here, path exists
            raise AssertionError(f"JSON path '{path}' should not exist")
        except (KeyError, TypeError):
            return self  # Path doesn't exist, assertion passes
    
    def assert_see(self, text: str):
        """Assert response contains text."""
        content = self.response.get_data(as_text=True)
        assert text in content, f"Response does not contain '{text}'"
        return self
    
    def assert_dont_see(self, text: str):
        """Assert response does not contain text."""
        content = self.response.get_data(as_text=True)
        assert text not in content, f"Response should not contain '{text}'"
        return self
    
    def assert_see_text(self, text: str):
        """Assert response contains text (HTML-aware)."""
        # This would need HTML parsing for true HTML-aware text checking
        return self.assert_see(text)
    
    def assert_dont_see_text(self, text: str):
        """Assert response does not contain text (HTML-aware)."""
        return self.assert_dont_see(text)
    
    def assert_view_has(self, key: str, value: Any = None):
        """Assert view was passed specific data."""
        # This would need integration with view system to track view data
        # For now, just check if data appears in response content
        content = self.response.get_data(as_text=True)
        if isinstance(value, str):
            assert value in content, f"View data '{key}' with value '{value}' not found in response"
        else:
            # For non-string values, just check if key appears
            assert str(key) in content, f"View data key '{key}' not found in response"
        return self
    
    def assert_view_has_all(self, data: Dict):
        """Assert view was passed all specified data."""
        for key, value in data.items():
            self.assert_view_has(key, value)
        return self
    
    def assert_view_missing(self, key: str):
        """Assert view was not passed specific data."""
        content = self.response.get_data(as_text=True)
        assert str(key) not in content, f"View should not have data key '{key}'"
        return self
    
    def assert_location(self, url: str):
        """Assert response Location header."""
        return self.assert_header('Location', url)
    
    def _assert_structure_matches(self, data: Any, structure: Any):
        """Recursively check if data matches structure."""
        if isinstance(structure, dict):
            assert isinstance(data, dict), "Expected dict in JSON structure"
            for key, expected_type in structure.items():
                assert key in data, f"Missing key '{key}' in JSON"
                self._assert_structure_matches(data[key], expected_type)
        elif isinstance(structure, list):
            assert isinstance(data, list), "Expected list in JSON structure"
            if structure:  # If structure list is not empty
                for item in data:
                    self._assert_structure_matches(item, structure[0])
        elif structure is not None:
            # Check type if structure specifies a type
            if isinstance(structure, type):
                assert isinstance(data, structure), \
                    f"Expected {structure.__name__}, got {type(data).__name__}"


class SessionAssertions:
    """Session-related assertions."""
    
    @staticmethod
    def assert_session_has(key: str, value: Any = None):
        """Assert session has key and optionally value."""
        assert key in session, f"Session does not have key '{key}'"
        
        if value is not None:
            actual_value = session[key]
            assert actual_value == value, \
                f"Session key '{key}' expected '{value}', got '{actual_value}'"
    
    @staticmethod
    def assert_session_missing(key: str):
        """Assert session does not have key."""
        assert key not in session, f"Session should not have key '{key}'"
    
    @staticmethod
    def assert_session_has_errors(key: str = 'default'):
        """Assert session has validation errors."""
        assert '_errors' in session, "Session does not have errors"
        assert key in session['_errors'], f"Session does not have errors for key '{key}'"
    
    @staticmethod
    def assert_session_has_no_errors():
        """Assert session has no validation errors."""
        assert '_errors' not in session or not session['_errors'], \
            "Session should not have errors"
    
    @staticmethod
    def assert_old_input_has(key: str, value: Any = None):
        """Assert old input has key and optionally value."""
        assert '_old_input' in session, "Session does not have old input"
        old_input = session['_old_input']
        assert key in old_input, f"Old input does not have key '{key}'"
        
        if value is not None:
            actual_value = old_input[key]
            assert actual_value == value, \
                f"Old input key '{key}' expected '{value}', got '{actual_value}'"


class CookieAssertions:
    """Cookie-related assertions."""
    
    def __init__(self, response: FlaskResponse):
        """Initialize with Flask response."""
        self.response = response
    
    def assert_cookie(self, name: str, value: Any = None):
        """Assert response sets cookie."""
        cookies = self._get_set_cookies()
        assert name in cookies, f"Response does not set cookie '{name}'"
        
        if value is not None:
            actual_value = cookies[name]['value']
            assert actual_value == str(value), \
                f"Cookie '{name}' expected '{value}', got '{actual_value}'"
        
        return self
    
    def assert_cookie_missing(self, name: str):
        """Assert response does not set cookie."""
        cookies = self._get_set_cookies()
        assert name not in cookies, f"Response should not set cookie '{name}'"
        return self
    
    def assert_cookie_expired(self, name: str):
        """Assert response expires cookie."""
        cookies = self._get_set_cookies()
        assert name in cookies, f"Response does not set cookie '{name}'"
        
        cookie = cookies[name]
        # Check if expires is in the past or max_age is 0
        expires = cookie.get('expires')
        max_age = cookie.get('max_age')
        
        if expires and 'Thu, 01 Jan 1970' in expires:
            return self
        if max_age == 0:
            return self
        
        raise AssertionError(f"Cookie '{name}' is not expired")
    
    def _get_set_cookies(self) -> Dict:
        """Extract Set-Cookie headers."""
        cookies = {}
        set_cookie_headers = self.response.headers.getlist('Set-Cookie')
        
        for header in set_cookie_headers:
            # Simple parsing - would need more robust parsing in production
            parts = header.split(';')
            if parts:
                name_value = parts[0].strip()
                if '=' in name_value:
                    name, value = name_value.split('=', 1)
                    cookies[name] = {'value': value}
                    
                    # Parse other attributes
                    for part in parts[1:]:
                        part = part.strip()
                        if '=' in part:
                            attr_name, attr_value = part.split('=', 1)
                            cookies[name][attr_name.lower()] = attr_value
                        else:
                            cookies[name][part.lower()] = True
        
        return cookies


def assert_response(response: FlaskResponse) -> ResponseAssertions:
    """Create response assertions helper."""
    return ResponseAssertions(response)


def assert_session() -> SessionAssertions:
    """Create session assertions helper."""
    return SessionAssertions()


def assert_cookies(response: FlaskResponse) -> CookieAssertions:
    """Create cookie assertions helper."""
    return CookieAssertions(response)