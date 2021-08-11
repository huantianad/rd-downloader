{ pkgs ? import <nixpkgs> {} }:

let
  python-with-packages = pkgs.python39.withPackages (pyPkgs: with pyPkgs; [
    requests
    colorama
    termcolor
    (buildPythonPackage rec {
      pname = "alive-progress";
      version = "1.6.2";
      propagatedBuildInputs = [ pytest ];
      src = fetchPypi {
        inherit pname version;
        sha256 = "642e1ce98becf226c8c36bf24e10221085998c5465a357a66fb83b7dc618b43e";
      };
    })
  ]);
in
  pkgs.mkShell {
    name = "rd-downloader";
    buildInputs = [
      python-with-packages
    ];
  }