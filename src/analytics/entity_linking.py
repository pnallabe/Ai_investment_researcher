"""
Entity linking and relationship extraction module
"""
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity"""
    text: str
    entity_type: str
    confidence: float
    start_pos: int = 0
    end_pos: int = 0
    canonical_name: str = None
    metadata: Dict[str, Any] = None


@dataclass
class EntityRelationship:
    """Represents a relationship between entities"""
    entity1: Entity
    entity2: Entity
    relationship_type: str
    confidence: float
    context: str = ""
    metadata: Dict[str, Any] = None


class EntityExtractor:
    """Extract entities from text documents"""
    
    def __init__(self):
        self.company_patterns = self._load_company_patterns()
        self.person_patterns = self._load_person_patterns()
        self.financial_patterns = self._load_financial_patterns()
        self.location_patterns = self._load_location_patterns()
    
    def _load_company_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for company entity recognition"""
        return [
            {
                "pattern": r'\b([A-Z][a-zA-Z\s&\.,]*(?:Inc|Corp|Corporation|Company|Ltd|Limited|LLC|LP|Co|Group|Holdings|Industries|Systems|Technologies|Solutions|Services|International|Worldwide|Global)\.?)\b',
                "type": "company",
                "confidence": 0.8
            },
            {
                "pattern": r'\b([A-Z][a-zA-Z\s]*\s+(?:Bank|Insurance|Financial|Capital|Investment|Fund|Trust|Securities|Partners|Advisors|Management))\b',
                "type": "financial_institution",
                "confidence": 0.75
            },
            {
                "pattern": r'\b(NYSE:|NASDAQ:|NYSE\s+|NASDAQ\s+)?([A-Z]{2,5})\b(?=\s|$|,|\.)',
                "type": "ticker_symbol",
                "confidence": 0.9
            }
        ]
    
    def _load_person_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for person entity recognition"""
        return [
            {
                "pattern": r'\b((?:Mr|Ms|Mrs|Dr|Prof|CEO|CFO|CTO|COO|Chairman|President|Director|Manager|Analyst)\.?\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
                "type": "person",
                "confidence": 0.7
            },
            {
                "pattern": r'\b(CEO|Chief Executive Officer|CFO|Chief Financial Officer|CTO|Chief Technology Officer|COO|Chief Operating Officer|Chairman|President|Vice President|VP)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
                "type": "executive",
                "confidence": 0.85
            }
        ]
    
    def _load_financial_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for financial entity recognition"""
        return [
            {
                "pattern": r'\$([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s*(million|billion|trillion|M|B|T)?\b',
                "type": "monetary_amount",
                "confidence": 0.9
            },
            {
                "pattern": r'\b([0-9]+(?:\.[0-9]+)?)\s*%\b',
                "type": "percentage",
                "confidence": 0.85
            },
            {
                "pattern": r'\b(Q[1-4]\s+20[0-9]{2}|[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20[0-9]{2})\b',
                "type": "date_period",
                "confidence": 0.8
            }
        ]
    
    def _load_location_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for location entity recognition"""
        return [
            {
                "pattern": r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b',
                "type": "location",
                "confidence": 0.75
            }
        ]
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities from text"""
        entities = []
        
        # Extract different types of entities
        entities.extend(self._extract_by_patterns(text, self.company_patterns))
        entities.extend(self._extract_by_patterns(text, self.person_patterns))
        entities.extend(self._extract_by_patterns(text, self.financial_patterns))
        entities.extend(self._extract_by_patterns(text, self.location_patterns))
        
        # Remove overlapping entities (keep highest confidence)
        entities = self._remove_overlapping_entities(entities)
        
        # Normalize and canonicalize entities
        entities = self._normalize_entities(entities)
        
        return entities
    
    def _extract_by_patterns(self, text: str, patterns: List[Dict[str, Any]]) -> List[Entity]:
        """Extract entities using regex patterns"""
        entities = []
        
        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            entity_type = pattern_info["type"]
            confidence = pattern_info["confidence"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entity_text = match.group().strip()
                
                # Skip very short or common words
                if len(entity_text) < 2 or entity_text.lower() in ["the", "and", "or", "in", "on", "at"]:
                    continue
                
                entity = Entity(
                    text=entity_text,
                    entity_type=entity_type,
                    confidence=confidence,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                
                entities.append(entity)
        
        return entities
    
    def _remove_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping the one with highest confidence"""
        # Sort by start position
        entities.sort(key=lambda e: e.start_pos)
        
        filtered_entities = []
        
        for entity in entities:
            # Check if this entity overlaps with any already selected entity
            overlaps = False
            
            for selected_entity in filtered_entities:
                if (entity.start_pos < selected_entity.end_pos and 
                    entity.end_pos > selected_entity.start_pos):
                    
                    # There's an overlap
                    if entity.confidence > selected_entity.confidence:
                        # Replace the selected entity with this one
                        filtered_entities.remove(selected_entity)
                        filtered_entities.append(entity)
                    
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _normalize_entities(self, entities: List[Entity]) -> List[Entity]:
        """Normalize and canonicalize entity names"""
        for entity in entities:
            if entity.entity_type in ["company", "financial_institution"]:
                # Clean up company names
                canonical_name = entity.text
                canonical_name = re.sub(r'\s+(Inc|Corp|Corporation|Company|Ltd|Limited|LLC|LP)\.?$', '', canonical_name, flags=re.IGNORECASE)
                canonical_name = canonical_name.strip()
                entity.canonical_name = canonical_name
                
            elif entity.entity_type == "ticker_symbol":
                # Extract just the ticker symbol
                ticker_match = re.search(r'([A-Z]{2,5})', entity.text)
                if ticker_match:
                    entity.canonical_name = ticker_match.group(1)
                
            elif entity.entity_type in ["person", "executive"]:
                # Normalize person names
                name_parts = entity.text.split()
                # Remove titles
                titles = ["Mr", "Ms", "Mrs", "Dr", "Prof", "CEO", "CFO", "CTO", "COO", "Chairman", "President", "Director", "Manager", "Analyst"]
                name_parts = [part for part in name_parts if part not in titles]
                entity.canonical_name = " ".join(name_parts)
        
        return entities


class EntityLinker:
    """Link extracted entities to known entities in the database"""
    
    def __init__(self, company_database: Dict[str, Dict[str, Any]] = None):
        self.company_database = company_database or {}
        self.ticker_to_company = {}
        self.name_variations = {}
        
        # Build lookup tables
        self._build_lookup_tables()
    
    def _build_lookup_tables(self):
        """Build lookup tables for entity linking"""
        for cik, company_info in self.company_database.items():
            company_name = company_info.get("name", "")
            tickers = company_info.get("tickers", [])
            
            # Map tickers to company
            for ticker in tickers:
                self.ticker_to_company[ticker] = cik
            
            # Generate name variations
            variations = self._generate_name_variations(company_name)
            for variation in variations:
                if variation not in self.name_variations:
                    self.name_variations[variation] = []
                self.name_variations[variation].append(cik)
    
    def _generate_name_variations(self, company_name: str) -> List[str]:
        """Generate variations of company names for matching"""
        variations = [company_name]
        
        # Remove common suffixes
        base_name = re.sub(r'\s+(Inc|Corp|Corporation|Company|Ltd|Limited|LLC|LP|Co|Group|Holdings|Industries|Systems|Technologies|Solutions|Services|International|Worldwide|Global)\.?$', '', company_name, flags=re.IGNORECASE)
        
        if base_name != company_name:
            variations.append(base_name)
        
        # Add abbreviated forms
        words = base_name.split()
        if len(words) > 1:
            # First word + last word
            variations.append(f"{words[0]} {words[-1]}")
            
            # Acronym
            acronym = "".join([word[0].upper() for word in words if len(word) > 2])
            if len(acronym) >= 2:
                variations.append(acronym)
        
        return variations
    
    def link_entity(self, entity: Entity) -> Optional[Dict[str, Any]]:
        """Link an entity to a known entity in the database"""
        if entity.entity_type == "ticker_symbol" and entity.canonical_name:
            # Direct ticker lookup
            cik = self.ticker_to_company.get(entity.canonical_name.upper())
            if cik:
                return {
                    "linked_cik": cik,
                    "linked_type": "company",
                    "confidence": 0.95,
                    "method": "ticker_lookup"
                }
        
        elif entity.entity_type in ["company", "financial_institution"] and entity.canonical_name:
            # Name-based lookup
            best_match = None
            best_score = 0
            
            for variation in self.name_variations:
                similarity = self._calculate_similarity(entity.canonical_name, variation)
                if similarity > best_score and similarity > 0.8:  # Threshold for matching
                    best_score = similarity
                    best_match = self.name_variations[variation][0]  # Take first match
            
            if best_match:
                return {
                    "linked_cik": best_match,
                    "linked_type": "company",
                    "confidence": best_score,
                    "method": "name_similarity"
                }
        
        return None
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names (simple approach)"""
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # Exact match
        if name1 == name2:
            return 1.0
        
        # Substring match
        if name1 in name2 or name2 in name1:
            shorter = min(len(name1), len(name2))
            longer = max(len(name1), len(name2))
            return shorter / longer
        
        # Jaccard similarity (word-based)
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)


class RelationshipExtractor:
    """Extract relationships between entities"""
    
    def __init__(self):
        self.relationship_patterns = self._load_relationship_patterns()
    
    def _load_relationship_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for relationship extraction"""
        return [
            {
                "pattern": r'({entity1})\s+(?:owns|acquired|purchased|bought)\s+({entity2})',
                "relationship": "OWNS",
                "confidence": 0.8
            },
            {
                "pattern": r'({entity1})\s+(?:partners with|partnered with|joint venture with)\s+({entity2})',
                "relationship": "PARTNERS_WITH",
                "confidence": 0.75
            },
            {
                "pattern": r'({entity1})\s+(?:competes with|competitor of|rival of)\s+({entity2})',
                "relationship": "COMPETES_WITH",
                "confidence": 0.7
            },
            {
                "pattern": r'({entity1})\s+(?:CEO|Chief Executive Officer|President)\s+({entity2})',
                "relationship": "EMPLOYS",
                "confidence": 0.85
            },
            {
                "pattern": r'({entity2})\s+(?:CEO|Chief Executive Officer|President)\s+of\s+({entity1})',
                "relationship": "EMPLOYS",
                "confidence": 0.85
            },
            {
                "pattern": r'({entity1})\s+(?:supplies|supplier to|provides services to)\s+({entity2})',
                "relationship": "SUPPLIES",
                "confidence": 0.75
            }
        ]
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[EntityRelationship]:
        """Extract relationships between entities in text"""
        relationships = []
        
        # Create entity lookup by position
        entity_positions = {(e.start_pos, e.end_pos): e for e in entities}
        
        # Try pattern-based extraction
        for pattern_info in self.relationship_patterns:
            pattern_template = pattern_info["pattern"]
            relationship_type = pattern_info["relationship"]
            confidence = pattern_info["confidence"]
            
            # Replace entity placeholders with actual entity text
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities):
                    if i != j:  # Don't relate entity to itself
                        
                        # Create pattern with actual entity text
                        pattern = pattern_template.replace("{entity1}", re.escape(entity1.text))
                        pattern = pattern.replace("{entity2}", re.escape(entity2.text))
                        
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        
                        for match in matches:
                            relationship = EntityRelationship(
                                entity1=entity1,
                                entity2=entity2,
                                relationship_type=relationship_type,
                                confidence=confidence,
                                context=match.group(),
                                metadata={
                                    "pattern_used": pattern_template,
                                    "match_position": (match.start(), match.end())
                                }
                            )
                            relationships.append(relationship)
        
        # Proximity-based relationship extraction
        proximity_relationships = self._extract_proximity_relationships(entities, text)
        relationships.extend(proximity_relationships)
        
        # Remove duplicates
        relationships = self._deduplicate_relationships(relationships)
        
        return relationships
    
    def _extract_proximity_relationships(self, entities: List[Entity], text: str) -> List[EntityRelationship]:
        """Extract relationships based on entity proximity"""
        relationships = []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda e: e.start_pos)
        
        # Look for entities that appear close together
        for i, entity1 in enumerate(sorted_entities):
            for j in range(i + 1, len(sorted_entities)):
                entity2 = sorted_entities[j]
                
                # Check if entities are within reasonable distance (e.g., same sentence)
                distance = entity2.start_pos - entity1.end_pos
                
                if distance < 200:  # Characters
                    # Extract context between entities
                    context = text[entity1.start_pos:entity2.end_pos]
                    
                    # Infer relationship type based on entity types and context
                    relationship_type = self._infer_relationship_type(entity1, entity2, context)
                    
                    if relationship_type:
                        relationship = EntityRelationship(
                            entity1=entity1,
                            entity2=entity2,
                            relationship_type=relationship_type,
                            confidence=0.5,  # Lower confidence for proximity-based
                            context=context,
                            metadata={
                                "method": "proximity",
                                "distance": distance
                            }
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _infer_relationship_type(self, entity1: Entity, entity2: Entity, context: str) -> Optional[str]:
        """Infer relationship type based on entity types and context"""
        # Company-Person relationships
        if (entity1.entity_type in ["company", "financial_institution"] and 
            entity2.entity_type in ["person", "executive"]):
            if any(word in context.lower() for word in ["ceo", "president", "chairman", "director", "officer"]):
                return "EMPLOYS"
        
        # Company-Company relationships
        elif (entity1.entity_type in ["company", "financial_institution"] and 
              entity2.entity_type in ["company", "financial_institution"]):
            
            if any(word in context.lower() for word in ["merger", "acquisition", "acquired", "bought"]):
                return "ACQUIRED"
            elif any(word in context.lower() for word in ["partnership", "joint venture", "alliance"]):
                return "PARTNERS_WITH"
            elif any(word in context.lower() for word in ["competitor", "rival", "competes"]):
                return "COMPETES_WITH"
        
        # Company-Financial relationships
        elif (entity1.entity_type in ["company", "financial_institution"] and 
              entity2.entity_type == "monetary_amount"):
            if any(word in context.lower() for word in ["revenue", "sales", "earnings", "profit"]):
                return "HAS_REVENUE"
            elif any(word in context.lower() for word in ["investment", "funding", "capital"]):
                return "RECEIVED_FUNDING"
        
        return None
    
    def _deduplicate_relationships(self, relationships: List[EntityRelationship]) -> List[EntityRelationship]:
        """Remove duplicate relationships"""
        seen = set()
        deduplicated = []
        
        for rel in relationships:
            # Create a key for deduplication
            key = (
                rel.entity1.text.lower(),
                rel.entity2.text.lower(),
                rel.relationship_type
            )
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(rel)
            else:
                # If we've seen this relationship, keep the one with higher confidence
                for i, existing_rel in enumerate(deduplicated):
                    existing_key = (
                        existing_rel.entity1.text.lower(),
                        existing_rel.entity2.text.lower(),
                        existing_rel.relationship_type
                    )
                    
                    if existing_key == key and rel.confidence > existing_rel.confidence:
                        deduplicated[i] = rel
                        break
        
        return deduplicated


class EntityLinkingPipeline:
    """Complete entity linking pipeline"""
    
    def __init__(self, company_database: Dict[str, Dict[str, Any]] = None):
        self.extractor = EntityExtractor()
        self.linker = EntityLinker(company_database)
        self.relationship_extractor = RelationshipExtractor()
    
    def process_document(self, text: str, document_id: str = None) -> Dict[str, Any]:
        """Process a document and extract entities and relationships"""
        try:
            # Extract entities
            entities = self.extractor.extract_entities(text)
            
            # Link entities to known entities
            linked_entities = []
            for entity in entities:
                link_info = self.linker.link_entity(entity)
                entity_data = {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence,
                    "canonical_name": entity.canonical_name,
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos,
                    "linked_info": link_info
                }
                linked_entities.append(entity_data)
            
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(text, entities)
            
            relationship_data = []
            for rel in relationships:
                rel_data = {
                    "entity1_text": rel.entity1.text,
                    "entity2_text": rel.entity2.text,
                    "relationship_type": rel.relationship_type,
                    "confidence": rel.confidence,
                    "context": rel.context,
                    "metadata": rel.metadata
                }
                relationship_data.append(rel_data)
            
            result = {
                "document_id": document_id,
                "entities": linked_entities,
                "relationships": relationship_data,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "stats": {
                    "total_entities": len(entities),
                    "linked_entities": len([e for e in linked_entities if e["linked_info"]]),
                    "total_relationships": len(relationships)
                }
            }
            
            logger.info(f"Processed document: {len(entities)} entities, {len(relationships)} relationships")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "document_id": document_id,
                "entities": [],
                "relationships": [],
                "error": str(e),
                "processing_timestamp": datetime.utcnow().isoformat()
            }