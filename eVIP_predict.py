#!/broad/software/free/Linux/redhat_5_x86_64/pkgs/python_2.5.4/bin/python
# <Script name>
# Author: Angela Brooks
# Program Completion Date:
# Description:
# Modification Date(s):
# Copyright (c) 2011, Angela Brooks. anbrooks@gmail.com
# All rights reserved.


import sys
import optparse 
import os
import pdb
import csv

#############
# CONSTANTS #
#############
DIFF_WT_MT_RANK = 5.0
#################
# END CONSTANTS #
#################


###########
# CLASSES #
###########
class OptionParser(optparse.OptionParser):
    """
    Adding a method for required arguments.
    Taken from:
    http://www.python.org/doc/2.3/lib/optparse-extending-examples.html
    """
    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            print "%s option not supplied" % option
            self.print_help()
            sys.exit(1)


###############
# END CLASSES #
###############
 
########
# MAIN #	
########
def main():
	
    opt_parser = OptionParser()
   
    # Add Options. Required options should have default=None
    opt_parser.add_option("-i",
                          dest="input_table",
                          type="string",
                          help="""Input table with mutation impact comparison
                                  pvals""",
                          default=None)
    opt_parser.add_option("-o",
                          dest="output_table",
                          type="string",
                          help="""Output table with mutation impact predictions
                                  based on different methods""",
                          default=None)
#   opt_parser.add_option("--robustness_thresh",
#                         dest="robust_thresh",
#                         type="float",
#                         help="P-value threshould for robustness",
#                         default=None)
    opt_parser.add_option("--conn_thresh",
                          dest="conn_thresh",
                          type="float",
                          help="P-value threshould for connectivity vs null.",
                          default=None)
    opt_parser.add_option("--mut_wt_rep_thresh",
                          dest="mut_wt_thresh",
                          type="float",
                          help="""P-value threshould for comparison of WT and mut
                                  robustness""",
                          default=None)
    opt_parser.add_option("--mut_wt_rep_rank_diff",
                          dest="mut_wt_rep_diff",
                          type="float",
                          help="""The minimum difference in median rankpoint
                                  between WT and mut to consider a difference.
                                  DEF=%d""" % DIFF_WT_MT_RANK,
                          default=DIFF_WT_MT_RANK)
    opt_parser.add_option("--disting_thresh",
                          dest="disting_thresh",
                          type="float",
                          help="""P-value threshould that tests if mut and wt reps
                                  are indistinguishable from each other""",
                          default=None)
#   opt_parser.add_option("--robustness_rank",
#                         dest="robust_rank",
#                         type="float",
#                         help="Rankpoint threshold for robustness.",
#                         default=None)
#   opt_parser.add_option("--conn_rank",
#                         dest="conn_rank",
#                         type="float",
#                         help="Rankpoint threshold for connectivity.",
#                         default=None)
    opt_parser.add_option("--conn_null_med",
                          dest="conn_null_med",
                          type="float",
                          help="Median of null connectivity distribution.",
                          default=None)
    opt_parser.add_option("--use_c_pval",
                          dest="use_c_pval",
                          action="store_true",
                          help="Will use corrected p-value instead of raw p-val",
                          default=False)

    (options, args) = opt_parser.parse_args()
	
    # validate the command line arguments
    opt_parser.check_required("-i")
    opt_parser.check_required("-o")
#   opt_parser.check_required("--robustness_thresh")
#   opt_parser.check_required("--conn_thresh")
    opt_parser.check_required("--mut_wt_rep_thresh")
    opt_parser.check_required("--disting_thresh")
#    opt_parser.check_required("--robustness_rank")
#    opt_parser.check_required("--conn_rank")
    opt_parser.check_required("--conn_null_med")

    input_table = open(options.input_table)
    output = open(options.output_table, "w")

#   r_thresh = options.robust_thresh 
    c_thresh = options.conn_thresh 
    mut_wt_thresh = options.mut_wt_thresh
    disting_thresh = options.disting_thresh

    mut_wt_rep_diff = options.mut_wt_rep_diff

    use_c_pval = options.use_c_pval

#   r_rank = options.robust_rank
#   c_rank = options.conn_rank

    conn_null_med = options.conn_null_med

    file_reader = csv.DictReader(input_table, delimiter="\t")

    column_headers = ["gene",
                      "mut",
                      "mut_rep",
                      "wt_rep",
                      "mut_wt_connectivity",
                      "wt",
                      "cell_line",
                      "mut_rep_null_pval",
                      "wt_rep_null_pval",
                      "mut_wt_rep_pval",
                      "mut_wt_conn_null_pval",
                      "wt_mut_rep_vs_wt_mut_conn_pval",
                      "mut_rep_null_c_pval",
                      "wt_rep_null_c_pval",
                      "mut_wt_rep_c_pval",
                      "mut_wt_conn_null_c_pval",
                      "wt_mut_rep_vs_wt_mut_conn_c_pval",
                      "prediction"]

# The prediction is based off of Scenario_7_decision_tree_COF

#                     "Scenario_1__90rankpt_thresh",
#                     "Scenario_2__rankpt_thresh",
#                     "Scenario_3__pval_thresh",
#                     "Scenario_4__diff_robust",
#                     "Scenario_5__diff_robust_decision_tree",
#                     "Scenario_6__decision_tree_swap",
#                     "Scenario_7__decision_tree_COF"]

    file_writer = csv.DictWriter(output, delimiter="\t",
                                 fieldnames=column_headers)
    file_writer.writeheader()

    for row in file_reader:
        if use_c_pval:
            row["prediction"] = get_prediction_6(float(row["wt_rep"]),
                                                                 float(row["mut_rep"]),
                                                                 float(row["mut_wt_rep_c_pval"]),
                                                                 float(row["mut_wt_connectivity"]),
                                                                 float(row["mut_wt_conn_null_c_pval"]),
                                                                 float(row["wt_mut_rep_vs_wt_mut_conn_c_pval"]),
                                                                 mut_wt_thresh,
                                                                 mut_wt_rep_diff,
                                                                 c_thresh, 
                                                                 disting_thresh,
                                                                 conn_null_med)
        else:
            row["prediction"] = get_prediction_6(float(row["wt_rep"]),
                                                                 float(row["mut_rep"]),
                                                                 float(row["mut_wt_rep_pval"]),
                                                                 float(row["mut_wt_connectivity"]),
                                                                 float(row["mut_wt_conn_null_pval"]),
                                                                 float(row["wt_mut_rep_vs_wt_mut_conn_pval"]),
                                                                 mut_wt_thresh,
                                                                 mut_wt_rep_diff,
                                                                 c_thresh, 
                                                                 disting_thresh,
                                                                 conn_null_med)

        file_writer.writerow(row)

    input_table.close()
    output.close()

			
    sys.exit(0)

############
# END_MAIN #
############

#############
# FUNCTIONS #
#############
def formatDir(i_dir):
    i_dir = os.path.realpath(i_dir)
    if i_dir.endswith("/"):
        i_dir = i_dir.rstrip("/")
    return i_dir

def formatLine(line):
    line = line.replace("\r","")
    line = line.replace("\n","")
    return line

def get_prediction_1(wt_rep, mut_rep, mut_wt_conn, r_rank, c_rank):
    """
    WT and mut replicate robustness compared using a user-specified rankpoint
    threshold

    Also, mut-wt connectivity is compared when WT and mut are robust
    """
    if wt_rep < r_rank and mut_rep < r_rank:
        return "NI"

    if wt_rep >= r_rank and mut_rep < r_rank:
        return "LOF"

    if wt_rep >= r_rank and mut_rep >= r_rank and mut_wt_conn >= c_rank:
        return "Inert"

    if wt_rep < r_rank and mut_rep >= r_rank:
        return "GOF"

    if wt_rep >= r_rank and mut_rep >= r_rank and mut_wt_conn < c_rank:
        return "GOF"

def get_prediction_2(wt_rep_null_pval, mut_rep_null_pval, mut_wt_conn_null_pval,
                     mut_wt_conn, r_thresh, c_thresh):
    """
    Similar to prediction 1, but using p-value against a null, instead of
    rankpoint thresholds
    """

    if wt_rep_null_pval >= r_thresh and mut_rep_null_pval >= r_thresh:
        return "NI"

    if wt_rep_null_pval < r_thresh and mut_rep_null_pval >= r_thresh:
        return "LOF"    

    if wt_rep_null_pval < r_thresh and mut_rep_null_pval < r_thresh and mut_wt_conn_null_pval < c_thresh:
        if mut_wt_conn >= 0: 
            return "Inert"
        else:
            return "GOF"

    if wt_rep_null_pval >= r_thresh and mut_rep_null_pval < r_thresh:
        return "GOF"

    if wt_rep_null_pval < r_thresh and mut_rep_null_pval < r_thresh and mut_wt_conn_null_pval >= c_thresh:
        return "GOF"

def get_prediction_3(wt_rep, mut_rep, mut_wt_rep_pval, mut_wt_conn, mut_wt_conn_pval,
                     mut_wt_thresh, mut_wt_rep_diff, c_thresh):
    """
    Instead of checking against a null, a difference in the robustness is used
    """
    if mut_wt_rep_pval < mut_wt_thresh:
        if wt_rep < mut_rep:
            if mut_rep - wt_rep >= mut_wt_rep_diff:
                return "GOF"
        elif wt_rep > mut_rep:
            if wt_rep - mut_rep >= mut_wt_rep_diff:
                return "LOF"

    if mut_wt_conn_pval < c_thresh:
        if mut_wt_conn > 0:
            return "Inert"
        else:
            return "GOF"
    else:
        return "NI"

def get_prediction_4(wt_rep, mut_rep, mut_wt_rep_pval,
                     mut_wt_conn, mut_wt_conn_pval, disting_pval,
                     mut_wt_thresh, mut_wt_rep_diff, c_thresh, disting_thresh):

    if mut_wt_rep_pval < mut_wt_thresh:
        if wt_rep < mut_rep:
            if mut_rep - wt_rep >= mut_wt_rep_diff:
                return "GOF"
        elif wt_rep > mut_rep:
            if wt_rep - mut_rep >= mut_wt_rep_diff:
                return "LOF"

    if mut_wt_conn_pval < c_thresh:
        if mut_wt_conn >= 0:
            if disting_pval < disting_thresh:
                return "COF"
            else:
                return "Inert"
        else:
            return "GOF" 
    else:
        return "NI"

def get_prediction_5(wt_rep, mut_rep, mut_wt_rep_pval, 
                     mut_wt_conn, mut_wt_conn_pval, disting_pval,
                     mut_wt_thresh, mut_wt_rep_diff, c_thresh, disting_thresh):

    if mut_wt_rep_pval < mut_wt_thresh:
        if wt_rep < mut_rep:
            if mut_rep - wt_rep >= mut_wt_rep_diff:
                return "GOF"
        elif wt_rep > mut_rep:
            if wt_rep - mut_rep >= mut_wt_rep_diff:
                return "LOF"

    if disting_pval < disting_thresh:
        return "COF"

    if mut_wt_conn_pval < c_thresh:
        return "Inert"

    return "NI"   
 
def get_prediction_6(wt_rep, mut_rep, mut_wt_rep_pval, 
                     mut_wt_conn, mut_wt_conn_pval, disting_pval,
                     mut_wt_thresh, mut_wt_rep_diff, c_thresh, disting_thresh,
                     conn_null_med):

    if disting_pval < disting_thresh:
        if max_diff(wt_rep, mut_rep, mut_wt_conn) < mut_wt_rep_diff:
            if mut_wt_conn_pval < c_thresh:
                return "Inert"
            else:
                return "Error"

        if mut_wt_conn_pval < c_thresh:
            if mut_wt_conn < conn_null_med:
                return "DOM-NEG"

        if mut_wt_rep_pval < mut_wt_thresh:
            if wt_rep < mut_rep:
                if mut_rep - wt_rep >= mut_wt_rep_diff:
                    return "GOF"
                else:
                    return "COF"
            elif wt_rep > mut_rep:
                if wt_rep - mut_rep >= mut_wt_rep_diff:
                    return "LOF"
                else:
                    return "COF"
            else:
                return "COF"
        else:
            return "COF"

    if mut_wt_conn_pval < c_thresh:
        return "Inert"

    return "NI"   

def max_diff(wt_rep, mut_rep, mut_wt_conn):
    max_diff = abs(wt_rep - mut_rep)

    wt_conn_diff = abs(wt_rep - mut_wt_conn)
    if wt_conn_diff > max_diff:
        max_diff = wt_conn_diff

    mut_conn_diff = abs(mut_rep - mut_wt_conn)
    if mut_conn_diff > max_diff:
        max_diff = mut_conn_diff

    return max_diff
#################
# END FUNCTIONS #	
#################	
if __name__ == "__main__": main()