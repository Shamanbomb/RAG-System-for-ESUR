# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 13:19:06 2025

@author: akome
"""

import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
import numpy as np

def create_grouped_stacked_percentage_plot_horizontal():
    try:
        # 1) Read inputs
        truthfulness_ratings = entry_truth_ratings.get().split(',')
        gpt4o_truth_counts   = list(map(int, entry_gpt4o_truth.get().split(',')))
        unenh_truth_counts   = list(map(int, entry_unenh_truth.get().split(',')))
        enh_truth_counts     = list(map(int, entry_enh_truth.get().split(',')))

        completeness_ratings = entry_compl_ratings.get().split(',')
        gpt4o_compl_counts   = list(map(int, entry_gpt4o_compl.get().split(',')))
        unenh_compl_counts   = list(map(int, entry_unenh_compl.get().split(',')))
        enh_compl_counts     = list(map(int, entry_enh_compl.get().split(',')))

        usefulness_ratings   = entry_usef_ratings.get().split(',')
        gpt4o_usef_counts    = list(map(int, entry_gpt4o_usef.get().split(',')))
        unenh_usef_counts    = list(map(int, entry_unenh_usef.get().split(',')))
        enh_usef_counts      = list(map(int, entry_enh_usef.get().split(',')))

        # 2) Convert rating strings to ints
        truthfulness_ratings = [int(r.strip()) for r in truthfulness_ratings]
        completeness_ratings = [int(r.strip()) for r in completeness_ratings]
        usefulness_ratings   = [int(r.strip()) for r in usefulness_ratings]

        # 3) Data structure
        metrics = [
            {
                'name': 'Truthfulness',
                'ratings': truthfulness_ratings,
                'counts': [
                    ('GPT4o',   gpt4o_truth_counts),
                    ('Unenh',   unenh_truth_counts),
                    ('Enh',     enh_truth_counts),
                ]
            },
            {
                'name': 'Completeness',
                'ratings': completeness_ratings,
                'counts': [
                    ('GPT4o',   gpt4o_compl_counts),
                    ('Unenh',   unenh_compl_counts),
                    ('Enh',     enh_compl_counts),
                ]
            },
            {
                'name': 'Usefulness',
                'ratings': usefulness_ratings,
                'counts': [
                    ('GPT4o',   gpt4o_usef_counts),
                    ('Unenh',   unenh_usef_counts),
                    ('Enh',     enh_usef_counts),
                ]
            },
        ]

        # 4) Pastel color scheme 
        #    (For Truthfulness: 0:"#ffd9d9", 1:"#d9ffd9")
        #    (For others 1..5:  1:"#ffd9d9", 2:"#ffe9d9", 3:"#ffffd9", 4:"#d9ffe9", 5:"#d9ffd9")
        def get_color(metric_name, rating):
            if metric_name == "Truthfulness":
                if rating == 0:
                    return "#ffd9d9"
                else:
                    return "#d9ffd9"
            else:
                color_map = {
                    1: "#ffd9d9",
                    2: "#ffe9d9",
                    3: "#ffffd9",
                    4: "#d9ffe9",
                    5: "#d9ffd9"
                }
                return color_map.get(rating, "#cccccc")

        # 5) We define 3 groups (Truth/Comp/Usef) along the **y-axis**,
        #    each group has 3 bars => positions y= [start, start+1, start+2]
        group_spacing = 4
        y_positions = []
        group_centers = []
        for i, m in enumerate(metrics):
            group_start = i * group_spacing
            y_vals = [group_start, group_start + 1, group_start + 2]
            y_positions.append(y_vals)
            group_centers.append(group_start + 1)

        fig, ax = plt.subplots(figsize=(10, 6))

        # 6) Helper for horizontal stacked bar
        #    We'll do: barh(y=yVal, left=leftVal, width=frac, height=0.8)
        #    and accumulate leftVal for each rating segment
        def draw_stacked_barh_percent(y, counts_for_ratings, rating_categories, metric_name):
            total = sum(counts_for_ratings)
            if total == 0:
                return
            left_val = 0.0
            for rating in sorted(rating_categories):
                try:
                    idx = rating_categories.index(rating)
                except ValueError:
                    continue

                if idx >= len(counts_for_ratings):
                    continue
                count = counts_for_ratings[idx]
                if count == 0:
                    continue

                frac = (count / total) * 100
                color = get_color(metric_name, rating)
                # barh:  y => the center row,
                #        width => frac,
                #        left => left_val
                ax.barh(y, frac, left=left_val, height=0.8, color=color)

                if frac >= 5:
                    x_center = left_val + frac / 2
                    label_text = f"{rating} ({int(round(frac))}%)"
                    ax.text(x_center, y, label_text,
                            ha='center', va='center',
                            fontweight='bold', fontsize=8)
                left_val += frac

        # 7) Actually plot each metric group
        for i, metric in enumerate(metrics):
            y_vals = y_positions[i]
            rating_list = metric['ratings']
            for j, (model_name, counts) in enumerate(metric['counts']):
                y_bar = y_vals[j]
                draw_stacked_barh_percent(y_bar, counts, rating_list, metric['name'])

        # 8) y-axis ticks correspond to the 9 bars (3 per group)
        all_y = []
        all_labels = []
        for i, metric in enumerate(metrics):
            y_vals = y_positions[i]
            for (model_name, _) in metric['counts']:
                all_labels.append(model_name)
            all_y.extend(y_vals)

        ax.set_yticks(all_y)
        ax.set_yticklabels(all_labels)

        # 9) Add metric labels on the y-axis or x-axis
        #    We'll put them on the left side near x=-10 or so, at the group_center
        #    Alternatively, you can place them on top/bottom or do something else
        for i, metric in enumerate(metrics):
            ax.text(-10, group_centers[i], metric['name'],
                    ha='right', va='center',
                    fontsize=11, fontweight='bold')

        # Flip the axis limits so everything is visible
        # We'll assume the maximum stacked is 100% on x.
        ax.set_xlim(0, 110)
        ax.set_xlabel("Percentage of Ratings (%)")

        # A custom chart title
        ax.set_title("Distribution of Ratings across the Different Models (Horizontal)")

        # No legend, each stacked segment is labeled
        plt.tight_layout()
        plt.savefig("mychart.pdf", bbox_inches='tight')
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# --------------------------------------------------------------------
# Below is your Tkinter UI hooking into the function above
# --------------------------------------------------------------------
root = tk.Tk()
root.title("Grouped+Stacked Horizontal Chart")

# TRUTHFULNESS
tk.Label(root, text="Truthfulness Ratings:").grid(row=0, column=0, padx=5, pady=5)
entry_truth_ratings = tk.Entry(root, width=50)
entry_truth_ratings.insert(0, "0,1")
entry_truth_ratings.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="GPT4o Truth Counts:").grid(row=1, column=0, padx=5, pady=5)
entry_gpt4o_truth = tk.Entry(root, width=50)
entry_gpt4o_truth.insert(0, "50,108")
entry_gpt4o_truth.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Unenh Truth Counts:").grid(row=2, column=0, padx=5, pady=5)
entry_unenh_truth = tk.Entry(root, width=50)
entry_unenh_truth.insert(0, "27,131")
entry_unenh_truth.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Enh Truth Counts:").grid(row=3, column=0, padx=5, pady=5)
entry_enh_truth = tk.Entry(root, width=50)
entry_enh_truth.insert(0, "17,141")
entry_enh_truth.grid(row=3, column=1, padx=5, pady=5)

# COMPLETENESS
tk.Label(root, text="Completeness Ratings:").grid(row=4, column=0, padx=5, pady=5)
entry_compl_ratings = tk.Entry(root, width=50)
entry_compl_ratings.insert(0, "1,2,3,4,5")
entry_compl_ratings.grid(row=4, column=1, padx=5, pady=5)

tk.Label(root, text="GPT4o Compl Counts:").grid(row=5, column=0, padx=5, pady=5)
entry_gpt4o_compl = tk.Entry(root, width=50)
entry_gpt4o_compl.insert(0, "25,24,54,28,27")
entry_gpt4o_compl.grid(row=5, column=1, padx=5, pady=5)

tk.Label(root, text="Unenh Compl Counts:").grid(row=6, column=0, padx=5, pady=5)
entry_unenh_compl = tk.Entry(root, width=50)
entry_unenh_compl.insert(0, "6,6,36,33,77")
entry_unenh_compl.grid(row=6, column=1, padx=5, pady=5)

tk.Label(root, text="Enh Compl Counts:").grid(row=7, column=0, padx=5, pady=5)
entry_enh_compl = tk.Entry(root, width=50)
entry_enh_compl.insert(0, "5,8,26,29,90")
entry_enh_compl.grid(row=7, column=1, padx=5, pady=5)

# USEFULNESS
tk.Label(root, text="Usefulness Ratings:").grid(row=8, column=0, padx=5, pady=5)
entry_usef_ratings = tk.Entry(root, width=50)
entry_usef_ratings.insert(0, "1,2,3,4,5")
entry_usef_ratings.grid(row=8, column=1, padx=5, pady=5)

tk.Label(root, text="GPT4o Usef Counts:").grid(row=9, column=0, padx=5, pady=5)
entry_gpt4o_usef = tk.Entry(root, width=50)
entry_gpt4o_usef.insert(0, "25,18,58,32,25")
entry_gpt4o_usef.grid(row=9, column=1, padx=5, pady=5)

tk.Label(root, text="Unenh Usef Counts:").grid(row=10, column=0, padx=5, pady=5)
entry_unenh_usef = tk.Entry(root, width=50)
entry_unenh_usef.insert(0, "6,14,29,37,72")
entry_unenh_usef.grid(row=10, column=1, padx=5, pady=5)

tk.Label(root, text="Enh Usef Counts:").grid(row=11, column=0, padx=5, pady=5)
entry_enh_usef = tk.Entry(root, width=50)
entry_enh_usef.insert(0, "3,17,22,36,76")
entry_enh_usef.grid(row=11, column=1, padx=5, pady=5)

# Button to generate the horizontal plot
btn_generate = tk.Button(
    root, text="Generate Horizontal Grouped+Stacked Chart",
    command=create_grouped_stacked_percentage_plot_horizontal
)
btn_generate.grid(row=12, column=0, columnspan=2, pady=10)

root.mainloop()
