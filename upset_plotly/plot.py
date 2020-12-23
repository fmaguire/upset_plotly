#!/usr/bin/env python
import upsetplot
import itertools
import pandas as pd
import plotly.express as px
import plotly.subplots as sbp
import plotly.graph_objects as go

MAX_UPSET_CATEGORIES=40
MAX_UPSET_INTERSECTIONS=25


def upset_plotly(data: pd.Series, title: str) -> go.Figure:
    """
    Takes a series formatted as per upsetplot.from_membership or
    upsetplot.from_contents
    """

    # check type work for from_membership or from_contents
    if type(data) not in [pd.Series, pd.DataFrame] or type(data.index) != pd.MultiIndex:
        raise ValueError("Data is incorrectly formatted, must be a boolean "
                         "multindex a la the output from upsetplot.from_memberships")

    # if data is empty or only contains one record then can't generate
    # upset plots therefore plot empty figure
    if data.empty:
        fig = go.Figure(layout={'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'annotations': [{
                                    'text': f"No data to plot",
                                    'xref': 'paper',
                                    'yref': 'paper',
                                    'showarrow': False,
                                    'font': {'size': 16}}]})
    elif len(data) == 1:
        fig = go.Figure(layout={'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'annotations': [{
                                'text': f"Only a single value for {title} "
                                         "with current selection. "
                                         "<br>Can't plot intersections for "
                                         "a single category (see above)",
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font': {'size': 16}}]})
    else:
        # get number of sets and categories into UpSet class
        upset_data = upsetplot.UpSet(data, sort_by="cardinality")

        num_sets, num_categories = upset_data.intersections.reset_index().shape

        # if the data is empty
        if num_sets == 0 or num_categories == 0:
            fig = go.Figure(layout={'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'annotations': [{
                                    'text': f"No data to plot",
                                    'xref': 'paper',
                                    'yref': 'paper',
                                    'showarrow': False,
                                    'font': {'size': 16}}]})
        # or if there is way too much data to plot
        elif num_categories > MAX_UPSET_CATEGORIES:
            fig = go.Figure(layout={
                                'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'annotations': [{
                                'text': f"{num_categories} total {title} "
                                         "categories with current selection. "
                                         "<br>Please subset input data "
                                         "further to display set "
                                         "intersections.",
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font': {'size': 16}
                                }]
                            })

        else:
            # filter to top MAX_UPSET_INTERSECTIONS sets by cardinality
            if num_sets > MAX_UPSET_INTERSECTIONS:
                truncated = True
                upset_data.intersections = upset_data.intersections[:MAX_UPSET_INTERSECTIONS]
            else:
                truncated = False

            # generate plot
            fig = plotly_upset_plot(upset_data, title, truncated)

            # size for display as appropriate for the number of categories
            fig.update_layout(height=get_figure_height(num_categories))

    return fig


def plotly_upset_plot(upset_data: upsetplot.UpSet, title: str, truncated: bool) -> go.Figure:
    """
    Generate upset plot in plotly
    :param upset_data: an upsetplot.UpSet class containing the intersections
                        for a given set of RGI result categories
    :param title: a string containing the title for this upsetplot
    :param truncated: a boolean indicating if this upsetplot has been truncated
                      to a subset of intersections
    :return: a plotly figure containing the upsetplot
    """

    # get the category names in each set for hover annotation
    set_category_annotations = []
    for mask in upset_data.intersections.index:
        categories_in_set = itertools.compress(\
                                  upset_data.intersections.index.names,
                                  mask)
        categories_in_set = "<br>".join(sorted(categories_in_set))
        set_category_annotations.append(categories_in_set)

    set_intersections = upset_data.intersections.reset_index()\
                            .iloc[:, :-1].astype(int).T.iloc[::-1]

    # make grid for set memberships
    grid_x = []
    grid_y = []
    membership_x = []
    membership_y = []
    names = []

    for (y, row) in enumerate(set_intersections.iterrows()):
        for (x, membership) in enumerate(row[1]):
            grid_x.append(x)
            grid_y.append(y)
            if membership == 1:
                membership_x.append(x)
                membership_y.append(y)
                names.append(row[0])

    # create subplot layout
    fig = sbp.make_subplots(rows=2, cols=2,
                            column_widths=[2, 0.2],
                            row_heights=[0.4, 2],
                            horizontal_spacing = 0.005,
                            vertical_spacing=0.01)

    # add barplot of intersection cardinalities
    fig.add_trace(go.Bar(y=upset_data.intersections.values,
                         x=set_category_annotations,
                         name=f"{title} set",
                         showlegend=False,
                         hovertemplate='Genomes w/ Set: %{y}<br>Set: [%{x}]<extra></extra>',
                         xaxis='x1',
                         yaxis='y1'),
                  row=1, col=1),

    # add barplot of count of category values
    fig.add_trace(go.Bar(y=upset_data.totals.iloc[::-1].index,
                         x=upset_data.totals.iloc[::-1],
                         orientation='h',
                         name=f"{title} unique count",
                         showlegend=False,
                         hovertemplate='Category: %{y}<br>Genomes: %{x}<extra></extra>',
                         yaxis='y2',
                         xaxis='x2'),
                  row=2, col=2)

    # create the backgrid for the set memberships
    fig.add_trace(go.Scatter(x=grid_x,
                             y=grid_y,
                             hoverinfo='skip',
                             mode='markers',
                             marker={'color': 'lightgrey'},
                             showlegend=False,
                             xaxis='x3',
                             yaxis='y3'),
                  row=2, col=1)

    # plot the set memberships
    fig.add_trace(go.Scatter(x=membership_x,
                             y=membership_y,
                             name=f"{title} in set",
                             hovertext=names,
                             hovertemplate='%{hovertext}<extra></extra>',
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
    fig = configure_upset_plot_axes(fig, set_intersections, truncated, title)

    return fig


def configure_upset_plot_axes(fig: go.Figure, set_intersections: pd.DataFrame,
                              truncated: bool, title: str) -> go.Figure:
    """
    Format and organise plot axes for upset plotly figure
    :param fig: a go.Figure containing the plotly upsetplot
    :param set_intersections: pandas DataFrame with all set intersections
    :param truncated: boolean if the number of intersections has been truncated
                      or not (i.e. if num intersections > MAX_UPSET_INTERSECTIONS)
    :param title: str containing the plot title
    :return: A go.Figure of the plotly upsetplot with tidied/formatted
             axes legends
    """

    if truncated:
        plot_label = f"{title} UpSet Plot<br>(Truncated to {MAX_UPSET_INTERSECTIONS} Most "\
                      "Common Intersections)"
    else:
        plot_label = f"{title} UpSet Plot<br>(All Intersections)"

    fig.update_layout(dict(
        title = plot_label,

        # tidy axes for cardinality plot
        xaxis1 = dict(showticklabels=False,
                      fixedrange=True),
        yaxis1 = dict(title="Set Count"),
                      #fixedrange=True),

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
        xaxis4 = dict(title=f"Unique Count of<br>{title}"),
                      #fixedrange=True),
        yaxis4 = dict(showticklabels=False,
                      fixedrange=True,
                      range=[-0.5, len(set_intersections.index)+0.5])
    )
    )
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
