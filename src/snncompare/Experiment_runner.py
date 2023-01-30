"""Contains the object that runs the entire experiment. Also Contains a single
setting of the experiment configuration settings.

(The values of the settings may vary, yet the types should be the same.)
"""
import functools
import timeit
from decimal import Decimal
from pprint import pprint
from typing import Dict, List, Optional

from snnbackends.plot_graphs import create_root_dir_if_not_exists
from snnbackends.verify_nx_graphs import verify_results_nx_graphs
from typeguard import typechecked

from snncompare.exp_config.Exp_config import (
    Exp_config,
    Supported_experiment_settings,
    append_unique_exp_config_id,
)
from snncompare.exp_config.run_config.Run_config import Run_config
from snncompare.helper import dicts_are_equal, generate_run_configs

from .exp_config.run_config.verify_run_completion import (
    assert_stage_is_completed,
)
from .exp_config.run_config.verify_run_settings import verify_has_unique_id
from .export_results.load_json_to_nx_graph import (
    load_json_to_nx_graph_from_file,
)
from .export_results.Output_stage_12 import output_files_stage_1_and_2
from .export_results.Output_stage_34 import output_stage_files_3_and_4
from .graph_generation.stage_1_get_input_graphs import get_used_graphs
from .import_results.check_completed_stages import has_outputted_stage
from .import_results.stage_1_load_input_graphs import load_results_stage_1
from .process_results.process_results import (
    export_results_to_json,
    set_results,
)
from .simulation.stage2_sim import sim_graphs

template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""
timeit.template = template  # type: ignore[attr-defined]


class Experiment_runner:
    """Experiment manager.

    First prepares the environment for running the experiment, and then
    calls a private method that executes the experiment consisting of 4
    stages.
    """

    # pylint: disable=R0903

    @typechecked
    def __init__(
        self,
        exp_config: Exp_config,
        specific_run_config: Optional[Run_config] = None,
        perform_run: bool = True,
    ) -> None:

        # Ensure output directories are created for stages 1 to 4.
        create_root_dir_if_not_exists("results")

        # Store the experiment configuration settings.
        self.exp_config = exp_config

        # Load the ranges of supported settings.
        self.supp_exp_config = Supported_experiment_settings()

        # Verify the experiment exp_config are complete and valid.
        # pylint: disable=R0801
        # verify_exp_config(
        #    self.supp_exp_config,
        #    exp_config,
        #    has_unique_id=False,
        #    allow_optional=True,
        # )

        # If the experiment exp_config does not contain a hash-code,
        # create the unique hash code for this configuration.
        # TODO: restore
        if not self.supp_exp_config.has_unique_config_id(self.exp_config):
            append_unique_exp_config_id(
                self.exp_config,
            )

        # Verify the unique hash code for this configuration is valid.
        verify_has_unique_id(self.exp_config.__dict__)

        self.run_configs = generate_run_configs(
            exp_config, specific_run_config
        )

        # Perform runs accordingly.
        if perform_run:
            self.__perform_run(self.exp_config, self.run_configs)

    # pylint: disable=W0238
    @typechecked
    def __perform_run(
        self, exp_config: Exp_config, run_configs: List[Run_config]
    ) -> None:
        """Private method that performs a run of the experiment.

        The 2 underscores indicate it is private. This method executes
        the run in the way the processed configuration settings specify.
        """
        duration: float
        results_nx_graphs: Dict
        for i, run_config in enumerate(run_configs):

            print(f"\n{i+1}/{len(run_configs)} [runs]")
            pprint(run_config.__dict__)

            print("\nstart stage I:  ", end=" ")

            duration, results_nx_graphs = timeit.Timer(  # type:ignore[misc]
                functools.partial(
                    self.__perform_run_stage_1,
                    exp_config,
                    run_config,
                )
            ).timeit(1)
            print(f"{round(duration,5)} [s]")
            print("Start stage II  ", end=" ")
            duration, _ = timeit.Timer(  # type:ignore[misc]
                functools.partial(
                    self.__perform_run_stage_2,
                    results_nx_graphs,
                    run_config,
                )
            ).timeit(1)
            print(f"{round(duration,5)} [s]")
            print("Start stage III ", end=" ")
            duration, _ = timeit.Timer(  # type:ignore[misc]
                functools.partial(
                    self.__perform_run_stage_3, results_nx_graphs, run_config
                )
            ).timeit(1)
            print(f"{round( Decimal(round(float(duration), 5)),5)} [s]")

            print("Start stage IV  ", end=" ")
            duration, _ = timeit.Timer(  # type:ignore[misc]
                functools.partial(
                    self.__perform_run_stage_4,
                    results_nx_graphs,
                )
            ).timeit(1)
            print(f"{round(duration,5)} [s]")
            # Store run results in dict of Experiment_runner.
            self.results_nx_graphs: Dict = {
                run_config.unique_id: results_nx_graphs  # type:ignore[index]
            }

    @typechecked
    def __perform_run_stage_1(
        self,
        exp_config: Exp_config,
        run_config: Run_config,
    ) -> Dict:
        """Performs the run for stage 1 or loads the data from file depending
        on the run configuration.

        Stage 1 applies a conversion that the user specified to run an
        SNN algorithm. This is done by taking an input graph, and
        generating an SNN (graph) that runs the intended algorithm.
        """

        # Check if stage 1 is performed. If not, perform it.
        if not has_outputted_stage(run_config, 1) or run_config.recreate_s1:
            # Run first stage of experiment, get input graph.
            stage_1_graphs: Dict = get_used_graphs(run_config)
            results_nx_graphs = {
                "exp_config": exp_config,
                "run_config": run_config,
                "graphs_dict": stage_1_graphs,
            }

            # Exports results, including graphs as dict.
            output_files_stage_1_and_2(results_nx_graphs, 1)
        else:
            results_nx_graphs = load_results_stage_1(run_config)
        self.equalise_loaded_run_config(
            results_nx_graphs["run_config"],
            run_config,
        )

        assert_stage_is_completed(
            run_config=run_config,
            stage_index=1,
        )
        return results_nx_graphs

    @typechecked
    def __perform_run_stage_2(
        self,
        results_nx_graphs: Dict,
        run_config: Run_config,
    ) -> None:
        """Performs the run for stage 2 or loads the data from file depending
        on the run configuration.

        Stage two simulates the SNN graphs over time and, if desired,
        exports each timestep of those SNN graphs to a json dictionary.
        """
        # Verify incoming results dict.
        verify_results_nx_graphs(
            results_nx_graphs=results_nx_graphs, run_config=run_config
        )

        if (
            not has_outputted_stage(run_config=run_config, stage_index=2)
            or run_config.recreate_s4
        ):

            # Load results from file.
            nx_graphs_dict = load_json_to_nx_graph_from_file(
                run_config=run_config,
                stage_index=2,
            )
            results_nx_graphs["graphs_dict"] = nx_graphs_dict

            # TODO: Verify the (incoming (and loaded)) graph types are as
            # expected.

            # Run simulation on networkx or lava backend.
            sim_graphs(
                run_config=run_config,
                stage_1_graphs=results_nx_graphs["graphs_dict"],
            )
            output_files_stage_1_and_2(results_nx_graphs, 2)

        assert_stage_is_completed(
            run_config=run_config,
            stage_index=2,
        )

    @typechecked
    def __perform_run_stage_3(
        self,
        results_nx_graphs: Dict,
        run_config: Run_config,
    ) -> None:
        """Performs the run for stage 3, which visualises the behaviour of the
        SNN graphs over time. This behaviour is shown as a sequence of images.

        The behaviour is described with:
        - Green neuron: means a neuron spikes in that timestep.
        - Green synapse: means the input neuron of that synapse spiked at that
        timestep.
        - Red neuron: radiation has damaged/killed the neuron, it won't spike.
        - Red synapse: means the input neuron of that synapse has died and will
        not spike at that timestep.
        - White/transparent neuron: works as expected, yet does not spike at
        that timestep.
        - A circular synapse: a recurrent connection of a neuron into itself.
        """
        if run_config.export_images:
            # Generate output json dicts (and plots) of propagated graphs.
            output_stage_files_3_and_4(results_nx_graphs, 3)

        assert_stage_is_completed(
            run_config=run_config,
            stage_index=3,
        )

        # TODO: assert gif file exists

    @typechecked
    def __perform_run_stage_4(
        self,
        results_nx_graphs: Dict,
        run_config: Run_config,
    ) -> None:
        """Performs the run for stage 4.

        Stage 4 computes the results of the SNN against the
        default/Neumann implementation. Then stores this result in the
        last entry of each graph.
        """
        if set_results(
            run_config,
            results_nx_graphs["graphs_dict"],
        ):
            export_results_to_json(results_nx_graphs, 4)

        assert_stage_is_completed(
            run_config=run_config,
            stage_index=4,
        )

    @typechecked
    def equalise_loaded_run_config(
        self,
        loaded_from_json: Run_config,
        incoming: Run_config,
    ) -> None:
        """Ensures the non-impactfull run config that is loaded from json are
        identical to those of the  incoming run_config."""
        for key, val in incoming.__dict__.items():

            if loaded_from_json.__dict__[key] != val:
                print(
                    f"setting run config[{key}] from "
                    + f"{loaded_from_json.__dict__[key]} to:{val}"
                )
                loaded_from_json.__dict__[key] = val
        if not dicts_are_equal(
            loaded_from_json.__dict__,
            incoming.__dict__,
            without_unique_id=False,
        ):
            pprint(loaded_from_json.__dict__)
            pprint(incoming.__dict__)
            raise AttributeError(
                "Run_config and loaded run_config from json are not equal."
            )
