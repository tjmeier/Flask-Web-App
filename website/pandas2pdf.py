import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.backends.backend_pdf import PdfPages

def pandas2pdf(df, pdf_name):

    alternating_colors = ([['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df))[:len(df)]

    #https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
    fig, ax =plt.subplots(figsize=(11, 8.5))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,
                        rowColours=['lightblue']*len(df),
                        colColours=['lightblue']*len(df.columns),
                        cellColours=alternating_colors,
                        loc='center')

    #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
    pp = PdfPages(f"{pdf_name}.pdf")
    pp.savefig(dpi = 300, orientation = 'landscape', bbox_inches = 'tight')
    pp.close()