"""Body map selector for marking the location of a photo or finding.

For Phase 2 a lightweight 2D silhouette is used. The user picks a region from a
labeled list while a front/back SVG gives a visual reference. This avoids the
heavy dependency of embedding a full interactive 3D model.
"""

from typing import Optional

import streamlit as st

from translations import _

# Hierarchical body sites used in PhotoSnapshot.body_site.
# Format: region:subregion:side
BODY_SITE_OPTIONS = {
    "front:head": "body_front_head",
    "back:head": "body_back_head",
    "front:neck": "body_front_neck",
    "back:neck": "body_back_neck",
    "front:chest": "body_chest",
    "front:abdomen": "body_abdomen",
    "front:pelvis": "body_pelvis",
    "back:upper_back": "body_upper_back",
    "back:lower_back": "body_lower_back",
    "back:buttock": "body_buttock",
    "arm:shoulder:left": "body_left_shoulder",
    "arm:shoulder:right": "body_right_shoulder",
    "arm:upper_arm:left": "body_left_upper_arm",
    "arm:upper_arm:right": "body_right_upper_arm",
    "arm:forearm:left": "body_left_forearm",
    "arm:forearm:right": "body_right_forearm",
    "arm:elbow:left": "body_left_elbow",
    "arm:elbow:right": "body_right_elbow",
    "hand:left": "body_left_hand",
    "hand:right": "body_right_hand",
    "hand:finger:index:left": "body_left_index_finger",
    "hand:finger:index:right": "body_right_index_finger",
    "hand:finger:middle:left": "body_left_middle_finger",
    "hand:finger:middle:right": "body_right_middle_finger",
    "hand:finger:ring:left": "body_left_ring_finger",
    "hand:finger:ring:right": "body_right_ring_finger",
    "hand:finger:little:left": "body_left_little_finger",
    "hand:finger:little:right": "body_right_little_finger",
    "hand:finger:thumb:left": "body_left_thumb",
    "hand:finger:thumb:right": "body_right_thumb",
    "leg:thigh:left": "body_left_thigh",
    "leg:thigh:right": "body_right_thigh",
    "leg:knee:left": "body_left_knee",
    "leg:knee:right": "body_right_knee",
    "leg:calf:left": "body_left_calf",
    "leg:calf:right": "body_right_calf",
    "leg:ankle:left": "body_left_ankle",
    "leg:ankle:right": "body_right_ankle",
    "foot:left": "body_left_foot",
    "foot:right": "body_right_foot",
    "foot:toe:big:left": "body_left_big_toe",
    "foot:toe:big:right": "body_right_big_toe",
    "nail:fingernail:left": "body_left_fingernails",
    "nail:fingernail:right": "body_right_fingernails",
    "nail:toenail:left": "body_left_toenails",
    "nail:toenail:right": "body_right_toenails",
    "other": "body_other",
}

# Simplified front/back body SVG for visual reference.
_FRONT_SVG = """
<svg viewBox="0 0 120 240" xmlns="http://www.w3.org/2000/svg" style="height: 280px;">
  <!-- head -->
  <ellipse cx="60" cy="25" rx="18" ry="22" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- neck -->
  <rect x="52" y="45" width="16" height="14" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- torso -->
  <path d="M35 60 Q25 70 25 100 L25 150 Q25 165 60 175 Q95 165 95 150 L95 100 Q95 70 85 60 Z"
        fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- left arm -->
  <path d="M25 75 Q10 90 12 130 Q14 155 20 165" fill="none" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>
  <!-- right arm -->
  <path d="M95 75 Q110 90 108 130 Q106 155 100 165" fill="none" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>
  <!-- left leg -->
  <path d="M42 168 L38 230" fill="none" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
  <!-- right leg -->
  <path d="M78 168 L82 230" fill="none" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
</svg>
"""

_BACK_SVG = """
<svg viewBox="0 0 120 240" xmlns="http://www.w3.org/2000/svg" style="height: 280px;">
  <!-- head -->
  <ellipse cx="60" cy="25" rx="18" ry="22" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- neck -->
  <rect x="52" y="45" width="16" height="14" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- torso -->
  <path d="M35 60 Q25 70 25 100 L25 150 Q25 165 60 175 Q95 165 95 150 L95 100 Q95 70 85 60 Z"
        fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <!-- left arm -->
  <path d="M25 75 Q10 90 12 130 Q14 155 20 165" fill="none" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>
  <!-- right arm -->
  <path d="M95 75 Q110 90 108 130 Q106 155 100 165" fill="none" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>
  <!-- left leg -->
  <path d="M42 168 L38 230" fill="none" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
  <!-- right leg -->
  <path d="M78 168 L82 230" fill="none" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
</svg>
"""


def select_body_site(label: str, current_value: Optional[str] = None) -> str:
    """Render a body map selector and return the selected body_site value.

    Args:
        label: Label for the selectbox.
        current_value: Pre-selected body_site, if any.

    Returns:
        The selected body_site string (e.g. ``front:chest``).
    """
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Front**")
        st.markdown(_FRONT_SVG, unsafe_allow_html=True)
    with col2:
        st.markdown("**Back**")
        st.markdown(_BACK_SVG, unsafe_allow_html=True)

    options = list(BODY_SITE_OPTIONS.keys())
    index = options.index(current_value) if current_value in options else 0
    selected = st.selectbox(
        label,
        options=options,
        format_func=lambda key: _(BODY_SITE_OPTIONS[key]),
        index=index,
        key="body_site_selector",
    )
    return selected


def body_site_label(body_site: str) -> str:
    """Return a human-readable label for a body_site value."""
    return _(BODY_SITE_OPTIONS.get(body_site, body_site))
