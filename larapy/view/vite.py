"""
Vite integration for Larapy - Laravel-like asset compilation
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from markupsafe import Markup
from flask import current_app


class ViteHelper:
    """Helper class for Vite asset compilation integration"""

    def __init__(self, public_path: str = None, build_directory: str = 'build'):
        self.public_path = public_path or self._get_public_path()
        self.build_directory = build_directory
        self.manifest_path = os.path.join(self.public_path, build_directory, '.vite', 'manifest.json')
        self.hot_file_path = os.path.join(self.public_path, 'hot')
        self._manifest_cache = None

    def _get_public_path(self) -> str:
        """Get the public path from Flask app config or default"""
        # Use current working directory + public instead of Flask's static folder
        import os
        from pathlib import Path

        public_path = Path.cwd() / 'public'
        return str(public_path)

    def is_running_hot(self) -> bool:
        """Check if Vite dev server is running"""
        return os.path.exists(self.hot_file_path)

    def get_hot_server_url(self) -> Optional[str]:
        """Get the Vite dev server URL"""
        if not self.is_running_hot():
            return None

        try:
            with open(self.hot_file_path, 'r') as f:
                return f.read().strip()
        except (IOError, OSError):
            return None

    def get_manifest(self) -> Dict[str, Any]:
        """Load and cache the Vite manifest file"""
        if self._manifest_cache is not None:
            return self._manifest_cache

        if not os.path.exists(self.manifest_path):
            return {}

        try:
            with open(self.manifest_path, 'r') as f:
                self._manifest_cache = json.load(f)
                return self._manifest_cache
        except (IOError, json.JSONDecodeError):
            return {}

    def get_asset_url(self, entry: str) -> Optional[str]:
        """Get the URL for a specific asset entry"""
        if self.is_running_hot():
            hot_url = self.get_hot_server_url()
            if hot_url:
                return f"{hot_url}/{entry}"

        manifest = self.get_manifest()
        if entry in manifest:
            asset_info = manifest[entry]
            if isinstance(asset_info, dict) and 'file' in asset_info:
                return f"/{self.build_directory}/{asset_info['file']}"
            elif isinstance(asset_info, str):
                return f"/{self.build_directory}/{asset_info}"

        return None

    def get_asset_imports(self, entry: str) -> List[str]:
        """Get CSS imports for a JavaScript entry"""
        manifest = self.get_manifest()
        if entry in manifest:
            asset_info = manifest[entry]
            if isinstance(asset_info, dict) and 'css' in asset_info:
                return [f"/{self.build_directory}/{css}" for css in asset_info['css']]
        return []

    def generate_script_tag(self, src: str, **attributes) -> str:
        """Generate a script tag with proper attributes"""
        attrs = []

        # Add default attributes for ES modules
        if self.is_running_hot():
            attributes.setdefault('type', 'module')
        else:
            attributes.setdefault('type', 'module')

        # Build attribute string
        for key, value in attributes.items():
            if value is True:
                attrs.append(key)
            elif value is not False and value is not None:
                attrs.append(f'{key}="{value}"')

        attr_string = ' ' + ' '.join(attrs) if attrs else ''
        return f'<script src="{src}"{attr_string}></script>'

    def generate_css_tag(self, href: str, **attributes) -> str:
        """Generate a CSS link tag"""
        attrs = []
        attributes.setdefault('rel', 'stylesheet')

        for key, value in attributes.items():
            if value is True:
                attrs.append(key)
            elif value is not False and value is not None:
                attrs.append(f'{key}="{value}"')

        attr_string = ' ' + ' '.join(attrs) if attrs else ''
        return f'<link href="{href}"{attr_string}>'

    def generate_vite_client_tag(self) -> str:
        """Generate Vite client script tag for HMR"""
        if not self.is_running_hot():
            return ''

        hot_url = self.get_hot_server_url()
        if not hot_url:
            return ''

        return self.generate_script_tag(f"{hot_url}/@vite/client", type="module")

    def generate_asset_tags(self, entries: List[str]) -> str:
        """Generate all necessary script and link tags for given entries"""
        tags = []

        # Add Vite client for HMR in development
        vite_client = self.generate_vite_client_tag()
        if vite_client:
            tags.append(vite_client)

        # Process each entry
        for entry in entries:
            asset_url = self.get_asset_url(entry)
            if not asset_url:
                continue

            # Generate script tag for JS files
            if entry.endswith('.js'):
                tags.append(self.generate_script_tag(asset_url))

                # Add CSS imports for this JS entry
                css_imports = self.get_asset_imports(entry)
                for css_url in css_imports:
                    tags.append(self.generate_css_tag(css_url))

            # Generate link tag for CSS files
            elif entry.endswith('.css'):
                tags.append(self.generate_css_tag(asset_url))

        return '\n'.join(tags)


def vite(entries: List[str], **kwargs) -> Markup:
    """
    Generate Vite asset tags for templates

    Usage in Jinja2 templates:
    {{ vite(['resources/css/app.css', 'resources/js/app.js']) }}
    """
    vite_helper = ViteHelper(**kwargs)
    tags = vite_helper.generate_asset_tags(entries)
    return Markup(tags)


def setup_vite_helper(app):
    """Setup Vite helper for Flask app"""
    app.jinja_env.globals['vite'] = vite