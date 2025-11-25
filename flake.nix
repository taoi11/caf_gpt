{
  description = "CAF-GPT Email Agent - FastAPI app for AI email responses";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        python = pkgs.python312;

        yagmail = python.buildPythonPackage rec {
          pname = "yagmail";
          version = "0.15.293";
          src = python.fetchPypi {
            inherit pname version;
            sha256 = "947a0864e4a64452c8e6b58c80b5bf45389bf8842d779701febfd34fa09649c7";
          };
          propagatedBuildInputs = with pkgs.python312Packages; [
            keyring
            keyrings.alt
            secure-smtplib
          ];
          doCheck = false;
        };

        pythonPackages = pypkgs: with pypkgs; [
          fastapi
          uvicorn
          pydantic
          pydantic-settings
          python-dotenv
          requests
          email-validator
          boto3
          structlog
          black
          mypy
          pytest
          imap-tools
          yagmail
          jinja2
          ollama
        ];

        pythonWithPackages = python.withPackages pythonPackages;

      in {
        devShell = pkgs.mkShell {
          packages = [
            pythonWithPackages
            pkgs.git
          ];

          shellHook = ''
            echo "CAF-GPT Email Agent development environment"
            echo "Run 'python src/main.py' to start the application"
          '';
        };
      });
}
