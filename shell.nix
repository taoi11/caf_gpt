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
    requests
    boto3

    # Development tools
    pylint
    black
    isort
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
  ];
  
  shellHook = ''
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Create static and media directories if they don't exist
    mkdir -p static/css static/js static/img media
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
      if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env file from .env.example. Please edit it with your settings."
      else
        echo "No .env.example file found. Please create a .env file manually."
      fi
    fi
    
    echo "NixOS development environment ready!"
    echo "Run 'python manage.py runserver' to start the development server."
  '';
}