#!/usr/bin/env python3
"""
Тесты для GraphRepository
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from graph_repository import GraphRepository, TNode, TArc


class TestGraphRepository(unittest.TestCase):
    """Тесты для GraphRepository"""
    
    def setUp(self):
        """Настройка тестов"""
        with patch('graph_repository.GraphDatabase'):
            self.repo = GraphRepository(
                uri='bolt://localhost:7687',
                user='neo4j',
                password='test',
                database='test-db'
            )
            self.repo.driver = Mock()
            # Создаем правильный mock для session
            mock_session = Mock()
            mock_session.__enter__ = Mock(return_value=mock_session)
            mock_session.__exit__ = Mock(return_value=None)
            mock_session.run.return_value = []
            self.repo.driver.session.return_value = mock_session
    
    def test_generate_random_string(self):
        """Тест генерации случайной строки"""
        random_str = self.repo.generate_random_string(10)
        self.assertEqual(len(random_str), 10)
        self.assertTrue(random_str.isalnum())
    
    def test_build_labels_clause(self):
        """Тест построения строки меток"""
        labels = ['User', 'Person']
        result = self.repo._build_labels_clause(labels)
        self.assertEqual(result, ':`User`:`Person`')
        
        # Тест с пустым списком
        result_empty = self.repo._build_labels_clause([])
        self.assertEqual(result_empty, '')
        
        # Тест с метками содержащими обратные кавычки
        labels_with_quotes = ['User`Test', 'Person']
        result_quotes = self.repo._build_labels_clause(labels_with_quotes)
        self.assertEqual(result_quotes, ':`User``Test`:`Person`')
    
    def test_collect_node(self):
        """Тест сбора узла"""
        node_data = {
            'element_id': '4:abc123',
            'uri': 'test_uri',
            'description': 'Test description',
            'title': 'Test title'
        }
        node = self.repo.collect_node(node_data)
        self.assertIsInstance(node, TNode)
        self.assertEqual(node.id, '4:abc123')
        self.assertEqual(node.uri, 'test_uri')
        self.assertEqual(node.description, 'Test description')
        self.assertEqual(node.title, 'Test title')
    
    def test_collect_arc(self):
        """Тест сбора связи"""
        arc_data = {
            'element_id': '5:def456',
            'uri': 'RELATES_TO',
            'node_uri_from': 'node1',
            'node_uri_to': 'node2'
        }
        arc = self.repo.collect_arc(arc_data)
        self.assertIsInstance(arc, TArc)
        self.assertEqual(arc.id, '5:def456')
        self.assertEqual(arc.uri, 'RELATES_TO')
        self.assertEqual(arc.node_uri_from, 'node1')
        self.assertEqual(arc.node_uri_to, 'node2')
    
    @patch.object(GraphRepository, '_execute_query')
    def test_get_all_nodes(self, mock_execute):
        """Тест получения всех узлов"""
        mock_execute.return_value = [
            {'element_id': '4:abc123', 'uri': 'uri1', 'description': 'desc1', 'title': 'title1'},
            {'element_id': '4:def456', 'uri': 'uri2', 'description': 'desc2', 'title': 'title2'}
        ]
        
        nodes = self.repo.get_all_nodes()
        self.assertEqual(len(nodes), 2)
        self.assertIsInstance(nodes[0], TNode)
        self.assertEqual(nodes[0].uri, 'uri1')
    
    @patch.object(GraphRepository, '_execute_query')
    def test_get_node_by_uri(self, mock_execute):
        """Тест получения узла по URI"""
        mock_execute.return_value = [
            {'element_id': '4:abc123', 'uri': 'test_uri', 'description': 'test', 'title': 'test'}
        ]
        
        node = self.repo.get_node_by_uri('test_uri')
        self.assertIsInstance(node, TNode)
        self.assertEqual(node.uri, 'test_uri')
        
        # Тест с несуществующим URI
        mock_execute.return_value = []
        node = self.repo.get_node_by_uri('nonexistent')
        self.assertIsNone(node)
    
    @patch.object(GraphRepository, '_execute_query')
    def test_create_node(self, mock_execute):
        """Тест создания узла"""
        mock_execute.return_value = [
            {'element_id': '4:abc123', 'uri': 'node_abc123', 'description': 'Test', 'title': 'Test'}
        ]
        
        params = {'title': 'Test', 'description': 'Test'}
        node = self.repo.create_node(params)
        self.assertIsInstance(node, TNode)
        self.assertEqual(node.title, 'Test')
    
    @patch.object(GraphRepository, '_execute_query')
    def test_create_arc(self, mock_execute):
        """Тест создания связи"""
        mock_execute.return_value = [
            {'element_id': '5:def456', 'uri': 'RELATES_TO', 'node_uri_from': 'node1', 'node_uri_to': 'node2'}
        ]
        
        arc = self.repo.create_arc('node1', 'node2', 'RELATES_TO')
        self.assertIsInstance(arc, TArc)
        self.assertEqual(arc.uri, 'RELATES_TO')
        self.assertEqual(arc.node_uri_from, 'node1')
        self.assertEqual(arc.node_uri_to, 'node2')
    
    @patch('graph_repository.GraphDatabase')
    def test_delete_node_by_uri(self, mock_graph_db):
        """Тест удаления узла"""
        # Создаем mock для session и result
        mock_session = Mock()
        mock_result = Mock()
        mock_summary = Mock()
        mock_summary.counters.nodes_deleted = 1
        mock_result.consume.return_value = mock_summary
        mock_session.run.return_value = mock_result
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        self.repo.driver.session.return_value = mock_session
        
        result = self.repo.delete_node_by_uri('test_uri')
        self.assertTrue(result)
        
        # Тест с несуществующим узлом
        mock_summary.counters.nodes_deleted = 0
        result = self.repo.delete_node_by_uri('nonexistent')
        self.assertFalse(result)
    
    @patch.object(GraphRepository, '_execute_query')
    def test_update_node(self, mock_execute):
        """Тест обновления узла"""
        mock_execute.return_value = [
            {'element_id': '4:abc123', 'uri': 'test_uri', 'description': 'Updated', 'title': 'Test'}
        ]
        
        updated_node = self.repo.update_node('test_uri', {'description': 'Updated'})
        self.assertIsInstance(updated_node, TNode)
        self.assertEqual(updated_node.description, 'Updated')
        
        # Тест с несуществующим узлом
        mock_execute.return_value = []
        updated_node = self.repo.update_node('nonexistent', {'description': 'Updated'})
        self.assertIsNone(updated_node)


class TestTNode(unittest.TestCase):
    """Тесты для TNode"""
    
    def test_tnode_creation(self):
        """Тест создания TNode"""
        node = TNode(
            id='4:abc123',
            uri='test_uri',
            description='Test description',
            title='Test title'
        )
        self.assertEqual(node.id, '4:abc123')
        self.assertEqual(node.uri, 'test_uri')
        self.assertEqual(node.description, 'Test description')
        self.assertEqual(node.title, 'Test title')
        self.assertIsNone(node.arcs)


class TestTArc(unittest.TestCase):
    """Тесты для TArc"""
    
    def test_tarc_creation(self):
        """Тест создания TArc"""
        arc = TArc(
            id='5:def456',
            uri='RELATES_TO',
            node_uri_from='node1',
            node_uri_to='node2'
        )
        self.assertEqual(arc.id, '5:def456')
        self.assertEqual(arc.uri, 'RELATES_TO')
        self.assertEqual(arc.node_uri_from, 'node1')
        self.assertEqual(arc.node_uri_to, 'node2')


if __name__ == '__main__':
    unittest.main()
