.. Zenith Analyser documentation master file, created by sphinx-quickstart

Zenith Analyser – Advanced Chrono-Informatics Library
=====================================================

**Zenith Analyser** is a specialized Python library dedicated to **chrono-informatics** —  
the computational study of time-organized structures, sequences, rhythms, temporal patterns,  
and chronological dynamics in simulated or observed event traces.

This library provides powerful tools to:

- Extract high-level **temporal statistics** (average duration, dispersion, rhythm consistency, temporal density)
- Detect **recurrent chronological patterns** using optimized suffix-array + LCP construction (O(n log n))
- Measure **sequence complexity** (transition variety, unique event ratio, entropy of regimes)
- Quantify **rhythm regularity**, inter-event dispersion and temporal coverage
- Generate publication-quality **visualizations** of temporal sequences (histograms, timelines, scatter sequences, pie charts of event types, multi-sequence comparisons)

Main application domains
------------------------

* Analysis of simulated legal / regulatory / social processes (law simulation, population dynamics)
* Study of target behaviors and chronological signatures
* Rhythm and cadence analysis in multi-agent simulations
* Pattern mining in long event traces (recurrent motifs, periodicity, anomalies)
* Chrono-informatics research — understanding computation as it unfolds over time

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   metrics
   visualizer


License
-------

Copyright © 2026 François TUMUSAVYEYESU  
Licensed under the **Apache License, Version 2.0**  
http://www.apache.org/licenses/LICENSE-2.0


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`