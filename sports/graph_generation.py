import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


N_SWITCH_UPS = 3
DIFFICULTY_LEVEL = "advanced"

df = pd.read_csv("/home/andrew/Documents/trick_generator/tricktable.csv")


def starting_trick_graph(tricks_df):
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

    # Hblock branch - Scaled down from 6.0
    add_node("hblock_spin_0", "0", 4, 0.0)  # Beginner
    add_node("hblock_spin_270", "270", 4, 0.35)  # Intermediate/Advanced
    add_node("hblock_spin_450", "450", 4, 2.5)  # Scaled down: 6.0 → 2.5
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

    # Soul branch - Lower negative weight to spread distribution
    add_node("soul_negative", "negative", 4, 0.15)  # Lower so neg 360s don't dominate
    add_node("soul_regular", "regular", 4, 0.05)  # Easy
    connect_all(["soul"], ["soul_negative", "soul_regular"])

    add_node("soul_spin_0", "0", 5, 0.0)  # Beginner
    add_node("soul_spin_180", "180", 5, 0.15)  # Intermediate
    add_node("soul_spin_360", "360", 5, 0.6)  # Advanced/Pro
    add_node("soul_spin_540", "540", 5, 4.0)  # Scaled down: 10.0 → 4.0
    connect_all(
        ["soul_negative", "soul_regular"],
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
    # Build a table of all valid node-to-trick combinations (all complete paths)
    source = "approach"

    # Trick nodes are terminal nodes with ids like "hblock::name::idx" / "soul::name::idx"
    trick_nodes = [n for n in G.nodes if "::" in n and G.out_degree(n) == 0]

    records = []

    for target in trick_nodes:
        for path in nx.all_simple_paths(G, source=source, target=target):
            rec = {
                "approach": None,
                "stance": None,
                "family": None,
                "soul_mode": None,  # only for soul branch
                "spin": None,
                "spin_dir": None,  # inspin/outspin where applicable
                "trick": None,
                "trick_node": target,
                "path_labels": " -> ".join(node_labels.get(n, n) for n in path),
            }

            # Parse path into columns
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

            # Optional weight summaries
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

    combinations_df = (
        pd.DataFrame(records)
        .sort_values(
            ["family", "trick", "approach", "stance", "soul_mode", "spin", "spin_dir"]
        )
        .reset_index(drop=True)
    )

    return combinations_df


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


def switch_up_graph(tricks_df, n_switch_ups: int = 1):
    G2 = nx.DiGraph()
    node_labels2 = {}

    kind_col = "soul or hblock"
    name_col = "trick name"
    diff_col = "normalised difficulty"

    def add_node2(node_id, label, layer, weight=None, role=None):
        attrs = {"subset": layer}
        if weight is not None:
            attrs["weight"] = float(weight)
        if role is not None:
            attrs["role"] = role
        G2.add_node(node_id, **attrs)
        node_labels2[node_id] = label

    def connect_all2(sources, targets):
        for s in sources:
            for t in targets:
                G2.add_edge(s, t)

    # Filter trick lists from df
    hblock_df2 = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("hblock"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )

    soul_df2 = (
        tricks_df.loc[
            tricks_df[kind_col].astype(str).str.strip().str.lower().eq("soul"),
            [name_col, diff_col],
        ]
        .dropna(subset=[name_col])
        .sort_values(name_col)
    )

    # Root nodes
    add_node2("start::hblock", "hblock", 0, role="starting_stance")
    add_node2("start::soul", "soul", 0, role="starting_stance")

    # Duplicate stance layer for each root
    for fam in ["hblock", "soul"]:
        add_node2(f"{fam}::switch", "switch", 1, 0.7, role="stance")
        add_node2(f"{fam}::natural", "natural", 1, 0.1, role="stance")
        G2.add_edge(f"start::{fam}", f"{fam}::switch")
        G2.add_edge(f"start::{fam}", f"{fam}::natural")

    # Hblock branch (duplicated from stance onward)
    add_node2("hblock::family", "hblock", 2, role="family")
    connect_all2(["hblock::switch", "hblock::natural"], ["hblock::family"])

    # Switch-up penalty: SMALLER to prevent difficulty explosion
    penalty_multiplier = min(n_switch_ups * 0.1, 0.4)  #  Reduced cap: 0.8 → 0.4

    add_node2("hblock::spin::0", "0", 3, 0.0, role="spin")
    add_node2("hblock::spin::270", "270", 3, 0.25 + penalty_multiplier, role="spin")
    add_node2(
        "hblock::spin::450", "450", 3, 2.0 + (penalty_multiplier * 2.5), role="spin"
    )
    connect_all2(
        ["hblock::family"],
        ["hblock::spin::0", "hblock::spin::270", "hblock::spin::450"],
    )

    add_node2("hblock::inspin", "inspin", 4, 0.3, role="spin_dir")
    add_node2("hblock::outspin", "outspin", 4, 0.4, role="spin_dir")
    connect_all2(
        ["hblock::spin::270", "hblock::spin::450"],
        ["hblock::inspin", "hblock::outspin"],
    )

    hblock_trick_nodes2 = []
    for i, row in hblock_df2.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"hblock::trick::{trick_name}::{i}"
        add_node2(node_id, trick_name, 5, row[diff_col], role="trick")
        hblock_trick_nodes2.append(node_id)

    connect_all2(["hblock::spin::0"], hblock_trick_nodes2)
    connect_all2(["hblock::inspin", "hblock::outspin"], hblock_trick_nodes2)

    # Soul branch (duplicated from stance onward)
    add_node2("soul::family", "soul", 2, role="family")
    connect_all2(["soul::switch", "soul::natural"], ["soul::family"])

    # Negatives and spins: VERY SMALL penalties to keep mega-tricks rare
    penalty_multiplier = min(n_switch_ups * 0.1, 0.5)  # Caps at 0.5 max

    add_node2(
        "soul::mode::negative",
        "negative",
        3,
        0.1 + penalty_multiplier,
        role="soul_mode",
    )
    add_node2("soul::mode::regular", "regular", 3, 0.02, role="soul_mode")
    connect_all2(["soul::family"], ["soul::mode::negative", "soul::mode::regular"])

    # Spins - Scaled down from 8.0
    add_node2("soul::spin::0", "0", 4, 0.0, role="spin")
    add_node2(
        "soul::spin::180", "180", 4, 0.12 + (penalty_multiplier * 0.3), role="spin"
    )
    add_node2(
        "soul::spin::360", "360", 4, 0.5 + (penalty_multiplier * 0.8), role="spin"
    )
    add_node2(
        "soul::spin::540", "540", 4, 3.2 + (penalty_multiplier * 3.0), role="spin"
    )
    connect_all2(
        ["soul::mode::negative", "soul::mode::regular"],
        ["soul::spin::0", "soul::spin::180", "soul::spin::360", "soul::spin::540"],
    )

    add_node2("soul::inspin", "inspin", 5, 0.3, role="spin_dir")
    add_node2("soul::outspin", "outspin", 5, 0.4, role="spin_dir")
    connect_all2(
        ["soul::spin::180", "soul::spin::360", "soul::spin::540"],
        ["soul::inspin", "soul::outspin"],
    )

    soul_trick_nodes2 = []
    for i, row in soul_df2.iterrows():
        trick_name = str(row[name_col]).strip()
        node_id = f"soul::trick::{trick_name}::{i}"
        add_node2(node_id, trick_name, 6, row[diff_col], role="trick")
        soul_trick_nodes2.append(node_id)

    connect_all2(["soul::spin::0"], soul_trick_nodes2)
    connect_all2(["soul::inspin", "soul::outspin"], soul_trick_nodes2)

    return G2, node_labels2


def create_switch_trick_table(G2, node_labels2):
    # Rebuild combinations table from both roots
    sources2 = ["start::hblock", "start::soul"]
    trick_nodes2 = [n for n in G2.nodes if G2.nodes[n].get("role") == "trick"]

    records2 = []
    for source2 in sources2:
        for target2 in trick_nodes2:
            for path2 in nx.all_simple_paths(G2, source=source2, target=target2):
                rec2 = {
                    "starting_stance": None,
                    "stance": None,
                    "family": None,
                    "soul_mode": None,
                    "spin": None,
                    "spin_dir": None,
                    "trick": None,
                    "trick_node": target2,
                    "path_labels": " -> ".join(node_labels2.get(n, n) for n in path2),
                }

                for n in path2:
                    role = G2.nodes[n].get("role")
                    label = node_labels2.get(n, n)
                    if role == "starting_stance":
                        rec2["starting_stance"] = label
                    elif role == "stance":
                        rec2["stance"] = label
                    elif role == "family":
                        rec2["family"] = label
                    elif role == "soul_mode":
                        rec2["soul_mode"] = label
                    elif role == "spin":
                        rec2["spin"] = label
                    elif role == "spin_dir":
                        rec2["spin_dir"] = label
                    elif role == "trick":
                        rec2["trick"] = label

                weights2 = [
                    G2.nodes[n].get("weight")
                    for n in path2
                    if G2.nodes[n].get("weight") is not None
                ]
                rec2["path_weight_sum"] = float(sum(weights2)) if weights2 else 0.0

                wprod2 = 1.0
                for w in weights2:
                    wprod2 *= float(w)
                rec2["path_weight_product"] = wprod2
                rec2["trick_difficulty"] = G2.nodes[target2].get("weight")

                records2.append(rec2)

    combinations_df_start = (
        pd.DataFrame(records2)
        .sort_values(
            [
                "starting_stance",
                "family",
                "trick",
                "stance",
                "soul_mode",
                "spin",
                "spin_dir",
            ]
        )
        .reset_index(drop=True)
    )
    return combinations_df_start


def select_weighted_trick(
    combination_df, DIFFICULTY=None, random_state=None, n_switch=0
):
    """
    Randomly select a trick from a combinations dataframe, weighted by path_weight_sum.

    Parameters
    ----------
    combination_df : pd.DataFrame
        Input dataframe with at least:
        family, path_weight_sum, and either output_trick_* or trick.
    DIFFICULTY : str or None
        One of: "beginner", "intermediate", "advanced", "pro", "insane".
        If None, selection is made from the full distribution.
    random_state : int or None
        Optional seed for reproducible sampling.

    Returns
    -------
    dict
        {
            "family": ...,
            "path_weight_sum": ...,
            "output_trick_base": ...,
            "output_trick_full": ...
        }
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

    # Percentile rank used for difficulty slicing
    work["_pct"] = work["path_weight_sum"].rank(method="average", pct=True)

    # FIXED: Wider bands to include more variety within each level
    difficulty_bands = {
        "beginner": (0.00, 0.50),  # Bottom 50% - lots of variety
        "intermediate": (0.00, 0.70),  # 35-70% - overlaps with beginner
        "advanced": (0.00, 0.85),  # 55-85% - overlaps lower for variety
        "pro": (0.00, 0.95),  # 65-95% - WIDER to include 360° mix
        "insane": (0.00, 1.00),  # Top 10%
    }

    if DIFFICULTY is None:
        eligible = work
    else:
        key = str(DIFFICULTY).strip().lower()
        if key not in difficulty_bands:
            raise ValueError(
                "DIFFICULTY must be one of: "
                "'beginner', 'intermediate', 'advanced', 'pro', 'insane', or None."
            )
        lo, hi = difficulty_bands[key]
        if lo == 0:
            eligible = work[(work["_pct"] >= lo) & (work["_pct"] <= hi)]
        else:
            eligible = work[(work["_pct"] > lo) & (work["_pct"] <= hi)]

        # Fallback if a band is empty due to ties/small sample size
        if eligible.empty:
            eligible = work

    # NEW APPROACH: Create weighted sample distribution
    # Easier tricks (lower path_weight_sum) appear MANY more times in the pool
    # This naturally enforces rarity of high-difficulty tricks

    # Difficulty-specific multiplier for inverse weighting
    difficulty_multipliers = {
        "beginner": 10.0 * n_switch,  # Very strong preference for easiest tricks
        "intermediate": 3.858 * n_switch,
        "advanced": 1.85 * n_switch,  # EXTREME - strongly favor easier end of band
        "pro": 1.566 * n_switch,  # ULTRA EXTREME - max 1 mega spin
        "insane": 0.01 * n_switch,  # Less aggressive - allow harder tricks
    }

    multiplier = difficulty_multipliers.get(key, 10.0) if DIFFICULTY else 8.0

    # Calculate inverse weights: 1 / (path_weight_sum ^ multiplier)
    # Lower difficulty = higher weight = more copies in sample pool
    inverse_weights = 1.0 / (eligible["path_weight_sum"] ** multiplier)

    # Normalize so they sum to 1
    inverse_weights = inverse_weights / inverse_weights.sum()

    # Create sample pool of 3000 tricks, weighted by inverse difficulty
    # Easier tricks will appear many more times
    sample_size = 3000
    sample_pool_indices = np.random.choice(
        eligible.index, size=sample_size, replace=True, p=inverse_weights
    )

    # Now randomly pick from this pre-weighted pool (uniform sampling)
    chosen_idx = np.random.choice(sample_pool_indices)
    chosen = eligible.loc[chosen_idx]

    return {
        "family": chosen["family"],
        "spin": chosen["spin"],
        "path_weight_sum": float(chosen["path_weight_sum"]),
        "output_trick_base": chosen["output_trick_base"],
        "output_trick_full": chosen["output_trick_full"],
    }


def adjust_spin_for_switch(df, previous_family):
    df = df.copy()

    # Convert spin to numeric safely
    df["spin_num"] = pd.to_numeric(df["spin"], errors="coerce")

    def transform(row):
        spin = row["spin_num"]
        if pd.isna(spin):
            return spin

        # SAME FAMILY + HBLOCK → bump 270 → 360
        if row["family"] == previous_family and row["family"] == "hblock":
            spin = max(spin + 90, 0)
            return spin
        elif row["family"] == previous_family and row["family"] == "soul":
            return spin

        return spin

    df["spin_num"] = df.apply(transform, axis=1)

    # Write back to original column (keep as int/string depending on your system)
    df["spin"] = df["spin_num"].astype(int).astype(str)

    return df.drop(columns=["spin_num"])


# Store individual difficulties for better combo calculation
all_tricks = None
all_trick_difficulty = 0
DIFFICULTY_LEVEL = (
    "advanced"  # Change this to generate combos of different difficulty levels
)
N_SWITCH_UPS = 3
TOTAL_WEIGHTED_DIFFICULTY = 0

start_tricks, start_trick_labels = starting_trick_graph(df)
start_trick_table = create_start_trick_table(start_tricks, start_trick_labels)
start_trick_table_formatted = start_trick_formatting(
    start_trick_table, None, start_trick=True
)
select_weighted_start_trick = select_weighted_trick(
    start_trick_table_formatted,
    DIFFICULTY=DIFFICULTY_LEVEL,
    random_state=None,
    n_switch=N_SWITCH_UPS,
)


TOTAL_WEIGHTED_DIFFICULTY += select_weighted_start_trick["path_weight_sum"]

print("=" * 70)
print(f"GENERATING COMBO: {DIFFICULTY_LEVEL.upper()} with {N_SWITCH_UPS} switch-ups")
print("=" * 70)
print("\n✓ Start Trick:")
print(f"  Difficulty: {TOTAL_WEIGHTED_DIFFICULTY:.3f}")
print(f"  Trick: {select_weighted_start_trick['output_trick_full']}")
all_tricks = select_weighted_start_trick["output_trick_full"]
all_trick_difficulty += select_weighted_start_trick["path_weight_sum"]
for i in range(N_SWITCH_UPS):
    if i == 0:
        switch_graph, switch_labels = switch_up_graph(df, n_switch_ups=1)
        switch_trick_table = create_switch_trick_table(switch_graph, switch_labels)
        switch_trick_table = adjust_spin_for_switch(
            switch_trick_table, select_weighted_start_trick["family"]
        )
        switch_trick_table_formatted = start_trick_formatting(
            switch_trick_table,
            select_weighted_start_trick["output_trick_full"],
            start_trick=False,
        )

        selected_switch_trick1 = select_weighted_trick(
            switch_trick_table_formatted,
            DIFFICULTY=DIFFICULTY_LEVEL,
            random_state=None,
            n_switch=N_SWITCH_UPS / 2,
        )
        while (
            selected_switch_trick1["output_trick_base"]
            == select_weighted_start_trick["output_trick_base"]
            and selected_switch_trick1["spin"] == 0
        ):
            selected_switch_trick1 = select_weighted_trick(
                switch_trick_table_formatted,
                DIFFICULTY=DIFFICULTY_LEVEL,
                random_state=None,
                n_switch=N_SWITCH_UPS / 2,
            )

        TOTAL_WEIGHTED_DIFFICULTY += selected_switch_trick1["path_weight_sum"]
        print("\n✓ Switch Trick:", i + 1)
        print(f"  Difficulty: {TOTAL_WEIGHTED_DIFFICULTY:.3f}")
        print(f"  Trick: {selected_switch_trick1['output_trick_full']}")
        print(f"  Spin: {selected_switch_trick1['spin']}")
        selected_switch_trick_old = selected_switch_trick1
        all_tricks += " to " + selected_switch_trick1["output_trick_full"]
        all_trick_difficulty += selected_switch_trick1["path_weight_sum"]

    else:
        switch_graph, switch_labels = switch_up_graph(df, n_switch_ups=i + 1)
        switch_trick_table = create_switch_trick_table(switch_graph, switch_labels)
        switch_trick_table = adjust_spin_for_switch(
            switch_trick_table, selected_switch_trick_old["family"]
        )
        switch_trick_table_formatted = start_trick_formatting(
            switch_trick_table,
            select_weighted_start_trick["output_trick_full"],
            start_trick=False,
        )
        selected_switch_trick2 = select_weighted_trick(
            switch_trick_table_formatted,
            DIFFICULTY=DIFFICULTY_LEVEL,
            random_state=None,
            n_switch=N_SWITCH_UPS / 2,
        )
        # while selected_switch_trick2["output_trick_base"] == selected_switch_trick["output_trick_base"] and selected_switch_trick2["spin"] == 0:
        #     selected_switch_trick2 = select_weighted_trick(
        #     switch_trick_table_formatted, DIFFICULTY=DIFFICULTY_LEVEL, random_state=None, n_switch=N_SWITCH_UPS/2,
        # )
        TOTAL_WEIGHTED_DIFFICULTY += selected_switch_trick2["path_weight_sum"]
        print("\n✓ Switch Trick:", i + 1)
        print(f"  Difficulty: {TOTAL_WEIGHTED_DIFFICULTY:.3f}")
        print(f"  Trick: {selected_switch_trick2['output_trick_full']}")
        print(f"  Trick: {selected_switch_trick2['output_trick_base']}")
        print(f"  Spin: {selected_switch_trick2['spin']}")
        all_tricks += " to " + selected_switch_trick2["output_trick_full"]
        all_trick_difficulty += selected_switch_trick2["path_weight_sum"]
    selected_switch_trick_old = selected_switch_trick2
