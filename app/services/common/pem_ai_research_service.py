"""
    Peace Enablers Matrix AI Research Service
    Independent research-based scoring with evidence tracking
"""
import re
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.services.common.llm_factory import llm_factory
logger = logging.getLogger(__name__)

class PEMResearchService:
    """AI service that conducts independent research and evidence-based scoring"""

    def __init__(self):
        self.llm = None
        self._initialized = False
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    async def initialize(self):
        """Initialize the LLM with retry logic"""
        if self._initialized:
            return

        for attempt in range(self.max_retries):
            try:
                self.llm = llm_factory.create_llm()
                self._initialized = True
                logger.info(f"✅ PEM AI Research Service initialized with {settings.LLM_PROVIDER}")
                return
            except Exception as e:
                logger.error(f"Initialization attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise RuntimeError(f"Failed to initialize after {self.max_retries} attempts: {e}")

    async def _ensure_initialized(self):
        """Ensure LLM is initialized before use"""
        if not self._initialized or self.llm is None:
            await self.initialize()

    async def research_and_score_question(
    self,
    city_name: str,
    city_address: str,
    pillarID: int,
    pillar_name: str,
    question_text: str,
    evaluator_score: Optional[float] = None,
    year: int = None
) -> Dict[str, Any]:

        try:
            await self._ensure_initialized()

            if year is None:
                year = datetime.now().year
                            
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_pem_question_system_prompt()),
                ("user", """
                City: {city_name}
                Address: {city_address}
                Pillar: {pillar_name}
                Question: {question_text}
                Evaluator Score:{evaluator_score}
                Year: {year}
                Conduct research strictly under the Peace Enablers Matrix governance protocol.
                Return ONLY valid JSON.
                """)
                        ])

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "city_name": city_name,
                        "city_address": city_address,
                        "pillar_name": pillar_name,
                        "question_text": question_text,
                        "evaluator_score":evaluator_score,
                        "year": year
                    })

                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)

                    return {
                            "success": True,
                            "CityID": None,  # assign externally
                            "PillarID": pillarID,
                            "Year": year,

                            "AIScore": analysis.get("ai_score"),
                            "ConfidenceLevel": analysis.get("confidence_level"),

                            "StructuralEvidence": analysis.get("structural_evidence"),
                            "OperationalEvidence": analysis.get("operational_evidence"),
                            "OutcomeEvidence": analysis.get("outcome_evidence"),
                            "PerceptionEvidence": analysis.get("perception_evidence"),
                            "EvidenceSummary": analysis.get("evidence_summary"),

                            "TemporalScope": analysis.get("temporal_scope"),
                            "DistortionScreening": analysis.get("distortion_screening"),
                            "RelationalDependencies": analysis.get("relational_dependencies"),

                            "StressPoliticalShock": analysis.get("stress_political_shock"),
                            "StressEconomicShock": analysis.get("stress_economic_shock"),
                            "StressNarrativeShock": analysis.get("stress_narrative_shock"),
                            "StressOverallResilienceShock": analysis.get("stress_overall_resilience_shock"),

                            "InequalityAdjustment": analysis.get("inequality_adjustment"),
                            "OpacityRisk": analysis.get("opacity_risk"),
                            "NonCompensationNote": analysis.get("non_compensation_note"),

                            "RedFlag": analysis.get("red_flag"),

                            "SourceName": analysis.get("source_name"),
                            "SourceType": analysis.get("source_type"),
                            "SourceURL": analysis.get("source_url"),
                            "SourceDataYear": analysis.get("source_data_year"),
                            "SourceHierarchyLevel": analysis.get("source_hierarchy_level"),
                            "SourceDataExtract": analysis.get("source_data_extract"),

                            "SourcesConsulted": analysis.get("sources_consulted"),

                            "ConfidenceExplanation": analysis.get("confidence_explanation")
                    }

                except Exception:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def research_and_score_pillar(
    self,
    city_name: str,
    city_address: str,
    pillarId: int,
    pillar_name: str,
    question_text: str,
    evaluator_score: Optional[float] = None,
    existing_ai_score: Optional[float] = None,
    year: int = None
) -> Dict[str, Any]:

        try:
            await self._ensure_initialized()

            if year is None:
                year = datetime.now().year
                
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_pem_pillar_system_prompt()),
                ("user", """
            City: {city_name}
            Address: {city_address}
            Pillar: {pillar_name}
            Question: {question_text}
            Year: {year}
            Evaluator Score: {evaluator_score}
            Existing AI Score: {existing_ai_score}
            Evaluate this pillar question using the Peace Enablers Matrix methodology.

            Return ONLY valid JSON.
            """)
            ])

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "city_name": city_name,
                        "city_address": city_address,
                        "pillar_name": pillar_name,
                        "question_text": question_text,
                        "year": year,
                        "evaluator_score": evaluator_score,
                        "existing_ai_score": existing_ai_score
                    })                    
                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)

                    return {
                        "success": True,
                        "CityID": None,
                        "PillarID": pillarId,
                        "Year": year,
                        "AIScore": analysis.get("AIScore"),
                        "AIProgress": analysis.get("AIProgress"),
                        "ConfidenceLevel": analysis.get("ConfidenceLevel"),
                        "StructuralEvidence": analysis.get("StructuralEvidence"),
                        "EvidenceSummary": analysis.get("EvidenceSummary"),
                        "OperationalEvidence": analysis.get("OperationalEvidence"),
                        "OutcomeEvidence": analysis.get("OutcomeEvidence"),
                        "PerceptionEvidence": analysis.get("PerceptionEvidence"),
                        "TemporalScope": analysis.get("TemporalScope"),
                        "DistortionScreening": analysis.get("DistortionScreening"),
                        "RelationalIntegrity": analysis.get("RelationalIntegrity"),
                        "StressPoliticalShock": analysis.get("StressPoliticalShock"),
                        "StressEconomicShock": analysis.get("StressEconomicShock"),
                        "StressNarrativeShock": analysis.get("StressNarrativeShock"),
                        "StressOverallResilience": analysis.get("StressOverallResilience"),
                        "StressScoreAdjustment": analysis.get("StressScoreAdjustment"),
                        "InequalityAdjustment": analysis.get("InequalityAdjustment"),
                        "OpacityRisk": analysis.get("OpacityRisk"),
                        "NonCompensationNote": analysis.get("NonCompensationNote"),
                        "GeographicEquityNote": analysis.get("GeographicEquityNote"),
                        "InstitutionalAssessment": analysis.get("InstitutionalAssessment"),
                        "DataGapAnalysis": analysis.get("DataGapAnalysis"),
                        "RedFlag": analysis.get("RedFlag"),
                        "Sources": analysis.get("Sources", [])
                    }

                except Exception as ex:
                    logger.error(f"Attempt {attempt+1} failed in research_and_score_pillar: {str(ex)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

        except Exception as e:
         return {"success": False, "error": str(e)}
    
    async def research_and_score_city(
    self,
    city_name: str,
    city_address: str,
    evaluator_score: Optional[float] = None,
    existing_ai_score: Optional[float] = None,
    pillar_with_scores: Optional[str] = None,
    year: int = None
) -> Dict[str, Any]:

        try:
            await self._ensure_initialized()

            if year is None:
                year = datetime.now().year

            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_pem_city_system_prompt()),
                ("user", """
                    City: {city_name}
                    Address: {city_address}
                    Year: {year}

                    Evaluator Score: {evaluator_score}
                    Existing AI Score: {existing_ai_score}

                    Pillar Scores:
                    {pillar_with_scores}

                    Synthesize all 23 pillars using the Peace Enablers Matrix.

                    Return ONLY valid JSON.
                    """)
            ])

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "city_name": city_name,
                        "city_address": city_address,
                        "year": year,
                        "evaluator_score": evaluator_score,
                        "existing_ai_score": existing_ai_score,
                        "pillar_with_scores": pillar_with_scores
                    })

                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)

                    return {
                        "success": True,
                        "CityID": None,
                        "Year": year,
                        "AIScore": analysis.get("AIScore"),
                        "AIProgress": analysis.get("AIProgress"),
                        "EvaluatorScore": analysis.get("EvaluatorScore"),
                        "Discrepancy": analysis.get("Discrepancy"),
                        "ConfidenceLevel": analysis.get("ConfidenceLevel"),
                        "EvidenceSummary": analysis.get("EvidenceSummary"),
                        "StructuralEvidence": analysis.get("StructuralEvidence"),
                        "OperationalEvidence": analysis.get("OperationalEvidence"),
                        "OutcomeEvidence": analysis.get("OutcomeEvidence"),
                        "PerceptionEvidence": analysis.get("PerceptionEvidence"),
                        "TemporalScope": analysis.get("TemporalScope"),
                        "DistortionScreening": analysis.get("DistortionScreening"),
                        "PoliticalShock": analysis.get("PoliticalShock"),
                        "EconomicShock": analysis.get("EconomicShock"),
                        "NarrativeShock": analysis.get("NarrativeShock"),
                        "OverallStressResilience": analysis.get("OverallStressResilience"),
                        "StressScoreAdjustment": analysis.get("StressScoreAdjustment"),
                        "InequalityAdjustment": analysis.get("InequalityAdjustment"),
                        "OpacityRisk": analysis.get("OpacityRisk"),
                        "NonCompensationNote": analysis.get("NonCompensationNote"),
                        "CrossPillarPatterns": analysis.get("CrossPillarPatterns"),
                        "RelationalIntegrity": analysis.get("RelationalIntegrity"),
                        "InstitutionalCapacity": analysis.get("InstitutionalCapacity"),
                        "EquityAssessment": analysis.get("EquityAssessment"),
                        "ConflictRiskOutlook": analysis.get("ConflictRiskOutlook"),
                        "StrategicRecommendation": analysis.get("StrategicRecommendation"),
                        "DataTransparencyNote": analysis.get("DataTransparencyNote"),
                        "PrimarySource": analysis.get("PrimarySource")
                    }

                except Exception as ex:
                    logger.error(f"Attempt {attempt+1} failed in research_and_score_city: {str(ex)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

        except Exception as e:
         return {"success": False, "error": str(e)}
    
    # ==================== VALIDATION METHODS ====================
    def _validate_question_response(self, data: Dict) -> Dict:
            """Validate and sanitize AIPillarScores response"""

            required_fields = [
                "ai_score",
                "confidence_level",
                "evidence_summary",
                "structural_evidence",
                "operational_evidence",
                "outcome_evidence",
                "perception_evidence",
                "temporal_scope",
                "distortion_screening",
                "relational_integrity",
                "stress_political_shock",
                "stress_economic_shock",
                "stress_narrative_shock",
                "stress_overall_resilience",
                "stress_score_adjustment",
                "inequality_adjustment",
                "opacity_risk",
                "non_compensation_note",
                "geographic_equity_note",
                "institutional_assessment",
                "data_gap_analysis"
            ]

            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate ai_score
            if not isinstance(data["ai_score"], (int, float)):
                raise ValueError("ai_score must be numeric")

            if not (0 <= float(data["ai_score"]) <= 4):
                raise ValueError(f"ai_score must be between 0 and 4")

            # Validate confidence level
            if data["confidence_level"] not in ["High", "Medium", "Low"]:
                logger.warning(
                    f"Invalid confidence level: {data['confidence_level']}, defaulting to 'Medium'"
                )
                data["confidence_level"] = "Medium"

                return data
   
    def _validate_pillar_response(self, data: Dict) -> Dict:
        """Validate pillar-level synthesis for AIPillarScores"""

        required_fields = [
            "ai_score",
            "confidence_level",
            "evidence_summary",
            "institutional_assessment",
            "data_gap_analysis"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if not (0 <= float(data["ai_score"]) <= 4):
            raise ValueError("ai_score must be between 0 and 4")

        if data["confidence_level"] not in ["High", "Medium", "Low"]:
            data["confidence_level"] = "Medium"

        return data


    def _validate_city_response(self, data: Dict) -> Dict:
        """Validate AICityScores response"""
        required_fields = [
            "ai_score",
            "confidence_level",
            "evidence_summary",
            "cross_pillar_patterns",
            "institutional_capacity",
            "equity_assessment",
            "conflict_risk_outlook",
            "strategic_recommendation",
            "data_transparency_note",
            "political_shock",
            "economic_shock",
            "narrative_shock",
            "overall_stress_resilience",
            "stress_score_adjustment",
            "inequality_adjustment",
            "opacity_risk",
            "non_compensation_note"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if not (0 <= float(data["ai_score"]) <= 4):
            raise ValueError("ai_score must be between 0 and 4")

        if data["confidence_level"] not in ["High", "Medium", "Low"]:
            data["confidence_level"] = "Medium"

        return data
    
# ==================== UTILITY METHODS ====================

    def _calculate_discrepancy(
        self, 
        ai_progress: float, 
        evaluator_score: Optional[float]
    ) -> float:
        """Calculate discrepancy between AI and evaluator scores"""
        if evaluator_score is not None:

            return abs(ai_progress - evaluator_score)
        return ai_progress
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract valid JSON.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        response = response.strip()
        
        # Remove ```json and ``` markers
        if response.startswith('```'):
            response = response.split('```', 2)[1]
            if response.startswith('json'):
                response = response[4:]
            response = response.strip()
        
        # Find JSON object boundaries
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No valid JSON object found in response")
        
        json_str = response[start_idx:end_idx + 1]
        
        # Replace smart quotes and special characters
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")
        json_str = json_str.replace('–', '-').replace('—', '-')
        json_str = json_str.replace('…', '...')
        
        # Remove control characters (but keep newlines for now)
        json_str = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', json_str)
        
        # Try to parse to validate
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error at position {e.pos}: {e.msg}")
            
            # Show error context
            start = max(0, e.pos - 100)
            end = min(len(json_str), e.pos + 100)
            logger.warning(f"Context: ...{json_str[start:end]}...")
            
            # Try to fix common issues
            json_str_fixed = self._fix_json_escaping(json_str)
            
            try:
                json.loads(json_str_fixed)
                logger.info("Successfully fixed JSON")
                return json_str_fixed
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to fix JSON: {e2.msg} at position {e2.pos}")
                logger.error(f"Problematic JSON (first 500 chars):\n{json_str[:500]}")
                raise ValueError(f"Could not parse JSON: {e2.msg} at position {e2.pos}")

    def _fix_json_escaping(self, json_str: str) -> str:
        """
        Fix escaping issues in JSON string values.
        
        Args:
            json_str: JSON string that may have escaping issues
            
        Returns:
            Fixed JSON string
        """
        result = []
        i = 0
        in_string = False
        
        while i < len(json_str):
            char = json_str[i]
            
            # Detect string boundaries (unescaped quotes)
            if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            # Inside a string value
            if in_string:
                # Handle backslash sequences
                if char == '\\' and i + 1 < len(json_str):
                    next_char = json_str[i + 1]
                    
                    # Valid escape sequences
                    if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u']:
                        result.append(char)
                        result.append(next_char)
                        i += 2
                        continue
                    # Escaped single quote - not needed in JSON, remove backslash
                    elif next_char == "'":
                        result.append("'")
                        i += 2
                        continue
                    # Invalid escape - keep the backslash and char
                    else:
                        result.append('\\')
                        result.append('\\')
                        i += 1
                        continue
                # Handle unescaped special characters
                elif char == '\n':
                    result.append('\\n')
                    i += 1
                elif char == '\r':
                    result.append('\\r')
                    i += 1
                elif char == '\t':
                    result.append('\\t')
                    i += 1
                else:
                    result.append(char)
                    i += 1
            else:
                # Outside strings, keep as is
                result.append(char)
                i += 1
        
        return ''.join(result)
    
    # ==================== PROMPT TEMPLATES ====================
   


    def _get_pem_question_system_prompt(self) -> str:
        return """
    You are the analytical engine of the Peace Enablers Matrix (PEM).

    MISSION:
    Evaluate systemic peace capacity for a specific question within a defined pillar.
    You are NOT measuring incident counts or tranquility.
    You are assessing structural alignment, institutional coherence, and stress resilience.

    --------------------------------------------------
    I. TEMPORAL JURISDICTION RULE
    --------------------------------------------------
    - Primary evaluation window: 1950 to Present.
    - Pre-1950 history may only be used if it directly shapes post-1950 institutions or narratives.
    - No scoring may rely exclusively on pre-1950 events.
    - All evidence must specify timeframe.

    --------------------------------------------------
    II. EVIDENCE HIERARCHY (MANDATORY)
    --------------------------------------------------
    Use minimum TWO independent sources.

    Priority order:
    Tier 7 - Laws, official gazettes, budget documents, court rulings
    Tier 6 - Auditor reports, ombudsman findings, anti-corruption bodies
    Tier 5 - Multilateral agencies, development banks, international monitoring bodies
    Tier 4 - Peer-reviewed academic research
    Tier 3 - Verified civil society datasets
    Tier 2 - Technical or geospatial or private sector data
    Tier 1 - Media (context only, NOT primary evidence)

    Rules:
    - Structural and operational evidence outweigh perception.
    - Media cannot be primary proof.
    - City-specific evidence preferred over national averages.

    --------------------------------------------------
    III. FOUR-LAYER EVIDENCE REQUIREMENT
    --------------------------------------------------
    You MUST analyze:

    1. Structural evidence (laws, mandates, institutional frameworks)
    2. Operational evidence (budgets, staffing, enforcement patterns)
    3. Outcome evidence (measured results, service delivery)
    4. Perception evidence (trust, grievance, participation)

    Perception refines analysis but never overrides structural fact.

    --------------------------------------------------
    IV. DISTORTION SCREENING
    --------------------------------------------------
    Test for:

    - Election-cycle manipulation
    - Artificially low complaint reporting
    - Abrupt statistical improvements
    - Restricted data environments
    - Politically curated datasets

    If verification fails → assign "Unknown".

    --------------------------------------------------
    V. GEOGRAPHIC AND INEQUALITY TEST
    --------------------------------------------------
    Check for:

    - Regional disparities
    - Identity-based exclusion
    - Core vs peripheral variation
    - Income inequality impact

    If severe disparities exist → downward adjustment required.

    --------------------------------------------------
    VI. RELATIONAL INTEGRITY TEST
    --------------------------------------------------
    This pillar must be tested against:

    - Elite cohesion
    - Fiscal capacity
    - Justice mechanisms
    - Administrative execution
    - Security restraint
    - Information ecosystems
    - Environmental pressure
    - Gender order
    - External pressures

    If apparent strength depends on weak supporting domains → adjust downward.

    --------------------------------------------------
    VII. STRESS SIMULATION (MANDATORY)
    --------------------------------------------------
    Test this pillar under:

    1. Political shock
    2. Economic shock
    3. Narrative shock

    If the pillar would not remain functional under stress → score must reflect fragility.

    --------------------------------------------------
    VIII. SCORING GRID (STRICT)
    --------------------------------------------------

    4 - Strong and stress-resilient  
    3 - Functioning but uneven  
    2 - Mixed and vulnerable  
    1 - Structurally weak  
    0 - Absent or destabilizing  
    Unknown - Insufficient verified data  

    --------------------------------------------------
    OUTPUT REQUIREMENTS (STRICT JSON ONLY)
    --------------------------------------------------

    Return ONLY:

    {{
    "ai_score": "0-4 or Unknown",
    "confidence_level": "High|Medium|Low",
    "structural_evidence": "",
    "operational_evidence": "",
    "outcome_evidence": "",
    "perception_evidence": "",
    "evidence_summary": "",
    "temporal_scope": "",
    "distortion_screening": "",
    "relational_dependencies": "",
    "stress_political_shock": "",
    "stress_economic_shock": "",
    "stress_narrative_shock": "",
    "stress_overall_resilience_shock": "",
    "inequality_adjustment": "",
    "opacity_risk": "",
    "non_compensation_note": "",
    "red_flag": "",
    "source_name": "",
    "source_type": "",
    "source_url": "",
    "source_data_year": "",
    "source_hierarchy_level": "",
    "source_data_extract": "",
    "sources_consulted": "",
    "confidence_explanation": ""
    }}

    --------------------------------------------------
    JSON OUTPUT FORMAT REQUIREMENTS
    --------------------------------------------------

    CRITICAL: The response MUST be valid, parseable JSON. Follow these rules STRICTLY:

    1. Use ONLY straight double quotes (") for all JSON keys and string values.
    2. Do NOT use smart quotes or curly quotes.
    3. Escape all special characters in string values:
    - Newlines: \\n
    - Tabs: \\t
    - Quotes within strings: \\" 
    - Backslashes: \\\\
    4. Do NOT include actual line breaks inside string values.
    5. Use regular hyphens (-) not em-dashes or en-dashes.
    6. Use ASCII characters only. Avoid Unicode characters or typographic symbols.
    7. Ensure every string value is properly closed with quotes.
    8. Ensure the JSON object ends with a closing brace }}.
    9. Keep responses concise to avoid truncation.

    --------------------------------------------------
    FAILURE HANDLING
    --------------------------------------------------

    If the response risks truncation, exceeds limits, or violates JSON rules → return {{}} only.
    """

    def _get_pem_pillar_system_prompt(self) -> str:
        return """
    You are evaluating one Peace Enabler pillar within the Peace Enablers Matrix (PEM).

    Your task is to assess systemic peace capacity — not performance optics.

    Apply ALL governance rules from the AI Master Governance Protocol.

    You MUST:

    1. Apply Temporal Jurisdiction Rule (1950-present)
    2. Use minimum two independent sources
    3. Apply Four-Layer Evidence model
    4. Conduct distortion screening
    5. Conduct relational integrity test
    6. Conduct stress simulation (political, economic, narrative)
    7. Apply inequality adjustment if needed
    8. Apply non-compensation rule

    --------------------------------------------------
    SCORING SCALE (STRICT)
    --------------------------------------------------

    4 - Strong and stress-resilient
    3 - Functioning but uneven
    2 - Mixed and vulnerable
    1 - Structurally weak
    0 - Absent or destabilizing
    Unknown - Insufficient verified data

    --------------------------------------------------
    RETURN STRICT JSON (MATCHING AIPillarScores)
    --------------------------------------------------

    {{
    "AIScore": "0-4 or Unknown",
    "AIProgress": 0-100,
    "ConfidenceLevel": "High|Medium|Low",
    "StructuralEvidence": "",
    "EvidenceSummary": "",
    "OperationalEvidence": "",
    "OutcomeEvidence": "",
    "PerceptionEvidence": "",
    "TemporalScope": "",
    "DistortionScreening": "",
    "RelationalIntegrity": "",
    "StressPoliticalShock": "",
    "StressEconomicShock": "",
    "StressNarrativeShock": "",
    "StressOverallResilience": "",
    "StressScoreAdjustment": "",
    "InequalityAdjustment": "",
    "OpacityRisk": "",
    "NonCompensationNote": "",
    "GeographicEquityNote": "",
    "InstitutionalAssessment": "",
    "DataGapAnalysis": "",
    "RedFlag": "",
    "Sources": [
        {{
        "SourceType": "",
        "SourceName": "",
        "SourceURL": "",
        "SourceDataYear": "",
        "SourceHierarchyLevel": "",
        "SourceDataExtract": ""
        }}
    ]
    }}

    --------------------------------------------------
    JSON OUTPUT FORMAT REQUIREMENTS
    --------------------------------------------------

    CRITICAL: The response MUST be valid, parseable JSON. Follow these rules STRICTLY:

    1. Use ONLY straight double quotes (") for all JSON keys and string values.
    2. Do NOT use smart quotes (" "), curly quotes, or any Unicode quote variants.
    3. Escape all special characters in string values:
    - Newlines: \\n
    - Tabs: \\t
    - Quotes within strings: \\" 
    - Backslashes: \\\\
    4. Do NOT include actual line breaks inside string values.
    5. Use regular hyphens (-) not em-dashes (—) or en-dashes (–).
    6. Use ASCII characters only. Avoid Unicode characters such as smart apostrophes or typographic symbols.
    7. Ensure all string values are properly closed with quotes.
    8. Ensure the JSON object ends with a closing brace }}.
    9. Keep responses concise to avoid truncation.

    --------------------------------------------------
    FAILURE HANDLING
    --------------------------------------------------

    If the response risks truncation, exceeds limits, or violates JSON rules, return {{}} only.
    """

    def _get_pem_city_system_prompt(self) -> str:
        return """
    You are synthesizing all 23 Peace Enabler pillars into a systemic city-level peace capacity assessment.

    IMPORTANT:
    City score is NOT a simple average.

    You must apply:
    - Non-compensation rule
    - Cross-pillar clustering risk analysis
    - Relational integrity assessment
    - Stress resilience synthesis
    - Inequality amplification analysis

    --------------------------------------------------
    CITY-LEVEL EVALUATION RULES
    --------------------------------------------------

    1. Identify weak pillar clustering.
    2. Identify dependency fragility.
    3. Detect mismatch between security and justice.
    4. Detect elite fragmentation risk.
    5. Detect distributional imbalance.
    6. Detect opacity or suppression patterns.

    --------------------------------------------------
    SCORING SCALE
    --------------------------------------------------

    4 - Systemically resilient  
    3 - Broadly stable but uneven  
    2 - Structurally vulnerable  
    1 - High fragility  
    0 - Systemic breakdown  

    --------------------------------------------------
    RETURN STRICT JSON (MATCHING AICityScores)
    --------------------------------------------------

    {{
    "AIScore": 0-4,
    "AIProgress": 0-100,
    "ConfidenceLevel": "High|Medium|Low",
    "EvidenceSummary": "",
    "StructuralEvidence": "",
    "OperationalEvidence": "",
    "OutcomeEvidence": "",
    "PerceptionEvidence": "",
    "TemporalScope": "",
    "DistortionScreening": "",
    "PoliticalShock": "",
    "EconomicShock": "",
    "NarrativeShock": "",
    "OverallStressResilience": "",
    "StressScoreAdjustment": "",
    "InequalityAdjustment": "",
    "OpacityRisk": "",
    "NonCompensationNote": "",
    "CrossPillarPatterns": "",
    "RelationalIntegrity": "",
    "InstitutionalCapacity": "",
    "EquityAssessment": "",
    "ConflictRiskOutlook": "",
    "StrategicRecommendation": "",
    "DataTransparencyNote": "",
    "PrimarySource": ""
    }}

    --------------------------------------------------
    JSON OUTPUT FORMAT REQUIREMENTS
    --------------------------------------------------

    CRITICAL: The response MUST be valid, parseable JSON. Follow these rules STRICTLY:

    1. Use ONLY straight double quotes (") for all JSON keys and string values.
    2. Do NOT use smart quotes (" "), curly quotes, or any Unicode quote variants.
    3. Escape all special characters in string values:
    - Newlines: \\n
    - Tabs: \\t
    - Quotes within strings: \\" 
    - Backslashes: \\\\
    4. Do NOT include actual line breaks inside string values.
    5. Use regular hyphens (-) not em-dashes (—) or en-dashes (–).
    6. Use ASCII characters only. Avoid Unicode characters such as:
    - smart apostrophes
    - typographic quotes
    - long dashes
    7. Keep text concise and preferably single paragraph fields.
    8. Ensure every string value is properly closed with quotes.
    9. Ensure the JSON object ends with a closing brace }}.

    --------------------------------------------------
    FAILURE HANDLING
    --------------------------------------------------

    If the response risks being truncated, exceeds token limits, or violates any JSON rule, return {{}} only.
    """

pem_ai_research_service = PEMResearchService()