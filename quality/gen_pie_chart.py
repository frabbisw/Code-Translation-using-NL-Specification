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

    # 3. Setup Figure
    # figsize=(5*n, 5*n) is a good balance between resolution and compactness
    fig, axes = plt.subplots(n, n, figsize=(5 * n, 5 * n))
    
    # ADJUSTMENT: Tighten the internal spacing to save white space
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    # 4. Iterate through the grid
    for i, target_lang in enumerate(lang_list):      # Row = Target
        for j, source_lang in enumerate(lang_list):  # Col = Source
            
            # Handle single vs multiple subplot indexing
            ax = axes[i, j] if n > 1 else axes
            key = f"{source_lang}_to_{target_lang}"
            
            # --- FIX 1: HEADERS ---
            # We set these immediately. We will NOT use ax.axis('off') later,
            # because that would delete these headers.
            if i == 0:
                ax.set_title(source_lang, fontsize=24, weight='bold', pad=20) 
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=24, weight='bold', rotation=90, labelpad=20)

            # --- PLOTTING LOGIC ---
            if source_lang == target_lang:
                # --- FIX 2: TRANSPARENT DIAGONAL ---
                # 1. Set background to transparent
                ax.set_facecolor('none')
                
                # 2. Hide ticks (markers on axis)
                ax.set_xticks([])
                ax.set_yticks([])
                
                # 3. Hide spines (the square border lines)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                # 4. Ensure grid is off
                ax.grid(False)
                
                # We do NOT add any text, so it remains empty.

            elif key in data:
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                # Pie Chart
                # radius=0.9 ensures it fills the square without overflowing
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    radius=0.9, 
                    pctdistance=0.85,
                    textprops={'fontsize': 16} 
                )
                
                # Legend
                # bbox_to_anchor places the legend intelligently outside the pie
                ax.legend(
                    wedges, 
                    labels, 
                    title="Issues", 
                    loc="center left", 
                    bbox_to_anchor=(0.95, 0.5),
                    fontsize=11,
                    frameon=False 
                )
                ax.set_aspect('equal')
            else:
                # No Data Case (also transparent)
                ax.set_facecolor('none')
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='#ccc', fontsize=14)
                
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.grid(False)

    print(f"Saving high-resolution figure to {output_file}...")
    
    # --- FIX 3: SAVING ---
    # bbox_inches='tight' -> prevents cutting off legends
    # transparent=True -> makes the 'none' backgrounds actually transparent
    plt.savefig(output_file, dpi=300, bbox_inches='tight', transparent=True)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
