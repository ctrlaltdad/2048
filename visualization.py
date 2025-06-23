import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import matplotlib.animation as animation

def plot_histogram(tiles, title, xlabel='Tile Value', ylabel='Frequency', show=True):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(tiles, bins=range(min(tiles), max(tiles)+2), edgecolor='black', alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    if show:
        plt.show()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def plot_heatmap(heatmap_matrix, lengths, tile_labels, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(heatmap_matrix, aspect='auto', cmap='YlOrRd', origin='lower')
    ax.set_xticks(np.arange(len(lengths)))
    ax.set_xticklabels(lengths)
    ax.set_yticks(np.arange(len(tile_labels)))
    ax.set_yticklabels(tile_labels)
    ax.set_xlabel('Sequence Length')
    ax.set_ylabel('Tile Value')
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label='Probability')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def plot_animated_histogram(animated_hist_data, animated_hist_moves, animated_hist_seq, move_labels):
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = range(2, max([max(d) for d in animated_hist_data])+2, 2)
    def update_hist(i):
        ax.clear()
        ax.hist(animated_hist_data[i], bins=bins, edgecolor='black', alpha=0.7)
        ax.set_title(f'Tile Distribution after {animated_hist_moves[i]} Moves\n(Sequence: {[move_labels[m] for m in animated_hist_seq]})')
        ax.set_xlabel('Tile Value')
        ax.set_ylabel('Frequency')
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ani = animation.FuncAnimation(fig, update_hist, frames=len(animated_hist_data), repeat=False)
    gif_buf = BytesIO()
    ani.save(gif_buf, writer='pillow', format='gif')
    plt.close(fig)
    gif_buf.seek(0)
    return base64.b64encode(gif_buf.read()).decode('utf-8')
