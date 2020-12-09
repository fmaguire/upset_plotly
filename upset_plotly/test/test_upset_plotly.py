import pandas as pd
from pathlib import Path
import upsetplot
from upset_plotly import plot

def test_plot():
    output_path = Path('plot.html')
    df = upsetplot.generate_counts()
    fig = plot.upset_plotly(df, 'test')
    fig.write_html(str(output_path))
    assert output_path.exists()
