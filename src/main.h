#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>

char *run(const char *data, const char *outputType, double _lambda, float _hI0,
          int _chargePrecision, const char *_method, int _mR, int _mK,
          double _eta, const char *ionizationDataFilename,
          const char *chargeCentersFilename);

PYBIND11_MODULE(pyeqeq_eqeq, mod)
{
    // Allow capturing output
    pybind11::add_ostream_redirect(mod, "ostream_redirect");

    mod.def("run", &run, pybind11::return_value_policy::reference);
}

