import subprocess

def run_script(script_name):
    try:
        result = subprocess.run(['python', script_name], check=True, capture_output=True, text=True)
        print(f"Output of {script_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}:\n{e.stderr}")

if __name__ == "__main__":
    # 运行 extract_pdf.py
    run_script('./extract_pdf.py')
    
    # 运行 graph_visual_with_neo4j.py
    run_script('./graph_visual_with_neo4j.py') 