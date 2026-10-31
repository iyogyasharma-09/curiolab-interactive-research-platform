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
        # Quantum Physics
        {
            "id": "node_quantum",
            "label": "Quantum Mechanics & Superposition",
            "domain": "Quantum Physics",
            "accent": "#06B6D4",
            "difficulty": "Intermediate",
            "x": 190,
            "y": 140,
            "summary": "Wavefunction superposition, Schrödinger time-evolution, non-local entanglement, and measurement postulation.",
            "related_nodes": ["node_topological", "node_coherence", "node_thermo", "node_fourier"],
            "resource_refs": ["demo_res_topological", "demo_res_coherence"]
        },
        {
            "id": "node_topological",
            "label": "Topological Phases & Majorana Modes",
            "domain": "Quantum Physics",
            "accent": "#06B6D4",
            "difficulty": "Advanced",
            "x": 120,
            "y": 270,
            "summary": "Symmetry-protected topological order, Chern invariants, and non-abelian zero-energy boundary modes in 1D superconductor chains.",
            "related_nodes": ["node_quantum", "node_coherence", "node_lattice_crypto"],
            "resource_refs": ["demo_res_topological"]
        },
        {
            "id": "node_coherence",
            "label": "Cryogenic Coherence & Nyquist Limits",
            "domain": "Quantum Physics",
            "accent": "#06B6D4",
            "difficulty": "Advanced",
            "x": 260,
            "y": 280,
            "summary": "Sub-20 mK dilution thermal shielding, phase decoherence relaxation (T2), and Johnson-Nyquist voltage noise suppression.",
            "related_nodes": ["node_quantum", "node_topological", "node_thermo", "node_telemetry"],
            "resource_refs": ["demo_res_coherence"]
        },

        # Information Theory
        {
            "id": "node_info",
            "label": "Information Theory & Shannon Capacity",
            "domain": "Information Theory",
            "accent": "#14B8A6",
            "difficulty": "Intermediate",
            "x": 430,
            "y": 180,
            "summary": "Shannon channel capacity, source coding theorems, entropy limits, and information-theoretic secrecy bounds.",
            "related_nodes": ["node_thermo", "node_classical_crypto", "node_lattice_crypto", "node_fourier"],
            "resource_refs": ["demo_res_entropy"]
        },
        {
            "id": "node_thermo",
            "label": "Thermodynamics & Landauer Erasure",
            "domain": "Information Theory",
            "accent": "#14B8A6",
            "difficulty": "Intermediate",
            "x": 310,
            "y": 110,
            "summary": "Physical limits of computation: logical bit erasure dissipates at least k_B T ln(2) of thermodynamic energy.",
            "related_nodes": ["node_info", "node_quantum", "node_coherence", "node_automata"],
            "resource_refs": ["demo_res_entropy"]
        },

        # Artificial Intelligence
        {
            "id": "node_ai",
            "label": "Machine Intelligence & Deep Architectures",
            "domain": "Artificial Intelligence",
            "accent": "#3B82F6",
            "difficulty": "Introductory",
            "x": 750,
            "y": 170,
            "summary": "Universal function approximation, gradient optimization, backpropagation through layers, and latent representation spaces.",
            "related_nodes": ["node_perceptron", "node_activation", "node_cv", "node_neuro"],
            "resource_refs": ["demo_res_perceptron", "demo_res_computer_vision"]
        },
        {
            "id": "node_perceptron",
            "label": "Single Perceptron & Hyperplane Partitioning",
            "domain": "Artificial Intelligence",
            "accent": "#3B82F6",
            "difficulty": "Introductory",
            "x": 870,
            "y": 290,
            "summary": "Linear decision hyperplanes, weighted affine combinations, bias calibration, and Minsky-Papert XOR separability boundaries.",
            "related_nodes": ["node_ai", "node_activation", "node_synaptic"],
            "resource_refs": ["demo_res_perceptron"]
        },
        {
            "id": "node_activation",
            "label": "Activation Functions & Non-Linear Mapping",
            "domain": "Artificial Intelligence",
            "accent": "#3B82F6",
            "difficulty": "Intermediate",
            "x": 750,
            "y": 320,
            "summary": "Continuous squashing operators (Sigmoid, Tanh, ReLU) enabling multi-layer neural networks to partition non-convex regions.",
            "related_nodes": ["node_ai", "node_perceptron", "node_cv", "node_fourier"],
            "resource_refs": ["demo_res_perceptron"]
        },

        # Neuroscience
        {
            "id": "node_neuro",
            "label": "Cognitive Neuroscience & Dendritic Computing",
            "domain": "Neuroscience",
            "accent": "#A78BFA",
            "difficulty": "Intermediate",
            "x": 610,
            "y": 90,
            "summary": "Action potential cascades, membrane capacitance dynamics, and dendritic spatial integration in biological circuits.",
            "related_nodes": ["node_synaptic", "node_ai", "node_perceptron"],
            "resource_refs": ["demo_res_neural"]
        },
        {
            "id": "node_synaptic",
            "label": "Synaptic Plasticity & STDP Spiking Dynamics",
            "domain": "Neuroscience",
            "accent": "#A78BFA",
            "difficulty": "Intermediate",
            "x": 600,
            "y": 230,
            "summary": "Spike-Timing-Dependent Plasticity: millisecond pre/post action potential timing driving long-term potentiation and depression.",
            "related_nodes": ["node_neuro", "node_perceptron", "node_ai", "node_automata"],
            "resource_refs": ["demo_res_neural"]
        },

        # Computer Vision
        {
            "id": "node_cv",
            "label": "Computer Vision & Spatial Equivariance",
            "domain": "Computer Vision",
            "accent": "#22D3EE",
            "difficulty": "Intermediate",
            "x": 890,
            "y": 140,
            "summary": "Translation equivariance, receptive fields, hierarchical visual feature abstraction, and pooling across spatial dimensions.",
            "related_nodes": ["node_ai", "node_feature_maps", "node_fourier"],
            "resource_refs": ["demo_res_computer_vision"]
        },
        {
            "id": "node_feature_maps",
            "label": "Convolutional Feature Maps & Edge Kernels",
            "domain": "Computer Vision",
            "accent": "#22D3EE",
            "difficulty": "Intermediate",
            "x": 920,
            "y": 40,
            "summary": "Discrete 2D spatial convolution filters, Sobel gradient edge detectors, and hierarchical visual texture mapping.",
            "related_nodes": ["node_cv", "node_ai", "node_telemetry"],
            "resource_refs": ["demo_res_computer_vision"]
        },

        # Cybersecurity
        {
            "id": "node_classical_crypto",
            "label": "Classical Substitution & Frequency Analysis",
            "domain": "Cybersecurity",
            "accent": "#F59E0B",
            "difficulty": "Introductory",
            "x": 400,
            "y": 350,
            "summary": "Monoalphabetic shift ciphers, modular arithmetic transformations, and unigram frequency cryptanalysis vulnerability.",
            "related_nodes": ["node_info", "node_lattice_crypto", "node_telemetry"],
            "resource_refs": ["demo_res_classical_crypto"]
        },
        {
            "id": "node_lattice_crypto",
            "label": "Post-Quantum Lattices & LWE Trapdoors",
            "domain": "Cybersecurity",
            "accent": "#F59E0B",
            "difficulty": "Advanced",
            "x": 540,
            "y": 360,
            "summary": "Learning With Errors (LWE), high-dimensional Shortest Vector Problems, and cryptographic schemes immune to Shor's algorithm.",
            "related_nodes": ["node_classical_crypto", "node_info", "node_topological", "node_fourier"],
            "resource_refs": ["demo_res_lattice_crypto"]
        },

        # Complexity Science
        {
            "id": "node_automata",
            "label": "Cellular Automata & Emergent Complexity",
            "domain": "Complexity Science",
            "accent": "#10B981",
            "difficulty": "Intermediate",
            "x": 460,
            "y": 480,
            "summary": "Decentralized grid state transitions producing unpredictable gliders, periodic oscillators, and Turing-universal computation.",
            "related_nodes": ["node_self_org", "node_thermo", "node_synaptic", "node_ai"],
            "resource_refs": ["demo_res_automata"]
        },
        {
            "id": "node_self_org",
            "label": "Self-Organization & Soliton Patterns",
            "domain": "Complexity Science",
            "accent": "#10B981",
            "difficulty": "Advanced",
            "x": 310,
            "y": 480,
            "summary": "Decentralized morphogenesis, dynamic balance in non-equilibrium systems, and persistent localized solitons.",
            "related_nodes": ["node_automata", "node_thermo", "node_topological"],
            "resource_refs": ["demo_res_automata"]
        },

        # Mathematics & Empirical Analysis
        {
            "id": "node_telemetry",
            "label": "Sensor Telemetry & Outlier Audits",
            "domain": "Mathematics",
            "accent": "#8B5CF6",
            "difficulty": "Introductory",
            "x": 220,
            "y": 390,
            "summary": "Z-score normalization, interquartile dispersion, instrument drift auditing, and physical boundary plausibility checks.",
            "related_nodes": ["node_coherence", "node_classical_crypto", "node_feature_maps", "node_fourier"],
            "resource_refs": ["demo_res_telemetry"]
        },
        {
            "id": "node_fourier",
            "label": "Discrete Fourier & Harmonic Analysis",
            "domain": "Mathematics",
            "accent": "#8B5CF6",
            "difficulty": "Intermediate",
            "x": 680,
            "y": 440,
            "summary": "Frequency spectral decomposition, orthogonal basis expansions, and hidden periodicities recovery in signal spaces.",
            "related_nodes": ["node_quantum", "node_info", "node_lattice_crypto", "node_cv", "node_telemetry"],
            "resource_refs": ["demo_res_lattice_crypto", "demo_res_computer_vision"]
        }
    ],
    "bridges": [
        {
            "id": "bridge_thermo_info",
            "source": "node_thermo",
            "target": "node_info",
            "title": "Landauer's Principle",
            "summary": "Erasing one bit of logical information dissipates at least k_B T ln(2) of thermodynamic heat.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "bridge_quantum_crypto",
            "source": "node_quantum",
            "target": "node_lattice_crypto",
            "title": "Quantum Period-Finding & Lattice Resistance",
            "summary": "Quantum Fourier transforms break discrete logarithm ciphers, necessitating lattice-based trapdoors.",
            "resource_ref": "demo_res_lattice_crypto"
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
            "id": "bridge_ai_perceptron",
            "source": "node_ai",
            "target": "node_perceptron",
            "title": "Linear Hyperplanes & Neural Foundations",
            "summary": "Single perceptrons establish linear decision boundaries that compose deep multi-layer representations.",
            "resource_ref": "demo_res_perceptron"
        },
        {
            "id": "bridge_perceptron_activation",
            "source": "node_perceptron",
            "target": "node_activation",
            "title": "Non-Linear Squashing & XOR Solvability",
            "summary": "Continuous non-linear activations overcome single-unit linear separability limits to solve non-convex problems.",
            "resource_ref": "demo_res_perceptron"
        },
        {
            "id": "bridge_ai_cv",
            "source": "node_ai",
            "target": "node_cv",
            "title": "Spatial Equivariance in Visual Representation",
            "summary": "Convolutional feature maps translate spatial sensor patterns into hierarchical neural representations.",
            "resource_ref": "demo_res_computer_vision"
        },
        {
            "id": "bridge_cv_feature",
            "source": "node_cv",
            "target": "node_feature_maps",
            "title": "Spatial Convolutions & Discrete Gradient Kernels",
            "summary": "Sliding parameterized 2D kernels calculates directional edge gradients and texture maps.",
            "resource_ref": "demo_res_computer_vision"
        },
        {
            "id": "bridge_info_classical_crypto",
            "source": "node_info",
            "target": "node_classical_crypto",
            "title": "Shannon's Secrecy & Letter Frequency Profile",
            "summary": "Natural language redundancy leaks probability distributions across classical substitution ciphers.",
            "resource_ref": "demo_res_classical_crypto"
        },
        {
            "id": "bridge_classical_lattice",
            "source": "node_classical_crypto",
            "target": "node_lattice_crypto",
            "title": "Cryptographic Evolution: Shifts to Lattices",
            "summary": "Progression from modular shift ciphers to hard geometric lattice vectors immune to quantum periods.",
            "resource_ref": "demo_res_lattice_crypto"
        },
        {
            "id": "bridge_quantum_topological",
            "source": "node_quantum",
            "target": "node_topological",
            "title": "Topological Protection & Majorana Modes",
            "summary": "Non-abelian boundary modes protect quantum states against local environmental decoherence.",
            "resource_ref": "demo_res_topological"
        },
        {
            "id": "bridge_quantum_coherence",
            "source": "node_quantum",
            "target": "node_coherence",
            "title": "Sub-Kelvin Thermal Noise Dissipation",
            "summary": "Dilution cryostats suppress thermal phonon scattering so quantum wavefunctions remain coherent.",
            "resource_ref": "demo_res_coherence"
        },
        {
            "id": "bridge_coherence_telemetry",
            "source": "node_coherence",
            "target": "node_telemetry",
            "title": "Cryogenic Telemetry & Noise Floor Audits",
            "summary": "Empirical calibration of sub-20 mK baselines against Johnson-Nyquist thermal noise boundaries.",
            "resource_ref": "demo_res_telemetry"
        },
        {
            "id": "bridge_neuro_synaptic",
            "source": "node_neuro",
            "target": "node_synaptic",
            "title": "STDP Temporal Coincidence Plasticity",
            "summary": "Biological synapses adjust connection strength dynamically based on relative spike timings.",
            "resource_ref": "demo_res_neural"
        },
        {
            "id": "bridge_synaptic_perceptron",
            "source": "node_synaptic",
            "target": "node_perceptron",
            "title": "Biological Plasticity vs Gradient Weight Updates",
            "summary": "Comparing millisecond biological STDP with artificial backpropagation weight adjustments.",
            "resource_ref": "demo_res_neural"
        },
        {
            "id": "bridge_automata_selforg",
            "source": "node_automata",
            "target": "node_self_org",
            "title": "Deterministic Local Rules & Soliton Emergence",
            "summary": "Uniform local neighbor updates produce self-repairing gliders and persistent localized complexity.",
            "resource_ref": "demo_res_automata"
        },
        {
            "id": "bridge_thermo_automata",
            "source": "node_thermo",
            "target": "node_automata",
            "title": "Information Entropy in Grid State Evolution",
            "summary": "Tracking algorithmic entropy and dissipation in reversible and irreversible cellular systems.",
            "resource_ref": "demo_res_entropy"
        },
        {
            "id": "bridge_fourier_quantum",
            "source": "node_fourier",
            "target": "node_quantum",
            "title": "Quantum Period Finding vs Classical Fourier",
            "summary": "Quantum Fourier transforms find hidden algebraic subgroup periods exponentially faster than classical FFT.",
            "resource_ref": "demo_res_lattice_crypto"
        },
        {
            "id": "bridge_fourier_cv",
            "source": "node_fourier",
            "target": "node_cv",
            "title": "Spatial Frequency Representations in Vision",
            "summary": "Decomposing visual sensor frames into spatial frequency bands for scale-invariant recognition.",
            "resource_ref": "demo_res_computer_vision"
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
        "domain": "Quantum Physics",
        "entry_type": "Experiment Log",
        "status": "Testing",
        "research_question": "Does dilution cryostat cooling below 20 mK suppress Johnson-Nyquist thermal voltage noise to theoretical limits?",
        "hypothesis": "Operating superconducting resonators at 15 mK will reduce thermal noise spectral density S_v to less than 10^-18 V^2/Hz.",
        "observations": "Recorded 14.8 mK cold plate baseline inside dilution cryostat. Thermal voltage noise measurement conforms to Nyquist formula S_v = 4 k_B T R.",
        "methodology": "Connected high-Q superconducting LC resonator to cryogenic amplifier chain; calibrated RF attenuators; integrated spectrum analyzer across 4-8 GHz band.",
        "results": "Noise floor reached 1.1 x 10^-19 V^2/Hz at 14.8 mK, matching theoretical predictions within 3.2% error margin.",
        "conclusion": "Cryogenic thermal shielding verified. High-frequency RF line filtering eliminated stray ambient photon leakage.",
        "tags": "Cryostats, Resonators, Johnson-Noise, Quantum",
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
        "entry_type": "Finding",
        "status": "Verified",
        "research_question": "Can atmospheric RF fluctuation seeds provide uniform entropy across 10,000 continuous 64-bit sampling iterations?",
        "hypothesis": "Atmospheric thermal noise exhibits zero unigram skew (|p - 0.5| < 0.001) across Dieharder statistical battery tests.",
        "observations": "Evaluated 10,000 generated 64-bit entropy sample words. Frequency distribution of zero and one bits shows zero statistical skew.",
        "methodology": "Captured wideband RF noise diode voltage samples; passed through Von Neumann de-skewing whitening filter; executed unigram and serial run tests.",
        "results": "Empirical bit balance measured at p = 0.50008. Chi-squared uniformity score passed at 95% confidence interval.",
        "conclusion": "Empirical results verify pseudo-quantum fluctuation simulator stability for cryptographic seeds.",
        "tags": "PRNG, Entropy, Statistical-Tests, Shannon",
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
        "domain": "Artificial Intelligence",
        "entry_type": "Hypothesis",
        "status": "Refuted",
        "research_question": "Can a single artificial neuron with continuous sigmoid activation separate non-linear XOR input coordinates?",
        "hypothesis": "Adjusting sigmoid steepness and bias offsets will permit a single linear hyperplane to partition diagonal XOR clusters.",
        "observations": "Tested single artificial neuron configuration on non-linear XOR input patterns (0,0->0; 0,1->1; 1,0->1; 1,1->0).",
        "methodology": "Swept weight combinations across [-5.0, +5.0] and bias across [-2.0, +2.0] in CurioLab Single Neuron Playground; plotted decision surface.",
        "results": "Maximum classification accuracy stalled at 75%. No single linear hyperplane can simultaneously partition (0,1) and (1,0) from (0,0) and (1,1).",
        "conclusion": "Confirmed Minsky-Papert theorem: a single linear hyperplane cannot partition non-linearly separable coordinates. Multi-layer representations or kernel projection required.",
        "tags": "Perceptrons, XOR, Decision-Boundaries, Machine-Learning",
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
        "entry_type": "Research Idea",
        "status": "Formulated",
        "research_question": "Can asymmetric boundary conditions in 2D cellular automata with Moore neighborhoods sustain stable directional solitons rather than static cyclic oscillators?",
        "hypothesis": "Introducing directional parity offsets into neighbor transition matrices will break reflective symmetry and generate persistent gliding solitons.",
        "observations": "Standard Conway B3/S23 life rules produce static blinkers and periodic gliders with fixed diagonal velocities.",
        "methodology": "Formulating transition rule lookup table with anisotropic weights along the cardinal axes; preparing simulation trial grid.",
        "results": "Theoretical formulation complete; awaiting interactive simulator execution.",
        "conclusion": "Hypothesis formulated for upcoming empirical investigation in CurioLab complexity workspace.",
        "tags": "Cellular-Automata, Solitons, Morphogenesis, Complexity",
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
