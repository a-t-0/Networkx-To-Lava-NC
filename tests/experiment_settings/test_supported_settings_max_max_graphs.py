"""Verifies the Supported_settings object catches invalid max_max_graphs
specifications."""
# pylint: disable=R0801
import copy
import unittest

from src.experiment_settings.Supported_settings import Supported_settings
from src.experiment_settings.verify_supported_settings import (
    verify_configuration_settings,
)
from tests.experiment_settings.test_supported_settings_iteration import (
    adap_sets,
    rad_sets,
    supp_sets,
    with_adaptation_with_radiation,
)


class Test_max_max_graphs_settings(unittest.TestCase):
    """Tests whether the verify_configuration_settings_types function catches
    invalid max_max_graphs settings.."""

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supp_sets = Supported_settings()
        self.valid_max_max_graphs = self.supp_sets.max_max_graphs

        self.invalid_max_max_graphs_value = {
            "max_max_graphs": "invalid value of type string iso list of"
            + " floats",
        }

        self.supp_sets = supp_sets
        self.adap_sets = adap_sets
        self.rad_sets = rad_sets
        self.with_adaptation_with_radiation = with_adaptation_with_radiation

    def test_max_max_graphs_is_none(self):
        """Verifies an error is thrown if configuration settings do not contain
        m."""

        with self.assertRaises(Exception) as context:
            # Configuration Settings of type None throw error.
            verify_configuration_settings(
                self.supp_sets, None, has_unique_id=False
            )

        self.assertEqual(
            "Error, the experiment_config is of type:"
            + f"{type(None)}, yet it was expected to be of"
            + " type dict.",
            str(context.exception),
        )

    def test_catch_invalid_max_max_graphs_type(self):
        """."""

        with self.assertRaises(Exception) as context:
            # max_max_graphs dictionary of type None throws error.
            verify_configuration_settings(
                self.supp_sets, "string_instead_of_dict", has_unique_id=False
            )
        self.assertEqual(
            "Error, the experiment_config is of type:"
            + f'{type("")}, yet it was expected to be of'
            + " type dict.",
            str(context.exception),
        )

    def test_catch_invalid_max_max_graphs_value_type_too_low(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of max_max_graphs in copy.
        config_settings["max_max_graphs"] = -2

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at least "
            + f"{self.supp_sets.min_max_graphs}. "
            + f"Instead, it is:{-2}",
            str(context.exception),
        )

    def test_catch_max_max_graphs_is_smaller_than_min_max_graphs(self):
        """To state the obvious, this also tests whether min_max_graphs is
        larger than max_graph size throws an exception."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of max_max_graphs in copy.
        config_settings["min_max_graphs"] = (
            config_settings["min_max_graphs"] + 1
        )
        config_settings["max_max_graphs"] = (
            config_settings["min_max_graphs"] - 1
        )

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            f'Lower bound:{config_settings["min_max_graphs"]} is larger than'
            f' upper bound:{config_settings["max_max_graphs"]}.',
            str(context.exception),
        )

    def test_catch_invalid_max_max_graphs_value_type_too_high(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of max_max_graphs in copy.
        config_settings["max_max_graphs"] = 50

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, setting expected to be at most "
            + f"{self.supp_sets.max_max_graphs}. Instead, it is:"
            + "50",
            str(context.exception),
        )

    def test_catch_empty_max_max_graphs_value(self):
        """."""
        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Set negative value of max_max_graphs in copy.
        config_settings["max_max_graphs"] = None

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "Error, expected type:<class 'int'>, yet it was:"
            + "<class 'NoneType'>",
            str(context.exception),
        )

    def test_returns_valid_m(self):
        """Verifies a valid max_max_graphs is returned."""
        returned_dict = verify_configuration_settings(
            self.supp_sets,
            self.with_adaptation_with_radiation,
            has_unique_id=False,
        )
        self.assertIsInstance(returned_dict, dict)

    def test_empty_max_max_graphs(self):
        """Verifies an exception is thrown if an empty max_max_graphs dict is
        thrown."""

        # Create deepcopy of configuration settings.
        config_settings = copy.deepcopy(self.with_adaptation_with_radiation)
        # Remove key and value of m.

        config_settings.pop("max_max_graphs")

        with self.assertRaises(Exception) as context:
            verify_configuration_settings(
                self.supp_sets, config_settings, has_unique_id=False
            )

        self.assertEqual(
            "'max_max_graphs'",
            str(context.exception),
        )