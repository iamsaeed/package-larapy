#!/usr/bin/env python3
"""
Larapy CLI - Simple command line interface for the Larapy framework
"""

import click


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Larapy Framework CLI - Laravel concepts in Python"""
    pass


@cli.command()
def version():
    """Show the framework version"""
    click.echo("Larapy Framework v1.0.0")
    click.echo("Laravel concepts implemented in Python Flask")


@cli.command()
def info():
    """Show framework information"""
    click.echo("🚀 Larapy Framework")
    click.echo("   A Flask-based framework implementing Laravel's core concepts")
    click.echo("")
    click.echo("Features:")
    click.echo("  ✅ Service Container & Dependency Injection")
    click.echo("  ✅ Application Lifecycle Management")
    click.echo("  ✅ Service Providers")
    click.echo("  ✅ Facades")
    click.echo("  ✅ Laravel-style Routing")
    click.echo("  ✅ Middleware Pipeline")
    click.echo("  ✅ Eloquent-like ORM")
    click.echo("  ✅ Configuration Management")
    click.echo("")
    click.echo("Run 'python example_app.py' to see the framework in action!")


if __name__ == '__main__':
    cli()
