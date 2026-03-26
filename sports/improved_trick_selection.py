"""
Improved Trick Selection System
================================
Fixes the difficulty explosion issues in the graph-based trick generator.

Key improvements:
1. Inverse weighting - easier tricks more likely within difficulty bands
2. Diminishing returns for switch-up difficulty
3. Non-overlapping difficulty bands
4. Target-based total difficulty constraints
"""

import pandas as pd
import numpy as np


def select_weighted_trick_improved(
    combination_df,
    DIFFICULTY=None,
    random_state=None,
    invert_weights=True,
    favor_easier=0.7,
):
    """
    Select a trick with improved weighting that doesn't favor hardest tricks.

    Parameters
    ----------
    combination_df : pd.DataFrame
        Input dataframe with columns: family, path_weight_sum, output_trick_*
    DIFFICULTY : str or None
        One of: "beginner", "intermediate", "advanced", "pro", "insane"
    random_state : int or None
        Random seed for reproducibility
    invert_weights : bool
        If True, easier tricks are more likely to be selected
    favor_easier : float (0-1)
        How much to favor easier tricks.
        0 = uniform, 1 = strongly favor easiest

    Returns
    -------
    dict with keys: family, path_weight_sum, output_trick_base, output_trick_full
    """
    df_local = combination_df.copy()

    # Ensure output columns exist
    if "output_trick_base" not in df_local.columns:
        df_local["output_trick_base"] = (
            df_local["trick"] if "trick" in df_local.columns else None
        )
    if "output_trick_full" not in df_local.columns:
        df_local["output_trick_full"] = (
            df_local["trick"] if "trick" in df_local.columns else None
        )

    required = ["family", "path_weight_sum", "output_trick_base", "output_trick_full"]
    missing = [c for c in required if c not in df_local.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    work = df_local.dropna(subset=required).copy()
    work = work[work["path_weight_sum"] > 0].copy()

    if work.empty:
        raise ValueError("No valid rows available for weighted selection.")

    # Percentile rank for difficulty slicing
    work["_pct"] = work["path_weight_sum"].rank(method="average", pct=True)

    # NON-OVERLAPPING difficulty bands (fixed!)
    difficulty_bands = {
        "beginner": (0.00, 0.25),  # Bottom 25%
        "intermediate": (0.25, 0.50),  # 25-50%
        "advanced": (0.50, 0.75),  # 50-75%
        "pro": (0.75, 0.90),  # 75-90%
        "insane": (0.90, 1.00),  # Top 10%
    }

    # Filter by difficulty band
    if DIFFICULTY is None:
        eligible = work
    else:
        key = str(DIFFICULTY).strip().lower()
        if key not in difficulty_bands:
            raise ValueError(
                f"DIFFICULTY must be one of: {list(difficulty_bands.keys())} or None"
            )

        lo, hi = difficulty_bands[key]
        if lo == 0:
            eligible = work[(work["_pct"] >= lo) & (work["_pct"] <= hi)]
        else:
            eligible = work[(work["_pct"] > lo) & (work["_pct"] <= hi)]

        if eligible.empty:
            eligible = work

    # IMPROVED WEIGHTING - favor easier tricks within the band
    if invert_weights:
        max_weight = eligible["path_weight_sum"].max()
        min_weight = eligible["path_weight_sum"].min()
        weight_range = max_weight - min_weight

        if weight_range > 0:
            # Normalize to 0-1 (0=easiest, 1=hardest)
            normalized = (eligible["path_weight_sum"] - min_weight) / weight_range

            # Invert and apply favor_easier exponent
            # Higher favor_easier = stronger preference for easy tricks
            sampling_weights = (1 - normalized) ** (1 / (1 - favor_easier + 0.01))
        else:
            # All same difficulty - uniform weights
            sampling_weights = np.ones(len(eligible))
    else:
        # Old behavior (not recommended)
        sampling_weights = eligible["path_weight_sum"]

    # Sample with improved weights
    chosen = eligible.sample(
        n=1, weights=sampling_weights, random_state=random_state
    ).iloc[0]

    return {
        "family": chosen["family"],
        "path_weight_sum": float(chosen["path_weight_sum"]),
        "output_trick_base": chosen["output_trick_base"],
        "output_trick_full": chosen["output_trick_full"],
    }


def calculate_combo_difficulty(trick_difficulties, method="diminishing"):
    """
    Calculate total combo difficulty with realistic scaling.

    Parameters
    ----------
    trick_difficulties : list of float
        Individual trick difficulties (path_weight_sum values)
    method : str
        "additive" - simple sum (old behavior, too high)
        "diminishing" - each switch-up contributes less (recommended)
        "average" - mean difficulty (too low)
        "weighted_avg" - weighted by position (good balance)

    Returns
    -------
    float : total combo difficulty
    """
    if not trick_difficulties:
        return 0.0

    if method == "additive":
        # Old method - too harsh
        return sum(trick_difficulties)

    elif method == "diminishing":
        # Each subsequent trick contributes less
        # Weights: [1.0, 0.6, 0.4, 0.3, 0.2, ...]
        weights = [1.0] + [0.6 / (i**0.5) for i in range(1, len(trick_difficulties))]
        return sum(d * w for d, w in zip(trick_difficulties, weights))

    elif method == "average":
        # Just the mean - often too lenient
        return sum(trick_difficulties) / len(trick_difficulties)

    elif method == "weighted_avg":
        # Start trick matters most, switches matter less
        # Weights: [0.5, 0.25, 0.15, 0.1, ...]
        total_tricks = len(trick_difficulties)
        weights = [0.5] + [0.5 / (2**i) for i in range(1, total_tricks)]
        weights = [w / sum(weights) for w in weights]  # Normalize

        base_avg = sum(trick_difficulties) / total_tricks
        weighted_avg = sum(d * w for d, w in zip(trick_difficulties, weights))

        # Scale up slightly for having multiple tricks
        combo_factor = 1 + (0.15 * (total_tricks - 1))
        return weighted_avg * combo_factor

    else:
        raise ValueError(f"Unknown method: {method}")


def generate_combo_with_target_difficulty(
    start_trick_table,
    switch_trick_tables,  # List of switch-up tables for each position
    target_difficulty_band="advanced",
    n_switch_ups=3,
    difficulty_method="diminishing",
    max_attempts=100,
    random_state=None,
):
    """
    Generate a full combo targeting a specific total difficulty range.

    This ensures the FINAL combo difficulty matches the requested level,
    not just each individual trick.

    Parameters
    ----------
    start_trick_table : pd.DataFrame
        Formatted table of starting tricks
    switch_trick_tables : list of pd.DataFrame
        List of switch-up tables (one per switch position)
    target_difficulty_band : str
        Desired total difficulty: "beginner", "intermediate", "advanced", "pro", "insane"
    n_switch_ups : int
        Number of switch-ups to include
    difficulty_method : str
        How to calculate total difficulty (see calculate_combo_difficulty)
    max_attempts : int
        Maximum tries to hit target difficulty
    random_state : int or None
        Random seed

    Returns
    -------
    dict with keys:
        - tricks : list of dicts (one per trick in combo)
        - total_difficulty : float
        - individual_difficulties : list of floats
        - difficulty_band : str
    """
    # Target difficulty ranges (these are for TOTAL combo difficulty)
    target_ranges = {
        "beginner": (1.0, 2.0),  # One basic trick
        "intermediate": (2.0, 3.5),  # One harder trick or simple combo
        "advanced": (3.5, 5.5),  # Multiple tricks, some technical
        "pro": (5.5, 7.5),  # Complex combo with spins
        "insane": (7.5, 12.0),  # Multiple hard tricks + switch-ups
    }

    if target_difficulty_band not in target_ranges:
        raise ValueError(f"Unknown difficulty band: {target_difficulty_band}")

    min_target, max_target = target_ranges[target_difficulty_band]

    if random_state is not None:
        np.random.seed(random_state)

    best_combo = None
    best_diff_from_target = float("inf")

    for attempt in range(max_attempts):
        tricks = []
        difficulties = []

        # Select start trick from a wider percentile range
        # Allow any trick, but weight selection appropriately
        start_trick = select_weighted_trick_improved(
            start_trick_table,
            DIFFICULTY=None,  # Don't restrict by band yet
            random_state=None,
            invert_weights=True,
            favor_easier=0.6,  # Moderate preference for easier starts
        )
        tricks.append(start_trick)
        difficulties.append(start_trick["path_weight_sum"])

        # Add switch-ups
        for i in range(min(n_switch_ups, len(switch_trick_tables))):
            switch_trick = select_weighted_trick_improved(
                switch_trick_tables[i],
                DIFFICULTY=None,
                random_state=None,
                invert_weights=True,
                favor_easier=0.5,  # Balanced selection
            )
            tricks.append(switch_trick)
            difficulties.append(switch_trick["path_weight_sum"])

        # Calculate total difficulty
        total_diff = calculate_combo_difficulty(difficulties, method=difficulty_method)

        # Check if within target range
        diff_from_target = 0
        if total_diff < min_target:
            diff_from_target = min_target - total_diff
        elif total_diff > max_target:
            diff_from_target = total_diff - max_target

        # Keep if best so far
        if diff_from_target < best_diff_from_target:
            best_diff_from_target = diff_from_target
            best_combo = {
                "tricks": tricks,
                "total_difficulty": total_diff,
                "individual_difficulties": difficulties,
                "difficulty_band": target_difficulty_band,
                "in_target_range": diff_from_target == 0,
            }

        # Stop if we hit the target
        if diff_from_target == 0:
            break

    return best_combo


# Example usage and testing
if __name__ == "__main__":
    print("Improved Trick Selection System Loaded!")
    print("\nKey Features:")
    print("✓ Inverse weighting - easier tricks more likely within bands")
    print("✓ Non-overlapping difficulty bands")
    print("✓ Diminishing returns for switch-up difficulty")
    print("✓ Target-based combo generation")
    print("\nUse select_weighted_trick_improved() instead of select_weighted_trick()")
