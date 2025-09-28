{ pkgs ? (import <nixpkgs> {}) }:

let
  # Python 3.12 packages
  pythonPackages = pkgs.python312.withPackages (ps: with ps; [
    # Application dependencies
    python-dotenv
    psycopg2
    django
    django-debug-toolbar
    gunicorn
    django-cors-headers
    django-csp
    requests
    boto3
    whitenoise

    # Development tools
    isort
    flake8
    autopep8
    pyflakes
  ]);
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python environment
    pythonPackages
    
    # Database
    postgresql
    
    # Development tools
    tree
    git

    # A tiny helper that formats simple whitespace issues with autopep8, then runs flake8
    (writeShellScriptBin "lint" ''
      #!/usr/bin/env bash
      set -euo pipefail
      autopep8 --in-place --recursive -v .
      # Lint afterwards to see remaining issues
      flake8 -v
    '')
  ];
}