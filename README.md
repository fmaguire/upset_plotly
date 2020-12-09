# UpSet Plotly

This is a really quick function to abuse plotly's scatter and bar charts
to generate an interactive UpSet plot in plotly.

This was developed for use with a dash application (@apetkau's [card-live-dashboard](github.com/arpcard/card-live-dashboard))
and is fairly rudimentary.

It relies on [upsetplot](https://pypi.org/project/UpSetPlot/) to process the data intersections from pandas DataFrame.

## Installation

Recommended to use a virtual environment of some conda (conda, venv, virtualenv etc).

```bash
git clone https://github.com/fmaguire/upset_plotly
python -m pip install -e upset_plotly
```

## Test

Pretty minimal functional test of plot generation:

```bash
pytest
```

Should generate an interactive plot in `plot.html` similar to:

[![upset_plotly/example.png][]][CARD:Live Dashboard]

## Usage

```python
from upset_plotly import plot

# replace this with your data prepared using upsetplot.from_memberships
# or upsetplot.from_counts
data = upsetplot.generate_counts()

# use the upset_plotly function to generate a plotly figure 
# providing a reasonable title, in this case "example"
fig = plot.upset_plotly(data, 'example')

# the resultant fig can then be visualised in dash or just written 
# to an interactive format e.g.
fig.write_html('example.html')

# or static image
fig.write_image("example.png")
```
