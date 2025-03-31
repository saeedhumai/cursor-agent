import ollama

try:
    # Get available models
    response = ollama.list()
    
    # Print response structure
    print("Response type:", type(response))
    print("Response attributes:", dir(response))
    
    # Try to access models
    if hasattr(response, "models"):
        models = response.models
        print("\nModels type:", type(models))
        
        if len(models) > 0:
            first_model = models[0]
            print("\nFirst model type:", type(first_model))
            print("First model attributes:", dir(first_model))
    
    # Try dictionary-style access
    try:
        models_dict = dict(response)
        print("\nResponse as dict:", models_dict)
    except:
        print("\nCannot convert response to dict")
        
    # Another approach - iterate directly
    print("\nIterating through models directly:")
    for model in response.models:
        print(f"Model: {model}")
        # Try to get name attribute
        for attr in ["name", "model", "id"]:
            if hasattr(model, attr):
                print(f"  - {attr}: {getattr(model, attr)}")
except Exception as e:
    print(f"Error: {str(e)}") 