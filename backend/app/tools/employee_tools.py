import re
from typing import Any, Dict, List, Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.tools.file_tools import CSVReaderTool

class EmployeeRankingTool(BaseTool):
    name = "ranking_tool"
    description = "Ranks employees based on required skill overlaps and available workload capacity."

    def run(
        self, 
        task_description: str,
        required_skills: Optional[List[str]] = None,
        priority: str = "Medium",
        deadline: str = "Immediate",
        **kwargs
    ) -> ToolResult:
        csv_tool = CSVReaderTool()
        res = csv_tool.run(file_path="sample_data/employees.csv")
        employees: List[Dict[str, Any]] = res.data if res.success else []

        if not employees:
            return ToolResult(success=False, error="No employee records found in database.")

        # Extract required skills if not explicitly provided
        req_skills_set = set()
        if required_skills:
            req_skills_set = {s.strip().lower() for s in required_skills}
        else:
            # Simple keyword extraction from task description
            words = set(re.findall(r"\b[a-zA-Z]{3,}\b", task_description.lower()))
            common_skills = {"python", "fastapi", "react", "sql", "docker", "etl", "seo", "copywriting", "cloud", "typescript"}
            req_skills_set = words.intersection(common_skills)

        scored_candidates = []

        for emp in employees:
            emp_skills = [s.strip().lower() for s in str(emp.get("skills", "")).split(";")]
            current_workload = float(emp.get("current_workload_hours", 40))
            max_capacity = float(emp.get("max_capacity_hours", 40))
            available_hours = max(0.0, max_capacity - current_workload)

            # Calculate skill match score
            if req_skills_set:
                matched_skills = [s for s in emp_skills if any(req in s for req in req_skills_set)]
                skill_score = (len(matched_skills) / len(req_skills_set)) * 100.0
            else:
                matched_skills = emp_skills
                skill_score = 50.0

            # Calculate capacity score (0-100 based on available hours)
            capacity_score = (available_hours / max_capacity) * 100.0 if max_capacity > 0 else 0.0

            # Weighted final score: 65% skills + 35% available capacity
            total_score = round((skill_score * 0.65) + (capacity_score * 0.35), 2)

            scored_candidates.append({
                "employee_id": emp.get("employee_id"),
                "name": emp.get("name"),
                "role": emp.get("role"),
                "skills": emp.get("skills"),
                "matched_skills": matched_skills,
                "available_hours": available_hours,
                "current_workload": current_workload,
                "score": total_score
            })

        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidate = scored_candidates[0] if scored_candidates else None

        # Decision rule: Escalate if score is too low or no suitable capacity
        if not top_candidate or top_candidate["score"] < 25.0:
            return ToolResult(
                success=True,
                data={
                    "status": "ESCALATION_REQUIRED",
                    "reasoning": "No candidate possesses the required skill profile or sufficient available capacity.",
                    "candidates": scored_candidates
                },
                message="Escalation triggered: No suitable employee found."
            )

        return ToolResult(
            success=True,
            data={
                "status": "ASSIGNED",
                "recommended_employee": top_candidate,
                "reasoning": f"Candidate {top_candidate['name']} selected with score {top_candidate['score']}/100. Matched skills: {', '.join(top_candidate['matched_skills'])}, Available capacity: {top_candidate['available_hours']} hrs.",
                "ranked_candidates": scored_candidates,
                "task_summary": {
                    "task": task_description,
                    "priority": priority,
                    "deadline": deadline,
                    "assigned_to": top_candidate["name"]
                }
            },
            message=f"Recommended assignment: {top_candidate['name']} ({top_candidate['role']})."
        )
