from app import create_app
import sys

app = create_app()

if __name__ == '__main__':
    print("Running direct_run.py to check routes")
    
    # Checking for specific route
    rule_found = False
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        if rule.endpoint == 'admin.edit_subject':
            print(f"Found admin.edit_subject: {rule.rule}")
            print(f"Methods: {rule.methods}")
            rule_found = True
            break
    
    if not rule_found:
        print("admin.edit_subject route not found!")
        
    # Print all routes
    print("\nAll routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        print(f"{rule.endpoint}: {rule.rule}")
    
    # Don't run the server, just check routes
    sys.exit(0)