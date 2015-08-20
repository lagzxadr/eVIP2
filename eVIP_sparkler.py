#!/broad/software/free/Linux/redhat_5_x86_64/pkgs/python_2.5.4/bin/python
# mutation_impact_viz.py 
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
import random
import math

from eVIP_compare import getSelfConnectivity, getConnectivity
from eVIP_predict import max_diff

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.markers as mmarkers
from matplotlib.colors import colorConverter
import numpy as np
import scipy.spatial.distance as distance
import scipy.cluster.hierarchy as sch

import cmap.io.gct as gct

#############
# CONSTANTS #
#############
DIFF_THRESH = 5
INFINITY = 10
DEF_PRED_COL = "prediction"

#RGB CODES
#GOF_COL = "#e31a1c"
GOF_COL = colorConverter.to_rgba("#ca0020", 1)
COF_PLUS_COL = colorConverter.to_rgba("#c2a5cf", 1)
COF_COL = colorConverter.to_rgba("#6a3d9a", 1)
COF_MINUS_COL = colorConverter.to_rgba("#c2a5cf", 1)
#LOF_COL = "#1f78b4"
LOF_COL = colorConverter.to_rgba("#0571b0", 1)
EQ_COL = colorConverter.to_rgba("#5aae61", 1)
INERT_COL = colorConverter.to_rgba("#000000", 1) 
NI_COL = colorConverter.to_rgba("#ffffff", 1) 

MAIN_MARKER = 'o'
NEG_MARKER = 'x'


XMIN=0
XMAX=4
YMIN=-3
YMAX=3

MARKER_SIZE= 300
SPARKLER_LINEWIDTH = 3
ALL_SPARKLER_LINEWIDTH = 2

THRESH_LS = "dotted"
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
    opt_parser.add_option("--pred_file",
                          dest="pred_file",
                          type="string",
                          help="""File containing the mutation impact
                                  predictions""",
                          default=None)
#   opt_parser.add_option("--col",
#                         dest="pred_col",
#                         type="string",
#                         help="""Prediciton files have predictions based on
#                                 multiple scenarios. The scenario needs to be
#                                 specified because figures will be plotted in
#                                 the order of GOF, LOF, COF,Inert, NI calls. This
#                                 specifies the name of the column that contains
#                                 the prediction. DEF=%s""" % DEF_PRED_COL,
#                         default=DEF_PRED_COL)
#   opt_parser.add_option("--sig_info",
#                         dest="sig_info",
#                         type="string",
#                         help="""sig info file with gene information and distil
#                                 information""",
#                         default=None)
#   opt_parser.add_option("--gctx",
#                         dest="gctx",
#                         type="string",
#                         help="GCTX file with rankpoint correlations",
#                         default=None)
#   opt_parser.add_option("--null_conn",
#                         dest="null_conn",
#                         type="string",
#                         help="""File of null connectivity values. This file is
#                                 given as output from
#                                 mutation_impact_pvals.py""",
#                         default=None)
    opt_parser.add_option("--ref_allele_mode",
                          dest="ref_allele_mode",
                          action="store_true",
                          help="""Instead of organizing plots by gene, will use
                                  the wt column to determine what are the
                                  reference alleles.""",
                          default=False)
    opt_parser.add_option("--thresh",
                          dest="thresh",
                          type="float",
                          help="-log10(P) threshold of significance",
                          default=None)
    opt_parser.add_option("--use_c_pval",
                          dest="use_c_pval",
                          action="store_true",
                          help="Use corrected p-val instead of raw p-val",
                          default=False)
#   opt_parser.add_option("--col",
#                         dest="pred_col",
#                         type="string",
#                         help="""Prediciton files have predictions based on
#                                 multiple scenarios. The scenario needs to be
#                                 specified because figures will be plotted in
#                                 the order of GOF, LOF, COF,Inert, NI calls.
#his
#                                 specifies the name of the column that contains
#                                 the prediction. DEF=%s""" % DEF_PRED_COL,
#                         default=DEF_PRED_COL)
    opt_parser.add_option("--annotate",
                          dest="annotate",
                          action="store_true",
                          help="Will add allele labels to points.",
                          default=False)
    opt_parser.add_option("--by_gene_color",
                          dest="by_gene_color",
                          type="string",
                          help="""File containing labels and colors for
                                  gene-cenric plot""",
                          default=None)
    opt_parser.add_option("--out_dir",
                          dest="out_dir",
                          type="string",
                          help="Output directory to put figures",
                          default=None)
    opt_parser.add_option("--pdf",
                          dest="pdf",
                          action="store_true",
                          help="Will print plots in pdf format instead of png",
                          default=False)
    opt_parser.add_option("--xmin",
                          dest="xmin",
                          type="float",
                          help="Min value of x-axis. DEF=%d" % XMIN,
                          default=XMIN)
    opt_parser.add_option("--xmax",
                          dest="xmax",
                          type="float",
                          help="Max value of x-axis. DEF=%d" % XMAX,
                          default=XMAX)
    opt_parser.add_option("--ymin",
                          dest="ymin",
                          type="float",
                          help="Min value of y-axis. DEF=%d" % YMIN,
                          default=YMIN)
    opt_parser.add_option("--ymax",
                          dest="ymax",
                          type="float",
                          help="Max value of y-axis. DEF=%d" % YMAX,
                          default=YMAX)

    (options, args) = opt_parser.parse_args()
	
    # validate the command line arguments
    opt_parser.check_required("--pred_file")
    opt_parser.check_required("--thresh")
#    opt_parser.check_required("--sig_info")
#   opt_parser.check_required("--gctx")
#   opt_parser.check_required("--null_conn")
    opt_parser.check_required("--out_dir")

    pred_file = open(options.pred_file)
#    pred_col = options.pred_col
    if options.pdf:
        format = "pdf"   
    else:
        format = "png"

    if os.path.exists(options.out_dir):
        out_dir = os.path.abspath(options.out_dir)
    else:
        os.mkdir(options.out_dir)
        out_dir = os.path.abspath(options.out_dir)
        print "Creating output directory: %s" % out_dir 

    thresh = options.thresh
    annotate = options.annotate
    pred_col = DEF_PRED_COL 
    ref_allele_mode = options.ref_allele_mode

    use_c_pval = options.use_c_pval

    xmin = options.xmin
    xmax = options.xmax
    ymin = options.ymin
    ymax = options.ymax

    gene2type = None
    if options.by_gene_color:
        gene2type = parseGeneColor(options.by_gene_color)

#    sig_info = open(options.sig_info)

#    null_conn = getNullConnDist(options.null_conn)

#   this_gctx = gct.GCT(options.gctx)
#   this_gctx.read()

    # Process predictions
    # allele2pvals = {allele:[mut vs wt pval, 
    #                         wt vs mut-wt pval,
    #                         mut-wt conn pval]                            
    (gene2mut_wt,
     gene2mut_wt_rep_p,
     gene2neg_log_p,
     gene2diff_score,
     gene2allele,
     gene2col,
     gene_type2pred2count,
     gene2markerstyle) = parse_pred_file(pred_file, thresh, pred_col, use_c_pval, gene2type, ref_allele_mode)

    # Print out gene type and prediction counts
    for gene_type in gene_type2pred2count:
        print "###%s###" % gene_type
        for pred in gene_type2pred2count[gene_type]:
            print "%s\t%s" % (pred, gene_type2pred2count[gene_type][pred])

    all_mut_wt = []   
    all_mut_wt_rep_p = []   
    all_neg_log_p = []
    all_col = []
    all_diff_score = []
    all_markerstyle = []

    gene_type2data = {"ONC":{"mut_wt":[],
                             "mut_wt_rep_p":[],
                             "neg_log_p":[],
                             "markerstyle":[],
                             "col":[]},
                      "TSG":{"mut_wt":[],
                             "mut_wt_rep_p":[],
                             "neg_log_p":[],
                             "markerstyle":[],
                             "col":[]},
                      "TSG_noTP53":{"mut_wt":[],
                                    "mut_wt_rep_p":[],
                                    "neg_log_p":[],
                                    "markerstyle":[],
                                    "col":[]},
                      "ONC-NEG":{"mut_wt":[],
                                "mut_wt_rep_p":[],
                                 "neg_log_p":[],
                                 "markerstyle":[],
                                 "col":[]}}

    for gene in gene2allele:

        this_fig = plt.figure()
        ax=this_fig.add_subplot(111)

#        plt.axhline(y=0, color="grey")

        all_mut_wt.extend(gene2mut_wt[gene])
        all_mut_wt_rep_p.extend(gene2mut_wt_rep_p[gene])
        all_neg_log_p.extend(gene2neg_log_p[gene])
        all_col.extend(gene2col[gene])
        all_diff_score.extend(gene2diff_score[gene])
        all_markerstyle.extend(gene2markerstyle[gene])

        if gene not in gene2type:
            gene2type[gene] = "UNKN"

        # Add to gene-type specific plot data
        for gene_type in gene_type2data:
            gene_type2data[gene_type]["mut_wt"].extend(gene2mut_wt[gene])
            gene_type2data[gene_type]["mut_wt_rep_p"].extend(gene2mut_wt_rep_p[gene])
            gene_type2data[gene_type]["neg_log_p"].extend(gene2neg_log_p[gene])
            gene_type2data[gene_type]["markerstyle"].extend(gene2markerstyle[gene])

            gene_root = gene.split("_")[0]
            if gene_type == "TSG_noTP53":
                if gene2type[gene_root] == "TSG" and gene != "TP53":
                    gene_type2data[gene_type]["col"].extend(gene2col[gene])
                else:
                    gene_type2data[gene_type]["col"].extend(makeGrey(gene2col[gene]))
            else:
                if gene2type[gene_root] == gene_type:
                    gene_type2data[gene_type]["col"].extend(gene2col[gene])
                else:
                    gene_type2data[gene_type]["col"].extend(makeGrey(gene2col[gene]))
    
#       # TSG no TP53
#       tsg_noTP53__mut_wt.extend(gene2mut_wt[gene])
#       tsg_noTP53_neg_log_p.extend(gene2neg_log_p[gene])
#       if gene2type[gene] == "TSG" and gene != "TP53":
#           tsg_noTP53_col.extend(gene2col[gene])
#       else:
#           tsg_noTP53_col.extend(makeGrey(gene2col[gene]))

        (main_markers,        
         neg_markers) = split_data(gene2markerstyle[gene],
                                   gene2neg_log_p[gene],
                                   gene2mut_wt_rep_p[gene],
                                   gene2col[gene])

        plt.scatter(main_markers["x"],
                    main_markers["y"],
                    s = MARKER_SIZE,
                    c=main_markers["col"],
                    marker=MAIN_MARKER,
                    edgecolors="none",
                    linewidth=0)

        plt.scatter(neg_markers["x"],
                    neg_markers["y"],
                    s = MARKER_SIZE,
                    c=neg_markers["col"],
                    marker=NEG_MARKER,
                    linewidth=4)
 
#       plt.scatter(gene2neg_log_p[gene],
#                    gene2mut_wt[gene],
#                   gene2mut_wt_rep_p[gene],
#                     s=gene2diff_score[gene],
#                   s=75,
#                   c=gene2col[gene],
#                    marker=gene2markerstyle[gene],
#                   marker=mmarkers.MarkerStyle(np.array(gene2markerstyle[gene])),
#                   linewidths=0)
#                    alpha=0.5)

        for i in range(len(gene2neg_log_p[gene])):
            this_col = gene2col[gene][i]
            if this_col == colorConverter.to_rgba("#ffffff", 1): # white
                this_col = "black" 
            plt.plot([0, gene2neg_log_p[gene][i]],
                     [0, gene2mut_wt_rep_p[gene][i]],
#                     [0, gene2mut_wt[gene][i]],
                     color=this_col,
                     linewidth=SPARKLER_LINEWIDTH)
        # Add lines
#       for i in range(len(gene2diff_score[gene])):
#           this_col = gene2col[gene][i]
#           if this_col == "white":
#               this_col = "black" 
#           plt.plot([0, gene2diff_score[gene][i]],
#                    [0, gene2neg_log_p[gene][i]],
#                    color=this_col)
#                     marker="-")

#       scatter_points = plt.scatter(gene2diff_score[gene],
#                   gene2neg_log_p[gene],
#                   s=75,
#                   c=gene2col[gene])
#                    alpha=0.5)


        if annotate:
            for i in range(len(gene2allele[gene])):
                ax.annotate(gene2allele[gene][i],
                            (gene2neg_log_p[gene][i],
                             gene2mut_wt_rep_p[gene][i]),
#                             gene2mut_wt[gene][i]),
                            textcoords='data')
#               ax.annotate(gene2allele[gene][i],
#                           (gene2diff_score[gene][i],
#                            gene2neg_log_p[gene][i]),
#                           textcoords='data')

        plt.axvline(x=thresh, color="grey", ls = THRESH_LS)
#        plt.axvline(x=5, color="grey", ls = 'dashed')
#        plt.axhline(y=thresh, color="grey", ls = THRESH_LS)  
#        plt.axhline(y=-thresh, color="grey", ls = THRESH_LS)

        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
#       plt.xlim(0, 200)
#       plt.ylim(-8, 8)

#        ax.set_ylabel("MUT-WT robustness")
        if use_c_pval:
            ax.set_xlabel("-log10(corrected p-val)")
        else:
            ax.set_xlabel("-log10(p-val)")
        ax.set_ylabel("impact direction score")
#        ax.set_ylabel("log10(MUT vs WT robust p-val) (-, if MUT robust < WT robust)")
#        ax.set_ylabel("log10(p-val) (-, if MUT robust < WT robust)")
#       ax.set_ylabel("-log10(p-val)")
#       ax.set_xlabel("difference score")

#       ax.set_yticklabels(["4","3", "2", "1","0",
#                       "1", "2", "3", "4"])
#       ax.set_yticklabels(["8","6", "4", "2", "0",
#                          "2", "4", "6","8"])
        ax.text(100, -7, "MUT robustness < WT robustness", fontsize="small",
                ha="center")
        ax.text(100, 7, "MUT robustness > WT robustness", fontsize="small",
                ha="center")

        # make legend
#       predictions = ["GOF", "LOF", "COF-Likely GOF", "COF-Likely LOF", "Inert", "NI"]
#       colors = [GOF_COL, LOF_COL, COF_PLUS_COL, COF_MINUS_COL, "black","white"]
        predictions = ["GOF", "LOF", "COF", "Inert"]
        colors = [GOF_COL, LOF_COL, COF_COL, "black"]

        recs = []
        for i in range(len(colors)):
            recs.append(mpatches.Rectangle((0,0),1,1,fc=colors[i]))

#       plt.legend(recs, predictions, loc="lower right", fontsize='xx-small',
#                  title="prediction")

        # DOM NEG symbol

        
        this_fig.savefig("%s/%s_spark_plots.%s" % (out_dir, gene, format),
                         format=format)

        plt.close(this_fig)


    # GENE-TYPE plots
    for legend_flag in ["legend_on", "legend_off"]:    
        for gene_type in gene_type2data:
            this_fig = plt.figure()
            ax = this_fig.add_subplot(111)

#            plt.axhline(y=0, color="grey")

            # Add lines
            for i in range(len(gene_type2data[gene_type]["mut_wt"])):
                this_col = gene_type2data[gene_type]["col"][i]
                if this_col == colorConverter.to_rgba("#ffffff", 1): # white
                    this_col = INERT_COL
                plt.plot([0, gene_type2data[gene_type]["neg_log_p"][i]],
                         [0, gene_type2data[gene_type]["mut_wt_rep_p"][i]],
#                         [0, gene_type2data[gene_type]["mut_wt"][i]],
                         color=this_col,
#                         alpha=0.5,
                         linewidth=SPARKLER_LINEWIDTH)
                
            (main_markers,        
            neg_markers) = split_data(gene_type2data[gene_type]["markerstyle"],
                                      gene_type2data[gene_type]["neg_log_p"],
                                      gene_type2data[gene_type]["mut_wt_rep_p"],
                                      gene_type2data[gene_type]["col"])

            plt.scatter(main_markers["x"],
                        main_markers["y"],
                        s = MARKER_SIZE,
                        c=main_markers["col"],
                        marker=MAIN_MARKER,
                        edgecolors="none",
                        linewidth=0)

            plt.scatter(neg_markers["x"],
                        neg_markers["y"],
                        s = MARKER_SIZE,
                        c=neg_markers["col"],
                        marker=NEG_MARKER,
                        linewidth=4)

#           plt.scatter(gene_type2data[gene_type]["neg_log_p"],
#                       gene_type2data[gene_type]["mut_wt_rep_p"],
#                        gene_type2data[gene_type]["mut_wt"],
#                       s=75,
#                       c=gene_type2data[gene_type]["col"],
#                       marker=gene_type2data[gene_type]["markerstyle"],
#                        marker=mmarkers.MarkerStyle(gene_type2data[gene_type]["markerstyle"]),
#                       linewidths=0)

            plt.axvline(x=thresh, color="grey", ls = THRESH_LS)
#            plt.axhline(y=thresh, color="grey", ls = THRESH_LS)  
#            plt.axhline(y=-thresh, color="grey", ls = THRESH_LS)

            plt.xlim(xmin, xmax)
            plt.ylim(ymin, ymax)

            if use_c_pval:
                ax.set_xlabel("-log10(corrected p-val)")
            else:
                ax.set_xlabel("-log10(p-val)")
            ax.set_ylabel("impact direction score")
#            ax.set_ylabel("MUT-WT robustness")
#            ax.set_ylabel("log10(MUT vs WT robust p-val) (-, if MUT robust < WT robust)")
            
#           ax.set_yticklabels(["4","3", "2", "1","0",
#                               "1", "2", "3", "4"])
#           ax.set_yticklabels(["8","6", "4", "2", "0",
#                              "2", "4", "6","8"])
            ax.text(100, -7, "MUT robustness < WT robustness", fontsize="small",
                    ha="center")
            ax.text(100, 7, "MUT robustness > WT robustness", fontsize="small",
                    ha="center")

            if legend_flag == "legend_on":
                plt.legend(recs, predictions, loc="lower right", fontsize='xx-small',
                           title="prediction")

            this_fig.savefig("%s/%s_spark_plots_%s.%s" % (out_dir, 
                                                       gene_type,
                                                       legend_flag,
                                                       format), format=format)

            plt.close(this_fig)

    # final plot
    this_fig = plt.figure()
    ax=this_fig.add_subplot(111)

    # Add lines
    for i in range(len(all_diff_score)):
        this_col = all_col[i]
        if this_col == "white":
            this_col = "black" 
        plt.plot([0, all_neg_log_p[i]],
                 [0, all_mut_wt_rep_p[i]],
#                 [0, all_mut_wt[i]],
                 color=this_col,
                 alpha=0.25,
                 linewidth=ALL_SPARKLER_LINEWIDTH)
    
#       plt.plot([0, all_diff_score[i]],
#                [0, all_neg_log_p[i]],
#                color=this_col)
#   
#   plt.scatter(all_diff_score,
#               all_neg_log_p,
#                s=all_diff_score,
#                s=75,
#               c=all_col)
#                alpha=0.5)
    
    (main_markers,        
     neg_markers) = split_data(all_markerstyle,
                               all_neg_log_p,
                               all_mut_wt_rep_p,
                               all_col)

    plt.scatter(main_markers["x"],
                main_markers["y"],
                s = MARKER_SIZE,
                c=main_markers["col"],
                marker=MAIN_MARKER,
                edgecolors="none",
                linewidth=0)

    plt.scatter(neg_markers["x"],
                neg_markers["y"],
                s = MARKER_SIZE,
                c=neg_markers["col"],
                marker=NEG_MARKER,
                linewidth=4)

#   plt.scatter(all_neg_log_p,
#               all_mut_wt_rep_p,
#                all_mut_wt,
#               s=75,
#               c=all_col,
#               marker=all_markerstyle,
#                marker=mmarkers.MarkerStyle(all_markerstyle),
#               linewidths=0)

#    plt.axvline(x=5, color="grey", ls = 'dashed')
#    plt.axhline(y=0, color="grey")
    plt.axvline(x=thresh, color="grey", ls = THRESH_LS)
#    plt.axhline(y=thresh, color="grey", ls = THRESH_LS)
#    plt.axhline(y=-thresh, color="grey", ls = THRESH_LS)

#   plt.xlim(0, 200)
#   plt.ylim(-8, 8)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

#   ax.set_ylabel("-log10(p-val)")
#   ax.set_xlabel("difference score")
    if use_c_pval:
        ax.set_xlabel("-log10(corrected p-val)")
    else:
        ax.set_xlabel("-log10(p-val)")
    ax.set_ylabel("impact direction score")
#    ax.set_ylabel("MUT-WT robustness")

#    ax.set_ylabel("log10(MUT vs WT robust p-val) (-, if MUT robust < WT robust)")

#   ax.set_yticklabels(["4","3", "2", "1","0",
#                       "1", "2", "3", "4"])
#   ax.set_yticklabels(["8","6", "4", "2", "0",
#                       "2", "4", "6","8"])
#   ax.text(100, -7, "MUT robustness < WT robustness", fontsize="small",
#           ha="center")
#   ax.text(100, 7, "MUT robustness > WT robustness", fontsize="small",
#           ha="center")

#   plt.legend(recs, predictions, loc="lower right", fontsize='xx-small',
#                  title="prediction")

    this_fig.savefig("%s/all_spark_plots.%s" % (out_dir, format), format=format)

    plt.close(this_fig)
                    
    sys.exit(0)

############
# END_MAIN #
############

#############
# FUNCTIONS #
#############
def formatAllele(allele):
    allele_elems = allele.split(".")[1:]

    return ".".join(allele_elems)

def formatDir(i_dir):
    i_dir = os.path.realpath(i_dir)
    if i_dir.endswith("/"):
        i_dir = i_dir.rstrip("/")
    return i_dir

def formatLine(line):
    line = line.replace("\r","")
    line = line.replace("\n","")
    return line

def getNegLog10(p_val):
    if p_val == 0.0:
        return INFINITY

    return -math.log(p_val, 10)
    
def makeGrey(col_list):
    return [colorConverter.to_rgba("#cccccc", 0.1) for i in range(len(col_list))]

def parseGeneColor(by_gene_color_file_name):
    """
    Returns
    gene2label 
    """
    gene_file = open(by_gene_color_file_name)
    
    gene2label = {}

    csv_reader = csv.DictReader(gene_file, delimiter="\t")
    for row in csv_reader:
        gene2label[row["gene"]] = row["label"]
        
    return gene2label

def parse_pred_file(pred_file, thresh, pred_col, use_c_pval, gene2type, ref_allele_mode):
    """
    (gene2mut_wt,
     gene2mut_wt_rep_p,
     gene2neg_log_p,
     gene2diff_score,
     gene2allele,
     gene2col,
     gene2markerstyle)
    """
    csv_reader = csv.DictReader(pred_file, delimiter="\t")

    gene2mut_wt = {}
    gene2mut_wt_rep_p = {}
    gene2neg_log_p = {}
    gene2diff_score = {}
    gene2allele= {}
    gene2col = {}
    gene2markerstyle = {}

    gene_type2pred2count = {"ONC":{},
                            "TSG":{},
                            "TSG_noTP53":{},
                            "ONC-NEG":{}}

    for gene_type in gene_type2pred2count:
        gene_type2pred2count[gene_type]["GOF"] = 0
        gene_type2pred2count[gene_type]["LOF"] = 0
        gene_type2pred2count[gene_type]["COF"] = 0
        gene_type2pred2count[gene_type]["DOM-NEG"] = 0
        gene_type2pred2count[gene_type]["Inert"] = 0

    for row in csv_reader:   
        gene = row["gene"] 
        wt_ref = row["wt"]
        allele = row["mut"]
        mut_rep = float(row["mut_rep"])
        wt_rep = float(row["wt_rep"])
        pred = row[pred_col]

        # Skip NI
        if pred == "NI":
            continue
    
        if ref_allele_mode:
            gene = wt_ref

        mut_wt_conn = float(row["mut_wt_connectivity"])
        if use_c_pval:
            mut_wt_rep_pval = getNegLog10(float(row["mut_wt_rep_c_pval"]))
            mut_wt_conn_pval = getNegLog10(float(row["mut_wt_conn_null_c_pval"]))
            impact_pval = getNegLog10(float(row["wt_mut_rep_vs_wt_mut_conn_c_pval"]))
        else:
            mut_wt_rep_pval = getNegLog10(float(row["mut_wt_rep_pval"]))
            mut_wt_conn_pval = getNegLog10(float(row["mut_wt_conn_null_pval"]))
            impact_pval = getNegLog10(float(row["wt_mut_rep_vs_wt_mut_conn_pval"]))

        # Update prediction count
        if pred != "NI":
            gene_root = gene.split("_")[0]
            if gene2type[gene_root] in gene_type2pred2count:
                this_type = gene2type[gene_root]
                if gene2type[gene_root] == "TSG":
                    if gene_root != "TP53":
                        gene_type2pred2count["TSG_noTP53"][pred] += 1
   
                gene_type2pred2count[this_type][pred] += 1


        # Initiatite dictionaries
        if gene not in gene2mut_wt:
            gene2mut_wt[gene] = []
            gene2mut_wt_rep_p[gene] = []
            gene2neg_log_p[gene] = []
            gene2diff_score[gene] = []
            gene2allele[gene] = []
            gene2col[gene] = []
            gene2markerstyle[gene] = []

        # Add allele
        gene2allele[gene].append(formatAllele(allele))

        # MUT - WT
        gene2mut_wt[gene].append(mut_rep - wt_rep)
    
        gene2neg_log_p[gene].append(impact_pval)

        if mut_rep >= wt_rep:
            gene2mut_wt_rep_p[gene].append(mut_wt_rep_pval)
        else:
            gene2mut_wt_rep_p[gene].append(-mut_wt_rep_pval)

#       if mut_rep >= wt_rep:
#           gene2neg_log_p[gene].append(impact_pval)
#       else: # mut_rep < wt_rep:
#           gene2neg_log_p[gene].append(-impact_pval)

        diff = max_diff(wt_rep, mut_rep, mut_wt_conn)
#        gene2diff_score[gene].append(20*2**(math.log(diff,2)))
        gene2diff_score[gene].append(diff)

        # Other features based on significance
        if pred == "GOF":
            gene2col[gene].append(GOF_COL)
            gene2markerstyle[gene].append(MAIN_MARKER)
        elif pred == "LOF":
            gene2col[gene].append(LOF_COL)
            gene2markerstyle[gene].append(MAIN_MARKER)
        elif pred == "Inert":
            gene2col[gene].append(INERT_COL)
            gene2markerstyle[gene].append(MAIN_MARKER)
        elif pred == "NI":
            gene2col[gene].append(NI_COL)
            gene2markerstyle[gene].append(MAIN_MARKER)
        elif pred == "COF":
            gene2col[gene].append(COF_COL)
            gene2markerstyle[gene].append(MAIN_MARKER)
        elif pred == "DOM-NEG":
            if mut_wt_rep_pval < thresh:
                gene2col[gene].append(COF_COL)
            else:
                if mut_rep >= wt_rep:
                    gene2col[gene].append(GOF_COL)
                else:
                    gene2col[gene].append(LOF_COL)
            gene2markerstyle[gene].append(NEG_MARKER)
#           if mut_rep > wt_rep:
#               gene2col[gene].append(COF_PLUS_COL)
#           elif mut_rep < wt_rep:
#               gene2col[gene].append(COF_MINUS_COL)
#           else: # mut_rep == wt_rep
#               gene2col[gene].append(EQ_COL)
        else:
            gene2col[gene].append("yellow")
            gene2markerstyle[gene].append(MAIN_MARKER)


#       if impact_pval > thresh:
#            gene2second_test_p[gene].append(np.pi * (5 * mut_wt_rep_pval)**2)
#           # Color based on GOF, LOF, COF
#           if mut_rep > wt_rep:
#               if mut_wt_rep_pval > thresh and (mut_rep - wt_rep) > DIFF_THRESH:
#                   gene2col[gene].append(GOF_COL)
#               else:
#                   gene2col[gene].append(COF_PLUS_COL)
#           elif wt_rep > mut_rep :
#               if mut_wt_rep_pval > thresh and (wt_rep - mut_rep) > DIFF_THRESH:
#                   gene2col[gene].append(LOF_COL)    
#               else:
#                   gene2col[gene].append(COF_MINUS_COL)    
#           else:
#               gene2col[gene].append(EQ_COL) 
#       else:        
#            gene2second_test_p[gene].append(np.pi * (2)
#           if mut_wt_conn_pval > thresh:
#               gene2col[gene].append("black")
#           else:
#               gene2col[gene].append("white")

    return gene2mut_wt, gene2mut_wt_rep_p, gene2neg_log_p, gene2diff_score, gene2allele, gene2col, gene_type2pred2count, gene2markerstyle

def split_data(marker_list, x_list, y_list, col_list):
    """
    Returns dictioaries for x, y, and colors
    """
    main_markers = {"x":[],
                    "y":[],
                    "col":[]}

    neg_markers = {"x":[],
                   "y":[],
                   "col":[]}

    for i in range(len(marker_list)):
        if marker_list[i] == MAIN_MARKER:
            main_markers["x"].append(x_list[i]) 
            main_markers["y"].append(y_list[i]) 
            main_markers["col"].append(col_list[i]) 
        else:
            neg_markers["x"].append(x_list[i]) 
            neg_markers["y"].append(y_list[i]) 
            neg_markers["col"].append(col_list[i]) 

    return main_markers, neg_markers
            

#################
# END FUNCTIONS #	
#################	
if __name__ == "__main__": main()