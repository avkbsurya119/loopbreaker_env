"""LoopBreaker Environment - Task/Scenario Definitions

Contains all scenarios for detecting different types of decision loops.
Each scenario includes events, correct detection, and correct intervention.
"""

SCENARIOS = [
    # ========== REPEATED SEARCH SCENARIOS ==========
    # Easy: Same query repeated multiple times
    {
        "task_id": "repeated_search_easy_1",
        "description": "User searches for the same productivity app query 3 times",
        "difficulty": "easy",
        "category": "repeated_search",
        "events": [
            {"type": "search", "value": "best todo app"},
            {"type": "search", "value": "best todo app"},
            {"type": "search", "value": "best todo app"},
        ],
        "correct_detection": "detect_repeated_search",
        "correct_intervention": "decide",
    },
    {
        "task_id": "repeated_search_easy_2",
        "description": "User searches for productivity tools repeatedly",
        "difficulty": "easy",
        "category": "repeated_search",
        "events": [
            {"type": "search", "value": "productivity tools 2024"},
            {"type": "search", "value": "productivity tools 2024"},
            {"type": "search", "value": "productivity tools 2024"},
            {"type": "search", "value": "productivity tools 2024"},
        ],
        "correct_detection": "detect_repeated_search",
        "correct_intervention": "decide",
    },
    # Medium: Similar query variants repeated
    {
        "task_id": "repeated_search_medium_1",
        "description": "User searches for similar variants of time management apps",
        "difficulty": "medium",
        "category": "repeated_search",
        "events": [
            {"type": "search", "value": "best time tracking app"},
            {"type": "search", "value": "top time tracking apps"},
            {"type": "search", "value": "time tracking app reviews"},
            {"type": "search", "value": "best time tracking software"},
        ],
        "correct_detection": "detect_repeated_search",
        "correct_intervention": "decide",
    },
    {
        "task_id": "repeated_search_medium_2",
        "description": "User searches for diet-related queries with variations",
        "difficulty": "medium",
        "category": "repeated_search",
        "events": [
            {"type": "search", "value": "best diet plan"},
            {"type": "search", "value": "top diet plans 2024"},
            {"type": "search", "value": "effective diet programs"},
            {"type": "search", "value": "best diets for weight loss"},
        ],
        "correct_detection": "detect_repeated_search",
        "correct_intervention": "reframe",
    },
    # Hard: Repeated search mixed with noise
    {
        "task_id": "repeated_search_hard_1",
        "description": "Repeated searches mixed with unrelated activity",
        "difficulty": "hard",
        "category": "repeated_search",
        "events": [
            {"type": "search", "value": "best laptop 2024"},
            {"type": "page_visit", "value": "news_article_1"},
            {"type": "search", "value": "top laptops reviews"},
            {"type": "app_switch", "value": "email_app"},
            {"type": "search", "value": "best laptop for programming"},
            {"type": "page_visit", "value": "social_media"},
            {"type": "search", "value": "laptop buying guide 2024"},
        ],
        "correct_detection": "detect_repeated_search",
        "correct_intervention": "decide",
    },

    # ========== REVISITING SAME CONTENT SCENARIOS ==========
    # Easy: Same page revisited directly
    {
        "task_id": "revisit_easy_1",
        "description": "User revisits the same article multiple times",
        "difficulty": "easy",
        "category": "revisit",
        "events": [
            {"type": "page_visit", "value": "article_productivity_tips"},
            {"type": "page_visit", "value": "article_productivity_tips"},
            {"type": "page_visit", "value": "article_productivity_tips"},
        ],
        "correct_detection": "detect_revisit",
        "correct_intervention": "pause",
    },
    {
        "task_id": "revisit_easy_2",
        "description": "User keeps opening the same product page",
        "difficulty": "easy",
        "category": "revisit",
        "events": [
            {"type": "page_visit", "value": "product_headphones_sony"},
            {"type": "page_visit", "value": "product_headphones_sony"},
            {"type": "page_visit", "value": "product_headphones_sony"},
            {"type": "page_visit", "value": "product_headphones_sony"},
        ],
        "correct_detection": "detect_revisit",
        "correct_intervention": "decide",
    },
    # Medium: Same page revisited after other pages
    {
        "task_id": "revisit_medium_1",
        "description": "User keeps returning to the same article between other visits",
        "difficulty": "medium",
        "category": "revisit",
        "events": [
            {"type": "page_visit", "value": "blog_post_habits"},
            {"type": "page_visit", "value": "news_tech"},
            {"type": "page_visit", "value": "blog_post_habits"},
            {"type": "page_visit", "value": "youtube_video_1"},
            {"type": "page_visit", "value": "blog_post_habits"},
        ],
        "correct_detection": "detect_revisit",
        "correct_intervention": "pause",
    },
    {
        "task_id": "revisit_medium_2",
        "description": "User revisits comparison page multiple times",
        "difficulty": "medium",
        "category": "revisit",
        "events": [
            {"type": "page_visit", "value": "comparison_phones_2024"},
            {"type": "search", "value": "iphone vs samsung"},
            {"type": "page_visit", "value": "comparison_phones_2024"},
            {"type": "page_visit", "value": "review_iphone"},
            {"type": "page_visit", "value": "comparison_phones_2024"},
        ],
        "correct_detection": "detect_revisit",
        "correct_intervention": "decide",
    },
    # Hard: Semantically same content with different URLs
    {
        "task_id": "revisit_hard_1",
        "description": "User visits semantically similar content from different sources",
        "difficulty": "hard",
        "category": "revisit",
        "events": [
            {"type": "page_visit", "value": "nytimes_productivity_article"},
            {"type": "page_visit", "value": "wsj_productivity_tips"},
            {"type": "page_visit", "value": "medium_productivity_guide"},
            {"type": "page_visit", "value": "forbes_productivity_hacks"},
            {"type": "page_visit", "value": "hbr_productivity_article"},
        ],
        "correct_detection": "detect_revisit",
        "correct_intervention": "reframe",
    },

    # ========== APP SWITCHING SCENARIOS ==========
    # Easy: Fast switch between 2 apps
    {
        "task_id": "app_switch_easy_1",
        "description": "User rapidly switches between two apps",
        "difficulty": "easy",
        "category": "app_switching",
        "events": [
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "email"},
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "email"},
            {"type": "app_switch", "value": "slack"},
        ],
        "correct_detection": "detect_app_switching",
        "correct_intervention": "pause",
    },
    {
        "task_id": "app_switch_easy_2",
        "description": "User oscillates between browser and IDE",
        "difficulty": "easy",
        "category": "app_switching",
        "events": [
            {"type": "app_switch", "value": "vscode"},
            {"type": "app_switch", "value": "chrome"},
            {"type": "app_switch", "value": "vscode"},
            {"type": "app_switch", "value": "chrome"},
        ],
        "correct_detection": "detect_app_switching",
        "correct_intervention": "decide",
    },
    # Medium: 3-app oscillation
    {
        "task_id": "app_switch_medium_1",
        "description": "User switches between three apps indecisively",
        "difficulty": "medium",
        "category": "app_switching",
        "events": [
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "email"},
            {"type": "app_switch", "value": "calendar"},
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "email"},
            {"type": "app_switch", "value": "calendar"},
        ],
        "correct_detection": "detect_app_switching",
        "correct_intervention": "pause",
    },
    {
        "task_id": "app_switch_medium_2",
        "description": "User switches between social media and work apps",
        "difficulty": "medium",
        "category": "app_switching",
        "events": [
            {"type": "app_switch", "value": "twitter"},
            {"type": "app_switch", "value": "notion"},
            {"type": "app_switch", "value": "instagram"},
            {"type": "app_switch", "value": "notion"},
            {"type": "app_switch", "value": "twitter"},
        ],
        "correct_detection": "detect_app_switching",
        "correct_intervention": "reframe",
    },
    # Hard: Mixed switching with productive and unproductive signals
    {
        "task_id": "app_switch_hard_1",
        "description": "Complex app switching pattern with mixed productivity",
        "difficulty": "hard",
        "category": "app_switching",
        "events": [
            {"type": "app_switch", "value": "vscode"},
            {"type": "search", "value": "how to fix bug"},
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "vscode"},
            {"type": "page_visit", "value": "stackoverflow_answer"},
            {"type": "app_switch", "value": "slack"},
            {"type": "app_switch", "value": "email"},
            {"type": "app_switch", "value": "vscode"},
        ],
        "correct_detection": "detect_app_switching",
        "correct_intervention": "decide",
    },

    # ========== NO LOOP SCENARIOS (for false positive testing) ==========
    {
        "task_id": "no_loop_1",
        "description": "Normal productive browsing session",
        "difficulty": "easy",
        "category": "no_loop",
        "events": [
            {"type": "search", "value": "python tutorial"},
            {"type": "page_visit", "value": "docs_python_org"},
            {"type": "page_visit", "value": "python_tutorial_page_2"},
            {"type": "app_switch", "value": "vscode"},
        ],
        "correct_detection": "continue_monitoring",
        "correct_intervention": "continue_monitoring",
    },
    {
        "task_id": "no_loop_2",
        "description": "Research session with diverse content",
        "difficulty": "medium",
        "category": "no_loop",
        "events": [
            {"type": "search", "value": "machine learning basics"},
            {"type": "page_visit", "value": "ml_course_page"},
            {"type": "search", "value": "neural networks explained"},
            {"type": "page_visit", "value": "nn_tutorial"},
            {"type": "app_switch", "value": "jupyter"},
        ],
        "correct_detection": "continue_monitoring",
        "correct_intervention": "continue_monitoring",
    },
]


def get_scenario_by_id(task_id: str) -> dict | None:
    """Get a scenario by its task_id."""
    for scenario in SCENARIOS:
        if scenario["task_id"] == task_id:
            return scenario
    return None


def get_scenarios_by_category(category: str) -> list[dict]:
    """Get all scenarios of a specific category."""
    return [s for s in SCENARIOS if s["category"] == category]


def get_scenarios_by_difficulty(difficulty: str) -> list[dict]:
    """Get all scenarios of a specific difficulty level."""
    return [s for s in SCENARIOS if s["difficulty"] == difficulty]
