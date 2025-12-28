"""
Knowledge Graph Engine.
Maps relationships between ingredients, health conditions, and medical profiles.
Enables intelligent conflict detection beyond simple text matching.
"""

import networkx as nx
from typing import List, Dict, Any, Set, Tuple
from database.db_manager import get_db_manager
from models.schemas import GraphConflict


class GraphEngine:
    """Knowledge Graph for health-ingredient relationships."""
    
    def __init__(self):
        """Initialize graph engine with access to hybrid database."""
        self.db = get_db_manager()
        self.graph = self.db.graph
        self.cache = {}
    
    def find_hidden_conflicts(
        self,
        ingredients: List[str],
        medical_conditions: List[str],
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Advanced conflict detection using knowledge graph.
        Goes beyond simple pattern matching to find indirect relationships.
        """
        conflicts = []
        
        # Direct conflicts (ingredient -> medical condition)
        direct_conflicts = self._find_direct_conflicts(ingredients, medical_conditions)
        conflicts.extend(direct_conflicts)
        
        # Indirect conflicts (ingredient -> related condition -> user's condition)
        indirect_conflicts = self._find_indirect_conflicts(
            ingredients, medical_conditions
        )
        conflicts.extend(indirect_conflicts)
        
        # Allergy conflicts
        allergy_conflicts = self._find_allergy_conflicts(ingredients, allergies)
        conflicts.extend(allergy_conflicts)
        
        # Dedup by (ingredient, condition) pair
        seen = set()
        unique_conflicts = []
        for conflict in conflicts:
            key = (conflict['ingredient'], conflict['health_condition'])
            if key not in seen:
                seen.add(key)
                unique_conflicts.append(conflict)
        
        return unique_conflicts
    
    def _find_direct_conflicts(
        self,
        ingredients: List[str],
        medical_conditions: List[str]
    ) -> List[Dict[str, Any]]:
        """Find direct ingredient -> health condition conflicts."""
        conflicts = []
        
        for ingredient in ingredients:
            ingredient_normalized = self._normalize(ingredient)
            
            if ingredient_normalized not in self.graph:
                continue
            
            # Get all direct successors of this ingredient
            successors = list(self.graph.successors(ingredient_normalized))
            
            for successor in successors:
                # Check if this successor matches any user condition
                for condition in medical_conditions:
                    if self._similarity_match(successor, condition):
                        edge_data = self.graph.edges.get(
                            (ingredient_normalized, successor), {}
                        )
                        conflicts.append({
                            'ingredient': ingredient,
                            'health_condition': condition,
                            'relationship': edge_data.get('relationship', 'affects'),
                            'severity': edge_data.get('severity', 'medium'),
                            'direct': True,
                        })
                        break
        
        return conflicts
    
    def _find_indirect_conflicts(
        self,
        ingredients: List[str],
        medical_conditions: List[str]
    ) -> List[Dict[str, Any]]:
        """Find indirect conflicts using paths in the graph."""
        conflicts = []
        
        for ingredient in ingredients:
            ingredient_normalized = self._normalize(ingredient)
            
            if ingredient_normalized not in self.graph:
                continue
            
            for condition in medical_conditions:
                condition_normalized = self._normalize(condition)
                
                # Find all paths from ingredient to related health nodes
                try:
                    # Use BFS to find shortest paths (max 3 hops)
                    paths = self._find_paths_bfs(
                        ingredient_normalized, condition_normalized, max_depth=3
                    )
                    
                    for path in paths:
                        if len(path) > 2:  # Only count indirect (length > 2)
                            severity = self._calculate_path_severity(path)
                            conflicts.append({
                                'ingredient': ingredient,
                                'health_condition': condition,
                                'relationship': f"indirect ({' -> '.join(path[1:-1])})",
                                'severity': severity,
                                'direct': False,
                                'path': path,
                            })
                except:
                    pass
        
        return conflicts
    
    def _find_allergy_conflicts(
        self,
        ingredients: List[str],
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        """Check if ingredients match known allergens."""
        conflicts = []
        
        common_allergens = {
            'peanut': ['peanut', 'groundnut', 'arachis'],
            'tree_nut': ['almond', 'walnut', 'cashew', 'pecan', 'macadamia'],
            'milk': ['milk', 'dairy', 'lactose', 'whey', 'casein'],
            'egg': ['egg', 'ovomucin'],
            'fish': ['fish', 'anchovy', 'cod', 'salmon'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'clam', 'oyster'],
            'soy': ['soy', 'soybean', 'tofu'],
            'wheat': ['wheat', 'gluten', 'barley', 'rye'],
        }
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()
            
            for allergy in allergies:
                allergy_lower = allergy.lower().strip()
                
                # Check direct match
                if allergy_lower in ingredient_lower:
                    conflicts.append({
                        'ingredient': ingredient,
                        'health_condition': f"Allergy: {allergy}",
                        'relationship': 'allergen_present',
                        'severity': 'high',
                        'direct': True,
                    })
                    continue
                
                # Check allergen family
                for allergen_type, variants in common_allergens.items():
                    if any(variant in ingredient_lower for variant in variants):
                        if self._similarity_match(allergen_type, allergy_lower):
                            conflicts.append({
                                'ingredient': ingredient,
                                'health_condition': f"Allergy: {allergy}",
                                'relationship': f'allergen_family ({allergen_type})',
                                'severity': 'high',
                                'direct': True,
                            })
                            break
        
        return conflicts
    
    def _find_paths_bfs(
        self,
        source: str,
        target: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        """Find paths between nodes using BFS."""
        if source not in self.graph or target not in self.graph:
            return []
        
        paths = []
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current == target:
                paths.append(path)
                continue
            
            for neighbor in self.graph.successors(current):
                if neighbor not in visited or len(path) < max_depth:
                    queue.append((neighbor, path + [neighbor]))
        
        return paths
    
    def _calculate_path_severity(self, path: List[str]) -> str:
        """Calculate severity based on path edges."""
        if len(path) < 2:
            return 'low'
        
        severities = []
        for i in range(len(path) - 1):
            edge_data = self.graph.edges.get((path[i], path[i + 1]), {})
            severities.append(edge_data.get('severity', 'medium'))
        
        # If any edge is 'high', path is high severity
        if 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        return 'low'
    
    def _normalize(self, text: str) -> str:
        """Normalize text for graph matching."""
        return text.lower().strip().replace(' ', '_')
    
    def _similarity_match(self, text1: str, text2: str) -> bool:
        """Simple similarity matching."""
        norm1 = self._normalize(text1)
        norm2 = self._normalize(text2)
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # Substring match
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # Levenshtein-like simple check
        return self._string_similarity(norm1, norm2) > 0.7
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Simple similarity score (0-1)."""
        if not s1 or not s2:
            return 0.0
        
        # Count common characters
        common = sum(1 for c in s1 if c in s2)
        return common / max(len(s1), len(s2))
    
    def add_relationship(
        self,
        source: str,
        target: str,
        relationship: str,
        severity: str
    ) -> bool:
        """Add new relationship to the knowledge graph."""
        try:
            source_norm = self._normalize(source)
            target_norm = self._normalize(target)
            
            self.graph.add_edge(
                source_norm, target_norm,
                relationship=relationship,
                severity=severity
            )
            
            # Clear cache
            self.cache.clear()
            return True
        except Exception as e:
            print(f"❌ Error adding relationship: {e}")
            return False
    
    def get_related_conditions(self, ingredient: str) -> List[str]:
        """Get all health conditions related to an ingredient."""
        ingredient_norm = self._normalize(ingredient)
        
        if ingredient_norm not in self.graph:
            return []
        
        # Get all successors
        successors = list(self.graph.successors(ingredient_norm))
        return [s.replace('_', ' ') for s in successors]
    
    def get_graph_metrics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(1, self.graph.number_of_nodes()),
        }
    
    def export_graph(self) -> Dict[str, Any]:
        """Export graph in JSON format for visualization."""
        nodes = [
            {'id': node, 'label': node.replace('_', ' ')}
            for node in self.graph.nodes()
        ]
        edges = [
            {
                'source': u,
                'target': v,
                'relationship': data.get('relationship', ''),
                'severity': data.get('severity', 'medium'),
            }
            for u, v, data in self.graph.edges(data=True)
        ]
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': self.get_graph_metrics(),
        }


# Global instance
graph_engine = None


def get_graph_engine() -> GraphEngine:
    """Get or create global graph engine instance."""
    global graph_engine
    if graph_engine is None:
        graph_engine = GraphEngine()
    return graph_engine
