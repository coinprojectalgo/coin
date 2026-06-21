
from __future__ import annotations

import argparse
from pathlib import Path

from coin_abm import (
    run_one_simulation,
    run_paper_experiments,
    save_summary_figure,
)


# ------------------------------------------------------------
# Interactive prompts
# ------------------------------------------------------------

def _prompt_float(label: str, default: float) -> float:
    raw = input(f"{label} [{default}]: ").strip()
    return float(raw) if raw else default


def _prompt_int(label: str, default: int) -> int:
    raw = input(f"{label} [{default}]: ").strip()
    return int(raw) if raw else default


def _prompt_bool(label: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    raw = input(f"{label} ({suffix}): ").strip().lower()

    if not raw:
        return default

    return raw in {"y", "yes", "true", "1"}


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="Counterinsurgency Agent-Based Model"
    )

    sub = parser.add_subparsers(dest="mode")

    # Single simulation mode
    sim = sub.add_parser(
        "simulate",
        help="Run one simulation"
    )

    sim.add_argument("--effectiveness", type=float)
    sim.add_argument("--accuracy", type=float)

    sim.add_argument("--p-gr", dest="p_gr", type=float)
    sim.add_argument("--p-ir", dest="p_ir", type=float)
    sim.add_argument("--p-iewr", dest="p_iewr", type=float)

    sim.add_argument("--soldier-recruit-n", type=int)
    sim.add_argument("--soldier-anger-delta", type=float)

    sim.add_argument("--insurgent-recruit-n", type=int)
    sim.add_argument("--insurgent-anger-delta", type=float)

    sim.add_argument("--seed", type=int)
    sim.add_argument("--max-ticks", type=int)

    sim.add_argument("--animate", action="store_true")
    sim.add_argument("--interval-ms", type=int)

    sim.add_argument(
        "--output",
        default="coin_summary.png"
    )

    # Paper mode
    paper = sub.add_parser(
        "paper",
        help="Run paper experiments"
    )

    paper.add_argument(
        "--output-dir",
        default="results"
    )

    paper.add_argument(
        "--seed",
        type=int,
        default=1
    )

    return parser


# ------------------------------------------------------------
# Interactive parameter collection
# ------------------------------------------------------------

def interactive_parameters() -> dict:

    print(
        "\nEnter simulation parameters "
        "(press Enter for defaults)\n"
    )

    # Restrict to values used in paper
    soldier_n = _prompt_int(
        "Number of civilians recruitable by soldier (1,5,9)",
        5
    )

    insurgent_n = _prompt_int(
        "Number of civilians recruitable by insurgent (1,5,9)",
        5
    )

    return {
        "effectiveness": _prompt_float(
            "Effectiveness",
            0.5
        ),

        "accuracy": _prompt_float(
            "Accuracy",
            0.5
        ),

        "p_gr": _prompt_float(
            "P_GR (probability soldier recruits)",
            0.5
        ),

        "p_ir": _prompt_float(
            "P_IR (probability insurgent recruits)",
            0.5
        ),

        "p_iewr": _prompt_float(
            "P_IEWR (insurgent exposed while recruiting)",
            0.5
        ),

        "soldier_recruit_n": soldier_n,

        "soldier_anger_delta": _prompt_float(
            "Soldier anger change",
            -0.15
        ),

        "insurgent_recruit_n": insurgent_n,

        "insurgent_anger_delta": _prompt_float(
            "Insurgent anger change",
            0.15
        ),

        "seed": _prompt_int(
            "Random seed",
            1
        ),

        "max_ticks": _prompt_int(
            "Maximum ticks",
            5000
        ),

        "animate": _prompt_bool(
            "Animate simulation",
            False
        ),

        "interval_ms": _prompt_int(
            "Animation interval (ms)",
            60
        ),
    }


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> None:

    parser = build_parser()
    args = parser.parse_args()

    # ------------------------------------
    # Paper batch mode
    # ------------------------------------

    if args.mode == "paper":

        run_paper_experiments(
            output_dir=args.output_dir,
            seed=args.seed
        )

        return

    # ------------------------------------
    # CLI simulation mode
    # ------------------------------------

    if args.mode == "simulate":

        params = {
            "effectiveness": args.effectiveness,
            "accuracy": args.accuracy,
            "p_gr": args.p_gr,
            "p_ir": args.p_ir,
            "p_iewr": args.p_iewr,
            "soldier_recruit_n": args.soldier_recruit_n,
            "soldier_anger_delta": args.soldier_anger_delta,
            "insurgent_recruit_n": args.insurgent_recruit_n,
            "insurgent_anger_delta": args.insurgent_anger_delta,
            "seed": args.seed,
            "max_ticks": args.max_ticks,
            "animate": args.animate,
            "interval_ms": args.interval_ms,
        }

        # If user omitted parameters,
        # switch to interactive mode.
        if params["effectiveness"] is None:
            params = interactive_parameters()

        model = run_one_simulation(**params)

        if not params["animate"]:

            output_path = Path(
                args.output
                if args.output
                else "coin_summary.png"
            )

            save_summary_figure(
                model,
                output_path
            )

            print(
                f"\nSaved figure to:\n"
                f"{output_path.resolve()}"
            )

            print(
                f"Termination: "
                f"{model.termination_reason}"
            )

            print(
                f"Ticks simulated: "
                f"{model.tick_count}"
            )

        return

    # ------------------------------------
    # Default interactive mode
    # ------------------------------------

    params = interactive_parameters()

    model = run_one_simulation(**params)

    if not params["animate"]:

        output_path = Path(
            "coin_summary.png"
        )

        save_summary_figure(
            model,
            output_path
        )

        print(
            f"\nSaved figure to:\n"
            f"{output_path.resolve()}"
        )

        print(
            f"Termination: "
            f"{model.termination_reason}"
        )

        print(
            f"Ticks simulated: "
            f"{model.tick_count}"
        )


if __name__ == "__main__":
    main()
