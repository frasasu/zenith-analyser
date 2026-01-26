zenith_analyser.metrics – Core Chrono-Informatics Engine
========================================================

.. automodule:: zenith_analyser.metrics
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`ZenithMetrics` class is the central component for temporal analysis.

.. autoclass:: ZenithMetrics
   :members:
   :undoc-members:
   :show-inheritance:

Key chrono-informatics features
-------------------------------

Pattern detection (suffix-array based)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ZenithMetrics.detect_patterns

Comprehensive temporal profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ZenithMetrics.get_comprehensive_metrics

Temporal statistics & rhythm analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ZenithMetrics.calculate_temporal_statistics
.. automethod:: ZenithMetrics.calculate_rhythm_metrics
.. automethod:: ZenithMetrics.calculate_temporal_density
.. automethod:: ZenithMetrics.calculate_sequence_complexity
.. automethod:: ZenithMetrics.calculate_event_frequency
.. automethod:: ZenithMetrics.calculate_entropy

Data extraction & scientific export
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ZenithMetrics.get_data_simulations
.. automethod:: ZenithMetrics.get_data_law
.. automethod:: ZenithMetrics.get_data_target
.. automethod:: ZenithMetrics.get_data_population

.. automethod:: ZenithMetrics.get_metrics_law
.. automethod:: ZenithMetrics.get_metrics_target
.. automethod:: ZenithMetrics.get_metrics_population

Low-level suffix array utilities (used internally by pattern detection)
-----------------------------------------------------------------------

.. automethod:: ZenithMetrics._build_suffix_array
.. automethod:: ZenithMetrics._build_lcp