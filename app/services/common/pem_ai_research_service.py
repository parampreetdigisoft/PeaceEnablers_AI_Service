"""
    Peace Enablers Matrix AI Research Service
    Independent research-based scoring with evidence tracking
"""
import re
import json
import asyncio
import logging
from langchain_core.messages import SystemMessage
from datetime import datetime
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.services.common.llm_factory import llm_factory
from app.services.common.pillar_prompts import PeaceEnablerPillarPrompts
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
    country_name: str,
    continent: str,
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
                            
            pillar_context = PeaceEnablerPillarPrompts.get_pillar_context(pillarID)
            system_prompt = self._question_system_prompt(
            pillar_context=pillar_context)
                            
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),  # ✅ NO templating
                ("user", """
                    Country: {country_name}
                    Continent: {continent}
                    Pillar: {pillar_name}
                    Question: {question_text}
                    Evaluator Score: {evaluator_score}
                    Year: {year}

                    Return ONLY valid JSON.
                """)
            ])

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "country_name": country_name,
                        "continent": continent,
                        "pillar_name": pillar_name,
                        "question_text": question_text,
                        "evaluator_score":evaluator_score,
                        "pillar_context": pillar_context,
                        "year": year
                    })
                    if not result or result.strip() == "{}":
                            continue  # retry
                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)
                    four_layer = analysis.get("four_layer_evidence", {})
                    stress = analysis.get("stress_simulation", {})

                    return {
                        "success": True,
                        "CountryID": None,
                        "PillarID": pillarID,
                        "Year": year,

                        "AIScore": analysis.get("ai_score"),
                        "AIProgress": analysis.get("ai_progress"),
                        "ConfidenceLevel": analysis.get("confidence_level"),

                        # ✅ FIXED (nested extraction)
                        "StructuralEvidence": four_layer.get("structural"),
                        "OperationalEvidence": four_layer.get("operational"),
                        "OutcomeEvidence": four_layer.get("outcome"),
                        "PerceptionEvidence": four_layer.get("perception"),

                        "EvidenceSummary": analysis.get("evidence_summary"),

                        "TemporalScope": analysis.get("temporal_scope"),
                        "DistortionScreening": analysis.get("distortion_screening"),
                        "RelationalDependencies": analysis.get("relational_dependencies"),

                        # ✅ FIXED (nested stress fields)
                        "StressPoliticalShock": stress.get("political_shock"),
                        "StressEconomicShock": stress.get("economic_shock"),
                        "StressNarrativeShock": stress.get("narrative_shock"),
                        "StressOverallResilienceShock": stress.get("overall_stress_resilience"),

                        "InequalityAdjustment": analysis.get("inequality_adjustment"),
                        "OpacityRisk": analysis.get("opacity_risk"),

                        # ❌ not present in response → keep None-safe
                        "NonCompensationNote": analysis.get("non_compensation_note"),

                        "RedFlag": analysis.get("red_flag"),

                        # ✅ source fields
                        "SourceName": analysis.get("source_name"),
                        "SourceType": analysis.get("source_type"),
                        "SourceURL": analysis.get("source_url"),
                        "SourceDataYear": analysis.get("source_data_year"),
                        "SourceHierarchyLevel": analysis.get("source_trust_level"),  # FIXED KEY
                        "SourceDataExtract": analysis.get("source_data_extract"),

                        # ❌ not present → optional
                        "SourcesConsulted": analysis.get("sources_consulted"),

                        # ❌ not present → optional
                        "ConfidenceExplanation": analysis.get("confidence_explanation")
                    }

                except Exception as ex:
                    logger.error(f"Attempt {attempt+1} for pillarID {pillarID} and country name {country_name} && question {question_text} failed in research_and_score_pillar: {str(ex)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def research_and_score_pillar(
    self,
    country_name: str,
    continent: str,
    pillarId: int,
    pillar_name: str,    
    evaluator_score: Optional[float] = None,
    existing_ai_score: Optional[float] = None,
    year: int = None
) -> Dict[str, Any]:

        try:
            await self._ensure_initialized()

            if year is None:
                year = datetime.now().year

            pillar_context = PeaceEnablerPillarPrompts.get_pillar_context(pillarId)
            system_prompt = self._pillar_system_prompt(
            pillar_context=pillar_context)
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),  # ✅ NO templating
                ("user", """
                    Country: {country_name}
                    Continent: {continent}
                    Pillar: {pillar_name}                                        
                    Year: {year}
                    Return ONLY valid JSON.
                """)
            ])              
           

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "country_name": country_name,
                        "continent": continent,
                        "pillar_name": pillar_name,                        
                        "year": year,
                        "evaluator_score": evaluator_score,
                        "existing_ai_score": existing_ai_score,
                        "pillar_context":pillar_context
                    })    
                    if not result or result.strip() == "{}":
                            continue  # retry                
                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)
                    
                    return {
                            "success": True,
                            "CountryID": None,
                            "PillarID": pillarId,
                            "Year": year,

                            # ✅ top-level
                            "AIScore": analysis.get("ai_score"),
                            "AIProgress": analysis.get("ai_progress"),
                            "ConfidenceLevel": analysis.get("confidence_level"),

                            # ✅ summary
                            "EvidenceSummary": analysis.get("evidence_summary"),

                            # ✅ four layer evidence (nested)
                            "StructuralEvidence": analysis.get("four_layer_evidence", {}).get("structural"),
                            "OperationalEvidence": analysis.get("four_layer_evidence", {}).get("operational"),
                            "OutcomeEvidence": analysis.get("four_layer_evidence", {}).get("outcome"),
                            "PerceptionEvidence": analysis.get("four_layer_evidence", {}).get("perception"),

                            # ✅ other fields
                            "TemporalScope": analysis.get("temporal_scope"),
                            "DistortionScreening": analysis.get("distortion_screening"),
                            "RelationalIntegrity": analysis.get("relational_integrity"),

                            # ✅ stress simulation (nested)
                            "StressPoliticalShock": analysis.get("stress_simulation", {}).get("political_shock"),
                            "StressEconomicShock": analysis.get("stress_simulation", {}).get("economic_shock"),
                            "StressNarrativeShock": analysis.get("stress_simulation", {}).get("narrative_shock"),
                            "StressOverallResilience": analysis.get("stress_simulation", {}).get("overall_stress_resilience"),
                            "StressScoreAdjustment": analysis.get("stress_simulation", {}).get("stress_score_adjustment"),

                            # ✅ adjustments
                            "InequalityAdjustment": analysis.get("inequality_adjustment"),
                            "OpacityRisk": analysis.get("opacity_risk"),
                            "NonCompensationNote": analysis.get("non_compensation_note"),

                            # ✅ additional fields (safe fallback if missing)
                            "GeographicEquityNote": analysis.get("geographic_equity_note"),
                            "InstitutionalAssessment": analysis.get("institutional_assessment"),
                            "DataGapAnalysis": analysis.get("data_gap_analysis"),
                            "RedFlag": analysis.get("red_flag"),

                            # ✅ sources array
                            "Sources": analysis.get("sources", [])
                        }

                except Exception as ex:
                    logger.error(f"Attempt {attempt+1} for  {pillar_name} and country name {country_name} failed in research_and_score_pillar: {str(ex)}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    raise

        except Exception as e:
         return {"success": False, "error": str(e)}
    
    async def research_and_score_country(
    self,
    country_name: str,
    continent: str,
    evaluator_score: Optional[float] = None,    
    year: int = None
) -> Dict[str, Any]:

        try:
            await self._ensure_initialized()

            if year is None:
                year = datetime.now().year

            # ✅ Pillars
            pillarNames = PeaceEnablerPillarPrompts.get_all_pillar_names()
            pillar_list_str = "\n".join(
                f"{k}. {v}" for k, v in pillarNames.items()
            )

            # ✅ System Prompt
            system_prompt = self._get_pem_country_system_prompt(
                pillar_list_str=pillar_list_str
            )          
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),  # ✅ NO templating here
                ("user", """
                    Country: {country_name}
                    Continent: {continent}
                    Year: {year}
                """)
            ])

            for attempt in range(self.max_retries):
                try:
                    chain = prompt | self.llm | StrOutputParser()

                    result = await chain.ainvoke({
                        "country_name": country_name,
                        "continent": continent,
                        "year": year,
                        "pillar_list_str": pillar_list_str,
                        "evaluator_note": evaluator_score or ""
                    })
                    if not result or result.strip() == "{}":
                            continue  # retry
                    cleaned = self._clean_json_response(result)
                    analysis = json.loads(cleaned)
                    four_layer = analysis.get("four_layer_evidence", {})
                    stress = analysis.get("stress_simulation", {})

                    return {
                            "success": True,
                            "CountryID": None,
                            "Year": year,

                            # ✅ Correct key mapping
                            "AIScore": analysis.get("ai_score"),
                            "AIProgress": analysis.get("ai_progress"),
                            "ConfidenceLevel": analysis.get("confidence_level"),
                            "EvidenceSummary": analysis.get("evidence_summary"),

                            # ✅ Nested extraction
                            "StructuralEvidence": four_layer.get("structural"),
                            "OperationalEvidence": four_layer.get("operational"),
                            "OutcomeEvidence": four_layer.get("outcome"),
                            "PerceptionEvidence": four_layer.get("perception"),

                            "TemporalScope": analysis.get("temporal_scope"),
                            "DistortionScreening": analysis.get("distortion_screening"),

                            # ✅ Stress block
                            "PoliticalShock": stress.get("political_shock"),
                            "EconomicShock": stress.get("economic_shock"),
                            "NarrativeShock": stress.get("narrative_shock"),
                            "OverallStressResilience": stress.get("overall_stress_resilience"),
                            "StressScoreAdjustment": stress.get("stress_score_adjustment"),

                            "InequalityAdjustment": analysis.get("inequality_adjustment"),
                            "OpacityRisk": analysis.get("opacity_risk"),
                            "NonCompensationNote": analysis.get("non_compensation_note"),
                            "CrossPillarPatterns": analysis.get("cross_pillar_patterns"),
                            "RelationalIntegrity": analysis.get("relational_integrity"),
                            "InstitutionalCapacity": analysis.get("institutional_capacity"),
                            "EquityAssessment": analysis.get("equity_assessment"),
                            "ConflictRiskOutlook": analysis.get("conflict_risk_outlook"),
                            "StrategicRecommendation": analysis.get("strategic_recommendation"),
                            "DataTransparencyNote": analysis.get("data_transparency_note"),
                            "PrimarySource": analysis.get("primary_source")
                        }

                except Exception as ex:
                    logger.error(f"Attempt {attempt+1}  for {country_name}failed in research_and_score_country: {str(ex)}")
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


    def _validate_country_response(self, data: Dict) -> Dict:
        """Validate AICountryScores response"""
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
   
    def _question_system_prompt(self, pillar_context: str) -> str:
        return f"""
            You are a specialist analyst for the Peace Enabler Index (PEM).
            You score individual questions about peace conditions in countries worldwide.
            Keep each section concise.
            Do not exceed requested word limits.

            {PeaceEnablerPillarPrompts.GOVERNANCE_PROTOCOL}

            PILLAR CONTEXT FOR THIS QUESTION:
            {pillar_context}

            YOUR MANDATORY PROCESS (execute in sequence — no shortcuts):
            Step 1: Establish temporal scope — what is the evidence range (1950-present)?
                    Note any pre-1950 roots and their current institutional expression.
            Step 2: Search for evidence across all four layers:
                    structural (laws/mandates), operational (budgets/enforcement),
                    outcome (measured results), perception (trust/grievance surveys).
            Step 3: Apply evidence hierarchy — official and international sources first, media last.
                    Require minimum two independent sources.
            Step 4: Screen for distortion — election cycles, suppressed data, restricted media,
                    abrupt unexplained improvements.
            Step 5: Test relational dependencies — which other peace domains directly affect
                    this question's answer?
            Step 6: Run stress simulation — political shock, economic shock, narrative shock.
                    Adjust score downward if the condition is unlikely to hold under stress.
            Step 7: Apply inequality adjustment — does performance reflect the whole population
                    or only elites and dominant groups? Adjust score if imbalance is found.
            Step 8: Apply data silence protocol — assign "Unknown" and document cause if data
                    cannot be verified. Never reward silence with a neutral score.
            Step 9: Assign final score using the seven-level grid.

            OUTPUT: Return ONLY this exact JSON object (no markdown, no extra text):
            {{{{
                "ai_score": <0|1|2|3|4|"N/A"|"Unknown">,
                "ai_progress": <0.00-100.00 or null if Unknown>,
                "confidence_level": "<High|Medium|Low>",
                "evidence_summary": "<150-200 words for a general reader. What does the evidence show for this pillar? Include both strengths and concerns. Plain language only — no internal protocol terms.>",
                "four_layer_evidence": {{{{
                    "structural": "<5-80 words for a general reader. What laws, mandates, or constitutional arrangements were found? 1-2 sentences.>",
                    "operational": "<5-80 words for a general reader. What budget, staffing, or enforcement data was found? 1-2 sentences.>",
                    "outcome": "<5-80 words for a general reader. What measured results or incident data was found? 1-2 sentences.>",
                    "perception": "<5-80 words for a general reader. What trust surveys or grievance data was found? State 'No data found' if unavailable.>"
                }}}},
                "temporal_scope": "<80-100 words for a general reader. Earliest and most recent evidence years used. Note any pre-1950 references and their current institutional form.>",
                "distortion_screening": "<80-100 words for a general reader. What was tested and what was found. State: Clean, Suspect, or Unknown. Explain any concerns found.>",
                "relational_dependencies": "< 80-100 words for a general reader. Which 2-3 other peace domains most affect this question, and in what direction? 2-3 sentences.>",
                "stress_simulation": {{{{
                    "political_shock": "<5-80 words for a general reader. How would this condition hold under a leadership crisis, electoral dispute, or elite fracture?>",
                    "economic_shock": "<5-80 words for a general reader. How would this condition hold under fiscal crisis, currency instability, or youth unemployment surge?>",
                    "narrative_shock": "<5-80 words for a general reader. How would this condition hold under a disinformation campaign, identity mobilization, or grievance amplification?>",
                    "overall_stress_resilience": "<High|Medium|Low>"
                }}}},
                "non_compensation_note": "<50-100 words for a general reader. Does this pillar's score account for the Non-Compensation Rule? Example: if security is strong but justice is absent, security cannot substitute. State 'Not applicable' if no such dependency exists.>",
                "inequality_adjustment": "<80-130 words for a general reader. Was a score adjustment made for distributional imbalance? State which group is excluded and by how much the score was adjusted downward. State 'No adjustment needed' if equity is adequate.>",
                "opacity_risk": "<80-130 words for a general reader. Describe any data gaps found: cause (conflict disruption, state suppression, institutional incapacity, missing infrastructure). Empty string if no opacity.>",
                "red_flag": "<80-130 words for a general reader. Describe any serious concern: cosmetic reform, single-source claims, elite-only data, or suppressed reporting. Empty string if none.>",
                "data_sources_count": <integer 1-5, Number of sources that data is collected>,
                "source_type": "<Official Government|International Organization|Academic|Civil Society|Geospatial|Media>",
                "source_name": "<Organization or publication name>",
                "source_url": "<URL or 'Not available'>",
                "source_data_year": <year as integer>,
                "source_trust_level": <1-7 matching evidence hierarchy above>,
                "source_data_extract": "<The specific data point or finding from this source, 1-2 sentences.>"
            }}}}

            --------------------------------------------------
            OUTPUT STYLE (MANDATORY)
            --------------------------------------------------

            - Write for general audience (no technical jargon)
            - Avoid internal scoring language
            - Use clear, concise, evidence-based statements
            - No bullet points or lists inside values

            --------------------------------------------------
            JSON OUTPUT FORMAT REQUIREMENTS (CRITICAL)
            --------------------------------------------------

            The response MUST be valid JSON.

            STRICT RULES:

            1. Use ONLY standard double quotes (")
            2. Do NOT use single quotes, smart quotes, or backticks
            3. Escape special characters: \\n \\t \\" \\\\
            4. No line breaks inside values
            5. Use ASCII characters only (no Unicode characters such as \u2019, smart apostrophes, or typographic symbols)
            6. No trailing commas
            7. No missing commas
            8. Use regular hyphens (-) not em-dashes (—) or en-dashes (–)
            9. No comments
            10. Output ONLY JSON
            11. Must start with {{ and end with }}

            --------------------------------------------------
            FAIL SAFE
            --------------------------------------------------

            If output risks invalid JSON or truncation -> return {{{{}}}}
        """

    def _pillar_system_prompt(self, pillar_context: str) -> str:
        return f"""
            You are a senior analyst for the Peace Enablers Mapper (PEM).
            You conduct deep, multi-source assessments of a single peace pillar for a country.
            Keep each section concise.
            Do not exceed requested word limits.

            {PeaceEnablerPillarPrompts.GOVERNANCE_PROTOCOL}

            PILLAR CONTEXT:
            {pillar_context}            

            YOUR MANDATORY PROCESS (execute in full — no shortcuts):
            Step 1: Establish temporal scope — what is the evidence range? Note pre-1950 roots
                    and their current institutional expression (if relevant).
            Step 2: Conduct broad web research across all evidence levels for this pillar.
            Step 3: Collect evidence across all four layers for this specific pillar.
            Step 4: Apply evidence hierarchy.
            Step 5: Test geographic equity — does the data reflect the whole country, or only
                    central/affluent zones? Identify core-periphery performance gaps.
            Step 6: Screen for distortion — election-cycle data, restricted media, curated statistics,
                    abrupt statistical improvements without verifiable explanation.
            Step 7: Test relational integrity — how does this pillar interact with 3-5 other
                    peace system domains? Are apparent strengths undermined by weak supporting pillars?
            Step 8: Run three-scenario stress simulation. Adjust score if pillar is stress-vulnerable.
            Step 9: Apply inequality adjustment. Adjust score if performance excludes marginalized groups.
            Step 10: Apply data silence protocol for any unverifiable data points.
            Step 11: Apply non-compensation rule — note if this pillar's strength is offset or
                    undermined by weakness in a dependent domain.
            Step 12: Assign final score using the seven-level grid.
            Step 13: Provide sources — MANDATORY:
                    - You MUST return between 1 and 7 sources
                    - Each source MUST include all required fields
                    - If you cannot find at least 1 valid sources, then make one guessing reasonable source                   

            OUTPUT: Return ONLY this exact JSON object (no markdown, no extra text):
            {{{{
                "ai_score": <0|1|2|3|4|"N/A"|"Unknown">,
                "ai_progress": <0.00-100.00 or null if Unknown>,
                "confidence_level": "<High|Medium|Low>",
                "evidence_summary": "<150-200 words for a general reader. What does the evidence show for this pillar? Include both strengths and concerns. Plain language only — no internal protocol terms.>",
                "four_layer_evidence": {{{{
                    "structural": "<5-80 words for a general reader. Legal frameworks, institutional mandates, constitutional arrangements found for this pillar. 2-3 sentences.>",
                    "operational": "<5-80 words for a general reader. Budget allocations, staffing levels, enforcement patterns, service delivery metrics. 2-3 sentences.>",
                    "outcome": "<5-80 words for a general reader. Measured results, incident data, distributional impact. 2-3 sentences.>",
                    "perception": "<5-80 words for a general reader. Trust surveys, grievance patterns, participation metrics. 2-3 sentences. State 'No data found' if unavailable.>"
                }}}},
                "sources": [
                    {{{{
                        "source_type": "<Official Government|International Organization|Academic|Civil Society|Geospatial|Media>",
                        "source_name": "Organization or publication name",
                        "source_url": "URL or 'Not available' LIKE https://example.com/report ",
                        "data_year": <data year as integer LIKE- 2025>,
                        "source_trust_level": <1-7>,
                        "data_extract": "<5-100 words for a general reader. The specific finding from this source. 1-3 sentences.>"
                    }}}}
                ],
                "temporal_scope": "<50-100 words for a general reader.  Evidence timeframe used (1950-present). Key historical turning points that shape current pillar conditions.>",
                "distortion_screening": "<50-100 words for a general reader. What was tested. Result: Clean, Suspect, or Unknown. Explain any concerns. Note if restricted media or curated data was encountered.>",
                "relational_integrity": "<50-100 words for a general reader. How does this pillar interact with 3-5 other peace system domains? Does an apparent strength depend on weak supporting domains? 3-4 sentences.>",
                "stress_simulation": {{{{
                    "political_shock": "<5-100 words for a general reader. How would this pillar hold under a leadership crisis, electoral dispute, or elite fracture?>",
                    "economic_shock": "<5-100 words for a general reader. How would this pillar hold under fiscal contraction, currency instability, or youth unemployment surge?>",
                    "narrative_shock": "<5-100 words for a general reader. How would this pillar hold under a disinformation cascade, identity mobilization, or grievance amplification?>",
                    "overall_stress_resilience": "<High|Medium|Low>",
                    "stress_score_adjustment": "<5-100 words for a general reader. Was the score adjusted downward for stress vulnerability? If yes, state original score and reason.>"
                }}}},
                "inequality_adjustment": "<50-100 words for a general reader. Were distributional imbalances found? Which groups are excluded (income, identity, geographic)? Was the score adjusted and by how much? State 'No adjustment needed' if equity is adequate.>",
                "opacity_risk": "<50-100 words for a general reader. Data gaps identified. Cause: conflict disruption, state suppression, institutional incapacity, or missing infrastructure. Significance for the assessment. Empty string if none.>",
                "non_compensation_note": "<50-100 words for a general reader. Does this pillar's score account for the Non-Compensation Rule? Example: if security is strong but justice is absent, security cannot substitute. State 'Not applicable' if no such dependency exists.>",
                "geographic_equity_note": "<50-100 words for a general reader. Are outcomes equitable across the country? Compare core vs periphery, income groups, identity communities. 2-3 sentences.>",
                "institutional_assessment": "<50-100 words for a general reader. Quality of governance and institutional capacity specifically for this pillar. 2-3 sentences.>",
                "data_gap_analysis": "<50-100 words for a general reader. What important information was unavailable? What does its absence signal about governance or transparency? 1-2 sentences.>",
                "red_flag": "<50-100 words for a general reader. Systemic concerns found: cosmetic reform presented as structural, single-source claims, elite capture, data suppression. Empty string if none.>"
            }}}}

            --------------------------------------------------
            OUTPUT STYLE (MANDATORY)
            --------------------------------------------------

            - Write for general audience (no technical jargon)
            - Avoid internal scoring language
            - Use clear, concise, evidence-based statements
            - No bullet points or lists inside values

            --------------------------------------------------
            JSON OUTPUT FORMAT REQUIREMENTS (CRITICAL)
            --------------------------------------------------

            The response MUST be valid JSON.

            STRICT RULES:

            1. Use ONLY standard double quotes (")
            2. Do NOT use single quotes, smart quotes, or backticks
            3. Escape special characters: \\n \\t \\" \\\\
            4. No line breaks inside values
            5. Use ASCII characters only (no Unicode characters such as \u2019, smart apostrophes, or typographic symbols)
            6. No trailing commas
            7. No missing commas
            8. Use regular hyphens (-) not em-dashes (—) or en-dashes (–)
            9. No comments
            10. Output ONLY JSON
            11. Must start with {{ and end with }}

            --------------------------------------------------
            FAIL SAFE
            --------------------------------------------------

            If output risks invalid JSON or truncation -> return {{{{}}}}
            """

    def _get_pem_country_system_prompt( self, pillar_list_str: str, evaluator_note: str = "") -> str:
        return f"""
        You are a lead analyst for the Peace Enablers Mapper (PEM).
        You conduct comprehensive, cross-pillar country-level peace assessments.
        Keep each section concise.
        Do not exceed requested word limits.
        Output for a general reader.

        {PeaceEnablerPillarPrompts.GOVERNANCE_PROTOCOL}

        ALL 23 PILLARS:
        {pillar_list_str}

        HUMAN REFERENCE:
        {evaluator_note}

        YOUR MANDATORY PROCESS (execute in full):
        Step 1: Search broadly across all 23 pillar domains for this country.
        Step 2: Establish the temporal scope (1950-present).
        Step 3: Collect four-layer evidence at country scale.
        Step 4: Screen for country-level distortion.
        Step 5: Identify cross-pillar patterns.
        Step 6: Apply relational integrity test.
        Step 7: Run country-scale stress simulation.
        Step 8: Test geographic equity.
        Step 9: Apply inequality adjustment if needed.
        Step 10: Apply non-compensation rule.
        Step 11: Apply data silence protocol.
        Step 12: Assign overall score.
        Step 13: Assess trajectory.

        OUTPUT: Return ONLY valid JSON (no markdown, no extra text):

        {{
            "ai_score": <0|1|2|3|4|"N/A"|"Unknown">,
            "ai_progress": <0.00-100.00 or null if Unknown>,
            "confidence_level": "<High|Medium|Low>",
            "evidence_summary": "<500-700 words, ASCII only. Follow the mandatory sections Executive Summary structure exactly as defined above. Write in continuous prose — no section headers, no bullet points, no numbered lists. The 4 sections must flow as a coherent narrative that answers: (1) How well is this country functioning? (2) What are the biggest risks in the next decade? (3) Where should policy or investment focus first? Sections in order: Country Score and Overview, System Diagnosis, Strategic Strengths, Structural Risks.>",
            "four_layer_evidence": {{
                "structural": "<20-150 words: Key structural evidence across pillars — laws, constitutions, institutional mandates.>",
                "operational": "<20-150 words: Key operational evidence — budgets, enforcement patterns, service delivery at country scale.>",
                "outcome": "<20-150 words: Key outcome evidence — incident data, distributional results, measured impacts.>",
                "perception": "<20-150 words: Key perception evidence — trust surveys, grievance patterns, civic participation.>"
            }},
            "temporal_scope": "<20-150 words: Evidence timeframe (1950-present). Key historical turning points shaping current conditions.>",
            "distortion_screening": "<20-150 words: Country-level distortion assessment. What was tested and what was found. Result: Clean, Suspect, or Unknown.>",
            "stress_simulation": {{
                "political_shock": "<20-150 words: How would this country's peace system hold under a leadership crisis or electoral dispute?>",
                "economic_shock": "<20-150 words: How would this country hold under fiscal crisis or a major unemployment surge?>",
                "narrative_shock": "<20-150 words: How would this country hold under large-scale disinformation or identity mobilization?>",
                "overall_stress_resilience":  "<High|Medium|Low>",
                "stress_score_adjustment": "<20-150 words: Was the overall score adjusted for stress vulnerability? State original score and reason if adjusted.>"
            }},
            "inequality_adjustment": "<20-150 words: Distributional imbalances found across income, geography, or identity groups. How did this affect the overall score?>",
            "opacity_risk": "<20-150 words: Which pillar domains had the most opaque or unverifiable data? What does that signal about governance transparency?>",
            "non_compensation_note": "<20-150 words: Which apparent country-level strengths were discounted because they could not compensate for weakness in dependent domains?>",
            "cross_pillar_patterns": "<20-150 words: What themes cut across multiple pillars? Are weaknesses reinforcing each other? Are strengths systemic or isolated?>",
            "relational_integrity": "<20-150 words: Does the country's peace system show alignment, or are there critical disconnects where a weak domain undermines others?>",
            "institutional_capacity": "<20-150 words: Overall state capacity, governance quality, and ability to manage stress across pillars.>",
            "equity_assessment": "<20-150 words: Are peace conditions equitable across geography, income groups, and identity communities?>",
            "conflict_risk_outlook": "<100-150 words: Near-term trajectory — improving, stable, or deteriorating? What are the 1-2 most critical risk drivers?>",
            "strategic_recommendation": "<100-150 words: The 2-3 highest-priority evidence-grounded actions to improve peace conditions.>",
            "data_transparency_note": "<20-150 words: How open and verifiable is country-level data? Are there structural opacity issues?>",
            "primary_source": "<20-150 words: Name of the most authoritative source used in this assessment.>"
        }}

        --------------------------------------------------
        EXECUTIVE SUMMARY WRITING FRAMEWORK (COUNTRY)
        --------------------------------------------------

        The evidence_summary field MUST follow this exact 4-section structure. Each section is mandatory.
        Target length: 550-700 words total. Write in flowing prose - no section headers, no bullet points.

        SECTION 1 - COUNTRY SCORE AND OVERVIEW (1 paragraph, ~120-150 words):
        You MUST begin the paragraph using the EXACT sentence structure below. Do not change wording except placeholders:
        "[Country] achieves an overall PEM score of [X]% percent across 23 pillars, placing it [above/at/below] the median among [peer group description]."
        Rules:
        - The phrase "percent across 23 pillars" MUST appear exactly as written
        - Do NOT repeat "percent across" more than once
        - Do NOT modify sentence structure
        - After this sentence, continue naturally to complete the paragraph
        This section must clearly answer: How well is this country functioning overall?

        SECTION 2 - SYSTEM DIAGNOSIS (1 paragraph, ~130-170 words):
        Describe what type of country system this is structurally.
        Answer: Is the country stable, fragile, reforming, or under systemic pressure?
        What trajectory is it on?
        Capture dominant national dynamics such as governance capacity, economic structure,
        demographic pressures, or conflict exposure.
        This must be a coherent system-level diagnosis, not a list of scores.

        SECTION 3 - STRATEGIC STRENGTHS (1 paragraph, ~130-170 words):
        Identify the 3-5 strongest pillars or domains.
        Do NOT list indicators.
        Frame them as structural strengths that support resilience, stability, or development.
        Explain why these strengths matter at country scale.

        SECTION 4 - STRUCTURAL RISKS (1 paragraph, ~130-170 words):
        Identify the 3-5 most critical systemic risks.
        These must affect long-term stability, peace, or development.
        Explain cause-effect relationships across sectors.
        This section must answer: What are the biggest risks in the next decade?

        EVIDENCE_SUMMARY QUALITY CHECKS:
        - Section 1 must characterize the country as a system, not list facts
        - Sections 2 and 3 must reflect system-level thinking, not indicators
        - Section 4 must include cross-sector cause-effect logic

        --------------------------------------------------
        JSON OUTPUT FORMAT REQUIREMENTS (CRITICAL)
        --------------------------------------------------

        The response MUST be valid JSON.

        STRICT RULES:

        1. Use ONLY standard double quotes (") for keys and values
        2. Do NOT use single quotes, smart quotes, or backticks
        3. Escape special characters:
        - \\n \\t \\" \\\\
        4. No line breaks inside values (single-line strings only)
        5. Use ASCII characters only (no Unicode characters such as \u2019, smart apostrophes, or typographic symbols)
        6. No trailing commas
        7. No missing commas
        8. Use regular hyphens (-) not em-dashes (—) or en-dashes (–)
        9. No comments inside JSON
        10. No extra text before or after JSON
        11. JSON must start with an opening brace and end with a closing brace

        If ANY rule is at risk -> return {{}}

        """

pem_ai_research_service = PEMResearchService()