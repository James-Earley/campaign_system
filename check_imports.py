# check_imports.py
import os

def check_files():
    route_dir = 'app/routes'
    issues = []
    
    for filename in os.listdir(route_dir):
        if filename.endswith('.py'):
            with open(os.path.join(route_dir, filename), 'r') as f:
                content = f.read()
                if 'initialize_models' in content:
                    issues.append(filename)
                    
    return issues

if __name__ == '__main__':
    print("Checking for old model initialization...")
    issues = check_files()
    if issues:
        print("Files still using initialize_models:")
        for file in issues:
            print(f"- {file}")
    else:
        print("All files are using the new pattern!")