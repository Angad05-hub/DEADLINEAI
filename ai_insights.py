"""
AI-powered insights generation for assignments.

This module provides functionality to generate intelligent insights about
assignments, including deadline analysis, workload estimation, priority
recommendations, and personalized suggestions.

Author: DEADLINEAI Team
Date: 2025-12-24
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PriorityLevel(Enum):
    """Priority levels for assignments."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DifficultyLevel(Enum):
    """Difficulty levels for assignments."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Assignment:
    """Represents an assignment with its metadata."""
    id: str
    title: str
    description: str
    deadline: datetime
    subject: str
    estimated_hours: float
    difficulty: DifficultyLevel
    priority: PriorityLevel
    completed: bool = False
    progress: float = 0.0
    dependencies: List[str] = None


@dataclass
class InsightMetric:
    """Represents a single insight metric."""
    name: str
    value: Any
    unit: str = ""
    interpretation: str = ""


class AssignmentInsights:
    """Generates AI-powered insights for assignments."""

    def __init__(self, assignments: List[Assignment]):
        """
        Initialize the insights generator with a list of assignments.

        Args:
            assignments: List of Assignment objects to analyze.
        """
        self.assignments = assignments
        self.current_time = datetime.utcnow()

    def calculate_urgency_score(self, assignment: Assignment) -> float:
        """
        Calculate urgency score for an assignment (0-100).

        Args:
            assignment: The assignment to score.

        Returns:
            Urgency score from 0 (not urgent) to 100 (extremely urgent).
        """
        if assignment.completed:
            return 0.0

        time_remaining = (assignment.deadline - self.current_time).total_seconds() / 3600
        estimated_hours = assignment.estimated_hours

        if time_remaining <= 0:
            return 100.0

        urgency = (estimated_hours / max(time_remaining, 1)) * 50
        urgency += (100 - time_remaining) / 10 if time_remaining < 24 else 0
        urgency += self._priority_weight(assignment.priority)

        return min(urgency, 100.0)

    def calculate_workload_distribution(self) -> Dict[str, float]:
        """
        Analyze workload distribution across different time periods.

        Returns:
            Dictionary with workload distribution insights.
        """
        distribution = {
            "today": 0.0,
            "this_week": 0.0,
            "this_month": 0.0,
            "overdue": 0.0
        }

        for assignment in self.assignments:
            if assignment.completed:
                continue

            time_diff = assignment.deadline - self.current_time
            remaining_hours = time_diff.total_seconds() / 3600

            if remaining_hours < 0:
                distribution["overdue"] += assignment.estimated_hours
            elif remaining_hours <= 24:
                distribution["today"] += assignment.estimated_hours
            elif remaining_hours <= 7 * 24:
                distribution["this_week"] += assignment.estimated_hours
            else:
                distribution["this_month"] += assignment.estimated_hours

        return distribution

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate AI-powered recommendations for assignment management.

        Returns:
            List of recommendation dictionaries.
        """
        recommendations = []

        # Check for overdue assignments
        overdue_assignments = [
            a for a in self.assignments
            if not a.completed and a.deadline < self.current_time
        ]

        if overdue_assignments:
            recommendations.append({
                "type": "critical",
                "category": "overdue",
                "message": f"You have {len(overdue_assignments)} overdue assignment(s). Prioritize completing them immediately.",
                "affected_assignments": [a.id for a in overdue_assignments],
                "priority": PriorityLevel.CRITICAL.value
            })

        # Analyze heavy workload periods
        workload = self.calculate_workload_distribution()
        if workload["today"] > 10:
            recommendations.append({
                "type": "warning",
                "category": "heavy_workload",
                "message": f"You have {workload['today']:.1f} hours of work due today. Consider adjusting your schedule.",
                "affected_period": "today",
                "priority": PriorityLevel.HIGH.value
            })

        # Check for unstarted high-priority assignments
        unstarted_high_priority = [
            a for a in self.assignments
            if not a.completed and a.progress == 0
            and a.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
        ]

        if unstarted_high_priority:
            recommendations.append({
                "type": "info",
                "category": "start_urgent",
                "message": f"Start {len(unstarted_high_priority)} high-priority assignment(s) that haven't been started.",
                "affected_assignments": [a.id for a in unstarted_high_priority],
                "priority": PriorityLevel.HIGH.value
            })

        return recommendations

    def get_prioritized_assignment_order(self) -> List[Assignment]:
        """
        Get assignments sorted by recommended priority order.

        Returns:
            List of assignments sorted by priority.
        """
        incomplete_assignments = [a for a in self.assignments if not a.completed]

        def priority_key(assignment: Assignment) -> tuple:
            urgency = self.calculate_urgency_score(assignment)
            difficulty_weight = self._difficulty_weight(assignment.difficulty)
            return (-urgency, -difficulty_weight, assignment.deadline)

        return sorted(incomplete_assignments, key=priority_key)

    def estimate_completion_time(self) -> Optional[datetime]:
        """
        Estimate when all assignments can be completed.

        Returns:
            Estimated completion datetime or None if impossible.
        """
        prioritized = self.get_prioritized_assignment_order()
        current_time = self.current_time
        total_hours = sum(a.estimated_hours for a in prioritized)

        if total_hours == 0:
            return current_time

        # Assume 8 hours of work per day
        days_needed = total_hours / 8
        estimated_completion = current_time + timedelta(days=days_needed)

        # Check if deadline violations exist
        for assignment in prioritized:
            if assignment.deadline < estimated_completion:
                return None

        return estimated_completion

    def generate_daily_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive daily insights.

        Returns:
            Dictionary containing daily insights.
        """
        workload = self.calculate_workload_distribution()
        recommendations = self.generate_recommendations()
        prioritized = self.get_prioritized_assignment_order()

        completion_estimate = self.estimate_completion_time()

        return {
            "generated_at": self.current_time.isoformat(),
            "summary": {
                "total_assignments": len(self.assignments),
                "completed": sum(1 for a in self.assignments if a.completed),
                "pending": sum(1 for a in self.assignments if not a.completed),
                "overdue": len([a for a in self.assignments if not a.completed and a.deadline < self.current_time])
            },
            "workload": workload,
            "next_deadline": self._get_next_deadline(),
            "priority_list": [
                {
                    "id": a.id,
                    "title": a.title,
                    "deadline": a.deadline.isoformat(),
                    "urgency_score": self.calculate_urgency_score(a),
                    "estimated_hours": a.estimated_hours
                }
                for a in prioritized[:5]
            ],
            "recommendations": recommendations,
            "estimated_completion": completion_estimate.isoformat() if completion_estimate else None
        }

    def _priority_weight(self, priority: PriorityLevel) -> float:
        """Get urgency weight for priority level."""
        weights = {
            PriorityLevel.CRITICAL: 30.0,
            PriorityLevel.HIGH: 20.0,
            PriorityLevel.MEDIUM: 10.0,
            PriorityLevel.LOW: 0.0
        }
        return weights.get(priority, 0.0)

    def _difficulty_weight(self, difficulty: DifficultyLevel) -> float:
        """Get weight for difficulty level."""
        weights = {
            DifficultyLevel.BEGINNER: 1.0,
            DifficultyLevel.INTERMEDIATE: 2.0,
            DifficultyLevel.ADVANCED: 3.0,
            DifficultyLevel.EXPERT: 4.0
        }
        return weights.get(difficulty, 2.0)

    def _get_next_deadline(self) -> Optional[str]:
        """Get the next upcoming deadline."""
        incomplete = [a for a in self.assignments if not a.completed and a.deadline >= self.current_time]
        if not incomplete:
            return None
        next_assignment = min(incomplete, key=lambda a: a.deadline)
        return next_assignment.deadline.isoformat()


class InsightAnalyzer:
    """Advanced analysis and reporting for assignment insights."""

    @staticmethod
    def generate_performance_report(insights: AssignmentInsights) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.

        Args:
            insights: AssignmentInsights instance.

        Returns:
            Performance report dictionary.
        """
        daily_insights = insights.generate_daily_insights()

        return {
            "report_type": "performance",
            "timestamp": datetime.utcnow().isoformat(),
            "insights": daily_insights,
            "suggestions": _get_personalized_suggestions(insights)
        }

    @staticmethod
    def export_insights_json(insights: AssignmentInsights, filepath: str) -> bool:
        """
        Export insights to JSON file.

        Args:
            insights: AssignmentInsights instance.
            filepath: Path to save the JSON file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            daily_insights = insights.generate_daily_insights()
            with open(filepath, 'w') as f:
                json.dump(daily_insights, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting insights: {e}")
            return False


def _get_personalized_suggestions(insights: AssignmentInsights) -> List[str]:
    """Generate personalized suggestions based on insights."""
    suggestions = []

    workload = insights.calculate_workload_distribution()

    if workload["overdue"] > 0:
        suggestions.append("Focus on completing overdue assignments first to avoid further delays.")

    if workload["today"] > 8:
        suggestions.append("Break down today's tasks into smaller chunks to stay motivated.")

    if len(insights.get_prioritized_assignment_order()) > 5:
        suggestions.append("Consider focusing on your top 3 priorities to avoid feeling overwhelmed.")

    if insights.estimate_completion_time() is None:
        suggestions.append("Your current workload exceeds available time. Consider negotiating deadlines or delegating tasks.")

    return suggestions or ["Keep up the good pace! Stay focused and manage your time effectively."]


def create_sample_assignments() -> List[Assignment]:
    """Create sample assignments for testing."""
    base_time = datetime.utcnow()

    return [
        Assignment(
            id="A001",
            title="Python Project - Data Analysis",
            description="Analyze CSV data and create visualizations",
            deadline=base_time + timedelta(hours=24),
            subject="Computer Science",
            estimated_hours=6,
            difficulty=DifficultyLevel.INTERMEDIATE,
            priority=PriorityLevel.HIGH,
            progress=0.3
        ),
        Assignment(
            id="A002",
            title="Essay - History of AI",
            description="Write 2000 words on AI evolution",
            deadline=base_time + timedelta(days=3),
            subject="History",
            estimated_hours=8,
            difficulty=DifficultyLevel.INTERMEDIATE,
            priority=PriorityLevel.MEDIUM,
            progress=0.0
        ),
        Assignment(
            id="A003",
            title="Math Problem Set",
            description="Complete 20 calculus problems",
            deadline=base_time + timedelta(hours=12),
            subject="Mathematics",
            estimated_hours=4,
            difficulty=DifficultyLevel.ADVANCED,
            priority=PriorityLevel.CRITICAL,
            progress=0.0
        ),
    ]


if __name__ == "__main__":
    # Example usage
    sample_assignments = create_sample_assignments()
    insights = AssignmentInsights(sample_assignments)

    daily_insights = insights.generate_daily_insights()
    print(json.dumps(daily_insights, indent=2))
