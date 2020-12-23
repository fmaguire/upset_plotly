import pandas as pd
from pathlib import Path
import upsetplot
from upset_plotly import plot

def test_plot():
    html_output_path = Path('plot.html')
    png_output_path = Path('plot.png')
    df = upsetplot.generate_counts()
    fig = plot.upset_plotly(df, 'test')
    fig.write_html(str(html_output_path))
    fig.write_image(str(png_output_path))
    assert html_output_path.exists()
    assert png_output_path.exists()


