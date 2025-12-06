from gluon import current, DIV, INPUT
from s3widgets import OptionsFilter


class LocationFilter(OptionsFilter):
    """
    Refactored Location Filter Widget

    This widget allows filtering data by location using hierarchical
    selectors (L0 → L1 → L2 → City → Translation).

    Improvements:
        - Added clear documentation
        - Broke large logic into smaller private methods
        - Improved naming consistency
        - Removed deep nesting when possible
        - Added helper methods for clarity and maintainability
    """

    label = "Location"
    represent = "location"
    colspan = ""

    def widget(self, resource, values):
        """
        Main entry point for rendering the location filter.

        Args:
            resource: S3 resource containing table/fields
            values: existing values (if any)

        Returns:
            DIV: HTML element representing the full filter widget
        """

        s3db = current.s3db

        container = DIV(_id="location-filter")

        # Render each hierarchical selector
        container += self._render_level_selector("L0", "Country")
        container += self._render_level_selector("L1", "State")
        container += self._render_level_selector("L2", "Region")
        container += self._render_city_selector()
        container += self._render_translation_selector()

        return container

    # =======================================================
    # Sub-components
    # =======================================================

    def _render_level_selector(self, level_code, label_text):
        """
        Create a generic location hierarchy filter (L0, L1, L2)

        Args:
            level_code (str): Location level ("L0", "L1", "L2")
            label_text (str): Display label

        Returns:
            DIV: selector container
        """
        selector_id = f"{level_code.lower().replace(' ', '-')}-filter"

        return DIV(
            DIV(label_text, _class="location-filter-label"),
            DIV(_id=f"{level_code.lower()}-location-filter"),
            DIV(_id=f"{selector_id}-error", _class="error-message"),
            _class="location-filter-container"
        )

    def _render_city_selector(self):
        """
        Builds the City selection component.
        """
        return DIV(
            DIV("City", _class="location-filter-label"),
            DIV(_id="city-location-filter"),
            DIV(_id="city-filter-error", _class="error-message"),
            _class="location-filter-container"
        )

    def _render_translation_selector(self):
        """
        Builds the Translation selection field.
        """
        return DIV(
            DIV("Translation", _class="location-filter-label"),
            DIV(
                INPUT(_type="text", _id="translation-input",
                      _placeholder="Enter translation…")
            ),
            DIV(_id="translation-error", _class="error-message"),
            _class="location-filter-container"
        )
