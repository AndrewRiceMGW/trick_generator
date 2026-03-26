"""
Graph-based Aggressive Inline Trick Generator - API Module
Refactored version of graph_generation.py for programmatic use
"""

import pandas as pd
import networkx as nx
import numpy as np
import os


# Load trick data
df = pd.read_json("sports/tricktable.json")


def filter_tricks_by_level(tricks_df, difficulty_level):
    """
    Filter tricks based on difficulty level and level limit column.

    Rules:
    - If level_limit is blank/None: all levels can use
    - If level_limit is 'intermediate': intermediate, advanced, pro, insane can use
    - If level_limit is 'advanced': advanced, pro, insane can use
    - Beginners cannot use negative tricks
    """
    # Define level hierarchy
    level_hierarchy = {
        "beginner": 0,
        "intermediate": 1,
        "advanced": 2,
        "pro": 3,
        "insane": 4,
    }

    if difficulty_level not in level_hierarchy:
        return tricks_df  # No filtering if invalid level

    user_level_rank = level_hierarchy[difficulty_level.lower()]

    # Filter based on level limit
    def can_use_trick(row):
        level_limit = row.get("level limit", None)

        # If level limit is empty/None, everyone can use it
        if pd.isna(level_limit) or str(level_limit).strip() == "":
            return True

        # Get the required level rank
        required_level = str(level_limit).strip().lower()
        if required_level not in level_hierarchy:
            return True  # If invalid level limit, allow it

        required_rank = level_hierarchy[required_level]

        # User must be at or above required level
        return user_level_rank >= required_rank

    filtered_df = tricks_df[tricks_df.apply(can_use_trick, axis=1)].copy()

    return filtered_df


def starting_trick_graph(tricks_df, difficulty_level=None):
    """Generate the starting trick graph"""
    G = nx.DiGraph()
    node_labels = {}

    kind_col = "soul or hblock"
    name_col = "trick name"
    diff_col = "normalised difficulty"

    def add_node(node_id, label, layer, weight=None):
        attrs = {"subset": layer}
        if weight is not None:
            attrs["weight"] = float(weight)
        G.add_node(node_id, **attrs)
        node_labels[node_id] = label

    def connect_all(sources, targets):
        for s in sources:
            for t in targets:
                G.add_edge(s, t)

    # Apply level filtering if difficulty level provided
    if difficulty_level:
        tricks_df = filter_tricks_by_level(tricks_df, difficulty_level)

    # Filter trick lists from df
    hblock_df = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("hblock"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )
    soul_df = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("soul"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )

    # Main path
    add_node("approach", "approach", 0)
    add_node("fakie", "fakie", 1, 0.3)
    add_node("regular_approach", "regular", 1, 0.1)

    add_node("switch", "switch", 2, 0.7)
    add_node("natural", "natural", 2, 0.1)

    add_node("hblock", "hblock", 3)
    add_node("soul", "soul", 3)

    G.add_edge("approach", "fakie")
    G.add_edge("approach", "regular_approach")
    connect_all(["fakie", "regular_approach"], ["switch", "natural"])
    connect_all(["switch", "natural"], ["hblock", "soul"])

    # Hblock branch
    add_node("hblock_spin_0", "0", 4, 0.3)
    add_node("hblock_spin_270", "270", 4, 1.35)
    add_node("hblock_spin_450", "450", 4, 3.0)
    connect_all(["hblock"], ["hblock_spin_0", "hblock_spin_270", "hblock_spin_450"])

    add_node("hblock_inspin", "inspin", 5, 0.3)
    add_node("hblock_outspin", "outspin", 5, 0.4)
    connect_all(
        ["hblock_spin_270", "hblock_spin_450"], ["hblock_inspin", "hblock_outspin"]
    )

    hblock_trick_nodes = []
    for i, row in hblock_df.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"hblock::{trick_name}::{i}"
        add_node(node_id, trick_name, 6, row[diff_col])
        hblock_trick_nodes.append(node_id)

    connect_all(["hblock_spin_0"], hblock_trick_nodes)
    connect_all(["hblock_inspin", "hblock_outspin"], hblock_trick_nodes)

    # Soul branch
    # Block beginners from using negatives
    soul_modes = []
    if difficulty_level and difficulty_level.lower() == "beginner":
        # Beginner: only regular soul mode
        add_node("soul_regular", "regular", 4, 0.05)
        soul_modes = ["soul_regular"]
    else:
        # All other levels: both negative and regular
        add_node("soul_negative", "negative", 4, 2.15)
        add_node("soul_regular", "regular", 4, 0.05)
        soul_modes = ["soul_negative", "soul_regular"]

    connect_all(["soul"], soul_modes)

    add_node("soul_spin_0", "0", 5, 0.03)
    add_node("soul_spin_180", "180", 5, 0.15)
    add_node("soul_spin_360", "360", 5, 1.6)
    add_node("soul_spin_540", "540", 5, 4.0)
    connect_all(
        soul_modes,
        ["soul_spin_0", "soul_spin_180", "soul_spin_360", "soul_spin_540"],
    )

    add_node("soul_inspin", "inspin", 6, 0.3)
    add_node("soul_outspin", "outspin", 6, 0.4)
    connect_all(
        ["soul_spin_180", "soul_spin_360", "soul_spin_540"],
        ["soul_inspin", "soul_outspin"],
    )

    soul_trick_nodes = []
    for i, row in soul_df.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"soul::{trick_name}::{i}"
        add_node(node_id, trick_name, 7, row[diff_col])
        soul_trick_nodes.append(node_id)

    connect_all(["soul_spin_0"], soul_trick_nodes)
    connect_all(["soul_inspin", "soul_outspin"], soul_trick_nodes)

    return G, node_labels


def create_start_trick_table(G, node_labels):
    """Build table of all valid trick combinations"""
    source = "approach"
    trick_nodes = [n for n in G.nodes if "::" in n and G.out_degree(n) == 0]
    records = []

    for target in trick_nodes:
        for path in nx.all_simple_paths(G, source=source, target=target):
            rec = {
                "approach": None,
                "stance": None,
                "family": None,
                "soul_mode": None,
                "spin": None,
                "spin_dir": None,
                "trick": None,
                "trick_node": target,
                "path_labels": " -> ".join(node_labels.get(n, n) for n in path),
            }

            for n in path:
                if n in ("fakie", "regular_approach"):
                    rec["approach"] = node_labels.get(n, n)
                elif n in ("switch", "natural"):
                    rec["stance"] = node_labels.get(n, n)
                elif n in ("hblock", "soul"):
                    rec["family"] = node_labels.get(n, n)
                elif n in ("soul_negative", "soul_regular"):
                    rec["soul_mode"] = node_labels.get(n, n)
                elif n.startswith("hblock_spin_") or n.startswith("soul_spin_"):
                    rec["spin"] = node_labels.get(n, n)
                elif n in (
                    "hblock_inspin",
                    "hblock_outspin",
                    "soul_inspin",
                    "soul_outspin",
                ):
                    rec["spin_dir"] = node_labels.get(n, n)
                elif "::" in n:
                    rec["trick"] = node_labels.get(n, n)

            # Compute path weight
            weights = [
                G.nodes[n].get("weight")
                for n in path
                if G.nodes[n].get("weight") is not None
            ]
            rec["path_weight_sum"] = float(sum(weights)) if weights else 0.0

            wprod = 1.0
            for w in weights:
                wprod *= float(w)
            rec["path_weight_product"] = wprod

            rec["trick_difficulty"] = G.nodes[target].get("weight")
            records.append(rec)

    return pd.DataFrame(records)


def switch_up_graph(tricks_df, n_switch_ups=1, difficulty_level=None):
    """Generate switch-up graph with adjusted weights"""
    G = nx.DiGraph()
    node_labels = {}

    kind_col = "soul or hblock"
    name_col = "trick name"
    diff_col = "normalised difficulty"

    def add_node(node_id, label, layer, weight=None):
        attrs = {"subset": layer}
        if weight is not None:
            attrs["weight"] = float(weight)
        G.add_node(node_id, **attrs)
        node_labels[node_id] = label

    def connect_all(sources, targets):
        for s in sources:
            for t in targets:
                G.add_edge(s, t)

    # Apply level filtering if difficulty level provided
    if difficulty_level:
        tricks_df = filter_tricks_by_level(tricks_df, difficulty_level)

    hblock_df = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("hblock"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )
    soul_df = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("soul"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )

    # Apply switch-up penalty
    penalty_multiplier = min(n_switch_ups * 0.1, 0.4)

    add_node("approach", "approach", 0)
    add_node("hblock", "hblock", 1)
    add_node("soul", "soul", 1)

    G.add_edge("approach", "hblock")
    G.add_edge("approach", "soul")

    # Hblock branch with penalties
    add_node("hblock::spin::0", "0", 2, 0.0)
    add_node("hblock::spin::270", "270", 2, 1.35 + penalty_multiplier)
    add_node("hblock::spin::450", "450", 2, 3.0 + (penalty_multiplier * 2.5))
    connect_all(
        ["hblock"], ["hblock::spin::0", "hblock::spin::270", "hblock::spin::450"]
    )

    add_node("hblock::inspin", "inspin", 3, 0.3)
    add_node("hblock::outspin", "outspin", 3, 0.4)
    connect_all(
        ["hblock::spin::270", "hblock::spin::450"],
        ["hblock::inspin", "hblock::outspin"],
    )

    hblock_trick_nodes = []
    for i, row in hblock_df.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"hblock::{trick_name}::{i}"
        add_node(node_id, trick_name, 4, row[diff_col])
        hblock_trick_nodes.append(node_id)

    connect_all(["hblock::spin::0"], hblock_trick_nodes)
    connect_all(["hblock::inspin", "hblock::outspin"], hblock_trick_nodes)

    # Soul branch with penalties
    # Block beginners from using negatives
    soul_modes = []
    if difficulty_level and difficulty_level.lower() == "beginner":
        # Beginner: only regular soul mode
        add_node("soul::regular", "regular", 2, 0.05)
        soul_modes = ["soul::regular"]
    else:
        # All other levels: both negative and regular
        add_node("soul::negative", "negative", 2, 4.15)
        add_node("soul::regular", "regular", 2, 0.05)
        soul_modes = ["soul::negative", "soul::regular"]

    connect_all(["soul"], soul_modes)

    add_node("soul::spin::0", "0", 3, 0.0)
    add_node("soul::spin::180", "180", 3, 0.15 + (penalty_multiplier * 0.3))
    add_node("soul::spin::360", "360", 3, 2.5 + (penalty_multiplier * 0.8))
    add_node("soul::spin::540", "540", 3, 6.2 + (penalty_multiplier * 3.0))
    connect_all(
        soul_modes,
        ["soul::spin::0", "soul::spin::180", "soul::spin::360", "soul::spin::540"],
    )

    add_node("soul::inspin", "inspin", 4, 0.3)
    add_node("soul::outspin", "outspin", 4, 0.4)
    connect_all(
        ["soul::spin::180", "soul::spin::360", "soul::spin::540"],
        ["soul::inspin", "soul::outspin"],
    )

    soul_trick_nodes = []
    for i, row in soul_df.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"soul::{trick_name}::{i}"
        add_node(node_id, trick_name, 5, row[diff_col])
        soul_trick_nodes.append(node_id)

    connect_all(["soul::spin::0"], soul_trick_nodes)
    connect_all(["soul::inspin", "soul::outspin"], soul_trick_nodes)

    return G, node_labels


def create_switch_trick_table(G, node_labels):
    """Create trick table for switch-ups"""
    source = "approach"
    trick_nodes = [n for n in G.nodes if "::" in n and G.out_degree(n) == 0]
    records = []

    for target in trick_nodes:
        for path in nx.all_simple_paths(G, source=source, target=target):
            rec = {
                "family": None,
                "soul_mode": None,
                "spin": None,
                "spin_dir": None,
                "trick": None,
                "trick_node": target,
                "path_labels": " -> ".join(node_labels.get(n, n) for n in path),
            }

            for n in path:
                if n in ("hblock", "soul"):
                    rec["family"] = node_labels.get(n, n)
                elif n in ("soul::negative", "soul::regular"):
                    rec["soul_mode"] = node_labels.get(n, n)
                elif "::spin::" in n:
                    label = node_labels.get(n, n)
                    rec["spin"] = label
                elif n in (
                    "hblock::inspin",
                    "hblock::outspin",
                    "soul::inspin",
                    "soul::outspin",
                ):
                    rec["spin_dir"] = node_labels.get(n, n)
                elif "::" in n and G.out_degree(n) == 0:
                    rec["trick"] = node_labels.get(n, n)

            weights = [
                G.nodes[n].get("weight")
                for n in path
                if G.nodes[n].get("weight") is not None
            ]
            rec["path_weight_sum"] = float(sum(weights)) if weights else 0.0

            wprod = 1.0
            for w in weights:
                wprod *= float(w)
            rec["path_weight_product"] = wprod

            rec["trick_difficulty"] = G.nodes[target].get("weight")
            records.append(rec)

    return pd.DataFrame(records)


def adjust_spin_for_switch(switch_trick_table, previous_family):
    """Adjust spin options based on previous trick family"""
    if previous_family == "hblock":
        filtered = switch_trick_table[
            switch_trick_table["spin"].isin(["0", "270", "450"])
        ].copy()
    else:
        filtered = switch_trick_table[
            ~switch_trick_table["spin"].isin(["270", "450"])
        ].copy()
    return filtered


def start_trick_formatting(start_trick_df, start_trick_name, start_trick=False):

    if start_trick == False:
        fakie = "fakie"
        zero = "zero spin"
    else:
        fakie = ""
        zero = ""

    start_trick_df["output_trick_base"] = start_trick_df[
        "trick"
    ]  # default to just the trick name
    start_trick_df["output_trick_full"] = start_trick_df[
        "trick"
    ]  # will build on this with modifiers

    for i in start_trick_df.index:
        row = start_trick_df.loc[i]
        spin_num = pd.to_numeric(row["spin"], errors="coerce")

        if start_trick == False:
            approach = "regular"
        else:
            approach = row["approach"]

        if start_trick_name == None:
            tru_spin = "tru spin"
            ao = "ao"
        elif "tru spin" in start_trick_name:
            tru_spin = f"{row['spin_dir']}"
            ao = f"{row['spin_dir']}"
        elif "ao" in start_trick_name:
            tru_spin = f"{row['spin_dir']}"
            ao = f"{row['spin_dir']}"
        else:
            tru_spin = "tru spin"
            ao = "ao"

        # hblock tricks - regular approach
        if (
            approach == "regular"
            and row["family"] == "hblock"
            and row["spin_dir"] == "inspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{row['spin_dir']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin_dir']} {row['spin']} {row['trick']}"
            )
        elif (
            approach == "regular"
            and row["family"] == "hblock"
            and row["spin_dir"] == "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"tru spin {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"tru spin {row['spin']} {row['trick']}"
            )
        # hblock tricks - fakie approach
        elif (
            approach == "fakie"
            and row["family"] == "hblock"
            and row["spin_dir"] != "inspin"
            and row["spin_dir"] != "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{fakie} {zero} {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = f"{fakie} {zero} {row['trick']}"
        elif (
            approach == "fakie"
            and row["family"] == "hblock"
            and row["spin_dir"] == "inspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{row['spin_dir']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{fakie}{row['spin_dir']} {row['spin']} {row['trick']}"
            )
        elif (
            approach == "fakie"
            and row["family"] == "hblock"
            and row["spin_dir"] == "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"tru spin {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"{fakie} tru spin {row['spin']} {row['trick']}"
            )
        # soul tricks - fakie approach zero spin
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (0, 360)
            and row["spin_dir"] == "inspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{ao} {row['soul_mode']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{ao} {row['spin']} {row['soul_mode']}  {row['trick']}"
            )
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (0, 360)
            and row["spin_dir"] != "inspin"
            and row["spin_dir"] != "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"zero {ao} {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = f"zero {ao} {row['trick']}"
        # soul tricks - fakie approach spin
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (0, 360)
            and row["spin_dir"] != "inspin"
            and row["spin_dir"] != "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{ao} {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = f"{fakie}{ao} {row['trick']}"
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (180, 540)
            and row["spin_dir"] == "inspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{tru_spin} {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"{fakie} {tru_spin} {row['spin']} {row['trick']}"
            )
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (180, 540)
            and row["spin_dir"] == "outspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{tru_spin} {row['soul_mode']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{fakie} {tru_spin}  {row['spin']} {row['soul_mode']} {row['trick']}"
            )
        elif (
            approach == "fakie"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (0, 360)
            and row["spin_dir"] == "inspin"
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{ao} {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"{fakie} {ao} {row['spin']} {row['trick']}"
            )
            # forward approach soul negative
        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (180, 540)
            and row["spin_dir"] in ("inspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{ao}  {row['soul_mode']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {ao} {row['soul_mode']} {row['trick']}"
            )
        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (180, 540)
            and row["spin_dir"] in ("outspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{tru_spin} {row['soul_mode']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {tru_spin} {row['soul_mode']} {row['trick']}"
            )
        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "negative"
            and spin_num in (0, 360)
            and row["spin_dir"] in ("inspin", "outspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{row['spin_dir']} {row['soul_mode']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {row['spin_dir']} {row['soul_mode']} {row['trick']}"
            )
            # forward approach soul regular
        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (180, 540)
            and row["spin_dir"] in ("inspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{ao}  {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {ao} {row['trick']}"
            )
        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (180, 540)
            and row["spin_dir"] in ("outspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = f"{tru_spin}  {row['trick']}"
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {tru_spin}  {row['trick']}"
            )

        elif (
            approach == "regular"
            and row["family"] == "soul"
            and row["soul_mode"] == "regular"
            and spin_num in (0, 360)
            and row["spin_dir"] in ("inspin", "outspin")
        ):
            start_trick_df.at[i, "output_trick_base"] = (
                f"{row['spin_dir']} {row['trick']}"
            )
            start_trick_df.at[i, "output_trick_full"] = (
                f"{row['spin']} {row['spin_dir']} {row['trick']}"
            )

    return start_trick_df


def select_weighted_trick(trick_table, DIFFICULTY=None, random_state=None, n_switch=0):
    """Select a trick using weighted sample pool approach"""

    # Difficulty bands (wider, overlapping)
    difficulty_bands = {
        "beginner": (0.00, 0.50),  # Bottom 50% - lots of variety
        "intermediate": (0.00, 0.70),  # 35-70% - overlaps with beginner
        "advanced": (0.00, 0.85),  # 55-85% - overlaps lower for variety
        "pro": (0.00, 0.95),  # 65-95% - WIDER to include 360° mix
        "insane": (0.00, 1.00),  # Top 10%
    }

    # Get eligible tricks based on difficulty
    if DIFFICULTY and DIFFICULTY.lower() in difficulty_bands:
        key = DIFFICULTY.lower()
        min_pct, max_pct = difficulty_bands[key]

        min_diff = trick_table["path_weight_sum"].quantile(min_pct)
        max_diff = trick_table["path_weight_sum"].quantile(max_pct)

        eligible = trick_table[
            (trick_table["path_weight_sum"] >= min_diff)
            & (trick_table["path_weight_sum"] <= max_diff)
        ].copy()

        if eligible.empty:
            eligible = trick_table.copy()
    else:
        eligible = trick_table.copy()

    # Weighted sample pool approach
    difficulty_multipliers = {
        "beginner": 3.9 * n_switch,  # Very strong preference for easiest tricks
        "intermediate": 3.4 * n_switch,
        "advanced": 1.85 * n_switch,  # EXTREME - strongly favor easier end of band
        "pro": 1.566 * n_switch,  # ULTRA EXTREME - max 1 mega spin
        "insane": 0.01 * n_switch,  # Less aggressive - allow harder tricks
    }

    multiplier = difficulty_multipliers.get(key, 10.0) if DIFFICULTY else 8.0

    # Calculate inverse weights
    # Handle zero or very small weights
    path_weights = eligible["path_weight_sum"].copy()
    # print(f"Path weights before inversion 1: {path_weights}")
    path_weights = path_weights.replace(0, 0.001)  # Replace zeros with small value
    # print(f"Path weights before inversion 2: {path_weights}")
    inverse_weights = 1.0 / (path_weights**multiplier)

    # Check for NaN or inf values
    if inverse_weights.isna().any() or np.isinf(inverse_weights).any():
        # Fallback: use uniform weights
        inverse_weights = np.ones(len(eligible))

    inverse_weights = inverse_weights / inverse_weights.sum()

    # Ensure we have valid probabilities
    if np.isnan(inverse_weights).any() or len(eligible) == 0:
        raise ValueError(f"No valid tricks found for difficulty level: {DIFFICULTY}")

    # Create sample pool of 3000 tricks
    sample_size = min(3000, len(eligible) * 100)  # Adjust pool size for small datasets
    sample_pool_indices = np.random.choice(
        eligible.index, size=sample_size, replace=True, p=inverse_weights
    )

    # Randomly pick from pre-weighted pool
    chosen_idx = np.random.choice(sample_pool_indices)
    chosen = eligible.loc[chosen_idx]

    return {
        "family": chosen["family"],
        "spin": chosen["spin"],
        "path_weight_sum": float(chosen["path_weight_sum"]),
        "output_trick_base": chosen["output_trick_base"],
        "output_trick_full": chosen["output_trick_full"],
    }


def generate_trick_combo(difficulty_level="advanced", n_switch_ups=2):
    """
    Main function to generate a trick combo

    Args:
        difficulty_level: "beginner", "intermediate", "advanced", "pro", or "insane"
        n_switch_ups: Number of switch-ups (0-3)

    Returns:
        Dictionary with trick data:
        {
            "name": "Full combo name",
            "difficulty": 4.5,
            "components": [
                {"trick": "Negative Mizou", "difficulty": 1.75},
                {"trick": "360 Fishbrain", "difficulty": 2.15}
            ],
            "totalDifficulty": 4.5,
            "individualDifficulties": [1.75, 2.15]
        }
    """

    # Generate starting trick
    start_tricks, start_trick_labels = starting_trick_graph(
        df, difficulty_level=difficulty_level
    )
    start_trick_table = create_start_trick_table(start_tricks, start_trick_labels)
    print(
        f"Start trick table:\n{start_trick_table.path_weight_sum.min()} - {start_trick_table.path_weight_sum.max()}"
    )
    start_trick_table_formatted = start_trick_formatting(
        start_trick_table, None, start_trick=True
    )

    selected_start_trick = select_weighted_trick(
        start_trick_table_formatted,
        DIFFICULTY=difficulty_level,
        random_state=None,
        n_switch=n_switch_ups,
    )

    # Initialize result
    total_difficulty = selected_start_trick["path_weight_sum"]
    components = [
        {
            "trick": selected_start_trick["output_trick_full"],
            "difficulty": round(selected_start_trick["path_weight_sum"], 2),
        }
    ]
    individual_difficulties = [selected_start_trick["path_weight_sum"]]
    full_combo_name = selected_start_trick["output_trick_full"]

    # Generate switch-ups
    selected_switch_trick_old = selected_start_trick

    for i in range(n_switch_ups):
        switch_graph, switch_labels = switch_up_graph(
            df, n_switch_ups=i + 1, difficulty_level=difficulty_level
        )
        switch_trick_table = create_switch_trick_table(switch_graph, switch_labels)
        switch_trick_table = adjust_spin_for_switch(
            switch_trick_table, selected_switch_trick_old["family"]
        )
        switch_trick_table_formatted = start_trick_formatting(
            switch_trick_table,
            selected_start_trick["output_trick_full"],
            start_trick=False,
        )

        selected_switch_trick = select_weighted_trick(
            switch_trick_table_formatted,
            DIFFICULTY=difficulty_level,
            random_state=None,
            n_switch=n_switch_ups / 2,
        )

        # Prevent duplicates with 0 spin
        max_attempts = 10
        attempts = 0
        while (
            attempts < max_attempts
            and selected_switch_trick["output_trick_base"]
            == selected_switch_trick_old["output_trick_base"]
            and selected_switch_trick["spin"] == "0"
        ):
            selected_switch_trick = select_weighted_trick(
                switch_trick_table_formatted,
                DIFFICULTY=difficulty_level,
                random_state=None,
                n_switch=n_switch_ups / 2,
            )
            attempts += 1

        total_difficulty += selected_switch_trick["path_weight_sum"]
        components.append(
            {
                "trick": selected_switch_trick["output_trick_full"],
                "difficulty": round(selected_switch_trick["path_weight_sum"], 2),
            }
        )
        individual_difficulties.append(selected_switch_trick["path_weight_sum"])
        full_combo_name += " to " + selected_switch_trick["output_trick_full"]

        selected_switch_trick_old = selected_switch_trick

    # Calculate diminishing returns difficulty
    if len(individual_difficulties) > 1:
        print(f"Individual difficulties: {individual_difficulties}")
        combo_difficulty = individual_difficulties[0]
        for i, diff in enumerate(individual_difficulties[1:], 1):
            scaling_factor = 1.0 / (1 + i * 0.15)
            combo_difficulty += diff * scaling_factor
    else:
        # print(f"Total difficulties: {total_difficulty}")
        combo_difficulty = total_difficulty

    return {
        "name": full_combo_name,
        "difficulty": round(combo_difficulty, 2),
        "components": components,
        "totalDifficulty": round(total_difficulty, 2),
        "individualDifficulties": individual_difficulties,
        "numSwitchUps": n_switch_ups,
        "difficultyLevel": difficulty_level,
    }


if __name__ == "__main__":
    # Test the function
    import sys

    difficulty = sys.argv[1] if len(sys.argv) > 1 else "advanced"
    n_switch = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    result = generate_trick_combo(difficulty, n_switch)

    print("=" * 70)
    print(f"GENERATING COMBO: {difficulty.upper()} with {n_switch} switch-ups")
    print("=" * 70)
    print(f"\n{result['name']}")
    print(f"\nDiminishing Difficulty: {result['difficulty']}")
    print(f"Total (Additive): {result['totalDifficulty']}")
    print("\nComponents:")
    for comp in result["components"]:
        print(f"  - {comp['trick']}: {comp['difficulty']}")
