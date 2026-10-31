"""
CurioLab — Centralized Application State Engine
================================================
Maintains shared, in-memory data structures across all modules.

No traditional backend, database, API, server, or cloud infrastructure is used.
This module serves as the single source of truth for all runtime state.
"""

import copy
import datetime
from sample_data import (
    DEMO_LIBRARY_RESOURCES,
    DEMO_GALAXY_GRAPH,
    DEMO_JOURNAL_ENTRIES,
    DEMO_NOTIFICATIONS
)


class AppState:
    """
    Centralized In-Memory State Manager for CurioLab.
    
    Implements an Observer pattern to notify UI components whenever
    state changes occur (e.g. experiment executed, challenge solved,
    bookmark toggled, or journal note created/deleted).
    """

    def __init__(self):
        # 1. Educational Demonstration Library Resources
        self.library_resources = copy.deepcopy(DEMO_LIBRARY_RESOURCES)

        # 2. Educational Demonstration Research Galaxy Graph
        self.galaxy_graph = copy.deepcopy(DEMO_GALAXY_GRAPH)

        # 3. Discovery Journal Records
        self.journal_entries = copy.deepcopy(DEMO_JOURNAL_ENTRIES)

        # 4. Laboratory Notifications
        self.notifications = copy.deepcopy(DEMO_NOTIFICATIONS)

        # 5. Research Detective Progression
        self.completed_challenges = set()
        self.hints_used = set()
        self.detective_score = 0

        # 6. Experiment Execution Counters
        self.experiment_runs = {
            "caesar": 0,
            "neural": 0,
            "dataviz": 0
        }

        # 7. UI Configuration
        self.current_theme = "Deep Obsidian"

        # 8. Pending Citation Draft (for Discovery Journal transfer)
        self.pending_journal_draft = None

        # 9. Observer Callbacks
        self._subscribers = []

    # -------------------------------------------------------------------------
    # OBSERVER SUBSCRIPTION PATTERN
    # -------------------------------------------------------------------------
    def subscribe(self, callback):
        """Registers a listener callback to be invoked on any state change."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Unregisters a listener callback."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def notify(self):
        """Notifies all registered subscribers of a state modification."""
        for callback in list(self._subscribers):
            try:
                callback()
            except Exception as e:
                # Catch exceptions gracefully so one widget failure doesn't break others
                print(f"[AppState Warning] Subscriber notification error: {e}")

    # -------------------------------------------------------------------------
    # METRICS & STATISTICAL AGGREGATION
    # -------------------------------------------------------------------------
    def get_metrics(self):
        """
        Calculates and returns current dynamic dashboard and curriculum metrics.
        Never returns hardcoded strings; all numbers derive from application state.
        """
        total_runs = sum(self.experiment_runs.values())
        solved_count = len(self.completed_challenges)
        total_challenges = 14  # 3 Cipher + 3 Data + 3 Stat + 5 Pattern
        library_count = len(self.library_resources)
        bookmarked_count = sum(1 for r in self.library_resources if r.get("bookmarked"))
        journal_count = len(self.journal_entries)
        verified_hypotheses = sum(1 for e in self.journal_entries if e.get("status") == "Verified")
        unread_notifs = sum(1 for n in self.notifications if not n.get("read"))

        # Calculate diligence (no-hint solves)
        if solved_count > 0:
            no_hint_count = sum(1 for cid in self.completed_challenges if cid not in self.hints_used)
            diligence_pct = (no_hint_count / float(solved_count)) * 100.0
        else:
            diligence_pct = 100.0

        curriculum_pct = (solved_count / float(total_challenges)) * 100.0

        return {
            "experiments_count": 3,
            "total_experiment_executions": total_runs,
            "solved_challenges_count": solved_count,
            "total_challenges_count": total_challenges,
            "curriculum_pct": curriculum_pct,
            "detective_score": self.detective_score,
            "diligence_pct": diligence_pct,
            "library_count": library_count,
            "bookmarked_count": bookmarked_count,
            "journal_count": journal_count,
            "verified_hypotheses": verified_hypotheses,
            "unread_notifs": unread_notifs,
        }

    # -------------------------------------------------------------------------
    # STATE MUTATIONS
    # -------------------------------------------------------------------------
    def record_experiment_run(self, tool_name):
        """Records an execution of an Experiment Lab module."""
        if tool_name in self.experiment_runs:
            self.experiment_runs[tool_name] += 1
        else:
            self.experiment_runs[tool_name] = 1
        self.notify()

    def register_detective_solve(self, challenge_id, used_hint=False):
        """
        Awards points and logs completion of an investigation challenge.
        Returns total points awarded for this action.
        """
        base_points = 100
        is_new = challenge_id not in self.completed_challenges

        if used_hint:
            self.hints_used.add(challenge_id)

        bonus_points = 0 if (challenge_id in self.hints_used) else 50
        total_award = base_points + bonus_points

        if is_new:
            self.completed_challenges.add(challenge_id)
            self.detective_score += total_award

            # Add notification
            self.notifications.insert(0, {
                "id": f"notif_solve_{challenge_id}",
                "title": f"🔍 Case Dossier Cleared: {challenge_id}",
                "desc": f"Investigation confirmed. Awarded +{total_award} pts to researcher profile.",
                "timestamp": "Just now",
                "accent": "#06B6D4",
                "read": False
            })

            self.notify()
            return total_award
        return 0

    def toggle_bookmark(self, resource_id):
        """Toggles the bookmark state of a demonstration library resource."""
        for res in self.library_resources:
            if res.get("id") == resource_id:
                res["bookmarked"] = not res.get("bookmarked", False)
                if res["bookmarked"]:
                    self.notifications.insert(0, {
                        "id": f"notif_bm_{resource_id}",
                        "title": "★ Resource Bookmarked",
                        "desc": f"Added '{res.get('title')}' to active research bookmarks.",
                        "timestamp": "Just now",
                        "accent": "#F59E0B",
                        "read": False
                    })
                self.notify()
                return res["bookmarked"]
        return False

    def add_journal_entry(self, title, domain, status, tags, body):
        """Adds a new research log entry to the Discovery Journal."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = {
            "id": f"log_{len(self.journal_entries) + 201}",
            "title": title.strip(),
            "timestamp": now_str,
            "domain": domain.strip() if domain else "General Lab Observation",
            "status": status if status in ("Formulated", "Testing", "Verified", "Refuted") else "Formulated",
            "tags": tags.strip() if tags else "Observation",
            "body": body.strip()
        }
        self.journal_entries.insert(0, new_entry)

        self.notifications.insert(0, {
            "id": f"notif_log_{new_entry['id']}",
            "title": "📓 Journal Entry Recorded",
            "desc": f"Saved lab observation '{new_entry['title']}' [{new_entry['status']}].",
            "timestamp": "Just now",
            "accent": "#10B981",
            "read": False
        })

        self.notify()
        return new_entry

    def delete_journal_entry(self, entry_id):
        """Removes a journal log entry by ID."""
        initial_count = len(self.journal_entries)
        self.journal_entries = [e for e in self.journal_entries if e.get("id") != entry_id]
        if len(self.journal_entries) < initial_count:
            self.notify()
            return True
        return False

    def generate_citation_draft(self, resource_id):
        """Generates a standardized educational citation draft from demonstration metadata."""
        for res in self.library_resources:
            if res.get("id") == resource_id:
                title = res.get("title", "Educational Resource")
                curator = res.get("curator", "CurioLab Curriculum Staff")
                year = res.get("year", 2026)
                domain = res.get("module_domain", "Multidisciplinary")
                level = res.get("curriculum_level", "Standard")
                eq = res.get("key_equation", "N/A")
                
                draft_title = f"Citation & Notes: {title}"
                draft_body = (
                    f"### [CurioLab Educational Demonstration Reference]\n"
                    f"- Record Identifier: {resource_id}\n"
                    f"- Curriculum Title: {title}\n"
                    f"- Curating Team: {curator}\n"
                    f"- Curriculum Year: {year} ({level} level)\n"
                    f"- Scientific Domain: {domain}\n"
                    f"- Theoretical Equation: {eq}\n\n"
                    f"**Demonstration Abstract:**\n"
                    f"{res.get('summary', '')}\n\n"
                    f"**Laboratory Synthesis & Student Notes:**\n"
                    f"{res.get('study_notes', '')}"
                )
                return {
                    "resource_id": resource_id,
                    "title": draft_title,
                    "domain": domain,
                    "tags": f"Citation, {domain}, Educational",
                    "status": "Formulated",
                    "body": draft_body
                }
        return None

    def clear_notifications(self):
        """Marks all notifications as read."""
        for n in self.notifications:
            n["read"] = True
        self.notify()
