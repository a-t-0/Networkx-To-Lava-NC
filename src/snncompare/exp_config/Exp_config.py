""""Stores the run config Dict type."""
import sys
from typing import Dict, List, Optional, Union

from typeguard import typechecked

if sys.version_info < (3, 11):
    pass
else:
    pass


# pylint: disable=R0902
# pylint: disable=R0903
class Exp_config:
    """Stores the exp_configriment settings object."""

    # pylint: disable=R0913
    # pylint: disable=R0914
    @typechecked
    def __init__(
        self,
        adaptations: Union[None, Dict[str, int]],
        algorithms: Dict[str, Dict[str, int]],
        max_graph_size: int,
        max_max_graphs: int,
        min_graph_size: int,
        min_max_graphs: int,
        neuron_models: list,
        overwrite_s1_snn_creation: bool,
        overwrite_s2_snn_propagation: bool,
        overwrite_s3_export_images: bool,
        overwrite_s4_sim_results: bool,
        radiations: Dict,
        seed: int,
        simulators: list,
        size_and_max_graphs: list,
        synaptic_models: list,
        export_images: Optional[bool] = False,
        export_types: Optional[List[str]] = None,
        unique_id: Optional[str] = None,
    ):
        """Stores run configuration settings for the exp_configriment."""

        # Required properties
        self.adaptations: Union[None, Dict[str, int]] = adaptations
        self.algorithms: Dict[str, Dict[str, int]] = algorithms
        self.max_graph_size: int = max_graph_size
        self.max_max_graphs: int = max_max_graphs
        self.min_graph_size: int = min_graph_size
        self.min_max_graphs: int = min_max_graphs
        self.neuron_models: list = neuron_models
        self.overwrite_s1_snn_creation: bool = overwrite_s1_snn_creation
        self.overwrite_s2_snn_propagation: bool = overwrite_s2_snn_propagation
        self.overwrite_s3_export_images: bool = overwrite_s3_export_images
        self.overwrite_s4_sim_results: bool = overwrite_s4_sim_results
        self.radiations: Dict = radiations
        self.seed: int = seed
        self.simulators: list = simulators
        self.size_and_max_graphs: list = size_and_max_graphs
        self.synaptic_models: list = synaptic_models

        # Optional properties
        self.export_images: bool = bool(export_images)
        if self.export_images:
            if export_types is not None:
                self.export_types: List[str] = export_types

        if unique_id is not None:
            self.unique_id: str = unique_id

        # Verify run config object.