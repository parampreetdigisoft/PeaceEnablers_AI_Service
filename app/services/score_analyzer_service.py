"""
Score analyzer service - LLM-powered analysis with database exception logging
"""
import math
import logging
from typing import Any, Optional
from app.services.common.database_service import db_service
from app.services.common.db_logger_service import db_logger_service
from app.services.common.pem_ai_research_service import pem_ai_research_service
from datetime import datetime
logger = logging.getLogger(__name__)


class ScoreAnalyzerService:
    """Service for analyzing SQL Server data using LLM"""

    __slots__ = ('db_service',)  # Memory optimization

    def __init__(self):
        self.db_service = db_service

    @staticmethod
    def to_float_safe(value) -> float:
        """Convert value to float safely, returning 0.0 for invalid values"""
        if value is None:
            return 0.0

        if isinstance(value, float):
            return 0.0 if (math.isnan(value) or math.isinf(value)) else round(value, 2)

        if isinstance(value, int):
            return float(value)

        if isinstance(value, str):
            s = value.strip().lower()
            if s in {"", "null", "none", "nan", "inf", "-inf", "infinity", "-infinity"}:
                return 0.0
            
            try:
                val = float(s.replace(",", ""))
                return 0.0 if (math.isnan(val) or math.isinf(val)) else round(val, 2)
            except (ValueError, TypeError):
                return 0.0

        return 0.0

    @staticmethod
    def to_int_safe(value) -> int:
        """Convert value to int safely, returning 0 for invalid values"""
        if value is None:
            return 0

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return 0 if (math.isnan(value) or math.isinf(value)) else int(value)

        if isinstance(value, str):
            s = value.strip().lower()
            if s in {"", "null", "none", "nan", "inf", "-inf", "infinity", "-infinity"}:
                return 0
            
            try:
                return int(float(s.replace(",", "")))
            except (ValueError, TypeError):
                return 0

        return 0

    def _get_city_data(self, city_id: Optional[int] = None):
        """Fetch city data with optional filtering"""
        where_clause = f"where IsDeleted=0 and CityID={city_id}" if city_id else "where IsDeleted=0"
        return db_service.read_with_query(
            f"Select CityID, CityName, State, Country from Cities {where_clause}"
        )

    async def analyze_all_cities_questions(self, city_id: Optional[int] = None) -> bool:
        """Analyze City Questions data for all cities or specific city"""
        try:
            df = self._get_city_data(city_id)        

            if df.empty:
                logger.error("No cities found for analysis analyze_all_cities_questions endpoint")
                return False

            for city in df.itertuples(index=False):
                try:
                     await self.analyze_PillarQuestions(city)
                    #  await self.analyze_cityPillar(city)
                    #  await self.analyze_city(city)
                except Exception as e:
                    logger.error(f"Failed to analyze city {city.CityID} ({city.CityName}): {e}")
                    continue

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_all_cities_questions: {e}")
            raise

    async def analyze_single_City(self, cityId: int) -> bool:
        """Analyze City Questions data for a specific city"""
        try:
            df = self._get_city_data(cityId)
            if df.empty:
                return False

            for city in df.itertuples(index=False):
                await self.analyze_city(city)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_single_City (CityID: {cityId}): {e}")
            raise

    async def analyze_city_pillars(self, cityId: int) -> bool:
        """Analyze City pillar data for a specific city"""
        try:
            df = self._get_city_data(cityId)
            if df.empty:
                return False

            for city in df.itertuples(index=False):
                await self.analyze_cityPillar(city)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_city_pillars (CityID: {cityId}): {e}")
            raise

    async def analyze_Single_Pillar(self, cityId: int, pillar_id: Optional[int] = None) -> bool:
        """Analyze specific pillar for a city"""
        try:
            df = self._get_city_data(cityId)
            if df.empty:
                return False

            for city in df.itertuples(index=False):
                await self.analyze_cityPillar(city, pillar_id)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_Single_Pillar (CityID: {cityId}, PillarID: {pillar_id}): {e}")
            raise

    async def analyze_questions_of_city_pillar(self, cityId: int, pillar_id: Optional[int] = None) -> bool:
        """Analyze questions for city pillar"""
        try:
            df = self._get_city_data(cityId)
            if df.empty:
                return False

            for city in df.itertuples(index=False):
                await self.analyze_PillarQuestions(city, pillar_id)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_questions_of_city_pillar (CityID: {cityId}): {e}")
            raise

    def _build_question_record(self, row, ai_data, normalized_value: float) -> dict[str, Any]:
        """Build question evaluation record from AI data aligned with AIEstimatedQuestionScores"""
        
        ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
        evaluator_score = self.to_float_safe(normalized_value * 100)

        return {
                    "CityID": row.CityID,
                    "PillarID": row.PillarID,
                    "QuestionID": row.QuestionID,
                    "Year": self.to_int_safe(ai_data.get("Year")),
                    "AIScore": self.to_float_safe(ai_data.get("AIScore")),
                    "AIProgress": self.to_float_safe(ai_data.get("AIProgress")),
                    "EvaluatorScore": self.to_float_safe(normalized_value * 100),
                    "Discrepancy": pem_ai_research_service._calculate_discrepancy(ai_progress, evaluator_score),
                    "ConfidenceLevel": ai_data.get("ConfidenceLevel"),
                    "EvidenceSummary": ai_data.get("EvidenceSummary"),
                    "StructuralEvidence": ai_data.get("StructuralEvidence"),
                    "OperationalEvidence": ai_data.get("OperationalEvidence"),
                    "OutcomeEvidence": ai_data.get("OutcomeEvidence"),
                    "PerceptionEvidence": ai_data.get("PerceptionEvidence"),
                    "TemporalScope": ai_data.get("TemporalScope"),
                    "DistortionScreening": ai_data.get("DistortionScreening"),
                    "RelationalDependencies": ai_data.get("RelationalDependencies"),
                    "StressPoliticalShock": ai_data.get("StressPoliticalShock"),
                    "StressEconomicShock": ai_data.get("StressEconomicShock"),
                    "StressNarrativeShock": ai_data.get("StressNarrativeShock"),
                    "StressOverallResilienceShock": ai_data.get("StressOverallResilienceShock"),
                    "InequalityAdjustment": ai_data.get("InequalityAdjustment"),
                    "OpacityRisk": ai_data.get("OpacityRisk"),
                    "RedFlag": ai_data.get("RedFlag"),
                    "SourceName": ai_data.get("SourceName"),
                    "SourceType": ai_data.get("SourceType"),
                    "SourceURL": ai_data.get("SourceURL"),
                    "SourceDataYear": self.to_int_safe(ai_data.get("SourceDataYear")),
                    "SourceHierarchyLevel": self.to_int_safe(ai_data.get("SourceHierarchyLevel")),
                    "SourceDataExtract": ai_data.get("SourceDataExtract"),
                    "SourcesConsulted": self.to_int_safe(ai_data.get("SourcesConsulted")),
    }

    async def analyze_PillarQuestions(self, city: Any, pillar_id: Optional[int] = None) -> bool:
        """Analyze Pillar Questions data for a city"""
        try:
            where = f"cityId = {city.CityID}"
            if pillar_id is not None:
                where = f"cityId = {city.CityID} and PillarID={pillar_id}"


            df = db_service.get_view_data("vw_AiCityPillarQuestionEvaluations", where)
            
            if not len(df):
                db_logger_service.log_message("INFO", f"No pillar questions found for city {city.CityID} ({city.CityName})")
                return False
            
            pillarIds = [pillar_id] if pillar_id is not None else df["PillarID"].unique().tolist()
            
            for pillarId in pillarIds:
                pillar_df = df[df["PillarID"] == pillarId]
                questionList: list[dict[str, Any]] = []
                
                try:
                    for row in pillar_df.itertuples(index=False):
                        normalized_value = 0 if (row.NormalizedValue is None or 
                                                  (isinstance(row.NormalizedValue, float) and 
                                                   math.isnan(row.NormalizedValue))) else row.NormalizedValue
                            
                        try:
                            ai_data = await pem_ai_research_service.research_and_score_question(
                                        city.CityName,
                                        f"State :{city.State}, Country :{city.Country}",
                                        row.PillarID,
                                        row.PillarName,
                                        row.QuestionText,
                                        row.ScoreProgress,
                                        None
                                    )

                            if ai_data["success"]:
                                ai_data["CityID"] = city.CityID
                                questionList.append(self._build_question_record(row, ai_data, normalized_value))
                                
                                if len(questionList) == 1:
                                    db_service.bulk_upsert_question_evaluations(questionList)
                                    questionList = []
                            else:
                                db_logger_service.log_message("WARNING", 
                                    f"AI analysis failed for QuestionID {row.QuestionID} in City {city.CityID}")
                                
                        except Exception as e:
                            logger.error(f"Error processing question {row.QuestionID} for city {city.CityID}: {e}")
                            continue
                    
                    if questionList:
                        db_service.bulk_upsert_question_evaluations(questionList)

                except Exception as e:
                    logger.error(f"Error analyzing pillar {pillarId} for city {city.CityID}: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_PillarQuestions for city {city.CityID}: {e}")
            raise

    async def analyze_cityPillar(self, city: Any, pillar_id: Optional[int] = None) -> bool:
        """Analyze city pillar data and generate evaluations"""

        try:
            where = f"cityId = {city.CityID} and PillarID = {pillar_id}" if pillar_id else f"cityId = {city.CityID}"
            df = db_service.get_view_data("vw_AiCityPillarEvaluation", where)

            if not len(df):
                db_logger_service.log_message("INFO", f"No pillar evaluations found for city {city.CityID} ({city.CityName})")
                return False

            pillarList = []
            pillarSourceList = []

            for row in df.itertuples(index=False):
                try:
                    ai_data = await pem_ai_research_service.research_and_score_pillar(
                        city.CityName,
                        f"State :{city.State}, Country :{city.Country}",
                        row.PillarID,
                        row.PillarName,
                        row.QuestionWithScores,
                        row.EvaluatorScore,
                        row.AIScore,
                    )

                    if not ai_data["success"]:
                        continue
                    
                    # Build pillar record aligned with AIPillarScores
                    ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
                    evaluator_score = self.to_float_safe(row.EvaluatorScore)
                    pillarList.append({
                        "CityID": row.CityID,
                        "PillarID": row.PillarID,
                        "Year": ai_data.get("Year"),
                        "AIScore": self.to_float_safe(ai_data.get("AIScore")),
                        "AIProgress": self.to_float_safe(ai_data.get("AIProgress")),
                        "EvaluatorScore": self.to_float_safe(row.EvaluatorScore),
                        "Discrepancy": pem_ai_research_service._calculate_discrepancy(ai_progress, evaluator_score),
                        "ConfidenceLevel": ai_data.get("ConfidenceLevel"),
                        "EvidenceSummary": ai_data.get("EvidenceSummary"),
                        "StructuralEvidence": ai_data.get("StructuralEvidence"),
                        "OperationalEvidence": ai_data.get("OperationalEvidence"),
                        "OutcomeEvidence": ai_data.get("OutcomeEvidence"),
                        "PerceptionEvidence": ai_data.get("PerceptionEvidence"),
                        "TemporalScope": ai_data.get("TemporalScope"),
                        "DistortionScreening": ai_data.get("DistortionScreening"),
                        "RelationalIntegrity": ai_data.get("RelationalIntegrity"),
                        "StressPoliticalShock": ai_data.get("StressPoliticalShock"),
                        "StressEconomicShock": ai_data.get("StressEconomicShock"),
                        "StressNarrativeShock": ai_data.get("StressNarrativeShock"),
                        "StressOverallResilience": ai_data.get("StressOverallResilience"),
                        "StressScoreAdjustment": ai_data.get("StressScoreAdjustment"),
                        "InequalityAdjustment": ai_data.get("InequalityAdjustment"),
                        "OpacityRisk": ai_data.get("OpacityRisk"),
                        "NonCompensationNote": ai_data.get("NonCompensationNote"),
                        "GeographicEquityNote": ai_data.get("GeographicEquityNote"),
                        "InstitutionalAssessment": ai_data.get("InstitutionalAssessment"),
                        "DataGapAnalysis": ai_data.get("DataGapAnalysis"),
                        "RedFlag": ai_data.get("RedFlag")
                    })

                    # Source list (if still required)
                    for src in ai_data.get("Sources", []):
                        pillarSourceList.append({
                            "CityID": row.CityID,
                            "DataYear": self.to_int_safe(ai_data.get("Year")),
                            "PillarID": row.PillarID,
                            "SourceType": src.get("SourceType"),
                            "SourceName": src.get("SourceName"),
                            "SourceURL": src.get("SourceURL"),
                            "DataExtract": src.get("SourceDataExtract"),
                            "TrustLevel": self.to_int_safe(src.get("SourceHierarchyLevel"))
                        })

                    if len(pillarList) == 1:
                        db_service.bulk_upsert_pillar_evaluations(pillarList, pillarSourceList)
                        pillarList = []
                        pillarSourceList = []

                except Exception as e:
                    logger.error(f"Error processing pillar {row.PillarID} for city {city.CityID}: {e}")
                    continue

            if pillarList:
                db_service.bulk_upsert_pillar_evaluations(pillarList, pillarSourceList)

            return True

        except Exception as e:
            logger.error(f"Error in analyze_cityPillar for city {city.CityID}: {e}")
            raise
        
        
    async def analyze_city(self, city: Any) -> bool:
        """Analyze overall city data and generate comprehensive evaluation"""

        try:
            df = db_service.get_view_data("vw_AiCityEvaluations", f"cityId = {city.CityID}")

            if not len(df):
                db_logger_service.log_message(
                    "INFO",
                    f"No city evaluations found for city {city.CityID} ({city.CityName})"
                )
                return False

            cityList = []

            for row in df.itertuples(index=False):
                try:
                    year = datetime.now().year
                    ai_data = await pem_ai_research_service.research_and_score_city(
                        city.CityName,
                        f"State :{city.State}, Country :{city.Country}",
                        row.EvaluatorScore,
                        row.AIScore,
                        row.PillarWithScores
                    )

                    if not ai_data["success"]:
                        continue
                    ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
                    evaluator_score = self.to_float_safe(row.EvaluatorScore)
                    cityList.append({
                        "CityID": row.CityID,
                        "Year": self.to_int_safe(ai_data.get("Year") or ai_data.get("year") or year),
                        "AIScore": self.to_float_safe(ai_data.get("AIScore") or ai_data.get("ai_score") or 0),
                        "AIProgress": self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0),
                        "EvaluatorScore": self.to_float_safe(row.EvaluatorScore),
                        "Discrepancy": pem_ai_research_service._calculate_discrepancy(ai_progress, evaluator_score), 
                        "ConfidenceLevel": ai_data.get("ConfidenceLevel") or ai_data.get("confidence_level") or "Unknown",
                        "EvidenceSummary": ai_data.get("EvidenceSummary") or ai_data.get("evidence_summary") or "",
                        "StructuralEvidence": ai_data.get("StructuralEvidence") or ai_data.get("structural_evidence") or "",
                        "OperationalEvidence": ai_data.get("OperationalEvidence") or ai_data.get("operational_evidence") or "",
                        "OutcomeEvidence": ai_data.get("OutcomeEvidence") or ai_data.get("outcome_evidence") or "",
                        "PerceptionEvidence": ai_data.get("PerceptionEvidence") or ai_data.get("perception_evidence") or "",
                        "TemporalScope": ai_data.get("TemporalScope") or ai_data.get("temporal_scope") or "",
                        "DistortionScreening": ai_data.get("DistortionScreening") or ai_data.get("distortion_screening") or "",
                        "PoliticalShock": ai_data.get("PoliticalShock") or ai_data.get("political_shock") or "",
                        "EconomicShock": ai_data.get("EconomicShock") or ai_data.get("economic_shock") or "",
                        "NarrativeShock": ai_data.get("NarrativeShock") or ai_data.get("narrative_shock") or "",
                        "OverallStressResilience": ai_data.get("OverallStressResilience") or ai_data.get("overall_stress_resilience") or "",
                        "StressScoreAdjustment": ai_data.get("StressScoreAdjustment") or ai_data.get("stress_score_adjustment") or "",
                        "InequalityAdjustment": ai_data.get("InequalityAdjustment") or ai_data.get("inequality_adjustment") or "",
                        "OpacityRisk": ai_data.get("OpacityRisk") or ai_data.get("opacity_risk") or "",
                        "NonCompensationNote": ai_data.get("NonCompensationNote") or ai_data.get("non_compensation_note") or "",
                        "CrossPillarPatterns": ai_data.get("CrossPillarPatterns") or ai_data.get("cross_pillar_patterns") or "",
                        "RelationalIntegrity": ai_data.get("RelationalIntegrity") or ai_data.get("relational_integrity") or "",
                        "InstitutionalCapacity": ai_data.get("InstitutionalCapacity") or ai_data.get("institutional_capacity") or "",
                        "EquityAssessment": ai_data.get("EquityAssessment") or ai_data.get("equity_assessment") or "",
                        "ConflictRiskOutlook": ai_data.get("ConflictRiskOutlook") or ai_data.get("conflict_risk_outlook") or "",
                        "StrategicRecommendation": ai_data.get("StrategicRecommendation") or ai_data.get("strategic_recommendation") or "",
                        "DataTransparencyNote": ai_data.get("DataTransparencyNote") or ai_data.get("data_transparency_note") or "",
                        "PrimarySource": ai_data.get("PrimarySource") or "",
                        "VerifiedBy": None  # leave NULL unless manual verification
                    })

                    if len(cityList) == 1:
                        db_service.bulk_upsert_city_evaluations(cityList)
                        cityList = []

                except Exception as e:
                    logger.error(f"Error processing city evaluation for {city.CityID}: {e}")
                    continue

            if cityList:
                db_service.bulk_upsert_city_evaluations(cityList)

            return True

        except Exception as e:
            logger.error(f"Error in analyze_city for city {city.CityID}: {e}")
            raise


# Singleton instance
score_analyzer_service = ScoreAnalyzerService()