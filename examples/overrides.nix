{ pkgs, python, self }:
  with pkgs.lib;

{
  lxml = { buildInputs=[pkgs.libxml2 pkgs.libxslt]; };
  pysqlite = { buildInputs=[pkgs.sqlite]; };
  pylibmc = { propagatedBuildInputs = [pkgs.libmemcached pkgs.cyrus_sasl pkgs.zlib]; };
  psycopg2 = { buildInputs=[pkgs.postgresql]; };
  pyyaml = p: { buildInputs = p.buildInputs ++ [pkgs.libyaml]; };
  cffi = p: { buildInputs = p.buildInputs ++ [pkgs.libffi]; };

  graph-explorer = p: { propagatedBuildInputs = p.propagatedBuildInputs++[python.modules.sqlite3]; doCheck = false; };
  sentry = {
    preCheck = ''
      rm tests/sentry/buffer/redis/tests.py
      rm tests/sentry/quotas/redis/tests.py
    '';
  };
  django-celery = p: { buildInputs = p.buildInputs ++ [python.modules.sqlite3]; };
  graphite-api = { doCheck = false; };
  plone = { doCheck = false; };
  relstorage = { doCheck = false; };
  numpy = {
    preBuild = ''export BLAS=${pkgs.blas} LAPACK=${pkgs.liblapack}'';
    setupPyBuildFlags = ["--fcompiler='gnu95'"];
    buildInputs = [ pkgs.gfortran pkgs.liblapack pkgs.blas ];
    doCheck = false;
  };
  scipy = {
    preBuild = ''export BLAS=${pkgs.blas} LAPACK=${pkgs.liblapack}'';
    setupPyBuildFlags = ["--fcompiler='gnu95'"];
    buildInputs = [ pkgs.gfortran pkgs.liblapack pkgs.blas ];
    preConfigure = ''
      export BLAS=${pkgs.blas} LAPACK=${pkgs.liblapack}
      sed -i '0,/from numpy.distutils.core/s//import setuptools;from numpy.distutils.core/' setup.py
    '';
    doCheck = false;
  };
  almir = p: {
    buildInputs = p.buildInputs ++ [pkgs.which pkgs.bacula];
    postInstall = ''
      ln -s ${pkgs.bacula}/bin/bconsole $out/bin
    '';
  };
  pyramid = {
    preCheck = ''
      rm pyramid/tests/test_response.py
    '';
  };
}
