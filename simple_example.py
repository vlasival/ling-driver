import os
from dotenv import load_dotenv
from graph_repository import GraphRepository, TNode, TArc

# Load environment variables
load_dotenv()

def create_repository():
    return GraphRepository(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password'),
        database='driver-test'
    )

with create_repository() as repo:
    user = repo.get_node_by_uri('node_gypcjrllfa')
    print(f"  • {user.title} - {user.description}")