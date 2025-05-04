# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 11:44:45 2025

@author: akome
"""

from math import comb
def exact_mcnemar_pvalue(N10, N01):
    d = N10 + N01
    if d == 0:
        return 1.0  # No discordant pairs => no difference to test
    
    # The two-sided p-value is essentially the probability of 
    # as many or more extreme splits of d under p=0.5
    # i.e. sum_{k=0 to observed_k} [ C(d,k) (0.5)^d ] * 2  (two-sided)
    
    observed_k = min(N10, N01)
    p_two_sided = 0
    for i in range(observed_k+1):
        p_two_sided += comb(d, i) * (0.5**d)
    p_two_sided *= 2
    
    # However, if observed_k*2 == d, we might double-count the exactly balanced scenario
    # Some references do a mid-p adjustment, but this is the basic test
    return min(1.0, p_two_sided)

# Example usage
N10 = 1
N01 = 5
pval = exact_mcnemar_pvalue(N10, N01)
print("Exact McNemar p-value =", pval)
