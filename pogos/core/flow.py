#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PDF flow-diagram utilities.

This module provides a simple linear flow renderer where each item is drawn as
an axis-aligned rectangle and connected with top-to-bottom arrows.
"""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import yaml
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, Rectangle

# =============================================================================
# Define variables
# =============================================================================
__PACKAGE__ = 'pogos'
__PATH__ = Path(__file__).parent.parent
__INSTRUMENT__ = 'None'
# load the yaml file
__YAML__ = yaml.load(open(__PATH__.joinpath('info.yaml')),
                     Loader=yaml.FullLoader)

# =============================================================================
# Get variables from info.yaml
# =============================================================================
__version__ = __YAML__['DRS.VERSION']
__authors__ = __YAML__['DRS.AUTHORS']
__date__ = __YAML__['DRS.DATE']
__release__ = __YAML__['DRS.RELEASE']


def _validate_inputs(title: str, start: str, steps: Sequence[str],
                     outpath: str) -> Tuple[List[str], Path]:
    """Validate and normalize public API inputs."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError('title must be a non-empty string')
    if not isinstance(start, str) or not start.strip():
        raise ValueError('start must be a non-empty string')
    if steps is None:
        steps = []
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise TypeError('steps must be a sequence of strings')
    normalized_steps: List[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, str) or not step.strip():
            raise ValueError(f'steps[{index}] must be a non-empty string')
        normalized_steps.append(step.strip())

    output_path = Path(outpath)
    if not output_path.is_absolute():
        raise ValueError('outpath must be an absolute path to a PDF file')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() != '.pdf':
        output_path = output_path.with_suffix('.pdf')

    items = [start.strip()] + normalized_steps
    return items, output_path


def _compute_layout(n_items: int) -> Tuple[float, float]:
    """Compute rectangle height and inter-box spacing in axis coordinates."""
    if n_items <= 0:
        raise ValueError('n_items must be > 0')
    y_bottom = 0.08
    y_top = 0.9
    available_height = y_top - y_bottom
    spacing_ratio = 0.6
    box_height = available_height / (n_items + spacing_ratio * (n_items - 1))
    box_height = max(0.035, min(0.14, box_height))
    spacing = box_height * spacing_ratio
    return box_height, spacing


def _draw_flow_page(title: str, items: Sequence[str], pdf: PdfPages) -> None:
    """Render a single-page linear flow diagram into the PDF."""
    fig, ax = plt.subplots(figsize=(8.5, 11.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.965, title, ha='center', va='top', fontsize=18,
            fontweight='bold')

    box_width = 0.72
    x_left = (1.0 - box_width) / 2.0
    x_center = 0.5
    n_items = len(items)
    box_height, spacing = _compute_layout(n_items)
    y_top_start = 0.88
    current_top = y_top_start

    for index, raw_text in enumerate(items):
        y_bottom = current_top - box_height
        rect = Rectangle((x_left, y_bottom), box_width, box_height,
                         linewidth=1.5, edgecolor='black', facecolor='white')
        ax.add_patch(rect)

        wrapped = textwrap.fill(raw_text, width=42)
        ax.text(x_center, y_bottom + box_height / 2.0, wrapped,
                ha='center', va='center', fontsize=10)

        if index < n_items - 1:
            next_top = current_top - box_height - spacing
            arrow = FancyArrowPatch((x_center, y_bottom), (x_center, next_top),
                                    arrowstyle='-|>', mutation_scale=14,
                                    linewidth=1.4, color='black')
            ax.add_patch(arrow)

        current_top = current_top - box_height - spacing

    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _read_csv_rows(csv_path: Path) -> List[List[str]]:
    """Read all CSV rows as string values."""
    if not csv_path.exists() or not csv_path.is_file():
        raise FileNotFoundError(f'CSV file does not exist: {csv_path}')
    with csv_path.open('r', newline='', encoding='utf-8') as handle:
        reader = csv.reader(handle)
        return [[str(cell) for cell in row] for row in reader]


def _draw_table_pages(title: str, csv_path: Path, pdf: PdfPages,
                      rows_per_page: int = 34) -> None:
    """Render CSV table rows across one or more pages."""
    rows = _read_csv_rows(csv_path)
    if not rows:
        return

    header = rows[0]
    data_rows = rows[1:]
    n_pages = max(1, (len(data_rows) + rows_per_page - 1) // rows_per_page)

    for page_index in range(n_pages):
        start = page_index * rows_per_page
        stop = start + rows_per_page
        chunk = data_rows[start:stop]
        page_rows = [header] + chunk

        fig, ax = plt.subplots(figsize=(11.0, 8.5))
        ax.axis('off')
        table_title = (
            f'{title}\nCSV: {csv_path.name} (table page {page_index + 1}/{n_pages})'
        )
        ax.set_title(table_title, fontsize=12, pad=18)

        table = ax.table(cellText=page_rows, loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)

        for col in range(len(header)):
            header_cell = table[(0, col)]
            header_cell.set_text_props(weight='bold')

        fig.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)


def generate_flow_pdf(title: str, start: str, steps: List[str], outpath: str,
                      csv_path: Optional[str] = None) -> Path:
    """Generate a flow diagram PDF and optionally append CSV table pages.

    Parameters
    ----------
    title : str
        Document heading shown on the flow page.
    start : str
        First flow box text.
    steps : List[str]
        Linear ordered steps following the start box.
    outpath : str
        Absolute path to output PDF.
    csv_path : Optional[str], default=None
        Optional path to a CSV file to render as table pages after the flow.

    Returns
    -------
    Path
        Final output path to the generated PDF.
    """
    items, output_path = _validate_inputs(title=title, start=start,
                                          steps=steps, outpath=outpath)
    # all inside the pdf pages matplotlib backend
    with PdfPages(output_path) as pdf:
        _draw_flow_page(title=title, items=items, pdf=pdf)
        if csv_path is not None:
            _draw_table_pages(title=title, csv_path=Path(csv_path), pdf=pdf)

    return output_path


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    demo_out = Path('/tmp/pogos_flow_demo.pdf')
    generate_flow_pdf(
        title='POGOS Linear Flow Demo',
        start='Start processing',
        steps=['Load data', 'Calibrate', 'Extract products', 'Publish outputs'],
        outpath=str(demo_out),
        csv_path=None,
    )
    print(f'Wrote demo PDF: {demo_out}')

# =============================================================================
# End of code
# =============================================================================
