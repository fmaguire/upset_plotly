#!/usr/bin/env python
import upsetplot
import itertools
import pandas as pd
import plotly.express as px
import plotly.subplots as sbp
import plotly.graph_objects as go

def upset_plotly(data: pd.Series, title: str) -> go.Figure:
    """
    Takes a series formatted as per
    """

    # check type
    if type(data) != pd.Series or type(data.index) != pd.MultiIndex:
        raise ValueError("Data is incorrectly formatted, must be a boolean "
                         "multindex a la the output from upsetplot.from_memberships")

    # convert to upset data
    data = upsetplot.UpSet(data, sort_by="cardinality")

    # get number of sets and categories in UpSet
    num_sets, num_categories = data.intersections.reset_index().shape

    # return empty figure if no data is provided
    # Creation of empty figure adapted from https://community.plotly.com/t/replacing-an-empty-graph-with-a-message/31497
    # via aaron's github.com/apetkau/card-live-dashboard
    if num_sets == 0 or num_categories == 0:
        fig = go.Figure(layout={
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'annotations': [{
                        'text': 'Dataset empty',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {
                            'size': 28
                        }
                    }]
            })

    # or empty figure with explanation if there are too many categories to plot
    elif num_categories > 40:
        fig = go.Figure(layout={
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f"{num_categories} total categories with current selection.<br>Too much data to plot intersections, please subset further.",
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {
                        'size': 28
                    }
                }]
            })

    else:
        # truncate to top 25 sets by cardinality
        if num_sets > 25:
            truncated = True
            data.intersections = data.intersections[:25]
        else:
            truncated = False

            # get the category names in each set for annotation
            set_category_annotations = []
            for mask in data.intersections.index:
                categories_in_set = itertools.compress(data.intersections.index.names,
                                                       mask)
                categories_in_set = "<br>".join(sorted(categories_in_set))
                set_category_annotations.append(categories_in_set)

            set_intersections = data.intersections.reset_index().iloc[:, :-1].astype(int).T.iloc[::-1]

            # begin actual plotting
            # make grid for set memberships
            grid_x = []
            grid_y = []
            membership_x = []
            membership_y = []
            names = []
            y = 0
            for row in set_intersections.iterrows():
                x = 0
                for membership in row[1]:
                    grid_x.append(x)
                    grid_y.append(y)
                    if membership == 1:
                        membership_x.append(x)
                        membership_y.append(y)
                        names.append(row[0])
                    x+=1
                y+=1

            # create subplot layout
            fig = sbp.make_subplots(rows=2, cols=2,
                                    column_widths=[2, 0.2],
                                    row_heights=[0.4, 2],
                                    horizontal_spacing = 0.005,
                                    vertical_spacing=0.01)

            # add barplot of intersection cardinalities
            fig.add_trace(go.Bar(y=data.intersections.values,
                                 x=set_category_annotations,
                                 name=f"{title} Set Cardinality",
                                 showlegend=False,
                                 hovertemplate='Set Count: %{y}<br>Set: [%{x}]',
                                 xaxis='x1',
                                 yaxis='y1'),
                          row=1, col=1),

            # add barplot of count of category values
            fig.add_trace(go.Bar(y = data.totals.iloc[::-1].index,
                                 x=data.totals.iloc[::-1],
                                 orientation='h',
                                 name=f"{title} Unique Counts",
                                 showlegend=False,
                                 hovertemplate='Category: %{y}<br>Category Count: %{x}',
                                 yaxis='y2',
                                 xaxis='x2'),
                          row=2, col=2)

            # create the backgrid for the set memberships
            fig.add_trace(go.Scatter(x = grid_x,
                                     y = grid_y,
                                     hoverinfo='skip',
                                     mode='markers',
                                     marker={'color': 'lightgrey'},
                                     showlegend=False,
                                     xaxis='x3',
                                     yaxis='y3'),
                          row=2, col=1)

            # plot the set memberships
            fig.add_trace(go.Scatter(x = membership_x,
                                     y = membership_y,
                                     name=f"{title} Set Intersections",
                                     hovertext=names,
                                     hovertemplate='%{hovertext}',
                                     mode='markers',
                                     marker={'color': 'blue'},
                                     xaxis='x4',
                                     yaxis='y4',
                                     showlegend=False),
                            row=2, col=1)

            # tidy up layout, disable and align axes so everything joins
            # there may be a better way to do this with shared/aligned axes
            # across plots that still allows zooming but I can't figure it out
            # right now!
            if truncated:
                plot_label = f"{title} UpSet Plot<br>(Truncated to 25 Most Common Intersections)"
            else:
                plot_label = f"{title} UpSet Plot<br>(All Intersections)"

            fig.update_layout(dict(
                title = plot_label,
                # cardinality
                xaxis1 = dict(showticklabels=False,
                              fixedrange=True),
                yaxis1 = dict(title="Set Count",
                              fixedrange=True),

                # grid
                xaxis2 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.columns)-0.5]),
                yaxis2 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.index)+0.5]),

                # membership
                xaxis3 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[-0.5, len(set_intersections.columns)-0.5]),
                yaxis3 = dict(
                    tickmode = 'array',
                    tickvals = list(range(len(set_intersections.index))),
                    ticktext = set_intersections.index,
                    title=f"{title}",
                    fixedrange=True,
                    range=[-0.5, len(set_intersections.index)+0.5],
                    tickfont=dict(size = 10),
                    automargin=True,
                ),

                # category count
                xaxis4 = dict(title="Category Count",
                              fixedrange=True),
                yaxis4 = dict(showticklabels=False,
                              fixedrange=True,
                              range=[0, len(set_intersections.index)+0.5])
            )
            )
            fig.update_layout(height=get_figure_height(num_categories))

    return fig

def get_figure_height(number_categories: int) -> int:
    """
    Given a number of categories to plot gets an appropriate figure height.
    :param number_categories: The number of categories to plot.
    :return: A figure height to be used by plotly.
    """
    if number_categories < 10:
        return 400
    elif number_categories < 20:
        return 500
    elif number_categories < 30:
        return 600
    else:
        return 800
