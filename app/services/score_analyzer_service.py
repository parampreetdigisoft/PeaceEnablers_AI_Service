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

    def _get_country_data(self, country_id: Optional[int] = None):
        """Fetch country data with optional filtering"""
        where_clause = f"where IsDeleted=0 and CountryID={country_id}" if country_id else "where IsDeleted=0"
        return db_service.read_with_query(
            f"Select CountryID, CountryName, Continent from Countries {where_clause}"
        )

    async def analyze_all_countries_questions(self, country_id: Optional[int] = None) -> bool:
        """Analyze Country Questions data for all countries or specific country"""
        try:
            df = self._get_country_data(country_id)        

            if df.empty:
                logger.error("No countries found for analysis analyze_all_countries_questions endpoint")
                return False

            for country in df.itertuples(index=False):
                try:
                       #await self.analyze_PillarQuestions(country)
                       await self.analyze_countryPillar(country)
                       #await self.analyze_country(country)
                except Exception as e:
                    logger.error(f"Failed to analyze country {country.CountryID} ({country.CountryName}): {e}")
                    continue

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_all_countries_questions: {e}")
            raise

    async def analyze_single_Country(self, countryId: int) -> bool:
        """Analyze Country Questions data for a specific country"""
        try:
            df = self._get_country_data(countryId)
            if df.empty:
                return False

            for country in df.itertuples(index=False):
                await self.analyze_country(country)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_single_Country (CountryID: {countryId}): {e}")
            raise

    async def analyze_country_pillars(self, countryId: int) -> bool:
        """Analyze Country pillar data for a specific country"""
        try:
            df = self._get_country_data(countryId)
            if df.empty:
                return False

            for country in df.itertuples(index=False):
                await self.analyze_countryPillar(country)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_country_pillars (CountryID: {countryId}): {e}")
            raise

    async def analyze_Single_Pillar(self, countryId: int, pillar_id: Optional[int] = None) -> bool:
        """Analyze specific pillar for a country"""
        try:
            df = self._get_country_data(countryId)
            if df.empty:
                return False

            for country in df.itertuples(index=False):
                await self.analyze_countryPillar(country, pillar_id)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_Single_Pillar (CountryID: {countryId}, PillarID: {pillar_id}): {e}")
            raise

    async def analyze_questions_of_country_pillar(self, countryId: int, pillar_id: Optional[int] = None) -> bool:
        """Analyze questions for country pillar"""
        try:
            df = self._get_country_data(countryId)
            if df.empty:
                return False

            for country in df.itertuples(index=False):
                await self.analyze_PillarQuestions(country, pillar_id)

            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_questions_of_country_pillar (CountryID: {countryId}): {e}")
            raise

    def _build_question_record(self, row, ai_data, normalized_value: float) -> dict[str, Any]:
        """Build question evaluation record from AI data aligned with AIEstimatedQuestionScores"""
        
        ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
        evaluator_score = self.to_float_safe(normalized_value * 100)

        return {
                    "CountryID": row.CountryID,
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

    async def analyze_PillarQuestions(self, country: Any, pillar_id: Optional[int] = None) -> bool:
        """Analyze Pillar Questions data for a country"""
        try:
            where = f"countryId = {country.CountryID}"
            if pillar_id is not None:
                where = f"countryId = {country.CountryID} and PillarID={pillar_id}"


            df = db_service.get_view_data("vw_AiCountryPillarQuestionEvaluations", where)
            
            if not len(df):
                db_logger_service.log_message("INFO", f"No pillar questions found for country {country.CountryID} ({country.CountryName})")
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
                                        country.CountryName,
                                        f"Continent :{country.Continent}, Country :{country.CountryName}",
                                        row.PillarID,
                                        row.PillarName,
                                        row.QuestionText,
                                        row.ScoreProgress,
                                        None
                                    )

                            if ai_data["success"]:
                                ai_data["CountryID"] = country.CountryID
                                questionList.append(self._build_question_record(row, ai_data, normalized_value))
                                
                                if len(questionList) == 1:
                                    db_service.bulk_upsert_question_evaluations(questionList)
                                    questionList = []
                            else:
                                db_logger_service.log_message("WARNING", 
                                    f"AI analysis failed for QuestionID {row.QuestionID} in Country {country.CountryID}")
                                
                        except Exception as e:
                            logger.error(f"Error processing question {row.QuestionID} for country {country.CountryID}: {e}")
                            continue
                    
                    if questionList:
                        db_service.bulk_upsert_question_evaluations(questionList)

                except Exception as e:
                    logger.error(f"Error analyzing pillar {pillarId} for country {country.CountryID}: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            logger.error(f"Error in analyze_PillarQuestions for country{country.CountryID}: {e}")
            raise

    async def analyze_countryPillar(self, country: Any, pillar_id: Optional[int] = None) -> bool:
        """Analyze country pillar data and generate evaluations"""

        try:
            where = f"countryId = {country.CountryID} and PillarID = {pillar_id}" if pillar_id else f"countryId = {country.CountryID}"
            df = db_service.get_view_data("vw_AiCountryPillarEvaluation", where)

            if not len(df):
                db_logger_service.log_message("INFO", f"No pillar evaluations found for country {country.CountryID} ({country.CountryName})")
                return False

            pillarList = []
            pillarSourceList = []

            for row in df.itertuples(index=False):
                try:
                    ai_data = await pem_ai_research_service.research_and_score_pillar(
                        country.CountryName,
                        f"Continent :{country.Continent}, Country :{country.CountryName}",
                        row.PillarID,
                        row.PillarName,                        
                        row.EvaluatorScore,
                        row.AIScore,
                    )

                    if not ai_data["success"]:
                        continue
                    
                    # Build pillar record aligned with AIPillarScores
                    ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
                    evaluator_score = self.to_float_safe(row.EvaluatorScore)
                    pillarList.append({
                        "CountryID": row.CountryID,
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
                            "CountryID": row.CountryID,
                            "DataYear": self.to_int_safe(src.get("data_year")),  # ✅ from source
                            "PillarID": row.PillarID,
                            "SourceType": src.get("source_type"),
                            "SourceName": src.get("source_name"),
                            "SourceURL": src.get("source_url"),
                            "DataExtract": src.get("data_extract"),
                            "TrustLevel": self.to_int_safe(src.get("source_trust_level"))
                        })

                    if len(pillarList) == 1:
                        db_service.bulk_upsert_pillar_evaluations(pillarList, pillarSourceList)
                        pillarList = []
                        pillarSourceList = []

                except Exception as e:
                    logger.error(f"Error processing pillar {row.PillarID} for country {country.CountryID}: {e}")
                    continue

            if pillarList:
                db_service.bulk_upsert_pillar_evaluations(pillarList, pillarSourceList)

            return True

        except Exception as e:
            logger.error(f"Error in analyze_countryPillar for country {country.CountryID}: {e}")
            raise
        
        
    async def analyze_country(self, country: Any) -> bool:
        """Analyze overall country data and generate comprehensive evaluation"""

        try:
            df = db_service.get_view_data("vw_AiCountryEvaluations", f"countryId = {country.CountryID}")

            if not len(df):
                db_logger_service.log_message(
                    "INFO",
                    f"No country evaluations found for country {country.CountryID} {country.CountryName})"
                )
                return False

            countryList = []

            for row in df.itertuples(index=False):
                try:
                    year = datetime.now().year
                    ai_data = await pem_ai_research_service.research_and_score_country(
                        country.CountryName,
                        f"Continent :{country.Continent}, Country :{country.CountryName}",
                        row.EvaluatorScore                        
                    )

                    if not ai_data["success"]:
                        continue
                    ai_progress = self.to_float_safe(ai_data.get("AIProgress") or ai_data.get("ai_progress") or 0)
                    evaluator_score = self.to_float_safe(row.EvaluatorScore)
                    countryList.append({
                        "CountryID": row.CountryID,
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

                    if len(countryList) == 1:
                        db_service.bulk_upsert_country_evaluations(countryList)
                        countryList = []

                except Exception as e:
                    logger.error(f"Error processing country evaluation for {country.CountryID}: {e}")
                    continue

            if countryList:
                db_service.bulk_upsert_country_evaluations(countryList)

            return True

        except Exception as e:
            logger.error(f"Error in analyze_country for country {country.CountryID}: {e}")
            raise


# Singleton instance
score_analyzer_service = ScoreAnalyzerService()