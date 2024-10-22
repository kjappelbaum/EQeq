# -*- coding: utf-8 -*-
import io
import json
import pathlib
from contextlib import ExitStack, redirect_stderr
import tempfile
from typing import Union

from manage_crystal.utils import parse_and_write

import pyeqeq_eqeq

from .settings import CHARGE_DATA_PATH, IONIZATION_DATA_PATH


def run_on_cif(
    cif,
    output_type: str = "list",
    dielectric_screening: float = 1.2,
    h_electron_affinity: float = -2.0,
    charge_precision: int = 3,
    method: str = "ewald",
    num_cells_real: int = 2,
    num_cells_freq: int = 2,
    ewald_splitting: float = 50,
    ionization_data_path: Union[str, pathlib.Path] = IONIZATION_DATA_PATH,
    charge_data_path: Union[str, pathlib.Path] = CHARGE_DATA_PATH,
    outpath: Union[str, pathlib.Path] = None,
    verbose: bool = True,
):
    output_type = output_type.lower()
    method = method.lower()

    # ExitStack allows conditional context manager
    with tempfile.TemporaryDirectory() as temp_dir, ExitStack() as stack:
        if not verbose:
            # Capture stderr. It is currently discarded (but could be returned)
            _stderr = io.StringIO()
            stack.enter_context(redirect_stderr(_stderr))

        # Standardize CIF file
        # Many valid CIF files will not be correctly read by EQeq, since that assumes a particular ordering of the
        # atom properties, see https://github.com/lsmo-epfl/EQeq/issues/24
        # We use the manage_crystals library to bring any input CIF file into the format expected by EQeq
        if verbose:
            print("Standardizing CIF file")
        temp_filename = str(pathlib.Path(temp_dir) / "standardized.cif")
        parse_and_write(cif, temp_filename)

        # Redirect C++ std::cout and std::cerr to python sys.stdout and sys.stderr
        # This needs to happen *before* capturing stdout/stderr at the python
        with pyeqeq_eqeq.ostream_redirect(stdout=True, stderr=True):

            result = pyeqeq_eqeq.run(
                temp_filename,
                "json" if output_type == "list" else output_type,
                dielectric_screening,
                h_electron_affinity,
                charge_precision,
                method,
                num_cells_real,
                num_cells_freq,
                ewald_splitting,
                ionization_data_path,
                charge_data_path,
            )
    if outpath is not None:
        with open(outpath, "w") as handle:
            handle.write(result)

    if output_type == "list":
        return json.loads(result)
    return result
