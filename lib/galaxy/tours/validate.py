import argparse
import sys

import yaml
from pydantic.error_wrappers import ValidationError

from ._impl import (
    get_tour_id_from_path,
    load_tour_from_path,
    tour_paths,
)
from ._schema import TourDetails

DESCRIPTION = "Perform static validation of a tour."


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = _arg_parser().parse_args(argv)
    target = args.target
    validated = True
    for tour_path in tour_paths(target):
        tour_id = get_tour_id_from_path(tour_path)
        message = None
        tour = None
        try:
            tour = load_tour_from_path(tour_path)
        except OSError:
            message = f"Tour '{tour_id}' could not be loaded, error reading file."
        except yaml.error.YAMLError:
            message = f"Tour '{tour_id}' could not be loaded, error within file." " Please check your yaml syntax."
        except TypeError:
            message = (
                f"Tour '{tour_id}' could not be loaded, error within file."
                " Possibly spacing related. Please check your yaml syntax."
            )
        if tour:
            try:
                TourDetails(**tour)
            except ValidationError as e:
                message = f"Validation issue with tour data for '{tour_id}'. [{e}]"
        if message:
            validated = False
            print(message)
        else:
            print(f"Tour {tour_id} statically validated!")
    if not validated:
        raise ValueError("One or more tours failed static validation.")


def _arg_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "target",
        metavar="TARGET",
        nargs="?",
        help="tour or directories of tours to validate",
        default="config/plugins/tours",
    )
    return parser


if __name__ == "__main__":
    main()