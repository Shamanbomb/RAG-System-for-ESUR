import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
import numpy as np

def create_grouped_stacked_percentage_plot():
    try:
        # -------------------------------------------------------------
        # 1) Read inputs from the Entry widgets
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

        # -------------------------------------------------------------
        # 3) Organize data into a structure we can iterate over
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

        # -------------------------------------------------------------
        # 4) Define color map
        # For Truthfulness (0,1) => 0:"#ffd9d9", 1:"#d9ffd9"
        # For other metrics (1..5):
        #   1:"#ffd9d9", 2:"#ffe9d9", 3:"#ffffd9", 4:"#d9ffe9", 5:"#d9ffd9"
        def get_color(metric_name, rating):
            if metric_name == "Truthfulness":
                if rating == 0:
                    return "#ffd9d9"  # bottom color
                else:
                    return "#d9ffd9"  # top color
            else:
                color_map = {
                    1: "#ffd9d9",
                    2: "#ffe9d9",
                    3: "#ffffd9",
                    4: "#d9ffe9",
                    5: "#d9ffd9"
                }
                return color_map.get(rating, "#cccccc")

        # -------------------------------------------------------------
        # 5) Lay out the x-axis: we have 3 metric groups, each with 3 bars
        group_spacing = 4
        x_positions = []
        group_centers = []
        for i, m in enumerate(metrics):
            group_start = i * group_spacing
            x_vals = [group_start, group_start + 1, group_start + 2]
            x_positions.append(x_vals)
            group_centers.append(group_start + 1)

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 10))

        # -------------------------------------------------------------
        # 6) Helper to draw stacked bars with rating & % labels
        def draw_stacked_bar_percent(x, counts_for_ratings, rating_categories, metric_name):
            total = sum(counts_for_ratings)
            if total == 0:
                return
            bottom_val = 0.0
            for rating in sorted(rating_categories):
                # Find the index of the rating, get the count
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
                ax.bar(x, frac, bottom=bottom_val, width=0.8, color=color)

                # Label only if segment is big enough
                if frac >= 5:
                    y_center = bottom_val + frac / 2
                    label_text = f"{rating} ({int(round(frac))}%)"
                    ax.text(x, y_center, label_text, ha='center', va='center',
                            fontweight='bold', fontsize=8)

                bottom_val += frac

        # -------------------------------------------------------------
        # 7) Plot each metric group
        for i, metric in enumerate(metrics):
            x_vals = x_positions[i]
            rating_list = metric['ratings']
            for j, (model_name, counts) in enumerate(metric['counts']):
                x_bar = x_vals[j]
                draw_stacked_bar_percent(x_bar, counts, rating_list, metric['name'])

        # -------------------------------------------------------------
        # 8) Label the x-axis bars with the model names
        all_x = []
        all_labels = []
        for i, metric in enumerate(metrics):
            x_vals = x_positions[i]
            for (model_name, _) in metric['counts']:
                all_labels.append(model_name)
            all_x.extend(x_vals)
        ax.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        ax.xaxis.grid(False)
        ax.set_xticks(all_x)
        ax.set_xticklabels(all_labels)

        # -------------------------------------------------------------
        # 9) Metric labels above each group
        for i, metric in enumerate(metrics):
            ax.text(group_centers[i], 105, metric['name'],
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylim(0, 110)
        ax.set_ylabel("Percentage of Ratings (%)")
        ax.set_title("Distribution of Ratings across the different Models")

        plt.tight_layout()
        plt.savefig("mychart.pdf", bbox_inches='tight')
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --------------------------------------------------------------------
# Below is your Tkinter UI hooking into the function above
# --------------------------------------------------------------------
root = tk.Tk()
root.title("Grouped+Stacked Percentage Chart (Rating + %, Pastel)")

# TRUTHFULNESS
tk.Label(root, text="Truthfulness Ratings:").grid(row=0, column=0, padx=5, pady=5)
entry_truth_ratings = tk.Entry(root, width=50)
entry_truth_ratings.insert(0, "0,1")  # binary
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

# Button to generate the plot
btn_generate = tk.Button(
    root, text="Generate Grouped+Stacked (Percent) Chart (Unified Pastels)",
    command=create_grouped_stacked_percentage_plot
)
btn_generate.grid(row=12, column=0, columnspan=2, pady=10)

root.mainloop()
