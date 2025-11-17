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
