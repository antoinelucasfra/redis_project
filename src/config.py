"""
Configuration constants for the Sushi Store Redis project.
Centralizes all ingredient definitions and store parameters.
"""

# ============================================================================
# STORE CONFIGURATION
# ============================================================================

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0

MAX_STOCK = 10_000
MIN_INITIAL_STOCK = 10
MAX_INITIAL_STOCK = 10_000
DEFAULT_SUSHI_COUNT = 100_000
RANDOM_SEED = 444

# ============================================================================
# INGREDIENT DEFINITIONS
# ============================================================================

# All ingredients are binary: 'Oui' (present) or 'Non' (absent)
INGREDIENT_OPTIONS = ['Oui', 'Non']

# Organized by category for better readability
PROTEINS = [
    'saumon', 'saumon_teriyaki', 'daurade', 'thon', 'crevette',
    'poulet', 'thon_cuit', 'foie_gras', 'tofu', 'truite',
    'hareng', 'poulpe', 'boeuf', 'chair_de_crabe', 'oeufs_de_saumon'
]

DAIRY_AND_EGGS = [
    'fromage', 'oeuf'
]

CONDIMENTS = [
    'gingembre', 'wasabi', 'sauce_salee', 'sauce_sucree',
    'sauce_sucreesalee', 'mayonnaise_classique', 'mayonnaise_teriyaki',
    'mayonnaise_japonaise', 'mayonnaise_spicy', 'mayonnaise_ponzu',
    'sauce_teriyaki', 'sauce_satay_aux_cacahuetes', 'sauce_epicee'
]

SPICES = [
    'anis', 'poivre_rose', 'cannelle', 'cardamome', 'curcuma',
    'macis', 'maniguette', 'paprika', 'piment', 'poivre',
    'safran', 'sumac'
]

HERBS = [
    'persil', 'herbe_de_provence', 'menthe', 'coriandre',
    'ciboulette', 'aneth'
]

VEGETABLES = [
    'avocat', 'mangue', 'carotte', 'feve', 'edamame',
    'chou', 'pomme', 'celeri_rave', 'baies_roses', 'prune',
    'betterave', 'noix_de_coco', 'citron_vert', 'citron_jaune',
    'dattes', 'laitue', 'roquette', 'concombre', 'poivrons',
    'asperge', 'oignons_crus', 'oignons_caramelises', 'oignons_frits'
]

TOPPINGS = [
    'sesame', 'feuilles_de_riz'
]

# Complete list of all ingredients (73 total)
ALL_INGREDIENTS = (
    PROTEINS + DAIRY_AND_EGGS + CONDIMENTS +
    SPICES + HERBS + VEGETABLES + TOPPINGS
)

# Verify count matches expected
assert len(ALL_INGREDIENTS) == 73, f"Expected 73 ingredients, got {len(ALL_INGREDIENTS)}"
