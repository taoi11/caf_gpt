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
      in {
        devShell = pkgs.mkShell {
          packages = [
            pkgs.python312
            pkgs.git
          ];

          shellHook = ''
            echo "CAF-GPT Email Agent development environment"
            echo "Setting up Python virtual environment..."
            if [ ! -d venv ]; then
              python -m venv venv
            fi
            source venv/bin/activate
            echo "Virtual environment activated"
            echo "Run 'pip install -e .' to install dependencies"
            echo "Run 'python src/main.py' to start the application"
          '';
        };
      });
}
