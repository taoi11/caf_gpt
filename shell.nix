{ pkgs ? (import <nixpkgs> {}) }:

let
  # Python 3.12 packages
  pythonPackages = pkgs.python312.withPackages (ps: with ps; [
    # Application dependencies
    python-dotenv
    fastapi
    uvicorn
    requests
    boto3

    # Development tools
    black
    mypy
    pytest
  ]);
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python environment
    pythonPackages
    
    # Development tools
    tree
    git
  ];
}