import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns 
import os 
from wquantiles import quantile

data_path = "C:/Users/veve1/OneDrive/Documents/ENSAE 3A/Memoire MiE/Data"
output_path = "C:/Users/veve1/OneDrive/Documents/ENSAE 3A/Memoire MiE/Output"

def graph_winners_losers(data,reform,elas_vect,bonus_cheques_uc):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    fig, ax = plt.subplots(figsize=(10, 7.5)) 
    if elas_vect == False :
        sns.barplot(x="niveau_vie_decile", y = 'Is_losers', data = data, hue = 'ref_elasticity', hue_order = hue_order , palette = sns.color_palette("Paired"), width = .9)
    else :
        sns.barplot(x="niveau_vie_decile", y = 'Is_losers', data = data, hue = 'ref_elasticity', hue_order= ['Douenne (2020)', 'Douenne (2020) vector'], palette = sns.color_palette("Paired"), width = .9) 
    plt.xlabel('Revenue decile', fontdict = {'fontsize' : 14})
    plt.ylabel('Share of net losers from the reform', fontdict = {'fontsize' : 14})
    plt.legend()

    y_max = 0.6
    ax.set_ylim(ymin = 0, ymax = y_max)
    plt.savefig(os.path.join(output_path,'Figures/Winners_losers_reform_{}_elas_vect_{}_bonus_cheques_uc_{}.png').format(reform.key[0],elas_vect,bonus_cheques_uc))    
    return

def graph_net_transfers(data,reform,elas_vect,bonus_cheques_uc):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    data = data[data['niveau_vie_decile'] != 'Total']
    fig, ax = plt.subplots(figsize=(10, 7.5)) 
    if elas_vect == False :
        sns.barplot(x="niveau_vie_decile", y = 'Net_transfers_reform', data = data, hue = 'ref_elasticity', hue_order = hue_order, palette = sns.color_palette("Paired"), width = .9)
    else :
        sns.barplot(x="niveau_vie_decile", y = 'Net_transfers_reform', data = data, hue = 'ref_elasticity', hue_order = ['Douenne (2020)' , 'Douenne (2020) vector'], palette = sns.color_palette("Paired"), width = .9)
    
    plt.xlabel('Revenue decile', fontdict = {'fontsize' : 14})
    plt.ylabel('Net transfers in euros', fontdict = {'fontsize' : 14})
    plt.legend()

    y_min, y_max = -12 , 17
    ax.set_ylim(ymin = y_min , ymax = y_max)
    plt.savefig(os.path.join(output_path,'Figures/Net_transfers_reform_{}_elas_vect_{}_bonus_cheques_uc_{}.png').format(reform.key[0],elas_vect,bonus_cheques_uc))
    return

def graph_effort_rate(data,reform,elas_vect,bonus_cheques_uc):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    fig, ax = plt.subplots(figsize=(10, 7.5)) 
    if elas_vect == False :
        sns.barplot(x="niveau_vie_decile", y = 'Effort_rate', data = data, hue = 'ref_elasticity', hue_order = hue_order, palette = sns.color_palette("Paired"), width = .9)
    else : 
        sns.barplot(x="niveau_vie_decile", y = 'Effort_rate', data = data, hue = 'ref_elasticity', hue_order = ['Douenne (2020)' , 'Douenne (2020) vector'], palette = sns.color_palette("Paired"), width = .9)
    
    plt.xlabel('Revenue decile', fontdict = {'fontsize' : 14})
    plt.ylabel('Additional taxes over disposable income', fontdict = {'fontsize' : 14})
    plt.legend()
    
    y_max = 0.2
    ax.set_ylim(ymin = 0 , ymax = y_max)
    plt.savefig(os.path.join(output_path,'Figures/Effort_rate_reform_{}_elas_vect_{}_bonus_cheques_uc_{}.png').format(reform.key[0],elas_vect,bonus_cheques_uc))
    return

def quantiles_for_boxplot(data,y):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    out = pd.DataFrame(data = {'niveau_vie_decile' : [] , 'ref_elasticity': [] , y : []})
    i_ref = 0
    data = data[data['ref_elasticity'].isin(hue_order)]
    for ref in hue_order:
        data_ref = data[data['ref_elasticity'] == ref]
        for decile in set(data_ref['niveau_vie_decile']):
            data_decile = data_ref[data_ref['niveau_vie_decile'] == decile]
            decile = decile + 0.7 + 0.1*i_ref  - 1
            for q in [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]:
                quantil = quantile(data_decile[y],data_decile['pondmen'],q)
                out = pd.concat([out,pd.DataFrame(data = {'niveau_vie_decile' : [decile] , 'ref_elasticity' : ref, y : [quantil], 'quantile' : [q]}),])
        i_ref +=1
    return out

def subtitle_legend_boxplots(ax, legend_format,markers):
    new_handles = []
    
    handles, labels = ax.get_legend_handles_labels()
    label_dict = dict(zip(labels, handles))
    
    #Means 2 labels were the same
    if len(label_dict) != len(labels):
        raise ValueError("Can not have repeated levels in labels!")
    
    for subtitle, level_order in legend_format.items():
        #Roll a blank handle to add in the subtitle
        blank_handle = matplotlib.patches.Patch(visible=False, label=subtitle)
        new_handles.append(blank_handle)
        
        for level in level_order:
            # If level is in the label_dict, it's a label-based level
            if level in label_dict:
                handle = label_dict[level]
                new_handles.append(handle)
            else:
                # If level is not a label, create a dummy handle with markers for percentiles
                percentile_index = legend_format['Percentiles'].index(level)
                marker = markers[percentile_index]
                percentile_handle = plt.Line2D([], [], linestyle='None', marker=marker, markersize=6, label=str(level),color = 'black')
                new_handles.append(percentile_handle)

    #Labels are populated from handle.get_label() when we only supply handles as an arg
    legend = ax.legend(handles=new_handles)

    #Turn off DrawingArea visibility to left justify the text if it contains a subtitle
    for draw_area in legend.findobj(matplotlib.offsetbox.DrawingArea):
        for handle in draw_area.get_children():
            if handle.get_label() in legend_format:
                draw_area.set_visible(False)

    return legend

def boxplot_net_transfers(data,reform,elas_vect,bonus_cheques_uc):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    legend_format = {'Elasticity reference' : hue_order,
                    'Percentiles' : [0.01, 0.10, 0.25, 0.5, 0.75, 0.90, 0.99]}
    markers = ['v', 'd', 'o', 'o', 'o' , 'd', '^']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    quantiles_to_plot = quantiles_for_boxplot(data,'Net_transfers_reform')
    sns.scatterplot(data = quantiles_to_plot , x='niveau_vie_decile', y='Net_transfers_reform', hue = 'ref_elasticity',  
                    style = 'quantile',
                    hue_order = hue_order, 
                    palette = sns.color_palette("Paired"), 
                    markers = markers,
                    s = 60,
                    legend = True)
    
    plt.xlabel('Revenue decile', fontdict = {'fontsize' : 14})
    plt.ylabel('Net transfers in euros', fontdict = {'fontsize' : 14})
    subtitle_legend_boxplots(ax, legend_format,markers)
    legend = ax.get_legend()
    legend.set_bbox_to_anchor((1, 0.53))
    ax.xaxis.set_ticks(range(1,11))
    y_min, y_max = -200 , 100
    ax.yaxis.set_ticks(range(y_min,y_max,50))
    
    plt.savefig(os.path.join(output_path,'Figures/Boxplot_net_transfers_reform_{}_elas_vect_{}_bonus_cheques_uc_{}.png').format(reform.key[0],elas_vect,bonus_cheques_uc))
    return

def boxplot_effort_rate(data,reform,elas_vect,bonus_cheques_uc):
    hue_order = ['Berry (2019)', 'Adam et al (2023)', 'Douenne (2020)', 'Combet et al (2009)', 'Ruiz & Trannoy (2008)','Rivers & Schaufele (2015)']
    legend_format = {'Elasticity reference' : hue_order,
                    'Percentiles' : [0.01, 0.10, 0.25, 0.5, 0.75, 0.90, 0.99]}
    markers = ['v', 'd', 'o', 'o', 'o' , 'd', '^']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    quantiles_to_plot = quantiles_for_boxplot(data,'Effort_rate')
    sns.scatterplot(data = quantiles_to_plot, x='niveau_vie_decile', y='Effort_rate', hue = 'ref_elasticity',  
                    style = 'quantile',
                    hue_order = hue_order, 
                    palette = sns.color_palette("Paired"), 
                    markers = markers,
                    s = 60,
                    legend = True)
    
    plt.xlabel('Revenue decile', fontdict = {'fontsize' : 14})
    plt.ylabel('Additional taxes over disposable income', fontdict = {'fontsize' : 14})
    subtitle_legend_boxplots(ax, legend_format,markers)
    legend = ax.get_legend()
    legend.set_bbox_to_anchor((1, 0.53))
    y_min, y_max = 0 , 1
    ax.set_ylim(y_min,y_max)
    
    plt.savefig(os.path.join(output_path,'Figures/Boxplot_effort_rate_reform_{}_elas_vect_{}_bonus_cheques_uc_{}.png').format(reform.key[0],elas_vect,bonus_cheques_uc))
    return