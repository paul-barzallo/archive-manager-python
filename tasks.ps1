#!/usr/bin/env pwsh
# PowerShell task runner for the contacts manager application
# Usage: .\tasks.ps1 <command>
# Commands: test, lint, format, check, clean, install

param(
    [Parameter(Position = 0)]
    [ValidateSet('test', 'lint', 'format', 'check', 'clean', 'install', 'help')]
    [string]$Command = 'help'
)

$ErrorActionPreference = 'Stop'

function Write-Header {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

switch ($Command) {
    'test' {
        Write-Header "Running tests with pytest..."
        python -m pytest tests/ -v
    }

    'lint' {
        Write-Header "Running linters..."

        if (Test-Command 'ruff') {
            Write-Host "Running ruff..." -ForegroundColor Yellow
            ruff check src/ tests/
        } else {
            Write-Host "ruff not found. Install with: pip install ruff" -ForegroundColor Red
        }

        if (Test-Command 'mypy') {
            Write-Host "`nRunning mypy..." -ForegroundColor Yellow
            mypy src/
        } else {
            Write-Host "mypy not found. Install with: pip install mypy" -ForegroundColor Red
        }
    }

    'format' {
        Write-Header "Formatting code..."

        if (Test-Command 'ruff') {
            Write-Host "Running ruff format..." -ForegroundColor Yellow
            ruff format src/ tests/
            ruff check --fix src/ tests/
        } else {
            Write-Host "ruff not found. Install with: pip install ruff" -ForegroundColor Red
            exit 1
        }
    }

    'check' {
        Write-Header "Running all checks..."
        & $PSCommandPath format
        & $PSCommandPath lint
        & $PSCommandPath test
    }

    'clean' {
        Write-Header "Cleaning build artifacts and caches..."

        $patterns = @(
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.egg-info',
            '.pytest_cache',
            '.mypy_cache',
            '.ruff_cache',
            'dist',
            'build',
            'htmlcov',
            '.coverage'
        )

        foreach ($pattern in $patterns) {
            Get-ChildItem -Path . -Recurse -Filter $pattern -Force -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }

        Write-Host "Clean complete!" -ForegroundColor Green
    }

    'install' {
        Write-Header "Installing dependencies..."

        if (Test-Path 'requirements.txt') {
            python -m pip install -r requirements.txt
        }

        python -m pip install -e .

        Write-Host "`nInstalling development dependencies..." -ForegroundColor Yellow
        python -m pip install pytest ruff mypy pre-commit

        Write-Host "`nSetting up pre-commit hooks..." -ForegroundColor Yellow
        if (Test-Command 'pre-commit') {
            pre-commit install
        } else {
            Write-Host "Warning: pre-commit not found in PATH" -ForegroundColor Yellow
        }

        Write-Host "`nInstallation complete!" -ForegroundColor Green
    }

    'help' {
        Write-Host @"

PowerShell Task Runner for Contacts Manager
============================================

Usage: .\tasks.ps1 <command>

Commands:
  test      Run pytest test suite
  lint      Run linters (ruff, mypy)
  format    Format code with ruff
  check     Run format, lint, and test
  clean     Remove build artifacts and caches
  install   Install dependencies and setup dev environment
  help      Show this help message

Examples:
  .\tasks.ps1 test
  .\tasks.ps1 format
  .\tasks.ps1 check

"@ -ForegroundColor White
    }
}
