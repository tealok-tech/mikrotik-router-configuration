# shell.nix
let
  # We pin to a specific nixpkgs commit for reproducibility.
  # Last updated: 2024-04-29. Check for new commits at https://status.nixos.org.
  pkgs = import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/cf8cc1201be8bc71b7cbbbdaf349b22f4f99c7ae.tar.gz") {};
  my-python-packages = python-packages: with python-packages; [
    aiohttp
  ];
  python-with-my-packages = pkgs.python3.withPackages my-python-packages;
in pkgs.mkShell {
  buildInputs = [
    pkgs.pre-commit
    python-with-my-packages
    pkgs.mypy
    pkgs.ruff
  ];
}
