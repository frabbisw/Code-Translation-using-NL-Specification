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
    # Keys are expected to be in format "Src_to_Tgt"
    languages = set()
    for key in data.keys():
        if "_to_" in key:
            parts = key.split("_to_")
            if len(parts) == 2:
                languages.add(parts[0])
                languages.add(parts[1])
    
    # Sort languages for consistent axis ordering
    lang_list = sorted(list(languages))
    n = len(lang_list)
    
    if n == 0:
        print("No valid 'Src_to_Tgt' keys found in JSON.")
        return

    # 3. Setup the plot grid
    # Rows = Target Languages, Columns = Source Languages
    fig, axes = plt.subplots(n, n, figsize=(4 * n, 4 * n), constrained_layout=True)
    
    # Title
    fig.suptitle('SonarQube Issues Distribution: Source (X-axis) vs Target (Y-axis)', fontsize=24, weight='bold')

    # 4. Iterate through the grid
    for i, target_lang in enumerate(lang_list):      # Row = Target
        for j, source_lang in enumerate(lang_list):  # Col = Source
            
            # Handle the axes object (axes is 1D if n=1, 2D if n>1)
            ax = axes[i, j] if n > 1 else axes
            
            # Construct key matching the JSON format
            key = f"{source_lang}_to_{target_lang}"
            
            # Label Axes (headers for rows/cols)
            if i == 0:
                ax.set_title(source_lang, fontsize=16, weight='bold', pad=20) # Top headers (Source)
            if j == 0:
                ax.set_ylabel(target_lang, fontsize=16, weight='bold', rotation=90, labelpad=20) # Left headers (Target)

            # Check for data
            if source_lang == target_lang:
                # Diagonal - usually N/A
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', color='grey', fontsize=12)
                ax.axis('off')
            elif key in data:
                # Plot Pie Chart
                issues = data[key]
                labels = [item['topic'] for item in issues]
                counts = [item['count'] for item in issues]
                
                # Plot
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    autopct='%1.0f%%',
                    startangle=90,
                    pctdistance=0.85,
                    textprops={'fontsize': 9}
                )
                
                # Add Legend (anchored to the side of the subplot to avoid clutter)
                # We use a small font size so it fits
                ax.legend(
                    wedges, 
                    labels, 
                    title="Top Issues", 
                    loc="center left", 
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize='x-small'
                )
                ax.set_aspect('equal')
            else:
                # No data found for this pair
                ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='grey', fontsize=10)
                ax.axis('off')

    # 5. Add global axis labels (optional, but helpful)
    fig.text(0.5, 0.02, 'Source Language', ha='center', fontsize=20, weight='bold')
    fig.text(0.02, 0.5, 'Target Language', va='center', rotation='vertical', fontsize=20, weight='bold')

    # 6. Save
    print(f"Saving figure to {output_file}...")
    plt.savefig(output_file, dpi=100)
    print("Done.")

if __name__ == "__main__":
    generate_issues_chart()
