# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 19:33:11 2025

@author: akome
"""

import pickle

# Load the documents.pkl file
with open('documents.pkl', 'rb') as f:
    data = pickle.load(f)

# Print original number of chunks
print(f"Original number of chunks: {len(data)}")

# Define the new chunk structure by splitting the content accordingly
new_chunks = [
    "B.5. DIALYSIS AND CONTRAST MEDIUM ADMINISTRATION\n"
    "All iodine- and gadolinium-based contrast agents can be removed by hemodialysis or peritoneal dialysis. "
    "However, there is no evidence that hemodialysis protects patients with impaired renal function from post contrast "
    "acute kidney injury or nephrogenic systemic fibrosis. In all patients, avoid osmotic and fluid overload. "
    "To avoid the risk of NSF refer to A.3.2. PATIENTS ON DIALYSIS\n"
    "Patients on hemodialysis Iodine-based contrast medium • Correlation of time of the contrast medium injection with the "
    "hemodialysis session is unnecessary. • Extra hemodialysis session to remove contrast medium is unnecessary. "
    "Gadolinium-based contrast agent • Correlation of time of the contrast agent injection with the hemodialysis session is "
    "recommended. • Extra hemodialysis session to remove contrast agent as soon as possible after it has been administered is recommended.",

    "B.6. CAN IODINE- AND GADOLINIUM-BASED CONTRAST AGENTS SAFELY BE GIVEN ON THE SAME DAY FOR ROUTINE EXAMINATIONS?\n"
    "Efficient practice may involve giving iodine- and gadolinium-based contrast agents for enhanced CT and MR on the same day. "
    "To reduce any potential for nephrotoxicity the following are recommended:\n"
    "1. Patients with normal renal function or moderately reduced (GFR > 30 ml/min/1.73 m2). "
    "75 % of both gadolinium- and iodine-based contrast agents are excreted by 4 hours after administration. "
    "There should be 4 hours between injections of iodine- and gadolinium-based contrast agents.\n"
    "2. Patients with severely reduced renal function (GFR < 30 ml/min/1.73 m2 or on dialysis). "
    "There should be 7 days between injections of iodine- and gadolinium-based contrast agents.",

    "B.7. HOW LONG SHOULD THERE BE BETWEEN TWO IODINE-BASED CONTRAST MEDIUM INJECTIONS FOR ROUTINE EXAMINATIONS?\n"
    "1. Patients with normal or moderately reduced renal function (GFR > 30 ml/min/1.73 m2). "
    "75 % of iodine-based contrast medium is excreted by 4 hours after administration. "
    "There should be 4 hours between injections of iodine-based contrast medium.\n"
    "2. Patients with severely reduced renal function (GFR < 30 ml/min/1.73 m2). "
    "There should be 48 hours between injections of iodine-based contrast medium.\n"
    "3. Patients on dialysis. If there is remnant renal function, there should be at least 48 hours between injections of iodine-based contrast medium.",

    "B.8. HOW LONG SHOULD THERE BE BETWEEN TWO GADOLINIUM-BASED CONTRAST AGENT INJECTIONS FOR ROUTINE EXAMINATIONS?\n"
    "1. Patients with normal or moderately reduced renal function (GFR > 30 ml/min/1.73 m2). "
    "75 % of extracellular gadolinium-based contrast agents are excreted by 4 hours after administration. "
    "There should be 4 hours between injections of gadolinium-based contrast agent.\n"
    "2. Patients with severely reduced renal function (GFR < 30 ml/min/1.73 m2) or on dialysis. "
    "There should be 7 days between injections of gadolinium-based contrast agent."
]

# Remove the old chunks (16, 17, 18) and insert the new ones
data = data[:15] + new_chunks + data[18+1:]

# Print updated number of chunks
print(f"Updated number of chunks: {len(data)}")

# Save the modified data back to documents.pkl
with open('documents.pkl', 'wb') as f:
    pickle.dump(data, f)

print("Updated documents.pkl has been saved successfully.")
