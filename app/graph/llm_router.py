from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class LLMRouter:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3)
        self.routing_prompt = ChatPromptTemplate.from_template("""
        Analyze current Dota 2 match state and determine next analysis phase.

        Current State:
        - Phase: {current_phase}
        - Game Time: {game_time}
        - Current Metrics: {metrics}

        Key Indicators:
        - Draft Phase: Hero selections, bans, team composition
        - Early Game: Lane setups, initial farm patterns (0-15min)
        - Mid Game: Team movements, objectives (15-30min)
        - Late Game: High ground pushes, critical fights (30+min)

        Determine next analysis phase based on game state indicators.
        Return only the phase name: [draft_analysis, early_game_analysis, mid_game_analysis, late_game_analysis, conclusion]
        """)

    def route(self, state: MatchAnalysisState) -> str:
        # Get routing decision from LLM
        response = self.llm.invoke(
            self.routing_prompt.format(
                current_phase=state["current_phase"],
                game_time=state["raw_data"].get("game_time", 0),
                metrics=self._extract_metrics(state)
            )
        )

        # Map LLM response to valid next node
        phase_mapping = {
            "draft_analysis": "draft_analysis",
            "early_game_analysis": "early_game_analysis",
            "mid_game_analysis": "mid_game_analysis",
            "late_game_analysis": "late_game_analysis",
            "conclusion": "conclusion"
        }

        return phase_mapping.get(response.content.strip().lower(), END)

    def _extract_metrics(self, state: MatchAnalysisState) -> Dict:
        """Extract relevant metrics for routing decision"""
        return {
            "tower_status": state["raw_data"].get("tower_status", {}),
            "gold_advantage": state["raw_data"].get("gold_advantage", 0),
            "kill_score": state["raw_data"].get("kill_score", "0-0")
        }

# Usage in Graph
workflow.add_conditional_edges(
    "data_ingestion",
    LLMRouter().route,
    {
        "draft_analysis": "draft_analysis",
        "early_game_analysis": "early_game_analysis",
        "mid_game_analysis": "mid_game_analysis",
        "late_game_analysis": "late_game_analysis",
        "conclusion": "conclusion",
        END: END
    }
)