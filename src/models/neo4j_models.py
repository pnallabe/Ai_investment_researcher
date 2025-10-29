"""
Neo4j graph models and operations
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass

from .database import neo4j_db

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Base class for graph nodes"""
    id: Optional[int] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class GraphRelationship:
    """Base class for graph relationships"""
    type: str
    start_node: GraphNode
    end_node: GraphNode
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class Neo4jCompanyModel:
    """Neo4j operations for Company nodes"""
    
    @staticmethod
    def create_company(cik: str, name: str, **properties) -> Dict[str, Any]:
        """Create a company node"""
        query = """
        MERGE (c:Company {cik: $cik})
        SET c.name = $name,
            c.created_at = datetime(),
            c += $properties
        RETURN c
        """
        parameters = {
            "cik": cik,
            "name": name,
            "properties": properties
        }
        
        result = neo4j_db.execute_write_query(query, parameters)
        return result.single()["c"] if result.single() else None
    
    @staticmethod
    def get_company_by_cik(cik: str) -> Optional[Dict[str, Any]]:
        """Get company by CIK"""
        query = "MATCH (c:Company {cik: $cik}) RETURN c"
        result = neo4j_db.execute_query(query, {"cik": cik})
        return result.single()["c"] if result.single() else None
    
    @staticmethod
    def create_subsidiary_relationship(parent_cik: str, subsidiary_cik: str, 
                                     ownership_percentage: float = None):
        """Create subsidiary relationship between companies"""
        query = """
        MATCH (parent:Company {cik: $parent_cik})
        MATCH (subsidiary:Company {cik: $subsidiary_cik})
        MERGE (parent)-[r:OWNS_SUBSIDIARY]->(subsidiary)
        SET r.ownership_percentage = $ownership_percentage,
            r.created_at = datetime()
        RETURN r
        """
        parameters = {
            "parent_cik": parent_cik,
            "subsidiary_cik": subsidiary_cik,
            "ownership_percentage": ownership_percentage
        }
        
        neo4j_db.execute_write_query(query, parameters)
    
    @staticmethod
    def create_partnership(company1_cik: str, company2_cik: str, 
                          partnership_type: str = "BUSINESS_PARTNER", **properties):
        """Create partnership relationship"""
        query = f"""
        MATCH (c1:Company {{cik: $company1_cik}})
        MATCH (c2:Company {{cik: $company2_cik}})
        MERGE (c1)-[r:{partnership_type}]->(c2)
        SET r += $properties,
            r.created_at = datetime()
        RETURN r
        """
        parameters = {
            "company1_cik": company1_cik,
            "company2_cik": company2_cik,
            "properties": properties
        }
        
        neo4j_db.execute_write_query(query, parameters)
    
    @staticmethod
    def get_company_relationships(cik: str, relationship_types: List[str] = None) -> List[Dict[str, Any]]:
        """Get all relationships for a company"""
        if relationship_types:
            rel_filter = "|".join(relationship_types)
            query = f"""
            MATCH (c:Company {{cik: $cik}})-[r:{rel_filter}]-(other:Company)
            RETURN type(r) as relationship_type, r as relationship, other as related_company
            """
        else:
            query = """
            MATCH (c:Company {cik: $cik})-[r]-(other:Company)
            RETURN type(r) as relationship_type, r as relationship, other as related_company
            """
        
        result = neo4j_db.execute_query(query, {"cik": cik})
        return [record.data() for record in result]


class Neo4jFilingModel:
    """Neo4j operations for Filing nodes"""
    
    @staticmethod
    def create_filing(accession_number: str, company_cik: str, form_type: str, 
                     filing_date: date, **properties) -> Dict[str, Any]:
        """Create a filing node and link to company"""
        query = """
        MATCH (c:Company {cik: $company_cik})
        CREATE (f:Filing {
            accession_number: $accession_number,
            form_type: $form_type,
            filing_date: date($filing_date),
            created_at: datetime()
        })
        SET f += $properties
        CREATE (c)-[:FILED]->(f)
        RETURN f
        """
        parameters = {
            "accession_number": accession_number,
            "company_cik": company_cik,
            "form_type": form_type,
            "filing_date": filing_date.isoformat(),
            "properties": properties
        }
        
        result = neo4j_db.execute_write_query(query, parameters)
        return result.single()["f"] if result.single() else None
    
    @staticmethod
    def create_company_mention_in_filing(filing_accession: str, mentioned_company_cik: str, 
                                       mention_context: str = None):
        """Create relationship when a company is mentioned in a filing"""
        query = """
        MATCH (f:Filing {accession_number: $filing_accession})
        MATCH (c:Company {cik: $mentioned_company_cik})
        MERGE (f)-[r:MENTIONS]->(c)
        SET r.context = $mention_context,
            r.created_at = datetime()
        RETURN r
        """
        parameters = {
            "filing_accession": filing_accession,
            "mentioned_company_cik": mentioned_company_cik,
            "mention_context": mention_context
        }
        
        neo4j_db.execute_write_query(query, parameters)


class Neo4jNewsModel:
    """Neo4j operations for News nodes"""
    
    @staticmethod
    def create_news_article(url: str, title: str, published_at: datetime, 
                           source: str, **properties) -> Dict[str, Any]:
        """Create a news article node"""
        query = """
        CREATE (a:Article {
            url: $url,
            title: $title,
            published_at: datetime($published_at),
            source: $source,
            created_at: datetime()
        })
        SET a += $properties
        RETURN a
        """
        parameters = {
            "url": url,
            "title": title,
            "published_at": published_at.isoformat(),
            "source": source,
            "properties": properties
        }
        
        result = neo4j_db.execute_write_query(query, parameters)
        return result.single()["a"] if result.single() else None
    
    @staticmethod
    def create_article_mentions_company(article_url: str, company_cik: str, 
                                      sentiment: str = "neutral", relevance_score: float = None):
        """Create relationship when article mentions a company"""
        query = """
        MATCH (a:Article {url: $article_url})
        MATCH (c:Company {cik: $company_cik})
        MERGE (a)-[r:MENTIONS]->(c)
        SET r.sentiment = $sentiment,
            r.relevance_score = $relevance_score,
            r.created_at = datetime()
        RETURN r
        """
        parameters = {
            "article_url": article_url,
            "company_cik": company_cik,
            "sentiment": sentiment,
            "relevance_score": relevance_score
        }
        
        neo4j_db.execute_write_query(query, parameters)


class Neo4jPersonModel:
    """Neo4j operations for Person nodes (executives, analysts, etc.)"""
    
    @staticmethod
    def create_person(name: str, title: str = None, **properties) -> Dict[str, Any]:
        """Create a person node"""
        query = """
        MERGE (p:Person {name: $name})
        SET p.title = $title,
            p.created_at = datetime(),
            p += $properties
        RETURN p
        """
        parameters = {
            "name": name,
            "title": title,
            "properties": properties
        }
        
        result = neo4j_db.execute_write_query(query, parameters)
        return result.single()["p"] if result.single() else None
    
    @staticmethod
    def create_employment_relationship(person_name: str, company_cik: str, 
                                     role: str, start_date: date = None, end_date: date = None):
        """Create employment relationship"""
        query = """
        MATCH (p:Person {name: $person_name})
        MATCH (c:Company {cik: $company_cik})
        MERGE (p)-[r:WORKS_FOR]->(c)
        SET r.role = $role,
            r.start_date = date($start_date),
            r.end_date = date($end_date),
            r.created_at = datetime()
        RETURN r
        """
        parameters = {
            "person_name": person_name,
            "company_cik": company_cik,
            "role": role,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
        
        neo4j_db.execute_write_query(query, parameters)


class Neo4jAnalyticsQueries:
    """Complex analytical queries using Neo4j"""
    
    @staticmethod
    def find_connected_companies(cik: str, max_hops: int = 2) -> List[Dict[str, Any]]:
        """Find companies connected to a given company within max_hops"""
        query = f"""
        MATCH path = (start:Company {{cik: $cik}})-[*1..{max_hops}]-(connected:Company)
        WHERE start <> connected
        RETURN DISTINCT connected.cik as cik, 
               connected.name as name,
               length(path) as distance,
               [rel in relationships(path) | type(rel)] as relationship_path
        ORDER BY distance, connected.name
        """
        
        result = neo4j_db.execute_query(query, {"cik": cik})
        return [record.data() for record in result]
    
    @staticmethod
    def find_companies_mentioned_together(cik: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Find companies frequently mentioned together in news"""
        query = """
        MATCH (target:Company {cik: $cik})<-[:MENTIONS]-(article:Article)
        WHERE article.published_at > datetime() - duration({days: $days_back})
        MATCH (article)-[:MENTIONS]->(other:Company)
        WHERE target <> other
        RETURN other.cik as cik,
               other.name as name,
               count(article) as co_mentions,
               collect(DISTINCT article.title)[0..5] as sample_articles
        ORDER BY co_mentions DESC
        LIMIT 20
        """
        
        result = neo4j_db.execute_query(query, {"cik": cik, "days_back": days_back})
        return [record.data() for record in result]
    
    @staticmethod
    def analyze_sector_sentiment(sector: str, days_back: int = 7) -> Dict[str, Any]:
        """Analyze sentiment for companies in a sector"""
        query = """
        MATCH (c:Company {sector: $sector})<-[m:MENTIONS]-(a:Article)
        WHERE a.published_at > datetime() - duration({days: $days_back})
        RETURN c.name as company_name,
               c.cik as cik,
               count(a) as article_count,
               avg(CASE m.sentiment 
                   WHEN 'positive' THEN 1 
                   WHEN 'negative' THEN -1 
                   ELSE 0 END) as avg_sentiment,
               collect(DISTINCT a.source) as news_sources
        ORDER BY avg_sentiment DESC
        """
        
        result = neo4j_db.execute_query(query, {"sector": sector, "days_back": days_back})
        return [record.data() for record in result]
    
    @staticmethod
    def find_corporate_network_influence(cik: str) -> Dict[str, Any]:
        """Calculate network influence metrics for a company"""
        query = """
        MATCH (center:Company {cik: $cik})
        
        // Count direct connections
        OPTIONAL MATCH (center)--(direct:Company)
        WITH center, count(DISTINCT direct) as direct_connections
        
        // Count second-degree connections
        OPTIONAL MATCH (center)--()--(second:Company)
        WHERE second <> center
        WITH center, direct_connections, count(DISTINCT second) as second_degree_connections
        
        // Count news mentions in last 30 days
        OPTIONAL MATCH (center)<-[:MENTIONS]-(recent_news:Article)
        WHERE recent_news.published_at > datetime() - duration({days: 30})
        WITH center, direct_connections, second_degree_connections, count(recent_news) as recent_mentions
        
        // Count filings in last 90 days
        OPTIONAL MATCH (center)-[:FILED]->(recent_filing:Filing)
        WHERE recent_filing.filing_date > date() - duration({days: 90})
        
        RETURN center.name as company_name,
               center.cik as cik,
               direct_connections,
               second_degree_connections,
               recent_mentions,
               count(recent_filing) as recent_filings,
               (direct_connections * 2 + second_degree_connections + recent_mentions * 0.5) as influence_score
        """
        
        result = neo4j_db.execute_query(query, {"cik": cik})
        return result.single().data() if result.single() else {}


class Neo4jDataLoader:
    """Utilities for loading data into Neo4j"""
    
    @staticmethod
    def batch_create_companies(companies: List[Dict[str, Any]]) -> int:
        """Batch create company nodes"""
        query = """
        UNWIND $companies as company
        MERGE (c:Company {cik: company.cik})
        SET c += company
        SET c.created_at = datetime()
        RETURN count(c) as created_count
        """
        
        result = neo4j_db.execute_write_query(query, {"companies": companies})
        return result.single()["created_count"] if result.single() else 0
    
    @staticmethod
    def batch_create_relationships(relationships: List[Dict[str, Any]]) -> int:
        """Batch create relationships"""
        query = """
        UNWIND $relationships as rel
        MATCH (start:Company {cik: rel.start_cik})
        MATCH (end:Company {cik: rel.end_cik})
        CALL apoc.create.relationship(start, rel.type, rel.properties, end) YIELD rel as created_rel
        RETURN count(created_rel) as created_count
        """
        
        # Note: This requires APOC plugin
        try:
            result = neo4j_db.execute_write_query(query, {"relationships": relationships})
            return result.single()["created_count"] if result.single() else 0
        except Exception as e:
            logger.error(f"Batch relationship creation failed (APOC may not be available): {str(e)}")
            # Fallback to individual creation
            count = 0
            for rel in relationships:
                try:
                    Neo4jCompanyModel.create_partnership(
                        rel["start_cik"], 
                        rel["end_cik"], 
                        rel["type"], 
                        **rel.get("properties", {})
                    )
                    count += 1
                except Exception:
                    continue
            return count
    
    @staticmethod
    def clear_all_data():
        """Clear all data from Neo4j (use with caution!)"""
        query = "MATCH (n) DETACH DELETE n"
        neo4j_db.execute_write_query(query)
        logger.warning("All Neo4j data has been cleared!")
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get database statistics"""
        query = """
        MATCH (n) 
        WITH labels(n) as node_labels, count(n) as node_count
        UNWIND node_labels as label
        WITH label, sum(node_count) as count
        WHERE label IS NOT NULL
        RETURN collect({label: label, count: count}) as node_stats

        UNION

        MATCH ()-[r]->()
        WITH type(r) as rel_type, count(r) as rel_count
        RETURN collect({relationship: rel_type, count: rel_count}) as relationship_stats
        """
        
        result = neo4j_db.execute_query(query)
        stats = {"nodes": {}, "relationships": {}}
        
        for record in result:
            if "node_stats" in record:
                for node_stat in record["node_stats"]:
                    stats["nodes"][node_stat["label"]] = node_stat["count"]
            if "relationship_stats" in record:
                for rel_stat in record["relationship_stats"]:
                    stats["relationships"][rel_stat["relationship"]] = rel_stat["count"]
        
        return stats