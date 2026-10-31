"""
CurioLab — Sample Data Module
==============================
Contains structured educational demonstration records for CurioLab.

CONTENT INTEGRITY NOTICE:
All records defined herein are strictly educational demonstration records
designed for local simulation and learning. They do NOT represent or fabricate
real-world peer-reviewed publications, real living authors, DOI identifiers,
or academic citation metrics.
"""

# =============================================================================
# EDUCATIONAL DEMONSTRATION LIBRARY RESOURCES
# =============================================================================
DEMO_LIBRARY_RESOURCES = [
    {
        "id": "demo_res_topological",
        "title": "Educational Guide: Topological Phases & Majorana Zero Modes",
        "curator": "CurioLab Physics Curriculum Team",
        "module_domain": "Condensed Matter Physics",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Advanced Theoretical",
        "summary": "An interactive tutorial explaining symmetry-protected topological order in one-dimensional superconducting wires and how non-abelian boundary states emerge.",
        "key_equation": "H = -μ ∑ c_i^† c_i - t ∑ (c_i^† c_{i+1} + h.c.) + Δ ∑ (c_i c_{i+1} + h.c.)",
        "study_notes": "Demonstrates topological protection against local thermal fluctuations in simulated quantum memory baselines.",
        "bookmarked": False,
        "demonstration_content": (
            "This curriculum module introduces topological band theory. In a 1D p-wave "
            "superconducting chain (Kitaev model), boundary zero-energy states appear when the chemical "
            "potential satisfies |μ| < 2t. The resulting parity states provide an educational model "
            "for understanding decoherence resistance in quantum information science."
        )
    },
    {
        "id": "demo_res_entropy",
        "title": "Educational Guide: Information Entropy & Landauer's Bound",
        "curator": "CurioLab Information Theory Curriculum Team",
        "module_domain": "Information Theory",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "summary": "An educational breakdown of Claude Shannon's channel capacity and Rolf Landauer's thermodynamic limit of logical bit erasure.",
        "key_equation": "C = B log₂(1 + S/N),   ΔQ ≥ k_B T ln(2)",
        "study_notes": "Connects logical computational states with thermodynamic energy dissipation limits.",
        "bookmarked": True,
        "demonstration_content": (
            "Logical operations that discard information (such as erasing a register) must increase "
            "the thermodynamic entropy of the environment by at least k_B ln(2) per erased bit. "
            "This fundamental principle illustrates that computation is inherently governed by physical laws."
        )
    },
    {
        "id": "demo_res_neural",
        "title": "Educational Guide: Synaptic Weights & Non-Linear Activation",
        "curator": "CurioLab Computational Neuroscience Team",
        "module_domain": "Cognitive Neuroscience & AI",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Introductory",
        "summary": "A conceptual breakdown of single-unit artificial neuron dynamics, weighted linear summation, and smooth sigmoid thresholding.",
        "key_equation": "z = w₁x₁ + w₂x₂ + b,   σ(z) = 1 / (1 + e^{-z})",
        "study_notes": "Theoretical companion to CurioLab's Single Artificial Neuron Playground.",
        "bookmarked": False,
        "demonstration_content": (
            "Biological neurons integrate electrical potentials from multiple dendrites at the cell soma. "
            "Artificial neural networks simplify this process into a dot product of inputs and synaptic weights, "
            "followed by a non-linear activation function that decides whether the artificial neuron fires."
        )
    },
    {
        "id": "demo_res_automata",
        "title": "Educational Guide: Cellular Automata & Emergent Complexity",
        "curator": "CurioLab Complex Systems Team",
        "module_domain": "Complexity Science",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "summary": "An exploration of how simple deterministic grid-based transition rules produce unpredictable, self-organizing macroscopic structures.",
        "key_equation": "s_{t+1}(x,y) = f(s_t(x±1, y±1))",
        "study_notes": "Demonstrates decentralized morphogenesis and pattern regeneration.",
        "bookmarked": False,
        "demonstration_content": (
            "Cellular automata illustrate that complex global behavior does not require centralized control. "
            "By computing uniform local updates across neighboring grid cells, systems like Conway's Game of Life "
            "and Wolfram's Rule 30 produce persistent gliders, periodic oscillators, and pseudo-random complexity."
        )
    },
    {
        "id": "demo_res_telemetry",
        "title": "Educational Guide: Sensor Telemetry & Statistical Outlier Audits",
        "curator": "CurioLab Empirical Methods Team",
        "module_domain": "Empirical Data Analysis",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Introductory",
        "summary": "An empirical audit manual on detecting sensor desynchronization, temperature violations, and decimal entry typos in telemetry streams.",
        "key_equation": "z_{score} = (x - μ) / σ,   IQR = Q₃ - Q₁",
        "study_notes": "Theoretical companion to CurioLab Research Detective Dossier #02 (The Data Detective).",
        "bookmarked": False,
        "demonstration_content": (
            "Empirical investigation requires checking data against physical boundaries and statistical norms. "
            "A cryogenic dilution refrigerator reporting 293.15 K indicates ambient room temperature contact failure, "
            "while subatomic velocity measurements exceeding 3.00 × 10⁸ m/s indicate optical timing desynchronization."
        )
    },
    {
        "id": "demo_res_cryptography",
        "title": "Educational Guide: Symmetric Shifts & Post-Quantum Lattices",
        "curator": "CurioLab Cryptography Curriculum Team",
        "module_domain": "Cryptographic Mathematics",
        "record_type": "Educational Demonstration Monograph",
        "curriculum_level": "Advanced",
        "summary": "A historical progression from Caesar substitution ciphers to modern lattice-based trapdoors resistant to quantum period-finding algorithms.",
        "key_equation": "E_k(m) = (m + k) mod 26,   b = As + e (mod q)",
        "study_notes": "Theoretical companion to CurioLab's Caesar Cipher Lab and Detective Dossier #01.",
        "bookmarked": False,
        "demonstration_content": (
            "Classical substitution ciphers are vulnerable to frequency analysis because letter statistics leak into "
            "ciphertext. Modern cryptography relies on hard geometric lattice problems such as Learning With Errors (LWE), "
            "which currently have no known polynomial-time quantum solution."
        )
    }
]


# =============================================================================
# EDUCATIONAL DEMONSTRATION RESEARCH GALAXY KNOWLEDGE GRAPH
# =============================================================================
DEMO_GALAXY_GRAPH = {
    "nodes": [
        {
            "id": "node_quantum",
            "label": "Quantum Mechanics",
            "x": 160,
            "y": 140,
            "domain": "Physics",
            "accent": "#06B6D4",
            "summary": "Wavefunction superposition, quantum states, and non-local correlations.",
            "resource_ref": "demo_res_topological"
        },
        {
            "id": "node_crypto",
            "label": "Cryptography",
            "x": 420,
            "y": 90,
            "domain": "Computer Science",
            "accent": "#8B5CF6",
            "summary": "Ciphers, mathematical entropy, trapdoor functions, and post-quantum lattices.",
            "resource_ref": "demo_res_cryptography"
        },
        {
            "id": "node_thermo",
            "label": "Thermodynamics",
            "x": 140,
            "y": 380,
            "domain": "Physics",
            "accent": "#F59E0B",
            "summary": "Energy dissipation, entropy, heat flow, and statistical mechanics.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "node_info",
            "label": "Information Theory",
            "x": 380,
            "y": 280,
            "domain": "Mathematics",
            "accent": "#14B8A6",
            "summary": "Channel capacity, bit compression, Shannon entropy, and error-correcting codes.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "node_neuro",
            "label": "Cognitive Neuroscience",
            "x": 670,
            "y": 140,
            "domain": "Biology",
            "accent": "#A78BFA",
            "summary": "Action potentials, dendritic summation, and synaptic plasticity dynamics.",
            "resource_ref": "demo_res_neural"
        },
        {
            "id": "node_ai",
            "label": "Machine Intelligence",
            "x": 680,
            "y": 350,
            "domain": "Computer Science",
            "accent": "#3B82F6",
            "summary": "Perceptrons, non-linear activation functions, optimization, and attention.",
            "resource_ref": "demo_res_neural"
        },
        {
            "id": "node_automata",
            "label": "Cellular Automata",
            "x": 450,
            "y": 450,
            "domain": "Complexity Science",
            "accent": "#10B981",
            "summary": "Decentralized grid states, self-organization, and emergent complexity.",
            "resource_ref": "demo_res_automata"
        }
    ],
    "bridges": [
        {
            "id": "bridge_thermo_info",
            "source": "node_thermo",
            "target": "node_info",
            "title": "Landauer's Principle",
            "summary": "Erasing one bit of logical information dissipates at least k_B T ln(2) of heat into the environment.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "bridge_quantum_crypto",
            "source": "node_quantum",
            "target": "node_crypto",
            "title": "Quantum Period-Finding & Lattice Resistance",
            "summary": "Quantum Fourier transforms break discrete logarithm ciphers, necessitating lattice-based trapdoors.",
            "resource_ref": "demo_res_cryptography"
        },
        {
            "id": "bridge_neuro_ai",
            "source": "node_neuro",
            "target": "node_ai",
            "title": "Dendritic Computation & Artificial Neurons",
            "summary": "McCulloch-Pitts artificial neurons model biological dendritic summation and synaptic thresholding.",
            "resource_ref": "demo_res_neural"
        },
        {
            "id": "bridge_info_crypto",
            "source": "node_info",
            "target": "node_crypto",
            "title": "Shannon's Perfect Secrecy",
            "summary": "Mathematical certainty that ciphertext discloses zero mutual information regarding the original plaintext.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "bridge_ai_automata",
            "source": "node_ai",
            "target": "node_automata",
            "title": "Neural Morphogenesis & Cellular Updates",
            "summary": "Optimizing local neighbor update kernels to achieve robust self-repairing patterns.",
            "resource_ref": "demo_res_automata"
        },
        {
            "id": "bridge_thermo_quantum",
            "source": "node_thermo",
            "target": "node_quantum",
            "title": "Sub-Kelvin Thermal Noise Dissipation",
            "summary": "Dilution cryostats suppress thermal phonon noise so quantum wavefunctions remain coherent.",
            "resource_ref": "demo_res_topological"
        }
    ]
}


# =============================================================================
# EDUCATIONAL DEMONSTRATION DISCOVERY JOURNAL RECORDS
# =============================================================================
DEMO_JOURNAL_ENTRIES = [
    {
        "id": "log_204",
        "title": "Sub-Kelvin Resonator Thermal Baseline Verification",
        "timestamp": "2026-10-28 14:30",
        "domain": "Cryogenic Physics",
        "status": "Testing",
        "tags": "Cryostats, Resonators, Johnson-Noise",
        "body": (
            "Recorded 14.8 mK cold plate baseline inside dilution cryostat. "
            "Thermal voltage noise measurement conforms to Nyquist formula S_v = 4 k_B T R. "
            "Verifying high-frequency RF line shielding to eliminate stray ambient photon leakage."
        )
    },
    {
        "id": "log_203",
        "title": "Statistical Randomness Uniformity in Atmospheric Entropy",
        "timestamp": "2026-10-25 09:15",
        "domain": "Information Theory",
        "status": "Verified",
        "tags": "PRNG, Entropy, Statistical-Tests",
        "body": (
            "Evaluated 10,000 generated 64-bit entropy sample words. "
            "Frequency distribution of zero and one bits shows zero statistical skew (|p - 0.5| < 0.001). "
            "Empirical results verify pseudo-quantum fluctuation simulator stability for cryptographic seeds."
        )
    },
    {
        "id": "log_202",
        "title": "Single-Neuron Non-Linear Separation Limits",
        "timestamp": "2026-10-20 16:45",
        "domain": "Computational Neuroscience",
        "status": "Refuted",
        "tags": "Perceptrons, XOR, Decision-Boundaries",
        "body": (
            "Tested single artificial neuron configuration on non-linear XOR input patterns (0,0->0; 0,1->1; 1,0->1; 1,1->0). "
            "Confirmed Minsky-Papert theorem: a single linear hyperplane cannot partition non-linearly separable coordinates. "
            "Multi-layer representations or kernel projection required."
        )
    },
    {
        "id": "log_201",
        "title": "Grid Cellular Soliton Symmetry Investigation",
        "timestamp": "2026-10-14 11:20",
        "domain": "Complexity Science",
        "status": "Formulated",
        "tags": "Cellular-Automata, Solitons, Morphogenesis",
        "body": (
            "Hypothesis: Asymmetric boundary conditions in 2D cellular automata with Moore neighborhoods "
            "can sustain stable directional solitons rather than static cyclic oscillators. "
            "Formulating rule parameters for upcoming simulator trial."
        )
    }
]


# =============================================================================
# EDUCATIONAL DEMONSTRATION NOTIFICATIONS
# =============================================================================
DEMO_NOTIFICATIONS = [
    {
        "id": "notif_1",
        "title": "⚡ Quantum Simulation Evaluated",
        "desc": "Wave packet dispersion simulation converged at 99.8% precision.",
        "timestamp": "10m ago",
        "accent": "#06B6D4",
        "read": False
    },
    {
        "id": "notif_2",
        "title": "🔍 Detective Dossier Cleared",
        "desc": "Investigation completed for empirical sensor telemetry case.",
        "timestamp": "1h ago",
        "accent": "#8B5CF6",
        "read": False
    },
    {
        "id": "notif_3",
        "title": "📚 Educational Monograph Added",
        "desc": "'Educational Guide: Topological Phases & Majorana Zero Modes' indexed.",
        "timestamp": "3h ago",
        "accent": "#14B8A6",
        "read": False
    },
    {
        "id": "notif_4",
        "title": "💡 Journal Hypothesis Verified",
        "desc": "'Statistical Randomness Uniformity in Atmospheric Entropy' confirmed.",
        "timestamp": "Yesterday",
        "accent": "#10B981",
        "read": False
    }
]
