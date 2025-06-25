import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import matplotlib.animation as animation
import os

def plot_histogram(tiles, title, xlabel='Tile Value', ylabel='Frequency', show=True, return_html=False):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(tiles, bins=range(min(tiles), max(tiles)+2), edgecolor='black', alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    if show and not return_html:
        plt.imshow(plt.imread(BytesIO(base64.b64decode(img_base64))))
        plt.axis('off')
        plt.show()
    if return_html:
        return (title, img_base64)
    return img_base64

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

def show_heatmap_from_tiles(tiles, title='Heatmap: Tile Distribution', show=True, return_html=False):
    tile_values = sorted(set(tiles))
    counts = [tiles.count(t) for t in tile_values]
    heatmap_matrix = np.array([counts])
    fig, ax = plt.subplots(figsize=(8, 2))
    im = ax.imshow(heatmap_matrix, aspect='auto', cmap='YlOrRd', origin='lower')
    ax.set_xticks(np.arange(len(tile_values)))
    ax.set_xticklabels(tile_values)
    ax.set_yticks([0])
    ax.set_yticklabels(['Runs'])
    ax.set_xlabel('Tile Value')
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label='Count')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    if show and not return_html:
        plt.imshow(plt.imread(BytesIO(base64.b64decode(img_base64))))
        plt.axis('off')
        plt.show()
    if return_html:
        return (title, img_base64)
    return img_base64

def save_visuals_to_html(plots, filename='results.html', title='2048 Simulation Results'):
    import os
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    section_header = f'<hr><h2>{title} <span style="font-size:small;">({timestamp})</span></h2>'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove the last </body></html> if present
        if content.strip().endswith('</body></html>'):
            content = content.strip()[:-14]
    else:
        # Start a new HTML file
        content = f'<html><head><title>2048 Simulation Results</title></head><body>\n<h1>2048 Simulation Results</h1>'
    # Add new section header and plots
    content += f'\n{section_header}'
    for plot_title, img_base64 in plots:
        content += f'\n<h3>{plot_title}</h3>'
        content += f'\n<img src="data:image/png;base64,{img_base64}"/><br/>'
    # Close the HTML
    content += '\n</body></html>'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
