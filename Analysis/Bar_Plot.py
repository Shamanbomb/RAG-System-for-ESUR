# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 16:17:48 2025

@author: akome
"""

import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
import numpy as np

# Define pastel colors for each model
COLOR_MAP = {
    'Unenhanced': '#b5d9ff',  # pastel blue
    'Enhanced': '#d9ffd9',    # pastel green
    'ChatGPT 4o': '#ffd9d9'   # pastel red
}

def create_bar_chart():
    try:
        # Process inputs, stripping extra spaces
        metrics = [m.strip() for m in entry_metrics.get().split(',')]
        means_list = [
            list(map(float, entry_unenhanced_means.get().split(','))),
            list(map(float, entry_enhanced_means.get().split(','))),
            list(map(float, entry_chatgpt4o_means.get().split(',')))
        ]
        stds_list = [
            list(map(float, entry_std_unenhanced.get().split(','))),
            list(map(float, entry_std_enhanced.get().split(','))),
            list(map(float, entry_std_chatgpt4o.get().split(',')))
        ]
        # Expecting 3 p-values per metric:
        # [p_left, p_full, p_right] = [p-value for (Unenhanced, Enhanced), 
        #                              p-value for (Unenhanced, ChatGPT 4o), 
        #                              p-value for (Enhanced, ChatGPT 4o)]
        raw_pvalues = [p.strip() for p in entry_pvalues.get().split(',')]
        n_metrics = len(metrics)
        if len(raw_pvalues) != n_metrics * 3:
            raise ValueError("For each metric, please provide 3 p-values (total p-values must equal 3 * number of metrics).")
        # Reorganize p-values per metric
        p_values = []
        for i in range(n_metrics):
            p_values.append(raw_pvalues[i*3:(i+1)*3])
        
        # Validate that all lists have the same length
        if not (n_metrics == len(means_list[0]) == len(means_list[1]) == len(means_list[2]) ==
                len(stds_list[0]) == len(stds_list[1]) == len(stds_list[2])):
            raise ValueError("All input lists (metrics, means, stds, p-values) must have the same length per metric.")

        # Use the original model order labels
        labels = ['Unenhanced', 'Enhanced', 'ChatGPT 4o']
        # Sort models by overall average means (for consistent ordering)
        avg = {lbl: np.mean(vals) for lbl, vals in zip(labels, means_list)}
        sorted_labels = sorted(labels, key=lambda l: avg[l])
        sorted_means = [means_list[labels.index(l)] for l in sorted_labels]
        sorted_stds = [stds_list[labels.index(l)] for l in sorted_labels]

        # x positions for each metric and bar width
        x = np.arange(n_metrics)
        width = 0.25

        fig, ax = plt.subplots()
        for i, lbl in enumerate(sorted_labels):
            ax.bar(x + i * width, sorted_means[i], width,
                   yerr=sorted_stds[i],
                   label=lbl,
                   capsize=5,
                   color=COLOR_MAP[lbl])
        
        # For each metric, draw three brackets:
        # Bottom-left: between first two bars (comparison: sorted_labels[0] vs sorted_labels[1])
        # Bottom-right: between last two bars (comparison: sorted_labels[1] vs sorted_labels[2])
        # Top: spanning from the first bar to the last bar (comparison: sorted_labels[0] vs sorted_labels[2])
        for j in range(n_metrics):
            # Calculate the top of the bars for metric j
            local_max = max(sorted_means[i][j] + sorted_stds[i][j] for i in range(3))
            # Define gaps (adjust these factors as needed)
            gap = local_max * 0.05 if local_max != 0 else 0.5
            # Offsets for the two levels:
            bottom_offset = local_max + gap
            top_offset = bottom_offset + gap

            # Get x positions for the three bars
            x0 = x[j] + 0 * width   # left bar
            x1 = x[j] + 1 * width   # middle bar
            x2 = x[j] + 2 * width   # right bar

            bracket_height = gap * 0.5  # height for each bracket

            # Draw bottom-left bracket (between bar 0 and bar 1)
            bl_base = bottom_offset
            bl_top = bl_base + bracket_height
            ax.plot([x0, x0, x1, x1], [bl_base, bl_top, bl_top, bl_base], lw=1.2, color='black')
            ax.text((x0+x1)/2, bl_top + gap*0.1, f"p = {p_values[j][0]}", ha='center', va='bottom', fontsize=8)
            
            # Draw bottom-right bracket (between bar 1 and bar 2)
            br_base = bottom_offset
            br_top = br_base + bracket_height
            ax.plot([x1, x1, x2, x2], [br_base, br_top, br_top, br_base], lw=1.2, color='black')
            ax.text((x1+x2)/2, br_top + gap*0.1, f"p = {p_values[j][2]}", ha='center', va='bottom', fontsize=8)
            
            # Draw top bracket (full-range, from bar 0 to bar 2)
            top_base = top_offset
            top_top = top_base + bracket_height
            ax.plot([x0, x0, x2, x2], [top_base, top_top, top_top, top_base], lw=1.2, color='black')
            ax.text((x0+x2)/2, top_top + gap*0.1, f"p = {p_values[j][1]}", ha='center', va='bottom', fontsize=8)
            
        ax.set_xticks(x + width)
        ax.set_xticklabels(metrics)
        ax.set_ylabel('Mean Score')
        ax.set_title('Comparison of Truthfulness')
        ax.legend()
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig("mybarchart.pdf", bbox_inches='tight')
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

root = tk.Tk()
root.title("Scientific Bar Chart Generator")

fields = [
    ("Metrics (comma-separated):", "entry_metrics"),
    ("Unenhanced Means (comma-separated):", "entry_unenhanced_means"),
    ("Enhanced Means (comma-separated):", "entry_enhanced_means"),
    ("ChatGPT 4o Means (comma-separated):", "entry_chatgpt4o_means"),
    ("Std Devs (Unenhanced, comma-separated):", "entry_std_unenhanced"),
    ("Std Devs (Enhanced, comma-separated):", "entry_std_enhanced"),
    ("Std Devs (ChatGPT 4o, comma-separated):", "entry_std_chatgpt4o"),
    ("P-values (3 per metric, comma-separated):", "entry_pvalues")
]

for i, (label, var) in enumerate(fields):
    tk.Label(root, text=label).grid(row=i, column=0, padx=5, pady=5)
    globals()[var] = tk.Entry(root, width=50)
    globals()[var].grid(row=i, column=1, padx=5, pady=5)

tk.Button(root, text="Generate Bar Chart", command=create_bar_chart).grid(row=len(fields), column=0, columnspan=2, pady=10)
root.mainloop()

