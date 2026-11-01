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

        # 5. Research Detective Progression & Scientific Investigation Stages
        self.investigation_stages = {
            "question": {
                "title": "1. Research Question",
                "status": "In Progress",
                "notes": "Investigate potential sensor drift and anomalous temperature excursions in the cryogenic resonator telemetry array.",
                "evidence": "Liquid helium baseline expected around 4.2 K."
            },
            "evidence": {
                "title": "2. Evidence Collection",
                "status": "In Progress",
                "notes": "Acquired 30 telemetry frames from Cryo Sensor Bank B during the liquid helium circulation test.",
                "evidence": "Dataset: Cryogenic Resonator Baseline (30 observations, 4 features)."
            },
            "exploration": {
                "title": "3. Dataset Exploration",
                "status": "Not Started",
                "notes": "Audit temperature readings using IQR fences and Z-score thresholding to identify corrupt telemetry frames.",
                "evidence": "Pending Data Detective inspection."
            },
            "analysis": {
                "title": "4. Analysis",
                "status": "Not Started",
                "notes": "Evaluate mean vs median skewness and check whether high accuracy masks false negatives.",
                "evidence": "Pending Statistical Trap investigation."
            },
            "observations": {
                "title": "5. Observations",
                "status": "Not Started",
                "notes": "Document any anomalous observations, residuals, and physical constraints.",
                "evidence": ""
            },
            "hypothesis": {
                "title": "6. Hypothesis",
                "status": "Not Started",
                "notes": "Evaluate whether extreme points reflect physical state transitions (e.g. cavity quench) or hardware measurement glitches.",
                "evidence": ""
            },
            "conclusion": {
                "title": "7. Conclusion",
                "status": "Not Started",
                "notes": "Synthesize conclusions regarding sensor array health and report limitations of the sample size.",
                "evidence": ""
            }
        }
        self.active_investigation = {
            "title": "Cryogenic Sensor Anomaly Investigation",
            "domain": "Data Science",
            "dataset_name": "Cryogenic Resonator Temperature Array",
            "dataset_description": "30 sequential telemetry frames measuring superconducting cavity temperatures (Kelvin) during liquid helium cooling.",
            "methodology": "Standardized IQR outlier fencing (k=1.5) and Z-score anomaly thresholding (|Z| >= 2.5).",
            "limitations": "Small sample size (N=30); single sensor channel; extreme thermal excursions may represent true localized quenching rather than electrical sensor faults.",
            "tags": "Research Detective, Data Science, Anomaly Audit, Outliers"
        }
        self.completed_challenges = set()
        self.hints_used = set()
        self.detective_score = 0

        # 6. Custom Experiments Architecture (Stage 7)
        self.custom_experiments = self._init_default_custom_experiments()
        self.active_custom_experiment_id = "exp_logistic_growth"

        # Built-in Experiment Execution Counters
        self.experiment_runs = {
            "caesar": 0,
            "neural": 0,
            "dataviz": 0
        }

        # 7. UI Configuration & Preferences
        self.current_theme = "Deep Obsidian"
        self.preferences = {
            "theme_name": "Deep Obsidian",
            "accent_color": "#06B6D4",
            "ui_scale": "Standard (100%)",
            "default_landing_page": "Discovery Hub",
            "preferred_resource_sort": "Title (A-Z)",
            "journal_default_type": "Hypothesis",
            "journal_default_status": "Formulated",
            "confirm_delete_journal": True,
            "galaxy_show_particles": True,
        }

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
        Derives from active state across both built-in and user-created experiments.
        """
        custom_exps = getattr(self, "custom_experiments", {})
        total_custom_runs = sum(len(e.get("runs", [])) for e in custom_exps.values())
        total_runs = sum(self.experiment_runs.values()) + total_custom_runs
        completed_stages = sum(1 for s in getattr(self, "investigation_stages", {}).values() if s.get("status") == "Completed")
        solved_count = completed_stages if hasattr(self, "investigation_stages") else len(self.completed_challenges)
        total_challenges = 7  # 7 Connected scientific investigation stages on the Investigation Board
        library_count = len(self.library_resources)
        bookmarked_count = sum(1 for r in self.library_resources if r.get("bookmarked"))
        journal_count = len(self.journal_entries)
        verified_hypotheses = sum(1 for e in self.journal_entries if e.get("status") == "Verified")
        unread_notifs = sum(1 for n in self.notifications if not n.get("read"))

        diligence_pct = 100.0
        curriculum_pct = (solved_count / float(total_challenges)) * 100.0
        self.detective_score = solved_count * 100

        return {
            "experiments_count": 3 + len(custom_exps),
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

    @property
    def bookmarks(self):
        """Returns list of IDs of currently bookmarked resources."""
        return [r["id"] for r in self.library_resources if r.get("bookmarked")]

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

    # -------------------------------------------------------------------------
    # SETTINGS, PREFERENCES & DATA CONTROLS
    # -------------------------------------------------------------------------
    def update_preferences(self, **kwargs):
        """Updates user preferences and notifies observers."""
        for k, v in kwargs.items():
            self.preferences[k] = v
        if "theme_name" in kwargs:
            self.current_theme = kwargs["theme_name"]
        self.notify()

    def reset_preferences(self):
        """Restores default application preferences."""
        self.preferences = {
            "theme_name": "Deep Obsidian",
            "accent_color": "#06B6D4",
            "ui_scale": "Standard (100%)",
            "default_landing_page": "Discovery Hub",
            "preferred_resource_sort": "Title (A-Z)",
            "journal_default_type": "Hypothesis",
            "journal_default_status": "Formulated",
            "confirm_delete_journal": True,
            "galaxy_show_particles": True,
        }
        self.current_theme = "Deep Obsidian"
        self.notify()

    def reset_bookmarks(self):
        """Resets all monograph bookmark states back to initial demonstration defaults."""
        initial_map = {r["id"]: r.get("bookmarked", False) for r in DEMO_LIBRARY_RESOURCES}
        for r in self.library_resources:
            r["bookmarked"] = initial_map.get(r["id"], False)
        self.notifications.insert(0, {
            "id": f"notif_reset_bm_{datetime.datetime.now().microsecond}",
            "title": "★ Bookmarks Reset",
            "desc": "All library monograph bookmarks restored to default curriculum baseline.",
            "timestamp": "Just now",
            "accent": "#F59E0B",
            "read": False,
            "target_page": "Knowledge Library"
        })
        self.notify()

    def reset_journal_entries(self):
        """Restores all Discovery Journal records back to initial demonstration dataset."""
        self.journal_entries = copy.deepcopy(DEMO_JOURNAL_ENTRIES)
        self.pending_journal_draft = None
        self.notifications.insert(0, {
            "id": f"notif_reset_journal_{datetime.datetime.now().microsecond}",
            "title": "📓 Journal Entries Reset",
            "desc": "Discovery Journal entries restored to baseline educational dataset.",
            "timestamp": "Just now",
            "accent": "#10B981",
            "read": False,
            "target_page": "Discovery Journal"
        })
        self.notify()

    # -------------------------------------------------------------------------
    # CUSTOM EXPERIMENT ARCHITECTURE (STAGE 7)
    # -------------------------------------------------------------------------
    def _init_default_custom_experiments(self):
        """Initializes default pre-configured custom experiments with baseline runs."""
        import math
        
        # 1. Logistic Population Growth & Saturation Dynamics
        pts_log1 = []
        for i in range(51):
            t = round(i * 0.5, 2)
            y = round(1000.0 / (1.0 + math.exp(-0.45 * (t - 10.0))), 4)
            pts_log1.append({"t": t, "y": y})
            
        pts_log2 = []
        for i in range(51):
            t = round(i * 0.5, 2)
            y = round(1000.0 / (1.0 + math.exp(-0.90 * (t - 10.0))), 4)
            pts_log2.append({"t": t, "y": y})

        # 2. Hooke's Law of Elasticity
        pts_hooke1 = []
        for i in range(21):
            x = round(i * 0.01, 3)
            y = round(45.0 * x + 0.15, 4)
            pts_hooke1.append({"x": x, "y": y})

        pts_hooke2 = []
        for i in range(21):
            x = round(i * 0.01, 3)
            y = round(90.0 * x + 0.15, 4)
            pts_hooke2.append({"x": x, "y": y})

        exps = {
            "exp_logistic_growth": {
                "id": "exp_logistic_growth",
                "title": "Logistic Population Growth & Saturation Dynamics",
                "domain": "Biology",
                "tags": "Population, Ecology, Non-linear, Saturation",
                "status": "Documented",
                "created_at": "2026-10-28 10:15",
                "updated_at": "2026-11-01 12:30",
                "research_question": "How does finite carrying capacity restrict theoretical exponential population growth in resource-limited ecological niches?",
                "objective": "Simulate the Verhulst logistic growth curve, determine the inflection point (maximum population growth rate), and evaluate sensitivity to the intrinsic growth coefficient.",
                "description": "Verhulst logistic model for resource-constrained population growth with asymptotic carrying capacity.",
                "theoretical_background": "In an unconstrained environment, population growth is exponential (Malthusian). In reality, competition for nutrients and space imposes a carrying capacity K, transforming the differential dynamics into dP/dt = r*P*(1 - P/K). Integrating yields the logistic sigmoid trajectory.",
                "expected_outcome": "Sigmoid S-shaped saturation trajectory with an inflection point at P = K/2 where growth rate peaks, followed by asymptotic convergence to K.",
                "equation": "y = K / (1 + exp(-r * (t - t0)))",
                "dependent_var": "y",
                "independent_vars": ["t"],
                "variable_descriptions": {
                    "t": "Elapsed time (days)",
                    "y": "Population size (organisms)",
                    "K": "Carrying capacity (organisms)",
                    "r": "Intrinsic growth rate (1/day)",
                    "t0": "Inflection time offset (days)"
                },
                "constants": {"e": 2.718281828},
                "units": {"t": "days", "y": "organisms", "K": "organisms", "r": "1/day", "t0": "days"},
                "assumptions": "Constant carrying capacity; instantaneous response to resource density without gestational lag; panmictic mating.",
                "boundary_conditions": "t >= 0; y(0) > 0; lim_{t -> infty} y(t) = K",
                "parameters": [
                    {"name": "Carrying Capacity", "symbol": "K", "type": "number", "default": 1000.0, "min": 100.0, "max": 5000.0, "step": 50.0, "unit": "organisms"},
                    {"name": "Growth Rate", "symbol": "r", "type": "slider", "default": 0.45, "min": 0.05, "max": 2.0, "step": 0.05, "unit": "1/day"},
                    {"name": "Inflection Center", "symbol": "t0", "type": "slider", "default": 10.0, "min": 2.0, "max": 20.0, "step": 0.5, "unit": "days"}
                ],
                "input_mode": "generated",
                "generated_config": {"var": "t", "start": 0.0, "stop": 25.0, "num_points": 51},
                "input_data": [{"t": round(i * 0.5, 2)} for i in range(51)],
                "execution_mode": "Series Evaluation",
                "num_iterations": 51,
                "num_trials": 1,
                "runs": [
                    {
                        "run_id": "run_log_001",
                        "run_number": 1,
                        "timestamp": "2026-10-28 10:20:00",
                        "parameters": {"K": 1000.0, "r": 0.45, "t0": 10.0},
                        "input_summary": "51 time points (0 to 25 days, dt=0.5)",
                        "outputs": pts_log1,
                        "summary_stats": {"count": 51, "min": 10.9869, "max": 998.8305, "mean": 479.54, "median": 500.0, "stdev": 361.22},
                        "status": "Success",
                        "error_message": "",
                        "run_notes": "Baseline parameterization (r=0.45). Inflection occurs at exactly t=10.0 where y=500."
                    },
                    {
                        "run_id": "run_log_002",
                        "run_number": 2,
                        "timestamp": "2026-10-28 10:25:30",
                        "parameters": {"K": 1000.0, "r": 0.90, "t0": 10.0},
                        "input_summary": "51 time points (0 to 25 days, dt=0.5)",
                        "outputs": pts_log2,
                        "summary_stats": {"count": 51, "min": 0.1234, "max": 999.9986, "mean": 490.15, "median": 500.0, "stdev": 447.88},
                        "status": "Success",
                        "error_message": "",
                        "run_notes": "Accelerated growth rate (r=0.90). Steep inflection gradient with earlier saturation convergence."
                    }
                ],
                "documentation": {
                    "research_question": "How does finite carrying capacity restrict theoretical exponential population growth in resource-limited ecological niches?",
                    "objective": "Simulate the Verhulst logistic growth curve, determine the inflection point (maximum population growth rate), and evaluate sensitivity to the intrinsic growth coefficient.",
                    "theoretical_background": "In unconstrained environments, Malthusian exponential growth prevails. Density-dependent environmental feedback imposes an asymptotic ceiling K.",
                    "hypothesis": "Increasing growth rate r steepens the inflection slope and shortens the transition window between exponential acceleration and saturation without changing the asymptotic ceiling K.",
                    "methodology": "Standardized analytical evaluation of the Verhulst equation across 51 discrete temporal observations (t=0 to 25 days, dt=0.5 days). Comparative sweeps performed between baseline r=0.45 and accelerated r=0.90.",
                    "parameters_conditions": "Baseline Run 1: K=1000, r=0.45, t0=10.0. Accelerated Run 2: K=1000, r=0.90, t0=10.0. Initial density y(0) ~ 11 organisms.",
                    "observations": "At t=0, y=10.98 organisms. S-curve inflection occurs precisely at t=10.0 days where y=500.0 organisms (K/2). Saturation (>99% of K) reached at t=21 days for r=0.45 and t=15 days for r=0.90.",
                    "results": "Inflection point verified at y = 500.0 organisms. Doubling r from 0.45 to 0.90 increased maximum instantaneous slope from 112.5 to 225.0 organisms/day, halving the saturation convergence time.",
                    "interpretation": "The empirical simulation confirms that carrying capacity K governs the steady-state equilibrium, whereas r acts exclusively on kinetic velocity through the phase portrait.",
                    "unexpected_findings": "Numerical discretization at dt=0.5 yielded less than 0.01% error compared to closed-form analytical integrals, confirming continuous-time validity.",
                    "limitations": "Model omits age-structured cohorts, spatial dispersion gradients, and stochastic meteorological shocks. In natural populations, time delays often induce underdamped oscillations around K.",
                    "conclusion": "The hypothesis is supported by evidence: growth coefficient r controls kinetic acceleration without altering asymptotic carrying capacity K.",
                    "future_investigation": "Incorporate second-order time delay tau into the differential formulation to model predatory-prey limit cycles and Hopf bifurcations.",
                    "hypothesis_status": "Supported by Evidence"
                }
            },
            "exp_hookes_law": {
                "id": "exp_hookes_law",
                "title": "Hooke's Law & Linear Mechanical Elasticity",
                "domain": "Physics",
                "tags": "Mechanical, Elasticity, Springs, Linear",
                "status": "Documented",
                "created_at": "2026-10-29 14:00",
                "updated_at": "2026-11-01 11:15",
                "research_question": "Does spring restoring force maintain strict linearity under moderate mechanical strain, and how does tare preload affect regression intercept?",
                "objective": "Measure force vs displacement response, extract spring constant k via linear regression, and verify elastic limit boundaries.",
                "description": "Linear elastic response of a helical mechanical spring under uniaxial tensile loading.",
                "theoretical_background": "Hooke's Law states that within the elastic limit of a material, deformation is directly proportional to applied force: F = k * x. Preload or sensor tare introduces an offset constant c.",
                "expected_outcome": "Linear trajectory with slope matching spring stiffness k and non-zero intercept representing tare mass.",
                "equation": "y = k * x + c",
                "dependent_var": "y",
                "independent_vars": ["x"],
                "variable_descriptions": {
                    "x": "Displacement elongation (m)",
                    "y": "Restoring force (N)",
                    "k": "Spring constant stiffness (N/m)",
                    "c": "Tare offset preload (N)"
                },
                "constants": {},
                "units": {"x": "m", "y": "N", "k": "N/m", "c": "N"},
                "assumptions": "Deformation remains strictly below yield strain; isothermal conditions; negligible spring mass.",
                "boundary_conditions": "0 <= x <= 0.25 m",
                "parameters": [
                    {"name": "Spring Constant", "symbol": "k", "type": "number", "default": 45.0, "min": 5.0, "max": 200.0, "step": 5.0, "unit": "N/m"},
                    {"name": "Preload Tare", "symbol": "c", "type": "slider", "default": 0.15, "min": 0.0, "max": 2.0, "step": 0.05, "unit": "N"}
                ],
                "input_mode": "generated",
                "generated_config": {"var": "x", "start": 0.0, "stop": 0.20, "num_points": 21},
                "input_data": [{"x": round(i * 0.01, 3)} for i in range(21)],
                "execution_mode": "Series Evaluation",
                "num_iterations": 21,
                "num_trials": 1,
                "runs": [
                    {
                        "run_id": "run_hooke_001",
                        "run_number": 1,
                        "timestamp": "2026-10-29 14:10:00",
                        "parameters": {"k": 45.0, "c": 0.15},
                        "input_summary": "21 displacement steps (0.0 to 0.20 m)",
                        "outputs": pts_hooke1,
                        "summary_stats": {"count": 21, "min": 0.15, "max": 9.15, "mean": 4.65, "median": 4.65, "stdev": 2.74},
                        "status": "Success",
                        "error_message": "",
                        "run_notes": "Standard steel helical spring (k=45 N/m). Linear R^2 = 1.0."
                    },
                    {
                        "run_id": "run_hooke_002",
                        "run_number": 2,
                        "timestamp": "2026-10-29 14:20:00",
                        "parameters": {"k": 90.0, "c": 0.15},
                        "input_summary": "21 displacement steps (0.0 to 0.20 m)",
                        "outputs": pts_hooke2,
                        "summary_stats": {"count": 21, "min": 0.15, "max": 18.15, "mean": 9.15, "median": 9.15, "stdev": 5.48},
                        "status": "Success",
                        "error_message": "",
                        "run_notes": "Stiffened alloy spring (k=90 N/m). Exact 2x force slope observed."
                    }
                ],
                "documentation": {
                    "research_question": "Does spring restoring force maintain strict linearity under moderate mechanical strain, and how does tare preload affect regression intercept?",
                    "objective": "Measure force vs displacement response, extract spring constant k via linear regression, and verify elastic limit boundaries.",
                    "theoretical_background": "Hooke's Law states that within elastic limit, F = k*x. Tare preload manifests as an additive intercept c.",
                    "hypothesis": "Restoring force scales with perfect linearity (R^2 > 0.999) across 0 to 0.20 m strain, and doubling k doubles the gradient without altering tare offset c.",
                    "methodology": "Stepwise elongation in increments of 0.01 m up to 0.20 m. Direct force transducer telemetry simulated across two spring constant calibrations (45 N/m and 90 N/m).",
                    "parameters_conditions": "Displacement range 0.0 to 0.20 m. Tare offset fixed at c = 0.15 N. Isothermal ambient laboratory environment.",
                    "observations": "At zero displacement x=0, force is 0.15 N (tare preload). At max elongation x=0.20 m, force reaches 9.15 N for k=45 N/m and 18.15 N for k=90 N/m.",
                    "results": "Slope matches k exactly: 45.0 N/m (Run 1) and 90.0 N/m (Run 2). Intercept is confirmed at 0.15 N.",
                    "interpretation": "Linear elasticity holds across the entire simulated window. The intercept successfully isolates tare calibration error.",
                    "unexpected_findings": "No hysteresis or plastic deformation observed under ideal theoretical assumption.",
                    "limitations": "Does not account for material fatigue, temperature-dependent shear modulus, or high-strain non-linear yield.",
                    "conclusion": "Hypothesis supported: linearity holds strictly within the tested domain, and tare preload is correctly partitioned as an invariant intercept.",
                    "future_investigation": "Model plastic deformation regime beyond elastic limit using non-linear strain-hardening equations.",
                    "hypothesis_status": "Supported by Evidence"
                }
            }
        }
        return exps

    def add_custom_experiment(self, exp_data):
        """Adds a newly created custom experiment to state and notifies subscribers."""
        import time, datetime
        exp_id = exp_data.get("id") or f"exp_custom_{int(time.time() * 1000)}"
        exp_data["id"] = exp_id
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        exp_data["created_at"] = exp_data.get("created_at") or now_str
        exp_data["updated_at"] = now_str
        if "runs" not in exp_data:
            exp_data["runs"] = []
        if "status" not in exp_data:
            exp_data["status"] = "Ready" if exp_data["runs"] else "Draft"

        self.custom_experiments[exp_id] = exp_data
        self.active_custom_experiment_id = exp_id

        self.notifications.insert(0, {
            "id": f"notif_exp_add_{exp_id}_{datetime.datetime.now().microsecond}",
            "title": f"🧪 New Experiment Created",
            "desc": f"Created custom experiment '{exp_data.get('title', exp_id)}'.",
            "timestamp": "Just now",
            "accent": "#A855F7",
            "read": False,
            "target_page": "Experiment Lab"
        })
        self.notify()
        return exp_id

    def update_custom_experiment(self, exp_id, exp_data):
        """Updates an existing custom experiment definition."""
        import datetime
        if exp_id in self.custom_experiments:
            exp_data["id"] = exp_id
            exp_data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.custom_experiments[exp_id].update(exp_data)
            self.notify()
            return True
        return False

    def duplicate_custom_experiment(self, exp_id):
        """Duplicates an existing custom experiment with cloned configurations."""
        import copy, time, datetime
        if exp_id in self.custom_experiments:
            orig = self.custom_experiments[exp_id]
            new_id = f"exp_custom_{int(time.time() * 1000)}"
            clone = copy.deepcopy(orig)
            clone["id"] = new_id
            clone["title"] = f"{orig.get('title', 'Experiment')} (Copy)"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            clone["created_at"] = now_str
            clone["updated_at"] = now_str
            self.custom_experiments[new_id] = clone
            self.active_custom_experiment_id = new_id

            self.notifications.insert(0, {
                "id": f"notif_exp_dup_{new_id}_{datetime.datetime.now().microsecond}",
                "title": "📑 Experiment Duplicated",
                "desc": f"Cloned experiment '{orig.get('title')}'.",
                "timestamp": "Just now",
                "accent": "#A855F7",
                "read": False,
                "target_page": "Experiment Lab"
            })
            self.notify()
            return new_id
        return None

    def delete_custom_experiment(self, exp_id):
        """Deletes a custom experiment by ID with observer notification."""
        if exp_id in self.custom_experiments:
            title = self.custom_experiments[exp_id].get("title", exp_id)
            del self.custom_experiments[exp_id]
            if self.active_custom_experiment_id == exp_id:
                self.active_custom_experiment_id = next(iter(self.custom_experiments.keys()), None)
            
            self.notifications.insert(0, {
                "id": f"notif_exp_del_{exp_id}_{datetime.datetime.now().microsecond}",
                "title": "🗑 Experiment Deleted",
                "desc": f"Removed custom experiment '{title}'.",
                "timestamp": "Just now",
                "accent": "#F43F5E",
                "read": False,
                "target_page": "Experiment Lab"
            })
            self.notify()
            return True
        return False

    def record_custom_experiment_run(self, exp_id, run_record):
        """Appends a newly executed run record to the experiment's history."""
        import datetime
        if exp_id in self.custom_experiments:
            exp = self.custom_experiments[exp_id]
            if "runs" not in exp:
                exp["runs"] = []
            exp["runs"].append(run_record)
            if exp.get("status") == "Draft":
                exp["status"] = "Executed"
            exp["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            self.notifications.insert(0, {
                "id": f"notif_exp_run_{exp_id}_{datetime.datetime.now().microsecond}",
                "title": "⚡ Experiment Executed",
                "desc": f"Run #{run_record.get('run_number', len(exp['runs']))} recorded for '{exp.get('title')}'.",
                "timestamp": "Just now",
                "accent": "#10B981",
                "read": False,
                "target_page": "Experiment Lab"
            })
            self.notify()
            return run_record.get("run_id")
        return None

    def delete_custom_experiment_run(self, exp_id, run_id):
        """Deletes a specific execution run from an experiment's history."""
        if exp_id in self.custom_experiments:
            exp = self.custom_experiments[exp_id]
            initial_len = len(exp.get("runs", []))
            exp["runs"] = [r for r in exp.get("runs", []) if r.get("run_id") != run_id]
            if len(exp["runs"]) < initial_len:
                self.notify()
                return True
        return False

    def update_experiment_documentation(self, exp_id, doc_data):
        """Updates the 13-field research documentation and hypothesis verification status."""
        import datetime
        if exp_id in self.custom_experiments:
            exp = self.custom_experiments[exp_id]
            exp["documentation"] = doc_data
            exp["status"] = "Documented"
            exp["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.notify()
            return True
        return False

    def get_custom_experiment(self, exp_id):
        """Retrieves a custom experiment dictionary by ID."""
        return self.custom_experiments.get(exp_id)

    def reset_experiment_runs(self):
        """Resets all Experiment Lab execution counters back to zero."""
        self.experiment_runs = {
            "caesar": 0,
            "neural": 0,
            "dataviz": 0
        }
        for exp in self.custom_experiments.values():
            exp["runs"] = []
            if exp.get("status") == "Executed":
                exp["status"] = "Ready"

        self.notifications.insert(0, {
            "id": f"notif_reset_exp_{datetime.datetime.now().microsecond}",
            "title": "⚗️ Experiment Telemetry Reset",
            "desc": "Execution counters for all laboratory simulations cleared to zero.",
            "timestamp": "Just now",
            "accent": "#06B6D4",
            "read": False,
            "target_page": "Experiment Lab"
        })
        self.notify()

    def reset_detective_progress(self):
        """Resets Research Detective investigation stages, active metadata, and notes."""
        self.completed_challenges.clear()
        self.hints_used.clear()
        self.detective_score = 0
        self.investigation_stages = {
            "question": {"title": "1. Research Question", "status": "Not Started", "notes": "", "evidence": ""},
            "evidence": {"title": "2. Evidence Collection", "status": "Not Started", "notes": "", "evidence": ""},
            "exploration": {"title": "3. Dataset Exploration", "status": "Not Started", "notes": "", "evidence": ""},
            "analysis": {"title": "4. Analysis", "status": "Not Started", "notes": "", "evidence": ""},
            "observations": {"title": "5. Observations", "status": "Not Started", "notes": "", "evidence": ""},
            "hypothesis": {"title": "6. Hypothesis", "status": "Not Started", "notes": "", "evidence": ""},
            "conclusion": {"title": "7. Conclusion", "status": "Not Started", "notes": "", "evidence": ""}
        }
        self.notifications.insert(0, {
            "id": f"notif_reset_det_{datetime.datetime.now().microsecond}",
            "title": "🔍 Detective Progress Reset",
            "desc": "Cleared investigation stages and active notes. Reset to initial workspace state.",
            "timestamp": "Just now",
            "accent": "#8B5CF6",
            "read": False,
            "target_page": "Research Detective"
        })
        self.notify()

    def reset_all_data(self):
        """Performs a complete application state reset to pristine demonstration defaults."""
        self.library_resources = copy.deepcopy(DEMO_LIBRARY_RESOURCES)
        self.galaxy_graph = copy.deepcopy(DEMO_GALAXY_GRAPH)
        self.journal_entries = copy.deepcopy(DEMO_JOURNAL_ENTRIES)
        self.notifications = copy.deepcopy(DEMO_NOTIFICATIONS)
        self.completed_challenges.clear()
        self.hints_used.clear()
        self.detective_score = 0
        self.experiment_runs = {"caesar": 0, "neural": 0, "dataviz": 0}
        self.custom_experiments = self._init_default_custom_experiments()
        self.active_custom_experiment_id = "exp_logistic_growth"
        self.pending_journal_draft = None
        self.reset_preferences()
        self.notify()

    # -------------------------------------------------------------------------
    # NOTIFICATION MANAGEMENT
    # -------------------------------------------------------------------------
    def mark_notification_read(self, notif_id):
        """Marks a specific notification as read."""
        for n in self.notifications:
            if n.get("id") == notif_id:
                n["read"] = True
                self.notify()
                return True
        return False

    def clear_notifications(self):
        """Marks all notifications as read."""
        for n in self.notifications:
            n["read"] = True
        self.notify()

    # -------------------------------------------------------------------------
    # GLOBAL MULTI-MODULE SEARCH ENGINE
    # -------------------------------------------------------------------------
    def search_all(self, query):
        """
        Executes a federated search across all laboratory modules:
        - Knowledge Library monographs
        - Research Galaxy concepts
        - Discovery Journal research logs
        - Experiment Lab simulations
        - Research Detective challenges
        Returns a structured list of match records.
        """
        q = (query or "").strip().lower()
        if not q:
            return []

        results = []

        # 1. Search Knowledge Library Monographs
        for res in self.library_resources:
            corpus = f"{res.get('title', '')} {res.get('module_domain', '')} {res.get('summary', '')} {res.get('key_equation', '')} {res.get('curator', '')} {res.get('study_notes', '')}".lower()
            if q in corpus:
                results.append({
                    "category": "Knowledge Library",
                    "badge": "MONOGRAPH",
                    "icon": "📚",
                    "id": res.get("id"),
                    "title": res.get("title"),
                    "subtitle": f"{res.get('module_domain')} • Level: {res.get('curriculum_level')} ({res.get('year')})",
                    "snippet": res.get("summary", "")[:130] + ("..." if len(res.get("summary", "")) > 130 else ""),
                    "accent": "#14B8A6",
                    "target_page": "Knowledge Library",
                    "target_id": res.get("id")
                })

        # 2. Search Research Galaxy Concepts
        for node in self.galaxy_graph.get("nodes", []):
            name = node.get("name") or node.get("label", "")
            corpus = f"{name} {node.get('domain', '')} {node.get('summary', '')} {node.get('difficulty', '')}".lower()
            if q in corpus:
                results.append({
                    "category": "Research Galaxy",
                    "badge": "CONCEPT",
                    "icon": "🌌",
                    "id": node.get("id"),
                    "title": name,
                    "subtitle": f"{node.get('domain')} • Level: {node.get('difficulty', 'Standard')}",
                    "snippet": node.get("summary", "")[:130] + ("..." if len(node.get("summary", "")) > 130 else ""),
                    "accent": "#8B5CF6",
                    "target_page": "Research Galaxy",
                    "target_id": node.get("id")
                })

        # 3. Search Discovery Journal Entries
        for entry in self.journal_entries:
            corpus = f"{entry.get('title', '')} {entry.get('domain', '')} {entry.get('entry_type', '')} {entry.get('research_question', '')} {entry.get('hypothesis', '')} {entry.get('observations', '')} {entry.get('results', '')} {entry.get('conclusion', '')} {entry.get('tags', '')}".lower()
            if q in corpus:
                results.append({
                    "category": "Discovery Journal",
                    "badge": entry.get("entry_type", "NOTE").upper(),
                    "icon": "📓",
                    "id": entry.get("id"),
                    "title": entry.get("title", "Untitled Entry"),
                    "subtitle": f"{entry.get('domain')} • [{entry.get('status', 'Formulated')}] {entry.get('timestamp')}",
                    "snippet": (entry.get("hypothesis") or entry.get("research_question") or entry.get("observations") or entry.get("body", ""))[:130],
                    "accent": "#10B981",
                    "target_page": "Discovery Journal",
                    "target_id": entry.get("id")
                })

        # 4. Search Experiment Lab Tools
        experiments = [
            ("caesar", "Caesar Substitution Cipher", "Cryptography", "Modular shift encryption, frequency cryptanalysis attack, and letter distribution bars.", "Experiment Lab"),
            ("neural", "Single-Neuron Activation Playground", "Artificial Intelligence", "Interactive 2D decision boundary, weight/bias tuning, and XOR non-linear separation limits.", "Experiment Lab"),
            ("dataviz", "Interactive Data Visualizer", "Data Science", "Synthetic wave packets, noise injection, and multi-variable chart plotting.", "Experiment Lab")
        ]
        for exp_id, exp_name, exp_dom, exp_desc, page in experiments:
            if q in f"{exp_name} {exp_dom} {exp_desc}".lower():
                results.append({
                    "category": "Experiment Lab",
                    "badge": "SIMULATION",
                    "icon": "⚗️",
                    "id": exp_id,
                    "title": exp_name,
                    "subtitle": f"{exp_dom} • Interactive Simulation Tool",
                    "snippet": exp_desc,
                    "accent": "#06B6D4",
                    "target_page": page,
                    "target_id": exp_id
                })

        # 4b. Search Custom Experiments
        for exp in (self.custom_experiments.values() if isinstance(self.custom_experiments, dict) else self.custom_experiments):
            exp_id = exp.get("id", "")
            title = exp.get("title", "")
            domain = exp.get("domain", "")
            desc = exp.get("description", "")
            eq = exp.get("equation", "")
            tags = " ".join(exp.get("tags", []))
            corpus = f"{title} {domain} {desc} {eq} {tags}".lower()
            if q in corpus:
                results.append({
                    "category": "Experiment Lab",
                    "badge": "CUSTOM EXP",
                    "icon": "🧪",
                    "id": exp_id,
                    "title": title,
                    "subtitle": f"{domain} • Equation: {eq}",
                    "snippet": desc[:130] + ("..." if len(desc) > 130 else ""),
                    "accent": "#10B981",
                    "target_page": "Experiment Lab",
                    "target_id": exp_id
                })

        # 5. Search Research Detective Modules
        cases = [
            ("detective_map", "Investigation Board: Detective Map", "Data Science", "Connected scientific workflow across research question, evidence, exploration, analysis, and conclusions.", "Research Detective"),
            ("data_detective", "Data Detective: Anomaly Investigation", "Data Science", "Import CSV datasets, validate records, detect IQR outliers and Z-score anomalies.", "Research Detective"),
            ("statistical_trap", "Statistical Trap: Deceptive Metrics", "Statistics", "Investigate class imbalance, accuracy paradox, mean vs median skew, and correlation vs causation.", "Research Detective"),
            ("pattern_mystery", "Pattern Mystery: Trend Discovery", "Data Science", "Scatter plots, regression trends, Pearson correlation, and unusual residual discovery.", "Research Detective")
        ]
        for case_id, case_name, case_dom, case_desc, page in cases:
            if q in f"{case_name} {case_dom} {case_desc}".lower():
                results.append({
                    "category": "Research Detective",
                    "badge": "CASE DOSSIER",
                    "icon": "🔍",
                    "id": case_id,
                    "title": case_name,
                    "subtitle": f"{case_dom} • Forensic Investigation",
                    "snippet": case_desc,
                    "accent": "#F59E0B",
                    "target_page": page,
                    "target_id": case_id
                })

        return results
