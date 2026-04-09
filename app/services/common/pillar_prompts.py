"""
Data Analyzer Service - LLM-powered analysis of SQL Server data
Enhanced with Veridian Urban Index pillar-specific prompts
"""


		
		
class PeaceEnablerPillarPrompts:
    """Provides context, focus areas, and research signals for all 23 Peace Enabler pillars."""
    GOVERNANCE_PROTOCOL = """
        =============================================================================
        AI MASTER GOVERNANCE PROTOCOL (PEM) — MANDATORY FOR EVERY ASSESSMENT
        =============================================================================

        1. TEMPORAL SCOPE
        - Evidence must cover 1950–present.
        - Pre-1950 allowed only if directly linked to current institutions/conflict and must name present-day expression.
        - No score based solely on pre-1950.
        - Every evidence must include year.

        2. EVIDENCE HIERARCHY (priority order)
        L1: Laws, budgets, court rulings, audits, procurement
        L2: Auditor/Ombudsman/anti-corruption/human rights bodies
        L3: UN, World Bank, IMF, regional institutions
        L4: Peer-reviewed research, think tanks
        L5: NGOs / civil society
        L6: Technical / satellite data
        L7: Media (context only, never primary)
        Rules:
        - ≥2 independent sources per claim
        - No single-source scoring
        - Structural/operational > perception

        3. FOUR-LAYER EVIDENCE (ALL REQUIRED)
        a) Structural (laws, institutions)
        b) Operational (budgets, staffing, delivery)
        c) Outcome (measured results)
        d) Perception (trust, grievances)
        → Perception cannot override structural/operational

        4. DISTRIBUTIONAL ANALYSIS (MANDATORY)
        Test for:
        - Regional disparities
        - Urban vs peripheral gaps
        - Income inequality
        - Identity-based inequality
        → Severe disparity = score reduction

        5. DISTORTION SCREENING
        Check for:
        - Election-cycle manipulation
        - Suppressed reporting
        - Restricted media
        - Sudden unexplained improvements
        - Selective datasets
        → Unverifiable = "Unknown" (never rewarded)
        → Data silence MUST NOT be rewarded

        6. SYSTEM INTEGRATION TEST
        Assess interdependence with:
        elite cohesion, fiscal capacity, administration, justice, services, economy,
        environment, information, pluralism, security restraint, education, health,
        gender, business integrity, early warning, external pressures
        → Weak dependencies = lower score

       7. STRESS TEST (REQUIRED)
        Simulate:
        a) Political shock (leadership change, electoral dispute, elite fracture)
        b) Economic shock (currency instability, unemployment surge, fiscal stress)
        c) Narrative shock (disinformation, identity mobilization, grievance escalation)
        → If system is not resilient, reduce score AND document adjustment

        8. SCORING SCALE (FIXED)
         4       = Strong and stress-resilient
         3       = Functioning but uneven
         2       = Mixed and vulnerable
         1       = Structurally weak
         0       = Absent or destabilizing
         N/A     = Structurally irrelevant to this specific city or context
         Unknown = Insufficient verifiable data (document as opacity risk — does NOT
                    reduce the numeric score, but must be flagged)

        9. EVIDENCE EXHAUSTION (MANDATORY BEFORE Unknown/N/A)
        1) Primary evidence → score required
        2) Secondary evidence → partial scoring allowed
        3) Proxy indicators → score required
        4) Cross-indicator inference → score required
        5) Contextual/national baseline → assign minimum (1–2)
        6) Applicability check → N/A only if impossible

        STRICT:
        - Any evidence → MUST score (0–4)
        - Weak system → score 1–2
        - Unknown only if ALL steps fail
        - N/A only if impossible

        UNKNOWN JUSTIFICATION (ALL REQUIRED):
        - No primary, secondary, proxy, cross-indicator, or contextual evidence exists

        10. NON-COMPENSATION
        No trade-offs across pillars (e.g., security ≠ justice, growth ≠ cohesion)

        11. INEQUALITY ADJUSTMENT
        Elite-skewed outcomes → reduce score

        12. DATA SILENCE RULE
        - Assign "Unknown"
        - State cause (conflict, suppression, incapacity, missing systems)
        - Treat as governance risk
        - Silence ≠ success

        13. PROHIBITIONS
        Do NOT:
        - Predict conflicts deterministically
        - Use rankings as analysis
        - Reward opacity
        - Inflate scores due to absence of violence
        - Accept claims without verification
        - Treat reforms as outcomes
        - Use media as primary evidence

        14. INTERPRETATION RULES
        - Trends > static values
        - High variance = fragility
        - Weak clusters = escalation risk
        - Stability without legitimacy = fragile
        - Calm ≠ resilience
        =============================================================================
    """

    PILLAR_CONTEXTS = {
        1: {
            "name": "Historical Memory and Narrative Legitimacy",
            "focus": (
                "How does this country/region interpret its past? Are there unresolved historical grievances "
                "being used for political mobilization? Look for: truth and reconciliation commissions, "
                "contested historical monuments, official history curricula, minority narratives, "
                "memory institutions (museums, memorials), and whether disputes over the past are "
                "handled through dialogue or suppression."
            ),
            "search_signals": [
                "historical reconciliation commission",
                "contested monuments or memorials",
                "minority historical recognition",
                "official history curriculum disputes",
                "collective memory institutions",
            ],
            "red_flags": [
                "Forcible erasure of minority histories",
                "State-sanctioned revisionist narratives",
                "Unprocessed mass atrocity memory",
                "Politically exploited historical grievances",
            ],
        },
        2: {
            "name": "Moral Order and Social Norms",
            "focus": (
                "Are widely shared moral expectations governing conduct across this society? "
                "Look for: social trust surveys, community enforcement of norms, "
                "civic behavior patterns, decline in informal social regulation, rise in "
                "punitive enforcement, community dispute resolution, and whether ethical norms "
                "are respected beyond formal law."
            ),
            "search_signals": [
                "social trust surveys",
                "community cohesion index",
                "civic norms compliance",
                "informal dispute resolution",
                "social fabric breakdown indicators",
            ],
            "red_flags": [
                "Rapid erosion of shared civic norms",
                "Rise in punitive enforcement replacing social trust",
                "High corruption normalized as acceptable behavior",
                "Collapse of informal community accountability",
            ],
        },
        3: {
            "name": "Informal Authority and Customary Mediation",
            "focus": (
                "Do traditional leaders, elders, or community-based mediators play a recognized "
                "role in resolving disputes? Look for: customary court systems, elder council activity, "
                "community mediation centers, indigenous justice mechanisms, and whether these "
                "complement or clash with formal state institutions."
            ),
            "search_signals": [
                "traditional leaders dispute resolution",
                "customary courts activity",
                "elder councils community mediation",
                "indigenous justice mechanisms",
                "community-based conflict resolution",
            ],
            "red_flags": [
                "Violent displacement of traditional authority",
                "State capture of customary institutions",
                "Customary mechanisms used to oppress minorities",
                "Total absence of informal mediation in fragile areas",
            ],
        },
        4: {
            "name": "Religious Institutions and Ethical Leadership",
            "focus": (
                "Do religious institutions contribute to social cohesion, ethical restraint, and "
                "coexistence? Look for: interfaith dialogue initiatives, religious leaders' public "
                "statements on peace, religious institution social services, reports of religious "
                "incitement, and whether faith leaders reinforce inclusion or deepen divisions."
            ),
            "search_signals": [
                "interfaith dialogue initiatives",
                "religious leaders peace statements",
                "religious extremism reports",
                "religious institution social services",
                "faith-based peacebuilding",
            ],
            "red_flags": [
                "Religious leaders inciting ethnic or sectarian violence",
                "State-sponsored religious persecution",
                "Radical religious groups filling governance vacuums",
                "Systematic discrimination justified through religious authority",
            ],
        },
        5: {
            "name": "State Legitimacy and Institutional Integrity",
            "focus": (
                "Do residents broadly trust and accept state authority? Look for: public trust in "
                "government surveys, corruption perceptions index, institutional integrity assessments, "
                "protest levels and causes, bureaucratic transparency, rule-of-law indicators, "
                "and whether institutions serve broad populations or narrow elites."
            ),
            "search_signals": [
                "public trust in government survey",
                "corruption perception index",
                "rule of law index",
                "institutional integrity assessment",
                "government accountability report",
            ],
            "red_flags": [
                "Pervasive institutional corruption",
                "Selective enforcement favoring elites",
                "Parallel governance structures undermining state",
                "Widespread public rejection of state authority",
            ],
        },
        6: {
            "name": "Elite Bargaining and Power-Sharing",
            "focus": (
                "How do political, military, and economic elites manage competition and succession? "
                "Look for: power-sharing agreements, constitutional succession mechanisms, "
                "elite factional conflicts, military involvement in politics, business-political "
                "capture, and whether elite transitions follow predictable institutional rules."
            ),
            "search_signals": [
                "power sharing agreement",
                "political succession crisis",
                "elite factional conflict",
                "military political interference",
                "constitutional leadership transition",
            ],
            "red_flags": [
                "Zero-sum elite competition with no institutional rules",
                "Military coup attempts or threats",
                "Personalization of power eliminating succession paths",
                "Economic elite capture of political institutions",
            ],
        },
        7: {
            "name": "Pluralism and Identity Governance",
            "focus": (
                "How does this country/region manage ethnic, religious, linguistic, and cultural diversity? "
                "Look for: anti-discrimination laws, minority representation in governance, "
                "language rights policies, ethnic or religious violence incidents, inclusion "
                "frameworks, and whether diversity is managed through recognition or coercion."
            ),
            "search_signals": [
                "minority rights protection",
                "ethnic or religious discrimination reports",
                "minority representation government",
                "language rights policy",
                "anti-discrimination framework",
            ],
            "red_flags": [
                "State-sponsored ethnic or religious exclusion",
                "Systematic underrepresentation of minorities",
                "Ethnically motivated violence incidents",
                "Forced assimilation policies",
            ],
        },
        8: {
            "name": "Livelihoods and Economic Dignity",
            "focus": (
                "Do residents have access to meaningful employment and economic security? "
                "Look for: unemployment rates (especially youth), wage adequacy data, "
                "informal economy scale, poverty rates, economic mobility indicators, "
                "household income surveys, and whether economic exclusion correlates with "
                "specific ethnic or regional groups."
            ),
            "search_signals": [
                "unemployment rate",
                "youth unemployment",
                "poverty rate household income",
                "economic exclusion minority",
                "informal economy livelihoods",
            ],
            "red_flags": [
                "Extreme youth unemployment driving radicalization",
                "Economic exclusion correlated with ethnic identity",
                "Collapse of formal employment without safety nets",
                "Persistent inter-generational poverty traps",
            ],
        },
        9: {
            "name": "Urban and Territorial Governance",
            "focus": (
                "Is governance capacity consistent across the country's geography, including peripheral "
                "and underserved areas? Look for: service delivery inequality data, municipal "
                "decentralization effectiveness, informal settlement governance, infrastructure "
                "gap between central and peripheral zones, and territorial control challenges."
            ),
            "search_signals": [
                "service delivery inequality urban areas",
                "informal settlement governance",
                "municipal decentralization",
                "urban periphery infrastructure gap",
                "territorial control breakdown",
            ],
            "red_flags": [
                "Complete absence of state services in peripheral zones",
                "Non-state armed groups controlling urban territories",
                "Extreme inequality between CBD and peripheral settlements",
                "Governance breakdown in rapidly growing urban areas",
            ],
        },
        10: {
            "name": "Environmental Stress and Resource Management",
            "focus": (
                "Are environmental pressures — climate change, water scarcity, land competition — "
                "being effectively governed? Look for: climate vulnerability assessments, "
                "water access data, land conflict reports, environmental governance quality, "
                "disaster risk management plans, and whether resource pressures are translating "
                "into social conflict."
            ),
            "search_signals": [
                "climate vulnerability assessment",
                "water scarcity conflict",
                "land use dispute",
                "environmental governance quality",
                "disaster risk management plan",
            ],
            "red_flags": [
                "Resource scarcity directly triggering violent conflict",
                "Environmental displacement without managed relocation",
                "Elite capture of scarce natural resources",
                "Lack of climate adaptation planning in high-risk zones",
            ],
        },
        11: {
            "name": "Information Ecosystems and Digital Space",
            "focus": (
                "Is the information environment characterized by credible institutions and balanced "
                "narratives, or driven by manipulation and disorder? Look for: media freedom index, "
                "disinformation reports, social media polarization data, press freedom ratings, "
                "digital access inequality, and the role of state or private actors in shaping "
                "information flows."
            ),
            "search_signals": [
                "media freedom index",
                "disinformation campaigns",
                "press freedom rating",
                "social media polarization",
                "digital access inequality",
            ],
            "red_flags": [
                "State-directed disinformation at scale",
                "Journalist killings or systematic persecution",
                "Social media driving ethnic incitement",
                "Complete media capture by political or business elites",
            ],
        },
        12: {
            "name": "Early Warning and Crisis Response Capacity",
            "focus": (
                "Can institutions detect, interpret, and respond to emerging tension signals before "
                "they escalate? Look for: conflict early warning systems, emergency response coordination "
                "structures, community-level tension monitoring, crisis management protocols, "
                "and whether past crisis escalations reveal systemic warning failures."
            ),
            "search_signals": [
                "conflict early warning system",
                "crisis response capacity",
                "emergency management coordination",
                "tension monitoring mechanism",
                "rapid response community conflict",
            ],
            "red_flags": [
                "Repeated escalation failures despite early signals",
                "No functional early warning infrastructure",
                "Political interference blocking timely crisis response",
                "Coordination failures across security and civilian agencies",
            ],
        },
        13: {
            "name": "External Pressures and Regional Dynamics",
            "focus": (
                "Is this country or region exposed to cross-border conflict, geopolitical competition, "
                "or regional instability spillovers? Look for: refugee and displacement flows, "
                "cross-border armed group activity, regional peace agreements, foreign political "
                "interference, and economic dependency on unstable neighbors."
            ),
            "search_signals": [
                "cross-border conflict spillover",
                "refugee displacement flows",
                "regional geopolitical competition",
                "foreign political interference",
                "regional peace agreement",
            ],
            "red_flags": [
                "Active armed group cross-border infiltration",
                "Mass refugee inflows straining local capacity",
                "Foreign state destabilization activities",
                "Economic collapse of neighboring states affecting local stability",
            ],
        },
        14: {
            "name": "Business Systems and Market Integrity",
            "focus": (
                "Are market systems operating with fairness, predictability, and integrity? "
                "Look for: business environment rankings, anti-monopoly enforcement, "
                "contract enforcement reliability, predatory business practices, "
                "market access for marginalized groups, and whether business elites "
                "are operating above legal accountability."
            ),
            "search_signals": [
                "business environment ranking",
                "market corruption report",
                "contract enforcement reliability",
                "economic monopoly capture",
                "market access marginalized groups",
            ],
            "red_flags": [
                "Systemic predatory capture of market by political elites",
                "Exclusion of minority or vulnerable groups from formal markets",
                "No functioning contract enforcement mechanisms",
                "Widespread extortion normalizing informal business payments",
            ],
        },
        15: {
            "name": "Justice, Accountability, and Moral Repair",
            "focus": (
                "Are justice systems accessible, functional, and oriented toward accountability "
                "and healing? Look for: access to justice surveys, court independence ratings, "
                "transitional justice mechanisms, victim reparations programs, impunity indices, "
                "and whether unresolved historical injustices are being addressed through "
                "credible legal and moral processes."
            ),
            "search_signals": [
                "access to justice survey",
                "court independence rating",
                "transitional justice mechanism",
                "impunity index",
                "victim reparation program",
            ],
            "red_flags": [
                "Systematic impunity for political or security elites",
                "Courts operating as instruments of political suppression",
                "Mass atrocity crimes without accountability processes",
                "Victim communities excluded from justice mechanisms",
            ],
        },
        16: {
            "name": "Security Institutions and Civil-Security Relations",
            "focus": (
                "Are security forces professional, restrained, and trusted by the public? "
                "Look for: police misconduct reports, use-of-force data, security sector "
                "oversight mechanisms, human rights abuse by security forces, civilian "
                "trust in police surveys, and whether security institutions are accountable "
                "to civilian governance."
            ),
            "search_signals": [
                "police misconduct human rights",
                "security force oversight",
                "civilian trust in police survey",
                "use of force abuse report",
                "security sector accountability",
            ],
            "red_flags": [
                "Systematic extrajudicial violence by security forces",
                "Security forces operating as political instruments",
                "No functional civilian oversight of security institutions",
                "Ethnic targeting by police or military",
            ],
        },
        17: {
            "name": "Fiscal Capacity and Redistribution Politics",
            "focus": (
                "Can the state effectively raise and fairly distribute resources? "
                "Look for: revenue collection efficiency, public spending equity data, "
                "budget transparency reports, redistribution effectiveness, "
                "fiscal decentralization to local government, and whether fiscal "
                "policy reinforces or alleviates inequality."
            ),
            "search_signals": [
                "public budget transparency",
                "revenue collection efficiency",
                "fiscal redistribution equity",
                "government spending inequality",
                "local government fiscal capacity",
            ],
            "red_flags": [
                "Severe fiscal crisis undermining basic service delivery",
                "Budget allocations systematically excluding minority regions",
                "Elite tax evasion at scale with no enforcement",
                "Corruption in public expenditure management",
            ],
        },
        18: {
            "name": "Education and Knowledge Systems",
            "focus": (
                "Is education equitable, quality-focused, and building shared civic foundations? "
                "Look for: school enrollment and completion rates, education quality assessments "
                "(PISA, national exams), curriculum content on civic values and diversity, "
                "education access for minorities and girls, teacher quality data, "
                "and whether education reproduces or reduces inequality."
            ),
            "search_signals": [
                "school enrollment completion rate",
                "education quality assessment",
                "civic education curriculum",
                "education access minority girls",
                "teacher quality learning outcomes",
            ],
            "red_flags": [
                "Education system actively reproducing ethnic or class divisions",
                "Systematic exclusion of minorities from quality education",
                "Curriculum promoting exclusionary nationalism",
                "High dropout rates correlated with poverty or gender",
            ],
        },
        19: {
            "name": "Health, Demography, and Human Viability",
            "focus": (
                "Are health systems functional and equitable, and are demographic pressures "
                "being managed effectively? Look for: health system capacity data, "
                "infant and maternal mortality rates, disease burden by income group, "
                "demographic pressure indicators (youth bulge, rapid urbanization), "
                "health access inequality, and pandemic preparedness assessments."
            ),
            "search_signals": [
                "health system capacity",
                "infant maternal mortality rate",
                "health access inequality",
                "demographic pressure youth bulge",
                "pandemic preparedness",
            ],
            "red_flags": [
                "Health system collapse in conflict-affected areas",
                "Severe health access inequality by ethnicity or region",
                "Youth bulge with no corresponding economic opportunity",
                "Health infrastructure used as instrument of exclusion",
            ],
        },
        20: {
            "name": "Gender Order and Family Structures",
            "focus": (
                "Are gender power relations equitable within households and in public life? "
                "Look for: gender-based violence rates, women's political representation, "
                "girls' education access, women's economic participation, "
                "domestic violence reporting systems, and whether gender inequality "
                "mirrors or amplifies broader structural tensions."
            ),
            "search_signals": [
                "gender-based violence rates",
                "women political representation",
                "girls education access",
                "women economic participation",
                "domestic violence reporting",
            ],
            "red_flags": [
                "High femicide rates with no accountability",
                "Women systematically excluded from governance",
                "Gender-based violence used as conflict weapon",
                "Legal frameworks enabling gender discrimination",
            ],
        },
        21: {
            "name": "Administrative Capacity and State Execution",
            "focus": (
                "Can government actually implement its decisions competently and consistently? "
                "Look for: public service delivery quality assessments, government efficiency "
                "rankings, policy implementation gap analyses, bureaucratic capacity surveys, "
                "e-government adoption, and whether administrative failures reflect "
                "resource gaps or structural dysfunction."
            ),
            "search_signals": [
                "government administrative efficiency",
                "public service delivery quality",
                "policy implementation capacity",
                "e-government digital services",
                "bureaucratic effectiveness ranking",
            ],
            "red_flags": [
                "Systemic inability to implement policies despite resources",
                "Patronage replacing meritocracy in civil service",
                "Major gap between laws enacted and laws enforced",
                "Administrative collapse in peripheral or minority regions",
            ],
        },
        22: {
            "name": "Absence of Active Conflict and Organized Violence",
            "focus": (
                "What is the current level of armed conflict, organized violence, and terrorism? "
                "Look for: active conflict incident data (ACLED, UCDP), terrorist attack frequency, "
                "criminal violence rates (homicide, organized crime), displaced population figures, "
                "ceasefire and peace agreement status, and whether violence is declining, "
                "stable, or escalating."
            ),
            "search_signals": [
                "armed conflict incidents ACLED",
                "terrorism attack frequency",
                "homicide rate organized crime",
                "internally displaced population",
                "peace agreement ceasefire status",
            ],
            "red_flags": [
                "Active large-scale armed conflict with civilian casualties",
                "Terrorist attacks on civilian infrastructure",
                "Criminal violence at war-level rates",
                "Mass displacement without durable solutions",
            ],
        },
        23: {
            "name": "Freedom of Religion, Belief, and Conscience",
            "focus": (
                "Are all belief communities protected in their practice, worship, and expression? "
                "Look for: religious freedom index scores, reports of state persecution of minority "
                "faiths, blasphemy law enforcement, forced conversions, destruction of places of "
                "worship, conscientious objector protections, and whether legal frameworks "
                "protect belief diversity within a shared civic order."
            ),
            "search_signals": [
                "religious freedom index",
                "minority faith persecution",
                "blasphemy law enforcement",
                "forced religious conversion",
                "place of worship destruction",
            ],
            "red_flags": [
                "State persecution of religious minorities",
                "Blasphemy laws used to suppress dissent",
                "Forced conversion or religious identity suppression",
                "Systematic destruction of minority religious sites",
            ],
        },
    }

    @classmethod
    def get_pillar_context(cls, pillar_id: int) -> str:
        """Return formatted context string for a given pillar ID (1-23)."""
        if pillar_id not in cls.PILLAR_CONTEXTS:
            return f"No context available for pillar ID {pillar_id}."

        pillar = cls.PILLAR_CONTEXTS[pillar_id]
        signals = "\n  - ".join(pillar["search_signals"])
        red_flags = "\n  - ".join(pillar["red_flags"])

        return (
            f"PILLAR: {pillar['name']}\n\n"
            f"FOCUS AREAS:\n{pillar['focus']}\n\n"
            f"KEY SEARCH SIGNALS:\n  - {signals}\n\n"
            f"RED FLAGS TO DETECT:\n  - {red_flags}"
        )

    @classmethod
    def get_all_pillar_names(cls) -> dict:
        """Return a mapping of pillar ID to pillar name."""
        return {
            pid: ctx["name"]
            for pid, ctx in cls.PILLAR_CONTEXTS.items()
        }
		