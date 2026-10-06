from collections import Counter
from typing import Any, Dict, List, Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.workflow.conditions import ConditionEvaluator

class ReportingTool(BaseTool):
    name = "reporting_tool"
    description = "Analyzes execution logs to compute success/failure rates, average durations, and improvement recommendations."

    def run(self, logs: List[Dict[str, Any]], fail_threshold_pct: float = 10.0, time_threshold_sec: float = 3.0, **kwargs) -> ToolResult:
        if not logs:
            return ToolResult(success=False, error="No execution logs provided to reporting_tool.")

        total_runs = len(logs)
        success_runs = sum(1 for log in logs if str(log.get("status", "")).upper() in ("SUCCESS", "COMPLETED", "OK"))
        failed_runs = total_runs - success_runs
        failure_rate_pct = round((failed_runs / total_runs) * 100.0, 2) if total_runs > 0 else 0.0
        success_rate_pct = round((success_runs / total_runs) * 100.0, 2) if total_runs > 0 else 0.0

        durations = [float(log.get("duration_seconds", 0)) for log in logs if str(log.get("duration_seconds", "")).replace(".", "", 1).isdigit()]
        avg_duration_sec = round(sum(durations) / len(durations), 2) if durations else 0.0

        # Group by workflow
        wf_stats: Dict[str, Dict[str, Any]] = {}
        error_counts = Counter()

        for log in logs:
            wf_id = str(log.get("workflow_id", "GENERAL")).upper()
            status = str(log.get("status", "")).upper()
            duration = float(log.get("duration_seconds", 0)) if str(log.get("duration_seconds", "")).replace(".", "", 1).isdigit() else 0.0
            err = log.get("error_message")

            if err and str(err).strip() and str(err).lower() != "nan":
                error_counts[str(err).strip()] += 1

            if wf_id not in wf_stats:
                wf_stats[wf_id] = {"total": 0, "success": 0, "failed": 0, "durations": []}
            wf_stats[wf_id]["total"] += 1
            if status in ("SUCCESS", "COMPLETED", "OK"):
                wf_stats[wf_id]["success"] += 1
            else:
                wf_stats[wf_id]["failed"] += 1
            wf_stats[wf_id]["durations"].append(duration)

        flagged_workflows = []
        for wf_id, s in wf_stats.items():
            wf_fail_rate = round((s["failed"] / s["total"]) * 100.0, 2)
            wf_avg_dur = round(sum(s["durations"]) / len(s["durations"]), 2) if s["durations"] else 0.0
            
            cond = ConditionEvaluator.evaluate_workflow_performance(
                failure_rate_pct=wf_fail_rate,
                avg_duration_sec=wf_avg_dur,
                fail_threshold=fail_threshold_pct,
                time_threshold=time_threshold_sec
            )
            
            if cond.passed:
                flagged_workflows.append({
                    "workflow_id": wf_id,
                    "total_runs": s["total"],
                    "failure_rate_pct": wf_fail_rate,
                    "avg_duration_sec": wf_avg_dur,
                    "issues": cond.details.get("issues", [])
                })

        recommendations = []
        if flagged_workflows:
            for fw in flagged_workflows:
                recommendations.append(f"Investigate {fw['workflow_id']}: {', '.join(fw['issues'])}.")
        else:
            recommendations.append("All workflows operating within SLA performance parameters.")

        report = {
            "summary_metrics": {
                "total_executions": total_runs,
                "success_rate_pct": success_rate_pct,
                "failure_rate_pct": failure_rate_pct,
                "average_execution_time_sec": avg_duration_sec
            },
            "flagged_workflows": flagged_workflows,
            "frequent_errors": [{"error": err, "count": count} for err, count in error_counts.most_common(5)],
            "recommendations": recommendations
        }

        return ToolResult(
            success=True,
            data=report,
            message=f"Analyzed {total_runs} execution logs. {len(flagged_workflows)} workflow(s) flagged for optimization."
        )
