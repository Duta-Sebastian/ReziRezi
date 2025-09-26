import os
import csv
import glob

def count_words_in_file(file_path):
    """Count words in a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split by whitespace and filter out empty strings
            words = [word for word in content.split() if word.strip()]
            return len(words)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def process_txt_files(folder_path, output_csv='word_counts.csv'):
    """Process all .txt files in a folder and create a CSV with word counts."""
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    # Find all .txt files in the folder
    txt_pattern = os.path.join(folder_path, "*.txt")
    txt_files = glob.glob(txt_pattern)
    
    if not txt_files:
        print(f"No .txt files found in '{folder_path}'")
        return
    
    # Prepare data for CSV
    file_data = []
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        word_count = count_words_in_file(file_path)
        file_data.append([filename, word_count])
        print(f"Processed: {filename} - {word_count} words")
    
    # Sort by filename for consistent output
    file_data.sort(key=lambda x: x[0])
    
    # Write to CSV
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Filename', 'Word Count'])  # Header
            writer.writerows(file_data)
        
        print(f"\nCSV file '{output_csv}' created successfully!")
        print(f"Processed {len(file_data)} text files.")
        
    except Exception as e:
        print(f"Error writing CSV file: {e}")

def main():
    # You can modify this path to point to your folder
    folder_path = "output_transcripts"
    
    # Optional: specify output CSV name
    output_name = input("Enter output CSV filename (press Enter for 'word_counts.csv'): ").strip()
    if not output_name:
        output_name = 'word_counts.csv'
    
    process_txt_files(folder_path, output_name)

if __name__ == "__main__":
    main()