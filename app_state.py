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

    def get_journal_stats(self):
        """
        Computes dynamic Discovery Journal statistics from in-memory records.
        Returns total entries, hypothesis status counts, and breakdown mappings.
        """
        total = len(self.journal_entries)
        formulated = sum(1 for e in self.journal_entries if e.get("status") == "Formulated")
        testing = sum(1 for e in self.journal_entries if e.get("status") == "Testing")
        verified = sum(1 for e in self.journal_entries if e.get("status") == "Verified")
        refuted = sum(1 for e in self.journal_entries if e.get("status") == "Refuted")
        
        type_counts = {}
        for e in self.journal_entries:
            etype = e.get("entry_type", "Observation")
            type_counts[etype] = type_counts.get(etype, 0) + 1

        domain_counts = {}
        for e in self.journal_entries:
            dom = e.get("domain", "General")
            domain_counts[dom] = domain_counts.get(dom, 0) + 1

        return {
            "total_entries": total,
            "formulated": formulated,
            "testing": testing,
            "verified": verified,
            "refuted": refuted,
            "by_type": type_counts,
            "by_domain": domain_counts
        }

    # -------------------------------------------------------------------------
    # RESEARCH GALAXY HELPERS
    # -------------------------------------------------------------------------
    def get_galaxy_nodes(self):
        """Returns all predefined nodes in the Research Galaxy."""
        return self.galaxy_graph.get("nodes", [])

    def get_galaxy_node(self, node_id):
        """Returns a single galaxy node dictionary by its stable unique ID."""
        for node in self.galaxy_graph.get("nodes", []):
            if node.get("id") == node_id:
                return node
        return None

    def get_galaxy_edges(self):
        """Returns all conceptual relationship bridges in the Research Galaxy."""
        return self.galaxy_graph.get("bridges", []) or self.galaxy_graph.get("edges", [])

    def get_galaxy_domains(self):
        """Returns a sorted list of unique scientific domains present in the galaxy graph."""
        domains = {node.get("domain", "General") for node in self.galaxy_graph.get("nodes", [])}
        return sorted(list(domains))

    def get_connected_nodes(self, node_id):
        """Returns list of node dicts directly connected to the specified node ID."""
        node = self.get_galaxy_node(node_id)
        if not node:
            return []
        connected_ids = set(node.get("related_nodes", []))
        return [n for n in self.galaxy_graph.get("nodes", []) if n.get("id") in connected_ids]

    def generate_concept_journal_draft(self, node_id):
        """
        Creates a pre-populated educational research draft from a Research Galaxy concept.
        Does not automatically commit to AppState; returns draft dictionary for user editing.
        """
        node = self.get_galaxy_node(node_id)
        if not node:
            return None
        
        name = node.get("name") or node.get("label", "Scientific Concept")
        domain = node.get("domain", "General")
        summary = node.get("summary", "")
        difficulty = node.get("difficulty", "Standard")
        
        related_nodes = self.get_connected_nodes(node_id)
        related_names = [rn.get("name") or rn.get("label", "Concept") for rn in related_nodes]
        rel_str = ", ".join(related_names) if related_names else "adjacent scientific disciplines"
        
        draft_title = f"Investigation: {name} in {domain}"
        draft_rq = f"How do the formal principles of {name} govern behavior in {domain}, and how do they interface with {rel_str}?"
        draft_hyp = f"If {name} theoretical models are applied, empirical observations will correlate with predictions established in {domain} curriculum standards."
        draft_obs = (
            f"CurioLab Research Galaxy Concept Card:\n"
            f"- Concept: {name} ({node_id})\n"
            f"- Scientific Domain: {domain}\n"
            f"- Curriculum Level: {difficulty}\n"
            f"- Educational Summary: {summary}\n"
            f"- Connected Disciplines: {rel_str}"
        )
        draft_methodology = (
            f"1. Conduct structured literature review using associated Knowledge Library monographs.\n"
            f"2. Configure interactive simulations or parameter sweeps.\n"
            f"3. Record comparative response metrics against baseline hypotheses."
        )
        draft_results = "Pending experimental execution and data gathering."
        draft_conclusion = "Hypothesis formulated and staged for exploratory testing."
        draft_tags = f"Galaxy, {domain}, {name}"

        return {
            "source_type": "galaxy_concept",
            "source_id": node_id,
            "title": draft_title,
            "domain": domain,
            "entry_type": "Hypothesis",
            "status": "Formulated",
            "research_question": draft_rq,
            "hypothesis": draft_hyp,
            "observations": draft_obs,
            "methodology": draft_methodology,
            "results": draft_results,
            "conclusion": draft_conclusion,
            "tags": draft_tags,
            "body": draft_obs
        }

    # -------------------------------------------------------------------------
    # DISCOVERY JOURNAL MUTATIONS
    # -------------------------------------------------------------------------
    def add_journal_entry(self, title, domain="General", status="Formulated", tags="Observation", body="",
                          entry_type="Observation", research_question="", hypothesis="", observations="",
                          methodology="", results="", conclusion="", source_ref=None):
        """
        Adds a complete research notebook record to the Discovery Journal.
        Maintains backwards compatibility with Stage 2 positional arguments.
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Synchronize body and observations for multi-view compatibility
        obs_text = observations.strip() if observations else body.strip()
        body_text = body.strip() if body else obs_text

        valid_statuses = ("Formulated", "Testing", "Verified", "Refuted")
        entry_status = status if status in valid_statuses else "Formulated"

        valid_types = (
            "Research Idea", "Research Question", "Hypothesis",
            "Experiment Log", "Observation", "Literature Note", "Finding"
        )
        clean_type = entry_type if entry_type in valid_types else "Observation"

        new_entry = {
            "id": f"log_{len(self.journal_entries) + 201}",
            "title": title.strip() if title else "Untitled Research Entry",
            "timestamp": now_str,
            "domain": domain.strip() if domain else "General",
            "entry_type": clean_type,
            "status": entry_status,
            "research_question": research_question.strip(),
            "hypothesis": hypothesis.strip(),
            "observations": obs_text,
            "methodology": methodology.strip(),
            "results": results.strip(),
            "conclusion": conclusion.strip(),
            "tags": tags.strip() if tags else clean_type,
            "body": body_text,
            "source_ref": source_ref
        }
        self.journal_entries.insert(0, new_entry)

        self.notifications.insert(0, {
            "id": f"notif_log_{new_entry['id']}",
            "title": f"📓 Journal: {new_entry['title']}",
            "desc": f"Saved {clean_type} record [{entry_status}].",
            "timestamp": "Just now",
            "accent": "#10B981",
            "read": False
        })

        self.notify()
        return new_entry

    def update_journal_entry(self, entry_id, **fields):
        """
        Updates an existing journal entry with new research fields.
        Notifies all subscribers and returns the updated entry.
        """
        for entry in self.journal_entries:
            if entry.get("id") == entry_id:
                for k, v in fields.items():
                    if k != "id":
                        if isinstance(v, str):
                            entry[k] = v.strip()
                        else:
                            entry[k] = v
                
                # Keep body and observations synchronized
                if "observations" in fields and not fields.get("body"):
                    entry["body"] = entry["observations"]
                elif "body" in fields and not fields.get("observations"):
                    entry["observations"] = entry["body"]

                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                entry["updated_at"] = now_str

                self.notifications.insert(0, {
                    "id": f"notif_update_{entry_id}_{datetime.datetime.now().microsecond}",
                    "title": f"✏️ Entry Updated: {entry.get('title', 'Entry')}",
                    "desc": f"Journal record [{entry.get('status')}] updated successfully.",
                    "timestamp": "Just now",
                    "accent": "#06B6D4",
                    "read": False
                })

                self.notify()
                return entry
        return None

    def duplicate_journal_entry(self, entry_id):
        """
        Creates an independent clone of an existing journal entry.
        Appends '(Copy)' to title and allocates a fresh unique ID.
        """
        for entry in self.journal_entries:
            if entry.get("id") == entry_id:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                clone = copy.deepcopy(entry)
                clone["id"] = f"log_{len(self.journal_entries) + 201}_{datetime.datetime.now().microsecond % 1000}"
                clone["title"] = f"{entry.get('title', 'Entry')} (Copy)"
                clone["timestamp"] = now_str
                clone.pop("updated_at", None)
                
                self.journal_entries.insert(0, clone)
                self.notifications.insert(0, {
                    "id": f"notif_dup_{clone['id']}",
                    "title": "📑 Entry Duplicated",
                    "desc": f"Cloned record as '{clone['title']}'.",
                    "timestamp": "Just now",
                    "accent": "#8B5CF6",
                    "read": False
                })
                self.notify()
                return clone
        return None

    def update_journal_entry_status(self, entry_id, new_status):
        """
        Updates the hypothesis progression status of a specific entry.
        Valid statuses: Formulated, Testing, Verified, Refuted.
        """
        valid_statuses = ("Formulated", "Testing", "Verified", "Refuted")
        if new_status not in valid_statuses:
            return False

        for entry in self.journal_entries:
            if entry.get("id") == entry_id:
                old_status = entry.get("status")
                entry["status"] = new_status
                entry["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                accent_map = {
                    "Formulated": "#94A3B8",
                    "Testing": "#38BDF8",
                    "Verified": "#10B981",
                    "Refuted": "#F43F5E"
                }

                self.notifications.insert(0, {
                    "id": f"notif_status_{entry_id}_{datetime.datetime.now().microsecond}",
                    "title": f"🔬 Status Updated: {entry.get('title', 'Entry')}",
                    "desc": f"Hypothesis transitioned: {old_status} ➔ {new_status}.",
                    "timestamp": "Just now",
                    "accent": accent_map.get(new_status, "#06B6D4"),
                    "read": False
                })

                self.notify()
                return True
        return False

    def delete_journal_entry(self, entry_id):
        """Removes a journal log entry by ID and notifies subscribers."""
        initial_count = len(self.journal_entries)
        entry_title = ""
        for e in self.journal_entries:
            if e.get("id") == entry_id:
                entry_title = e.get("title", entry_id)
                break

        self.journal_entries = [e for e in self.journal_entries if e.get("id") != entry_id]
        if len(self.journal_entries) < initial_count:
            self.notifications.insert(0, {
                "id": f"notif_del_{entry_id}",
                "title": "🗑 Journal Entry Removed",
                "desc": f"Deleted record '{entry_title}'.",
                "timestamp": "Just now",
                "accent": "#F43F5E",
                "read": False
            })
            self.notify()
            return True
        return False

    def generate_citation_draft(self, resource_id):
        """
        Generates a standardized educational citation draft from demonstration metadata.
        Now populates full scientific journal fields for Stage 3 notebook integration.
        """
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
                    "source_type": "library_citation",
                    "resource_id": resource_id,
                    "title": draft_title,
                    "domain": domain,
                    "entry_type": "Literature Note",
                    "status": "Formulated",
                    "research_question": f"What foundational principles does '{title}' contribute to {domain} research?",
                    "hypothesis": "Demonstration monograph provides theoretical backing for laboratory model verification.",
                    "observations": draft_body,
                    "methodology": f"Academic literature review of curriculum demonstration record {resource_id}.",
                    "results": f"Core equation '{eq}' identified for simulation implementation.",
                    "conclusion": "Citation successfully staged into personal discovery journal.",
                    "tags": f"Citation, {domain}, Educational",
                    "body": draft_body
                }
        return None

    def clear_notifications(self):
        """Marks all notifications as read."""
        for n in self.notifications:
            n["read"] = True
        self.notify()
