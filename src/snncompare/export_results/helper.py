"""Contains helper functions for exporting simulation results."""
import collections
import copy
import hashlib
import json
from typing import Any, Dict, List, Union

import networkx as nx
from simsnn.core.simulators import Simulator
from snnradiation.Rad_damage import list_of_hashes_to_hash
from typeguard import typechecked

from snncompare.exp_config.Exp_config import Exp_config

from ..helper import get_some_duration


@typechecked
def flatten(
    *, d: Dict, parent_key: str = "", sep: str = "_"
) -> Union[Dict, Dict[str, float], Dict[str, int]]:
    """Flattens a dictionary (makes multiple lines into a oneliner)."""
    items: List = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(
                flatten(d=dict(v), parent_key=new_key, sep=sep).items()
            )
        else:
            items.append((new_key, v))
    return dict(items)


@typechecked
def exp_config_to_filename(
    *,
    exp_config: Exp_config,
) -> str:
    """Converts an Exp_config dictionary into a filename.

    Does that by flattining the dictionary (and all its child-
    dictionaries).
    """
    # TODO: order dictionaries by alphabetical order by default.
    # TODO: allow user to specify a custom order of parameters.

    # stripped_run_config:Dict = copy.deepcopy(run_config).__dict__
    stripped_exp_config: Exp_config = copy.deepcopy(exp_config)
    stripped_exp_config_dict: Dict = stripped_exp_config.__dict__
    unique_id = stripped_exp_config_dict["unique_id"]
    stripped_exp_config_dict.pop("unique_id")

    # Convert all the radiation settings into a list of hashes.
    list_of_rad_hashes: List[str] = list(
        map(
            lambda radiation: radiation.get_rad_settings_hash(),
            stripped_exp_config_dict["radiations"],
        )
    )
    # Convert the list of hashes into a single hash.
    stripped_exp_config_dict["radiation"] = list_of_hashes_to_hash(
        hashes=list_of_rad_hashes
    )

    # instead (To reduce filename length).
    filename = str(flatten(d=stripped_exp_config_dict))

    # Remove the ' symbols.
    # Don't, that makes it more difficult to load the dict again.
    # filename=filename.replace("'","")

    # Don't, that makes it more difficult to load the dict again.
    # Remove the spaces.
    filename = filename.replace(" ", "")
    filename = filename.replace("'", "")
    filename = filename.replace("[", "")
    filename = filename.replace("]", "")
    filename = filename.replace("{", "")
    filename = filename.replace("}", "")
    filename = filename.replace("adaptations_", "")
    filename = filename.replace("algorithms_", "")
    filename = filename.replace("graphs_", "")
    filename = filename.replace("radiations_", "")
    filename = filename.replace("unique_", "")

    if len(filename) > 256:
        filename = unique_id
        # raise NameError(f"Filename={filename} is too long:{len(filename)}")

    return filename


@typechecked
def get_expected_image_paths_stage_3(  # type:ignore[misc]
    *,
    nx_graphs_dict: Dict[str, Union[nx.Graph, nx.DiGraph, Simulator]],
    input_graph: nx.Graph,
    run_config: Any,
    extensions: List[str],
) -> List[str]:
    """Returns the expected image filepaths for stage 3.

    (If export is on).
    """
    image_filepaths = []

    if "alg_props" not in input_graph.graph.keys():
        raise KeyError("Error, algo_props is not set.")

    # TODO: move this into hardcoded setting.
    image_dir = "latex/Images/graphs/"
    for extension in extensions:
        for graph_name, snn_graph in nx_graphs_dict.items():
            if graph_name != "input_graph":
                sim_duration = get_some_duration(
                    simulator=run_config.simulator,
                    snn_graph=snn_graph,
                    duration_name="actual_duration",
                )
                for t in range(0, sim_duration):
                    image_filepaths.append(
                        image_dir
                        + f"{graph_name}_{run_config.unique_id}"
                        + f"_{t}.{extension}"
                    )
    return image_filepaths


@typechecked
def get_unique_run_config_id(  # type:ignore[misc]
    *,
    run_config: Any,
) -> str:
    """Checks if an experiment configuration dictionary already has a unique
    identifier, and if not it computes and appends it.

    If it does, throws an error.
    TODO: move into helper

    :param exp_config: Exp_config:
    """
    if "unique_id" in run_config.__dict__.keys():
        raise KeyError(
            f"Error, the exp_config:{run_config}\n"
            + "already contains a unique identifier."
        )

    # Create deepcopy.
    some_config = copy.deepcopy(run_config)

    # Convert Rad_damage into hash
    del some_config.radiation
    some_config.radiation = run_config.radiation.get_rad_settings_hash()

    # Compute a unique code belonging to this particular experiment
    # configuration.
    unique_id = str(
        hashlib.sha256(
            json.dumps(sorted(some_config.__dict__)).encode("utf-8")
        ).hexdigest()
    )
    return unique_id
