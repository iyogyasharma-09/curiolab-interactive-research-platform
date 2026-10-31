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
        "curator": "CurioLab Quantum Physics Curriculum Staff",
        "module_domain": "Quantum Physics",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Advanced",
        "year": 2026,
        "tags": ["Quantum", "Topology", "Majorana", "Superconductivity"],
        "summary": "An interactive tutorial explaining symmetry-protected topological order in one-dimensional superconducting wires and how non-abelian boundary states emerge.",
        "key_equation": "H = -μ ∑ c_i^† c_i - t ∑ (c_i^† c_{i+1} + h.c.) + Δ ∑ (c_i c_{i+1} + h.c.)",
        "key_concepts": ["Chern Invariants", "Majorana Zero Modes", "Parity Qubits", "Topological Protection"],
        "related_topics": ["Quantum Computing", "Cryogenic Physics", "Condensed Matter"],
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
        "curator": "CurioLab Information Theory Curriculum Staff",
        "module_domain": "Information Theory",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "year": 2025,
        "tags": ["Information Theory", "Entropy", "Thermodynamics", "Bit-Erasure"],
        "summary": "An educational breakdown of Claude Shannon's channel capacity and Rolf Landauer's thermodynamic limit of logical bit erasure.",
        "key_equation": "C = B log₂(1 + S/N),   ΔQ ≥ k_B T ln(2)",
        "key_concepts": ["Shannon Channel Capacity", "Landauer Bound", "Thermodynamic Erasure", "Entropy Scaling"],
        "related_topics": ["Statistical Physics", "Cryptographic Entropy", "Energy Dissipation"],
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
        "title": "Educational Guide: Synaptic Plasticity & Spiking Dynamics",
        "curator": "CurioLab Neuroscience Curriculum Staff",
        "module_domain": "Neuroscience",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "year": 2025,
        "tags": ["Neuroscience", "STDP", "Synaptic Plasticity", "Spikes"],
        "summary": "Exploration of biological spike-timing-dependent plasticity (STDP) and how millisecond timing synchronizes recurrent neuronal circuits.",
        "key_equation": "Δw = A_+ e^{-Δt / τ_+} (for Δt > 0),   -A_- e^{Δt / τ_-} (for Δt < 0)",
        "key_concepts": ["Spike-Timing-Dependent Plasticity", "Dendritic Summation", "Homeostatic Plasticity", "Temporal Coincidence"],
        "related_topics": ["Artificial Intelligence", "Cognitive Modeling", "Bio-Electronics"],
        "study_notes": "Theoretical background for synaptic weight calibration in biological neural networks.",
        "bookmarked": False,
        "demonstration_content": (
            "Biological synapses adapt connection strength dynamically based on the relative timing of "
            "presynaptic and postsynaptic action potentials. When a presynaptic spike fires immediately prior "
            "to a postsynaptic spike, long-term potentiation reinforces the link."
        )
    },
    {
        "id": "demo_res_perceptron",
        "title": "Educational Guide: Perceptron Limits & Gradient Optimization",
        "curator": "CurioLab Machine Intelligence Curriculum Staff",
        "module_domain": "Artificial Intelligence",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Introductory",
        "year": 2026,
        "tags": ["AI", "Perceptrons", "Sigmoid", "Backpropagation"],
        "summary": "An intuitive tutorial on single-unit artificial neuron dynamics, linear separability constraints, and continuous sigmoid activation.",
        "key_equation": "z = w₁x₁ + w₂x₂ + b,   σ(z) = 1 / (1 + e^{-z})",
        "key_concepts": ["Linear Hyperplanes", "Sigmoid Activation", "Gradient Descent", "Decision Boundaries"],
        "related_topics": ["Neuroscience", "Optimization", "Pattern Classification"],
        "study_notes": "Theoretical companion to CurioLab's Single Artificial Neuron Playground.",
        "bookmarked": False,
        "demonstration_content": (
            "A single artificial neuron computes a weighted sum followed by a non-linear squashing function. "
            "While capable of solving linear boolean operations (AND, OR), single hyperplanes cannot partition "
            "non-convex spaces (XOR), motivating deep multi-layer architectures."
        )
    },
    {
        "id": "demo_res_automata",
        "title": "Educational Guide: Cellular Automata & Emergent Complexity",
        "curator": "CurioLab Complex Systems Curriculum Staff",
        "module_domain": "Complexity Science",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "year": 2025,
        "tags": ["Complexity", "Cellular Automata", "Conway", "Self-Organization"],
        "summary": "An exploration of how simple deterministic grid-based transition rules produce unpredictable, self-organizing macroscopic structures.",
        "key_equation": "s_{t+1}(x,y) = f(s_t(x±1, y±1))",
        "key_concepts": ["Deterministic Local Rules", "Glider Solitons", "Morphogenesis", "Turing Universality"],
        "related_topics": ["Theoretical Computer Science", "Biological Patterning", "Nonlinear Dynamics"],
        "study_notes": "Demonstrates decentralized morphogenesis and pattern regeneration without central coordinators.",
        "bookmarked": False,
        "demonstration_content": (
            "Cellular automata illustrate that complex global behavior does not require centralized control. "
            "By computing uniform local updates across neighboring grid cells, systems like Conway's Game of Life "
            "and Wolfram's Rule 30 produce persistent gliders, periodic oscillators, and pseudo-random complexity."
        )
    },
    {
        "id": "demo_res_lattice_crypto",
        "title": "Educational Guide: Post-Quantum Lattice Trapdoors & Shor Resistance",
        "curator": "CurioLab Cybersecurity Curriculum Staff",
        "module_domain": "Cybersecurity",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Advanced",
        "year": 2026,
        "tags": ["Cybersecurity", "Lattices", "Post-Quantum", "LWE"],
        "summary": "An architectural guide to Learning With Errors (LWE) and high-dimensional lattice trapdoors designed to withstand quantum Fourier period-finding attacks.",
        "key_equation": "b = As + e (mod q),   ||e||_∞ ≤ B",
        "key_concepts": ["Learning With Errors", "Shortest Vector Problem", "Quantum Fourier Transform", "Trapdoor Lattices"],
        "related_topics": ["Quantum Physics", "Information Theory", "Discrete Mathematics"],
        "study_notes": "Essential curriculum resource on modern post-quantum cryptographic standards.",
        "bookmarked": False,
        "demonstration_content": (
            "While Shor's quantum algorithm factors large integers in polynomial time by finding periodicities, "
            "geometric lattice problems in high dimensions exhibit no known hidden subgroup structures, providing "
            "a robust basis for post-quantum public-key exchange."
        )
    },
    {
        "id": "demo_res_computer_vision",
        "title": "Educational Guide: Convolutional Feature Maps & Spatial Invariance",
        "curator": "CurioLab Visual Computing Curriculum Staff",
        "module_domain": "Computer Vision",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Intermediate",
        "year": 2026,
        "tags": ["Computer Vision", "Convolution", "Kernels", "Spatial Invariance"],
        "summary": "A practical breakdown of discrete spatial 2D convolutions, edge detection filters (Sobel), and hierarchical visual feature abstraction.",
        "key_equation": "(I * K)(x,y) = ∑_i ∑_j I(x-i, y-j) K(i,j)",
        "key_concepts": ["Kernel Convolution", "Translation Equivariance", "Receptive Fields", "Spatial Pooling"],
        "related_topics": ["Artificial Intelligence", "Signal Processing", "Neurobiology"],
        "study_notes": "Explains how parameterized filters extract edge orientation and visual texture maps.",
        "bookmarked": False,
        "demonstration_content": (
            "Visual processing relies on translation equivariance: an edge or contour is equally meaningful "
            "regardless of its spatial position in the sensor frame. Sliding discrete convolution kernels computes "
            "local gradient responses that form hierarchical representations in deep vision models."
        )
    },
    {
        "id": "demo_res_telemetry",
        "title": "Educational Guide: Sensor Telemetry & Statistical Outlier Audits",
        "curator": "CurioLab Empirical Methods Curriculum Staff",
        "module_domain": "Empirical Data Analysis",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Introductory",
        "year": 2025,
        "tags": ["Data Analysis", "Outliers", "Telemetry", "Standard Deviation"],
        "summary": "An empirical audit manual on detecting sensor desynchronization, temperature violations, and decimal entry typos in telemetry streams.",
        "key_equation": "z_{score} = (x - μ) / σ,   IQR = Q₃ - Q₁",
        "key_concepts": ["Z-Score Normalization", "Interquartile Range", "Instrument Noise", "Physical Boundary Checks"],
        "related_topics": ["Statistical Inference", "Instrument Engineering", "Quality Assurance"],
        "study_notes": "Theoretical companion to CurioLab Research Detective Dossier #02 (The Data Detective).",
        "bookmarked": False,
        "demonstration_content": (
            "Empirical investigation requires checking data against physical boundaries and statistical norms. "
            "A cryogenic dilution refrigerator reporting 293.15 K indicates ambient room temperature contact failure, "
            "while subatomic velocity measurements exceeding 3.00 × 10⁸ m/s indicate optical timing desynchronization."
        )
    },
    {
        "id": "demo_res_coherence",
        "title": "Educational Guide: Quantum Coherence & Cryogenic Thermal Shielding",
        "curator": "CurioLab Quantum Physics Curriculum Staff",
        "module_domain": "Quantum Physics",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Advanced",
        "year": 2026,
        "tags": ["Quantum", "Cryogenics", "Coherence", "Johnson-Nyquist"],
        "summary": "A laboratory study guide detailing how dilution cryostats cooled to 15 mK suppress thermal phonon scattering and Johnson-Nyquist voltage noise.",
        "key_equation": "S_v(f) = 4 k_B T R,   T_2^* = (1 / (2 T_1) + 1 / T_φ)^{-1}",
        "key_concepts": ["Thermal Nyquist Noise", "Phonon Attenuation", "Phase Decoherence (T2)", "Superconducting Resonators"],
        "related_topics": ["Cryogenic Engineering", "Quantum Computing", "Condensed Matter"],
        "study_notes": "Explains why dilution refrigeration is required for high-coherence resonator tests.",
        "bookmarked": False,
        "demonstration_content": (
            "Macroscopic quantum states are fragile against thermal fluctuations. Dilution refrigerators "
            "circulating helium-3/helium-4 mixtures achieve sub-20 mK baselines where thermal photon energy "
            "k_B T is negligible compared to quantum transition energies ℏω, preventing premature state collapse."
        )
    },
    {
        "id": "demo_res_classical_crypto",
        "title": "Educational Guide: Classical Substitution & Frequency Cryptanalysis",
        "curator": "CurioLab Cybersecurity Curriculum Staff",
        "module_domain": "Cybersecurity",
        "record_type": "CurioLab Educational Demonstration Monograph",
        "curriculum_level": "Introductory",
        "year": 2024,
        "tags": ["Cybersecurity", "Caesar Cipher", "Cryptanalysis", "Frequency Analysis"],
        "summary": "Historical analysis of monoalphabetic shift ciphers and how natural language unigram probability distributions permit trivial cryptanalytic recovery.",
        "key_equation": "E_k(m) = (m + k) mod 26,   D_k(c) = (c - k) mod 26",
        "key_concepts": ["Modular Shift Arithmetic", "Unigram Frequency Profiles", "Ciphertext Invariance", "ROT13 Transformation"],
        "related_topics": ["Information Theory", "Discrete Mathematics", "Data Security"],
        "study_notes": "Theoretical companion to CurioLab's Caesar Cipher Playground and Detective Room 1.",
        "bookmarked": False,
        "demonstration_content": (
            "In a monoalphabetic Caesar cipher, each plaintext character is shifted by a constant integer k. "
            "Because individual letter probabilities are unaltered by substitution, computing letter frequency "
            "histograms breaks arbitrary Caesar ciphers almost instantaneously."
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
