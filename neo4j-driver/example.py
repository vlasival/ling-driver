#!/usr/bin/env python3
"""
Comprehensive example of GraphRepository usage with Neo4j
Demonstrates all major features and best practices
"""

import os
import time
from dotenv import load_dotenv
from graph_repository import GraphRepository, TNode, TArc

# Load environment variables
load_dotenv()


def create_repository():
    """Create and return a configured GraphRepository instance"""
    return GraphRepository(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password'),
        database='driver-test'
    )


def demo_basic_operations():
    """Demonstrate basic CRUD operations"""
    print("🔧 Basic Operations Demo")
    print("=" * 50)
    
    with create_repository() as repo:
        # Create nodes
        print("\n📝 Creating nodes...")
        
        user = repo.create_node({
            'title': 'Alice Johnson',
            'description': 'Senior Software Engineer',
            'labels': ['User', 'Employee'],
            'email': 'alice@company.com',
            'department': 'Engineering',
            'hire_date': '2023-01-15'
        })
        print(f"  ✅ Created user: {user.title}")
        
        project = repo.create_node({
            'title': 'E-commerce Platform',
            'description': 'Modern e-commerce solution with microservices',
            'labels': ['Project'],
            'status': 'active',
            'budget': 500000,
            'start_date': '2024-01-01'
        })
        print(f"  ✅ Created project: {project.title}")
        
        task1 = repo.create_node({
            'title': 'Implement User Authentication',
            'description': 'Add JWT-based authentication system',
            'labels': ['Task'],
            'priority': 'high',
            'estimated_hours': 40,
            'status': 'in_progress'
        })
        print(f"  ✅ Created task: {task1.title}")
        
        task2 = repo.create_node({
            'title': 'Database Schema Design',
            'description': 'Design and implement database schema',
            'labels': ['Task'],
            'priority': 'medium',
            'estimated_hours': 24,
            'status': 'completed'
        })
        print(f"  ✅ Created task: {task2.title}")
        
        # Create relationships
        print("\n🔗 Creating relationships...")
        
        repo.create_arc(
            user.uri, project.uri, 'OWNS',
            {'role': 'project_manager', 'assigned_date': '2024-01-01'}
        )
        print(f"  ✅ {user.title} OWNS {project.title}")
        
        repo.create_arc(
            project.uri, task1.uri, 'CONTAINS',
            {'created_date': '2024-01-15'}
        )
        print(f"  ✅ {project.title} CONTAINS {task1.title}")
        
        repo.create_arc(
            project.uri, task2.uri, 'CONTAINS',
            {'created_date': '2024-01-10'}
        )
        print(f"  ✅ {project.title} CONTAINS {task2.title}")
        
        repo.create_arc(
            user.uri, task1.uri, 'ASSIGNED_TO',
            {'assigned_date': '2024-01-20', 'estimated_completion': '2024-02-15'}
        )
        print(f"  ✅ {user.title} ASSIGNED_TO {task1.title}")
        
        repo.create_arc(
            user.uri, task2.uri, 'ASSIGNED_TO',
            {'assigned_date': '2024-01-10', 'completed_date': '2024-01-25'}
        )
        print(f"  ✅ {user.title} ASSIGNED_TO {task2.title}")
        
        return user, project, task1, task2


def demo_data_retrieval():
    """Demonstrate various data retrieval methods"""
    print("\n\n🔍 Data Retrieval Demo")
    print("=" * 50)
    
    with create_repository() as repo:
        # Get all nodes
        print("\n📊 All nodes in the graph:")
        all_nodes = repo.get_all_nodes()
        for node in all_nodes:
            print(f"  • {node.title} ({node.uri})")
        
        # Get nodes by labels
        print(f"\n👥 Users in the system:")
        users = repo.get_nodes_by_labels(['User'])
        for user in users:
            print(f"  • {user.title} - {user.description}")
        
        print(f"\n📋 Tasks in the system:")
        tasks = repo.get_nodes_by_labels(['Task'])
        for task in tasks:
            print(f"  • {task.title} (Priority: {getattr(task, 'priority', 'N/A')})")
        
        # Get nodes with relationships
        print(f"\n🕸️  Nodes with their relationships:")
        nodes_with_arcs = repo.get_all_nodes_and_arcs()
        for node in nodes_with_arcs:
            print(f"  • {node.title}")
            if node.arcs:
                for arc in node.arcs:
                    print(f"    └─ {arc.uri} → {arc.node_uri_to}")


def demo_advanced_queries():
    """Demonstrate advanced Cypher queries"""
    print("\n\n🚀 Advanced Queries Demo")
    print("=" * 50)
    
    with create_repository() as repo:
        # Complex query: Find all tasks assigned to users
        print("\n📋 Tasks assigned to users:")
        query = """
        MATCH (u:User)-[r:ASSIGNED_TO]->(t:Task)
        RETURN u.title as user, t.title as task, r.assigned_date as assigned_date
        ORDER BY r.assigned_date
        """
        results = repo.run_custom_query(query)
        for result in results:
            print(f"  • {result['user']} → {result['task']} (assigned: {result['assigned_date']})")
        
        # Query: Find project hierarchy
        print("\n🏗️  Project hierarchy:")
        query = """
        MATCH (p:Project)-[r:CONTAINS]->(t:Task)
        RETURN p.title as project, t.title as task, t.priority as priority
        ORDER BY p.title, t.priority
        """
        results = repo.run_custom_query(query)
        for result in results:
            print(f"  • {result['project']} → {result['task']} ({result['priority']} priority)")
        
        # Query: Find paths between nodes
        print("\n🛤️  Paths between users and tasks:")
        query = """
        MATCH path = (u:User)-[*1..3]-(t:Task)
        WHERE u.uri = $user_uri
        RETURN path, length(path) as path_length
        ORDER BY path_length
        LIMIT 5
        """
        users = repo.get_nodes_by_labels(['User'])
        if users:
            start_uri = users[0].uri
            results = repo.run_custom_query(query, {'user_uri': start_uri})
            print(f"  Paths from {users[0].title}:")
            for result in results:
                print(f"    └─ Path length: {result['path_length']}")


def demo_updates_and_utilities():
    """Demonstrate update operations and utility functions"""
    print("\n\n⚙️  Updates & Utilities Demo")
    print("=" * 50)
    
    with create_repository() as repo:
        # Update a node
        print("\n🔄 Updating node...")
        users = repo.get_nodes_by_labels(['User'])
        if users:
            user = users[0]
            updated_user = repo.update_node(user.uri, {
                'last_login': '2024-01-30',
                'status': 'active',
                'notes': 'Updated via GraphRepository demo'
            })
            if updated_user:
                print(f"  ✅ Updated user: {updated_user.title}")
        
        # Generate random strings
        print("\n🎲 Random string generation:")
        for i in range(3):
            random_str = repo.generate_random_string(12)
            print(f"  • Random string {i+1}: {random_str}")
        
        # Custom query with parameters
        print("\n🔍 Custom parameterized query:")
        query = """
        MATCH (n)
        WHERE n.priority = $priority
        RETURN n.title as title, n.description as description
        ORDER BY n.title
        """
        results = repo.run_custom_query(query, {'priority': 'high'})
        print("  High priority items:")
        for result in results:
            print(f"    • {result['title']}: {result['description']}")


def demo_cleanup():
    """Demonstrate cleanup operations (commented out for safety)"""
    print("\n\n🧹 Cleanup Operations Demo")
    print("=" * 50)
    
    with create_repository() as repo:
        print("\n⚠️  Cleanup operations (commented out for safety):")
        
        # Get some nodes to demonstrate deletion
        tasks = repo.get_nodes_by_labels(['Task'])
        if tasks:
            task = tasks[0]
            print(f"  # Would delete task: {task.title} (URI: {task.uri})")
            print(f"  # repo.delete_node_by_uri('{task.uri}')")
        
        # Get some arcs to demonstrate deletion
        print("\n  # Would delete relationships:")
        print("  # repo.delete_arc_by_id(arc_id)")
        
        print("\n  💡 Uncomment the lines above to perform actual cleanup")


def main():
    """Main demonstration function"""
    print("🎯 GraphRepository Comprehensive Demo")
    print("=" * 60)
    print("This demo showcases all major features of GraphRepository")
    print("Working with Neo4j database: driver-test")
    print("=" * 60)
    
    try:
        # Run all demonstrations
        demo_basic_operations()
        demo_data_retrieval()
        demo_advanced_queries()
        demo_updates_and_utilities()
        demo_cleanup()
        
        print("\n\n✅ Demo completed successfully!")
        print("=" * 60)
        print("All GraphRepository features have been demonstrated.")
        print("Check your Neo4j browser to see the created data.")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Make sure Neo4j is running and credentials are correct.")


if __name__ == "__main__":
    main()