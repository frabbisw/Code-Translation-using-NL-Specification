import json
import matplotlib.pyplot as plt

def generate_issues_chart(json_file='tags.json', output_file='tags.png'):
    # 1. Load Data
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found. Please ensure the file exists.")
        return

    # 2. Extract unique languages to determine grid size
    languages = set()
    for key in data.keys():
        if "_to_" in key:
            parts = key.split("_to_")
            if len(parts) == 2:
                languages.add(parts[0])
                languages.add(parts[1])
    
    lang_list = sorted(list(languages))
    n = len(lang_list)
    
    if n == 0:
        print("No valid 'Src_to_Tgt' keys found in JSON.")
        return

    # 3. Setup Figure with Tighter Spacing
    # We remove constrained_layout to have manual control over spacing
    fig, axes = plt.subplots(n, n, figsize=(5 * n, 5 * n)) 
    
    # MANUAL ADJUSTMENT: This removes whitespace between subplots and around edges
    plt.subplots_adjust(
        left=0.05,    # Small margin on left
        right=0.98,   # Small margin on right
        top=0.95,     # Small margin on top (for column headers)
        bottom=0.05,  # Small margin on bottom
        wspace=0.1,   # Minimal horizontal space between charts
        hspace=0.1    # Minimal vertical space between charts
    )

    # 4. Iterate through the grid
    for i, target_lang in enumerate(lang_list):      # Row = Target
        for j, source_lang in enumerate(lang_list):  # Col = Source
            
            # Handle single vs multiple subplot indexing
            if n > 1:
                ax = axes[i, j]
            else:
                ax = axes

            key = f"{source_lang}_to_{target_lang}"
            
            # --- FIX FOR BROKEN LABELS ---
            # We set labels first. We will NOT use ax.axis('off') later, 
            # as that deletes these labels.
            if i == 0:
                ax.set_title(source_lang, fontsize=20, weight='bold', pad=10) 
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=20, weight='bold', rotation=90, labelpad=10)

            # --- PLOTTING LOGIC ---
            if source_lang == target_lang:
                # Diagonal (N/A)
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', color='#ccc', fontsize=24, weight='bold')
                
                # CRITICAL FIX: Do not use ax.axis('off'). 
                # Instead, manually hide ticks and spines so labels persist.
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

            elif key in data:
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    pctdistance=0.85,
                    textprops={'fontsize': 16} 
                )
                
                # Legend - optimized to take less space
                ax.legend(
                    wedges, 
                    labels, 
                    title="Issues", 
                    loc="center left", 
                    bbox_to_anchor=(0.9, 0, 0.5, 1), # Adjusted position
                    fontsize=13,
                    frameon=False # Removes box around legend to save visual clutter
                )
                ax.set_aspect('equal')
            else:
                # No Data Case
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='grey', fontsize=16)
                
                # Hide ticks/spines but keep labels
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)

    # Global axis labels (Optional - usually the row/col headers are enough now)
    # If you want to save more space, you can comment these two lines out:
    fig.text(0.5, 0.01, 'Source Language', ha='center', fontsize=24, weight='bold')
    fig.text(0.01, 0.5, 'Target Language', va='center', rotation='vertical', fontsize=24, weight='bold')

    print(f"Saving high-resolution figure to {output_file}...")
    plt.savefig(output_file, dpi=300)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
