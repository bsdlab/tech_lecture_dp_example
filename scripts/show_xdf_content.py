"""Simple script to load XDF content and display it in a plotly figure."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from fire import Fire
import pyxdf


def show_xdf_content(filepath: str):
    """
    Load and visualize XDF file content with one subplot per stream.

    Parameters
    ----------
    filepath : str
        Path to the XDF file to load.
    """
    # Load XDF file
    streams, header = pyxdf.load_xdf(filepath)

    if not streams:
        print("No streams found in XDF file")
        return

    # Create subplots - one row per stream
    n_streams = len(streams)
    fig = make_subplots(
        rows=n_streams,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Stream name=" + stream["info"]["name"][0] for stream in streams
        ],
        vertical_spacing=0.08,
    )

    # Get viridis colormap
    viridis = px.colors.sequential.Viridis
    tzero = min(stream["time_stamps"][0] for stream in streams)

    for idx, stream in enumerate(streams, start=1):
        # Extract stream info
        stream_name = stream["info"]["name"][0]
        timestamps = stream["time_stamps"]
        data = stream["time_series"]
        channel_format = stream["info"].get("channel_format", ["unknown"])[0]

        if channel_format == "string":
            # String/marker data - plot as scatter points with text
            marker_texts = []
            for marker in data:
                if isinstance(marker, (list, np.ndarray)):
                    marker_texts.append(marker[0] if len(marker) > 0 else "")
                else:
                    marker_texts.append(str(marker))

            # Sample colors from viridis
            colors = [
                viridis[int((i / max(len(timestamps) - 1, 1)) * (len(viridis) - 1))]
                for i in range(len(timestamps))
            ]

            fig.add_trace(
                go.Scatter(
                    x=timestamps - tzero,
                    y=[0] * len(timestamps),
                    mode="markers+text",
                    marker=dict(size=10, color=colors),
                    text=marker_texts,
                    textposition="top right",
                    name=stream_name,
                    showlegend=False,
                ),
                row=idx,
                col=1,
            )

            # Set y-axis range for marker streams
            fig.update_yaxes(range=[-0.5, 0.5], showticklabels=False, row=idx, col=1)

        else:  # expect numeric format
            # Numeric data - plot as lines with different colors per channel
            n_channels = data.shape[1] if data.ndim > 1 else 1

            if data.ndim == 1:
                data = data.reshape(-1, 1)

            # Plot each channel with a color from viridis
            for ch_idx in range(n_channels):
                # Sample colors from viridis scale
                color_idx = int((ch_idx / max(n_channels - 1, 1)) * (len(viridis) - 1))
                color = viridis[color_idx]

                fig.add_trace(
                    go.Scatter(
                        x=timestamps - tzero,
                        y=data[:, ch_idx],
                        mode="lines",
                        name=f"{stream_name} Ch{ch_idx}",
                        line=dict(color=color),
                        showlegend=(
                            n_channels <= 10
                        ),  # Only show legend if not too many
                    ),
                    row=idx,
                    col=1,
                )

        # Update y-axis label
        fig.update_yaxes(
            title_text="Markers" if channel_format == "string" else "Value",
            row=idx,
            col=1,
        )

    # Update x-axis label on bottom plot
    fig.update_xaxes(title_text="Time [s]", row=n_streams, col=1)

    # Update layout
    fig.update_layout(
        height=300 * n_streams,
        title_text="XDF File Content",
        showlegend=True,
        hovermode="x unified",
    )

    fig.show()


if __name__ == "__main__":
    Fire(show_xdf_content)
