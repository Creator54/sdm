{
  description = "A minimal CLI tool for managing SigNoz dashboards";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
      in
      {
        packages.default = python.pkgs.buildPythonApplication {
          pname = "sdm";
          version = "0.1.0";
          src = ./.;

          propagatedBuildInputs = with python.pkgs; [
            requests
            python-dotenv
            rich
            pyjwt
          ];

          doCheck = false;  # Disable tests for now
        };

        apps.default = flake-utils.lib.mkApp {
          drv = self.packages.${system}.default;
        };
      }
    );
} 