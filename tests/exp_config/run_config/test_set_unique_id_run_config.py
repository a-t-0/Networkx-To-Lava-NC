"""Tests whether the run_config gets the same unique_id at all times if its
content is the same, and that it gets different unique ids for different
run_config settings."""
# pylint: disable=R0801
import copy
import unittest
from typing import Dict, List

from typeguard import typechecked

from snncompare.exp_config.custom_setts.run_configs.algo_test import (
    long_exp_config_for_mdsa_testing,
)
from snncompare.exp_config.run_config import Run_config
from snncompare.exp_config.Supported_experiment_settings import (
    Supported_experiment_settings,
)
from snncompare.exp_config.verify_experiment_settings import (
    verify_experiment_config,
)
from snncompare.Experiment_runner import experiment_config_to_run_configs
from snncompare.src.snncompare.exp_config import Exp_config
from tests.exp_config.exp_config.test_set_unique_id_exp_config import (
    get_config_one,
)


class Test_setting_unique_id_run_config(unittest.TestCase):
    """Tests whether the run_config gets the same unique_id at all times if its
    content is the same, and that it gets different unique ids for different
    run_config settings."""

    # Initialize test object
    @typechecked
    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        # Generate default experiment config.
        self.exp_config: Exp_config = get_config_one()

        self.exp_config.show_snns = False
        self.exp_config.export_images = False
        verify_experiment_config(
            Supported_experiment_settings(),
            self.exp_config,
            has_unique_id=False,
            allow_optional=True,
        )

    @typechecked
    def test_unique_id_is_consistent_over_multiple_runs(self) -> None:
        """Verifies the same run config gets the same unique_id."""

        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(self.exp_config)

        # Generate run configurations.
        run_configs: List[Run_config] = experiment_config_to_run_configs(
            exp_config
        )
        self.assertGreaterEqual(len(run_configs), 2)

        no_ids = copy.deepcopy(run_configs)
        for run_config in no_ids:
            run_config.pop("unique_id")

        # Verify the run configs are all different, (exclude the unique_id from
        # the comparison.)
        for row, row_run_config in enumerate(run_configs):
            for col, col_run_config in enumerate(copy.deepcopy(run_configs)):
                if row == col:
                    self.assertTrue(row_run_config == col_run_config)
                else:
                    self.assertFalse(row_run_config == col_run_config)

        # Verify the run configs are all different, (exclude the unique_id from
        # the comparison.)
        for index, run_config in enumerate(run_configs):
            if index == 0:
                self.assertEqual(
                    run_config.unique_id,
                    "8583218e3da8df30a7a9a72a0d4712e2d774b95ba042be"
                    + "75ebde042792397bde",
                )
            if index == 1:
                self.assertEqual(
                    run_config.unique_id,
                    "f155c0e35222e9f405c2a436d88970d899faa116e4557ae2f"
                    + "daf3e901c3a6842",
                )

    @typechecked
    def test_same_run_config_same_unique_id(self) -> None:
        """Verifies the same run config gets the same unique_id."""

        long_mdsa_testing: Dict = long_exp_config_for_mdsa_testing()
        long_mdsa_testing["show_snns"] = False
        long_mdsa_testing["export_images"] = False

        # Create deepcopy of configuration settings.
        exp_config = copy.deepcopy(long_mdsa_testing)

        # Generate run configurations.
        run_configs: List[Run_config] = experiment_config_to_run_configs(
            exp_config
        )
        self.assertGreaterEqual(len(run_configs), 2)

        no_ids = copy.deepcopy(run_configs)
        for run_config in no_ids:
            run_config.pop("unique_id")

        # Verify the run configs are all different, (exclude the unique_id from
        # the comparison.)
        for row, row_run_config in enumerate(run_configs):
            for col, col_run_config in enumerate(copy.deepcopy(run_configs)):
                if row == col:
                    self.assertTrue(row_run_config == col_run_config)
                else:
                    self.assertFalse(row_run_config == col_run_config)