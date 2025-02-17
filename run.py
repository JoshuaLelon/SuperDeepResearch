"""
Test script for the full research pipeline.
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools.e2e_tool import full_research_pipeline

def main():
    # Test query
    query = "What are the different types of roses and which one has the most thorns?"
    
    print("Starting research pipeline...")
    print(f"Query: {query}\n")
    
    try:
        result = full_research_pipeline(query)
        print("Research completed successfully!")
        print("\nResults:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 