# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python3
    pkgs.python3Packages.pip
  ];
  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "google.gemini-cli-vscode-ide-companion"
      "ms-python.python"
    ];
    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          # Attempt to install dependencies right before running to ensure they exist
          command = ["/bin/bash" "-c" "pip install -r requirements.txt && python3 -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"];
          manager = "web";
        };
      };
    };
    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        pip-install = "pip install -r requirements.txt";
        default.openFiles = [ "README.md" "app.py" ];
      };
      # Runs when the workspace is (re)started
      onStart = {
        pip-install = "pip install -r requirements.txt";
      };
    };
  };
}
